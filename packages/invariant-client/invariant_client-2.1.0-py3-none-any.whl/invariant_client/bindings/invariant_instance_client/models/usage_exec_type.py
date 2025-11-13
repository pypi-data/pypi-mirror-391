from enum import Enum


class UsageExecType(str, Enum):
    EVAL = "eval"
    UPLOAD_SNAPSHOT = "upload_snapshot"

    def __str__(self) -> str:
        return str(self.value)
