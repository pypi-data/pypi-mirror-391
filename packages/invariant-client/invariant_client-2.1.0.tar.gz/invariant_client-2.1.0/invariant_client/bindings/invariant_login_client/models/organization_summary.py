from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="OrganizationSummary")


@_attrs_define
class OrganizationSummary:
    """
    Attributes:
        uuid (UUID):
        name (str):
        description (str):
        color (str):
        icon (str):
        url (str):
    """

    uuid: UUID
    name: str
    description: str
    color: str
    icon: str
    url: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        name = self.name

        description = self.description

        color = self.color

        icon = self.icon

        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "name": name,
                "description": description,
                "color": color,
                "icon": icon,
                "url": url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        name = d.pop("name")

        description = d.pop("description")

        color = d.pop("color")

        icon = d.pop("icon")

        url = d.pop("url")

        organization_summary = cls(
            uuid=uuid,
            name=name,
            description=description,
            color=color,
            icon=icon,
            url=url,
        )

        organization_summary.additional_properties = d
        return organization_summary

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
