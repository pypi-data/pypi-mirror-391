import json
from collections.abc import Mapping
from io import BytesIO
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import File, FileJsonType

T = TypeVar("T", bound="BodyUploadSnapshotOrganizationNameApiV1UploadsnapshotPost")


@_attrs_define
class BodyUploadSnapshotOrganizationNameApiV1UploadsnapshotPost:
    """
    Attributes:
        file (Union[File, list[File]]):
    """

    file: Union[File, list[File]]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file: Union[FileJsonType, list[FileJsonType]]
        if isinstance(self.file, File):
            file = self.file.to_tuple()

        else:
            file = []
            for file_type_1_item_data in self.file:
                file_type_1_item = file_type_1_item_data.to_tuple()

                file.append(file_type_1_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file": file,
            }
        )

        return field_dict

    def to_multipart(self) -> dict[str, Any]:
        file: tuple[None, bytes, str]

        if isinstance(self.file, File):
            file = self.file.to_tuple()
        else:
            _temp_file = []
            for file_type_1_item_data in self.file:
                file_type_1_item = file_type_1_item_data.to_tuple()

                _temp_file.append(file_type_1_item)
            file = (None, json.dumps(_temp_file).encode(), "application/json")

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = (None, str(prop).encode(), "text/plain")

        field_dict.update(
            {
                "file": file,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_file(data: object) -> Union[File, list[File]]:
            try:
                if not isinstance(data, bytes):
                    raise TypeError()
                file_type_0 = File(payload=BytesIO(data))

                return file_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, list):
                raise TypeError()
            file_type_1 = []
            _file_type_1 = data
            for file_type_1_item_data in _file_type_1:
                file_type_1_item = File(payload=BytesIO(file_type_1_item_data))

                file_type_1.append(file_type_1_item)

            return file_type_1

        file = _parse_file(d.pop("file"))

        body_upload_snapshot_organization_name_api_v1_uploadsnapshot_post = cls(
            file=file,
        )

        body_upload_snapshot_organization_name_api_v1_uploadsnapshot_post.additional_properties = d
        return body_upload_snapshot_organization_name_api_v1_uploadsnapshot_post

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
