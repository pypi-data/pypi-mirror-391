from collections.abc import Callable
from operator import not_ as negate


def nearly_equal(a: int | float, b: int | float) -> bool:
    return abs(a - b) < 0.00001


def equal_within(a: int | float, b: int | float, epsilon: float | int) -> bool:
    return abs(a - b) < epsilon


def match_empty(item: str | None | bool | set[str] | float) -> bool:
    return not bool(item)


def trivial_condition(n: object) -> bool:
    return True


def as_bool(object_: object) -> bool:
    return bool(object_)


def make_maybe_not(_negated: bool) -> Callable[[object], bool]:
    return negate if _negated else as_bool
