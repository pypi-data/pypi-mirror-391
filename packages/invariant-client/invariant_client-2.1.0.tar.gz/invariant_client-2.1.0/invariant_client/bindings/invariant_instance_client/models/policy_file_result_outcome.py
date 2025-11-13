from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.policy_file_result_policy import PolicyFileResultPolicy


T = TypeVar("T", bound="PolicyFileResultOutcome")


@_attrs_define
class PolicyFileResultOutcome:
    """
    Attributes:
        original_filename (str):
        policies (list['PolicyFileResultPolicy']):
        file_errors (Union[None, Unset, list[str]]):
    """

    original_filename: str
    policies: list["PolicyFileResultPolicy"]
    file_errors: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        original_filename = self.original_filename

        policies = []
        for policies_item_data in self.policies:
            policies_item = policies_item_data.to_dict()
            policies.append(policies_item)

        file_errors: Union[None, Unset, list[str]]
        if isinstance(self.file_errors, Unset):
            file_errors = UNSET
        elif isinstance(self.file_errors, list):
            file_errors = self.file_errors

        else:
            file_errors = self.file_errors

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "original_filename": original_filename,
                "policies": policies,
            }
        )
        if file_errors is not UNSET:
            field_dict["file_errors"] = file_errors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.policy_file_result_policy import PolicyFileResultPolicy

        d = dict(src_dict)
        original_filename = d.pop("original_filename")

        policies = []
        _policies = d.pop("policies")
        for policies_item_data in _policies:
            policies_item = PolicyFileResultPolicy.from_dict(policies_item_data)

            policies.append(policies_item)

        def _parse_file_errors(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                file_errors_type_0 = cast(list[str], data)

                return file_errors_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        file_errors = _parse_file_errors(d.pop("file_errors", UNSET))

        policy_file_result_outcome = cls(
            original_filename=original_filename,
            policies=policies,
            file_errors=file_errors,
        )

        policy_file_result_outcome.additional_properties = d
        return policy_file_result_outcome

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
