from enum import Enum


class ResourceType(str, Enum):
    DEFS = "DEFS"
    LOCATIONS = "LOCATIONS"
    MODEL_ADJUSTMENTS = "MODEL_ADJUSTMENTS"
    RULES = "RULES"
    YAML_SALAD = "YAML_SALAD"

    def __str__(self) -> str:
        return str(self.value)
