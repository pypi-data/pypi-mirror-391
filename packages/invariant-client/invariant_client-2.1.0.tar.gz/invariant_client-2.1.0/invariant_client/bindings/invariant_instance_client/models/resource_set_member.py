from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ResourceSetMember")


@_attrs_define
class ResourceSetMember:
    """A member resource in a resource set.

    Attributes:
        document_uuid (UUID):
        file_path (str):
    """

    document_uuid: UUID
    file_path: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        document_uuid = str(self.document_uuid)

        file_path = self.file_path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "document_uuid": document_uuid,
                "file_path": file_path,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        document_uuid = UUID(d.pop("document_uuid"))

        file_path = d.pop("file_path")

        resource_set_member = cls(
            document_uuid=document_uuid,
            file_path=file_path,
        )

        resource_set_member.additional_properties = d
        return resource_set_member

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
