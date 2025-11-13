from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreateMonitorTargetRequest")


@_attrs_define
class CreateMonitorTargetRequest:
    """
    Attributes:
        name (str):
        comment (str):
        repository_url (str):
        monitor_path (str):
        network_name (str):
    """

    name: str
    comment: str
    repository_url: str
    monitor_path: str
    network_name: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        comment = self.comment

        repository_url = self.repository_url

        monitor_path = self.monitor_path

        network_name = self.network_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "comment": comment,
                "repository_url": repository_url,
                "monitor_path": monitor_path,
                "network_name": network_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        comment = d.pop("comment")

        repository_url = d.pop("repository_url")

        monitor_path = d.pop("monitor_path")

        network_name = d.pop("network_name")

        create_monitor_target_request = cls(
            name=name,
            comment=comment,
            repository_url=repository_url,
            monitor_path=monitor_path,
            network_name=network_name,
        )

        create_monitor_target_request.additional_properties = d
        return create_monitor_target_request

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
