import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.slack_metadata import SlackMetadata


T = TypeVar("T", bound="SlackIntegration")


@_attrs_define
class SlackIntegration:
    """
    Attributes:
        uuid (UUID):
        organization_uuid (UUID):
        team_id (str):
        metadata (SlackMetadata):
        created_at (datetime.datetime):
    """

    uuid: UUID
    organization_uuid: UUID
    team_id: str
    metadata: "SlackMetadata"
    created_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        organization_uuid = str(self.organization_uuid)

        team_id = self.team_id

        metadata = self.metadata.to_dict()

        created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "organization_uuid": organization_uuid,
                "team_id": team_id,
                "metadata": metadata,
                "created_at": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.slack_metadata import SlackMetadata

        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        organization_uuid = UUID(d.pop("organization_uuid"))

        team_id = d.pop("team_id")

        metadata = SlackMetadata.from_dict(d.pop("metadata"))

        created_at = isoparse(d.pop("created_at"))

        slack_integration = cls(
            uuid=uuid,
            organization_uuid=organization_uuid,
            team_id=team_id,
            metadata=metadata,
            created_at=created_at,
        )

        slack_integration.additional_properties = d
        return slack_integration

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
