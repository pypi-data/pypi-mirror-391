from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UsageStats")


@_attrs_define
class UsageStats:
    """Counts usages.

    Attributes:
        periods (list[int]):
        uploads (list[int]):
        pro (list[int]):
        basic (list[int]):
        basic_eval (list[int]):
    """

    periods: list[int]
    uploads: list[int]
    pro: list[int]
    basic: list[int]
    basic_eval: list[int]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        periods = self.periods

        uploads = self.uploads

        pro = self.pro

        basic = self.basic

        basic_eval = self.basic_eval

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "periods": periods,
                "uploads": uploads,
                "pro": pro,
                "basic": basic,
                "basic_eval": basic_eval,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        periods = cast(list[int], d.pop("periods"))

        uploads = cast(list[int], d.pop("uploads"))

        pro = cast(list[int], d.pop("pro"))

        basic = cast(list[int], d.pop("basic"))

        basic_eval = cast(list[int], d.pop("basic_eval"))

        usage_stats = cls(
            periods=periods,
            uploads=uploads,
            pro=pro,
            basic=basic,
            basic_eval=basic_eval,
        )

        usage_stats.additional_properties = d
        return usage_stats

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
