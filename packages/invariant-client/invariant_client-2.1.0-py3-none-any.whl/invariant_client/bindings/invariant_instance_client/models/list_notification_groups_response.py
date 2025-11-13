from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.notification_group import NotificationGroup


T = TypeVar("T", bound="ListNotificationGroupsResponse")


@_attrs_define
class ListNotificationGroupsResponse:
    """List of NotificationGroups

    Attributes:
        notification_groups (list['NotificationGroup']):
    """

    notification_groups: list["NotificationGroup"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        notification_groups = []
        for notification_groups_item_data in self.notification_groups:
            notification_groups_item = notification_groups_item_data.to_dict()
            notification_groups.append(notification_groups_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "notification_groups": notification_groups,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.notification_group import NotificationGroup

        d = dict(src_dict)
        notification_groups = []
        _notification_groups = d.pop("notification_groups")
        for notification_groups_item_data in _notification_groups:
            notification_groups_item = NotificationGroup.from_dict(
                notification_groups_item_data
            )

            notification_groups.append(notification_groups_item)

        list_notification_groups_response = cls(
            notification_groups=notification_groups,
        )

        list_notification_groups_response.additional_properties = d
        return list_notification_groups_response

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
