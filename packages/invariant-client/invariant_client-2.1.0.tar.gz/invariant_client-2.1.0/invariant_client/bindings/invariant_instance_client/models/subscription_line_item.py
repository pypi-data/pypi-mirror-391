from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SubscriptionLineItem")


@_attrs_define
class SubscriptionLineItem:
    """
    Attributes:
        id (str):
        subscription_id (str):
        product_id (str):
        quantity (int):
        is_original (bool):
    """

    id: str
    subscription_id: str
    product_id: str
    quantity: int
    is_original: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        subscription_id = self.subscription_id

        product_id = self.product_id

        quantity = self.quantity

        is_original = self.is_original

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "subscription_id": subscription_id,
                "product_id": product_id,
                "quantity": quantity,
                "is_original": is_original,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        subscription_id = d.pop("subscription_id")

        product_id = d.pop("product_id")

        quantity = d.pop("quantity")

        is_original = d.pop("is_original")

        subscription_line_item = cls(
            id=id,
            subscription_id=subscription_id,
            product_id=product_id,
            quantity=quantity,
            is_original=is_original,
        )

        subscription_line_item.additional_properties = d
        return subscription_line_item

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
