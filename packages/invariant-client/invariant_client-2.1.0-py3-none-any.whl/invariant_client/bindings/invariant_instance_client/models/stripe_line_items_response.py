from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.stripe_line_items_response_item_data import (
        StripeLineItemsResponseItemData,
    )
    from ..models.subscription_line_item import SubscriptionLineItem


T = TypeVar("T", bound="StripeLineItemsResponse")


@_attrs_define
class StripeLineItemsResponse:
    """
    Attributes:
        line_items (list['SubscriptionLineItem']):
        item_data (StripeLineItemsResponseItemData):
    """

    line_items: list["SubscriptionLineItem"]
    item_data: "StripeLineItemsResponseItemData"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        line_items = []
        for line_items_item_data in self.line_items:
            line_items_item = line_items_item_data.to_dict()
            line_items.append(line_items_item)

        item_data = self.item_data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "line_items": line_items,
                "item_data": item_data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.stripe_line_items_response_item_data import (
            StripeLineItemsResponseItemData,
        )
        from ..models.subscription_line_item import SubscriptionLineItem

        d = dict(src_dict)
        line_items = []
        _line_items = d.pop("line_items")
        for line_items_item_data in _line_items:
            line_items_item = SubscriptionLineItem.from_dict(line_items_item_data)

            line_items.append(line_items_item)

        item_data = StripeLineItemsResponseItemData.from_dict(d.pop("item_data"))

        stripe_line_items_response = cls(
            line_items=line_items,
            item_data=item_data,
        )

        stripe_line_items_response.additional_properties = d
        return stripe_line_items_response

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
