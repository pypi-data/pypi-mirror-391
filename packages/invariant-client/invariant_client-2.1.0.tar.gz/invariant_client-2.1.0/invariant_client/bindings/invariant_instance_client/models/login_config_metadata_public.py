import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.basic_auth_login_method import BasicAuthLoginMethod
    from ..models.oidc_login_method import OIDCLoginMethod
    from ..models.oidc_principal import OIDCPrincipal


T = TypeVar("T", bound="LoginConfigMetadataPublic")


@_attrs_define
class LoginConfigMetadataPublic:
    """
    Attributes:
        email_validated (bool):
        needs_password (bool):
        allowed_methods (Union[None, Unset, list[Union['BasicAuthLoginMethod', 'OIDCLoginMethod']]]):
        oidc_principals (Union[None, Unset, list['OIDCPrincipal']]):
        managing_org (Union[None, UUID, Unset]):
        needs_setup_code_version (Union[None, Unset, int]):
        setup_code_expires_at (Union[None, Unset, datetime.datetime]):
        needs_invite_link_version (Union[None, Unset, int]):
        invite_link_expires_at (Union[None, Unset, datetime.datetime]):
    """

    email_validated: bool
    needs_password: bool
    allowed_methods: Union[
        None, Unset, list[Union["BasicAuthLoginMethod", "OIDCLoginMethod"]]
    ] = UNSET
    oidc_principals: Union[None, Unset, list["OIDCPrincipal"]] = UNSET
    managing_org: Union[None, UUID, Unset] = UNSET
    needs_setup_code_version: Union[None, Unset, int] = UNSET
    setup_code_expires_at: Union[None, Unset, datetime.datetime] = UNSET
    needs_invite_link_version: Union[None, Unset, int] = UNSET
    invite_link_expires_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.basic_auth_login_method import BasicAuthLoginMethod

        email_validated = self.email_validated

        needs_password = self.needs_password

        allowed_methods: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.allowed_methods, Unset):
            allowed_methods = UNSET
        elif isinstance(self.allowed_methods, list):
            allowed_methods = []
            for allowed_methods_type_0_item_data in self.allowed_methods:
                allowed_methods_type_0_item: dict[str, Any]
                if isinstance(allowed_methods_type_0_item_data, BasicAuthLoginMethod):
                    allowed_methods_type_0_item = (
                        allowed_methods_type_0_item_data.to_dict()
                    )
                else:
                    allowed_methods_type_0_item = (
                        allowed_methods_type_0_item_data.to_dict()
                    )

                allowed_methods.append(allowed_methods_type_0_item)

        else:
            allowed_methods = self.allowed_methods

        oidc_principals: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.oidc_principals, Unset):
            oidc_principals = UNSET
        elif isinstance(self.oidc_principals, list):
            oidc_principals = []
            for oidc_principals_type_0_item_data in self.oidc_principals:
                oidc_principals_type_0_item = oidc_principals_type_0_item_data.to_dict()
                oidc_principals.append(oidc_principals_type_0_item)

        else:
            oidc_principals = self.oidc_principals

        managing_org: Union[None, Unset, str]
        if isinstance(self.managing_org, Unset):
            managing_org = UNSET
        elif isinstance(self.managing_org, UUID):
            managing_org = str(self.managing_org)
        else:
            managing_org = self.managing_org

        needs_setup_code_version: Union[None, Unset, int]
        if isinstance(self.needs_setup_code_version, Unset):
            needs_setup_code_version = UNSET
        else:
            needs_setup_code_version = self.needs_setup_code_version

        setup_code_expires_at: Union[None, Unset, str]
        if isinstance(self.setup_code_expires_at, Unset):
            setup_code_expires_at = UNSET
        elif isinstance(self.setup_code_expires_at, datetime.datetime):
            setup_code_expires_at = self.setup_code_expires_at.isoformat()
        else:
            setup_code_expires_at = self.setup_code_expires_at

        needs_invite_link_version: Union[None, Unset, int]
        if isinstance(self.needs_invite_link_version, Unset):
            needs_invite_link_version = UNSET
        else:
            needs_invite_link_version = self.needs_invite_link_version

        invite_link_expires_at: Union[None, Unset, str]
        if isinstance(self.invite_link_expires_at, Unset):
            invite_link_expires_at = UNSET
        elif isinstance(self.invite_link_expires_at, datetime.datetime):
            invite_link_expires_at = self.invite_link_expires_at.isoformat()
        else:
            invite_link_expires_at = self.invite_link_expires_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email_validated": email_validated,
                "needs_password": needs_password,
            }
        )
        if allowed_methods is not UNSET:
            field_dict["allowed_methods"] = allowed_methods
        if oidc_principals is not UNSET:
            field_dict["oidc_principals"] = oidc_principals
        if managing_org is not UNSET:
            field_dict["managing_org"] = managing_org
        if needs_setup_code_version is not UNSET:
            field_dict["needs_setup_code_version"] = needs_setup_code_version
        if setup_code_expires_at is not UNSET:
            field_dict["setup_code_expires_at"] = setup_code_expires_at
        if needs_invite_link_version is not UNSET:
            field_dict["needs_invite_link_version"] = needs_invite_link_version
        if invite_link_expires_at is not UNSET:
            field_dict["invite_link_expires_at"] = invite_link_expires_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.basic_auth_login_method import BasicAuthLoginMethod
        from ..models.oidc_login_method import OIDCLoginMethod
        from ..models.oidc_principal import OIDCPrincipal

        d = dict(src_dict)
        email_validated = d.pop("email_validated")

        needs_password = d.pop("needs_password")

        def _parse_allowed_methods(
            data: object,
        ) -> Union[None, Unset, list[Union["BasicAuthLoginMethod", "OIDCLoginMethod"]]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                allowed_methods_type_0 = []
                _allowed_methods_type_0 = data
                for allowed_methods_type_0_item_data in _allowed_methods_type_0:

                    def _parse_allowed_methods_type_0_item(
                        data: object,
                    ) -> Union["BasicAuthLoginMethod", "OIDCLoginMethod"]:
                        try:
                            if not isinstance(data, dict):
                                raise TypeError()
                            allowed_methods_type_0_item_type_0 = (
                                BasicAuthLoginMethod.from_dict(data)
                            )

                            return allowed_methods_type_0_item_type_0
                        except:  # noqa: E722
                            pass
                        if not isinstance(data, dict):
                            raise TypeError()
                        allowed_methods_type_0_item_type_1 = OIDCLoginMethod.from_dict(
                            data
                        )

                        return allowed_methods_type_0_item_type_1

                    allowed_methods_type_0_item = _parse_allowed_methods_type_0_item(
                        allowed_methods_type_0_item_data
                    )

                    allowed_methods_type_0.append(allowed_methods_type_0_item)

                return allowed_methods_type_0
            except:  # noqa: E722
                pass
            return cast(
                Union[
                    None, Unset, list[Union["BasicAuthLoginMethod", "OIDCLoginMethod"]]
                ],
                data,
            )

        allowed_methods = _parse_allowed_methods(d.pop("allowed_methods", UNSET))

        def _parse_oidc_principals(
            data: object,
        ) -> Union[None, Unset, list["OIDCPrincipal"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                oidc_principals_type_0 = []
                _oidc_principals_type_0 = data
                for oidc_principals_type_0_item_data in _oidc_principals_type_0:
                    oidc_principals_type_0_item = OIDCPrincipal.from_dict(
                        oidc_principals_type_0_item_data
                    )

                    oidc_principals_type_0.append(oidc_principals_type_0_item)

                return oidc_principals_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["OIDCPrincipal"]], data)

        oidc_principals = _parse_oidc_principals(d.pop("oidc_principals", UNSET))

        def _parse_managing_org(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                managing_org_type_0 = UUID(data)

                return managing_org_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        managing_org = _parse_managing_org(d.pop("managing_org", UNSET))

        def _parse_needs_setup_code_version(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        needs_setup_code_version = _parse_needs_setup_code_version(
            d.pop("needs_setup_code_version", UNSET)
        )

        def _parse_setup_code_expires_at(
            data: object,
        ) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                setup_code_expires_at_type_0 = isoparse(data)

                return setup_code_expires_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        setup_code_expires_at = _parse_setup_code_expires_at(
            d.pop("setup_code_expires_at", UNSET)
        )

        def _parse_needs_invite_link_version(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        needs_invite_link_version = _parse_needs_invite_link_version(
            d.pop("needs_invite_link_version", UNSET)
        )

        def _parse_invite_link_expires_at(
            data: object,
        ) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                invite_link_expires_at_type_0 = isoparse(data)

                return invite_link_expires_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        invite_link_expires_at = _parse_invite_link_expires_at(
            d.pop("invite_link_expires_at", UNSET)
        )

        login_config_metadata_public = cls(
            email_validated=email_validated,
            needs_password=needs_password,
            allowed_methods=allowed_methods,
            oidc_principals=oidc_principals,
            managing_org=managing_org,
            needs_setup_code_version=needs_setup_code_version,
            setup_code_expires_at=setup_code_expires_at,
            needs_invite_link_version=needs_invite_link_version,
            invite_link_expires_at=invite_link_expires_at,
        )

        login_config_metadata_public.additional_properties = d
        return login_config_metadata_public

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
