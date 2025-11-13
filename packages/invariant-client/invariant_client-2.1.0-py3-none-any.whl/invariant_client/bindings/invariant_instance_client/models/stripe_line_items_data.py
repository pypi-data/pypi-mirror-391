from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="StripeLineItemsData")


@_attrs_define
class StripeLineItemsData:
    """
    Attributes:
        id (str):
        subscription (str):
        start_date (int):
        next_billing_date (int):
    """

    id: str
    subscription: str
    start_date: int
    next_billing_date: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        subscription = self.subscription

        start_date = self.start_date

        next_billing_date = self.next_billing_date

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "subscription": subscription,
                "start_date": start_date,
                "next_billing_date": next_billing_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        subscription = d.pop("subscription")

        start_date = d.pop("start_date")

        next_billing_date = d.pop("next_billing_date")

        stripe_line_items_data = cls(
            id=id,
            subscription=subscription,
            start_date=start_date,
            next_billing_date=next_billing_date,
        )

        stripe_line_items_data.additional_properties = d
        return stripe_line_items_data

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
