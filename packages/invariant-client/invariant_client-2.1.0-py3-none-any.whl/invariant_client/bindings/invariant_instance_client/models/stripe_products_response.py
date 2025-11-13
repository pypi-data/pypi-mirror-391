from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.stripe_products_response_plans import StripeProductsResponsePlans


T = TypeVar("T", bound="StripeProductsResponse")


@_attrs_define
class StripeProductsResponse:
    """
    Attributes:
        plans (StripeProductsResponsePlans):
    """

    plans: "StripeProductsResponsePlans"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        plans = self.plans.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "plans": plans,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.stripe_products_response_plans import StripeProductsResponsePlans

        d = dict(src_dict)
        plans = StripeProductsResponsePlans.from_dict(d.pop("plans"))

        stripe_products_response = cls(
            plans=plans,
        )

        stripe_products_response.additional_properties = d
        return stripe_products_response

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
