from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.credit_stats import CreditStats
    from ..models.usage_stats import UsageStats


T = TypeVar("T", bound="UsageStatsResponse")


@_attrs_define
class UsageStatsResponse:
    """
    Attributes:
        period (str):
        stats (UsageStats): Counts usages.
        credit_stats (CreditStats): Represents credit costs.
    """

    period: str
    stats: "UsageStats"
    credit_stats: "CreditStats"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        period = self.period

        stats = self.stats.to_dict()

        credit_stats = self.credit_stats.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "period": period,
                "stats": stats,
                "credit_stats": credit_stats,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.credit_stats import CreditStats
        from ..models.usage_stats import UsageStats

        d = dict(src_dict)
        period = d.pop("period")

        stats = UsageStats.from_dict(d.pop("stats"))

        credit_stats = CreditStats.from_dict(d.pop("credit_stats"))

        usage_stats_response = cls(
            period=period,
            stats=stats,
            credit_stats=credit_stats,
        )

        usage_stats_response.additional_properties = d
        return usage_stats_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
