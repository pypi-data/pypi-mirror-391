from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EmailSubscriber")


@_attrs_define
class EmailSubscriber:
    """
    Attributes:
        email (str):
        type_ (Union[Literal['email'], Unset]):  Default: 'email'.
    """

    email: str
    type_: Union[Literal["email"], Unset] = "email"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        type_ = cast(Union[Literal["email"], Unset], d.pop("type", UNSET))
        if type_ != "email" and not isinstance(type_, Unset):
            raise ValueError(f"type must match const 'email', got '{type_}'")

        email_subscriber = cls(
            email=email,
            type_=type_,
        )

        email_subscriber.additional_properties = d
        return email_subscriber

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
