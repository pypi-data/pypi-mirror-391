from enum import Enum


class RuleOutcome(str, Enum):
    ERROR = "error"
    FAIL = "fail"
    PASS = "pass"

    def __str__(self) -> str:
        return str(self.value)
