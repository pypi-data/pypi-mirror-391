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

if TYPE_CHECKING:
    from ..models.basic_auth_login_method import BasicAuthLoginMethod
    from ..models.oidc_login_method import OIDCLoginMethod


T = TypeVar("T", bound="ModifyDefaultLoginMethodsRequest")


@_attrs_define
class ModifyDefaultLoginMethodsRequest:
    """
    Attributes:
        policy_key (Literal['default_allowed_methods']):
        value (list[Union['BasicAuthLoginMethod', 'OIDCLoginMethod']]):
    """

    policy_key: Literal["default_allowed_methods"]
    value: list[Union["BasicAuthLoginMethod", "OIDCLoginMethod"]]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.basic_auth_login_method import BasicAuthLoginMethod

        policy_key = self.policy_key

        value = []
        for value_item_data in self.value:
            value_item: dict[str, Any]
            if isinstance(value_item_data, BasicAuthLoginMethod):
                value_item = value_item_data.to_dict()
            else:
                value_item = value_item_data.to_dict()

            value.append(value_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "policy_key": policy_key,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.basic_auth_login_method import BasicAuthLoginMethod
        from ..models.oidc_login_method import OIDCLoginMethod

        d = dict(src_dict)
        policy_key = cast(Literal["default_allowed_methods"], d.pop("policy_key"))
        if policy_key != "default_allowed_methods":
            raise ValueError(
                f"policy_key must match const 'default_allowed_methods', got '{policy_key}'"
            )

        value = []
        _value = d.pop("value")
        for value_item_data in _value:

            def _parse_value_item(
                data: object,
            ) -> Union["BasicAuthLoginMethod", "OIDCLoginMethod"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    value_item_type_0 = BasicAuthLoginMethod.from_dict(data)

                    return value_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                value_item_type_1 = OIDCLoginMethod.from_dict(data)

                return value_item_type_1

            value_item = _parse_value_item(value_item_data)

            value.append(value_item)

        modify_default_login_methods_request = cls(
            policy_key=policy_key,
            value=value,
        )

        modify_default_login_methods_request.additional_properties = d
        return modify_default_login_methods_request

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
