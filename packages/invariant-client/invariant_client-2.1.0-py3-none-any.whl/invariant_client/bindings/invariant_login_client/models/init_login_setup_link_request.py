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

T = TypeVar("T", bound="InitLoginSetupLinkRequest")


@_attrs_define
class InitLoginSetupLinkRequest:
    """This request initiates a login session based on a managed user setup link.

    Attributes:
        type_ (Literal['init_login_setup']):
        slink (str):
        email (Union[None, Unset, str]):
    """

    type_: Literal["init_login_setup"]
    slink: str
    email: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        slink = self.slink

        email: Union[None, Unset, str]
        if isinstance(self.email, Unset):
            email = UNSET
        else:
            email = self.email

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "slink": slink,
            }
        )
        if email is not UNSET:
            field_dict["email"] = email

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["init_login_setup"], d.pop("type"))
        if type_ != "init_login_setup":
            raise ValueError(f"type must match const 'init_login_setup', got '{type_}'")

        slink = d.pop("slink")

        def _parse_email(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        email = _parse_email(d.pop("email", UNSET))

        init_login_setup_link_request = cls(
            type_=type_,
            slink=slink,
            email=email,
        )

        init_login_setup_link_request.additional_properties = d
        return init_login_setup_link_request

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
