from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="IntegrationDataSlackAppInstallationData")


@_attrs_define
class IntegrationDataSlackAppInstallationData:
    """
    Attributes:
        bot_token (str):
        team_id (str):
        team_name (str):
        user_creator (UUID):
    """

    bot_token: str
    team_id: str
    team_name: str
    user_creator: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bot_token = self.bot_token

        team_id = self.team_id

        team_name = self.team_name

        user_creator = str(self.user_creator)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "bot_token": bot_token,
                "team_id": team_id,
                "team_name": team_name,
                "user_creator": user_creator,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bot_token = d.pop("bot_token")

        team_id = d.pop("team_id")

        team_name = d.pop("team_name")

        user_creator = UUID(d.pop("user_creator"))

        integration_data_slack_app_installation_data = cls(
            bot_token=bot_token,
            team_id=team_id,
            team_name=team_name,
            user_creator=user_creator,
        )

        integration_data_slack_app_installation_data.additional_properties = d
        return integration_data_slack_app_installation_data

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
