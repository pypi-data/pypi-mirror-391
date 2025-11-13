from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.editable_document_version_metadata_index_type_0 import (
        EditableDocumentVersionMetadataIndexType0,
    )
    from ..models.uuid_volume_locator import UUIDVolumeLocator


T = TypeVar("T", bound="EditableDocumentVersionMetadata")


@_attrs_define
class EditableDocumentVersionMetadata:
    """
    Attributes:
        data_volume (UUIDVolumeLocator):
        creator_uuid (Union[None, UUID, Unset]):
        file_hash (Union[None, Unset, str]):
        size_bytes (Union[None, Unset, int]):
        index (Union['EditableDocumentVersionMetadataIndexType0', None, Unset]):
    """

    data_volume: "UUIDVolumeLocator"
    creator_uuid: Union[None, UUID, Unset] = UNSET
    file_hash: Union[None, Unset, str] = UNSET
    size_bytes: Union[None, Unset, int] = UNSET
    index: Union["EditableDocumentVersionMetadataIndexType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.editable_document_version_metadata_index_type_0 import (
            EditableDocumentVersionMetadataIndexType0,
        )

        data_volume = self.data_volume.to_dict()

        creator_uuid: Union[None, Unset, str]
        if isinstance(self.creator_uuid, Unset):
            creator_uuid = UNSET
        elif isinstance(self.creator_uuid, UUID):
            creator_uuid = str(self.creator_uuid)
        else:
            creator_uuid = self.creator_uuid

        file_hash: Union[None, Unset, str]
        if isinstance(self.file_hash, Unset):
            file_hash = UNSET
        else:
            file_hash = self.file_hash

        size_bytes: Union[None, Unset, int]
        if isinstance(self.size_bytes, Unset):
            size_bytes = UNSET
        else:
            size_bytes = self.size_bytes

        index: Union[None, Unset, dict[str, Any]]
        if isinstance(self.index, Unset):
            index = UNSET
        elif isinstance(self.index, EditableDocumentVersionMetadataIndexType0):
            index = self.index.to_dict()
        else:
            index = self.index

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_volume": data_volume,
            }
        )
        if creator_uuid is not UNSET:
            field_dict["creator_uuid"] = creator_uuid
        if file_hash is not UNSET:
            field_dict["file_hash"] = file_hash
        if size_bytes is not UNSET:
            field_dict["size_bytes"] = size_bytes
        if index is not UNSET:
            field_dict["index"] = index

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.editable_document_version_metadata_index_type_0 import (
            EditableDocumentVersionMetadataIndexType0,
        )
        from ..models.uuid_volume_locator import UUIDVolumeLocator

        d = dict(src_dict)
        data_volume = UUIDVolumeLocator.from_dict(d.pop("data_volume"))

        def _parse_creator_uuid(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                creator_uuid_type_0 = UUID(data)

                return creator_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        creator_uuid = _parse_creator_uuid(d.pop("creator_uuid", UNSET))

        def _parse_file_hash(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        file_hash = _parse_file_hash(d.pop("file_hash", UNSET))

        def _parse_size_bytes(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        size_bytes = _parse_size_bytes(d.pop("size_bytes", UNSET))

        def _parse_index(
            data: object,
        ) -> Union["EditableDocumentVersionMetadataIndexType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                index_type_0 = EditableDocumentVersionMetadataIndexType0.from_dict(data)

                return index_type_0
            except:  # noqa: E722
                pass
            return cast(
                Union["EditableDocumentVersionMetadataIndexType0", None, Unset], data
            )

        index = _parse_index(d.pop("index", UNSET))

        editable_document_version_metadata = cls(
            data_volume=data_volume,
            creator_uuid=creator_uuid,
            file_hash=file_hash,
            size_bytes=size_bytes,
            index=index,
        )

        editable_document_version_metadata.additional_properties = d
        return editable_document_version_metadata

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
