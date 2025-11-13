from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.exec_response_result_files import ExecResponseResultFiles
    from ..models.exec_response_results import ExecResponseResults


T = TypeVar("T", bound="ExecResponse")


@_attrs_define
class ExecResponse:
    """
    Attributes:
        exec_uuid (UUID):
        snapshot_uuid (UUID):
        results (ExecResponseResults):
        result_files (ExecResponseResultFiles):
        elapsed (float):
    """

    exec_uuid: UUID
    snapshot_uuid: UUID
    results: "ExecResponseResults"
    result_files: "ExecResponseResultFiles"
    elapsed: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        exec_uuid = str(self.exec_uuid)

        snapshot_uuid = str(self.snapshot_uuid)

        results = self.results.to_dict()

        result_files = self.result_files.to_dict()

        elapsed = self.elapsed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "exec_uuid": exec_uuid,
                "snapshot_uuid": snapshot_uuid,
                "results": results,
                "result_files": result_files,
                "elapsed": elapsed,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.exec_response_result_files import ExecResponseResultFiles
        from ..models.exec_response_results import ExecResponseResults

        d = dict(src_dict)
        exec_uuid = UUID(d.pop("exec_uuid"))

        snapshot_uuid = UUID(d.pop("snapshot_uuid"))

        results = ExecResponseResults.from_dict(d.pop("results"))

        result_files = ExecResponseResultFiles.from_dict(d.pop("result_files"))

        elapsed = d.pop("elapsed")

        exec_response = cls(
            exec_uuid=exec_uuid,
            snapshot_uuid=snapshot_uuid,
            results=results,
            result_files=result_files,
            elapsed=elapsed,
        )

        exec_response.additional_properties = d
        return exec_response

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
