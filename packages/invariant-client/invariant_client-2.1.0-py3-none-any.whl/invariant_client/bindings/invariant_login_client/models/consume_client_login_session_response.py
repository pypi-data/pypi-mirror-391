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

T = TypeVar("T", bound="ConsumeClientLoginSessionResponse")


@_attrs_define
class ConsumeClientLoginSessionResponse:
    """
    Attributes:
        status (int):
        retry_after (int):
        access_token (Union[None, str]):
        org_name (Union[None, str]):
        type_ (Union[Literal['urn:invariant:responses:consume_client_login_response'], Unset]):  Default:
            'urn:invariant:responses:consume_client_login_response'.
    """

    status: int
    retry_after: int
    access_token: Union[None, str]
    org_name: Union[None, str]
    type_: Union[
        Literal["urn:invariant:responses:consume_client_login_response"], Unset
    ] = "urn:invariant:responses:consume_client_login_response"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        retry_after = self.retry_after

        access_token: Union[None, str]
        access_token = self.access_token

        org_name: Union[None, str]
        org_name = self.org_name

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "retry_after": retry_after,
                "access_token": access_token,
                "org_name": org_name,
            }
        )
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = d.pop("status")

        retry_after = d.pop("retry_after")

        def _parse_access_token(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        access_token = _parse_access_token(d.pop("access_token"))

        def _parse_org_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        org_name = _parse_org_name(d.pop("org_name"))

        type_ = cast(
            Union[
                Literal["urn:invariant:responses:consume_client_login_response"], Unset
            ],
            d.pop("type", UNSET),
        )
        if (
            type_ != "urn:invariant:responses:consume_client_login_response"
            and not isinstance(type_, Unset)
        ):
            raise ValueError(
                f"type must match const 'urn:invariant:responses:consume_client_login_response', got '{type_}'"
            )

        consume_client_login_session_response = cls(
            status=status,
            retry_after=retry_after,
            access_token=access_token,
            org_name=org_name,
            type_=type_,
        )

        consume_client_login_session_response.additional_properties = d
        return consume_client_login_session_response

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
