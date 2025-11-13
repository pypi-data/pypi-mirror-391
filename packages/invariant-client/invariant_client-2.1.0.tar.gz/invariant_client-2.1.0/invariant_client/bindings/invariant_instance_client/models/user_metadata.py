import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.built_in_role import BuiltInRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="UserMetadata")


@_attrs_define
class UserMetadata:
    """
    Attributes:
        is_superuser (bool):
        needs_invite_link_version (Union[None, Unset, int]):
        invite_link_expires_at (Union[None, Unset, datetime.datetime]):
        is_service_account (Union[Unset, bool]):  Default: False.
        service_account_name (Union[None, Unset, str]):
        service_account_comment (Union[None, Unset, str]):
        role (Union[BuiltInRole, None, Unset]):
    """

    is_superuser: bool
    needs_invite_link_version: Union[None, Unset, int] = UNSET
    invite_link_expires_at: Union[None, Unset, datetime.datetime] = UNSET
    is_service_account: Union[Unset, bool] = False
    service_account_name: Union[None, Unset, str] = UNSET
    service_account_comment: Union[None, Unset, str] = UNSET
    role: Union[BuiltInRole, None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        is_superuser = self.is_superuser

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

        is_service_account = self.is_service_account

        service_account_name: Union[None, Unset, str]
        if isinstance(self.service_account_name, Unset):
            service_account_name = UNSET
        else:
            service_account_name = self.service_account_name

        service_account_comment: Union[None, Unset, str]
        if isinstance(self.service_account_comment, Unset):
            service_account_comment = UNSET
        else:
            service_account_comment = self.service_account_comment

        role: Union[None, Unset, str]
        if isinstance(self.role, Unset):
            role = UNSET
        elif isinstance(self.role, BuiltInRole):
            role = self.role.value
        else:
            role = self.role

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "is_superuser": is_superuser,
            }
        )
        if needs_invite_link_version is not UNSET:
            field_dict["needs_invite_link_version"] = needs_invite_link_version
        if invite_link_expires_at is not UNSET:
            field_dict["invite_link_expires_at"] = invite_link_expires_at
        if is_service_account is not UNSET:
            field_dict["is_service_account"] = is_service_account
        if service_account_name is not UNSET:
            field_dict["service_account_name"] = service_account_name
        if service_account_comment is not UNSET:
            field_dict["service_account_comment"] = service_account_comment
        if role is not UNSET:
            field_dict["role"] = role

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_superuser = d.pop("is_superuser")

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

        is_service_account = d.pop("is_service_account", UNSET)

        def _parse_service_account_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        service_account_name = _parse_service_account_name(
            d.pop("service_account_name", UNSET)
        )

        def _parse_service_account_comment(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        service_account_comment = _parse_service_account_comment(
            d.pop("service_account_comment", UNSET)
        )

        def _parse_role(data: object) -> Union[BuiltInRole, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                role_type_0 = BuiltInRole(data)

                return role_type_0
            except:  # noqa: E722
                pass
            return cast(Union[BuiltInRole, None, Unset], data)

        role = _parse_role(d.pop("role", UNSET))

        user_metadata = cls(
            is_superuser=is_superuser,
            needs_invite_link_version=needs_invite_link_version,
            invite_link_expires_at=invite_link_expires_at,
            is_service_account=is_service_account,
            service_account_name=service_account_name,
            service_account_comment=service_account_comment,
            role=role,
        )

        user_metadata.additional_properties = d
        return user_metadata

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
