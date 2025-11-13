from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.report_task import ReportTask


T = TypeVar("T", bound="ListReportTasksResponse")


@_attrs_define
class ListReportTasksResponse:
    """
    Attributes:
        in_progress (list['ReportTask']):
    """

    in_progress: list["ReportTask"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        in_progress = []
        for in_progress_item_data in self.in_progress:
            in_progress_item = in_progress_item_data.to_dict()
            in_progress.append(in_progress_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "in_progress": in_progress,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.report_task import ReportTask

        d = dict(src_dict)
        in_progress = []
        _in_progress = d.pop("in_progress")
        for in_progress_item_data in _in_progress:
            in_progress_item = ReportTask.from_dict(in_progress_item_data)

            in_progress.append(in_progress_item)

        list_report_tasks_response = cls(
            in_progress=in_progress,
        )

        list_report_tasks_response.additional_properties = d
        return list_report_tasks_response

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
