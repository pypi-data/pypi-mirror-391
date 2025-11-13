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
    from ..models.basic_auth_login_method import BasicAuthLoginMethod
    from ..models.oidc_login_method import OIDCLoginMethod


T = TypeVar("T", bound="CreateManagedUserRequest")


@_attrs_define
class CreateManagedUserRequest:
    """
    Attributes:
        type_ (Literal['managed']):
        email (str):
        allowed_methods (Union[None, Unset, list[Union['BasicAuthLoginMethod', 'OIDCLoginMethod']]]):
        send_invite (Union[Unset, bool]):  Default: False.
        use_setup_code (Union[Unset, bool]):  Default: False.
        is_superuser (Union[Unset, bool]):  Default: False.
    """

    type_: Literal["managed"]
    email: str
    allowed_methods: Union[
        None, Unset, list[Union["BasicAuthLoginMethod", "OIDCLoginMethod"]]
    ] = UNSET
    send_invite: Union[Unset, bool] = False
    use_setup_code: Union[Unset, bool] = False
    is_superuser: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.basic_auth_login_method import BasicAuthLoginMethod

        type_ = self.type_

        email = self.email

        allowed_methods: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.allowed_methods, Unset):
            allowed_methods = UNSET
        elif isinstance(self.allowed_methods, list):
            allowed_methods = []
            for allowed_methods_type_0_item_data in self.allowed_methods:
                allowed_methods_type_0_item: dict[str, Any]
                if isinstance(allowed_methods_type_0_item_data, BasicAuthLoginMethod):
                    allowed_methods_type_0_item = (
                        allowed_methods_type_0_item_data.to_dict()
                    )
                else:
                    allowed_methods_type_0_item = (
                        allowed_methods_type_0_item_data.to_dict()
                    )

                allowed_methods.append(allowed_methods_type_0_item)

        else:
            allowed_methods = self.allowed_methods

        send_invite = self.send_invite

        use_setup_code = self.use_setup_code

        is_superuser = self.is_superuser

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "email": email,
            }
        )
        if allowed_methods is not UNSET:
            field_dict["allowed_methods"] = allowed_methods
        if send_invite is not UNSET:
            field_dict["send_invite"] = send_invite
        if use_setup_code is not UNSET:
            field_dict["use_setup_code"] = use_setup_code
        if is_superuser is not UNSET:
            field_dict["is_superuser"] = is_superuser

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.basic_auth_login_method import BasicAuthLoginMethod
        from ..models.oidc_login_method import OIDCLoginMethod

        d = dict(src_dict)
        type_ = cast(Literal["managed"], d.pop("type"))
        if type_ != "managed":
            raise ValueError(f"type must match const 'managed', got '{type_}'")

        email = d.pop("email")

        def _parse_allowed_methods(
            data: object,
        ) -> Union[None, Unset, list[Union["BasicAuthLoginMethod", "OIDCLoginMethod"]]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                allowed_methods_type_0 = []
                _allowed_methods_type_0 = data
                for allowed_methods_type_0_item_data in _allowed_methods_type_0:

                    def _parse_allowed_methods_type_0_item(
                        data: object,
                    ) -> Union["BasicAuthLoginMethod", "OIDCLoginMethod"]:
                        try:
                            if not isinstance(data, dict):
                                raise TypeError()
                            allowed_methods_type_0_item_type_0 = (
                                BasicAuthLoginMethod.from_dict(data)
                            )

                            return allowed_methods_type_0_item_type_0
                        except:  # noqa: E722
                            pass
                        if not isinstance(data, dict):
                            raise TypeError()
                        allowed_methods_type_0_item_type_1 = OIDCLoginMethod.from_dict(
                            data
                        )

                        return allowed_methods_type_0_item_type_1

                    allowed_methods_type_0_item = _parse_allowed_methods_type_0_item(
                        allowed_methods_type_0_item_data
                    )

                    allowed_methods_type_0.append(allowed_methods_type_0_item)

                return allowed_methods_type_0
            except:  # noqa: E722
                pass
            return cast(
                Union[
                    None, Unset, list[Union["BasicAuthLoginMethod", "OIDCLoginMethod"]]
                ],
                data,
            )

        allowed_methods = _parse_allowed_methods(d.pop("allowed_methods", UNSET))

        send_invite = d.pop("send_invite", UNSET)

        use_setup_code = d.pop("use_setup_code", UNSET)

        is_superuser = d.pop("is_superuser", UNSET)

        create_managed_user_request = cls(
            type_=type_,
            email=email,
            allowed_methods=allowed_methods,
            send_invite=send_invite,
            use_setup_code=use_setup_code,
            is_superuser=is_superuser,
        )

        create_managed_user_request.additional_properties = d
        return create_managed_user_request

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
