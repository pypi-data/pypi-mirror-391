from enum import Enum


class GenericState(str, Enum):
    ERROR = "error"
    OK = "ok"

    def __str__(self) -> str:
        return str(self.value)
