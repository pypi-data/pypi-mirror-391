import jax
import jax.numpy as jnp
import numpy as np
from jaxopt import ProximalGradient, ProjectedGradient
from jaxopt.prox import prox_lasso
from jaxopt.projection import projection_linf_ball, projection_l2_ball
import matplotlib.pyplot as plt
from time import time

jax.config.update("jax_enable_x64", True)


def project_onto_lorentz_cone(v):
    """Project (t, x) in R^{1+n} onto the Lorentz (second-order) cone."""
    t = v[0]
    x = v[1:]
    norm_x = jnp.linalg.norm(x)

    # Case 1: already in the cone
    def case1():
        return v

    # Case 2: projection is origin
    def case2():
        return jnp.zeros_like(v)

    # Case 3: general projection
    def case3():
        alpha = 0.5 * (1 + t / norm_x)
        projected_t = alpha * norm_x
        projected_x = alpha * x
        return jnp.concatenate([jnp.array([projected_t]), projected_x])

    return jnp.where(norm_x <= t, case1(), jnp.where(norm_x <= -t, case2(), case3()))


# x = jnp.array([-1.25, 1.0])
# print(project_onto_lorentz_cone(x))
# raise

E = 200e3
nu = 0.3
sig0 = 350.0
sigu = 500.0
b = 1e3
lmbda = E * nu / (1 + nu) / (1 - 2 * nu)
mu = E / 2 / (1 + nu) / (1 - 2 * nu)


def hardening(p):
    return (sigu - sig0) * (p + jnp.exp(-b * p) / b)


def sph(eps):
    return jnp.linalg.trace(eps) / 3 * jnp.eye(3)


def dev(eps):
    return eps - sph(eps)


def dev_vect(eps):
    eps_ = eps.reshape((3, 3))
    return dev(eps_).ravel()


def psi_el(eps):
    eps = eps.reshape((3, 3))
    return lmbda / 2 * jnp.trace(sph(eps) @ sph(eps)) + mu * jnp.trace(
        dev(eps) @ dev(eps)
    )


def least_squares(x, eps):
    p = x[0]
    epsp = x[1:]
    return psi_el(eps - epsp) + hardening(p)


def prox(x, hyperparams, scale=1.0):
    x_ = x.at[0].set(x[0] - hyperparams * scale)
    x_ = x_.at[1:].set(dev_vect(x_[1:]))
    return project_onto_lorentz_cone(x_)


# x = jnp.linspace(-2, 2, 100)
# print([projection_l2_ball(xi, max_value=1.0) for xi in x])

# plt.plot(x, prox_lasso(x, l1reg=1.0))
# # plt.plot(x, projection_l2_ball(x, max_value=1))
# # plt.plot(eps, prox(eps, 1.0))
# plt.show()
# raise


pg = ProximalGradient(fun=least_squares, prox=prox, tol=1e-6, implicit_diff=True)


def compute_stress(eps, x_old):
    solve = pg.run(x_old, hyperparams_prox=sig0, eps=eps)
    x = solve.params
    sig = jax.grad(least_squares, argnums=1)(x, eps)
    return sig, x


Nsteps = int(1e3)
eps = jnp.kron(
    jnp.linspace(0, 10e-3, Nsteps + 1)[:, None],
    jnp.diag(jnp.asarray([1, -0.5, -0.5], dtype=jnp.float64)).ravel()[None, :],
)
x_old = np.zeros((Nsteps + 1, 10))

tic = time()
sig, x = jax.block_until_ready(jax.jit(jax.vmap(compute_stress))(eps, x_old))
print("Evaluation:", (time() - tic) / Nsteps)

plt.figure()
plt.plot(eps[:, 0], sig[:, 0], "-C3")
plt.plot(eps[:, 0], sig[:, 1], "-C2")
plt.show()
