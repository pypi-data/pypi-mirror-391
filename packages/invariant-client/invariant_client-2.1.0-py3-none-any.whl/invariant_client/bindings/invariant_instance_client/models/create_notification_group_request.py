from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.email_subscriber import EmailSubscriber
    from ..models.slack_subscriber import SlackSubscriber


T = TypeVar("T", bound="CreateNotificationGroupRequest")


@_attrs_define
class CreateNotificationGroupRequest:
    """
    Attributes:
        name (str):
        comment (str):
        network_subscriptions (Union[None, list[str]]):
        subscribers (Union[Unset, list[Union['EmailSubscriber', 'SlackSubscriber']]]):
    """

    name: str
    comment: str
    network_subscriptions: Union[None, list[str]]
    subscribers: Union[Unset, list[Union["EmailSubscriber", "SlackSubscriber"]]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.slack_subscriber import SlackSubscriber

        name = self.name

        comment = self.comment

        network_subscriptions: Union[None, list[str]]
        if isinstance(self.network_subscriptions, list):
            network_subscriptions = self.network_subscriptions

        else:
            network_subscriptions = self.network_subscriptions

        subscribers: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.subscribers, Unset):
            subscribers = []
            for subscribers_item_data in self.subscribers:
                subscribers_item: dict[str, Any]
                if isinstance(subscribers_item_data, SlackSubscriber):
                    subscribers_item = subscribers_item_data.to_dict()
                else:
                    subscribers_item = subscribers_item_data.to_dict()

                subscribers.append(subscribers_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "comment": comment,
                "network_subscriptions": network_subscriptions,
            }
        )
        if subscribers is not UNSET:
            field_dict["subscribers"] = subscribers

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.email_subscriber import EmailSubscriber
        from ..models.slack_subscriber import SlackSubscriber

        d = dict(src_dict)
        name = d.pop("name")

        comment = d.pop("comment")

        def _parse_network_subscriptions(data: object) -> Union[None, list[str]]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                network_subscriptions_type_0 = cast(list[str], data)

                return network_subscriptions_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, list[str]], data)

        network_subscriptions = _parse_network_subscriptions(
            d.pop("network_subscriptions")
        )

        subscribers = []
        _subscribers = d.pop("subscribers", UNSET)
        for subscribers_item_data in _subscribers or []:

            def _parse_subscribers_item(
                data: object,
            ) -> Union["EmailSubscriber", "SlackSubscriber"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    subscribers_item_type_0 = SlackSubscriber.from_dict(data)

                    return subscribers_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                subscribers_item_type_1 = EmailSubscriber.from_dict(data)

                return subscribers_item_type_1

            subscribers_item = _parse_subscribers_item(subscribers_item_data)

            subscribers.append(subscribers_item)

        create_notification_group_request = cls(
            name=name,
            comment=comment,
            network_subscriptions=network_subscriptions,
            subscribers=subscribers,
        )

        create_notification_group_request.additional_properties = d
        return create_notification_group_request

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
