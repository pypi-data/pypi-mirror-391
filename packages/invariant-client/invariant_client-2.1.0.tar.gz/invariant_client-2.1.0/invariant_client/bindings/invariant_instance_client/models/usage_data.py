from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.usage_data_inventory import UsageDataInventory


T = TypeVar("T", bound="UsageData")


@_attrs_define
class UsageData:
    """
    Attributes:
        inventory (UsageDataInventory):
    """

    inventory: "UsageDataInventory"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        inventory = self.inventory.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "inventory": inventory,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.usage_data_inventory import UsageDataInventory

        d = dict(src_dict)
        inventory = UsageDataInventory.from_dict(d.pop("inventory"))

        usage_data = cls(
            inventory=inventory,
        )

        usage_data.additional_properties = d
        return usage_data

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
