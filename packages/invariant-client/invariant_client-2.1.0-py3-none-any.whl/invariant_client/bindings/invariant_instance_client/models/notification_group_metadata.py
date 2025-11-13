from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.email_subscriber import EmailSubscriber
    from ..models.slack_subscriber import SlackSubscriber


T = TypeVar("T", bound="NotificationGroupMetadata")


@_attrs_define
class NotificationGroupMetadata:
    """
    Attributes:
        name (str):
        comment (Union[None, Unset, str]):
        email_targets (Union[None, Unset, list[str]]):
        subscribers (Union[Unset, list[Union['EmailSubscriber', 'SlackSubscriber']]]):
        network_subscriptions (Union[None, Unset, list[str]]):
    """

    name: str
    comment: Union[None, Unset, str] = UNSET
    email_targets: Union[None, Unset, list[str]] = UNSET
    subscribers: Union[Unset, list[Union["EmailSubscriber", "SlackSubscriber"]]] = UNSET
    network_subscriptions: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.email_subscriber import EmailSubscriber

        name = self.name

        comment: Union[None, Unset, str]
        if isinstance(self.comment, Unset):
            comment = UNSET
        else:
            comment = self.comment

        email_targets: Union[None, Unset, list[str]]
        if isinstance(self.email_targets, Unset):
            email_targets = UNSET
        elif isinstance(self.email_targets, list):
            email_targets = self.email_targets

        else:
            email_targets = self.email_targets

        subscribers: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.subscribers, Unset):
            subscribers = []
            for subscribers_item_data in self.subscribers:
                subscribers_item: dict[str, Any]
                if isinstance(subscribers_item_data, EmailSubscriber):
                    subscribers_item = subscribers_item_data.to_dict()
                else:
                    subscribers_item = subscribers_item_data.to_dict()

                subscribers.append(subscribers_item)

        network_subscriptions: Union[None, Unset, list[str]]
        if isinstance(self.network_subscriptions, Unset):
            network_subscriptions = UNSET
        elif isinstance(self.network_subscriptions, list):
            network_subscriptions = self.network_subscriptions

        else:
            network_subscriptions = self.network_subscriptions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if comment is not UNSET:
            field_dict["comment"] = comment
        if email_targets is not UNSET:
            field_dict["email_targets"] = email_targets
        if subscribers is not UNSET:
            field_dict["subscribers"] = subscribers
        if network_subscriptions is not UNSET:
            field_dict["network_subscriptions"] = network_subscriptions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.email_subscriber import EmailSubscriber
        from ..models.slack_subscriber import SlackSubscriber

        d = dict(src_dict)
        name = d.pop("name")

        def _parse_comment(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        comment = _parse_comment(d.pop("comment", UNSET))

        def _parse_email_targets(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                email_targets_type_0 = cast(list[str], data)

                return email_targets_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        email_targets = _parse_email_targets(d.pop("email_targets", UNSET))

        subscribers = []
        _subscribers = d.pop("subscribers", UNSET)
        for subscribers_item_data in _subscribers or []:

            def _parse_subscribers_item(
                data: object,
            ) -> Union["EmailSubscriber", "SlackSubscriber"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    subscribers_item_type_0 = EmailSubscriber.from_dict(data)

                    return subscribers_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                subscribers_item_type_1 = SlackSubscriber.from_dict(data)

                return subscribers_item_type_1

            subscribers_item = _parse_subscribers_item(subscribers_item_data)

            subscribers.append(subscribers_item)

        def _parse_network_subscriptions(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                network_subscriptions_type_0 = cast(list[str], data)

                return network_subscriptions_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        network_subscriptions = _parse_network_subscriptions(
            d.pop("network_subscriptions", UNSET)
        )

        notification_group_metadata = cls(
            name=name,
            comment=comment,
            email_targets=email_targets,
            subscribers=subscribers,
            network_subscriptions=network_subscriptions,
        )

        notification_group_metadata.additional_properties = d
        return notification_group_metadata

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
