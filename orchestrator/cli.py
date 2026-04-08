from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from orchestrator.pipeline import (
    activate_pr,
    bootstrap_run,
    build_approval_request,
    cleanup_rehearsal_artifacts,
    create_clarification,
    draft_clarifications,
    draft_pr_plan,
    draft_work_items,
    create_goal,
    create_pr_plan,
    create_work_item,
    draft_approval_packet,
    evaluate_gates,
    get_factory_status,
    get_work_item_readiness,
    inspect_approval,
    inspect_draft_approval,
    inspect_approval_queue,
    inspect_clarification,
    inspect_goal,
    inspect_orchestration,
    inspect_pr_plan,
    inspect_run,
    inspect_work_item,
    parse_hygiene_approval_queue_selector,
    apply_hygiene_approval_queue_target,
    promote_clarification_draft,
    promote_pr_plan_draft,
    promote_work_item_draft,
    record_docs_sync,
    record_qa,
    record_review,
    record_verification,
    resolve_clarification,
    resolve_hygiene_approval_queue_dry_run_target,
    resolve_latest_run_id,
    resolve_approval,
    start_execution,
    suggest_next_pr,
    trace_run,
    trace_lineage,
)
from orchestrator.yaml_io import read_yaml


def _default_run_id() -> str:
    return datetime.now(timezone.utc).strftime("RUN-%Y%m%dT%H%M%SZ")


def _render_status(status: dict[str, object]) -> str:
    lines = ["Active PR:"]

    active_pr = status["active_pr"]
    if isinstance(active_pr, dict):
        lines.append(f"- pr_id: {active_pr['pr_id']}")
        lines.append(f"- work_item_id: {active_pr['work_item_id']}")
        if active_pr.get("path"):
            lines.append(f"- path: {active_pr['path']}")
    else:
        lines.append("- none")

    active_pr_readiness = status.get("active_pr_readiness")
    if isinstance(active_pr, dict):
        lines.append("")
        lines.append("Work Item Readiness:")
        if isinstance(active_pr_readiness, dict) and active_pr_readiness.get("error"):
            lines.append("- status: unavailable")
            lines.append(f"- work_item_id: {active_pr_readiness['work_item_id']}")
            lines.append(f"- reason: {active_pr_readiness['error']}")
        elif isinstance(active_pr_readiness, dict):
            lines.append(f"- summary: {active_pr_readiness['overall_readiness_summary']}")
            lines.append(f"- linked_clarifications: {active_pr_readiness['linked_clarification_count']}")
        else:
            lines.append("- none")

    lines.append("")
    lines.append("Latest Run:")
    latest_run = status["latest_run"]
    if isinstance(latest_run, dict):
        lines.append(f"- run_id: {latest_run['run_id']}")
        lines.append(f"- state: {latest_run['state']}")
        if latest_run.get("path"):
            lines.append(f"- path: {latest_run['path']}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Approval:")
    approval = status["approval"]
    lines.append(f"- status: {approval['status']}")
    if isinstance(approval, dict) and approval.get("path"):
        lines.append(f"- path: {approval['path']}")

    lines.append("")
    lines.append("Approval Queue:")
    approval_queue = status["approval_queue"]
    lines.append(f"- pending_total: {approval_queue['pending_total']}")
    lines.append(f"- latest_run_has_pending: {approval_queue['latest_run_has_pending']}")
    lines.append(f"- stale_pending_count: {approval_queue['stale_pending_count']}")
    stale_run_ids = approval_queue.get("stale_pending_run_ids") or []
    if stale_run_ids:
        lines.append(f"- stale_pending_run_ids: {', '.join(stale_run_ids)}")
    else:
        lines.append("- stale_pending_run_ids: none")
    stale_paths = approval_queue.get("stale_pending_paths") or []
    if stale_paths:
        for stale_path in stale_paths:
            lines.append(f"- stale_pending_path: {stale_path}")
    else:
        lines.append("- stale_pending_path: none")

    open_clarifications = status["open_clarifications"]
    if isinstance(open_clarifications, list) and open_clarifications:
        lines.append("")
        lines.append(f"Open Clarifications ({len(open_clarifications)}):")
        for clarification_id in open_clarifications:
            lines.append(f"- clarification_id: {clarification_id}")

    return "\n".join(lines)


def _render_approval_queue_inspection(inspection: dict[str, object]) -> str:
    lines = ["Approval Queue Inspection:"]
    lines.append(f"- latest_run_id: {inspection.get('latest_run_id') or 'none'}")
    lines.append(f"- pending_total: {inspection['pending_total']}")
    relation_summary = inspection.get("latest_relation_summary")
    if not isinstance(relation_summary, dict):
        relation_summary = {}

    lines.append("")
    lines.append("Relation Summary:")
    lines.append(f"- latest_relation_count_latest: {relation_summary.get('latest_relation_count_latest', 0)}")
    lines.append(f"- latest_relation_count_stale: {relation_summary.get('latest_relation_count_stale', 0)}")
    lines.append(f"- latest_relation_count_no_latest_run: {relation_summary.get('latest_relation_count_no_latest_run', 0)}")
    lines.append(f"- latest_relation_count_unparseable: {relation_summary.get('latest_relation_count_unparseable', 0)}")

    lines.append("")
    lines.append("Pending Approvals:")
    items = inspection.get("items")
    if not isinstance(items, list) or not items:
        lines.append("- none")
        return "\n".join(lines)

    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        lines.append(f"- item: {index}")
        lines.append(f"  path: {item['path']}")
        lines.append(f"  parsed_run_id: {item.get('parsed_run_id') or 'unparseable'}")
        lines.append(f"  latest_relation: {item['latest_relation']}")
        lines.append(f"  matching_run_path: {item.get('matching_run_path') or 'none'}")
        lines.append(f"  matching_pr_id: {item.get('matching_pr_id') or 'none'}")
        lines.append(f"  matching_run_state: {item.get('matching_run_state') or 'none'}")
        lines.append(f"  readiness_context: {item['readiness_context_presence']}")
        queue_hygiene_audit = item.get("queue_hygiene_audit")
        if isinstance(queue_hygiene_audit, dict) and queue_hygiene_audit:
            lines.append("  queue_hygiene_audit:")
            for field in (
                "status",
                "applied_at",
                "selector_family",
                "requested_run_id",
                "requested_approval_id",
            ):
                if field in queue_hygiene_audit:
                    lines.append(f"    {field}: {queue_hygiene_audit[field]}")
            lines.append(
                "  queue_hygiene_note: read-only operator visibility only; exact stored audit fields only; not cleanup, resolve, approval decision, readiness/gate, selector, latest/stale relation, or Relation Summary state"
            )
        lines.append(f"  note: {item.get('note') or 'none'}")
    return "\n".join(lines)


def _render_suggest_next_pr(suggestion: dict[str, object]) -> str:
    lines = ["Short State Block:"]
    short_state = suggestion.get("short_state_block")
    if isinstance(short_state, dict):
        lines.append(f"- branch: {short_state.get('branch') or 'unavailable'}")
        lines.append(f"- active_pr: {short_state.get('active_pr') or 'none'}")
        lines.append(f"- latest_run_id: {short_state.get('latest_run_id') or 'none'}")
        lines.append(f"- latest_run_state: {short_state.get('latest_run_state') or 'none'}")
        lines.append(f"- approval_status: {short_state.get('approval_status') or 'none'}")
        lines.append(f"- pending_total: {short_state.get('pending_total')}")
        lines.append(f"- stale_pending_count: {short_state.get('stale_pending_count')}")
        lines.append(f"- open_clarification_count: {short_state.get('open_clarification_count')}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Assist-Only Flow:")
    lines.append(f"- note: {suggestion.get('flow_note') or 'short state block only'}")
    lines.append(f"- assist_only_note: {suggestion.get('assist_only_note') or 'read-only operator assist only'}")
    if suggestion.get("current_branch_note"):
        lines.append(f"- current_branch_note: {suggestion.get('current_branch_note')}")
    if suggestion.get("ambiguity_note"):
        lines.append(f"- ambiguity_note: {suggestion.get('ambiguity_note')}")

    if suggestion.get("mode") in {"active-pr-present", "active-pr-ambiguous"}:
        lines.append("")
        lines.append("PR Suggestion:")
        lines.append("- none")
        if suggestion.get("mode") == "active-pr-ambiguous":
            lines.append("")
            lines.append("Active PR Context:")
            active_prs = suggestion.get("active_prs")
            if isinstance(active_prs, list) and active_prs:
                for active_pr in active_prs:
                    if not isinstance(active_pr, dict):
                        continue
                    lines.append(f"- active_pr_id: {active_pr.get('pr_id') or 'unknown'}")
                    lines.append(f"  work_item_id: {active_pr.get('work_item_id') or 'unknown'}")
                    lines.append(f"  path: {active_pr.get('path') or 'none'}")
            else:
                lines.append("- none")
        else:
            active_pr = suggestion.get("active_pr")
            if isinstance(active_pr, dict):
                lines.append(f"- active_pr_id: {active_pr.get('pr_id') or 'unknown'}")
                lines.append(f"- work_item_id: {active_pr.get('work_item_id') or 'unknown'}")
                lines.append(f"- path: {active_pr.get('path') or 'none'}")
        return "\n".join(lines)

    suggested_pr = suggestion.get("suggested_pr")
    lines.append("")
    lines.append("PR Suggestion:")
    if isinstance(suggested_pr, dict):
        lines.append(f"- pr_id: {suggested_pr.get('pr_id') or 'none'}")
        lines.append(f"- branch: {suggested_pr.get('branch') or 'none'}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Minimum Execution Packet:")
    packet = suggestion.get("minimum_execution_packet")
    if isinstance(packet, dict):
        lines.append(f"- branch_name: {packet.get('branch_name') or 'none'}")
        work_scope = packet.get("work_scope")
        if isinstance(work_scope, list) and work_scope:
            for item in work_scope[:2]:
                lines.append(f"- work_scope: {item}")
        else:
            lines.append("- work_scope: none")
        validation_commands = packet.get("validation_commands")
        if isinstance(validation_commands, list) and validation_commands:
            for command in validation_commands:
                lines.append(f"- validation_command: {command}")
        else:
            lines.append("- validation_command: none")
        lines.append(f"- closeout_log_format: {packet.get('closeout_log_format') or 'none'}")
    else:
        lines.append("- none")

    return "\n".join(lines)


def _render_approval_inspection(inspection: dict[str, object]) -> str:
    lines = ["Approval Inspection:"]
    lines.append(f"- run_id: {inspection.get('run_id') or 'none'}")
    lines.append(f"- run_path: {inspection.get('run_path') or 'none'}")
    lines.append(f"- run_exists: {inspection['run_exists']}")
    lines.append(f"- run_state: {inspection.get('run_state') or 'none'}")
    lines.append(f"- approval_request_path: {inspection.get('approval_request_path') or 'none'}")
    lines.append(f"- approval_request_exists: {inspection['approval_request_exists']}")
    lines.append(f"- approval_request_status: {inspection.get('approval_request_status') or 'none'}")
    lines.append(f"- evidence_bundle_path: {inspection.get('evidence_bundle_path') or 'none'}")
    lines.append(f"- evidence_bundle_exists: {inspection['evidence_bundle_exists']}")
    lines.append(f"- readiness_summary: {inspection.get('readiness_summary') or 'none'}")
    lines.append(f"- degraded_note: {inspection.get('degraded_note') or 'none'}")
    return "\n".join(lines)


def _render_draft_approval_inspection(inspection: dict[str, object]) -> str:
    lines = ["Draft Summary"]
    draft_summary = inspection.get("draft_summary")
    if isinstance(draft_summary, dict):
        lines.append(f"- run_id: {inspection.get('run_id') or 'none'}")
        lines.append(f"- draft_path: {inspection.get('draft_path') or 'none'}")
        lines.append(f"- canonical_run_path: {inspection.get('canonical_run_path') or 'none'}")
        lines.append(
            f"- canonical_approval_request_path: {inspection.get('canonical_approval_request_path') or 'none'}"
        )
        lines.append(f"- draft_status: {draft_summary.get('draft_status') or 'none'}")
        lines.append(f"- canonical: {draft_summary.get('canonical')}")
        lines.append(f"- approval_id: {draft_summary.get('approval_id') or 'none'}")
        lines.append(f"- work_item_id: {draft_summary.get('work_item_id') or 'none'}")
        lines.append(f"- pr_id: {draft_summary.get('pr_id') or 'none'}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Sanity Check")
    sanity_check = inspection.get("sanity_check")
    if isinstance(sanity_check, dict):
        lines.append(f"- run_id_match: {sanity_check.get('run_id_match')}")
        lines.append(f"- required_fields_present: {sanity_check.get('required_fields_present')}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Legacy Residue")
    legacy_residue = inspection.get("legacy_residue")
    if isinstance(legacy_residue, dict):
        draft_present = bool(legacy_residue.get("draft_present"))
        canonical_present = bool(legacy_residue.get("canonical_present"))
        if draft_present or canonical_present:
            lines.append(f"- draft_present: {draft_present}")
            lines.append(f"- canonical_present: {canonical_present}")
            lines.append("- note: legacy approval field residue detected; compare and clean up manually")
        else:
            lines.append("- none")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Diff Summary")
    diff_summary = inspection.get("diff_summary")
    if isinstance(diff_summary, list) and diff_summary:
        for entry in diff_summary:
            if not isinstance(entry, dict):
                continue
            lines.append(f"- field: {entry.get('field') or 'unknown'}")
            lines.append(f"  draft: {entry.get('draft') or 'none'}")
            lines.append(f"  canonical: {entry.get('canonical') or 'none'}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Operator Note")
    operator_note = inspection.get("operator_note")
    if isinstance(operator_note, dict):
        lines.append(f"- {operator_note.get('assist_only') or 'assist only'}")
    else:
        lines.append("- assist only")
    return "\n".join(lines)


def _render_review_approval_summary(inspection: dict[str, object], run_id: str) -> str:
    return "\n".join(
        [
            _render_draft_approval_inspection(inspection),
            "",
            "Next step (manual):",
            f"python -m factory build-approval --root . --run-id {run_id}",
            "manual follow-up only",
            "no approval command was executed",
        ]
    )


def _render_run_inspection(inspection: dict[str, object]) -> str:
    lines = ["Run Inspection:"]
    lines.append(f"- run_id: {inspection.get('run_id') or 'none'}")
    lines.append(f"- run_path: {inspection.get('run_path') or 'none'}")
    lines.append(f"- run_exists: {inspection['run_exists']}")
    lines.append(f"- run_state: {inspection.get('run_state') or 'none'}")
    lines.append(f"- latest_relation: {inspection.get('latest_relation') or 'none'}")
    lines.append(f"- active_pr_relation: {inspection.get('active_pr_relation') or 'none'}")
    lines.append(f"- degraded_note: {inspection.get('degraded_note') or 'none'}")

    lines.append("")
    lines.append("Artifacts:")
    artifacts = inspection.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        lines.append("- none")
        return "\n".join(lines)

    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        lines.append(f"- artifact: {artifact.get('artifact') or 'unknown'}")
        lines.append(f"  path: {artifact.get('path') or 'none'}")
        lines.append(f"  exists: {artifact.get('exists')}")
        lines.append(f"  status: {artifact.get('status') or 'none'}")
        lines.append(f"  note: {artifact.get('note') or 'none'}")

    return "\n".join(lines)


def _render_pr_plan_inspection(inspection: dict[str, object]) -> str:
    lines = ["PR Plan Inspection:"]
    lines.append(f"- pr_id: {inspection.get('pr_id') or 'none'}")
    lines.append(f"- plan_path: {inspection.get('plan_path') or 'none'}")
    lines.append(f"- exists: {inspection['exists']}")
    lines.append(f"- active_relation: {inspection.get('active_relation') or 'none'}")
    lines.append(f"- source_goal_id: {inspection.get('source_goal_id') or 'none'}")
    lines.append(f"- source_work_item_id: {inspection.get('source_work_item_id') or 'none'}")
    lines.append(f"- metadata_timestamp: {inspection.get('metadata_timestamp') or 'none'}")
    lines.append(f"- degraded_note: {inspection.get('degraded_note') or 'none'}")

    lines.append("")
    lines.append("Linked Clarifications:")
    linked_clarification_ids = inspection.get("linked_clarification_ids")
    if isinstance(linked_clarification_ids, list) and linked_clarification_ids:
        for clarification_id in linked_clarification_ids:
            lines.append(f"- clarification_id: {clarification_id}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Readiness Visibility:")
    readiness_visibility = inspection.get("readiness_visibility")
    if isinstance(readiness_visibility, dict) and readiness_visibility:
        lines.append(f"- summary: {readiness_visibility.get('summary') or 'none'}")
        lines.append(
            f"- linked_clarification_count: {readiness_visibility.get('linked_clarification_count') or 'none'}"
        )
        context = readiness_visibility.get("context")
        if isinstance(context, list) and context:
            for entry in context:
                if isinstance(entry, dict):
                    lines.append(f"- context: {entry.get('label') or 'unknown'} = {entry.get('value') or 'none'}")
    else:
        lines.append("- none")

    return "\n".join(lines)


def _render_work_item_inspection(inspection: dict[str, object]) -> str:
    lines = ["Work Item Inspection:"]
    lines.append(f"- work_item_id: {inspection.get('work_item_id') or 'none'}")
    lines.append(f"- work_item_path: {inspection.get('work_item_path') or 'none'}")
    lines.append(f"- exists: {inspection['exists']}")
    lines.append(f"- title: {inspection.get('title') or 'none'}")
    lines.append(f"- summary: {inspection.get('summary') or 'none'}")
    lines.append(f"- goal_id: {inspection.get('goal_id') or 'none'}")
    lines.append(f"- metadata_timestamp: {inspection.get('metadata_timestamp') or 'none'}")
    lines.append(f"- degraded_note: {inspection.get('degraded_note') or 'none'}")

    lines.append("")
    lines.append("Linked Clarifications:")
    linked_clarification_ids = inspection.get("linked_clarification_ids")
    if isinstance(linked_clarification_ids, list) and linked_clarification_ids:
        for clarification_id in linked_clarification_ids:
            lines.append(f"- clarification_id: {clarification_id}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Readiness Visibility:")
    readiness_visibility = inspection.get("readiness_visibility")
    if isinstance(readiness_visibility, dict) and readiness_visibility:
        linked_clarification_count = readiness_visibility.get("linked_clarification_count")
        lines.append(f"- summary: {readiness_visibility.get('summary') or 'none'}")
        lines.append(f"- linked_clarification_count: {linked_clarification_count if linked_clarification_count is not None else 'none'}")
        context = readiness_visibility.get("context")
        if isinstance(context, list) and context:
            for entry in context:
                if isinstance(entry, dict):
                    lines.append(
                        f"- clarification: {entry.get('clarification_id') or 'unknown'} = {entry.get('status') or 'none'}"
                    )
    else:
        lines.append("- none")

    return "\n".join(lines)


def _render_orchestration_inspection(inspection: dict[str, object]) -> str:
    lines = ["Orchestration Inspection:"]

    anchor = inspection.get("anchor")
    if not isinstance(anchor, dict):
        anchor = {}
    lines.append("")
    lines.append("Anchor Summary:")
    lines.append(f"- work_item_id: {anchor.get('work_item_id') or 'none'}")
    lines.append(f"- work_item_path: {anchor.get('work_item_path') or 'none'}")
    lines.append(f"- exists: {anchor.get('exists')}")
    lines.append(f"- title: {anchor.get('title') or 'none'}")
    lines.append(f"- goal_id: {anchor.get('goal_id') or 'none'}")
    lines.append("- anchor_mode: exact anchor only")
    lines.append("- visibility_note: read-only operator visibility only")

    linked = inspection.get("linked_official_artifacts")
    if not isinstance(linked, dict):
        linked = {}
    pr_plans = linked.get("pr_plans")
    if not isinstance(pr_plans, list):
        pr_plans = []
    runs = linked.get("runs")
    if not isinstance(runs, list):
        runs = []

    lines.append("")
    lines.append("Linked Official Artifact Summary:")
    lines.append("- source_rule: official artifact summary only")
    lines.append(f"- linked_pr_plan_count: {len(pr_plans)}")
    lines.append(f"- linked_run_count: {len(runs)}")

    lines.append("")
    lines.append("PR Plans:")
    if pr_plans:
        for plan in pr_plans:
            if not isinstance(plan, dict):
                continue
            lines.append(f"- pr_id: {plan.get('pr_id') or 'none'}")
            lines.append(f"  location: {plan.get('location') or 'none'}")
            lines.append(f"  path: {plan.get('path') or 'none'}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Runs:")
    if runs:
        for run in runs:
            if not isinstance(run, dict):
                continue
            lines.append(f"- run_id: {run.get('run_id') or 'none'}")
            lines.append(f"  state: {run.get('state') or 'none'}")
            lines.append(f"  pr_id: {run.get('pr_id') or 'none'}")
            lines.append(f"  path: {run.get('path') or 'none'}")
            lines.append(f"  approval_request_status: {run.get('approval_request_status') or 'none'}")
            queue_entries = run.get("queue_entries")
            if isinstance(queue_entries, list) and queue_entries:
                for entry in queue_entries:
                    if not isinstance(entry, dict):
                        continue
                    lines.append(f"  queue_status: {entry.get('queue_status') or 'none'}")
                    lines.append(f"  queue_path: {entry.get('path') or 'none'}")
            else:
                lines.append("  queue_status: none")
                lines.append("  queue_path: none")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Ambiguity / Incomplete State:")
    note_parts = [
        value
        for value in (
            inspection.get("ambiguity_note"),
            inspection.get("incomplete_state_note"),
            inspection.get("degraded_note"),
        )
        if value
    ]
    if note_parts:
        for note in note_parts:
            lines.append(f"- note: {note}")
    else:
        lines.append("- note: none")

    lines.append("")
    lines.append("Possible Next Manual Step:")
    next_step = inspection.get("possible_next_manual_step")
    if next_step:
        lines.append(f"- possible next manual step: {next_step}")
    else:
        lines.append("- none")

    return "\n".join(lines)


def _render_clarification_inspection(inspection: dict[str, object]) -> str:
    lines = ["Clarification Inspection:"]
    lines.append(f"- clarification_id: {inspection.get('clarification_id') or 'none'}")
    lines.append(f"- clarification_path: {inspection.get('clarification_path') or 'none'}")
    lines.append(f"- exists: {inspection['exists']}")
    lines.append(f"- title: {inspection.get('title') or 'none'}")
    lines.append(f"- question: {inspection.get('question') or 'none'}")
    lines.append(f"- summary: {inspection.get('summary') or 'none'}")
    lines.append(f"- status: {inspection.get('status') or 'none'}")
    lines.append(f"- goal_id: {inspection.get('goal_id') or 'none'}")
    lines.append(f"- metadata_timestamp: {inspection.get('metadata_timestamp') or 'none'}")
    lines.append(f"- degraded_note: {inspection.get('degraded_note') or 'none'}")

    lines.append("")
    lines.append("Linked Work Items:")
    linked_work_item_ids = inspection.get("linked_work_item_ids")
    if isinstance(linked_work_item_ids, list) and linked_work_item_ids:
        for work_item_id in linked_work_item_ids:
            lines.append(f"- work_item_id: {work_item_id}")
    else:
        lines.append("- none")

    return "\n".join(lines)


def _render_goal_inspection(inspection: dict[str, object]) -> str:
    lines = ["Goal Inspection:"]
    lines.append(f"- goal_id: {inspection.get('goal_id') or 'none'}")
    lines.append(f"- goal_path: {inspection.get('goal_path') or 'none'}")
    lines.append(f"- exists: {inspection['exists']}")
    lines.append(f"- title: {inspection.get('title') or 'none'}")
    lines.append(f"- summary: {inspection.get('summary') or 'none'}")
    lines.append(f"- status: {inspection.get('status') or 'none'}")
    lines.append(f"- metadata_timestamp: {inspection.get('metadata_timestamp') or 'none'}")
    lines.append(f"- degraded_note: {inspection.get('degraded_note') or 'none'}")

    lines.append("")
    lines.append("Linked Clarifications:")
    linked_clarification_ids = inspection.get("linked_clarification_ids")
    if isinstance(linked_clarification_ids, list) and linked_clarification_ids:
        for clarification_id in linked_clarification_ids:
            lines.append(f"- clarification_id: {clarification_id}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Linked Work Items:")
    linked_work_item_ids = inspection.get("linked_work_item_ids")
    if isinstance(linked_work_item_ids, list) and linked_work_item_ids:
        for work_item_id in linked_work_item_ids:
            lines.append(f"- work_item_id: {work_item_id}")
    else:
        lines.append("- none")

    return "\n".join(lines)


def _render_lineage_trace(trace: dict[str, object]) -> str:
    lines = ["Lineage Trace:"]

    run = trace["run"]
    lines.append("Run:")
    lines.append(f"- run_id: {run.get('run_id') or 'none'}")
    lines.append(f"- run_path: {run.get('run_path') or 'none'}")
    lines.append(f"- run_state: {run.get('run_state') or 'none'}")

    approval = trace["approval"]
    lines.append("")
    lines.append("Approval:")
    lines.append(f"- approval_request_path: {approval.get('approval_request_path') or 'none'}")
    lines.append(f"- approval_request_status: {approval.get('approval_request_status') or 'none'}")
    lines.append(f"- queue_path: {approval.get('queue_path') or 'none'}")
    lines.append(f"- queue_status: {approval.get('queue_status') or 'none'}")

    pr_plan = trace["pr_plan"]
    lines.append("")
    lines.append("PR Plan:")
    lines.append(f"- pr_id: {pr_plan.get('pr_id') or 'none'}")
    lines.append(f"- plan_path: {pr_plan.get('plan_path') or 'none'}")
    lines.append(f"- active_relation: {pr_plan.get('active_relation') or 'none'}")

    work_item = trace["work_item"]
    lines.append("")
    lines.append("Work Item:")
    lines.append(f"- work_item_id: {work_item.get('work_item_id') or 'none'}")
    lines.append(f"- work_item_path: {work_item.get('work_item_path') or 'none'}")
    readiness_visibility = work_item.get("readiness_visibility")
    if isinstance(readiness_visibility, dict) and readiness_visibility:
        lines.append(f"- readiness_visibility: {readiness_visibility.get('summary') or 'none'}")
    else:
        lines.append("- readiness_visibility: none")

    goal = trace["goal"]
    lines.append("")
    lines.append("Goal:")
    lines.append(f"- goal_id: {goal.get('goal_id') or 'none'}")
    lines.append(f"- goal_path: {goal.get('goal_path') or 'none'}")

    clarifications = trace["clarifications"]
    lines.append("")
    lines.append("Clarifications:")
    clarification_ids = clarifications.get("linked_clarification_ids")
    if isinstance(clarification_ids, list) and clarification_ids:
        for clarification_id in clarification_ids:
            lines.append(f"- clarification_id: {clarification_id}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Degraded Notes:")
    degraded_notes = trace.get("degraded_notes")
    if isinstance(degraded_notes, list) and degraded_notes:
        for note in degraded_notes:
            lines.append(f"- {note}")
    else:
        lines.append("- none")

    return "\n".join(lines)


def _render_trace_run(trace: dict[str, object]) -> str:
    lines = ["Trace Run (debug-only)"]

    lines.append("")
    lines.append("Run info:")
    lines.append(f"- run_id: {trace.get('run_id') or 'none'}")
    lines.append(f"- run_path: {trace.get('run_path') or 'none'}")
    lines.append(f"- pr_id: {trace.get('pr_id') or 'none'}")
    lines.append(f"- work_item_id: {trace.get('work_item_id') or 'none'}")
    lines.append(f"- state: {trace.get('state') or 'none'}")

    lines.append("")
    lines.append("Artifacts:")
    artifacts = trace.get("artifacts")
    if not isinstance(artifacts, dict):
        artifacts = {}
    lines.append(f"- run.yaml: {artifacts.get('run.yaml') or 'missing'}")
    lines.append(f"- approval-request.yaml: {artifacts.get('approval-request.yaml') or 'missing'}")
    lines.append(f"- draft-approval: {artifacts.get('draft-approval') or 'missing'}")

    lines.append("")
    lines.append("Note:")
    lines.append("- trace-only")
    lines.append("- not a decision surface")
    return "\n".join(lines)


def _render_create_pr_plan_summary(
    path: Path,
    had_active_pr: bool,
    pr_id: str,
    readiness: dict[str, object],
) -> str:
    lines = ["PR Plan Created:"]
    lines.append(f"- pr_id: {pr_id}")
    lines.append(f"- location: {'archive' if had_active_pr else 'active'}")
    lines.append(f"- path: {path.as_posix()}")
    lines.append(f"- work_item_readiness: {readiness['overall_readiness_summary']}")
    lines.append(f"- linked_clarifications: {readiness['linked_clarification_count']}")
    if had_active_pr:
        lines.append("- reason: active PR already exists, so the new plan was created in archive")
    else:
        lines.append("- reason: no active PR existed, so the new plan became active")
    lines.append(_render_pr_plan_next_step(had_active_pr=had_active_pr, pr_id=pr_id))
    return "\n".join(lines)


def _render_draft_pr_plan_summary(path: Path, work_item_id: str) -> str:
    lines = ["PR Plan Draft Created:"]
    lines.append(f"- work_item_id: {work_item_id}")
    lines.append(f"- path: {path.as_posix()}")
    lines.append(
        f"- next: review the draft, then promote it with factory promote-pr-plan-draft --root . --work-item-id {work_item_id}"
    )
    return "\n".join(lines)


def _render_draft_approval_packet_summary(path: Path, run_id: str) -> str:
    lines = ["Approval Packet Draft Created:"]
    lines.append(f"- run_id: {run_id}")
    lines.append(f"- path: {path.as_posix()}")
    lines.append("- draft_status: draft-only")
    lines.append("- canonical: false")
    lines.append("- operator_assist_only: review the exact draft before updating canonical artifacts")
    lines.append("- next_step_manual_hint: manual follow-up only; no command was executed automatically")
    lines.append("- Next step (manual):")
    lines.append(f"  python -m factory build-approval --root . --run-id {run_id}")
    return "\n".join(lines)


def _render_draft_clarifications_summary(path: Path, goal_id: str) -> str:
    lines = ["Clarification Draft Created:"]
    lines.append(f"- goal_id: {goal_id}")
    lines.append(f"- path: {path.as_posix()}")
    lines.append(
        f"- next: review the draft, then promote one item with factory promote-clarification-draft --root . --goal-id {goal_id} --draft-index <n> --clarification-id <id>"
    )
    return "\n".join(lines)


def _render_promote_clarification_draft_summary(path: Path, goal_id: str, clarification_id: str) -> str:
    lines = ["Clarification Draft Promoted:"]
    lines.append(f"- goal_id: {goal_id}")
    lines.append(f"- clarification_id: {clarification_id}")
    lines.append(f"- path: {path.as_posix()}")
    lines.append(f"- next: factory draft-work-items --root . --goal-id {goal_id}")
    return "\n".join(lines)


def _render_draft_work_items_summary(path: Path, goal_id: str) -> str:
    lines = ["Work Item Draft Created:"]
    lines.append(f"- goal_id: {goal_id}")
    lines.append(f"- path: {path.as_posix()}")
    lines.append(
        f"- next: review the draft, then promote one candidate with factory promote-work-item-draft --root . --goal-id {goal_id} --draft-index <n> --work-item-id <id>"
    )
    return "\n".join(lines)


def _render_promote_work_item_draft_summary(path: Path, work_item_id: str) -> str:
    lines = ["Work Item Draft Promoted:"]
    lines.append(f"- work_item_id: {work_item_id}")
    lines.append(f"- path: {path.as_posix()}")
    lines.append(f"- next: factory draft-pr-plan --root . --work-item-id {work_item_id}")
    return "\n".join(lines)


def _render_promote_pr_plan_draft_summary(
    path: Path,
    had_active_pr: bool,
    pr_id: str,
    readiness: dict[str, object],
) -> str:
    lines = ["PR Plan Draft Promoted:"]
    lines.append(f"- pr_id: {pr_id}")
    lines.append(f"- location: {'archive' if had_active_pr else 'active'}")
    lines.append(f"- path: {path.as_posix()}")
    lines.append(f"- work_item_readiness: {readiness['overall_readiness_summary']}")
    lines.append(f"- linked_clarifications: {readiness['linked_clarification_count']}")
    if had_active_pr:
        lines.append("- reason: active PR already exists, so the promoted plan was created in archive")
    else:
        lines.append("- reason: no active PR existed, so the promoted plan became active")
    lines.append(_render_pr_plan_next_step(had_active_pr=had_active_pr, pr_id=pr_id))
    return "\n".join(lines)


def _render_pr_plan_next_step(*, had_active_pr: bool, pr_id: str) -> str:
    if had_active_pr:
        return f"- next: factory activate-pr --root . --pr-id {pr_id}"
    return "- next: factory start-execution --root ."


def _render_help_epilog(*lines: str) -> str:
    return "\n".join(lines)


def _render_activate_pr_summary(pr_id: str, active_path: Path, archived_paths: list[Path]) -> str:
    lines = ["Active PR Updated:"]
    lines.append(f"- active_pr_id: {pr_id}")
    lines.append(f"- active_path: {active_path.as_posix()}")
    if archived_paths:
        for archived_path in archived_paths:
            lines.append(f"- archived_previous_active: {archived_path.as_posix()}")
    else:
        lines.append("- archived_previous_active: none")
    lines.append("- next: factory start-execution --root .")
    return "\n".join(lines)


def _render_start_execution_summary(run_root: Path, run_id: str) -> str:
    lines = ["Execution Started:"]
    lines.append(f"- run_id: {run_id}")
    lines.append(f"- run_path: {run_root.as_posix()}")
    lines.append(f"- next: factory inspect-run --root . --run-id {run_id}")
    return "\n".join(lines)


def _render_record_review_summary(path: Path, run_id: str) -> str:
    lines = ["Review Recorded:"]
    lines.append(f"- run_id: {run_id}")
    lines.append(f"- review_report_path: {path.as_posix()}")
    lines.append(f"- next: factory inspect-run --root . --run-id {run_id}")
    return "\n".join(lines)


def _render_record_qa_summary(path: Path, run_id: str) -> str:
    lines = ["QA Recorded:"]
    lines.append(f"- run_id: {run_id}")
    lines.append(f"- qa_report_path: {path.as_posix()}")
    lines.append(f"- next: factory inspect-run --root . --run-id {run_id}")
    return "\n".join(lines)


def _render_record_docs_sync_summary(path: Path, run_id: str) -> str:
    lines = ["Docs Sync Recorded:"]
    lines.append(f"- run_id: {run_id}")
    lines.append(f"- docs_sync_report_path: {path.as_posix()}")
    lines.append(f"- next: factory inspect-run --root . --run-id {run_id}")
    return "\n".join(lines)


def _render_record_verification_summary(path: Path, run_id: str) -> str:
    lines = ["Verification Recorded:"]
    lines.append(f"- run_id: {run_id}")
    lines.append(f"- verification_report_path: {path.as_posix()}")
    lines.append(f"- next: factory inspect-run --root . --run-id {run_id}")
    return "\n".join(lines)


def _render_gate_check_summary(path: Path, run_id: str) -> str:
    lines = ["Gate Check Complete:"]
    lines.append(f"- run_id: {run_id}")
    lines.append(f"- gate_status_path: {path.as_posix()}")
    lines.append(f"- next: factory inspect-run --root . --run-id {run_id}")
    return "\n".join(lines)


def _render_start_execution_error(root_dir: Path, run_id: str) -> str:
    active_dir = root_dir / "prs" / "active"
    active_plans = sorted(active_dir.glob("*.md"))
    if not active_plans:
        return "\n".join(
            [
                "start-execution could not start because there is no active PR plan under prs/active/.",
                "Next action: create a PR plan, or activate the intended archived PR before starting execution.",
                f"Examples: factory create-pr-plan --root . --pr-id PR-XXX --work-item-id WI-XXX --title \"...\" --summary \"...\"; factory activate-pr --root . --pr-id PR-XXX; factory start-execution --root . --run-id {run_id}",
            ]
        )
    if len(active_plans) > 1:
        plan_list = ", ".join(path.as_posix() for path in active_plans)
        return "\n".join(
            [
                f"start-execution could not start because prs/active/ must contain exactly one active PR plan, but found {len(active_plans)}.",
                f"Current active candidates: {plan_list}",
                f"Next action: leave one active PR plan, usually by moving the intended PR through `factory activate-pr --root . --pr-id <id>`, then rerun `factory start-execution --root . --run-id {run_id}`.",
            ]
        )

    pr_plan_path = active_plans[0]
    work_item_id = "unknown"
    current_heading = None
    for raw_line in pr_plan_path.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("## "):
            current_heading = raw_line[3:].strip()
            continue
        if current_heading == "Work Item ID" and raw_line.strip():
            work_item_id = raw_line.strip()
            break
    work_item_dir = root_dir / "docs" / "work-items"
    expected_exact = work_item_dir / f"{work_item_id}.md"
    matches = sorted(work_item_dir.glob(f"{work_item_id}-*.md"))
    if not expected_exact.exists() and not matches:
        return "\n".join(
            [
                f"start-execution found active PR {pr_plan_path.as_posix()}, but its Work Item ID '{work_item_id}' does not resolve to a work item artifact under docs/work-items/.",
                "Next action: create or restore the matching work item artifact before starting execution.",
                f"Examples: docs/work-items/{work_item_id}.md or docs/work-items/{work_item_id}-<slug>.md; then rerun `factory start-execution --root . --run-id {run_id}`.",
            ]
        )
    return "start-execution could not start because the active PR linkage is invalid."


def _render_cleanup_summary(result: dict[str, object]) -> str:
    include_demo = bool(result["include_demo"])
    mode = str(result["mode"])
    targets = result["targets"]

    lines = ["Cleanup Rehearsal:"]
    lines.append(f"- mode: {mode}")
    lines.append(f"- scope: {'rehearsal+demo' if include_demo else 'rehearsal-only'}")
    lines.append(f"- matched: {result['matched_count']}")

    if isinstance(targets, list) and targets:
        lines.append("")
        lines.append("Targets:")
        for target in targets:
            if isinstance(target, dict):
                lines.append(f"- {target['path']}")
    else:
        lines.append("")
        lines.append("Targets:")
        lines.append("- none")

    return "\n".join(lines)


def _render_work_item_readiness(readiness: dict[str, object]) -> str:
    lines = ["Work Item Readiness:"]
    lines.append(f"- work_item_id: {readiness['work_item_id']}")
    lines.append(f"- goal_id: {readiness['goal_id']}")
    lines.append(f"- linked_clarification_count: {readiness['linked_clarification_count']}")
    lines.append("")
    lines.append("Clarifications:")

    clarifications = readiness["clarifications"]
    if isinstance(clarifications, list) and clarifications:
        for clarification in clarifications:
            if isinstance(clarification, dict):
                lines.append(f"- {clarification['clarification_id']}: {clarification['status']}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("Overall Readiness:")
    lines.append(f"- summary: {readiness['overall_readiness_summary']}")
    return "\n".join(lines)


def _render_build_approval_summary(
    run_id: str,
    approval_path: Path,
    queue_path: Path | None,
    readiness_context: dict[str, object],
) -> str:
    lines = ["Build Approval:"]
    lines.append(f"- run_id: {run_id}")
    lines.append(f"- approval_request: {approval_path.as_posix()}")
    lines.append(f"- queue_item: {queue_path.as_posix() if queue_path is not None else 'none'}")
    if readiness_context.get("status") == "available":
        lines.append(f"- readiness_summary: {readiness_context['readiness_summary']}")
        lines.append(f"- linked_clarifications: {readiness_context['linked_clarification_count']}")
    else:
        lines.append("- readiness: unavailable")
    lines.append(f"- next: factory inspect-approval --root . --run-id {run_id}")
    return "\n".join(lines)


def _render_hygiene_approval_queue_dry_run_preview(preview: dict[str, str]) -> str:
    lines = ["Hygiene Approval Queue Dry Run Preview:"]
    lines.append("- stage: dry-run")
    lines.append("- dry_run: true")
    lines.append("- apply: false")
    lines.append(f"- selector_family: {preview['selector_family']}")
    lines.append(f"- run_id: {preview['run_id']}")
    lines.append(f"- approval_id: {preview['approval_id']}")
    lines.append(f"- queue_item: {preview['queue_item_path']}")
    lines.append("- mutation: none")
    lines.append("- cleanup: not implemented")
    lines.append("- auto_resolve: not implemented")
    lines.append("- selector_scope: exact target only")
    lines.append("- visibility_note: stale/latest and Relation Summary remain read-only operator visibility, not hygiene selectors")
    lines.append("- next: review this exact target-local preview first, then rerun the same selector with --apply if mutation is still intended")
    return "\n".join(lines)


def _render_hygiene_approval_queue_apply_summary(applied: dict[str, str]) -> str:
    lines = ["Hygiene Approval Queue Apply:"]
    lines.append("- stage: apply")
    lines.append("- dry_run: false")
    lines.append("- apply: true")
    lines.append(f"- selector_family: {applied['selector_family']}")
    lines.append(f"- run_id: {applied['run_id']}")
    lines.append(f"- approval_id: {applied['approval_id']}")
    lines.append(f"- queue_item: {applied['queue_item_path']}")
    lines.append("- mutation: queue_hygiene metadata updated on the exact target queue artifact only")
    lines.append("- cleanup: not implemented")
    lines.append("- auto_resolve: not implemented")
    lines.append("- selector_scope: exact target only")
    lines.append("- visibility_note: stale/latest and Relation Summary remain read-only operator visibility, not hygiene selectors")
    lines.append("- next: verify the exact target artifact change; no non-target queue artifacts were touched")
    return "\n".join(lines)


def _add_run_selector_arguments(parser: argparse.ArgumentParser) -> None:
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--run-id")
    selector.add_argument(
        "--latest",
        action="store_true",
        help="Use the latest run selected from runs/latest/*/run.yaml",
    )


def _add_trace_lineage_selector_arguments(parser: argparse.ArgumentParser) -> None:
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--run-id")
    selector.add_argument(
        "--latest-run",
        action="store_true",
        help="Use the latest run selected from runs/latest/*/run.yaml",
    )


def _resolve_run_id_argument(parser: argparse.ArgumentParser, args: argparse.Namespace) -> str:
    if getattr(args, "run_id", None):
        return str(args.run_id)
    if getattr(args, "latest", False):
        try:
            return resolve_latest_run_id(root_dir=Path(args.root))
        except ValueError as exc:
            parser.error(str(exc))
    parser.error(f"{args.command} requires either --run-id <id> or --latest")
    return ""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="factory")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser(
        "status",
        help="Show current repo-local system status",
        description="Show current repo-local system status for operator visibility continuity.",
        epilog=_render_help_epilog(
            "Next step:",
            "  choose a read-only follow-up such as factory inspect-approval-queue --root . or factory inspect-pr-plan --root . --active",
            "",
            "Example:",
            "  factory status --root .",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    status_parser.add_argument("--root", default=".", help="Repository root path")

    inspect_approval_queue_parser = subparsers.add_parser(
        "inspect-approval-queue",
        help="Inspect pending approval queue entries without changing approval semantics",
        description="Inspect pending approval queue entries in visibility-only mode.",
        epilog=_render_help_epilog(
            "Next step:",
            "  continue read-only approval visibility with factory inspect-approval --root . --run-id <run-id>",
            "",
            "Example:",
            "  factory inspect-approval-queue --root .",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    inspect_approval_queue_parser.add_argument("--root", default=".", help="Repository root path")

    suggest_next_pr_parser = subparsers.add_parser(
        "suggest-next-pr",
        help="Suggest one assist-only next PR candidate from current repo state without mutation",
        description="Suggest one assist-only next PR candidate from current repo state in read-only mode.",
        epilog=_render_help_epilog(
            "Next step:",
            "  review the short state block and minimum execution packet as operator assist only; if an active PR already exists, this command stops instead of suggesting another PR",
            "",
            "Example:",
            "  factory suggest-next-pr --root .",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    suggest_next_pr_parser.add_argument("--root", default=".", help="Repository root path")

    hygiene_approval_queue_parser = subparsers.add_parser(
        "hygiene-approval-queue",
        help="Preview or apply exact-target approval queue hygiene without cleanup semantics",
        description=(
            "Stage 3 exact-target approval queue hygiene with dry-run-first preview and explicit apply. "
            "Use exactly one selector family (--run-id or --approval-id) and exactly one mode family "
            "(--dry-run or --apply)."
        ),
        epilog=_render_help_epilog(
            "Next step:",
            "  run --dry-run first with exactly one explicit selector, review the exact pending queue target, then rerun the same selector with --apply only if the target-local mutation is still intended",
            "  stale/latest visibility from factory status or factory inspect-approval-queue is read-only operator guidance, not a hygiene selector or cleanup signal",
            "  hygiene mutates only the exact pending queue target artifact; it does not add cleanup or auto-resolve semantics",
            "",
            "Example:",
            "  factory hygiene-approval-queue --root . --run-id RUN-20260327T055614Z --dry-run",
            "  factory hygiene-approval-queue --root . --approval-id APR-RUN-20260327T055614Z --dry-run",
            "  factory hygiene-approval-queue --root . --run-id RUN-20260327T055614Z --apply",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    hygiene_approval_queue_parser.add_argument("--root", default=".", help="Repository root path")
    hygiene_selector = hygiene_approval_queue_parser.add_mutually_exclusive_group(required=True)
    hygiene_selector.add_argument("--run-id", help="Exact run selector in the form RUN-...; heuristic selectors such as stale/latest are refused")
    hygiene_selector.add_argument("--approval-id", help="Exact approval selector in the form APR-RUN-...; heuristic selectors such as stale/latest are refused")
    hygiene_mode = hygiene_approval_queue_parser.add_mutually_exclusive_group(required=True)
    hygiene_mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the exact pending queue target without changing queue artifacts; run this first",
    )
    hygiene_mode.add_argument(
        "--apply",
        action="store_true",
        help="After dry-run review, mutate only the exact pending queue target artifact; no cleanup or auto-resolve semantics",
    )

    inspect_approval_parser = subparsers.add_parser(
        "inspect-approval",
        help="Inspect approval package artifacts in visibility-only mode",
        description="Inspect approval package artifacts in visibility-only mode.",
        epilog=_render_help_epilog(
            "Next step:",
            "  factory resolve-approval --root . --run-id <run-id> --decision approve --actor <actor> --note \"all gates satisfied\"",
            "",
            "Example:",
            "  factory inspect-approval --root . --run-id RUN-056",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    inspect_approval_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(inspect_approval_parser)

    inspect_draft_approval_parser = subparsers.add_parser(
        "inspect-draft-approval",
        help="Inspect one exact draft approval artifact against canonical run artifacts in assist-only mode",
        description="Inspect one exact draft approval artifact against canonical run artifacts in assist-only mode.",
        epilog=_render_help_epilog(
            "Next step:",
            "  review the exact differences as operator assist only; this command does not make approval decisions or mutate canonical artifacts",
            "",
            "Example:",
            "  factory inspect-draft-approval --root . --run-id RUN-20260327T063724Z",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    inspect_draft_approval_parser.add_argument("--root", default=".", help="Repository root path")
    inspect_draft_approval_parser.add_argument(
        "--run-id",
        required=True,
        help="Exact run selector in the form RUN-...; no latest fallback or implicit selection",
    )

    review_approval_parser = subparsers.add_parser(
        "review-approval",
        help="Review one exact approval draft via the existing inspection output plus a manual next-step hint",
        description="Review one exact approval draft via the existing inspection output plus a manual next-step hint.",
        epilog=_render_help_epilog(
            "Next step:",
            "  this wrapper is assist only; inspect output is preserved and no approval decision or build command is executed",
            "  python -m factory build-approval --root . --run-id <run-id>",
            "",
            "Example:",
            "  factory review-approval --root . --run-id RUN-20260327T063724Z",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    review_approval_parser.add_argument("--root", default=".", help="Repository root path")
    review_approval_parser.add_argument(
        "--run-id",
        required=True,
        help="Exact run selector in the form RUN-...; no latest fallback or implicit selection",
    )

    inspect_run_parser = subparsers.add_parser(
        "inspect-run",
        help="Inspect run-scoped execution artifacts in visibility-only mode",
        description="Inspect run-scoped execution artifacts in visibility-only mode.",
        epilog=_render_help_epilog(
            "Next step:",
            '  factory record-review --root . --run-id <run-id> --status pass --summary "review ok"',
            "",
            "Example:",
            "  factory inspect-run --root . --run-id RUN-055",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    inspect_run_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(inspect_run_parser)

    trace_run_parser = subparsers.add_parser(
        "trace-run",
        help="Trace one exact run in debug-only mode",
        description="Trace one exact run in debug-only mode.",
        epilog=_render_help_epilog(
            "Debug-only:",
            "  this command reads one exact run and optional artifacts without decision or approval-flow behavior",
            "",
            "Example:",
            "  factory trace-run --root . --run-id RUN-20260327T063724Z",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    trace_run_parser.add_argument("--root", default=".", help="Repository root path")
    trace_run_parser.add_argument(
        "--run-id",
        required=True,
        help="Exact run selector in the form RUN-...; no latest fallback or implicit selection",
    )

    inspect_pr_plan_parser = subparsers.add_parser(
        "inspect-pr-plan",
        help="Inspect PR plan artifacts in visibility-only mode",
        description="Inspect PR plan artifacts in visibility-only mode.",
        epilog=_render_help_epilog(
            "Next step:",
            "  check whether the plan is active or archived, then choose the next operator command explicitly",
            "",
            "Example:",
            "  factory inspect-pr-plan --root . --active",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    inspect_pr_plan_parser.add_argument("--root", default=".", help="Repository root path")
    pr_plan_selector = inspect_pr_plan_parser.add_mutually_exclusive_group(required=True)
    pr_plan_selector.add_argument(
        "--active",
        action="store_true",
        help="Inspect the single active PR plan using existing active PR semantics",
    )
    pr_plan_selector.add_argument("--pr-id", help="Inspect a PR plan by PR ID from active or archive")

    inspect_work_item_parser = subparsers.add_parser(
        "inspect-work-item",
        help="Inspect work item artifacts in visibility-only mode",
        description="Inspect work item artifacts in visibility-only mode.",
        epilog=_render_help_epilog(
            "Next step:",
            '  continue visibility with factory work-item-readiness --root . --work-item-id <work-item-id> or prepare a plan with factory create-pr-plan --root . --pr-id <pr-id> --work-item-id <work-item-id> --title "..." --summary "..."',
            "",
            "Example:",
            "  factory inspect-work-item --root . --work-item-id WI-063",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    inspect_work_item_parser.add_argument("--root", default=".", help="Repository root path")
    inspect_work_item_parser.add_argument("--work-item-id", required=True)

    inspect_orchestration_parser = subparsers.add_parser(
        "inspect-orchestration",
        help="Inspect exact --work-item-id <WI-...> orchestration visibility only",
        description=(
            "Inspect the exact --work-item-id <WI-...> anchor and linked official artifacts in "
            "read-only operator visibility-only mode."
        ),
        epilog=_render_help_epilog(
            "Next step:",
            "  continue with exact-anchor visibility only; official artifact summary remains read-only only, and a possible next manual step appears only when official artifacts show a single obvious path",
            "",
            "Example:",
            "  factory inspect-orchestration --root . --work-item-id WI-090",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    inspect_orchestration_parser.add_argument("--root", default=".", help="Repository root path")
    inspect_orchestration_parser.add_argument("--work-item-id", required=True)

    inspect_clarification_parser = subparsers.add_parser(
        "inspect-clarification",
        help="Inspect clarification artifacts in visibility-only mode",
        description="Inspect clarification artifacts in visibility-only mode.",
        epilog=_render_help_epilog(
            "Next step:",
            '  resolve it with factory resolve-clarification --root . --goal-id <goal-id> --clarification-id <clarification-id> --resolution "..." or continue planning with factory draft-work-items --root . --goal-id <goal-id>',
            "",
            "Example:",
            "  factory inspect-clarification --root . --clarification-id CLAR-063",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    inspect_clarification_parser.add_argument("--root", default=".", help="Repository root path")
    inspect_clarification_parser.add_argument("--clarification-id", required=True)

    inspect_goal_parser = subparsers.add_parser(
        "inspect-goal",
        help="Inspect goal artifacts in visibility-only mode",
        description="Inspect goal artifacts in visibility-only mode.",
        epilog=_render_help_epilog(
            "Next step:",
            '  continue visibility with factory draft-clarifications --root . --goal-id <goal-id> or add one with factory create-clarification --root . --goal-id <goal-id> --clarification-id <clarification-id> --question "..."',
            "",
            "Example:",
            "  factory inspect-goal --root . --goal-id GOAL-063",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    inspect_goal_parser.add_argument("--root", default=".", help="Repository root path")
    inspect_goal_parser.add_argument("--goal-id", required=True)

    trace_lineage_parser = subparsers.add_parser(
        "trace-lineage",
        help="Trace run-linked repo-local artifacts in visibility-only mode",
        description="Trace run-linked repo-local artifacts in visibility-only mode.",
        epilog=_render_help_epilog(
            "Next step:",
            "  continue read-only follow-up with factory inspect-run --root . --run-id <run-id> or factory inspect-approval --root . --run-id <run-id>",
            "",
            "Example:",
            "  factory trace-lineage --root . --run-id RUN-063",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    trace_lineage_parser.add_argument("--root", default=".", help="Repository root path")
    _add_trace_lineage_selector_arguments(trace_lineage_parser)

    bootstrap_parser = subparsers.add_parser(
        "bootstrap-run",
        help="Create baseline run artifacts",
        description="Create baseline run artifacts for an operator-managed flow.",
        epilog=_render_help_epilog(
            "Next step:",
            "  inspect the run state with factory status --root . or factory inspect-run --root . --run-id <run-id>",
            "",
            "Example:",
            "  factory bootstrap-run --root . --run-id RUN-064 --work-item-id WI-064 --work-item-title \"operator assist help\" --pr-id PR-064",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    bootstrap_parser.add_argument("--root", default=".", help="Repository root path")
    bootstrap_parser.add_argument("--run-id", default=_default_run_id())
    bootstrap_parser.add_argument("--work-item-id", default="WI-000")
    bootstrap_parser.add_argument("--work-item-title", default="bootstrap-run")
    bootstrap_parser.add_argument("--pr-id", default="PR-000")

    record_review_parser = subparsers.add_parser(
        "record-review",
        help="Record review result",
        description="Record review result.",
        epilog=_render_help_epilog(
            "Next step:",
            "  factory record-qa --root . --run-id <run-id> --status pass --summary \"qa ok\"",
            "",
            "Example:",
            "  factory record-review --root . --run-id RUN-056 --status pass --summary \"review ok\"",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    record_review_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(record_review_parser)
    record_review_parser.add_argument("--status", choices=["pass", "fail"], required=True)
    record_review_parser.add_argument("--summary", required=True)

    record_verification_parser = subparsers.add_parser(
        "record-verification",
        help="Record verification checks result",
        description="Record verification checks result.",
        epilog=_render_help_epilog(
            "Next step:",
            "  factory gate-check --root . --run-id <run-id>",
            "",
            "Example:",
            "  factory record-verification --root . --run-id RUN-056 --lint pass --tests pass --type-check pass --build pass --summary \"verification ok\"",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    record_verification_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(record_verification_parser)
    record_verification_parser.add_argument("--lint", choices=["pass", "fail", "pending"], required=True)
    record_verification_parser.add_argument("--tests", choices=["pass", "fail", "pending"], required=True)
    record_verification_parser.add_argument("--type-check", choices=["pass", "fail", "pending"], required=True)
    record_verification_parser.add_argument("--build", choices=["pass", "fail", "pending"], required=True)
    record_verification_parser.add_argument("--summary", required=True)

    record_qa_parser = subparsers.add_parser(
        "record-qa",
        help="Record QA result",
        description="Record QA result.",
        epilog=_render_help_epilog(
            "Next step:",
            "  factory record-docs-sync --root . --run-id <run-id> --status complete --summary \"docs synced\"",
            "",
            "Example:",
            "  factory record-qa --root . --run-id RUN-056 --status pass --summary \"qa ok\"",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    record_qa_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(record_qa_parser)
    record_qa_parser.add_argument("--status", choices=["pass", "fail"], required=True)
    record_qa_parser.add_argument("--summary", required=True)

    record_docs_sync_parser = subparsers.add_parser(
        "record-docs-sync",
        help="Record docs sync result",
        description="Record docs sync result.",
        epilog=_render_help_epilog(
            "Next step:",
            "  factory record-verification --root . --run-id <run-id> --lint pass --tests pass --type-check pass --build pass --summary \"verification ok\"",
            "",
            "Example:",
            "  factory record-docs-sync --root . --run-id RUN-056 --status complete --summary \"docs synced\"",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    record_docs_sync_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(record_docs_sync_parser)
    record_docs_sync_parser.add_argument("--status", choices=["complete", "required", "not-needed"], required=True)
    record_docs_sync_parser.add_argument("--summary", required=True)

    gate_check_parser = subparsers.add_parser(
        "gate-check",
        help="Evaluate gate status",
        description="Evaluate gate status.",
        epilog=_render_help_epilog(
            "Next step:",
            "  factory build-approval --root . --run-id <run-id>",
            "",
            "Example:",
            "  factory gate-check --root . --run-id RUN-056",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    gate_check_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(gate_check_parser)

    build_approval_parser = subparsers.add_parser(
        "build-approval",
        help="Build evidence and approval request",
        description="Build evidence and approval request.",
        epilog=_render_help_epilog(
            "Next step:",
            "  factory resolve-approval --root . --run-id <run-id> --decision approve --actor <actor> --note \"all gates satisfied\"",
            "",
            "Example:",
            "  factory build-approval --root . --run-id RUN-056",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    build_approval_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(build_approval_parser)

    draft_approval_packet_parser = subparsers.add_parser(
        "draft-approval-packet",
        help="Create a non-canonical approval packet draft for one exact run without queue mutation",
        description="Create a non-canonical approval packet draft for one exact run without queue mutation.",
        epilog=_render_help_epilog(
            "Next step:",
            "  review the exact draft file, then run factory build-approval --root . --run-id <run-id> only if canonical approval artifacts are still needed",
            "",
            "Example:",
            "  factory draft-approval-packet --root . --run-id RUN-20260327T063724Z",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    draft_approval_packet_parser.add_argument("--root", default=".", help="Repository root path")
    draft_approval_packet_parser.add_argument("--run-id", required=True, help="Exact run selector in the form RUN-...")

    create_goal_parser = subparsers.add_parser(
        "create-goal",
        help="Create a goal intake artifact",
        description="Create a goal intake artifact for operator-managed manual/create intake.",
        epilog=_render_help_epilog(
            "Next step:",
            "  add an operator-selected follow-up with factory create-clarification --root . --goal-id <goal-id> --clarification-id <clarification-id> --title \"...\" --category scope --question \"...\" or review possible prompts with factory draft-clarifications --root . --goal-id <goal-id>",
            "",
            "Example:",
            '  factory create-goal --root . --goal-id GOAL-064 --title "manual help discoverability" --problem "operators need clearer manual/create command help" --outcome "operators can choose the next command explicitly"',
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    create_goal_parser.add_argument("--root", default=".", help="Repository root path")
    create_goal_parser.add_argument("--goal-id", required=True)
    create_goal_parser.add_argument("--title", required=True)
    create_goal_parser.add_argument("--problem", required=True)
    create_goal_parser.add_argument("--outcome", required=True)
    create_goal_parser.add_argument("--constraints")

    draft_clarifications_parser = subparsers.add_parser(
        "draft-clarifications",
        help="Create a deterministic clarification draft artifact without queue mutation",
        description="Create a deterministic clarification draft artifact without queue mutation.",
        epilog=_render_help_epilog(
            "Next step:",
            "  review the draft, then promote one item with factory promote-clarification-draft --root . --goal-id <goal-id> --draft-index <n> --clarification-id <id>",
            "",
            "Example:",
            "  factory draft-clarifications --root . --goal-id GOAL-034",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    draft_clarifications_parser.add_argument("--root", default=".", help="Repository root path")
    draft_clarifications_parser.add_argument("--goal-id", required=True)

    draft_work_items_parser = subparsers.add_parser(
        "draft-work-items",
        help="Draft work item candidates from official clarification artifacts",
        description="Draft work item candidates from official clarification artifacts.",
        epilog=_render_help_epilog(
            "Next step:",
            "  review the draft, then promote one candidate with factory promote-work-item-draft --root . --goal-id <goal-id> --draft-index <n> --work-item-id <id>",
            "",
            "Example:",
            "  factory draft-work-items --root . --goal-id GOAL-036",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    draft_work_items_parser.add_argument("--root", default=".", help="Repository root path")
    draft_work_items_parser.add_argument("--goal-id", required=True)

    draft_pr_plan_parser = subparsers.add_parser(
        "draft-pr-plan",
        help="Draft a PR plan artifact from an official work item without PR lifecycle mutation",
        description="Draft a PR plan artifact from an official work item without PR lifecycle mutation.",
        epilog=_render_help_epilog(
            "Next step:",
            "  review the draft, then promote it with factory promote-pr-plan-draft --root . --work-item-id <work-item-id>",
            "",
            "Example:",
            "  factory draft-pr-plan --root . --work-item-id WI-038",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    draft_pr_plan_parser.add_argument("--root", default=".", help="Repository root path")
    draft_pr_plan_parser.add_argument("--work-item-id", required=True)

    promote_clarification_draft_parser = subparsers.add_parser(
        "promote-clarification-draft",
        help="Promote one draft item into an official clarification artifact",
        description="Promote one draft item into an official clarification artifact.",
        epilog=_render_help_epilog(
            "Next step:",
            "  factory draft-work-items --root . --goal-id <goal-id>",
            "",
            "Example:",
            "  factory promote-clarification-draft --root . --goal-id GOAL-034 --draft-index 1 --clarification-id CLAR-001",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    promote_clarification_draft_parser.add_argument("--root", default=".", help="Repository root path")
    promote_clarification_draft_parser.add_argument("--goal-id", required=True)
    promote_clarification_draft_parser.add_argument("--draft-index", type=int, required=True)
    promote_clarification_draft_parser.add_argument("--clarification-id", required=True)

    promote_work_item_draft_parser = subparsers.add_parser(
        "promote-work-item-draft",
        help="Promote one work item draft candidate into an official work item artifact",
        description="Promote one work item draft candidate into an official work item artifact.",
        epilog=_render_help_epilog(
            "Next step:",
            "  factory draft-pr-plan --root . --work-item-id <work-item-id>",
            "",
            "Example:",
            "  factory promote-work-item-draft --root . --goal-id GOAL-036 --draft-index 1 --work-item-id WI-036",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    promote_work_item_draft_parser.add_argument("--root", default=".", help="Repository root path")
    promote_work_item_draft_parser.add_argument("--goal-id", required=True)
    promote_work_item_draft_parser.add_argument("--draft-index", type=int, required=True)
    promote_work_item_draft_parser.add_argument("--work-item-id", required=True)

    promote_pr_plan_draft_parser = subparsers.add_parser(
        "promote-pr-plan-draft",
        help="Promote one PR plan draft into an official PR plan artifact",
        description="Promote one PR plan draft into an official PR plan artifact.",
        epilog=_render_help_epilog(
            "Next step:",
            "  if no active PR exists, factory start-execution --root .",
            "  if an active PR already exists, factory activate-pr --root . --pr-id <pr-id>",
            "",
            "Example:",
            "  factory promote-pr-plan-draft --root . --work-item-id WI-039",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    promote_pr_plan_draft_parser.add_argument("--root", default=".", help="Repository root path")
    promote_pr_plan_draft_parser.add_argument("--work-item-id", required=True)

    create_clarification_parser = subparsers.add_parser(
        "create-clarification",
        help="Create a clarification artifact for a goal",
        description="Create a clarification artifact for a goal in an operator-managed manual/create flow.",
        epilog=_render_help_epilog(
            "Next step:",
            "  record the chosen outcome with factory resolve-clarification --root . --goal-id <goal-id> --clarification-id <clarification-id> --decision resolved --resolution-notes \"...\" --next-action \"...\" or review candidate work with factory draft-work-items --root . --goal-id <goal-id>",
            "",
            "Example:",
            '  factory create-clarification --root . --goal-id GOAL-064 --clarification-id CLAR-064 --title "manual next step wording" --category ux --question "Which operator hint should follow create-goal?"',
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    create_clarification_parser.add_argument("--root", default=".", help="Repository root path")
    create_clarification_parser.add_argument("--goal-id", required=True)
    create_clarification_parser.add_argument("--clarification-id", required=True)
    create_clarification_parser.add_argument("--title", required=True)
    create_clarification_parser.add_argument("--category", required=True)
    create_clarification_parser.add_argument("--question", required=True)
    create_clarification_parser.add_argument("--escalation", action="store_true")

    resolve_clarification_parser = subparsers.add_parser(
        "resolve-clarification",
        help="Resolve an open clarification artifact for a goal",
        description="Resolve an open clarification artifact for a goal within an operator-managed manual/create flow.",
        epilog=_render_help_epilog(
            "Next step:",
            "  prepare the next operator-selected planning step with factory draft-work-items --root . --goal-id <goal-id> or create an official item with factory create-work-item --root . --work-item-id <work-item-id> --title \"...\" --goal-id <goal-id> --description \"...\"",
            "",
            "Example:",
            '  factory resolve-clarification --root . --goal-id GOAL-064 --clarification-id CLAR-064 --decision resolved --resolution-notes "Use operator hints only." --next-action "Create a work item once wording is confirmed"',
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    resolve_clarification_parser.add_argument("--root", default=".", help="Repository root path")
    resolve_clarification_parser.add_argument("--goal-id", required=True)
    resolve_clarification_parser.add_argument("--clarification-id", required=True)
    resolve_clarification_parser.add_argument("--decision", choices=["resolved", "deferred", "escalated"], required=True)
    resolve_clarification_parser.add_argument("--resolution-notes", required=True)
    resolve_clarification_parser.add_argument("--next-action", required=True)
    resolve_clarification_parser.add_argument("--suggested-resolution")

    create_work_item_parser = subparsers.add_parser(
        "create-work-item",
        help="Create a work item artifact",
        description="Create a work item artifact from approved manual/create inputs.",
        epilog=_render_help_epilog(
            "Next step:",
            "  inspect clarification visibility with factory work-item-readiness --root . --work-item-id <work-item-id> or prepare a plan with factory create-pr-plan --root . --pr-id <pr-id> --work-item-id <work-item-id> --title \"...\" --summary \"...\"",
            "",
            "Example:",
            '  factory create-work-item --root . --work-item-id WI-064 --title "manual command help discoverability" --goal-id GOAL-064 --description "Add descriptions, next steps, and examples for manual/create commands"',
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    create_work_item_parser.add_argument("--root", default=".", help="Repository root path")
    create_work_item_parser.add_argument("--work-item-id", required=True)
    create_work_item_parser.add_argument("--title", required=True)
    create_work_item_parser.add_argument("--goal-id", required=True)
    create_work_item_parser.add_argument("--description", required=True)
    create_work_item_parser.add_argument("--acceptance-criteria")
    create_work_item_parser.add_argument(
        "--clarification-id",
        action="append",
        dest="clarification_ids",
        help="Link one or more clarification artifacts under the same goal",
    )

    work_item_readiness_parser = subparsers.add_parser(
        "work-item-readiness",
        help="Show read-only clarification readiness visibility for a work item",
        description="Show read-only clarification readiness visibility for a work item.",
        epilog=_render_help_epilog(
            "Next step:",
            "  use this visibility to decide the next operator action, such as factory create-pr-plan --root . --pr-id <pr-id> --work-item-id <work-item-id> --title \"...\" --summary \"...\" or factory inspect-work-item --root . --work-item-id <work-item-id>",
            "",
            "Example:",
            "  factory work-item-readiness --root . --work-item-id WI-064",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    work_item_readiness_parser.add_argument("--root", default=".", help="Repository root path")
    work_item_readiness_parser.add_argument("--work-item-id", required=True)

    create_pr_plan_parser = subparsers.add_parser(
        "create-pr-plan",
        help="Create an official PR plan artifact from a work item",
        description="Create an official PR plan artifact from a work item.",
        epilog=_render_help_epilog(
            "Next step:",
            "  if no active PR exists, factory start-execution --root .",
            "  if an active PR already exists, factory activate-pr --root . --pr-id <pr-id>",
            "",
            "Example:",
            '  factory create-pr-plan --root . --pr-id PR-055 --work-item-id WI-055 --title "official PR help discoverability" --summary "Add minimum help next steps for official PR flow"',
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    create_pr_plan_parser.add_argument("--root", default=".", help="Repository root path")
    create_pr_plan_parser.add_argument("--pr-id", required=True)
    create_pr_plan_parser.add_argument("--work-item-id", required=True)
    create_pr_plan_parser.add_argument("--title", required=True)
    create_pr_plan_parser.add_argument("--summary", required=True)

    activate_pr_parser = subparsers.add_parser(
        "activate-pr",
        help="Switch the single active PR plan",
        description="Switch the single active PR plan.",
        epilog=_render_help_epilog(
            "Next step:",
            "  factory start-execution --root .",
            "",
            "Example:",
            "  factory activate-pr --root . --pr-id PR-055",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    activate_pr_parser.add_argument("--root", default=".", help="Repository root path")
    activate_pr_parser.add_argument("--pr-id", required=True)

    start_execution_parser = subparsers.add_parser(
        "start-execution",
        help="Start a run from the single active PR plan",
        description="Start a run from the single active PR plan.",
        epilog=_render_help_epilog(
            "Next step:",
            "  factory inspect-run --root . --run-id <run-id>",
            "",
            "Example:",
            "  factory start-execution --root . --run-id RUN-055",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    start_execution_parser.add_argument("--root", default=".", help="Repository root path")
    start_execution_parser.add_argument("--run-id", default=_default_run_id())

    resolve_approval_parser = subparsers.add_parser(
        "resolve-approval",
        help="Resolve pending approval request",
        description="Resolve pending approval request.",
        epilog=_render_help_epilog(
            "Next step:",
            "  factory inspect-approval --root . --run-id <run-id>",
            "",
            "Example:",
            "  factory resolve-approval --root . --run-id RUN-056 --decision approve --actor approver.local --note \"all gates satisfied\"",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    resolve_approval_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(resolve_approval_parser)
    resolve_approval_parser.add_argument("--decision", choices=["approve", "reject", "exception"], required=True)
    resolve_approval_parser.add_argument("--actor", required=True)
    resolve_approval_parser.add_argument("--note", required=True)

    cleanup_parser = subparsers.add_parser(
        "cleanup-rehearsal",
        help="List or remove rehearsal artifacts from repo-local operating paths",
        description="List or remove rehearsal artifacts from repo-local operating paths in an operator-managed flow.",
        epilog=_render_help_epilog(
            "Next step:",
            "  inspect the resulting repo-local state with factory status --root . or factory inspect-run --root . --run-id <run-id>",
            "",
            "Example:",
            "  factory cleanup-rehearsal --root .",
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    cleanup_parser.add_argument("--root", default=".", help="Repository root path")
    cleanup_parser.add_argument("--apply", action="store_true", help="Actually delete matched artifacts")
    cleanup_parser.add_argument(
        "--include-demo",
        action="store_true",
        help="Include legacy DEMO artifacts in addition to rehearsal artifacts",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "status":
        print(_render_status(get_factory_status(root_dir=Path(args.root))))
        return 0

    if args.command == "inspect-approval-queue":
        print(_render_approval_queue_inspection(inspect_approval_queue(root_dir=Path(args.root))))
        return 0

    if args.command == "suggest-next-pr":
        print(_render_suggest_next_pr(suggest_next_pr(root_dir=Path(args.root))))
        return 0

    if args.command == "hygiene-approval-queue":
        try:
            selection = parse_hygiene_approval_queue_selector(
                run_id=getattr(args, "run_id", None),
                approval_id=getattr(args, "approval_id", None),
            )
            if getattr(args, "dry_run", False):
                preview = resolve_hygiene_approval_queue_dry_run_target(
                    root_dir=Path(args.root),
                    selection=selection,
                )
            else:
                preview = apply_hygiene_approval_queue_target(
                    root_dir=Path(args.root),
                    selection=selection,
                )
        except ValueError as exc:
            parser.error(str(exc))
        if getattr(args, "dry_run", False):
            print(_render_hygiene_approval_queue_dry_run_preview(preview))
        else:
            print(_render_hygiene_approval_queue_apply_summary(preview))
        return 0

    if args.command == "inspect-approval":
        run_id = str(args.run_id) if getattr(args, "run_id", None) else None
        if getattr(args, "latest", False):
            try:
                run_id = resolve_latest_run_id(root_dir=Path(args.root))
            except ValueError:
                run_id = None
        elif run_id is None:
            parser.error("inspect-approval requires either --run-id <id> or --latest")
        print(_render_approval_inspection(inspect_approval(root_dir=Path(args.root), run_id=run_id)))
        return 0

    if args.command == "inspect-draft-approval":
        try:
            inspection = inspect_draft_approval(root_dir=Path(args.root), run_id=str(args.run_id))
        except (FileNotFoundError, ValueError) as exc:
            parser.error(str(exc))
        print(_render_draft_approval_inspection(inspection))
        return 0

    if args.command == "review-approval":
        try:
            inspection = inspect_draft_approval(root_dir=Path(args.root), run_id=str(args.run_id))
        except (FileNotFoundError, ValueError) as exc:
            parser.error(str(exc))
        print(_render_review_approval_summary(inspection, str(args.run_id)))
        return 0

    if args.command == "inspect-run":
        run_id = str(args.run_id) if getattr(args, "run_id", None) else None
        if getattr(args, "latest", False):
            try:
                run_id = resolve_latest_run_id(root_dir=Path(args.root))
            except ValueError:
                run_id = None
        elif run_id is None:
            parser.error("inspect-run requires either --run-id <id> or --latest")
        print(_render_run_inspection(inspect_run(root_dir=Path(args.root), run_id=run_id)))
        return 0

    if args.command == "trace-run":
        try:
            print(_render_trace_run(trace_run(root_dir=Path(args.root), run_id=str(args.run_id))))
        except (FileNotFoundError, ValueError) as exc:
            parser.error(str(exc))
        return 0

    if args.command == "inspect-pr-plan":
        print(
            _render_pr_plan_inspection(
                inspect_pr_plan(
                    root_dir=Path(args.root),
                    pr_id=str(args.pr_id) if getattr(args, "pr_id", None) else None,
                    active=bool(getattr(args, "active", False)),
                )
            )
        )
        return 0

    if args.command == "inspect-work-item":
        print(
            _render_work_item_inspection(
                inspect_work_item(
                    root_dir=Path(args.root),
                    work_item_id=args.work_item_id,
                )
            )
        )
        return 0

    if args.command == "inspect-orchestration":
        print(
            _render_orchestration_inspection(
                inspect_orchestration(
                    root_dir=Path(args.root),
                    work_item_id=args.work_item_id,
                )
            )
        )
        return 0

    if args.command == "inspect-clarification":
        print(
            _render_clarification_inspection(
                inspect_clarification(
                    root_dir=Path(args.root),
                    clarification_id=args.clarification_id,
                )
            )
        )
        return 0

    if args.command == "inspect-goal":
        print(
            _render_goal_inspection(
                inspect_goal(
                    root_dir=Path(args.root),
                    goal_id=args.goal_id,
                )
            )
        )
        return 0

    if args.command == "trace-lineage":
        run_id = str(args.run_id) if getattr(args, "run_id", None) else None
        if getattr(args, "latest_run", False):
            try:
                run_id = resolve_latest_run_id(root_dir=Path(args.root))
            except ValueError:
                run_id = None
        elif run_id is None:
            parser.error("trace-lineage requires either --run-id <id> or --latest-run")
        print(_render_lineage_trace(trace_lineage(root_dir=Path(args.root), run_id=run_id)))
        return 0

    if args.command == "bootstrap-run":
        run_root = bootstrap_run(
            root_dir=Path(args.root),
            run_id=args.run_id,
            work_item_id=args.work_item_id,
            work_item_title=args.work_item_title,
            pr_id=args.pr_id,
        )
        print(run_root.as_posix())
        return 0

    if args.command == "record-review":
        run_id = _resolve_run_id_argument(parser, args)
        path = record_review(
            root_dir=Path(args.root),
            run_id=run_id,
            status=args.status,
            summary=args.summary,
        )
        print(_render_record_review_summary(path, run_id))
        return 0

    if args.command == "record-verification":
        run_id = _resolve_run_id_argument(parser, args)
        path = record_verification(
            root_dir=Path(args.root),
            run_id=run_id,
            lint=args.lint,
            tests=args.tests,
            type_check=args.type_check,
            build=args.build,
            summary=args.summary,
        )
        print(_render_record_verification_summary(path, run_id))
        return 0

    if args.command == "record-qa":
        run_id = _resolve_run_id_argument(parser, args)
        path = record_qa(
            root_dir=Path(args.root),
            run_id=run_id,
            status=args.status,
            summary=args.summary,
        )
        print(_render_record_qa_summary(path, run_id))
        return 0

    if args.command == "record-docs-sync":
        run_id = _resolve_run_id_argument(parser, args)
        path = record_docs_sync(
            root_dir=Path(args.root),
            run_id=run_id,
            status=args.status,
            summary=args.summary,
        )
        print(_render_record_docs_sync_summary(path, run_id))
        return 0

    if args.command == "gate-check":
        run_id = _resolve_run_id_argument(parser, args)
        path = evaluate_gates(root_dir=Path(args.root), run_id=run_id)
        print(_render_gate_check_summary(path, run_id))
        return 0

    if args.command == "build-approval":
        run_id = _resolve_run_id_argument(parser, args)
        approval_path, queue_path = build_approval_request(root_dir=Path(args.root), run_id=run_id)
        approval_payload = read_yaml(approval_path).get("approval_request", {})
        readiness_context = approval_payload.get("readiness_context", {})
        print(_render_build_approval_summary(run_id, approval_path, queue_path, readiness_context))
        return 0

    if args.command == "draft-approval-packet":
        try:
            path = draft_approval_packet(root_dir=Path(args.root), run_id=args.run_id)
        except (FileNotFoundError, FileExistsError, ValueError) as exc:
            parser.error(str(exc))
        print(_render_draft_approval_packet_summary(path, args.run_id))
        return 0

    if args.command == "create-goal":
        try:
            path = create_goal(
                root_dir=Path(args.root),
                goal_id=args.goal_id,
                title=args.title,
                problem=args.problem,
                outcome=args.outcome,
                constraints=args.constraints,
            )
        except FileExistsError as exc:
            parser.error(str(exc))
        print(path.as_posix())
        return 0

    if args.command == "draft-clarifications":
        try:
            path = draft_clarifications(
                root_dir=Path(args.root),
                goal_id=args.goal_id,
            )
        except (FileNotFoundError, FileExistsError) as exc:
            parser.error(str(exc))
        print(_render_draft_clarifications_summary(path, args.goal_id))
        return 0

    if args.command == "draft-work-items":
        try:
            path = draft_work_items(
                root_dir=Path(args.root),
                goal_id=args.goal_id,
            )
        except (FileNotFoundError, FileExistsError) as exc:
            parser.error(str(exc))
        print(_render_draft_work_items_summary(path, args.goal_id))
        return 0

    if args.command == "draft-pr-plan":
        try:
            path = draft_pr_plan(
                root_dir=Path(args.root),
                work_item_id=args.work_item_id,
            )
        except (FileNotFoundError, FileExistsError) as exc:
            parser.error(str(exc))
        print(_render_draft_pr_plan_summary(path, args.work_item_id))
        return 0

    if args.command == "create-clarification":
        try:
            path = create_clarification(
                root_dir=Path(args.root),
                goal_id=args.goal_id,
                clarification_id=args.clarification_id,
                title=args.title,
                category=args.category,
                question=args.question,
                escalation=args.escalation,
            )
        except (FileExistsError, ValueError) as exc:
            parser.error(str(exc))
        print(path.as_posix())
        return 0

    if args.command == "promote-clarification-draft":
        try:
            path = promote_clarification_draft(
                root_dir=Path(args.root),
                goal_id=args.goal_id,
                draft_index=args.draft_index,
                clarification_id=args.clarification_id,
            )
        except (FileNotFoundError, FileExistsError, IndexError) as exc:
            parser.error(str(exc))
        print(_render_promote_clarification_draft_summary(path, args.goal_id, args.clarification_id))
        return 0

    if args.command == "promote-work-item-draft":
        try:
            path = promote_work_item_draft(
                root_dir=Path(args.root),
                goal_id=args.goal_id,
                draft_index=args.draft_index,
                work_item_id=args.work_item_id,
            )
        except (FileNotFoundError, FileExistsError, IndexError, ValueError) as exc:
            parser.error(str(exc))
        print(_render_promote_work_item_draft_summary(path, args.work_item_id))
        return 0

    if args.command == "promote-pr-plan-draft":
        root_dir = Path(args.root)
        had_active_pr = any((root_dir / "prs" / "active").glob("*.md"))
        try:
            result = promote_pr_plan_draft(
                root_dir=root_dir,
                work_item_id=args.work_item_id,
            )
        except (FileNotFoundError, FileExistsError, ValueError) as exc:
            parser.error(str(exc))
        print(
            _render_promote_pr_plan_draft_summary(
                result["path"],
                had_active_pr,
                result["path"].stem,
                result["readiness"],
            )
        )
        return 0

    if args.command == "resolve-clarification":
        try:
            path = resolve_clarification(
                root_dir=Path(args.root),
                goal_id=args.goal_id,
                clarification_id=args.clarification_id,
                decision=args.decision,
                resolution_notes=args.resolution_notes,
                next_action=args.next_action,
                suggested_resolution=args.suggested_resolution,
            )
        except (FileNotFoundError, ValueError) as exc:
            parser.error(str(exc))
        print(path.as_posix())
        return 0

    if args.command == "create-work-item":
        try:
            path = create_work_item(
                root_dir=Path(args.root),
                work_item_id=args.work_item_id,
                title=args.title,
                goal_id=args.goal_id,
                description=args.description,
                acceptance_criteria=args.acceptance_criteria,
                clarification_ids=args.clarification_ids,
            )
        except (FileExistsError, FileNotFoundError, ValueError) as exc:
            parser.error(str(exc))
        print(path.as_posix())
        return 0

    if args.command == "work-item-readiness":
        try:
            readiness = get_work_item_readiness(root_dir=Path(args.root), work_item_id=args.work_item_id)
        except (FileNotFoundError, ValueError) as exc:
            parser.error(str(exc))
        print(_render_work_item_readiness(readiness))
        return 0

    if args.command == "create-pr-plan":
        root_dir = Path(args.root)
        had_active_pr = any((root_dir / "prs" / "active").glob("*.md"))
        try:
            result = create_pr_plan(
                root_dir=root_dir,
                pr_id=args.pr_id,
                work_item_id=args.work_item_id,
                title=args.title,
                summary=args.summary,
            )
        except (FileExistsError, FileNotFoundError, ValueError) as exc:
            parser.error(str(exc))
        print(
            _render_create_pr_plan_summary(
                result["path"],
                had_active_pr,
                args.pr_id,
                result["readiness"],
            )
        )
        return 0

    if args.command == "activate-pr":
        root_dir = Path(args.root)
        active_dir = root_dir / "prs" / "active"
        archive_dir = root_dir / "prs" / "archive"
        prior_active_paths = sorted(path for path in active_dir.glob("*.md") if path.name != f"{args.pr_id}.md")
        try:
            path = activate_pr(root_dir=root_dir, pr_id=args.pr_id)
        except (FileNotFoundError, ValueError) as exc:
            parser.error(str(exc))
        archived_paths = [archive_dir / path.name for path in prior_active_paths if (archive_dir / path.name).exists()]
        print(_render_activate_pr_summary(args.pr_id, path, archived_paths))
        return 0

    if args.command == "start-execution":
        root_dir = Path(args.root)
        try:
            run_root = start_execution(root_dir=root_dir, run_id=args.run_id)
        except ValueError as exc:
            parser.error(_render_start_execution_error(root_dir, args.run_id))
        print(_render_start_execution_summary(run_root, args.run_id))
        return 0

    if args.command == "resolve-approval":
        run_id = _resolve_run_id_argument(parser, args)
        decision_path, queue_path = resolve_approval(
            root_dir=Path(args.root),
            run_id=run_id,
            decision=args.decision,
            actor=args.actor,
            note=args.note,
        )
        print(decision_path.as_posix())
        print(queue_path.as_posix())
        return 0

    if args.command == "cleanup-rehearsal":
        result = cleanup_rehearsal_artifacts(
            root_dir=Path(args.root),
            apply=args.apply,
            include_demo=args.include_demo,
        )
        print(_render_cleanup_summary(result))
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


def inspect_approval_queue_main(argv: Sequence[str] | None = None) -> int:
    forwarded_argv = list(sys.argv[1:] if argv is None else argv)
    return main(["inspect-approval-queue", *forwarded_argv])


if __name__ == "__main__":
    raise SystemExit(main())
