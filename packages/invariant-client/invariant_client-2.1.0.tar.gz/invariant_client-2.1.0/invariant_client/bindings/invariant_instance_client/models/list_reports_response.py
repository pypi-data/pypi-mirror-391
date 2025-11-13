from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.report import Report
    from ..models.report_extras import ReportExtras


T = TypeVar("T", bound="ListReportsResponse")


@_attrs_define
class ListReportsResponse:
    """
    Attributes:
        reports (list['Report']):
        with_extras (list['ReportExtras']):
    """

    reports: list["Report"]
    with_extras: list["ReportExtras"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reports = []
        for reports_item_data in self.reports:
            reports_item = reports_item_data.to_dict()
            reports.append(reports_item)

        with_extras = []
        for with_extras_item_data in self.with_extras:
            with_extras_item = with_extras_item_data.to_dict()
            with_extras.append(with_extras_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "reports": reports,
                "with_extras": with_extras,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.report import Report
        from ..models.report_extras import ReportExtras

        d = dict(src_dict)
        reports = []
        _reports = d.pop("reports")
        for reports_item_data in _reports:
            reports_item = Report.from_dict(reports_item_data)

            reports.append(reports_item)

        with_extras = []
        _with_extras = d.pop("with_extras")
        for with_extras_item_data in _with_extras:
            with_extras_item = ReportExtras.from_dict(with_extras_item_data)

            with_extras.append(with_extras_item)

        list_reports_response = cls(
            reports=reports,
            with_extras=with_extras,
        )

        list_reports_response.additional_properties = d
        return list_reports_response

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
