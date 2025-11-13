from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.document_type import DocumentType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.editable_document_metadata_index_type_0 import (
        EditableDocumentMetadataIndexType0,
    )


T = TypeVar("T", bound="EditableDocumentMetadata")


@_attrs_define
class EditableDocumentMetadata:
    """
    Attributes:
        name (str):
        document_type (DocumentType):
        index (Union['EditableDocumentMetadataIndexType0', None, Unset]):
    """

    name: str
    document_type: DocumentType
    index: Union["EditableDocumentMetadataIndexType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.editable_document_metadata_index_type_0 import (
            EditableDocumentMetadataIndexType0,
        )

        name = self.name

        document_type = self.document_type.value

        index: Union[None, Unset, dict[str, Any]]
        if isinstance(self.index, Unset):
            index = UNSET
        elif isinstance(self.index, EditableDocumentMetadataIndexType0):
            index = self.index.to_dict()
        else:
            index = self.index

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "document_type": document_type,
            }
        )
        if index is not UNSET:
            field_dict["index"] = index

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.editable_document_metadata_index_type_0 import (
            EditableDocumentMetadataIndexType0,
        )

        d = dict(src_dict)
        name = d.pop("name")

        document_type = DocumentType(d.pop("document_type"))

        def _parse_index(
            data: object,
        ) -> Union["EditableDocumentMetadataIndexType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                index_type_0 = EditableDocumentMetadataIndexType0.from_dict(data)

                return index_type_0
            except:  # noqa: E722
                pass
            return cast(Union["EditableDocumentMetadataIndexType0", None, Unset], data)

        index = _parse_index(d.pop("index", UNSET))

        editable_document_metadata = cls(
            name=name,
            document_type=document_type,
            index=index,
        )

        editable_document_metadata.additional_properties = d
        return editable_document_metadata

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
