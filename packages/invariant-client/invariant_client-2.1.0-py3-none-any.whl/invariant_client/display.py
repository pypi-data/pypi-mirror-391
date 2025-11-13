import enum
import json
import os
import pydoc
import sys
from typing import Any, Iterable, Mapping
from attr import asdict
import pandas
from rich import print_json
from tabulate import tabulate
from invariant_client.bindings.invariant_instance_client.models.get_report_summary_response import GetReportSummaryResponse
from invariant_client.pysdk import OutputFormat


def snapshot_status(response: GetReportSummaryResponse):
    """Display a message indicating the overall status of the analysis user task."""
    status = response.status.to_dict()
    status = status.get('state')
    if status == 'COMPLETE':
        pass
    elif status == 'FAILED':
        print("Error: Snapshot could not be evaluated.")
    elif status == 'INCOMPLETE':
        print("Error: Snapshot evaluation did not finish.")


# AP_KEYS = [
#     'critical_flows_ok', 'critical_flows_violations', 'critical_flows_violations_unenforced', 'critical_flows_skipped', 'critical_flows_details', 'critical_flows_logs',
#     'policy_ok', 'policy_violations', 'policy_violations_unenforced', 'policy_skipped', 'policy_details', 'policy_logs']


class CondensedOutcomes(str, enum.Enum):
    OK = "All rules passed"
    VIOLATIONS = "Rule violations found"
    NO_MODEL = "Could not model network"
    NO_RULES = "No rules provided"
    SKIPPED = "Some rules skipped"
    ERROR = "Processing failed"

    @classmethod
    def from_GetReportSummaryResponse(cls, response: GetReportSummaryResponse):
        """Map this response onto an outcome."""
        # Total disaster
        if response.status['state'] == 'FAILED':
            return cls.ERROR

        # No model could be created at all
        summary = response.summary.to_dict()
        if summary.get('nodes', None) is None:
            return cls.NO_MODEL

        # No rules were provided
        if summary.get('policy_violations', None) is None:
            return cls.NO_RULES

        # Violations found
        if summary.get('policy_violations', 0) + summary.get('critical_flows_violations', 0) > 0:
            return cls.VIOLATIONS

        # OK but some invalid rules were found
        if summary.get('policy_skipped', 0) + summary.get('critical_flows_skipped', 0) > 0:
            return cls.SKIPPED

        # OK
        if summary.get('policy_ok', 0) + summary.get('critical_flows_ok', 0) > 0:
            return cls.OK

        # if sum(summary.get(key, 0) for key in AP_KEYS) == 0:
        #     return cls.NO_RULES
        # Fall back to no-rules
        return cls.NO_RULES


def snapshot_condensed_status(response: GetReportSummaryResponse):
    """Display a single message indicating the overall snapshot outcome."""
    outcome = CondensedOutcomes.from_GetReportSummaryResponse(response)
    print(f"outcome: {outcome.value}")


def snapshot_summary_table(response: GetReportSummaryResponse, format: OutputFormat):
    """Display a table containing row counts for all emitted reports."""
    if format == OutputFormat.JSON:
        print_json(data=response.to_dict())
    elif format == OutputFormat.FAST_JSON:
        print(json.dumps(response.to_dict()))
    else:
        print_frame(pandas.DataFrame(response.summary.to_dict().items(), columns=['File', 'RowCount']), format)


def snapshot_halted(response: GetReportSummaryResponse):
    """Describe each halted step."""
    status = response.status.to_dict()
    halted = []
    def visit_step(step: dict, prefix: list):
        prefix = prefix + [step['name']] if prefix else [step['name']]
        if step['state'] != 'COMPLETE':
            halted.append((prefix, step))
        for child_step in step['steps']:
            visit_step(child_step, prefix)
    visit_step(status, None)
    if len(halted):
        print("\nThe following steps were not completed:")
        for prefix, step in halted:
            print(f"    {' > '.join(prefix)}")
            if step['state'] != 'FAILED':
                print(f"\n        {step['state']}")


def snapshot_errors(errors: pandas.DataFrame, format: OutputFormat):
    """Describe each error."""
    # Group errors by label, then repeat the header every 10th member
    for label, error_group in errors.groupby(by=['label']):
        label = label[0]
        for i, error in enumerate(error_group.to_dict(orient='records')):
            prefix = ""
            if not i % 10:
                prefix = f"In {label}{' (continued)' if i > 0 else ''}:\n\n"
            data = json.loads(error['detail'])
            if data['type'] == 'urn:invariant:errors:child_step_failed':
                continue
            if data['type'] == 'urn:invariant:errors:internal_exception':
                print(f"\nInternal error in {label}:\n    {data['detail']}", file=sys.stderr)
                continue

            print(f"\n{prefix}    {data['title']}\n    {data['detail']}", file=sys.stderr)
    print('', file=sys.stderr)

def print_frame(data: Mapping[str, Iterable[Any]] | Iterable[Iterable[Any]], format: OutputFormat):
    if format == OutputFormat.TSV:
        print(tabulate(data, headers='keys', tablefmt='tsv'))
    elif format == OutputFormat.TABULATE or format == OutputFormat.CONDENSED:
        os.environ["LESS"] = "-SXFRs"
        pydoc.pager(tabulate(data, headers='keys', tablefmt='psql'))
    else:
        raise ValueError(f"Unacceptable format: {format}")
