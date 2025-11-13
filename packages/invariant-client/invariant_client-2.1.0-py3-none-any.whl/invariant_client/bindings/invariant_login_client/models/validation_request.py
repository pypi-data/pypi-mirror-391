from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ValidationRequest")


@_attrs_define
class ValidationRequest:
    """Respond to the validate_email challenge.

    Attributes:
        type_ (Literal['email_valid']):
        pin (str):
    """

    type_: Literal["email_valid"]
    pin: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        pin = self.pin

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "pin": pin,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["email_valid"], d.pop("type"))
        if type_ != "email_valid":
            raise ValueError(f"type must match const 'email_valid', got '{type_}'")

        pin = d.pop("pin")

        validation_request = cls(
            type_=type_,
            pin=pin,
        )

        validation_request.additional_properties = d
        return validation_request

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
