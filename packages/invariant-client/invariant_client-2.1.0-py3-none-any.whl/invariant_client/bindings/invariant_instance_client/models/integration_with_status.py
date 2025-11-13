from typing import Any, Dict, Type, TypeVar, TYPE_CHECKING

from typing import List


from attrs import define as _attrs_define
from attrs import field as _attrs_field


from typing import Dict
from typing import List

if TYPE_CHECKING:
    from ..models.integration import Integration
    from ..models.external_status_integration import ExternalStatusIntegration
    from ..models.repository import Repository


T = TypeVar("T", bound="IntegrationWithStatus")


@_attrs_define
class IntegrationWithStatus:
    """
    Attributes:
        integration (Integration):
        repositories (List['Repository']):
        status (ExternalStatusIntegration):
    """

    integration: "Integration"
    repositories: List["Repository"]
    status: "ExternalStatusIntegration"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        integration = self.integration.to_dict()

        repositories = []
        for repositories_item_data in self.repositories:
            repositories_item = repositories_item_data.to_dict()

            repositories.append(repositories_item)

        status = self.status.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "integration": integration,
                "repositories": repositories,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.integration import Integration
        from ..models.external_status_integration import ExternalStatusIntegration
        from ..models.repository import Repository

        d = src_dict.copy()
        integration = Integration.from_dict(d.pop("integration"))

        repositories = []
        _repositories = d.pop("repositories")
        for repositories_item_data in _repositories:
            repositories_item = Repository.from_dict(repositories_item_data)

            repositories.append(repositories_item)

        status = ExternalStatusIntegration.from_dict(d.pop("status"))

        integration_with_status = cls(
            integration=integration,
            repositories=repositories,
            status=status,
        )

        integration_with_status.additional_properties = d
        return integration_with_status

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
