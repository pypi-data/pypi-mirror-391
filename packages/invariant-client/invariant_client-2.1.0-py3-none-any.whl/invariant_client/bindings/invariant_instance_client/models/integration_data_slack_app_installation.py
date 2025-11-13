from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.integration_data_slack_app_installation_data import (
        IntegrationDataSlackAppInstallationData,
    )


T = TypeVar("T", bound="IntegrationDataSlackAppInstallation")


@_attrs_define
class IntegrationDataSlackAppInstallation:
    """
    Attributes:
        type_ (Literal['slack_app_installation']):
        slack_app_install (IntegrationDataSlackAppInstallationData):
    """

    type_: Literal["slack_app_installation"]
    slack_app_install: "IntegrationDataSlackAppInstallationData"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        slack_app_install = self.slack_app_install.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "slack_app_install": slack_app_install,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.integration_data_slack_app_installation_data import (
            IntegrationDataSlackAppInstallationData,
        )

        d = dict(src_dict)
        type_ = cast(Literal["slack_app_installation"], d.pop("type"))
        if type_ != "slack_app_installation":
            raise ValueError(
                f"type must match const 'slack_app_installation', got '{type_}'"
            )

        slack_app_install = IntegrationDataSlackAppInstallationData.from_dict(
            d.pop("slack_app_install")
        )

        integration_data_slack_app_installation = cls(
            type_=type_,
            slack_app_install=slack_app_install,
        )

        integration_data_slack_app_installation.additional_properties = d
        return integration_data_slack_app_installation

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
