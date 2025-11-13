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

from ..types import UNSET, Unset

T = TypeVar("T", bound="SlackSubscriber")


@_attrs_define
class SlackSubscriber:
    """
    Attributes:
        team (str):
        channel (str):
        type_ (Union[Literal['slack'], Unset]):  Default: 'slack'.
    """

    team: str
    channel: str
    type_: Union[Literal["slack"], Unset] = "slack"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        team = self.team

        channel = self.channel

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "team": team,
                "channel": channel,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        team = d.pop("team")

        channel = d.pop("channel")

        type_ = cast(Union[Literal["slack"], Unset], d.pop("type", UNSET))
        if type_ != "slack" and not isinstance(type_, Unset):
            raise ValueError(f"type must match const 'slack', got '{type_}'")

        slack_subscriber = cls(
            team=team,
            channel=channel,
            type_=type_,
        )

        slack_subscriber.additional_properties = d
        return slack_subscriber

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
