from enum import Enum


class BuiltInRole(str, Enum):
    EVALUATOR = "evaluator"
    NETWORK_MANAGER = "network_manager"
    UPLOAD_ONLY = "upload_only"
    WORKSPACE_MANAGER = "workspace_manager"

    def __str__(self) -> str:
        return str(self.value)
