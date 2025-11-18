import jax

jax.config.update("jax_platform_name", "cpu")

from time import time
import equinox as eqx
import matplotlib.pyplot as plt
import jax.numpy as jnp

from jaxmat.loader import ImposedLoading, global_solve
from jaxmat.tensors import SymmetricTensor2, dev
import jaxmat.materials as jm


def test_elastoplasticity(material, Nbatch=1):

    state = material.init_state(Nbatch)
    Eps = state.strain

    plt.figure()

    imposed_eps = 0
    dt = 0
    Nsteps = 101
    times = jnp.linspace(0, 1.0, Nsteps)
    t = 0
    for i, dt in enumerate(jnp.diff(times)):
        t += dt
        imposed_eps = 5e-3
        if t > 0.5:
            imposed_eps = 0

        def set_eps(Eps):
            return SymmetricTensor2(
                tensor=jnp.diag(jnp.asarray([1.0, -0.5, -0.5]) * imposed_eps)
            )

        Eps = eqx.filter_vmap(
            set_eps,
        )(Eps)
        tic = time()
        Sig, state = material.batched_constitutive_update(Eps, state, dt)
        print(
            f"Incr {i+1}: Resolution time/batch:",
            (time() - tic) / Nbatch,
        )
        state = state.update(strain=Eps)
        Sig = state.stress

        plt.plot(t, Sig[0][0, 0], "xb")
    plt.show()


E, nu = 100e3, 0.3
elastic_model = jm.LinearElasticIsotropic(E, nu)
viscous_model = jm.LinearElasticIsotropic(20e3, nu)


# class HardeningPotential(eqx.Module):
#     sig0 = 350.0
#     sigu = 500.0
#     b = 1e3

#     def __call__(self, p):
#         return (self.sigu - self.sig0) * (p + jnp.exp(-self.b * p) / self.b)


# class PlasticDissipation(eqx.Module):
#     def __call__(self, epsp):
#         return (
#             jnp.sqrt(2 / 3) * jnp.sqrt(jnp.trace(dev(epsp) @ dev(epsp)) + 1e-16) ** 1.5
#         )


Nbatch = int(1)

free_energy = jm.FreeEnergy(elastic_model, viscous_model)
dissipation = jm.DissipationPotential(
    eta=1e3
    # hardening.sig0, PlasticDissipation(), barrier_parameter=0.001
)
material = jm.GeneralizedStandardMaterial(free_energy, dissipation)
test_elastoplasticity(material, Nbatch=Nbatch)
