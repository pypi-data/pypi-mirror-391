from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.external_status_integration import ExternalStatusIntegration
    from ..models.integration import Integration
    from ..models.slack_integration import SlackIntegration


T = TypeVar("T", bound="IntegrationWithStatusSlackApp")


@_attrs_define
class IntegrationWithStatusSlackApp:
    """
    Attributes:
        integration (Integration):
        slack_data (Union['SlackIntegration', None]):
        status (ExternalStatusIntegration):
        type_ (Union[Literal['slack_app_installation'], Unset]):  Default: 'slack_app_installation'.
    """

    integration: "Integration"
    slack_data: Union["SlackIntegration", None]
    status: "ExternalStatusIntegration"
    type_: Union[Literal["slack_app_installation"], Unset] = "slack_app_installation"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.slack_integration import SlackIntegration

        integration = self.integration.to_dict()

        slack_data: Union[None, dict[str, Any]]
        if isinstance(self.slack_data, SlackIntegration):
            slack_data = self.slack_data.to_dict()
        else:
            slack_data = self.slack_data

        status = self.status.to_dict()

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "integration": integration,
                "slack_data": slack_data,
                "status": status,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.external_status_integration import ExternalStatusIntegration
        from ..models.integration import Integration
        from ..models.slack_integration import SlackIntegration

        d = dict(src_dict)
        integration = Integration.from_dict(d.pop("integration"))

        def _parse_slack_data(data: object) -> Union["SlackIntegration", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                slack_data_type_0 = SlackIntegration.from_dict(data)

                return slack_data_type_0
            except:  # noqa: E722
                pass
            return cast(Union["SlackIntegration", None], data)

        slack_data = _parse_slack_data(d.pop("slack_data"))

        status = ExternalStatusIntegration.from_dict(d.pop("status"))

        type_ = cast(
            Union[Literal["slack_app_installation"], Unset], d.pop("type", UNSET)
        )
        if type_ != "slack_app_installation" and not isinstance(type_, Unset):
            raise ValueError(
                f"type must match const 'slack_app_installation', got '{type_}'"
            )

        integration_with_status_slack_app = cls(
            integration=integration,
            slack_data=slack_data,
            status=status,
            type_=type_,
        )

        integration_with_status_slack_app.additional_properties = d
        return integration_with_status_slack_app

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
