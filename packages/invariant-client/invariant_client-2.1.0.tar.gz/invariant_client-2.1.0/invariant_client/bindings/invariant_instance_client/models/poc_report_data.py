from collections.abc import Mapping
from typing import Any, TypeVar
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="POCReportData")


@_attrs_define
class POCReportData:
    """
    Attributes:
        issues (UUID):
        edges (UUID):
        routers (UUID):
        nodes (UUID):
        external_ports (UUID):
        rule_findings (UUID):
        connect_to (UUID):
    """

    issues: UUID
    edges: UUID
    routers: UUID
    nodes: UUID
    external_ports: UUID
    rule_findings: UUID
    connect_to: UUID
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        issues = str(self.issues)

        edges = str(self.edges)

        routers = str(self.routers)

        nodes = str(self.nodes)

        external_ports = str(self.external_ports)

        rule_findings = str(self.rule_findings)

        connect_to = str(self.connect_to)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "issues": issues,
                "edges": edges,
                "routers": routers,
                "nodes": nodes,
                "external_ports": external_ports,
                "rule_findings": rule_findings,
                "connectTo": connect_to,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        issues = UUID(d.pop("issues"))

        edges = UUID(d.pop("edges"))

        routers = UUID(d.pop("routers"))

        nodes = UUID(d.pop("nodes"))

        external_ports = UUID(d.pop("external_ports"))

        rule_findings = UUID(d.pop("rule_findings"))

        connect_to = UUID(d.pop("connectTo"))

        poc_report_data = cls(
            issues=issues,
            edges=edges,
            routers=routers,
            nodes=nodes,
            external_ports=external_ports,
            rule_findings=rule_findings,
            connect_to=connect_to,
        )

        poc_report_data.additional_properties = d
        return poc_report_data

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
