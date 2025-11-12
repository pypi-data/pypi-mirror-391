import re
from abc import ABC, abstractmethod
from collections.abc import Callable, Hashable, Iterable
from dataclasses import dataclass
from pathlib import Path
from types import UnionType
from typing import Annotated, Any, Protocol, Self, TypeVar

T = TypeVar("T")
H = TypeVar("H", bound=Hashable)


type Atomic = int | float | str | bool | None
type ClassInfo = type | UnionType | tuple["ClassInfo"]
type JSONPrimitive = int | float | str | None
type JSONDict = dict[str, JSONPrimitive | "JSONDict" | list["JSONDict | JSONPrimitive"]]
# alternative: JSONDict = dict[str, Union["JSONDict", str, list[str], tuple[str, ...], set[str]]]
type JSONList = list[JSONPrimitive | JSONDict]
type Endofunction[T] = Callable[[T], T]
type SequenceAlias[T] = list[T] | tuple[T] | set[T] | map[T] | filter[T]
_SequenceAliasVar = list | tuple | set | map | filter

_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)
_T_contra = TypeVar("_T_contra", contravariant=True)


def areinstances(iterable_instance: Iterable[Any], class_or_tuple: ClassInfo) -> bool:
    return all(map(lambda inst: isinstance(inst, class_or_tuple), iterable_instance))


def fallback_if_none(orig: T | None, alt: T) -> T:
    return alt if (orig is None) else orig


def call_fallback_if_none(orig: T | None, alt: Callable[[], T]) -> T:
    return alt() if (orig is None) else orig


class SupportsGe(Protocol):
    def __ge__(self: T, __other: T) -> bool: ...


class SupportsGt(Protocol):
    def __gt__(self: T, __other: T) -> bool: ...


class SupportsLe(Protocol):
    def __le__(self: T, __other: T) -> bool: ...


class SupportsLt(Protocol):
    def __lt__(self: T, __other: T) -> bool: ...


@dataclass(frozen=True)
class _BaseMetadata:
    """Base class for all metadata.

    This exists mainly so that implementers
    can do `isinstance(..., BaseMetadata)` while traversing field annotations.
    """

    __slots__ = ()


@dataclass(frozen=True)
class Ge(_BaseMetadata):
    """Ge(ge=x) implies that the value must be greater than or equal to x.

    It can be used with any type that supports the ``>=`` operator,
    including numbers, dates and times, strings, sets, and so on.
    """

    ge: SupportsGe


@dataclass(frozen=True)
class Gt(_BaseMetadata):
    """Gt(gt=x) implies that the value must be greater than x.

    It can be used with any type that supports the ``>`` operator,
    including numbers, dates and times, strings, sets, and so on.
    """

    gt: SupportsGt


@dataclass(frozen=True)
class Lt(_BaseMetadata):
    """Lt(lt=x) implies that the value must be less than x.

    It can be used with any type that supports the ``<`` operator,
    including numbers, dates and times, strings, sets, and so on.
    """

    lt: SupportsLt


@dataclass(frozen=True)
class Le(_BaseMetadata):
    """Le(le=x) implies that the value must be less than x.

    It can be used with any type that supports the ``<=`` operator,
    including numbers, dates and times, strings, sets, and so on.
    """

    le: SupportsLe


class SupportsIO(ABC):
    @classmethod
    @abstractmethod
    def read(cls, read_path: Path) -> Self: ...

    @abstractmethod
    def write(self, write_path: Path) -> None: ...


class Pattern:
    DATE: re.Pattern[str] = re.compile(r"^[12]\d\d\d-(0?\d|1[012]|)-(0?\d|[12]\d|3[01])$")
    DATE_STRICT: re.Pattern[str] = re.compile(r"^[12]\d\d\d-(0\d|1[012]|)-(0\d|[12]\d|3[01])$")
    DATE_LOOSE: re.Pattern[str] = re.compile(r"(\d{2,4})[^\d](\d\d?)[^\d](\d\d?)")
    ID: re.Pattern[str] = re.compile(r"^[A-Za-z][A-Za-z0-9_]+$")
    ID_OR_2IDS: re.Pattern[str] = re.compile(r"^[A-Za-z][A-Za-z0-9_]+,[A-Za-z][A-Za-z0-9_]+$")
    NATURAL: re.Pattern[str] = re.compile(r"^[1-9][0-9]*$")
    PROPORTION: re.Pattern[str] = re.compile(r"^0?\.[0-9]+$")
    PROPORTION_OR_2: re.Pattern[str] = re.compile(r"^0?\.[0-9]+$|^0?\.[0-9]+,0?\.[0-9]+$")


TimeAmountRaw = str | int

Natural = Annotated[int, Ge(ge=0)]
Nonnegative = Annotated[float, Ge(ge=0)]
Positive = Annotated[float, Gt(gt=0)]
PositiveScore = Annotated[float, Gt(gt=0.0), Lt(lt=5.0)]
NegativeScore = Annotated[float, Gt(gt=-5.0), Lt(lt=0.0)]
Proportion = Annotated[float, Ge(ge=0.0), Le(le=1.0)]
NonnegativeInt = Annotated[int, Ge(ge=0)]
NonnegativeFloat = Annotated[float, Ge(ge=0.0)]
PolarityScore = Annotated[float, Ge(ge=-1.0), Le(le=1.0)]


def ensure_set(x: H | SequenceAlias[H]) -> set[H]:
    return set(x) if isinstance(x, _SequenceAliasVar) else {x}


def ensure_tuple(x: T | SequenceAlias[T]) -> tuple[T, ...]:
    return tuple(x) if isinstance(x, _SequenceAliasVar) else (x,)


def ensure_list(x: T | SequenceAlias[T]) -> list[T]:
    return list(x) if isinstance(x, _SequenceAliasVar) else [x]


# ==============


class IdentityFunction(Protocol):
    def __call__(self, x: _T, /) -> _T: ...


# stable
class SupportsNext(Protocol[_T_co]):
    def __next__(self) -> _T_co: ...


class SupportsBool(Protocol):
    def __bool__(self) -> bool: ...


# Comparison protocols
class SupportsDunderLT(Protocol[_T_contra]):
    def __lt__(self, other: _T_contra, /) -> SupportsBool: ...


class SupportsDunderGT(Protocol[_T_contra]):
    def __gt__(self, other: _T_contra, /) -> SupportsBool: ...


class SupportsDunderLE(Protocol[_T_contra]):
    def __le__(self, other: _T_contra, /) -> SupportsBool: ...


class SupportsDunderGE(Protocol[_T_contra]):
    def __ge__(self, other: _T_contra, /) -> SupportsBool: ...


class SupportsAllComparisons(
    SupportsDunderLT[Any],
    SupportsDunderGT[Any],
    SupportsDunderLE[Any],
    SupportsDunderGE[Any],
    Protocol,
): ...


type SupportsRichComparison = SupportsDunderLT[Any] | SupportsDunderGT[Any]
SupportsRichComparisonT = TypeVar("SupportsRichComparisonT", bound=SupportsRichComparison)

C = TypeVar("C", bound=SupportsRichComparison)
