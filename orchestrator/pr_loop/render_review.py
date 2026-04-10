from __future__ import annotations

from pathlib import Path

from orchestrator.pr_loop.gate_check import evaluate_pr_loop_fixture_gate
from orchestrator.pr_loop.inspect import inspect_pr_loop_fixture, validate_pr_id


def render_pr_loop_review_packet(*, root_dir: Path, pr_id: str) -> str:
    pr_id = validate_pr_id(pr_id)
    inspection = inspect_pr_loop_fixture(root_dir=root_dir, pr_id=pr_id)
    gate_check = evaluate_pr_loop_fixture_gate(root_dir=root_dir, pr_id=pr_id)

    lines = ["# PR Loop Review Packet Draft"]
    lines.append("")
    lines.append("## Findings Input")
    failed_conditions = gate_check.get("failed_conditions")
    if isinstance(failed_conditions, list) and failed_conditions:
        for condition in failed_conditions:
            if not isinstance(condition, dict):
                continue
            lines.append(f"- condition: {_display(condition.get('name'))}")
            lines.append(f"  reason: {_display(condition.get('reason'))}")
    else:
        lines.append("- none from local fixture gate summary")

    lines.append("")
    lines.append("## Review Packet Facts")
    lines.append(f"- pr_id: {pr_id}")
    lines.append("- source: local_non_runtime_fixture")
    lines.append(f"- fixture_status: {_display(inspection.get('fixture_status'))}")
    lines.append(f"- gate_status: {_display(gate_check.get('gate_status'))}")
    lines.append(f"- failed_condition_count: {_display(gate_check.get('failed_condition_count'))}")
    lines.append(f"- required_file_count: {_display(inspection.get('required_file_count'))}")
    lines.append(f"- present_file_count: {_display(inspection.get('present_file_count'))}")

    missing_files = inspection.get("missing_files")
    lines.append("")
    lines.append("## Fixture Completeness")
    if isinstance(missing_files, list) and missing_files:
        for missing_file in missing_files:
            lines.append(f"- missing_fixture_file: {missing_file}")
    else:
        lines.append("- missing_fixture_file: none")
    lines.append(f"- inspect_note: {_display(inspection.get('note'))}")

    lines.append("")
    lines.append("## Review Scope Reminder")
    lines.append("- Use this packet as findings-first review drafting input only.")
    lines.append("- Verify code diff, tests, docs sync, and repo artifacts separately.")
    lines.append("- Do not treat trace/debug output or fixture fields as live runtime facts.")

    lines.append("")
    lines.append("## Non Authority Reminder")
    lines.append("- runtime_authority: none")
    lines.append("- merge_authority: none")
    lines.append("- approval_authority: none")
    lines.append("- mutation: none")
    lines.append("- fixture_scope: local inert fixture only")

    lines.append("")
    lines.append("## Reviewer Focus Checklist")
    lines.append("- Material findings before summary.")
    lines.append("- Scope drift from the explicit PR id.")
    lines.append("- Mismatch between README, plan, help text, validator, output, and tests.")
    lines.append("- Any claim that fixture data is live runtime state, gate evidence, or merge authority.")

    return "\n".join(lines)


def _display(value: object) -> str:
    if value is None:
        return "none"
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)
