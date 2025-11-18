import equinox as eqx


class BaseModule(eqx.Module):
    default_attr: int = eqx.field(static=True, init=False, default=42)


class SubModule(BaseModule):
    required_attr: float  # no default, so required argument in __init__
    another_required: str
    another_default_arg = 0.0


# Now you can instantiate:
sub = SubModule(3.14, "hello")
print(sub.default_attr)  # 42 from base
