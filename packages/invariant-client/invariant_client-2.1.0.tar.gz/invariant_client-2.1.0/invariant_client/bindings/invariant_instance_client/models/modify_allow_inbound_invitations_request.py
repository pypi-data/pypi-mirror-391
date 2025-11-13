from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ModifyAllowInboundInvitationsRequest")


@_attrs_define
class ModifyAllowInboundInvitationsRequest:
    """
    Attributes:
        policy_key (Literal['allow_inbound_invitations']):
        value (bool):
    """

    policy_key: Literal["allow_inbound_invitations"]
    value: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        policy_key = self.policy_key

        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "policy_key": policy_key,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        policy_key = cast(Literal["allow_inbound_invitations"], d.pop("policy_key"))
        if policy_key != "allow_inbound_invitations":
            raise ValueError(
                f"policy_key must match const 'allow_inbound_invitations', got '{policy_key}'"
            )

        value = d.pop("value")

        modify_allow_inbound_invitations_request = cls(
            policy_key=policy_key,
            value=value,
        )

        modify_allow_inbound_invitations_request.additional_properties = d
        return modify_allow_inbound_invitations_request

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
