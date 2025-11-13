from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="UpdateEditableDocumentNameUpdate")


@_attrs_define
class UpdateEditableDocumentNameUpdate:
    """
    Attributes:
        resource_set_name (str):
        new_file_path (str):
    """

    resource_set_name: str
    new_file_path: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        resource_set_name = self.resource_set_name

        new_file_path = self.new_file_path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "resource_set_name": resource_set_name,
                "new_file_path": new_file_path,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        resource_set_name = d.pop("resource_set_name")

        new_file_path = d.pop("new_file_path")

        update_editable_document_name_update = cls(
            resource_set_name=resource_set_name,
            new_file_path=new_file_path,
        )

        update_editable_document_name_update.additional_properties = d
        return update_editable_document_name_update

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
