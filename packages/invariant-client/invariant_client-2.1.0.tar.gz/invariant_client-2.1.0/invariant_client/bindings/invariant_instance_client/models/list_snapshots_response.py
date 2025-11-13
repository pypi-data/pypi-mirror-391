from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.report_extras import ReportExtras
    from ..models.rule_summary_group_uploaded import RuleSummaryGroupUploaded
    from ..models.rule_summary_group_webrule import RuleSummaryGroupWebrule
    from ..models.snapshot_model import SnapshotModel


T = TypeVar("T", bound="ListSnapshotsResponse")


@_attrs_define
class ListSnapshotsResponse:
    """
    Attributes:
        snapshot (SnapshotModel):
        rules_summary (list[Union['RuleSummaryGroupUploaded', 'RuleSummaryGroupWebrule']]):
        extras (Union['ReportExtras', None]):
    """

    snapshot: "SnapshotModel"
    rules_summary: list[Union["RuleSummaryGroupUploaded", "RuleSummaryGroupWebrule"]]
    extras: Union["ReportExtras", None]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.report_extras import ReportExtras
        from ..models.rule_summary_group_webrule import RuleSummaryGroupWebrule

        snapshot = self.snapshot.to_dict()

        rules_summary = []
        for rules_summary_item_data in self.rules_summary:
            rules_summary_item: dict[str, Any]
            if isinstance(rules_summary_item_data, RuleSummaryGroupWebrule):
                rules_summary_item = rules_summary_item_data.to_dict()
            else:
                rules_summary_item = rules_summary_item_data.to_dict()

            rules_summary.append(rules_summary_item)

        extras: Union[None, dict[str, Any]]
        if isinstance(self.extras, ReportExtras):
            extras = self.extras.to_dict()
        else:
            extras = self.extras

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "snapshot": snapshot,
                "rules_summary": rules_summary,
                "extras": extras,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.report_extras import ReportExtras
        from ..models.rule_summary_group_uploaded import RuleSummaryGroupUploaded
        from ..models.rule_summary_group_webrule import RuleSummaryGroupWebrule
        from ..models.snapshot_model import SnapshotModel

        d = dict(src_dict)
        snapshot = SnapshotModel.from_dict(d.pop("snapshot"))

        rules_summary = []
        _rules_summary = d.pop("rules_summary")
        for rules_summary_item_data in _rules_summary:

            def _parse_rules_summary_item(
                data: object,
            ) -> Union["RuleSummaryGroupUploaded", "RuleSummaryGroupWebrule"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    rules_summary_item_type_0 = RuleSummaryGroupWebrule.from_dict(data)

                    return rules_summary_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                rules_summary_item_type_1 = RuleSummaryGroupUploaded.from_dict(data)

                return rules_summary_item_type_1

            rules_summary_item = _parse_rules_summary_item(rules_summary_item_data)

            rules_summary.append(rules_summary_item)

        def _parse_extras(data: object) -> Union["ReportExtras", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                extras_type_0 = ReportExtras.from_dict(data)

                return extras_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ReportExtras", None], data)

        extras = _parse_extras(d.pop("extras"))

        list_snapshots_response = cls(
            snapshot=snapshot,
            rules_summary=rules_summary,
            extras=extras,
        )

        list_snapshots_response.additional_properties = d
        return list_snapshots_response

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
