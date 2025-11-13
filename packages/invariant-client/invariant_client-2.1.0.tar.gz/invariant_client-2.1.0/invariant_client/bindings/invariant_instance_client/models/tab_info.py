from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.tab_info_parameters_type_0 import TabInfoParametersType0
    from ..models.tab_info_state_type_0 import TabInfoStateType0


T = TypeVar("T", bound="TabInfo")


@_attrs_define
class TabInfo:
    """
    Attributes:
        urn (str):
        active (bool):
        override_name (Union[None, str]):
        parameters (Union['TabInfoParametersType0', None]):
        state (Union['TabInfoStateType0', None]):
    """

    urn: str
    active: bool
    override_name: Union[None, str]
    parameters: Union["TabInfoParametersType0", None]
    state: Union["TabInfoStateType0", None]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.tab_info_parameters_type_0 import TabInfoParametersType0
        from ..models.tab_info_state_type_0 import TabInfoStateType0

        urn = self.urn

        active = self.active

        override_name: Union[None, str]
        override_name = self.override_name

        parameters: Union[None, dict[str, Any]]
        if isinstance(self.parameters, TabInfoParametersType0):
            parameters = self.parameters.to_dict()
        else:
            parameters = self.parameters

        state: Union[None, dict[str, Any]]
        if isinstance(self.state, TabInfoStateType0):
            state = self.state.to_dict()
        else:
            state = self.state

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "urn": urn,
                "active": active,
                "override_name": override_name,
                "parameters": parameters,
                "state": state,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tab_info_parameters_type_0 import TabInfoParametersType0
        from ..models.tab_info_state_type_0 import TabInfoStateType0

        d = dict(src_dict)
        urn = d.pop("urn")

        active = d.pop("active")

        def _parse_override_name(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        override_name = _parse_override_name(d.pop("override_name"))

        def _parse_parameters(data: object) -> Union["TabInfoParametersType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parameters_type_0 = TabInfoParametersType0.from_dict(data)

                return parameters_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TabInfoParametersType0", None], data)

        parameters = _parse_parameters(d.pop("parameters"))

        def _parse_state(data: object) -> Union["TabInfoStateType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                state_type_0 = TabInfoStateType0.from_dict(data)

                return state_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TabInfoStateType0", None], data)

        state = _parse_state(d.pop("state"))

        tab_info = cls(
            urn=urn,
            active=active,
            override_name=override_name,
            parameters=parameters,
            state=state,
        )

        tab_info.additional_properties = d
        return tab_info

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
