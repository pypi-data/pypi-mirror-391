from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="OIDCSecurityIntegrationMetadata")


@_attrs_define
class OIDCSecurityIntegrationMetadata:
    """
    Attributes:
        type_ (Literal['oidc']):
        name (str):
        server_metadata_url (str):
        client_id (str):
        client_secret (str):
    """

    type_: Literal["oidc"]
    name: str
    server_metadata_url: str
    client_id: str
    client_secret: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        name = self.name

        server_metadata_url = self.server_metadata_url

        client_id = self.client_id

        client_secret = self.client_secret

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "name": name,
                "server_metadata_url": server_metadata_url,
                "client_id": client_id,
                "client_secret": client_secret,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["oidc"], d.pop("type"))
        if type_ != "oidc":
            raise ValueError(f"type must match const 'oidc', got '{type_}'")

        name = d.pop("name")

        server_metadata_url = d.pop("server_metadata_url")

        client_id = d.pop("client_id")

        client_secret = d.pop("client_secret")

        oidc_security_integration_metadata = cls(
            type_=type_,
            name=name,
            server_metadata_url=server_metadata_url,
            client_id=client_id,
            client_secret=client_secret,
        )

        oidc_security_integration_metadata.additional_properties = d
        return oidc_security_integration_metadata

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
