from enum import Enum


class InvariantPrice(str, Enum):
    CAPACITY_ENTERPRISE_TIERED = "capacity_enterprise_tiered"
    CAPACITY_STANDARD_TIERED = "capacity_standard_tiered"
    PRO_PLAN_MONTHLY = "pro_plan_monthly"
    USAGE_ENTERPRISE_METERED = "usage_enterprise_metered"
    USAGE_STANDARD_METERED = "usage_standard_metered"

    def __str__(self) -> str:
        return str(self.value)
