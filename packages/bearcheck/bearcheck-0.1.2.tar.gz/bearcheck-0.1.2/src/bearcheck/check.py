from typing import Any, cast
from beartype.door import die_if_unbearable, is_bearable


class Check[A]:  # type: ignore
    pass


def bearcheck[T](a: Any, check: type[Check[T]]) -> T:
    args = getattr(check, "__args__", None)
    if args is None:
        if not isinstance(check, Check):
            raise ValueError("Not a valid Check class: {check!r}")
        raise ValueError("Check class must be templated e.g. Check[int | str]")
    die_if_unbearable(a, args[0])
    return cast(T, a)


def beartest[T](a: Any, check: type[Check[T]]) -> T | None:
    args = getattr(check, "__args__", None)
    if args is None:
        if not isinstance(check, Check):
            raise ValueError("Not a valid Check class: {check!r}")
        raise ValueError("Check class must be templated e.g. Check[int | str]")
    if is_bearable(a, args[0]):
        return cast(T, a)
    return None
