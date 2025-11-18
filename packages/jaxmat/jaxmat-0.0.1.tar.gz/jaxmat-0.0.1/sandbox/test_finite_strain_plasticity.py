import jax

jax.config.update("jax_platform_name", "gpu")

from time import time
import equinox as eqx
import matplotlib.pyplot as plt
import jax.numpy as jnp
from jaxmat.tensors import Tensor2
import jaxmat.materials as jm
from fast_fe_fp_elastoplasticity import FeFpJ2Plasticity


def test_FeFp_elastoplasticity(material, Nbatch=1):

    state = material.init_state(Nbatch)
    F = state.F

    plt.figure()
    eps_dot = 30e-3

    imposed_eps = 0
    dt = 0
    Nsteps = 31
    times = jnp.linspace(0, 1.0, Nsteps)
    t = 0

    plt.plot(state.F[0][0, 0] - 1, state.PK1[0][0, 0], "xb")
    for i, dt in enumerate(jnp.diff(times)):
        t += dt
        imposed_eps += eps_dot * dt
        lamb = 1 + imposed_eps

        def set_F(F):
            return Tensor2(
                tensor=jnp.diag(
                    jnp.asarray([lamb, 1 / jnp.sqrt(lamb), 1 / jnp.sqrt(lamb)])
                )
            )

        F = eqx.filter_vmap(
            set_F,
        )(F)
        tic = time()
        Sig, state = material.batched_constitutive_update(F, state, dt)
        print(
            f"Incr {i+1}: Resolution time/batch:",
            (time() - tic),
        )
        state = state.update(F=F)

        # lamb_list = lamb * jnp.ones((Nbatch,))
        # loading = ImposedLoading(
        #     "finite_strain",
        #     FXX=lamb_list,
        # )
        # primals = (F, state, loading, material, dt)
        # tic = time()
        # F_sol, state, stats = global_solve(*primals)
        # num_evals = (
        #     stats["num_steps"][0] + 1
        # )  # add 1 because we recompute residual at the end
        # print(
        #     f"Incr {i+1}: Num iter = {num_evals-1} Resolution time/iteration/batch:",
        #     (time() - tic) / num_evals / Nbatch,
        # )
        # state = state.update(F=F_sol)

        plt.plot(state.F[0][0, 0] - 1, state.PK1[0][0, 0], "xb")
        plt.plot(state.F[0][0, 0] - 1, state.Cauchy[0][0, 0], "sr")
    plt.show()


E, nu = 70e3, 0.3
elastic_model = jm.LinearElasticIsotropic(E, nu)

sig0 = 500.0
sigu = 750.0
b = 1000.0


class YieldStress(eqx.Module):
    def __call__(self, p):
        return sig0 + (sigu - sig0) * (1 - jnp.exp(-b * p))


Nbatch = int(1e6)

# material = jm.FeFpJ2Plasticity(elastic_model, YieldStress())
material = FeFpJ2Plasticity(elastic_model, YieldStress())
test_FeFp_elastoplasticity(material, Nbatch=Nbatch)
