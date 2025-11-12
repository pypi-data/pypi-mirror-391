import re
from typing import Iterable

from .typing_utils import areinstances


def re_bool_search(p: re.Pattern[str], s: str | None) -> bool:
    if not s:
        return False
    return bool(re.search(p, s))


def re_bool_search_any(pattern: re.Pattern[str], strings: Iterable[str] | None) -> bool:
    """
    TODO: Move to adiumentum
    """
    if not strings:
        return False
    for s in strings:
        if re.search(pattern, s):
            return True
    return False


def re_split(expr: str | re.Pattern[str], s: str) -> list[str]:
    segments = re.split(expr, s)
    if not areinstances(segments, str):
        raise TypeError("Function 're_split' may only return a list of strings.")
    return segments


def escape_character(s: str) -> str:
    return {
        ".": "\\.",
        "?": "\\?",
        "|": "\\|",
        "*": "\\*",
        "+": "\\+",
        "^": "\\^",
        "[": "\\[",
        "]": "\\]",
        "{": "\\{",
        "}": "\\}",
        "(": "\\(",
        ")": "\\)",
    }.get(s, s)
