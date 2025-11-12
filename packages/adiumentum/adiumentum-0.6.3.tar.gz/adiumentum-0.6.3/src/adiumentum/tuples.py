""" """

from collections.abc import Callable, Iterable, Sequence
from typing import (
    TYPE_CHECKING,
    TypeVar,
    TypeVarTuple,
    cast,
    overload,
)

from .functional import identity

if TYPE_CHECKING:
    from _typeshed import SupportsRichComparison
else:
    type SupportsRichComparison = float

S = TypeVar("S")
T = TypeVar("T")
Tup = TypeVar("Tup", bound=tuple)
Ts = TypeVarTuple("Ts")
C = TypeVar("C", bound=SupportsRichComparison)


@overload
def keep_first[T, *Ts](tups: list[tuple[T, *Ts]]) -> list[T]: ...
@overload
def keep_first[T, *Ts](tups: tuple[tuple[T, *Ts], ...]) -> tuple[T, ...]: ...
def keep_first[T, *Ts](tups: Iterable[tuple[T, *Ts]]) -> Sequence[T]:
    if isinstance(tups, list):
        return [t[0] for t in tups]
    return tuple(t[0] for t in tups)


@overload
def keep_second[S, T, *Ts](tups: tuple[tuple[S, T, *Ts], ...]) -> tuple[T, ...]: ...
@overload
def keep_second[S, T, *Ts](tups: list[tuple[S, T, *Ts]]) -> list[T]: ...
def keep_second[S, T, *Ts](tups: Iterable[tuple[S, T, *Ts]]) -> Sequence[T]:
    if isinstance(tups, list):
        return [t[1] for t in tups]
    return tuple(t[1] for t in tups)


@overload
def keep_last[*Ts, T](tups: tuple[tuple[*Ts, T], ...]) -> tuple[T, ...]: ...
@overload
def keep_last[*Ts, T](tups: list[tuple[*Ts, T]]) -> list[T]: ...
def keep_last[*Ts, T](tups: Iterable[tuple[*Ts, T]]) -> Sequence[T]:
    if isinstance(tups, list):
        return [t[-1] for t in tups]
    return tuple(t[-1] for t in tups)


def _make_selector(
    u: int | slice | tuple[int, ...] | None = None,
) -> Callable[[tuple[object, ...]], object]:
    u = u if u is not None else slice(None)

    if isinstance(u, tuple):

        def _use(t: tuple[object, ...]) -> object:
            return tuple(t[i] for i in u)

    else:

        def _use(t: tuple[object, ...]) -> object:
            return t[u]

    return _use


@overload
def filter_tuples[Tup](
    seq: tuple[Tup, ...],
    *,
    use: int | slice | tuple[int,] | None = None,
    condition: Callable[[object], bool] = bool,
) -> tuple[Tup, ...]: ...


@overload
def filter_tuples[Tup](
    seq: list[Tup],
    *,
    use: int | slice | tuple[int,] | None = None,
    condition: Callable[[object], bool] = bool,
) -> Sequence[Tup]: ...


def filter_tuples[Tup](
    seq: Iterable[Tup],
    *,
    use: int | slice | tuple[int,] | None = None,
    condition: Callable[[object], bool] = bool,
) -> Sequence[Tup]:
    use = use if use is not None else slice(use)
    select = _make_selector(use)

    def _condition(elem: Tup) -> bool:
        return condition(select(cast(tuple[object, ...], elem)))

    filtered = filter(_condition, seq)
    if isinstance(seq, list):
        return list(filtered)
    return tuple(filtered)


@overload
def sort_tuples[Tup](
    seq: list[Tup],
    *,
    use: int | slice | tuple[int,] | None = None,
    key: Callable[[Tup], SupportsRichComparison] | None = None,
) -> list[Tup]: ...


@overload
def sort_tuples[Tup](
    seq: tuple[Tup, ...],
    *,
    use: int | slice | tuple[int,] | None = None,
    key: Callable[[Tup], SupportsRichComparison] | None = None,
) -> tuple[Tup, ...]: ...


def sort_tuples[Tup](
    seq: Iterable[Tup],
    *,
    use: int | slice | tuple[int,] | None = None,
    key: Callable[[Tup], SupportsRichComparison] | None = None,
) -> Sequence[Tup]:
    select = _make_selector(use)

    key = key if key is not None else cast(Callable[[Tup], SupportsRichComparison], identity)

    def _key(elem: Tup) -> SupportsRichComparison:
        selected = cast(Tup, select(cast(tuple[object, ...], elem)))
        return key(selected)

    return (list if isinstance(seq, list) else tuple)(sorted(seq, key=_key))
