from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.invariant_plan import InvariantPlan
from ..types import UNSET, Unset

T = TypeVar("T", bound="SetupCheckoutRequest")


@_attrs_define
class SetupCheckoutRequest:
    """
    Attributes:
        plan (InvariantPlan): Organization subscription plans.
        type_ (Union[Literal['plan_change'], Unset]):  Default: 'plan_change'.
        capacity (Union[None, Unset, int]):
    """

    plan: InvariantPlan
    type_: Union[Literal["plan_change"], Unset] = "plan_change"
    capacity: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        plan = self.plan.value

        type_ = self.type_

        capacity: Union[None, Unset, int]
        if isinstance(self.capacity, Unset):
            capacity = UNSET
        else:
            capacity = self.capacity

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "plan": plan,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_
        if capacity is not UNSET:
            field_dict["capacity"] = capacity

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        plan = InvariantPlan(d.pop("plan"))

        type_ = cast(Union[Literal["plan_change"], Unset], d.pop("type", UNSET))
        if type_ != "plan_change" and not isinstance(type_, Unset):
            raise ValueError(f"type must match const 'plan_change', got '{type_}'")

        def _parse_capacity(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        capacity = _parse_capacity(d.pop("capacity", UNSET))

        setup_checkout_request = cls(
            plan=plan,
            type_=type_,
            capacity=capacity,
        )

        setup_checkout_request.additional_properties = d
        return setup_checkout_request

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
