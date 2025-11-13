from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.list_snapshots_response import ListSnapshotsResponse
    from ..models.network import Network


T = TypeVar("T", bound="NetworkWithExtras")


@_attrs_define
class NetworkWithExtras:
    """
    Attributes:
        network (Network):
        current_snapshot (Union['ListSnapshotsResponse', None, Unset]):
    """

    network: "Network"
    current_snapshot: Union["ListSnapshotsResponse", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.list_snapshots_response import ListSnapshotsResponse

        network = self.network.to_dict()

        current_snapshot: Union[None, Unset, dict[str, Any]]
        if isinstance(self.current_snapshot, Unset):
            current_snapshot = UNSET
        elif isinstance(self.current_snapshot, ListSnapshotsResponse):
            current_snapshot = self.current_snapshot.to_dict()
        else:
            current_snapshot = self.current_snapshot

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "network": network,
            }
        )
        if current_snapshot is not UNSET:
            field_dict["current_snapshot"] = current_snapshot

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.list_snapshots_response import ListSnapshotsResponse
        from ..models.network import Network

        d = dict(src_dict)
        network = Network.from_dict(d.pop("network"))

        def _parse_current_snapshot(
            data: object,
        ) -> Union["ListSnapshotsResponse", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                current_snapshot_type_0 = ListSnapshotsResponse.from_dict(data)

                return current_snapshot_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ListSnapshotsResponse", None, Unset], data)

        current_snapshot = _parse_current_snapshot(d.pop("current_snapshot", UNSET))

        network_with_extras = cls(
            network=network,
            current_snapshot=current_snapshot,
        )

        network_with_extras.additional_properties = d
        return network_with_extras

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
