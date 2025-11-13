from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.slack_channel import SlackChannel


T = TypeVar("T", bound="SlackMetadata")


@_attrs_define
class SlackMetadata:
    """
    Attributes:
        channels (list['SlackChannel']):
    """

    channels: list["SlackChannel"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        channels = []
        for channels_item_data in self.channels:
            channels_item = channels_item_data.to_dict()
            channels.append(channels_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "channels": channels,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.slack_channel import SlackChannel

        d = dict(src_dict)
        channels = []
        _channels = d.pop("channels")
        for channels_item_data in _channels:
            channels_item = SlackChannel.from_dict(channels_item_data)

            channels.append(channels_item)

        slack_metadata = cls(
            channels=channels,
        )

        slack_metadata.additional_properties = d
        return slack_metadata

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
