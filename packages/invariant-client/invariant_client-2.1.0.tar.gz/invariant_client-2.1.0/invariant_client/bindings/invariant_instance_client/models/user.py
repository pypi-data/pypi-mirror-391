import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_metadata import UserMetadata


T = TypeVar("T", bound="User")


@_attrs_define
class User:
    """
    Attributes:
        uuid (UUID):
        organization_uuid (UUID):
        login_uuid (Union[None, UUID]):
        email (str):
        metadata (UserMetadata):
        is_active (bool):
        created_at (datetime.datetime):
        deleted_at (Union[None, Unset, datetime.datetime]):
    """

    uuid: UUID
    organization_uuid: UUID
    login_uuid: Union[None, UUID]
    email: str
    metadata: "UserMetadata"
    is_active: bool
    created_at: datetime.datetime
    deleted_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        organization_uuid = str(self.organization_uuid)

        login_uuid: Union[None, str]
        if isinstance(self.login_uuid, UUID):
            login_uuid = str(self.login_uuid)
        else:
            login_uuid = self.login_uuid

        email = self.email

        metadata = self.metadata.to_dict()

        is_active = self.is_active

        created_at = self.created_at.isoformat()

        deleted_at: Union[None, Unset, str]
        if isinstance(self.deleted_at, Unset):
            deleted_at = UNSET
        elif isinstance(self.deleted_at, datetime.datetime):
            deleted_at = self.deleted_at.isoformat()
        else:
            deleted_at = self.deleted_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "organization_uuid": organization_uuid,
                "login_uuid": login_uuid,
                "email": email,
                "metadata": metadata,
                "is_active": is_active,
                "created_at": created_at,
            }
        )
        if deleted_at is not UNSET:
            field_dict["deleted_at"] = deleted_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_metadata import UserMetadata

        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        organization_uuid = UUID(d.pop("organization_uuid"))

        def _parse_login_uuid(data: object) -> Union[None, UUID]:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                login_uuid_type_0 = UUID(data)

                return login_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID], data)

        login_uuid = _parse_login_uuid(d.pop("login_uuid"))

        email = d.pop("email")

        metadata = UserMetadata.from_dict(d.pop("metadata"))

        is_active = d.pop("is_active")

        created_at = isoparse(d.pop("created_at"))

        def _parse_deleted_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                deleted_at_type_0 = isoparse(data)

                return deleted_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        deleted_at = _parse_deleted_at(d.pop("deleted_at", UNSET))

        user = cls(
            uuid=uuid,
            organization_uuid=organization_uuid,
            login_uuid=login_uuid,
            email=email,
            metadata=metadata,
            is_active=is_active,
            created_at=created_at,
            deleted_at=deleted_at,
        )

        user.additional_properties = d
        return user

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
