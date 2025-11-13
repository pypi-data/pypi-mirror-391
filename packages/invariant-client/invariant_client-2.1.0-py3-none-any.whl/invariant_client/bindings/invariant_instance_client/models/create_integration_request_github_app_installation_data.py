from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CreateIntegrationRequestGithubAppInstallationData")


@_attrs_define
class CreateIntegrationRequestGithubAppInstallationData:
    """
    Attributes:
        code (str):
        installation_id (str):
        setup_action (str):
        state (str):
    """

    code: str
    installation_id: str
    setup_action: str
    state: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        installation_id = self.installation_id

        setup_action = self.setup_action

        state = self.state

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code": code,
                "installation_id": installation_id,
                "setup_action": setup_action,
                "state": state,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        code = d.pop("code")

        installation_id = d.pop("installation_id")

        setup_action = d.pop("setup_action")

        state = d.pop("state")

        create_integration_request_github_app_installation_data = cls(
            code=code,
            installation_id=installation_id,
            setup_action=setup_action,
            state=state,
        )

        create_integration_request_github_app_installation_data.additional_properties = d
        return create_integration_request_github_app_installation_data

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
