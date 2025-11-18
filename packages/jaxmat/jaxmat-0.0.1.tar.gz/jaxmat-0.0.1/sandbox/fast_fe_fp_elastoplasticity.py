import jax.numpy as jnp
import equinox as eqx
import optimistix as optx
from jaxmat.utils import default_value
from jaxmat.state import AbstractState
from jaxmat.tensors import SymmetricTensor2, Tensor2, dev
from jaxmat.tensors.linear_algebra import det33 as det
from jaxmat.materials import FiniteStrainBehavior
from jaxmat.materials.elasticity import LinearElasticIsotropic
from jaxmat.materials.plastic_surfaces import AbstractPlasticSurface, vonMises
from jaxmat.tensors.utils import FischerBurmeister as FB
import jax


class InternalState(AbstractState):
    """Internal state for :class:`FeFpJ2Plasticity`."""

    p: float = default_value(0.0)
    """Cumulated plastic strain $p$."""
    be_bar: SymmetricTensor2 = SymmetricTensor2.identity()
    r"""Isochoric elastic left Cauchy-Green strain $\bar{\bb}^\text{e}$."""


class FeFpJ2Plasticity(FiniteStrainBehavior):
    """Material model based on https://onlinelibrary.wiley.com/doi/epdf/10.1002/nme.6843"""

    elasticity: LinearElasticIsotropic
    """Isotropic elastic model."""
    yield_stress: eqx.Module
    """Isotropic hardening law controlling the evolution of the yield surface size."""
    plastic_surface: AbstractPlasticSurface = vonMises()
    """von Mises plastic surface."""
    internal_type = InternalState

    def constitutive_update(self, F, state, dt):
        F_old = state.F
        isv_old = state.internal
        be_bar_old = isv_old.be_bar
        p_old = isv_old.p
        Id = SymmetricTensor2.identity()

        def solve_state(F):
            # relative strain and elastic predictor
            f = F @ F_old.inv
            f_bar = f * jnp.linalg.det(f) ** (-1 / 3)
            be_bar_trial = f_bar.T @ be_bar_old @ f_bar
            clipped_equiv_stress = lambda s: jnp.clip(
                self.plastic_surface(s), a_min=1e-8
            )

            def residual(dy, args):
                # dp, be_bar_arr = dx
                # be_bar = SymmetricTensor2(array=be_bar_arr)
                dp, be_bar_arr = dy.p, dy.be_bar
                be_bar = SymmetricTensor2(array=be_bar_arr)
                s = self.elasticity.mu * dev(be_bar)
                yield_criterion = clipped_equiv_stress(s) - self.yield_stress(
                    p_old + dp
                )
                n = jax.jacfwd(clipped_equiv_stress)(s)
                res = (
                    FB(-yield_criterion / self.elasticity.E, dp),
                    (
                        dev(be_bar - be_bar_trial)
                        + 2 * dp * jnp.linalg.trace(be_bar) / 3 * n
                        + Id * (det(be_bar) - 1)
                    ).sym.array,
                )
                return res

            disv0 = isv_old.update(p=0, be_bar=be_bar_trial.sym)

            def flatten(x):
                if isinstance(x, Tensor2):
                    return x.array
                else:
                    return x

            dy0 = jax.tree.map(flatten, disv0, is_leaf=lambda x: isinstance(x, Tensor2))

            sol = optx.root_find(
                residual, self.solver, dy0, adjoint=self.adjoint, throw=False
            )
            y = sol.value
            isv = isv_old.update(p=p_old + y.p, be_bar=SymmetricTensor2(array=y.be_bar))
            return isv, be_bar_trial

        isv, _ = solve_state(F)
        # # dp = dy.p
        # be_bar = SymmetricTensor2(array=isv.be_bar)
        # y = isv_old.update(p=isv_old.p + dp, be_bar=be_bar)

        s = self.elasticity.mu * dev(isv.be_bar)
        J = det(F)
        tau = s + self.elasticity.kappa / 2 * (J**2 - 1) * Id
        P = Tensor2(tensor=tau @ F.inv.T)

        new_state = state.update(PK1=P, internal=isv)
        return P, new_state
