import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.access_session_context_type_0 import AccessSessionContextType0
    from ..models.network_ip_access_actor import NetworkIPAccessActor
    from ..models.network_user_access_actor import NetworkUserAccessActor
    from ..models.network_user_access_actor_v1 import NetworkUserAccessActorV1
    from ..models.system_access_actor import SystemAccessActor


T = TypeVar("T", bound="AccessSession")


@_attrs_define
class AccessSession:
    """Represents a data acess actor. This could represent an end user accessing data over the network or some internal
    system action.


        Attributes:
            organization_uuid (UUID):
            actor (Union['NetworkIPAccessActor', 'NetworkUserAccessActor', 'NetworkUserAccessActorV1',
                'SystemAccessActor']):
            context (Union['AccessSessionContextType0', None]):
            created_at (datetime.datetime):
            object_urn (str):
    """

    organization_uuid: UUID
    actor: Union[
        "NetworkIPAccessActor",
        "NetworkUserAccessActor",
        "NetworkUserAccessActorV1",
        "SystemAccessActor",
    ]
    context: Union["AccessSessionContextType0", None]
    created_at: datetime.datetime
    object_urn: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.access_session_context_type_0 import AccessSessionContextType0
        from ..models.network_ip_access_actor import NetworkIPAccessActor
        from ..models.network_user_access_actor import NetworkUserAccessActor
        from ..models.network_user_access_actor_v1 import NetworkUserAccessActorV1

        organization_uuid = str(self.organization_uuid)

        actor: dict[str, Any]
        if isinstance(self.actor, NetworkUserAccessActor):
            actor = self.actor.to_dict()
        elif isinstance(self.actor, NetworkUserAccessActorV1):
            actor = self.actor.to_dict()
        elif isinstance(self.actor, NetworkIPAccessActor):
            actor = self.actor.to_dict()
        else:
            actor = self.actor.to_dict()

        context: Union[None, dict[str, Any]]
        if isinstance(self.context, AccessSessionContextType0):
            context = self.context.to_dict()
        else:
            context = self.context

        created_at = self.created_at.isoformat()

        object_urn = self.object_urn

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "organization_uuid": organization_uuid,
                "actor": actor,
                "context": context,
                "created_at": created_at,
                "object_urn": object_urn,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_session_context_type_0 import AccessSessionContextType0
        from ..models.network_ip_access_actor import NetworkIPAccessActor
        from ..models.network_user_access_actor import NetworkUserAccessActor
        from ..models.network_user_access_actor_v1 import NetworkUserAccessActorV1
        from ..models.system_access_actor import SystemAccessActor

        d = dict(src_dict)
        organization_uuid = UUID(d.pop("organization_uuid"))

        def _parse_actor(
            data: object,
        ) -> Union[
            "NetworkIPAccessActor",
            "NetworkUserAccessActor",
            "NetworkUserAccessActorV1",
            "SystemAccessActor",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                actor_type_0 = NetworkUserAccessActor.from_dict(data)

                return actor_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                actor_type_1 = NetworkUserAccessActorV1.from_dict(data)

                return actor_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                actor_type_2 = NetworkIPAccessActor.from_dict(data)

                return actor_type_2
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            actor_type_3 = SystemAccessActor.from_dict(data)

            return actor_type_3

        actor = _parse_actor(d.pop("actor"))

        def _parse_context(data: object) -> Union["AccessSessionContextType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                context_type_0 = AccessSessionContextType0.from_dict(data)

                return context_type_0
            except:  # noqa: E722
                pass
            return cast(Union["AccessSessionContextType0", None], data)

        context = _parse_context(d.pop("context"))

        created_at = isoparse(d.pop("created_at"))

        object_urn = d.pop("object_urn")

        access_session = cls(
            organization_uuid=organization_uuid,
            actor=actor,
            context=context,
            created_at=created_at,
            object_urn=object_urn,
        )

        access_session.additional_properties = d
        return access_session

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
