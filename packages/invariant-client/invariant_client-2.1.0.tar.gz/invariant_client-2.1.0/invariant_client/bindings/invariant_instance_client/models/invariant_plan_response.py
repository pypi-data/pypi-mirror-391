from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.invariant_price import InvariantPrice

T = TypeVar("T", bound="InvariantPlanResponse")


@_attrs_define
class InvariantPlanResponse:
    """
    Attributes:
        value (str):
        prices (list[InvariantPrice]):
        description (str):
        has_capacity (bool):
        hidden (bool):
        permit_enterprise (bool):
        permit_non_enterprise (bool):
    """

    value: str
    prices: list[InvariantPrice]
    description: str
    has_capacity: bool
    hidden: bool
    permit_enterprise: bool
    permit_non_enterprise: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = self.value

        prices = []
        for prices_item_data in self.prices:
            prices_item = prices_item_data.value
            prices.append(prices_item)

        description = self.description

        has_capacity = self.has_capacity

        hidden = self.hidden

        permit_enterprise = self.permit_enterprise

        permit_non_enterprise = self.permit_non_enterprise

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "value": value,
                "prices": prices,
                "description": description,
                "has_capacity": has_capacity,
                "hidden": hidden,
                "permit_enterprise": permit_enterprise,
                "permit_non_enterprise": permit_non_enterprise,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        value = d.pop("value")

        prices = []
        _prices = d.pop("prices")
        for prices_item_data in _prices:
            prices_item = InvariantPrice(prices_item_data)

            prices.append(prices_item)

        description = d.pop("description")

        has_capacity = d.pop("has_capacity")

        hidden = d.pop("hidden")

        permit_enterprise = d.pop("permit_enterprise")

        permit_non_enterprise = d.pop("permit_non_enterprise")

        invariant_plan_response = cls(
            value=value,
            prices=prices,
            description=description,
            has_capacity=has_capacity,
            hidden=hidden,
            permit_enterprise=permit_enterprise,
            permit_non_enterprise=permit_non_enterprise,
        )

        invariant_plan_response.additional_properties = d
        return invariant_plan_response

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
