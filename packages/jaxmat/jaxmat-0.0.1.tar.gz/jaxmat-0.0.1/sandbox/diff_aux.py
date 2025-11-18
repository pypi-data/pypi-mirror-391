import jax
import jax.numpy as jnp
import optimistix as optx


def compute_sqrt(x):
    def fn(y, args):
        def expensive_function(y):
            return y**2

        return y**2 - args, expensive_function(y)

    solver = optx.Newton(rtol=1e-5, atol=1e-5)

    y0 = jnp.array(1.0)
    sol = optx.root_find(fn, solver, y0, x, has_aux=True)
    sqrt_x = sol.value
    x_ = sol.aux
    return sqrt_x, x_


x0 = 2.0
print(compute_sqrt(x0))
print(jax.jacobian(compute_sqrt)(x0))
