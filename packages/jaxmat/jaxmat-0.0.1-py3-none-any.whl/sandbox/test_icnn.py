import jax

jax.config.update("jax_platform_name", "cpu")
jax.config.update("jax_enable_x64", True)
# jax.config.update("jax_disable_jit", True)

from pathlib import Path
from time import time
import matplotlib.pyplot as plt
import numpy as np
import equinox as eqx
from optax.tree_utils import tree_scale
import jax.numpy as jnp

from jaxmat.loader import ImposedLoading, global_solve
from jaxmat.tensors import SymmetricTensor2
import jaxmat.materials as jm
import jaxmat
from jaxmat.neural_networks.icnn import ICNN

import optimistix as optx
import optax
import lineax as lx


current_path = Path().resolve()


class Ogden(eqx.Module):
    mu: jax.Array
    alpha: jax.Array

    def __call__(self, lamb):
        alp2 = self.alpha / 2
        return jnp.sum(
            self.mu
            / self.alpha
            * (lamb[0] ** alp2 + lamb[1] ** alp2 + lamb[2] ** alp2 - 3)
        )


data = np.loadtxt(current_path / "sandbox/Treloar_data.csv", skiprows=1, delimiter=",")
stress_data = []
load_data = []
for i in range(3):
    load_data.append(data[data[:, 2 * i] != np.inf, 2 * i])
    stress_data.append(data[data[:, 2 * i] != np.inf, 2 * i + 1])


def resample(x, y, N, downsample_ratio=0.0):
    xr = jnp.linspace(
        (1 + downsample_ratio) * min(x), (1 - downsample_ratio) * max(x), N
    )
    yr = jnp.interp(xr, x, y)
    return xr, yr


lamb1 = load_data[0]
lamb2 = load_data[1]
lamb3 = load_data[2]
P1 = stress_data[0]
P2 = stress_data[1]
P3 = stress_data[2]

Nsample = 50
dsratio = 0.0
lamb1, P1 = resample(lamb1, P1, Nsample, downsample_ratio=dsratio)
lamb2, P2 = resample(lamb2, P2, Nsample, downsample_ratio=dsratio)
lamb3, P3 = resample(lamb3, P3, Nsample, downsample_ratio=dsratio)

train_state1 = jnp.vstack((lamb1, 1 / jnp.sqrt(lamb1), 1 / jnp.sqrt(lamb1))).T
train_state2 = jnp.vstack((lamb2, jnp.ones_like(lamb2), 1 / lamb2)).T
train_state3 = jnp.vstack((lamb3, lamb3, 1 / lamb3**2)).T
train_state = jnp.vstack((train_state1, train_state2, train_state3))
# P = jnp.concatenate((P1, P2, P3))
# # training_input = {"uniax": train_state1, "equiax": train_state2, "biax": train_state3}
# training_output = {"uniax": P1, "equiax": P2, "biax": P3}
training_input = {"uniax": train_state1, "biax": train_state3}
training_output = {"uniax": P1, "biax": P3}


lamb_ = jnp.linspace(0.5, 12, 200)
out_train = jnp.vstack((lamb_, 1 / jnp.sqrt(lamb_), 1 / jnp.sqrt(lamb_))).T
# Pnorm = jnp.concatenate(
#     (jnp.full_like(P1, max(P1)), jnp.full_like(P2, max(P2)), jnp.full_like(P3, max(P3)))
# )
# Pnorm = jnp.ones_like(P)
# train_state = jnp.vstack((train_state1, train_state3))
# P = jnp.concatenate((P1, P3))


# data = np.loadtxt(
#     current_path / "sandbox/CANNsBRAINdata.csv", skiprows=0, delimiter=","
# )
# lamb1 = data[:, 0]
# gamma = data[:, 2]
# P1 = data[:, 1]
# P2 = data[:, 3]
# train_state1 = jnp.vstack((lamb1, 1 / jnp.sqrt(lamb1), 1 / jnp.sqrt(lamb1))).T
# lamb2 = jnp.sqrt(1 + gamma**2 / 4) + gamma / 2
# lamb2_ = jnp.sqrt(1 + gamma**2 / 4) - gamma / 2
# train_state2 = jnp.vstack((lamb2, lamb2_, jnp.ones_like(lamb2))).T
# training_input = {"uniax": train_state1, "shear": train_state2}
# training_output = {"uniax": P1, "shear": P2}

solver = optx.BFGS(
    rtol=1e-6,
    atol=1e-8,
    # linear_solver=lx.AutoLinearSolver(well_posed=False),
    verbose=frozenset({"loss", "step_size"}),
)

# solver = optx.OptaxMinimiser(
#     optax.adagrad(1e-3),
#     rtol=1e-4,
#     atol=1e-8,
#     # linear_solver=lx.AutoLinearSolver(well_posed=False),
#     verbose=frozenset({"loss", "step_size"}),
# )

key = jax.random.PRNGKey(42)
dim = 4
Ntrain = 50


class PANN(ICNN):
    base_material: eqx.Module

    def __init__(self, in_dim, hidden_dims, key, base_material):
        super().__init__(in_dim, hidden_dims, key)
        self.base_material = base_material

    def pann_energy(self, lambC):
        J = jnp.sqrt(jnp.prod(lambC))
        invariants = jnp.asarray(
            [
                jnp.sum(lambC) - 3,
                (lambC[1] * lambC[2])
                + (lambC[0] * lambC[2])
                + (lambC[0] * lambC[1])
                - 3,
                J**2,
                -2 * J,
            ]
        )
        return super().__call__(invariants)

    def __call__(self, lambC):
        return (
            self.pann_energy(lambC)
            - self.pann_energy(jnp.ones((4,)))
            + self.base_material(lambC)
        )


num_Ogd = 3
base_material = Ogden(
    2 + jax.random.normal(key, shape=num_Ogd),
    jax.random.uniform(key, shape=num_Ogd, minval=0.5, maxval=8.0),
)

material = PANN(dim, [10], key, base_material=base_material)

# def PANN(material, lambC):
#     J = jnp.sqrt(jnp.prod(lambC))
#     invariants = jnp.asarray(
#         [
#             jnp.sum(lambC),
#             (lambC[1] * lambC[2]) + (lambC[0] * lambC[2]) + (lambC[0] * lambC[1]),
#             J**2,
#         ]
#     )
#     return material(invariants) + (J + 1 / J - 2) ** 2


def compute_stress(material, state):
    lambC = state**2
    PK2 = 2 * jax.jacfwd(material)(lambC)
    PK2 = PK2 - 2 * jax.jacfwd(material)(jnp.ones(3))
    PK1 = jnp.diag(state) @ PK2
    return PK1


def pann_energy(material, state):
    lambC = state**2
    return material.pann_energy(lambC)


batched_compute_stress = jax.vmap(compute_stress, in_axes=(None, 0))
batched_pann_energy = jax.vmap(pann_energy, in_axes=(None, 0))


def loss(material, args):
    input, output, out_input = args

    def elem_loss(input, output):
        return batched_compute_stress(material, input)[:, 0] - output

    return jax.tree.map(elem_loss, input, output), 1e2 * batched_pann_energy(
        material, out_input
    )


sol = optx.least_squares(
    loss,
    solver,
    material,
    args=(training_input, training_output, out_train),
    has_aux=False,
    throw=False,
    max_steps=10000,
    # options={"jac": "bwd"},
)
print(sol.stats)
# +
results = sol.aux
new_material = sol.value
# new_material = material

# print(loss(new_material, train_state))

import matplotlib.pyplot as plt

for i, (test_state, Ptest) in enumerate(
    zip([train_state1, train_state2, train_state3], [P1, P2, P3])
):
    # for i, (test_state, Ptest) in enumerate(zip([train_state1, train_state2], [P1, P2])):
    plt.subplot(1, 3, i + 1)
    plt.plot(test_state[:, 0], Ptest, "xC3")
    results = batched_compute_stress(new_material, test_state)
    plt.plot(test_state[:, 0], results[:, 0], "-oC0")
    # plt.plot(jnp.sum(train_state**2, axis=1) - 3, P, "oC3")
    # plt.plot(jnp.sum(train_state**2, axis=1) - 3, results[:, 0], "xC0")
plt.show()
# plt.subplot(1, 3, 1)
plt.figure()
ampl = 0.3
lamb = jnp.linspace(
    (1 - ampl) * min(train_state1[:, 0]), (1 + ampl) * max(train_state1[:, 0]), 100
)
test_uniax = jnp.vstack((lamb, 1 / jnp.sqrt(lamb), 1 / jnp.sqrt(lamb))).T
uniax = batched_compute_stress(new_material, test_uniax)
plt.plot(lamb, uniax[:, 0], "xC1")
plt.show()
