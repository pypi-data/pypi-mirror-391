from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.resource_set import ResourceSet
    from ..models.resource_set_member import ResourceSetMember


T = TypeVar("T", bound="GetResourceSetResponse")


@_attrs_define
class GetResourceSetResponse:
    """
    Attributes:
        resource_set (ResourceSet):
        current_version (int):
        member_resources (list['ResourceSetMember']):
    """

    resource_set: "ResourceSet"
    current_version: int
    member_resources: list["ResourceSetMember"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        resource_set = self.resource_set.to_dict()

        current_version = self.current_version

        member_resources = []
        for member_resources_item_data in self.member_resources:
            member_resources_item = member_resources_item_data.to_dict()
            member_resources.append(member_resources_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "resource_set": resource_set,
                "current_version": current_version,
                "member_resources": member_resources,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.resource_set import ResourceSet
        from ..models.resource_set_member import ResourceSetMember

        d = dict(src_dict)
        resource_set = ResourceSet.from_dict(d.pop("resource_set"))

        current_version = d.pop("current_version")

        member_resources = []
        _member_resources = d.pop("member_resources")
        for member_resources_item_data in _member_resources:
            member_resources_item = ResourceSetMember.from_dict(
                member_resources_item_data
            )

            member_resources.append(member_resources_item)

        get_resource_set_response = cls(
            resource_set=resource_set,
            current_version=current_version,
            member_resources=member_resources,
        )

        get_resource_set_response.additional_properties = d
        return get_resource_set_response

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
