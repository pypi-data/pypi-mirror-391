from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.error_info_extras import ErrorInfoExtras


T = TypeVar("T", bound="ErrorInfo")


@_attrs_define
class ErrorInfo:
    """User-facing snapshot processing error. The CLI or UI would make this information available to the user.

    Attributes:
        uuid (str):
        type_ (str):
        subject_urn (str):
        title (str):
        detail (str):
        data (ErrorInfoExtras): Extra data for this error instance. Clients should largely display this data verbatim.
    """

    uuid: str
    type_: str
    subject_urn: str
    title: str
    detail: str
    data: "ErrorInfoExtras"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = self.uuid

        type_ = self.type_

        subject_urn = self.subject_urn

        title = self.title

        detail: str
        detail = self.detail

        data = self.data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "type": type_,
                "subject_urn": subject_urn,
                "title": title,
                "detail": detail,
                "data": data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.error_info_extras import ErrorInfoExtras

        d = dict(src_dict)
        uuid = d.pop("uuid")

        type_ = d.pop("type")

        subject_urn = d.pop("subject_urn")

        title = d.pop("title")

        def _parse_detail(data: object) -> str:
            return cast(str, data)

        detail = _parse_detail(d.pop("detail"))

        data = ErrorInfoExtras.from_dict(d.pop("data"))

        error_info = cls(
            uuid=uuid,
            type_=type_,
            subject_urn=subject_urn,
            title=title,
            detail=detail,
            data=data,
        )

        error_info.additional_properties = d
        return error_info

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
