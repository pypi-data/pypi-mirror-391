from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.editable_document import EditableDocument
    from ..models.editable_document_version import EditableDocumentVersion


T = TypeVar("T", bound="EditableDocumentResult")


@_attrs_define
class EditableDocumentResult:
    """Result of an editable document read operation, containing the current version and metadata.

    Attributes:
        document (EditableDocument):
        target_version (Union['EditableDocumentVersion', None, Unset]):
        target_contents (Union[None, Unset, str]):
    """

    document: "EditableDocument"
    target_version: Union["EditableDocumentVersion", None, Unset] = UNSET
    target_contents: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.editable_document_version import EditableDocumentVersion

        document = self.document.to_dict()

        target_version: Union[None, Unset, dict[str, Any]]
        if isinstance(self.target_version, Unset):
            target_version = UNSET
        elif isinstance(self.target_version, EditableDocumentVersion):
            target_version = self.target_version.to_dict()
        else:
            target_version = self.target_version

        target_contents: Union[None, Unset, str]
        if isinstance(self.target_contents, Unset):
            target_contents = UNSET
        else:
            target_contents = self.target_contents

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "document": document,
            }
        )
        if target_version is not UNSET:
            field_dict["target_version"] = target_version
        if target_contents is not UNSET:
            field_dict["target_contents"] = target_contents

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.editable_document import EditableDocument
        from ..models.editable_document_version import EditableDocumentVersion

        d = dict(src_dict)
        document = EditableDocument.from_dict(d.pop("document"))

        def _parse_target_version(
            data: object,
        ) -> Union["EditableDocumentVersion", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                target_version_type_0 = EditableDocumentVersion.from_dict(data)

                return target_version_type_0
            except:  # noqa: E722
                pass
            return cast(Union["EditableDocumentVersion", None, Unset], data)

        target_version = _parse_target_version(d.pop("target_version", UNSET))

        def _parse_target_contents(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        target_contents = _parse_target_contents(d.pop("target_contents", UNSET))

        editable_document_result = cls(
            document=document,
            target_version=target_version,
            target_contents=target_contents,
        )

        editable_document_result.additional_properties = d
        return editable_document_result

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
