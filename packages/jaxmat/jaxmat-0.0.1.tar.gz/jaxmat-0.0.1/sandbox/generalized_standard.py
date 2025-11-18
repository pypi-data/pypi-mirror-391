import jax
import jax.numpy as jnp
import equinox as eqx
import optimistix as optx
from optax.tree_utils import tree_add, tree_zeros_like, tree_scale
from jaxmat.state import (
    AbstractState,
    make_batched,
)
from jaxmat.tensors import SymmetricTensor2
import jaxmat.materials as jm
from jaxmat.solvers import LevenbergMarquardtLineSearch
import lineax as lx


class FreeEnergy(eqx.Module):
    elastic_model: jm.AbstractLinearElastic
    viscous_model: list[jm.AbstractLinearElastic]

    def __call__(self, eps, isv):

        epsv = isv.epsv
        psi_el = 0.5 * jnp.trace(eps @ (self.elastic_model.C @ eps))

        def viscous_free_energy(viscous_model, epsv):
            eps_el = eps - epsv
            return 0.5 * jnp.trace(eps_el @ (viscous_model.C @ eps_el))

        psi_v = jnp.sum(jax.vmap(viscous_free_energy)(self.viscous_model, epsv))
        return psi_el + psi_v


class DissipationPotential(eqx.Module):
    eta: jax.Array

    def __call__(self, isv_dot):
        epsv_dot = isv_dot.epsv

        def viscous_dissipation(eta, epsv_dot):
            return 0.5 * eta * jnp.trace(epsv_dot @ epsv_dot)

        return jnp.sum(jax.vmap(viscous_dissipation)(self.eta, epsv_dot))


class GeneralizedStandardMaterial(jm.SmallStrainBehavior):
    free_energy: eqx.Module
    dissipation_potential: eqx.Module
    internal: AbstractState
    solver_ = LevenbergMarquardtLineSearch(
        rtol=1e-6, atol=1e-6, linear_solver=lx.AutoLinearSolver(well_posed=False)
    )

    def incremental_potential(self, d_isv, args):
        eps, state, dt = args
        isv_old = state.internal
        isv = tree_add(isv_old, d_isv)
        isv_dot = tree_scale(1 / dt, d_isv)
        free_eng = self.free_energy(eps, isv)
        diss_eng = dt * self.dissipation_potential(isv_dot)
        return free_eng + diss_eng

    def constitutive_update(self, eps, state, dt):
        isv_old = state.internal
        d_isv0 = tree_zeros_like(isv_old)
        args = eps, state, dt
        sol = optx.minimise(
            self.incremental_potential,
            self.solver_,
            d_isv0,
            args,
            throw=False,
        )
        d_isv = sol.value
        isv = tree_add(isv_old, d_isv)
        sig = jax.jacfwd(self.free_energy, argnums=0)(eps, isv)
        new_state = state.update(stress=sig, internal=isv)
        return sig, new_state
