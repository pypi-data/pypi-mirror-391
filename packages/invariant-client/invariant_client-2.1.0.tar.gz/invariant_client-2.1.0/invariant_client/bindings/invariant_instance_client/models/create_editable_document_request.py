from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.document_type import DocumentType
from ..models.resource_type import ResourceType
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateEditableDocumentRequest")


@_attrs_define
class CreateEditableDocumentRequest:
    """
    Attributes:
        resource_set_name (str):
        document_type (DocumentType):
        resource_type (ResourceType):
        content (str):
        file_path (Union[Unset, str]):  Default: 'placeholder'.
        description (Union[None, Unset, str]):
    """

    resource_set_name: str
    document_type: DocumentType
    resource_type: ResourceType
    content: str
    file_path: Union[Unset, str] = "placeholder"
    description: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        resource_set_name = self.resource_set_name

        document_type = self.document_type.value

        resource_type = self.resource_type.value

        content = self.content

        file_path = self.file_path

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "resource_set_name": resource_set_name,
                "document_type": document_type,
                "resource_type": resource_type,
                "content": content,
            }
        )
        if file_path is not UNSET:
            field_dict["file_path"] = file_path
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        resource_set_name = d.pop("resource_set_name")

        document_type = DocumentType(d.pop("document_type"))

        resource_type = ResourceType(d.pop("resource_type"))

        content = d.pop("content")

        file_path = d.pop("file_path", UNSET)

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        create_editable_document_request = cls(
            resource_set_name=resource_set_name,
            document_type=document_type,
            resource_type=resource_type,
            content=content,
            file_path=file_path,
            description=description,
        )

        create_editable_document_request.additional_properties = d
        return create_editable_document_request

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
