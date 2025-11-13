import datetime
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
from dateutil.parser import isoparse

from ..models.generic_state import GenericState

if TYPE_CHECKING:
    from ..models.error_info import ErrorInfo


T = TypeVar("T", bound="ExternalStatusDataIntegration")


@_attrs_define
class ExternalStatusDataIntegration:
    """
    Attributes:
        type_ (Literal['integration']):
        state (GenericState):
        error (Union['ErrorInfo', None]):
        last_used_at (datetime.datetime):
        modified_at (datetime.datetime):
    """

    type_: Literal["integration"]
    state: GenericState
    error: Union["ErrorInfo", None]
    last_used_at: datetime.datetime
    modified_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.error_info import ErrorInfo

        type_ = self.type_

        state = self.state.value

        error: Union[None, dict[str, Any]]
        if isinstance(self.error, ErrorInfo):
            error = self.error.to_dict()
        else:
            error = self.error

        last_used_at = self.last_used_at.isoformat()

        modified_at = self.modified_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "state": state,
                "error": error,
                "last_used_at": last_used_at,
                "modified_at": modified_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.error_info import ErrorInfo

        d = dict(src_dict)
        type_ = cast(Literal["integration"], d.pop("type"))
        if type_ != "integration":
            raise ValueError(f"type must match const 'integration', got '{type_}'")

        state = GenericState(d.pop("state"))

        def _parse_error(data: object) -> Union["ErrorInfo", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                error_type_0 = ErrorInfo.from_dict(data)

                return error_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ErrorInfo", None], data)

        error = _parse_error(d.pop("error"))

        last_used_at = isoparse(d.pop("last_used_at"))

        modified_at = isoparse(d.pop("modified_at"))

        external_status_data_integration = cls(
            type_=type_,
            state=state,
            error=error,
            last_used_at=last_used_at,
            modified_at=modified_at,
        )

        external_status_data_integration.additional_properties = d
        return external_status_data_integration

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
