from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ErrorInfoExtras")


@_attrs_define
class ErrorInfoExtras:
    """Extra data for this error instance. Clients should largely display this data verbatim.

    Attributes:
        file (Union[None, Unset, str]):
        start (Union[None, Unset, list[int]]):
        end (Union[None, Unset, list[int]]):
    """

    file: Union[None, Unset, str] = UNSET
    start: Union[None, Unset, list[int]] = UNSET
    end: Union[None, Unset, list[int]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file: Union[None, Unset, str]
        if isinstance(self.file, Unset):
            file = UNSET
        else:
            file = self.file

        start: Union[None, Unset, list[int]]
        if isinstance(self.start, Unset):
            start = UNSET
        elif isinstance(self.start, list):
            start = []
            for start_type_0_item_data in self.start:
                start_type_0_item: int
                start_type_0_item = start_type_0_item_data
                start.append(start_type_0_item)

        else:
            start = self.start

        end: Union[None, Unset, list[int]]
        if isinstance(self.end, Unset):
            end = UNSET
        elif isinstance(self.end, list):
            end = []
            for end_type_0_item_data in self.end:
                end_type_0_item: int
                end_type_0_item = end_type_0_item_data
                end.append(end_type_0_item)

        else:
            end = self.end

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if file is not UNSET:
            field_dict["file"] = file
        if start is not UNSET:
            field_dict["start"] = start
        if end is not UNSET:
            field_dict["end"] = end

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_file(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        file = _parse_file(d.pop("file", UNSET))

        def _parse_start(data: object) -> Union[None, Unset, list[int]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                start_type_0 = []
                _start_type_0 = data
                for start_type_0_item_data in _start_type_0:

                    def _parse_start_type_0_item(data: object) -> int:
                        return cast(int, data)

                    start_type_0_item = _parse_start_type_0_item(start_type_0_item_data)

                    start_type_0.append(start_type_0_item)

                return start_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[int]], data)

        start = _parse_start(d.pop("start", UNSET))

        def _parse_end(data: object) -> Union[None, Unset, list[int]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                end_type_0 = []
                _end_type_0 = data
                for end_type_0_item_data in _end_type_0:

                    def _parse_end_type_0_item(data: object) -> int:
                        return cast(int, data)

                    end_type_0_item = _parse_end_type_0_item(end_type_0_item_data)

                    end_type_0.append(end_type_0_item)

                return end_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[int]], data)

        end = _parse_end(d.pop("end", UNSET))

        error_info_extras = cls(
            file=file,
            start=start,
            end=end,
        )

        error_info_extras.additional_properties = d
        return error_info_extras

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
