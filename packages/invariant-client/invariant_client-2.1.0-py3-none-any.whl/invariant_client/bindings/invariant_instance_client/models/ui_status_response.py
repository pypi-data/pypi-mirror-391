from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.organization import Organization
    from ..models.ui_status_response_permissions import UIStatusResponsePermissions
    from ..models.user import User
    from ..models.user_tabs_config import UserTabsConfig


T = TypeVar("T", bound="UIStatusResponse")


@_attrs_define
class UIStatusResponse:
    """
    Attributes:
        user (User):
        organization (Organization): The internal model inside the database.
        permissions (UIStatusResponsePermissions):
        tabs (Union['UserTabsConfig', None]):
    """

    user: "User"
    organization: "Organization"
    permissions: "UIStatusResponsePermissions"
    tabs: Union["UserTabsConfig", None]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.user_tabs_config import UserTabsConfig

        user = self.user.to_dict()

        organization = self.organization.to_dict()

        permissions = self.permissions.to_dict()

        tabs: Union[None, dict[str, Any]]
        if isinstance(self.tabs, UserTabsConfig):
            tabs = self.tabs.to_dict()
        else:
            tabs = self.tabs

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user": user,
                "organization": organization,
                "permissions": permissions,
                "tabs": tabs,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.organization import Organization
        from ..models.ui_status_response_permissions import UIStatusResponsePermissions
        from ..models.user import User
        from ..models.user_tabs_config import UserTabsConfig

        d = dict(src_dict)
        user = User.from_dict(d.pop("user"))

        organization = Organization.from_dict(d.pop("organization"))

        permissions = UIStatusResponsePermissions.from_dict(d.pop("permissions"))

        def _parse_tabs(data: object) -> Union["UserTabsConfig", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                tabs_type_0 = UserTabsConfig.from_dict(data)

                return tabs_type_0
            except:  # noqa: E722
                pass
            return cast(Union["UserTabsConfig", None], data)

        tabs = _parse_tabs(d.pop("tabs"))

        ui_status_response = cls(
            user=user,
            organization=organization,
            permissions=permissions,
            tabs=tabs,
        )

        ui_status_response.additional_properties = d
        return ui_status_response

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
