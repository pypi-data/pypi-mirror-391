from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateTokenRequest")


@_attrs_define
class CreateTokenRequest:
    """
    Attributes:
        name (Union[None, Unset, str]):
        comment (Union[None, Unset, str]):
        service_user_uuid (Union[None, UUID, Unset]):
    """

    name: Union[None, Unset, str] = UNSET
    comment: Union[None, Unset, str] = UNSET
    service_user_uuid: Union[None, UUID, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        comment: Union[None, Unset, str]
        if isinstance(self.comment, Unset):
            comment = UNSET
        else:
            comment = self.comment

        service_user_uuid: Union[None, Unset, str]
        if isinstance(self.service_user_uuid, Unset):
            service_user_uuid = UNSET
        elif isinstance(self.service_user_uuid, UUID):
            service_user_uuid = str(self.service_user_uuid)
        else:
            service_user_uuid = self.service_user_uuid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if comment is not UNSET:
            field_dict["comment"] = comment
        if service_user_uuid is not UNSET:
            field_dict["service_user_uuid"] = service_user_uuid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_comment(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        comment = _parse_comment(d.pop("comment", UNSET))

        def _parse_service_user_uuid(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                service_user_uuid_type_0 = UUID(data)

                return service_user_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        service_user_uuid = _parse_service_user_uuid(d.pop("service_user_uuid", UNSET))

        create_token_request = cls(
            name=name,
            comment=comment,
            service_user_uuid=service_user_uuid,
        )

        create_token_request.additional_properties = d
        return create_token_request

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
