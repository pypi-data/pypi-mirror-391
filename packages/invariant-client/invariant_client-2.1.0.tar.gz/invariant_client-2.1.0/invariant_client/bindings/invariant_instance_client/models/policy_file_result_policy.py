from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.policy_file_result_rule import PolicyFileResultRule


T = TypeVar("T", bound="PolicyFileResultPolicy")


@_attrs_define
class PolicyFileResultPolicy:
    """
    Attributes:
        name (str):
        rules (list['PolicyFileResultRule']):
        policy_errors (Union[None, Unset, list[str]]):
        comment (Union[None, Unset, str]):
        owner (Union[None, Unset, str]):
    """

    name: str
    rules: list["PolicyFileResultRule"]
    policy_errors: Union[None, Unset, list[str]] = UNSET
    comment: Union[None, Unset, str] = UNSET
    owner: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        rules = []
        for rules_item_data in self.rules:
            rules_item = rules_item_data.to_dict()
            rules.append(rules_item)

        policy_errors: Union[None, Unset, list[str]]
        if isinstance(self.policy_errors, Unset):
            policy_errors = UNSET
        elif isinstance(self.policy_errors, list):
            policy_errors = self.policy_errors

        else:
            policy_errors = self.policy_errors

        comment: Union[None, Unset, str]
        if isinstance(self.comment, Unset):
            comment = UNSET
        else:
            comment = self.comment

        owner: Union[None, Unset, str]
        if isinstance(self.owner, Unset):
            owner = UNSET
        else:
            owner = self.owner

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "rules": rules,
            }
        )
        if policy_errors is not UNSET:
            field_dict["policy_errors"] = policy_errors
        if comment is not UNSET:
            field_dict["comment"] = comment
        if owner is not UNSET:
            field_dict["owner"] = owner

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.policy_file_result_rule import PolicyFileResultRule

        d = dict(src_dict)
        name = d.pop("name")

        rules = []
        _rules = d.pop("rules")
        for rules_item_data in _rules:
            rules_item = PolicyFileResultRule.from_dict(rules_item_data)

            rules.append(rules_item)

        def _parse_policy_errors(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                policy_errors_type_0 = cast(list[str], data)

                return policy_errors_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        policy_errors = _parse_policy_errors(d.pop("policy_errors", UNSET))

        def _parse_comment(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        comment = _parse_comment(d.pop("comment", UNSET))

        def _parse_owner(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        owner = _parse_owner(d.pop("owner", UNSET))

        policy_file_result_policy = cls(
            name=name,
            rules=rules,
            policy_errors=policy_errors,
            comment=comment,
            owner=owner,
        )

        policy_file_result_policy.additional_properties = d
        return policy_file_result_policy

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
