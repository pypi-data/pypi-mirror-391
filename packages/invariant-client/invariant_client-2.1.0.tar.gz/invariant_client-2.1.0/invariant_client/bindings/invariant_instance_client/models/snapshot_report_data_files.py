from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.file_index import FileIndex


T = TypeVar("T", bound="SnapshotReportDataFiles")


@_attrs_define
class SnapshotReportDataFiles:
    """ """

    additional_properties: dict[str, Union["FileIndex", UUID]] = _attrs_field(
        init=False, factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            if isinstance(prop, UUID):
                field_dict[prop_name] = str(prop)
            else:
                field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.file_index import FileIndex

        d = dict(src_dict)
        snapshot_report_data_files = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():

            def _parse_additional_property(data: object) -> Union["FileIndex", UUID]:
                try:
                    if not isinstance(data, str):
                        raise TypeError()
                    additional_property_type_0 = UUID(data)

                    return additional_property_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                additional_property_type_1 = FileIndex.from_dict(data)

                return additional_property_type_1

            additional_property = _parse_additional_property(prop_dict)

            additional_properties[prop_name] = additional_property

        snapshot_report_data_files.additional_properties = additional_properties
        return snapshot_report_data_files

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Union["FileIndex", UUID]:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Union["FileIndex", UUID]) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
