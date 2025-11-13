from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    Union,
    cast,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NetworkIPAccessActor")


@_attrs_define
class NetworkIPAccessActor:
    """
    Attributes:
        uuid (UUID):
        source_address (list[Union[int, str]]):
        type_ (Union[Literal['network_ip'], Unset]):  Default: 'network_ip'.
    """

    uuid: UUID
    source_address: list[Union[int, str]]
    type_: Union[Literal["network_ip"], Unset] = "network_ip"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        source_address = []
        for componentsschemas_address_item_data in self.source_address:
            componentsschemas_address_item: Union[int, str]
            componentsschemas_address_item = componentsschemas_address_item_data
            source_address.append(componentsschemas_address_item)

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "source_address": source_address,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        source_address = []
        _source_address = d.pop("source_address")
        for componentsschemas_address_item_data in _source_address:

            def _parse_componentsschemas_address_item(data: object) -> Union[int, str]:
                return cast(Union[int, str], data)

            componentsschemas_address_item = _parse_componentsschemas_address_item(
                componentsschemas_address_item_data
            )

            source_address.append(componentsschemas_address_item)

        type_ = cast(Union[Literal["network_ip"], Unset], d.pop("type", UNSET))
        if type_ != "network_ip" and not isinstance(type_, Unset):
            raise ValueError(f"type must match const 'network_ip', got '{type_}'")

        network_ip_access_actor = cls(
            uuid=uuid,
            source_address=source_address,
            type_=type_,
        )

        network_ip_access_actor.additional_properties = d
        return network_ip_access_actor

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
