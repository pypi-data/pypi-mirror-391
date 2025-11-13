from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.rule_outcome import RuleOutcome
from ..models.rule_type import RuleType
from ..types import UNSET, Unset

T = TypeVar("T", bound="PolicyFileResultRule")


@_attrs_define
class PolicyFileResultRule:
    """
    Attributes:
        status (RuleOutcome): Rule evaluation outcome.
        rule_type (Union[None, RuleType]):
        comment (Union[None, Unset, str]):
        errors (Union[None, Unset, list[str]]):
    """

    status: RuleOutcome
    rule_type: Union[None, RuleType]
    comment: Union[None, Unset, str] = UNSET
    errors: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status.value

        rule_type: Union[None, str]
        if isinstance(self.rule_type, RuleType):
            rule_type = self.rule_type.value
        else:
            rule_type = self.rule_type

        comment: Union[None, Unset, str]
        if isinstance(self.comment, Unset):
            comment = UNSET
        else:
            comment = self.comment

        errors: Union[None, Unset, list[str]]
        if isinstance(self.errors, Unset):
            errors = UNSET
        elif isinstance(self.errors, list):
            errors = self.errors

        else:
            errors = self.errors

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "rule_type": rule_type,
            }
        )
        if comment is not UNSET:
            field_dict["comment"] = comment
        if errors is not UNSET:
            field_dict["errors"] = errors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = RuleOutcome(d.pop("status"))

        def _parse_rule_type(data: object) -> Union[None, RuleType]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                rule_type_type_0 = RuleType(data)

                return rule_type_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, RuleType], data)

        rule_type = _parse_rule_type(d.pop("rule_type"))

        def _parse_comment(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        comment = _parse_comment(d.pop("comment", UNSET))

        def _parse_errors(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                errors_type_0 = cast(list[str], data)

                return errors_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        errors = _parse_errors(d.pop("errors", UNSET))

        policy_file_result_rule = cls(
            status=status,
            rule_type=rule_type,
            comment=comment,
            errors=errors,
        )

        policy_file_result_rule.additional_properties = d
        return policy_file_result_rule

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
