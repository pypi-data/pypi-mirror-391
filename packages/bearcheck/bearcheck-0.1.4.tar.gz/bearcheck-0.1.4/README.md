# bearcheck

Tiny extension to [beartype](https://github.com/beartype/),
which allows inline type assertion and narrowing similar to
[check_type](https://typeguard.readthedocs.io/en/stable/api.html#typeguard.check_type)
from [typeguard](https://github.com/agronholm/typeguard).

Using `bearcheck()` is *faster* and *safer* than `check_type()`, since it
leverages the incredibly fast *beartype* library for type checking, and
allows specifying the exact return type.

### Usage

```python
from bearcheck import bearcheck, Check

var = bearcheck("a", Check[Literal["a", "b"]])
reveal_type(var)  # Type of "var" is "Literal['a', 'b']"
```

.. as opposed to ..

```python
from typeguard import check_type

var = check_type("a", Literal["a", "b"])
reveal_type(var)  # Type of "var" is "Any"
```

`type_check()` returns *Any* if the type hint is not primitive, a common pitfall!
