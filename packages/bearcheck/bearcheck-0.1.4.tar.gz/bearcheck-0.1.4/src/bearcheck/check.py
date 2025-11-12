from typing import Any, Generic, TypeVar, cast
from beartype.door import die_if_unbearable, is_bearable


CheckType = TypeVar("CheckType")


class Check(Generic[CheckType]):  # type: ignore
    pass


def bearcheck(a: Any, check: type[Check[CheckType]]) -> CheckType:
    args = getattr(check, "__args__", None)
    if args is None:
        if not isinstance(check, Check):
            raise ValueError(f"Not a valid Check class: {check!r}")
        raise ValueError("Check class must be templated e.g. Check[int | str]")
    die_if_unbearable(a, args[0])
    return cast(CheckType, a)


def beartest(a: Any, check: type[Check[CheckType]]) -> CheckType | None:
    args = getattr(check, "__args__", None)
    if args is None:
        if not isinstance(check, Check):
            raise ValueError(f"Not a valid Check class: {check!r}")
        raise ValueError("Check class must be templated e.g. Check[int | str]")
    if is_bearable(a, args[0]):
        return cast(CheckType, a)
    return None
