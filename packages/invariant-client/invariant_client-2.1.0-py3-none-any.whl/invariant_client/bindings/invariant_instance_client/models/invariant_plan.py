from enum import Enum


class InvariantPlan(str, Enum):
    CAPACITY = "capacity"
    CAPACITY_ENTERPRISE = "capacity_enterprise"
    FREE = "free"
    PAYGO = "paygo"
    PAYGO_ENTERPRISE = "paygo_enterprise"
    PRO = "pro"
    TRIAL = "trial"

    def __str__(self) -> str:
        return str(self.value)
