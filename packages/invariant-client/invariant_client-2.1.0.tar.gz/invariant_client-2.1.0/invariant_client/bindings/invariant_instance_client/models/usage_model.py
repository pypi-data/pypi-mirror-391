import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.usage_data import UsageData
    from ..models.usage_metadata import UsageMetadata


T = TypeVar("T", bound="UsageModel")


@_attrs_define
class UsageModel:
    """
    Attributes:
        organization_uuid (UUID):
        network_uuid (UUID):
        exec_uuid (UUID):
        data (UsageData):
        metadata (UsageMetadata):
        created_at (Union[Unset, datetime.datetime]):
    """

    organization_uuid: UUID
    network_uuid: UUID
    exec_uuid: UUID
    data: "UsageData"
    metadata: "UsageMetadata"
    created_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organization_uuid = str(self.organization_uuid)

        network_uuid = str(self.network_uuid)

        exec_uuid = str(self.exec_uuid)

        data = self.data.to_dict()

        metadata = self.metadata.to_dict()

        created_at: Union[Unset, str] = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "organization_uuid": organization_uuid,
                "network_uuid": network_uuid,
                "exec_uuid": exec_uuid,
                "data": data,
                "metadata": metadata,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.usage_data import UsageData
        from ..models.usage_metadata import UsageMetadata

        d = dict(src_dict)
        organization_uuid = UUID(d.pop("organization_uuid"))

        network_uuid = UUID(d.pop("network_uuid"))

        exec_uuid = UUID(d.pop("exec_uuid"))

        data = UsageData.from_dict(d.pop("data"))

        metadata = UsageMetadata.from_dict(d.pop("metadata"))

        _created_at = d.pop("created_at", UNSET)
        created_at: Union[Unset, datetime.datetime]
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        usage_model = cls(
            organization_uuid=organization_uuid,
            network_uuid=network_uuid,
            exec_uuid=exec_uuid,
            data=data,
            metadata=metadata,
            created_at=created_at,
        )

        usage_model.additional_properties = d
        return usage_model

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
