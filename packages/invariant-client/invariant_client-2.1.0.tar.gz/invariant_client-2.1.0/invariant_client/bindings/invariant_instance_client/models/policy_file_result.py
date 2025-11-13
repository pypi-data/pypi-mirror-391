import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.policy_file_result_outcome import PolicyFileResultOutcome


T = TypeVar("T", bound="PolicyFileResult")


@_attrs_define
class PolicyFileResult:
    """
    Attributes:
        uuid (UUID):
        organization_uuid (UUID):
        network_uuid (UUID):
        snapshot_uuid (UUID):
        outcome (PolicyFileResultOutcome):
        created_at (datetime.datetime):
        rule_resource_set_uuid (Union[None, UUID, Unset]):
        rule_editable_document_uuid (Union[None, UUID, Unset]):
        original_filename (Union[None, Unset, str]):
        deleted_at (Union[None, Unset, datetime.datetime]):
    """

    uuid: UUID
    organization_uuid: UUID
    network_uuid: UUID
    snapshot_uuid: UUID
    outcome: "PolicyFileResultOutcome"
    created_at: datetime.datetime
    rule_resource_set_uuid: Union[None, UUID, Unset] = UNSET
    rule_editable_document_uuid: Union[None, UUID, Unset] = UNSET
    original_filename: Union[None, Unset, str] = UNSET
    deleted_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        organization_uuid = str(self.organization_uuid)

        network_uuid = str(self.network_uuid)

        snapshot_uuid = str(self.snapshot_uuid)

        outcome = self.outcome.to_dict()

        created_at = self.created_at.isoformat()

        rule_resource_set_uuid: Union[None, Unset, str]
        if isinstance(self.rule_resource_set_uuid, Unset):
            rule_resource_set_uuid = UNSET
        elif isinstance(self.rule_resource_set_uuid, UUID):
            rule_resource_set_uuid = str(self.rule_resource_set_uuid)
        else:
            rule_resource_set_uuid = self.rule_resource_set_uuid

        rule_editable_document_uuid: Union[None, Unset, str]
        if isinstance(self.rule_editable_document_uuid, Unset):
            rule_editable_document_uuid = UNSET
        elif isinstance(self.rule_editable_document_uuid, UUID):
            rule_editable_document_uuid = str(self.rule_editable_document_uuid)
        else:
            rule_editable_document_uuid = self.rule_editable_document_uuid

        original_filename: Union[None, Unset, str]
        if isinstance(self.original_filename, Unset):
            original_filename = UNSET
        else:
            original_filename = self.original_filename

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
                "network_uuid": network_uuid,
                "snapshot_uuid": snapshot_uuid,
                "outcome": outcome,
                "created_at": created_at,
            }
        )
        if rule_resource_set_uuid is not UNSET:
            field_dict["rule_resource_set_uuid"] = rule_resource_set_uuid
        if rule_editable_document_uuid is not UNSET:
            field_dict["rule_editable_document_uuid"] = rule_editable_document_uuid
        if original_filename is not UNSET:
            field_dict["original_filename"] = original_filename
        if deleted_at is not UNSET:
            field_dict["deleted_at"] = deleted_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.policy_file_result_outcome import PolicyFileResultOutcome

        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        organization_uuid = UUID(d.pop("organization_uuid"))

        network_uuid = UUID(d.pop("network_uuid"))

        snapshot_uuid = UUID(d.pop("snapshot_uuid"))

        outcome = PolicyFileResultOutcome.from_dict(d.pop("outcome"))

        created_at = isoparse(d.pop("created_at"))

        def _parse_rule_resource_set_uuid(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                rule_resource_set_uuid_type_0 = UUID(data)

                return rule_resource_set_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        rule_resource_set_uuid = _parse_rule_resource_set_uuid(
            d.pop("rule_resource_set_uuid", UNSET)
        )

        def _parse_rule_editable_document_uuid(
            data: object,
        ) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                rule_editable_document_uuid_type_0 = UUID(data)

                return rule_editable_document_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        rule_editable_document_uuid = _parse_rule_editable_document_uuid(
            d.pop("rule_editable_document_uuid", UNSET)
        )

        def _parse_original_filename(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        original_filename = _parse_original_filename(d.pop("original_filename", UNSET))

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

        policy_file_result = cls(
            uuid=uuid,
            organization_uuid=organization_uuid,
            network_uuid=network_uuid,
            snapshot_uuid=snapshot_uuid,
            outcome=outcome,
            created_at=created_at,
            rule_resource_set_uuid=rule_resource_set_uuid,
            rule_editable_document_uuid=rule_editable_document_uuid,
            original_filename=original_filename,
            deleted_at=deleted_at,
        )

        policy_file_result.additional_properties = d
        return policy_file_result

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
