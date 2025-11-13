from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.invariant_plan import InvariantPlan
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.subscription_line_item import SubscriptionLineItem


T = TypeVar("T", bound="OrgMetadata")


@_attrs_define
class OrgMetadata:
    """
    Attributes:
        color (str):
        icon (str):
        ent (Union[None, Unset, bool]):
        plan (Union[InvariantPlan, None, Unset]):
        subscriptions_line_items (Union[Unset, list['SubscriptionLineItem']]):
        plan_lock (Union[Unset, bool]):  Default: False.
        stripe_custid (Union[None, Unset, str]):
    """

    color: str
    icon: str
    ent: Union[None, Unset, bool] = UNSET
    plan: Union[InvariantPlan, None, Unset] = UNSET
    subscriptions_line_items: Union[Unset, list["SubscriptionLineItem"]] = UNSET
    plan_lock: Union[Unset, bool] = False
    stripe_custid: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        color = self.color

        icon = self.icon

        ent: Union[None, Unset, bool]
        if isinstance(self.ent, Unset):
            ent = UNSET
        else:
            ent = self.ent

        plan: Union[None, Unset, str]
        if isinstance(self.plan, Unset):
            plan = UNSET
        elif isinstance(self.plan, InvariantPlan):
            plan = self.plan.value
        else:
            plan = self.plan

        subscriptions_line_items: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.subscriptions_line_items, Unset):
            subscriptions_line_items = []
            for subscriptions_line_items_item_data in self.subscriptions_line_items:
                subscriptions_line_items_item = (
                    subscriptions_line_items_item_data.to_dict()
                )
                subscriptions_line_items.append(subscriptions_line_items_item)

        plan_lock = self.plan_lock

        stripe_custid: Union[None, Unset, str]
        if isinstance(self.stripe_custid, Unset):
            stripe_custid = UNSET
        else:
            stripe_custid = self.stripe_custid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "color": color,
                "icon": icon,
            }
        )
        if ent is not UNSET:
            field_dict["ent"] = ent
        if plan is not UNSET:
            field_dict["plan"] = plan
        if subscriptions_line_items is not UNSET:
            field_dict["subscriptions_line_items"] = subscriptions_line_items
        if plan_lock is not UNSET:
            field_dict["plan_lock"] = plan_lock
        if stripe_custid is not UNSET:
            field_dict["stripe_custid"] = stripe_custid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.subscription_line_item import SubscriptionLineItem

        d = dict(src_dict)
        color = d.pop("color")

        icon = d.pop("icon")

        def _parse_ent(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        ent = _parse_ent(d.pop("ent", UNSET))

        def _parse_plan(data: object) -> Union[InvariantPlan, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                plan_type_0 = InvariantPlan(data)

                return plan_type_0
            except:  # noqa: E722
                pass
            return cast(Union[InvariantPlan, None, Unset], data)

        plan = _parse_plan(d.pop("plan", UNSET))

        subscriptions_line_items = []
        _subscriptions_line_items = d.pop("subscriptions_line_items", UNSET)
        for subscriptions_line_items_item_data in _subscriptions_line_items or []:
            subscriptions_line_items_item = SubscriptionLineItem.from_dict(
                subscriptions_line_items_item_data
            )

            subscriptions_line_items.append(subscriptions_line_items_item)

        plan_lock = d.pop("plan_lock", UNSET)

        def _parse_stripe_custid(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        stripe_custid = _parse_stripe_custid(d.pop("stripe_custid", UNSET))

        org_metadata = cls(
            color=color,
            icon=icon,
            ent=ent,
            plan=plan,
            subscriptions_line_items=subscriptions_line_items,
            plan_lock=plan_lock,
            stripe_custid=stripe_custid,
        )

        org_metadata.additional_properties = d
        return org_metadata

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
