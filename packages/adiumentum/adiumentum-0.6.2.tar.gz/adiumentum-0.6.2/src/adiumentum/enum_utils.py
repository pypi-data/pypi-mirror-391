from enum import StrEnum


class StrEnumUpper(StrEnum):
    """ """

    @staticmethod
    def _generate_next_value_(name: str, start, count, last_values):  # type: ignore
        return name

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}.{self.name}"
