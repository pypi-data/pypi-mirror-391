import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.external_status_data_integration import ExternalStatusDataIntegration


T = TypeVar("T", bound="ExternalStatusIntegration")


@_attrs_define
class ExternalStatusIntegration:
    """
    Attributes:
        organization_uuid (UUID):
        subject_uuid (UUID):
        data (ExternalStatusDataIntegration):
        created_at (datetime.datetime):
    """

    organization_uuid: UUID
    subject_uuid: UUID
    data: "ExternalStatusDataIntegration"
    created_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organization_uuid = str(self.organization_uuid)

        subject_uuid = str(self.subject_uuid)

        data = self.data.to_dict()

        created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "organization_uuid": organization_uuid,
                "subject_uuid": subject_uuid,
                "data": data,
                "created_at": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.external_status_data_integration import (
            ExternalStatusDataIntegration,
        )

        d = dict(src_dict)
        organization_uuid = UUID(d.pop("organization_uuid"))

        subject_uuid = UUID(d.pop("subject_uuid"))

        data = ExternalStatusDataIntegration.from_dict(d.pop("data"))

        created_at = isoparse(d.pop("created_at"))

        external_status_integration = cls(
            organization_uuid=organization_uuid,
            subject_uuid=subject_uuid,
            data=data,
            created_at=created_at,
        )

        external_status_integration.additional_properties = d
        return external_status_integration

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
