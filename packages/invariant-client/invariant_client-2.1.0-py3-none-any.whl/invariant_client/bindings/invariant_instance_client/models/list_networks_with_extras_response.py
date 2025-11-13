from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.network_with_extras import NetworkWithExtras


T = TypeVar("T", bound="ListNetworksWithExtrasResponse")


@_attrs_define
class ListNetworksWithExtrasResponse:
    """List of Networks - include UI-assistive context from the most recent snapshot of each network.

    Attributes:
        networks (list['NetworkWithExtras']):
    """

    networks: list["NetworkWithExtras"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        networks = []
        for networks_item_data in self.networks:
            networks_item = networks_item_data.to_dict()
            networks.append(networks_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "networks": networks,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.network_with_extras import NetworkWithExtras

        d = dict(src_dict)
        networks = []
        _networks = d.pop("networks")
        for networks_item_data in _networks:
            networks_item = NetworkWithExtras.from_dict(networks_item_data)

            networks.append(networks_item)

        list_networks_with_extras_response = cls(
            networks=networks,
        )

        list_networks_with_extras_response.additional_properties = d
        return list_networks_with_extras_response

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
