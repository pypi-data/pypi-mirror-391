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
    from ..models.public import Public


T = TypeVar("T", bound="AuthnChallenge")


@_attrs_define
class AuthnChallenge:
    """The user must provide a primary authentication credential.

    Attributes:
        type_ (Literal['authn']):
        allowed_methods (list[Union['BasicAuthLoginMethod', 'Public']]):
    """

    type_: Literal["authn"]
    allowed_methods: list[Union["BasicAuthLoginMethod", "Public"]]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.basic_auth_login_method import BasicAuthLoginMethod

        type_ = self.type_

        allowed_methods = []
        for allowed_methods_item_data in self.allowed_methods:
            allowed_methods_item: dict[str, Any]
            if isinstance(allowed_methods_item_data, BasicAuthLoginMethod):
                allowed_methods_item = allowed_methods_item_data.to_dict()
            else:
                allowed_methods_item = allowed_methods_item_data.to_dict()

            allowed_methods.append(allowed_methods_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "allowed_methods": allowed_methods,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.basic_auth_login_method import BasicAuthLoginMethod
        from ..models.public import Public

        d = dict(src_dict)
        type_ = cast(Literal["authn"], d.pop("type"))
        if type_ != "authn":
            raise ValueError(f"type must match const 'authn', got '{type_}'")

        allowed_methods = []
        _allowed_methods = d.pop("allowed_methods")
        for allowed_methods_item_data in _allowed_methods:

            def _parse_allowed_methods_item(
                data: object,
            ) -> Union["BasicAuthLoginMethod", "Public"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    allowed_methods_item_type_0 = BasicAuthLoginMethod.from_dict(data)

                    return allowed_methods_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                allowed_methods_item_type_1 = Public.from_dict(data)

                return allowed_methods_item_type_1

            allowed_methods_item = _parse_allowed_methods_item(
                allowed_methods_item_data
            )

            allowed_methods.append(allowed_methods_item)

        authn_challenge = cls(
            type_=type_,
            allowed_methods=allowed_methods,
        )

        authn_challenge.additional_properties = d
        return authn_challenge

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
