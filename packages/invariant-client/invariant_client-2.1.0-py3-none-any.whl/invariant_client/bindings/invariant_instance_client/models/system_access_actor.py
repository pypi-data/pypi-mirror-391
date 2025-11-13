from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    Union,
    cast,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SystemAccessActor")


@_attrs_define
class SystemAccessActor:
    """
    Attributes:
        context (str):
        type_ (Union[Literal['system'], Unset]):  Default: 'system'.
        uuid (Union[Unset, UUID]):  Default: UUID('deadbeef-cafe-431a-aac7-4aecc20c0316').
    """

    context: str
    type_: Union[Literal["system"], Unset] = "system"
    uuid: Union[Unset, UUID] = UUID("deadbeef-cafe-431a-aac7-4aecc20c0316")
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        context = self.context

        type_ = self.type_

        uuid: Union[Unset, str] = UNSET
        if not isinstance(self.uuid, Unset):
            uuid = str(self.uuid)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "context": context,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_
        if uuid is not UNSET:
            field_dict["uuid"] = uuid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        context = d.pop("context")

        type_ = cast(Union[Literal["system"], Unset], d.pop("type", UNSET))
        if type_ != "system" and not isinstance(type_, Unset):
            raise ValueError(f"type must match const 'system', got '{type_}'")

        _uuid = d.pop("uuid", UNSET)
        uuid: Union[Unset, UUID]
        if isinstance(_uuid, Unset):
            uuid = UNSET
        else:
            uuid = UUID(_uuid)

        system_access_actor = cls(
            context=context,
            type_=type_,
            uuid=uuid,
        )

        system_access_actor.additional_properties = d
        return system_access_actor

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
