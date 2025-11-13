from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ConsoleRequestOptions")


@_attrs_define
class ConsoleRequestOptions:
    """Computed information about the user's local terminal.

    Attributes:
        color_system (Union[None, str]):
        no_color (bool):
        width (int):
        height (int):
        is_jupyter (bool):
        is_terminal (bool):
        is_interactive (bool):
        legacy_windows (bool):
    """

    color_system: Union[None, str]
    no_color: bool
    width: int
    height: int
    is_jupyter: bool
    is_terminal: bool
    is_interactive: bool
    legacy_windows: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        color_system: Union[None, str]
        color_system = self.color_system

        no_color = self.no_color

        width = self.width

        height = self.height

        is_jupyter = self.is_jupyter

        is_terminal = self.is_terminal

        is_interactive = self.is_interactive

        legacy_windows = self.legacy_windows

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "color_system": color_system,
                "no_color": no_color,
                "width": width,
                "height": height,
                "is_jupyter": is_jupyter,
                "is_terminal": is_terminal,
                "is_interactive": is_interactive,
                "legacy_windows": legacy_windows,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_color_system(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        color_system = _parse_color_system(d.pop("color_system"))

        no_color = d.pop("no_color")

        width = d.pop("width")

        height = d.pop("height")

        is_jupyter = d.pop("is_jupyter")

        is_terminal = d.pop("is_terminal")

        is_interactive = d.pop("is_interactive")

        legacy_windows = d.pop("legacy_windows")

        console_request_options = cls(
            color_system=color_system,
            no_color=no_color,
            width=width,
            height=height,
            is_jupyter=is_jupyter,
            is_terminal=is_terminal,
            is_interactive=is_interactive,
            legacy_windows=legacy_windows,
        )

        console_request_options.additional_properties = d
        return console_request_options

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
