from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.login_config_public import LoginConfigPublic
    from ..models.user import User


T = TypeVar("T", bound="OrganizationMemberWithExtras")


@_attrs_define
class OrganizationMemberWithExtras:
    """
    Attributes:
        user (User):
        login (Union['LoginConfigPublic', None]):
    """

    user: "User"
    login: Union["LoginConfigPublic", None]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.login_config_public import LoginConfigPublic

        user = self.user.to_dict()

        login: Union[None, dict[str, Any]]
        if isinstance(self.login, LoginConfigPublic):
            login = self.login.to_dict()
        else:
            login = self.login

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user": user,
                "login": login,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.login_config_public import LoginConfigPublic
        from ..models.user import User

        d = dict(src_dict)
        user = User.from_dict(d.pop("user"))

        def _parse_login(data: object) -> Union["LoginConfigPublic", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                login_type_0 = LoginConfigPublic.from_dict(data)

                return login_type_0
            except:  # noqa: E722
                pass
            return cast(Union["LoginConfigPublic", None], data)

        login = _parse_login(d.pop("login"))

        organization_member_with_extras = cls(
            user=user,
            login=login,
        )

        organization_member_with_extras.additional_properties = d
        return organization_member_with_extras

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
