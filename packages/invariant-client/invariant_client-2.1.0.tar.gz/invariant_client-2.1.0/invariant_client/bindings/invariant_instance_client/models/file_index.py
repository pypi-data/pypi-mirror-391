from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FileIndex")


@_attrs_define
class FileIndex:
    """
    Attributes:
        all_files (list[UUID]):
        volume (Union[None, UUID, Unset]):
    """

    all_files: list[UUID]
    volume: Union[None, UUID, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        all_files = []
        for all_files_item_data in self.all_files:
            all_files_item = str(all_files_item_data)
            all_files.append(all_files_item)

        volume: Union[None, Unset, str]
        if isinstance(self.volume, Unset):
            volume = UNSET
        elif isinstance(self.volume, UUID):
            volume = str(self.volume)
        else:
            volume = self.volume

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "all_files": all_files,
            }
        )
        if volume is not UNSET:
            field_dict["volume"] = volume

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        all_files = []
        _all_files = d.pop("all_files")
        for all_files_item_data in _all_files:
            all_files_item = UUID(all_files_item_data)

            all_files.append(all_files_item)

        def _parse_volume(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                volume_type_0 = UUID(data)

                return volume_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        volume = _parse_volume(d.pop("volume", UNSET))

        file_index = cls(
            all_files=all_files,
            volume=volume,
        )

        file_index.additional_properties = d
        return file_index

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
