from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MonitorTargetMetadata")


@_attrs_define
class MonitorTargetMetadata:
    """
    Attributes:
        name (str):
        comment (Union[None, Unset, str]):
        repository_url (Union[None, Unset, str]):
        monitor_path (Union[None, Unset, str]):
        network_name (Union[None, Unset, str]):
    """

    name: str
    comment: Union[None, Unset, str] = UNSET
    repository_url: Union[None, Unset, str] = UNSET
    monitor_path: Union[None, Unset, str] = UNSET
    network_name: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        comment: Union[None, Unset, str]
        if isinstance(self.comment, Unset):
            comment = UNSET
        else:
            comment = self.comment

        repository_url: Union[None, Unset, str]
        if isinstance(self.repository_url, Unset):
            repository_url = UNSET
        else:
            repository_url = self.repository_url

        monitor_path: Union[None, Unset, str]
        if isinstance(self.monitor_path, Unset):
            monitor_path = UNSET
        else:
            monitor_path = self.monitor_path

        network_name: Union[None, Unset, str]
        if isinstance(self.network_name, Unset):
            network_name = UNSET
        else:
            network_name = self.network_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if comment is not UNSET:
            field_dict["comment"] = comment
        if repository_url is not UNSET:
            field_dict["repository_url"] = repository_url
        if monitor_path is not UNSET:
            field_dict["monitor_path"] = monitor_path
        if network_name is not UNSET:
            field_dict["network_name"] = network_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        def _parse_comment(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        comment = _parse_comment(d.pop("comment", UNSET))

        def _parse_repository_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        repository_url = _parse_repository_url(d.pop("repository_url", UNSET))

        def _parse_monitor_path(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        monitor_path = _parse_monitor_path(d.pop("monitor_path", UNSET))

        def _parse_network_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        network_name = _parse_network_name(d.pop("network_name", UNSET))

        monitor_target_metadata = cls(
            name=name,
            comment=comment,
            repository_url=repository_url,
            monitor_path=monitor_path,
            network_name=network_name,
        )

        monitor_target_metadata.additional_properties = d
        return monitor_target_metadata

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
