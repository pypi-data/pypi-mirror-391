from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SetupCheckoutResponse")


@_attrs_define
class SetupCheckoutResponse:
    """
    Attributes:
        client_reference_id (UUID):
        redirect_url (str):
    """

    client_reference_id: UUID
    redirect_url: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        client_reference_id = str(self.client_reference_id)

        redirect_url = self.redirect_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "client_reference_id": client_reference_id,
                "redirect_url": redirect_url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        client_reference_id = UUID(d.pop("client_reference_id"))

        redirect_url = d.pop("redirect_url")

        setup_checkout_response = cls(
            client_reference_id=client_reference_id,
            redirect_url=redirect_url,
        )

        setup_checkout_response.additional_properties = d
        return setup_checkout_response

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
