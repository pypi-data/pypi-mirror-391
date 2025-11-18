import jax

jax.config.update("jax_platform_name", "cpu")

import equinox as eqx
import matplotlib.pyplot as plt
import jax.numpy as jnp

from jaxmat.materials.viscoelasticity import StandardLinearSolid, GeneralizedMaxwell
from jaxmat.utils import enforce_dtype
from jaxmat.state import AbstractState
from jaxmat.loader import ImposedLoading, global_solve
from jaxmat.tensors import SymmetricTensor2
import jaxmat.materials as jm
import diffrax


class SLSState(AbstractState):
    """Internal state for the :class:`StandardLinearSolid` behavior."""

    epsv: SymmetricTensor2 = eqx.field(default_factory=lambda: SymmetricTensor2())
    """Viscous strain"""


class StandardLinearSolidDiffrax(jm.SmallStrainBehavior):
    elasticity: jm.AbstractLinearElastic
    maxwell_stiffness: jm.AbstractLinearElastic
    maxwell_viscosity: float = enforce_dtype()
    internal_type = SLSState
    solver: diffrax.AbstractSolver = eqx.field(
        static=True, init=False, default=diffrax.Tsit5()
    )
    adjoint: diffrax.AbstractAdjoint = eqx.field(
        static=True, init=False, default=diffrax.ForwardMode()
    )

    @eqx.filter_jit
    def constitutive_update(self, eps, state, dt):
        epsv_old = state.internal.epsv

        tau = self.maxwell_viscosity / self.maxwell_stiffness.E

        def ode_term(t, epsv, eps):
            epsv_dot = (eps - epsv) / tau
            return epsv_dot

        term = diffrax.ODETerm(ode_term)
        t0 = 0.0
        t1 = dt
        dt0 = dt
        sol = diffrax.diffeqsolve(
            term, self.solver, t0, t1, dt0, epsv_old, args=eps, adjoint=self.adjoint
        )
        epsv_new = SymmetricTensor2(
            tensor=sol.ys[0]
        )  # sol.ys is batched over output times (here only one)

        sig = self.elasticity.C @ eps + self.maxwell_stiffness.C @ (eps - epsv_new)
        isv = state.internal.update(epsv=epsv_new)
        new_state = state.update(strain=eps, stress=sig, internal=isv)
        return sig, new_state


def compute_evolution(material, eps_list, times):
    # Initial material state
    state0 = material.init_state()
    dt = jnp.diff(times)

    def step(state, args):
        epszz, dt_ = args

        loading = ImposedLoading(epszz=epszz, sigxx=0.0, sigyy=0.0)

        Eps = state.strain
        Eps, new_state, stats = global_solve(
            Eps, state, loading, material, dt_, in_axes=None
        )

        new_stress = new_state.stress
        sigzz = new_stress[2, 2]
        epsvzz = new_state.internal.epsv[..., 2, 2]

        return new_state, (sigzz, epsvzz)

    # Use lax.scan to loop over eps_list efficiently
    _, out = jax.lax.scan(step, state0, (eps_list, dt))

    return out


E0, nu = 70e3, 0.3
elastic_model = jm.LinearElasticIsotropic(E0, nu)
E1 = 20e3
tau = 0.05
eta = E1 * tau
viscous_model = jm.LinearElasticIsotropic(E1, nu)

material = StandardLinearSolidDiffrax(
    elasticity=elastic_model,
    maxwell_stiffness=viscous_model,
    maxwell_viscosity=eta,
)
# material = GeneralizedMaxwell(
#     elasticity=elastic_model,
#     viscous_branches=jm.LinearElasticIsotropic(jnp.asarray([E1]), jnp.asarray([nu])),
#     relaxation_times=jnp.array([tau]),
# )

Nincr = 20
times = jnp.linspace(0, 10 * tau, Nincr + 1)
epsr = 1e-3
epszz = jnp.full(shape=(Nincr,), fill_value=epsr)

sigzz, epsvzz = compute_evolution(material, epszz, times)
sigzz = jnp.insert(sigzz, 0, 0.0)
epsvzz = jnp.insert(epsvzz, 0, 0.0)

plt.figure()
plt.plot(times, epsr * (1 - jnp.exp(-times / tau)), "-C3", label="Exact")
plt.plot(times, epsvzz, "ok", label="FEM")
plt.xlabel("Time $t$")
plt.ylabel(r"Viscous strain $\varepsilon_{yy}^\text{v}$")
plt.ylim(0, 1.2 * epsr)
plt.legend()
plt.show()

plt.figure()
plt.plot(times, E0 * epsr + E1 * epsr * jnp.exp(-times / tau), "-C3", label="Exact")
plt.plot(times, sigzz, "ok", label="FEM")
plt.xlabel("Time $t$")
plt.ylabel(r"Stress $\sigma_{yy}$ [MPa]")
plt.legend()
plt.show()
