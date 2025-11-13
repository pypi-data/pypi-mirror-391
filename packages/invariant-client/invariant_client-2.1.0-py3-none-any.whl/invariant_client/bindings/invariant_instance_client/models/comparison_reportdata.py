from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.comparison_reportdata_files import ComparisonReportdataFiles
    from ..models.file_index import FileIndex


T = TypeVar("T", bound="ComparisonReportdata")


@_attrs_define
class ComparisonReportdata:
    """
    Attributes:
        files (ComparisonReportdataFiles):
        solutions (Union['FileIndex', None, UUID, Unset]):
    """

    files: "ComparisonReportdataFiles"
    solutions: Union["FileIndex", None, UUID, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.file_index import FileIndex

        files = self.files.to_dict()

        solutions: Union[None, Unset, dict[str, Any], str]
        if isinstance(self.solutions, Unset):
            solutions = UNSET
        elif isinstance(self.solutions, UUID):
            solutions = str(self.solutions)
        elif isinstance(self.solutions, FileIndex):
            solutions = self.solutions.to_dict()
        else:
            solutions = self.solutions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
            }
        )
        if solutions is not UNSET:
            field_dict["solutions"] = solutions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.comparison_reportdata_files import ComparisonReportdataFiles
        from ..models.file_index import FileIndex

        d = dict(src_dict)
        files = ComparisonReportdataFiles.from_dict(d.pop("files"))

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

        comparison_reportdata = cls(
            files=files,
            solutions=solutions,
        )

        comparison_reportdata.additional_properties = d
        return comparison_reportdata

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
