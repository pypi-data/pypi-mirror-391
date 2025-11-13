from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.comparison_reportdata import ComparisonReportdata
    from ..models.file_index import FileIndex
    from ..models.snapshot_report_data_files import SnapshotReportDataFiles


T = TypeVar("T", bound="SnapshotReportData")


@_attrs_define
class SnapshotReportData:
    """
    Attributes:
        files (SnapshotReportDataFiles):
        summary (Union['FileIndex', UUID]):
        status (Union['FileIndex', UUID]):
        errors (Union['FileIndex', UUID]):
        solutions (Union['FileIndex', None, UUID, Unset]):
        compare_to (Union['ComparisonReportdata', None, Unset]):
    """

    files: "SnapshotReportDataFiles"
    summary: Union["FileIndex", UUID]
    status: Union["FileIndex", UUID]
    errors: Union["FileIndex", UUID]
    solutions: Union["FileIndex", None, UUID, Unset] = UNSET
    compare_to: Union["ComparisonReportdata", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.comparison_reportdata import ComparisonReportdata
        from ..models.file_index import FileIndex

        files = self.files.to_dict()

        summary: Union[dict[str, Any], str]
        if isinstance(self.summary, UUID):
            summary = str(self.summary)
        else:
            summary = self.summary.to_dict()

        status: Union[dict[str, Any], str]
        if isinstance(self.status, UUID):
            status = str(self.status)
        else:
            status = self.status.to_dict()

        errors: Union[dict[str, Any], str]
        if isinstance(self.errors, UUID):
            errors = str(self.errors)
        else:
            errors = self.errors.to_dict()

        solutions: Union[None, Unset, dict[str, Any], str]
        if isinstance(self.solutions, Unset):
            solutions = UNSET
        elif isinstance(self.solutions, UUID):
            solutions = str(self.solutions)
        elif isinstance(self.solutions, FileIndex):
            solutions = self.solutions.to_dict()
        else:
            solutions = self.solutions

        compare_to: Union[None, Unset, dict[str, Any]]
        if isinstance(self.compare_to, Unset):
            compare_to = UNSET
        elif isinstance(self.compare_to, ComparisonReportdata):
            compare_to = self.compare_to.to_dict()
        else:
            compare_to = self.compare_to

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
                "summary": summary,
                "status": status,
                "errors": errors,
            }
        )
        if solutions is not UNSET:
            field_dict["solutions"] = solutions
        if compare_to is not UNSET:
            field_dict["compare_to"] = compare_to

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.comparison_reportdata import ComparisonReportdata
        from ..models.file_index import FileIndex
        from ..models.snapshot_report_data_files import SnapshotReportDataFiles

        d = dict(src_dict)
        files = SnapshotReportDataFiles.from_dict(d.pop("files"))

        def _parse_summary(data: object) -> Union["FileIndex", UUID]:
            try:
                if not isinstance(data, str):
                    raise TypeError()
                summary_type_0 = UUID(data)

                return summary_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            summary_type_1 = FileIndex.from_dict(data)

            return summary_type_1

        summary = _parse_summary(d.pop("summary"))

        def _parse_status(data: object) -> Union["FileIndex", UUID]:
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_0 = UUID(data)

                return status_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            status_type_1 = FileIndex.from_dict(data)

            return status_type_1

        status = _parse_status(d.pop("status"))

        def _parse_errors(data: object) -> Union["FileIndex", UUID]:
            try:
                if not isinstance(data, str):
                    raise TypeError()
                errors_type_0 = UUID(data)

                return errors_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            errors_type_1 = FileIndex.from_dict(data)

            return errors_type_1

        errors = _parse_errors(d.pop("errors"))

        def _parse_solutions(data: object) -> Union["FileIndex", None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                solutions_type_0 = UUID(data)

                return solutions_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                solutions_type_1 = FileIndex.from_dict(data)

                return solutions_type_1
            except:  # noqa: E722
                pass
            return cast(Union["FileIndex", None, UUID, Unset], data)

        solutions = _parse_solutions(d.pop("solutions", UNSET))

        def _parse_compare_to(
            data: object,
        ) -> Union["ComparisonReportdata", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                compare_to_type_0 = ComparisonReportdata.from_dict(data)

                return compare_to_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ComparisonReportdata", None, Unset], data)

        compare_to = _parse_compare_to(d.pop("compare_to", UNSET))

        snapshot_report_data = cls(
            files=files,
            summary=summary,
            status=status,
            errors=errors,
            solutions=solutions,
            compare_to=compare_to,
        )

        snapshot_report_data.additional_properties = d
        return snapshot_report_data

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
