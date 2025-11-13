from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="EmailPasswordLoginRequest")


@_attrs_define
class EmailPasswordLoginRequest:
    """Respond to the authn challenge with basic authentication credentials.

    Attributes:
        type_ (Literal['basic_auth']):
        password (str):
    """

    type_: Literal["basic_auth"]
    password: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        password = self.password

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "password": password,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["basic_auth"], d.pop("type"))
        if type_ != "basic_auth":
            raise ValueError(f"type must match const 'basic_auth', got '{type_}'")

        password = d.pop("password")

        email_password_login_request = cls(
            type_=type_,
            password=password,
        )

        email_password_login_request.additional_properties = d
        return email_password_login_request

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
