from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SnapshotMetadata")


@_attrs_define
class SnapshotMetadata:
    """
    Attributes:
        volume_model (Union[None, UUID, Unset]):
        report_uuid (Union[None, UUID, Unset]):
        session_uuid (Union[None, UUID, Unset]):
    """

    volume_model: Union[None, UUID, Unset] = UNSET
    report_uuid: Union[None, UUID, Unset] = UNSET
    session_uuid: Union[None, UUID, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        volume_model: Union[None, Unset, str]
        if isinstance(self.volume_model, Unset):
            volume_model = UNSET
        elif isinstance(self.volume_model, UUID):
            volume_model = str(self.volume_model)
        else:
            volume_model = self.volume_model

        report_uuid: Union[None, Unset, str]
        if isinstance(self.report_uuid, Unset):
            report_uuid = UNSET
        elif isinstance(self.report_uuid, UUID):
            report_uuid = str(self.report_uuid)
        else:
            report_uuid = self.report_uuid

        session_uuid: Union[None, Unset, str]
        if isinstance(self.session_uuid, Unset):
            session_uuid = UNSET
        elif isinstance(self.session_uuid, UUID):
            session_uuid = str(self.session_uuid)
        else:
            session_uuid = self.session_uuid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if volume_model is not UNSET:
            field_dict["volume_model"] = volume_model
        if report_uuid is not UNSET:
            field_dict["report_uuid"] = report_uuid
        if session_uuid is not UNSET:
            field_dict["session_uuid"] = session_uuid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_volume_model(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                volume_model_type_0 = UUID(data)

                return volume_model_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        volume_model = _parse_volume_model(d.pop("volume_model", UNSET))

        def _parse_report_uuid(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                report_uuid_type_0 = UUID(data)

                return report_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        report_uuid = _parse_report_uuid(d.pop("report_uuid", UNSET))

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

        snapshot_metadata = cls(
            volume_model=volume_model,
            report_uuid=report_uuid,
            session_uuid=session_uuid,
        )

        snapshot_metadata.additional_properties = d
        return snapshot_metadata

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
