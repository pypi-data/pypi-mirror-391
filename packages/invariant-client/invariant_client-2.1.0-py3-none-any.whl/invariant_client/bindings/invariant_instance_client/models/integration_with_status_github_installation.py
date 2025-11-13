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
    from ..models.repository import Repository


T = TypeVar("T", bound="IntegrationWithStatusGithubInstallation")


@_attrs_define
class IntegrationWithStatusGithubInstallation:
    """
    Attributes:
        integration (Integration):
        repositories (list['Repository']):
        status (ExternalStatusIntegration):
        type_ (Union[Literal['github_app_installation'], Unset]):  Default: 'github_app_installation'.
    """

    integration: "Integration"
    repositories: list["Repository"]
    status: "ExternalStatusIntegration"
    type_: Union[Literal["github_app_installation"], Unset] = "github_app_installation"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        integration = self.integration.to_dict()

        repositories = []
        for repositories_item_data in self.repositories:
            repositories_item = repositories_item_data.to_dict()
            repositories.append(repositories_item)

        status = self.status.to_dict()

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "integration": integration,
                "repositories": repositories,
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
        from ..models.repository import Repository

        d = dict(src_dict)
        integration = Integration.from_dict(d.pop("integration"))

        repositories = []
        _repositories = d.pop("repositories")
        for repositories_item_data in _repositories:
            repositories_item = Repository.from_dict(repositories_item_data)

            repositories.append(repositories_item)

        status = ExternalStatusIntegration.from_dict(d.pop("status"))

        type_ = cast(
            Union[Literal["github_app_installation"], Unset], d.pop("type", UNSET)
        )
        if type_ != "github_app_installation" and not isinstance(type_, Unset):
            raise ValueError(
                f"type must match const 'github_app_installation', got '{type_}'"
            )

        integration_with_status_github_installation = cls(
            integration=integration,
            repositories=repositories,
            status=status,
            type_=type_,
        )

        integration_with_status_github_installation.additional_properties = d
        return integration_with_status_github_installation

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
