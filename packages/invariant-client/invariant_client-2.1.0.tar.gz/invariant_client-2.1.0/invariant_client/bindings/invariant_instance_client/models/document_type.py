from enum import Enum


class DocumentType(str, Enum):
    AWS_DESCRIBE = "AWS_DESCRIBE"
    BATFISH_JSON = "BATFISH_JSON"
    INVARIANT_YAML_SPEC = "INVARIANT_YAML_SPEC"
    NET_CONFIG = "NET_CONFIG"
    RESOURCE_SET = "RESOURCE_SET"

    def __str__(self) -> str:
        return str(self.value)
