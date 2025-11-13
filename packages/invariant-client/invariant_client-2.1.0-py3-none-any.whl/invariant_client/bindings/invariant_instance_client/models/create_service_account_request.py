from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateServiceAccountRequest")


@_attrs_define
class CreateServiceAccountRequest:
    """
    Attributes:
        type_ (Literal['service_account']):
        sa_name (str):
        sa_comment (Union[None, Unset, str]):
        is_superuser (Union[Unset, bool]):  Default: False.
    """

    type_: Literal["service_account"]
    sa_name: str
    sa_comment: Union[None, Unset, str] = UNSET
    is_superuser: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        sa_name = self.sa_name

        sa_comment: Union[None, Unset, str]
        if isinstance(self.sa_comment, Unset):
            sa_comment = UNSET
        else:
            sa_comment = self.sa_comment

        is_superuser = self.is_superuser

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "sa_name": sa_name,
            }
        )
        if sa_comment is not UNSET:
            field_dict["sa_comment"] = sa_comment
        if is_superuser is not UNSET:
            field_dict["is_superuser"] = is_superuser

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = cast(Literal["service_account"], d.pop("type"))
        if type_ != "service_account":
            raise ValueError(f"type must match const 'service_account', got '{type_}'")

        sa_name = d.pop("sa_name")

        def _parse_sa_comment(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        sa_comment = _parse_sa_comment(d.pop("sa_comment", UNSET))

        is_superuser = d.pop("is_superuser", UNSET)

        create_service_account_request = cls(
            type_=type_,
            sa_name=sa_name,
            sa_comment=sa_comment,
            is_superuser=is_superuser,
        )

        create_service_account_request.additional_properties = d
        return create_service_account_request

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
