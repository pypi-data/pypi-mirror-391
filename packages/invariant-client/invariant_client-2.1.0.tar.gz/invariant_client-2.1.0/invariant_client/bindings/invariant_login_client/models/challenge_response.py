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
    from ..models.authn_challenge import AuthnChallenge
    from ..models.new_login_challenge import NewLoginChallenge
    from ..models.password_reset_pin_challenge import PasswordResetPINChallenge
    from ..models.set_password_challenge import SetPasswordChallenge
    from ..models.setup_code_challenge import SetupCodeChallenge
    from ..models.start_challenge import StartChallenge
    from ..models.validate_email_challenge import ValidateEmailChallenge


T = TypeVar("T", bound="ChallengeResponse")


@_attrs_define
class ChallengeResponse:
    """
    Attributes:
        status (int):
        type_ (Literal['urn:invariant:errors:auth_challenge']):
        title (str):
        detail (str):
        challenge (Union['AuthnChallenge', 'NewLoginChallenge', 'PasswordResetPINChallenge', 'SetPasswordChallenge',
            'SetupCodeChallenge', 'StartChallenge', 'ValidateEmailChallenge']):
        instance (Union[None, Unset, str]):
        login_token (Union[None, Unset, str]):
    """

    status: int
    type_: Literal["urn:invariant:errors:auth_challenge"]
    title: str
    detail: str
    challenge: Union[
        "AuthnChallenge",
        "NewLoginChallenge",
        "PasswordResetPINChallenge",
        "SetPasswordChallenge",
        "SetupCodeChallenge",
        "StartChallenge",
        "ValidateEmailChallenge",
    ]
    instance: Union[None, Unset, str] = UNSET
    login_token: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.authn_challenge import AuthnChallenge
        from ..models.new_login_challenge import NewLoginChallenge
        from ..models.password_reset_pin_challenge import PasswordResetPINChallenge
        from ..models.set_password_challenge import SetPasswordChallenge
        from ..models.setup_code_challenge import SetupCodeChallenge
        from ..models.validate_email_challenge import ValidateEmailChallenge

        status = self.status

        type_ = self.type_

        title = self.title

        detail = self.detail

        challenge: dict[str, Any]
        if isinstance(self.challenge, AuthnChallenge):
            challenge = self.challenge.to_dict()
        elif isinstance(self.challenge, NewLoginChallenge):
            challenge = self.challenge.to_dict()
        elif isinstance(self.challenge, ValidateEmailChallenge):
            challenge = self.challenge.to_dict()
        elif isinstance(self.challenge, PasswordResetPINChallenge):
            challenge = self.challenge.to_dict()
        elif isinstance(self.challenge, SetPasswordChallenge):
            challenge = self.challenge.to_dict()
        elif isinstance(self.challenge, SetupCodeChallenge):
            challenge = self.challenge.to_dict()
        else:
            challenge = self.challenge.to_dict()

        instance: Union[None, Unset, str]
        if isinstance(self.instance, Unset):
            instance = UNSET
        else:
            instance = self.instance

        login_token: Union[None, Unset, str]
        if isinstance(self.login_token, Unset):
            login_token = UNSET
        else:
            login_token = self.login_token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "type": type_,
                "title": title,
                "detail": detail,
                "challenge": challenge,
            }
        )
        if instance is not UNSET:
            field_dict["instance"] = instance
        if login_token is not UNSET:
            field_dict["login_token"] = login_token

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authn_challenge import AuthnChallenge
        from ..models.new_login_challenge import NewLoginChallenge
        from ..models.password_reset_pin_challenge import PasswordResetPINChallenge
        from ..models.set_password_challenge import SetPasswordChallenge
        from ..models.setup_code_challenge import SetupCodeChallenge
        from ..models.start_challenge import StartChallenge
        from ..models.validate_email_challenge import ValidateEmailChallenge

        d = dict(src_dict)
        status = d.pop("status")

        type_ = cast(Literal["urn:invariant:errors:auth_challenge"], d.pop("type"))
        if type_ != "urn:invariant:errors:auth_challenge":
            raise ValueError(
                f"type must match const 'urn:invariant:errors:auth_challenge', got '{type_}'"
            )

        title = d.pop("title")

        detail = d.pop("detail")

        def _parse_challenge(
            data: object,
        ) -> Union[
            "AuthnChallenge",
            "NewLoginChallenge",
            "PasswordResetPINChallenge",
            "SetPasswordChallenge",
            "SetupCodeChallenge",
            "StartChallenge",
            "ValidateEmailChallenge",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                challenge_type_0 = AuthnChallenge.from_dict(data)

                return challenge_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                challenge_type_1 = NewLoginChallenge.from_dict(data)

                return challenge_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                challenge_type_2 = ValidateEmailChallenge.from_dict(data)

                return challenge_type_2
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                challenge_type_3 = PasswordResetPINChallenge.from_dict(data)

                return challenge_type_3
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                challenge_type_4 = SetPasswordChallenge.from_dict(data)

                return challenge_type_4
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                challenge_type_5 = SetupCodeChallenge.from_dict(data)

                return challenge_type_5
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            challenge_type_6 = StartChallenge.from_dict(data)

            return challenge_type_6

        challenge = _parse_challenge(d.pop("challenge"))

        def _parse_instance(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        instance = _parse_instance(d.pop("instance", UNSET))

        def _parse_login_token(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        login_token = _parse_login_token(d.pop("login_token", UNSET))

        challenge_response = cls(
            status=status,
            type_=type_,
            title=title,
            detail=detail,
            challenge=challenge,
            instance=instance,
            login_token=login_token,
        )

        challenge_response.additional_properties = d
        return challenge_response

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
