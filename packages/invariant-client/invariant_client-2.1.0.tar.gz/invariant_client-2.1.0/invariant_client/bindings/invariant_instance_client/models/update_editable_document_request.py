from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_editable_document_name_update import (
        UpdateEditableDocumentNameUpdate,
    )


T = TypeVar("T", bound="UpdateEditableDocumentRequest")


@_attrs_define
class UpdateEditableDocumentRequest:
    """
    Attributes:
        base_version_number (int):
        content (str):
        update_file_path (Union['UpdateEditableDocumentNameUpdate', None, Unset]):
    """

    base_version_number: int
    content: str
    update_file_path: Union["UpdateEditableDocumentNameUpdate", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.update_editable_document_name_update import (
            UpdateEditableDocumentNameUpdate,
        )

        base_version_number = self.base_version_number

        content = self.content

        update_file_path: Union[None, Unset, dict[str, Any]]
        if isinstance(self.update_file_path, Unset):
            update_file_path = UNSET
        elif isinstance(self.update_file_path, UpdateEditableDocumentNameUpdate):
            update_file_path = self.update_file_path.to_dict()
        else:
            update_file_path = self.update_file_path

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "base_version_number": base_version_number,
                "content": content,
            }
        )
        if update_file_path is not UNSET:
            field_dict["update_file_path"] = update_file_path

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_editable_document_name_update import (
            UpdateEditableDocumentNameUpdate,
        )

        d = dict(src_dict)
        base_version_number = d.pop("base_version_number")

        content = d.pop("content")

        def _parse_update_file_path(
            data: object,
        ) -> Union["UpdateEditableDocumentNameUpdate", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                update_file_path_type_0 = UpdateEditableDocumentNameUpdate.from_dict(
                    data
                )

                return update_file_path_type_0
            except:  # noqa: E722
                pass
            return cast(Union["UpdateEditableDocumentNameUpdate", None, Unset], data)

        update_file_path = _parse_update_file_path(d.pop("update_file_path", UNSET))

        update_editable_document_request = cls(
            base_version_number=base_version_number,
            content=content,
            update_file_path=update_file_path,
        )

        update_editable_document_request.additional_properties = d
        return update_editable_document_request

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
