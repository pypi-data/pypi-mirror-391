from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.basic_auth_login_method import BasicAuthLoginMethod
    from ..models.oidc_login_method import OIDCLoginMethod


T = TypeVar("T", bound="SecurityPolicyMetadata")


@_attrs_define
class SecurityPolicyMetadata:
    """
    Attributes:
        default_allowed_methods (Union[Unset, list[Union['BasicAuthLoginMethod', 'OIDCLoginMethod']]]):
        allow_inbound_invitations (Union[Unset, bool]):  Default: True.
        allow_outbound_invitations (Union[Unset, bool]):  Default: True.
    """

    default_allowed_methods: Union[
        Unset, list[Union["BasicAuthLoginMethod", "OIDCLoginMethod"]]
    ] = UNSET
    allow_inbound_invitations: Union[Unset, bool] = True
    allow_outbound_invitations: Union[Unset, bool] = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.basic_auth_login_method import BasicAuthLoginMethod

        default_allowed_methods: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.default_allowed_methods, Unset):
            default_allowed_methods = []
            for default_allowed_methods_item_data in self.default_allowed_methods:
                default_allowed_methods_item: dict[str, Any]
                if isinstance(default_allowed_methods_item_data, BasicAuthLoginMethod):
                    default_allowed_methods_item = (
                        default_allowed_methods_item_data.to_dict()
                    )
                else:
                    default_allowed_methods_item = (
                        default_allowed_methods_item_data.to_dict()
                    )

                default_allowed_methods.append(default_allowed_methods_item)

        allow_inbound_invitations = self.allow_inbound_invitations

        allow_outbound_invitations = self.allow_outbound_invitations

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if default_allowed_methods is not UNSET:
            field_dict["default_allowed_methods"] = default_allowed_methods
        if allow_inbound_invitations is not UNSET:
            field_dict["allow_inbound_invitations"] = allow_inbound_invitations
        if allow_outbound_invitations is not UNSET:
            field_dict["allow_outbound_invitations"] = allow_outbound_invitations

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.basic_auth_login_method import BasicAuthLoginMethod
        from ..models.oidc_login_method import OIDCLoginMethod

        d = dict(src_dict)
        default_allowed_methods = []
        _default_allowed_methods = d.pop("default_allowed_methods", UNSET)
        for default_allowed_methods_item_data in _default_allowed_methods or []:

            def _parse_default_allowed_methods_item(
                data: object,
            ) -> Union["BasicAuthLoginMethod", "OIDCLoginMethod"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    default_allowed_methods_item_type_0 = (
                        BasicAuthLoginMethod.from_dict(data)
                    )

                    return default_allowed_methods_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                default_allowed_methods_item_type_1 = OIDCLoginMethod.from_dict(data)

                return default_allowed_methods_item_type_1

            default_allowed_methods_item = _parse_default_allowed_methods_item(
                default_allowed_methods_item_data
            )

            default_allowed_methods.append(default_allowed_methods_item)

        allow_inbound_invitations = d.pop("allow_inbound_invitations", UNSET)

        allow_outbound_invitations = d.pop("allow_outbound_invitations", UNSET)

        security_policy_metadata = cls(
            default_allowed_methods=default_allowed_methods,
            allow_inbound_invitations=allow_inbound_invitations,
            allow_outbound_invitations=allow_outbound_invitations,
        )

        security_policy_metadata.additional_properties = d
        return security_policy_metadata

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
