from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ReportExtras")


@_attrs_define
class ReportExtras:
    """
    Attributes:
        report_uuid (UUID):
        network_name (str):
        cf_violations (int):
        ap_violations (int):
        node_count (int):
        rule_count (int):
        status (str):
        errors_count (int):
        errors_lines (list[str]):
    """

    report_uuid: UUID
    network_name: str
    cf_violations: int
    ap_violations: int
    node_count: int
    rule_count: int
    status: str
    errors_count: int
    errors_lines: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        report_uuid = str(self.report_uuid)

        network_name = self.network_name

        cf_violations = self.cf_violations

        ap_violations = self.ap_violations

        node_count = self.node_count

        rule_count = self.rule_count

        status = self.status

        errors_count = self.errors_count

        errors_lines = self.errors_lines

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "report_uuid": report_uuid,
                "network_name": network_name,
                "cf_violations": cf_violations,
                "ap_violations": ap_violations,
                "node_count": node_count,
                "rule_count": rule_count,
                "status": status,
                "errors_count": errors_count,
                "errors_lines": errors_lines,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        report_uuid = UUID(d.pop("report_uuid"))

        network_name = d.pop("network_name")

        cf_violations = d.pop("cf_violations")

        ap_violations = d.pop("ap_violations")

        node_count = d.pop("node_count")

        rule_count = d.pop("rule_count")

        status = d.pop("status")

        errors_count = d.pop("errors_count")

        errors_lines = cast(list[str], d.pop("errors_lines"))

        report_extras = cls(
            report_uuid=report_uuid,
            network_name=network_name,
            cf_violations=cf_violations,
            ap_violations=ap_violations,
            node_count=node_count,
            rule_count=rule_count,
            status=status,
            errors_count=errors_count,
            errors_lines=errors_lines,
        )

        report_extras.additional_properties = d
        return report_extras

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
