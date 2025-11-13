from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.console_request_options import ConsoleRequestOptions


T = TypeVar("T", bound="ReportTextSummaryRequest")


@_attrs_define
class ReportTextSummaryRequest:
    """
    Attributes:
        mode (Union[Unset, str]):  Default: 'text'.
        traces (Union[Unset, bool]):  Default: False.
        console_settings (Union['ConsoleRequestOptions', None, Unset]):
    """

    mode: Union[Unset, str] = "text"
    traces: Union[Unset, bool] = False
    console_settings: Union["ConsoleRequestOptions", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.console_request_options import ConsoleRequestOptions

        mode = self.mode

        traces = self.traces

        console_settings: Union[None, Unset, dict[str, Any]]
        if isinstance(self.console_settings, Unset):
            console_settings = UNSET
        elif isinstance(self.console_settings, ConsoleRequestOptions):
            console_settings = self.console_settings.to_dict()
        else:
            console_settings = self.console_settings

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if mode is not UNSET:
            field_dict["mode"] = mode
        if traces is not UNSET:
            field_dict["traces"] = traces
        if console_settings is not UNSET:
            field_dict["console_settings"] = console_settings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.console_request_options import ConsoleRequestOptions

        d = dict(src_dict)
        mode = d.pop("mode", UNSET)

        traces = d.pop("traces", UNSET)

        def _parse_console_settings(
            data: object,
        ) -> Union["ConsoleRequestOptions", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                console_settings_type_0 = ConsoleRequestOptions.from_dict(data)

                return console_settings_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ConsoleRequestOptions", None, Unset], data)

        console_settings = _parse_console_settings(d.pop("console_settings", UNSET))

        report_text_summary_request = cls(
            mode=mode,
            traces=traces,
            console_settings=console_settings,
        )

        report_text_summary_request.additional_properties = d
        return report_text_summary_request

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
