import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.editable_document_version_metadata import (
        EditableDocumentVersionMetadata,
    )


T = TypeVar("T", bound="EditableDocumentVersion")


@_attrs_define
class EditableDocumentVersion:
    """
    Attributes:
        editable_document_uuid (UUID):
        version_number (int):
        metadata (EditableDocumentVersionMetadata):
        created_at (datetime.datetime):
    """

    editable_document_uuid: UUID
    version_number: int
    metadata: "EditableDocumentVersionMetadata"
    created_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        editable_document_uuid = str(self.editable_document_uuid)

        version_number = self.version_number

        metadata = self.metadata.to_dict()

        created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "editable_document_uuid": editable_document_uuid,
                "version_number": version_number,
                "metadata": metadata,
                "created_at": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.editable_document_version_metadata import (
            EditableDocumentVersionMetadata,
        )

        d = dict(src_dict)
        editable_document_uuid = UUID(d.pop("editable_document_uuid"))

        version_number = d.pop("version_number")

        metadata = EditableDocumentVersionMetadata.from_dict(d.pop("metadata"))

        created_at = isoparse(d.pop("created_at"))

        editable_document_version = cls(
            editable_document_uuid=editable_document_uuid,
            version_number=version_number,
            metadata=metadata,
            created_at=created_at,
        )

        editable_document_version.additional_properties = d
        return editable_document_version

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
