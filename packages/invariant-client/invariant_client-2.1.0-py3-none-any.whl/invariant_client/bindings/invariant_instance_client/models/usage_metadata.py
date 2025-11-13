from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.usage_exec_type import UsageExecType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.access_session import AccessSession


T = TypeVar("T", bound="UsageMetadata")


@_attrs_define
class UsageMetadata:
    """
    Attributes:
        exec_type (UsageExecType): Tracks the source execution type.
        access_session (AccessSession): Represents a data acess actor. This could represent an end user accessing data
            over the network or some internal system action.

        snapshot_uuid (Union[None, UUID, Unset]):
    """

    exec_type: UsageExecType
    access_session: "AccessSession"
    snapshot_uuid: Union[None, UUID, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        exec_type = self.exec_type.value

        access_session = self.access_session.to_dict()

        snapshot_uuid: Union[None, Unset, str]
        if isinstance(self.snapshot_uuid, Unset):
            snapshot_uuid = UNSET
        elif isinstance(self.snapshot_uuid, UUID):
            snapshot_uuid = str(self.snapshot_uuid)
        else:
            snapshot_uuid = self.snapshot_uuid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "exec_type": exec_type,
                "access_session": access_session,
            }
        )
        if snapshot_uuid is not UNSET:
            field_dict["snapshot_uuid"] = snapshot_uuid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_session import AccessSession

        d = dict(src_dict)
        exec_type = UsageExecType(d.pop("exec_type"))

        access_session = AccessSession.from_dict(d.pop("access_session"))

        def _parse_snapshot_uuid(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                snapshot_uuid_type_0 = UUID(data)

                return snapshot_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        snapshot_uuid = _parse_snapshot_uuid(d.pop("snapshot_uuid", UNSET))

        usage_metadata = cls(
            exec_type=exec_type,
            access_session=access_session,
            snapshot_uuid=snapshot_uuid,
        )

        usage_metadata.additional_properties = d
        return usage_metadata

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
