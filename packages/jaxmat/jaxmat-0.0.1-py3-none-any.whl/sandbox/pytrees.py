import jax.numpy as jnp
import equinox as eqx
import jax


class MyTree(eqx.Module):
    a: jax.Array
    b: jax.Array
    c: jax.Array

    def __init__(self):
        self.a = jnp.zeros((3,))
        self.b = jnp.ones((5,))
        self.c = jnp.zeros((5,), dtype=jnp.bool)


tree = MyTree()
print(tree)
# new_leaf = 5
get_leaf = lambda t: t.a
new_tree = eqx.tree_at(get_leaf, tree, replace_fn=lambda x: x.at[0].set(5))
print(new_tree.a)
