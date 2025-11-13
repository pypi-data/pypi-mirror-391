from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.policy_file_result import PolicyFileResult
    from ..models.rule_summary_stats import RuleSummaryStats


T = TypeVar("T", bound="RuleSummaryGroupUploaded")


@_attrs_define
class RuleSummaryGroupUploaded:
    """
    Attributes:
        stats (RuleSummaryStats):
        name (str):
        policies (list['PolicyFileResult']):
        type_ (Union[Literal['uploaded'], Unset]):  Default: 'uploaded'.
    """

    stats: "RuleSummaryStats"
    name: str
    policies: list["PolicyFileResult"]
    type_: Union[Literal["uploaded"], Unset] = "uploaded"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        stats = self.stats.to_dict()

        name = self.name

        policies = []
        for policies_item_data in self.policies:
            policies_item = policies_item_data.to_dict()
            policies.append(policies_item)

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stats": stats,
                "name": name,
                "policies": policies,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.policy_file_result import PolicyFileResult
        from ..models.rule_summary_stats import RuleSummaryStats

        d = dict(src_dict)
        stats = RuleSummaryStats.from_dict(d.pop("stats"))

        name = d.pop("name")

        policies = []
        _policies = d.pop("policies")
        for policies_item_data in _policies:
            policies_item = PolicyFileResult.from_dict(policies_item_data)

            policies.append(policies_item)

        type_ = cast(Union[Literal["uploaded"], Unset], d.pop("type", UNSET))
        if type_ != "uploaded" and not isinstance(type_, Unset):
            raise ValueError(f"type must match const 'uploaded', got '{type_}'")

        rule_summary_group_uploaded = cls(
            stats=stats,
            name=name,
            policies=policies,
            type_=type_,
        )

        rule_summary_group_uploaded.additional_properties = d
        return rule_summary_group_uploaded

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
