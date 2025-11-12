from typing import Any, cast
from beartype.door import die_if_unbearable


class Check[A]:  # type: ignore
    pass


def bearcheck[T](a: Any, check: type[Check[T]]) -> T:
    args = getattr(check, "__args__", None)
    if args is None:
        raise ValueError("Check class must be templated e.g. Check[int | str]")
    die_if_unbearable(a, args[0])
    return cast(T, a)
