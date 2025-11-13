from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.resource_set import ResourceSet


T = TypeVar("T", bound="ResourceSetWithExtras")


@_attrs_define
class ResourceSetWithExtras:
    """
    Attributes:
        resource_set (ResourceSet):
        attached_networks (list[str]):
    """

    resource_set: "ResourceSet"
    attached_networks: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        resource_set = self.resource_set.to_dict()

        attached_networks = self.attached_networks

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "resource_set": resource_set,
                "attached_networks": attached_networks,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.resource_set import ResourceSet

        d = dict(src_dict)
        resource_set = ResourceSet.from_dict(d.pop("resource_set"))

        attached_networks = cast(list[str], d.pop("attached_networks"))

        resource_set_with_extras = cls(
            resource_set=resource_set,
            attached_networks=attached_networks,
        )

        resource_set_with_extras.additional_properties = d
        return resource_set_with_extras

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
