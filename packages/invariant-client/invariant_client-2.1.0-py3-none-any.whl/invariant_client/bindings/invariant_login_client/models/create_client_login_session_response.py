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

T = TypeVar("T", bound="CreateClientLoginSessionResponse")


@_attrs_define
class CreateClientLoginSessionResponse:
    """
    Attributes:
        status (int):
        pin (str):
        url (str):
        uuid (str):
        token (str):
        type_ (Union[Literal['urn:invariant:responses:init_client_login_response'], Unset]):  Default:
            'urn:invariant:responses:init_client_login_response'.
    """

    status: int
    pin: str
    url: str
    uuid: str
    token: str
    type_: Union[
        Literal["urn:invariant:responses:init_client_login_response"], Unset
    ] = "urn:invariant:responses:init_client_login_response"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        pin = self.pin

        url = self.url

        uuid = self.uuid

        token = self.token

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "pin": pin,
                "url": url,
                "uuid": uuid,
                "token": token,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = d.pop("status")

        pin = d.pop("pin")

        url = d.pop("url")

        uuid = d.pop("uuid")

        token = d.pop("token")

        type_ = cast(
            Union[Literal["urn:invariant:responses:init_client_login_response"], Unset],
            d.pop("type", UNSET),
        )
        if (
            type_ != "urn:invariant:responses:init_client_login_response"
            and not isinstance(type_, Unset)
        ):
            raise ValueError(
                f"type must match const 'urn:invariant:responses:init_client_login_response', got '{type_}'"
            )

        create_client_login_session_response = cls(
            status=status,
            pin=pin,
            url=url,
            uuid=uuid,
            token=token,
            type_=type_,
        )

        create_client_login_session_response.additional_properties = d
        return create_client_login_session_response

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
