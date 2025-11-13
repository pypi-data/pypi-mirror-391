import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.resource_set_metadata import ResourceSetMetadata


T = TypeVar("T", bound="ResourceSet")


@_attrs_define
class ResourceSet:
    """
    Attributes:
        uuid (UUID):
        organization_uuid (UUID):
        editable_document_uuid (UUID):
        name (str):
        metadata (ResourceSetMetadata):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
    """

    uuid: UUID
    organization_uuid: UUID
    editable_document_uuid: UUID
    name: str
    metadata: "ResourceSetMetadata"
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        organization_uuid = str(self.organization_uuid)

        editable_document_uuid = str(self.editable_document_uuid)

        name = self.name

        metadata = self.metadata.to_dict()

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "organization_uuid": organization_uuid,
                "editable_document_uuid": editable_document_uuid,
                "name": name,
                "metadata": metadata,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.resource_set_metadata import ResourceSetMetadata

        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        organization_uuid = UUID(d.pop("organization_uuid"))

        editable_document_uuid = UUID(d.pop("editable_document_uuid"))

        name = d.pop("name")

        metadata = ResourceSetMetadata.from_dict(d.pop("metadata"))

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        resource_set = cls(
            uuid=uuid,
            organization_uuid=organization_uuid,
            editable_document_uuid=editable_document_uuid,
            name=name,
            metadata=metadata,
            created_at=created_at,
            updated_at=updated_at,
        )

        resource_set.additional_properties = d
        return resource_set

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
