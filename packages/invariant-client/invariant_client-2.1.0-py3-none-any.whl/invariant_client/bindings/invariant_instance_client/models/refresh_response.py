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

T = TypeVar("T", bound="RefreshResponse")


@_attrs_define
class RefreshResponse:
    """
    Attributes:
        access_token (str):
        status (Union[Literal[200], Unset]):  Default: 200.
        type_ (Union[Literal['urn:invariant:responses:refresh_response'], Unset]):  Default:
            'urn:invariant:responses:refresh_response'.
    """

    access_token: str
    status: Union[Literal[200], Unset] = 200
    type_: Union[Literal["urn:invariant:responses:refresh_response"], Unset] = (
        "urn:invariant:responses:refresh_response"
    )
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_token = self.access_token

        status = self.status

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "access_token": access_token,
            }
        )
        if status is not UNSET:
            field_dict["status"] = status
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        access_token = d.pop("access_token")

        status = cast(Union[Literal[200], Unset], d.pop("status", UNSET))
        if status != 200 and not isinstance(status, Unset):
            raise ValueError(f"status must match const 200, got '{status}'")

        type_ = cast(
            Union[Literal["urn:invariant:responses:refresh_response"], Unset],
            d.pop("type", UNSET),
        )
        if type_ != "urn:invariant:responses:refresh_response" and not isinstance(
            type_, Unset
        ):
            raise ValueError(
                f"type must match const 'urn:invariant:responses:refresh_response', got '{type_}'"
            )

        refresh_response = cls(
            access_token=access_token,
            status=status,
            type_=type_,
        )

        refresh_response.additional_properties = d
        return refresh_response

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
