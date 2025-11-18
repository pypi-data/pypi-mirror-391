import jax.numpy as jnp
import equinox as eqx
import optimistix as optx
from optax.tree_utils import tree_add, tree_zeros_like
from jaxmat.utils import default_value, enforce_dtype
from jaxmat.state import AbstractState, make_batched
from jaxmat.tensors import SymmetricTensor2, dev
from .behavior import SmallStrainBehavior
from .elasticity import LinearElasticIsotropic
from .plastic_surfaces import (
    AbstractPlasticSurface,
    vonMises,
)
from jaxmat.tensors.utils import FischerBurmeister as FB
import jax


class InternalState(AbstractState):
    """Internal state for hardening plasticity"""

    p: jax.Array = default_value(0.0)
    epsp: SymmetricTensor2 = eqx.field(default_factory=lambda: SymmetricTensor2())


class vonMisesIsotropicHardening(SmallStrainBehavior):
    elastic_model: LinearElasticIsotropic
    yield_stress: eqx.Module
    plastic_surface: AbstractPlasticSurface = vonMises()
    internal: AbstractState = InternalState()

    @eqx.filter_jit
    @eqx.debug.assert_max_traces(max_traces=1)
    def constitutive_update(self, eps, state, dt):
        eps_old = state.strain
        deps = eps - eps_old
        isv_old = state.internal
        sig_old = state.stress

        def solve_state(deps, isv_old):
            mu = self.elastic_model.mu
            sig_el = sig_old + self.elastic_model.C @ deps
            sig_eq_el = self.plastic_surface(sig_el)
            n_el = self.plastic_surface.normal(sig_el)
            p_old = isv_old.p

            def residual(dp, args):
                p = p_old + dp
                yield_criterion = sig_eq_el - 3 * mu * dp - self.yield_stress(p)
                res = FB(-yield_criterion / self.elastic_model.E, dp)
                return res

            dy0 = jnp.array(0.0)
            sol = optx.root_find(residual, self.solver, dy0, adjoint=self.adjoint)
            dp = sol.value

            depsp = n_el * dp
            sig = sig_old + self.elastic_model.C @ (deps - dev(depsp))
            isv = isv_old.add(p=dp, epsp=depsp)
            return sig, isv

        sig, isv = solve_state(deps, isv_old)

        new_state = state.update(strain=eps, stress=sig, internal=isv)
        return sig, new_state


class GeneralIsotropicHardening(SmallStrainBehavior):
    elastic_model: LinearElasticIsotropic
    yield_stress: eqx.Module
    plastic_surface: AbstractPlasticSurface
    internal = InternalState()

    @eqx.filter_jit
    @eqx.debug.assert_max_traces(max_traces=1)
    def constitutive_update(self, eps, state, dt):
        eps_old = state.strain
        deps = eps - eps_old
        isv_old = state.internal
        sig_old = state.stress

        def eval_stress(deps, dy):
            return sig_old + self.elastic_model.C @ (deps - dy.epsp)

        def solve_state(deps, y_old):
            p_old = y_old.p

            def residual(dy, args):
                dp, depsp = dy.p, dy.epsp
                sig = eval_stress(deps, dy)
                yield_criterion = self.plastic_surface(sig) - self.yield_stress(
                    p_old + dp
                )
                n = self.plastic_surface.normal(sig)
                res = (
                    FB(-yield_criterion / self.elastic_model.E, dp),
                    depsp - n * dp,
                )
                y = tree_add(y_old, dy)
                return (res, y)

            dy0 = tree_zeros_like(isv_old)
            sol = optx.root_find(
                residual, self.solver, dy0, has_aux=True, adjoint=self.adjoint
            )
            dy = sol.value
            y = sol.aux
            sig = eval_stress(deps, dy)
            return sig, y

        sig, isv = solve_state(deps, isv_old)
        new_state = state.update(strain=eps, stress=sig, internal=isv)
        return sig, new_state


class GeneralHardeningInternalState(AbstractState):
    p: float = default_value(0.0)
    epsp: SymmetricTensor2 = eqx.field(default_factory=lambda: SymmetricTensor2())
    alpha: SymmetricTensor2 = eqx.field(init=False)
    nvar: int = eqx.field(static=True, default=1)

    def __post_init__(self):
        self.alpha = make_batched(SymmetricTensor2(), self.nvar)


class GeneralHardening(SmallStrainBehavior):
    elastic_model: LinearElasticIsotropic
    yield_stress: float = enforce_dtype()
    plastic_surface: AbstractPlasticSurface
    combined_hardening: eqx.Module
    nvar: int = eqx.field(static=True, default=1)
    internal: AbstractState = eqx.field(init=False)

    def __post_init__(self):
        self.internal = GeneralHardeningInternalState(nvar=self.nvar)

    @eqx.filter_jit
    @eqx.debug.assert_max_traces(max_traces=1)
    def constitutive_update(self, eps, state, dt):
        eps_old = state.strain
        deps = eps - eps_old
        isv_old = state.internal
        sig_old = state.stress

        def eval_stress(deps, dy):
            return sig_old + self.elastic_model.C @ (deps - dy.epsp)

        def solve_state(deps, y_old):
            def residual(dy, args):
                dp, depsp, dalpha = dy.p, dy.epsp, dy.alpha
                y = tree_add(y_old, dy)
                p, alpha = y.p, y.alpha
                sig = eval_stress(deps, dy)
                X = self.combined_hardening.dalpha(alpha, p)
                yield_criterion = (
                    self.plastic_surface(sig, X)
                    - self.combined_hardening.dp(alpha, p)
                    - self.yield_stress
                )
                n = self.plastic_surface.normal(sig, X)
                res = (
                    FB(-yield_criterion / self.elastic_model.E, dp),
                    depsp - n * dp,
                    dalpha + self.plastic_surface.dX(sig, X) * dp,
                )
                return (res, y)

            dy0 = tree_zeros_like(isv_old)
            sol = optx.root_find(
                residual,
                self.solver,
                dy0,
                has_aux=True,
                adjoint=self.adjoint,
                throw=False,
            )
            dy = sol.value
            y = sol.aux
            sig = eval_stress(deps, dy)
            return sig, y

        sig, isv = solve_state(deps, isv_old)
        new_state = state.update(strain=eps, stress=sig, internal=isv)
        return sig, new_state


class MultiSurfaceInternalState(AbstractState):
    p: float = eqx.field(init=False)
    epsp: SymmetricTensor2 = eqx.field(default_factory=lambda: SymmetricTensor2())
    alpha: SymmetricTensor2 = eqx.field(init=False)
    n_surf: int = eqx.field(static=True, default=1)

    def __post_init__(self):
        self.p = jnp.zeros((self.n_surf,))
        self.alpha = make_batched(SymmetricTensor2(), self.n_surf)


class GeneralPlasticity(SmallStrainBehavior):
    elastic_model: LinearElasticIsotropic
    yield_stresses: list[eqx.Module]
    plastic_surfaces: list[AbstractPlasticSurface]
    combined_hardening: eqx.Module
    n_surf: int = eqx.field(static=True, default=1)
    internal: AbstractState = eqx.field(init=False)

    def __post_init__(self):
        assert len(self.yield_stresses) == len(self.plastic_surfaces)
        self.n_surf = len(self.plastic_surfaces)
        self.internal = MultiSurfaceInternalState(n_surf=self.n_surf)

    @eqx.filter_jit
    @eqx.debug.assert_max_traces(max_traces=1)
    def constitutive_update(self, eps, state, dt):
        eps_old = state.strain
        deps = eps - eps_old
        isv_old = state.internal
        sig_old = state.stress

        def eval_stress(deps, dy):
            return sig_old + self.elastic_model.C @ (
                deps - SymmetricTensor2(tensor=jnp.sum(dy.alpha, axis=0))
            )

        def solve_state(deps, y_old):

            def residual(dy, args):
                y = tree_add(y_old, dy)
                alpha = y.alpha
                p = y.p

                sig = eval_stress(deps, dy)
                X = self.combined_hardening.dalpha(alpha, p)

                res_epsp = dy.epsp
                res_plast = []
                for i in range(self.n_surf):
                    yield_criterion = (
                        self.plastic_surfaces[i](sig - X[i])
                        - self.yield_stresses[i]
                        - self.combined_hardening.dp(alpha, p)[i]
                    )
                    n = self.plastic_surfaces[i].normal(sig - X[i])
                    res_plast.append(
                        FB(-yield_criterion / self.elastic_model.E, dy.p[i])
                    )
                    res_epsp -= n * dy.p[i]

                res = res_plast, res_epsp
                return (res, y)

            dy0 = tree_zeros_like(isv_old)
            sol = optx.root_find(
                residual, self.solver, dy0, has_aux=True, adjoint=self.adjoint
            )
            dy = sol.value
            y = sol.aux
            sig = eval_stress(deps, dy)
            return sig, y

        sig, isv = solve_state(deps, isv_old)
        new_state = state.update(strain=eps, stress=sig, internal=isv)
        return sig, new_state
