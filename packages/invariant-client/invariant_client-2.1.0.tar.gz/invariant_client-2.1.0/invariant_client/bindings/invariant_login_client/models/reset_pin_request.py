from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ResetPINRequest")


@_attrs_define
class ResetPINRequest:
    """Respond to the reset_pin challenge.

    Attributes:
        type_ (Literal['reset_pin_request']):
        pin (str):
    """

    type_: Literal["reset_pin_request"]
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
        type_ = cast(Literal["reset_pin_request"], d.pop("type"))
        if type_ != "reset_pin_request":
            raise ValueError(
                f"type must match const 'reset_pin_request', got '{type_}'"
            )

        pin = d.pop("pin")

        reset_pin_request = cls(
            type_=type_,
            pin=pin,
        )

        reset_pin_request.additional_properties = d
        return reset_pin_request

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
