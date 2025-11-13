from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReportMetadata")


@_attrs_define
class ReportMetadata:
    """
    Attributes:
        session_uuid (Union[None, UUID, Unset]):
        role (Union[None, Unset, str]):
        source_urn (Union[None, Unset, str]):
        volume_model_uuid (Union[None, UUID, Unset]):
    """

    session_uuid: Union[None, UUID, Unset] = UNSET
    role: Union[None, Unset, str] = UNSET
    source_urn: Union[None, Unset, str] = UNSET
    volume_model_uuid: Union[None, UUID, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        session_uuid: Union[None, Unset, str]
        if isinstance(self.session_uuid, Unset):
            session_uuid = UNSET
        elif isinstance(self.session_uuid, UUID):
            session_uuid = str(self.session_uuid)
        else:
            session_uuid = self.session_uuid

        role: Union[None, Unset, str]
        if isinstance(self.role, Unset):
            role = UNSET
        else:
            role = self.role

        source_urn: Union[None, Unset, str]
        if isinstance(self.source_urn, Unset):
            source_urn = UNSET
        else:
            source_urn = self.source_urn

        volume_model_uuid: Union[None, Unset, str]
        if isinstance(self.volume_model_uuid, Unset):
            volume_model_uuid = UNSET
        elif isinstance(self.volume_model_uuid, UUID):
            volume_model_uuid = str(self.volume_model_uuid)
        else:
            volume_model_uuid = self.volume_model_uuid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if session_uuid is not UNSET:
            field_dict["session_uuid"] = session_uuid
        if role is not UNSET:
            field_dict["role"] = role
        if source_urn is not UNSET:
            field_dict["source_urn"] = source_urn
        if volume_model_uuid is not UNSET:
            field_dict["volume_model_uuid"] = volume_model_uuid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_session_uuid(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                session_uuid_type_0 = UUID(data)

                return session_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        session_uuid = _parse_session_uuid(d.pop("session_uuid", UNSET))

        def _parse_role(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        role = _parse_role(d.pop("role", UNSET))

        def _parse_source_urn(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        source_urn = _parse_source_urn(d.pop("source_urn", UNSET))

        def _parse_volume_model_uuid(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                volume_model_uuid_type_0 = UUID(data)

                return volume_model_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        volume_model_uuid = _parse_volume_model_uuid(d.pop("volume_model_uuid", UNSET))

        report_metadata = cls(
            session_uuid=session_uuid,
            role=role,
            source_urn=source_urn,
            volume_model_uuid=volume_model_uuid,
        )

        report_metadata.additional_properties = d
        return report_metadata

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
