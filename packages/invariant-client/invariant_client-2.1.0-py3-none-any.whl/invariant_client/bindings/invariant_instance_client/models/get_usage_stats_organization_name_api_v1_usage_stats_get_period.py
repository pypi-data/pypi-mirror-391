from enum import Enum


class GetUsageStatsOrganizationNameApiV1UsageStatsGetPeriod(str, Enum):
    DAY = "day"
    MONTH = "month"

    def __str__(self) -> str:
        return str(self.value)
