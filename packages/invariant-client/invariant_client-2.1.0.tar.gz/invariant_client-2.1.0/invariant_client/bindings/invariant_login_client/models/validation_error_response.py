from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.validation_error_response_part import ValidationErrorResponsePart


T = TypeVar("T", bound="ValidationErrorResponse")


@_attrs_define
class ValidationErrorResponse:
    """
    Attributes:
        status (int):
        type_ (Literal['urn:invariant:errors:validation']):
        title (Literal['There was a problem with your request.']):
        detail (str):
        validations (list['ValidationErrorResponsePart']):
        instance (Union[None, Unset, str]):
    """

    status: int
    type_: Literal["urn:invariant:errors:validation"]
    title: Literal["There was a problem with your request."]
    detail: str
    validations: list["ValidationErrorResponsePart"]
    instance: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        type_ = self.type_

        title = self.title

        detail = self.detail

        validations = []
        for validations_item_data in self.validations:
            validations_item = validations_item_data.to_dict()
            validations.append(validations_item)

        instance: Union[None, Unset, str]
        if isinstance(self.instance, Unset):
            instance = UNSET
        else:
            instance = self.instance

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "type": type_,
                "title": title,
                "detail": detail,
                "validations": validations,
            }
        )
        if instance is not UNSET:
            field_dict["instance"] = instance

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.validation_error_response_part import ValidationErrorResponsePart

        d = dict(src_dict)
        status = d.pop("status")

        type_ = cast(Literal["urn:invariant:errors:validation"], d.pop("type"))
        if type_ != "urn:invariant:errors:validation":
            raise ValueError(
                f"type must match const 'urn:invariant:errors:validation', got '{type_}'"
            )

        title = cast(Literal["There was a problem with your request."], d.pop("title"))
        if title != "There was a problem with your request.":
            raise ValueError(
                f"title must match const 'There was a problem with your request.', got '{title}'"
            )

        detail = d.pop("detail")

        validations = []
        _validations = d.pop("validations")
        for validations_item_data in _validations:
            validations_item = ValidationErrorResponsePart.from_dict(
                validations_item_data
            )

            validations.append(validations_item)

        def _parse_instance(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        instance = _parse_instance(d.pop("instance", UNSET))

        validation_error_response = cls(
            status=status,
            type_=type_,
            title=title,
            detail=detail,
            validations=validations,
            instance=instance,
        )

        validation_error_response.additional_properties = d
        return validation_error_response

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
