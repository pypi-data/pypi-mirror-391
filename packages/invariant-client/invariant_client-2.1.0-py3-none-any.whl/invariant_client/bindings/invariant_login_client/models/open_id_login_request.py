from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="OpenIDLoginRequest")


@_attrs_define
class OpenIDLoginRequest:
    """Respond to the authn challenge with basic authentication credentials.

    Attributes:
        type_ (Literal['oidc_auth']):
        token (str):
    """

    type_: Literal["oidc_auth"]
    token: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        token = self.token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "token": token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["oidc_auth"], d.pop("type"))
        if type_ != "oidc_auth":
            raise ValueError(f"type must match const 'oidc_auth', got '{type_}'")

        token = d.pop("token")

        open_id_login_request = cls(
            type_=type_,
            token=token,
        )

        open_id_login_request.additional_properties = d
        return open_id_login_request

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
