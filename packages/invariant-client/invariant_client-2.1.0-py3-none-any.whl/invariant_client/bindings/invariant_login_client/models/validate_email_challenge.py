from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ValidateEmailChallenge")


@_attrs_define
class ValidateEmailChallenge:
    """The user must prove control of the email address by PIN before gaining access to the account.

    Attributes:
        type_ (Literal['validate_email']):
    """

    type_: Literal["validate_email"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["validate_email"], d.pop("type"))
        if type_ != "validate_email":
            raise ValueError(f"type must match const 'validate_email', got '{type_}'")

        validate_email_challenge = cls(
            type_=type_,
        )

        validate_email_challenge.additional_properties = d
        return validate_email_challenge

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
