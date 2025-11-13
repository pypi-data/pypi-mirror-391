import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.integration_data_github_app_installation import (
        IntegrationDataGithubAppInstallation,
    )
    from ..models.integration_data_slack_app_installation import (
        IntegrationDataSlackAppInstallation,
    )


T = TypeVar("T", bound="Integration")


@_attrs_define
class Integration:
    """
    Attributes:
        uuid (UUID):
        organization_uuid (UUID):
        data (Union['IntegrationDataGithubAppInstallation', 'IntegrationDataSlackAppInstallation']):
        is_active (bool):
        created_at (datetime.datetime):
    """

    uuid: UUID
    organization_uuid: UUID
    data: Union[
        "IntegrationDataGithubAppInstallation", "IntegrationDataSlackAppInstallation"
    ]
    is_active: bool
    created_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.integration_data_github_app_installation import (
            IntegrationDataGithubAppInstallation,
        )

        uuid = str(self.uuid)

        organization_uuid = str(self.organization_uuid)

        data: dict[str, Any]
        if isinstance(self.data, IntegrationDataGithubAppInstallation):
            data = self.data.to_dict()
        else:
            data = self.data.to_dict()

        is_active = self.is_active

        created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "organization_uuid": organization_uuid,
                "data": data,
                "is_active": is_active,
                "created_at": created_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.integration_data_github_app_installation import (
            IntegrationDataGithubAppInstallation,
        )
        from ..models.integration_data_slack_app_installation import (
            IntegrationDataSlackAppInstallation,
        )

        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        organization_uuid = UUID(d.pop("organization_uuid"))

        def _parse_data(
            data: object,
        ) -> Union[
            "IntegrationDataGithubAppInstallation",
            "IntegrationDataSlackAppInstallation",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_0 = IntegrationDataGithubAppInstallation.from_dict(data)

                return data_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            data_type_1 = IntegrationDataSlackAppInstallation.from_dict(data)

            return data_type_1

        data = _parse_data(d.pop("data"))

        is_active = d.pop("is_active")

        created_at = isoparse(d.pop("created_at"))

        integration = cls(
            uuid=uuid,
            organization_uuid=organization_uuid,
            data=data,
            is_active=is_active,
            created_at=created_at,
        )

        integration.additional_properties = d
        return integration

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
