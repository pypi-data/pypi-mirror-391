import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.snapshot_metadata import SnapshotMetadata


T = TypeVar("T", bound="SnapshotModel")


@_attrs_define
class SnapshotModel:
    """
    Attributes:
        organization_uuid (UUID):
        network_uuid (UUID):
        metadata (SnapshotMetadata):
        uuid (Union[Unset, UUID]):
        created_at (Union[Unset, datetime.datetime]):
        deleted_at (Union[None, Unset, datetime.datetime]):
    """

    organization_uuid: UUID
    network_uuid: UUID
    metadata: "SnapshotMetadata"
    uuid: Union[Unset, UUID] = UNSET
    created_at: Union[Unset, datetime.datetime] = UNSET
    deleted_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organization_uuid = str(self.organization_uuid)

        network_uuid = str(self.network_uuid)

        metadata = self.metadata.to_dict()

        uuid: Union[Unset, str] = UNSET
        if not isinstance(self.uuid, Unset):
            uuid = str(self.uuid)

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
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
                "organization_uuid": organization_uuid,
                "network_uuid": network_uuid,
                "metadata": metadata,
            }
        )
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if deleted_at is not UNSET:
            field_dict["deleted_at"] = deleted_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.snapshot_metadata import SnapshotMetadata

        d = dict(src_dict)
        organization_uuid = UUID(d.pop("organization_uuid"))

        network_uuid = UUID(d.pop("network_uuid"))

        metadata = SnapshotMetadata.from_dict(d.pop("metadata"))

        _uuid = d.pop("uuid", UNSET)
        uuid: Union[Unset, UUID]
        if isinstance(_uuid, Unset):
            uuid = UNSET
        else:
            uuid = UUID(_uuid)

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

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

        snapshot_model = cls(
            organization_uuid=organization_uuid,
            network_uuid=network_uuid,
            metadata=metadata,
            uuid=uuid,
            created_at=created_at,
            deleted_at=deleted_at,
        )

        snapshot_model.additional_properties = d
        return snapshot_model

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
