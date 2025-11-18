import jax
import jax.numpy as jnp
import equinox as eqx
import optimistix as optx
from optax.tree_utils import tree_add, tree_zeros_like
from jaxmat.utils import default_value
from jaxmat.state import AbstractState
from jaxmat.tensors import SymmetricTensor2, dev
import jaxmat.materials as jm
from jaxmat.materials.behavior import SmallStrainBehavior
from jaxmat.tensors.utils import FischerBurmeister as FB


class InternalState(AbstractState):
    d: float = default_value(0.0)


class IsotropicDegradation(eqx.Module):
    def __call__(self, d):
        return (1 - d) ** 2


class DamageThreshold(eqx.Module):
    Y0: float
    alpha: float

    def __call__(self, d):
        return self.Y0 * (1 + self.alpha * d)


class Damage(SmallStrainBehavior):
    elastic_model: jm.AbstractLinearElastic
    degradation: IsotropicDegradation
    damage_threshold: DamageThreshold
    internal_type = InternalState

    @eqx.filter_jit
    @eqx.debug.assert_max_traces(max_traces=1)
    def constitutive_update(self, eps, state, dt):
        eps_old = state.strain
        isv_old = state.internal

        def solve_state(eps, isv_old):
            d_old = isv_old.d

            def residual(d, args):
                dd = d - d_old
                Y = -jax.grad(self.degradation)(d) * self.elastic_model.strain_energy(
                    eps
                )
                damage_criterion = jnp.where(d < 1, Y - self.damage_threshold(d), d - 1)
                # jax.debug.print("d={}, Y={}, Yc={}", d, Y, self.damage_threshold(d))
                res = FB(-damage_criterion, dd)
                return res

            dy0 = jnp.array(d_old)
            sol = optx.root_find(
                residual,
                self.solver,
                dy0,
                adjoint=self.adjoint,
                options={"lower": d_old, "upper": 1.0},
            )
            d = sol.value

            sig = (self.elastic_model.C @ eps) * self.degradation(d)
            isv = isv_old.update(d=d)
            return sig, isv

        sig, isv = solve_state(eps, isv_old)

        new_state = state.update(strain=eps, stress=sig, internal=isv)
        return sig, new_state
