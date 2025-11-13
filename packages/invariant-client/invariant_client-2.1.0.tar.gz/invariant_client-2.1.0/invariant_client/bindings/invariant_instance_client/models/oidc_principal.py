from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="OIDCPrincipal")


@_attrs_define
class OIDCPrincipal:
    """
    Attributes:
        organization_uuid (UUID):
        integration_uuid (UUID):
        principal_id (str):
    """

    organization_uuid: UUID
    integration_uuid: UUID
    principal_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organization_uuid = str(self.organization_uuid)

        integration_uuid = str(self.integration_uuid)

        principal_id = self.principal_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "organization_uuid": organization_uuid,
                "integration_uuid": integration_uuid,
                "principal_id": principal_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        organization_uuid = UUID(d.pop("organization_uuid"))

        integration_uuid = UUID(d.pop("integration_uuid"))

        principal_id = d.pop("principal_id")

        oidc_principal = cls(
            organization_uuid=organization_uuid,
            integration_uuid=integration_uuid,
            principal_id=principal_id,
        )

        oidc_principal.additional_properties = d
        return oidc_principal

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
