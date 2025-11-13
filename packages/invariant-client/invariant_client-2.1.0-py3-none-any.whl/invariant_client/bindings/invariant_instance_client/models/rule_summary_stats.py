from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RuleSummaryStats")


@_attrs_define
class RuleSummaryStats:
    """
    Attributes:
        pass_count (int):
        fail_count (int):
        error_count (int):
        total_rules (int):
    """

    pass_count: int
    fail_count: int
    error_count: int
    total_rules: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pass_count = self.pass_count

        fail_count = self.fail_count

        error_count = self.error_count

        total_rules = self.total_rules

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pass_count": pass_count,
                "fail_count": fail_count,
                "error_count": error_count,
                "total_rules": total_rules,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        pass_count = d.pop("pass_count")

        fail_count = d.pop("fail_count")

        error_count = d.pop("error_count")

        total_rules = d.pop("total_rules")

        rule_summary_stats = cls(
            pass_count=pass_count,
            fail_count=fail_count,
            error_count=error_count,
            total_rules=total_rules,
        )

        rule_summary_stats.additional_properties = d
        return rule_summary_stats

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
