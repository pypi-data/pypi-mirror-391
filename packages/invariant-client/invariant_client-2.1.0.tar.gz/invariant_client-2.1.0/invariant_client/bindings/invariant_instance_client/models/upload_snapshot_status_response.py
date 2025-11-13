from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UploadSnapshotStatusResponse")


@_attrs_define
class UploadSnapshotStatusResponse:
    """
    Attributes:
        is_running (bool):
        terminated (bool):
        retry_after_seconds (Union[None, Unset, int]):  Default: 1.
    """

    is_running: bool
    terminated: bool
    retry_after_seconds: Union[None, Unset, int] = 1
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_running = self.is_running

        terminated = self.terminated

        retry_after_seconds: Union[None, Unset, int]
        if isinstance(self.retry_after_seconds, Unset):
            retry_after_seconds = UNSET
        else:
            retry_after_seconds = self.retry_after_seconds

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "is_running": is_running,
                "terminated": terminated,
            }
        )
        if retry_after_seconds is not UNSET:
            field_dict["retry_after_seconds"] = retry_after_seconds

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_running = d.pop("is_running")

        terminated = d.pop("terminated")

        def _parse_retry_after_seconds(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        retry_after_seconds = _parse_retry_after_seconds(
            d.pop("retry_after_seconds", UNSET)
        )

        upload_snapshot_status_response = cls(
            is_running=is_running,
            terminated=terminated,
            retry_after_seconds=retry_after_seconds,
        )

        upload_snapshot_status_response.additional_properties = d
        return upload_snapshot_status_response

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
