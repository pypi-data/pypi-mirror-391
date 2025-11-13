import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.poc_report_data import POCReportData
    from ..models.report_metadata import ReportMetadata
    from ..models.snapshot_report_data import SnapshotReportData


T = TypeVar("T", bound="Report")


@_attrs_define
class Report:
    """
    Attributes:
        uuid (UUID):
        organization_uuid (UUID):
        network_uuid (UUID):
        reports (Union['POCReportData', 'SnapshotReportData']):
        metadata (ReportMetadata):
        created_at (datetime.datetime):
        snapshot_uuid (Union[None, UUID, Unset]):
    """

    uuid: UUID
    organization_uuid: UUID
    network_uuid: UUID
    reports: Union["POCReportData", "SnapshotReportData"]
    metadata: "ReportMetadata"
    created_at: datetime.datetime
    snapshot_uuid: Union[None, UUID, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.snapshot_report_data import SnapshotReportData

        uuid = str(self.uuid)

        organization_uuid = str(self.organization_uuid)

        network_uuid = str(self.network_uuid)

        reports: dict[str, Any]
        if isinstance(self.reports, SnapshotReportData):
            reports = self.reports.to_dict()
        else:
            reports = self.reports.to_dict()

        metadata = self.metadata.to_dict()

        created_at = self.created_at.isoformat()

        snapshot_uuid: Union[None, Unset, str]
        if isinstance(self.snapshot_uuid, Unset):
            snapshot_uuid = UNSET
        elif isinstance(self.snapshot_uuid, UUID):
            snapshot_uuid = str(self.snapshot_uuid)
        else:
            snapshot_uuid = self.snapshot_uuid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "organization_uuid": organization_uuid,
                "network_uuid": network_uuid,
                "reports": reports,
                "metadata": metadata,
                "created_at": created_at,
            }
        )
        if snapshot_uuid is not UNSET:
            field_dict["snapshot_uuid"] = snapshot_uuid

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.poc_report_data import POCReportData
        from ..models.report_metadata import ReportMetadata
        from ..models.snapshot_report_data import SnapshotReportData

        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        organization_uuid = UUID(d.pop("organization_uuid"))

        network_uuid = UUID(d.pop("network_uuid"))

        def _parse_reports(
            data: object,
        ) -> Union["POCReportData", "SnapshotReportData"]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                reports_type_0 = SnapshotReportData.from_dict(data)

                return reports_type_0
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            reports_type_1 = POCReportData.from_dict(data)

            return reports_type_1

        reports = _parse_reports(d.pop("reports"))

        metadata = ReportMetadata.from_dict(d.pop("metadata"))

        created_at = isoparse(d.pop("created_at"))

        def _parse_snapshot_uuid(data: object) -> Union[None, UUID, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                snapshot_uuid_type_0 = UUID(data)

                return snapshot_uuid_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, UUID, Unset], data)

        snapshot_uuid = _parse_snapshot_uuid(d.pop("snapshot_uuid", UNSET))

        report = cls(
            uuid=uuid,
            organization_uuid=organization_uuid,
            network_uuid=network_uuid,
            reports=reports,
            metadata=metadata,
            created_at=created_at,
            snapshot_uuid=snapshot_uuid,
        )

        report.additional_properties = d
        return report

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
