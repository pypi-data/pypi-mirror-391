from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.network import Network


T = TypeVar("T", bound="ListNetworksResponse")


@_attrs_define
class ListNetworksResponse:
    """List of Networks

    Attributes:
        networks (list['Network']):
    """

    networks: list["Network"]
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
        from ..models.network import Network

        d = dict(src_dict)
        networks = []
        _networks = d.pop("networks")
        for networks_item_data in _networks:
            networks_item = Network.from_dict(networks_item_data)

            networks.append(networks_item)

        list_networks_response = cls(
            networks=networks,
        )

        list_networks_response.additional_properties = d
        return list_networks_response

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
