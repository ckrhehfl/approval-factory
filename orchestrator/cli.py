from __future__ import annotations

import argparse
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
    draft_work_items,
    create_goal,
    create_pr_plan,
    create_work_item,
    evaluate_gates,
    get_factory_status,
    get_work_item_readiness,
    inspect_approval,
    inspect_approval_queue,
    inspect_clarification,
    inspect_goal,
    inspect_pr_plan,
    inspect_run,
    inspect_work_item,
    promote_clarification_draft,
    record_docs_sync,
    record_qa,
    record_review,
    record_verification,
    resolve_clarification,
    resolve_latest_run_id,
    resolve_approval,
    start_execution,
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
        lines.append(f"  matching_run_state: {item.get('matching_run_state') or 'none'}")
        lines.append(f"  readiness_context: {item['readiness_context_presence']}")
        lines.append(f"  note: {item.get('note') or 'none'}")
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
        lines.append(f"- next: factory activate-pr --root . --pr-id {pr_id}")
    else:
        lines.append("- reason: no active PR existed, so the new plan became active")
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
    approval_path: Path,
    queue_path: Path | None,
    readiness_context: dict[str, object],
) -> str:
    lines = ["Build Approval:"]
    lines.append(f"- approval_request: {approval_path.as_posix()}")
    lines.append(f"- queue_item: {queue_path.as_posix() if queue_path is not None else 'none'}")
    if readiness_context.get("status") == "available":
        lines.append(f"- readiness_summary: {readiness_context['readiness_summary']}")
        lines.append(f"- linked_clarifications: {readiness_context['linked_clarification_count']}")
    else:
        lines.append("- readiness: unavailable")
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

    status_parser = subparsers.add_parser("status", help="Show current repo-local system status")
    status_parser.add_argument("--root", default=".", help="Repository root path")

    inspect_approval_queue_parser = subparsers.add_parser(
        "inspect-approval-queue",
        help="Inspect pending approval queue entries without changing approval semantics",
    )
    inspect_approval_queue_parser.add_argument("--root", default=".", help="Repository root path")

    inspect_approval_parser = subparsers.add_parser(
        "inspect-approval",
        help="Inspect approval package artifacts in visibility-only mode",
    )
    inspect_approval_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(inspect_approval_parser)

    inspect_run_parser = subparsers.add_parser(
        "inspect-run",
        help="Inspect run-scoped execution artifacts in visibility-only mode",
    )
    inspect_run_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(inspect_run_parser)

    inspect_pr_plan_parser = subparsers.add_parser(
        "inspect-pr-plan",
        help="Inspect PR plan artifacts in visibility-only mode",
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
    )
    inspect_work_item_parser.add_argument("--root", default=".", help="Repository root path")
    inspect_work_item_parser.add_argument("--work-item-id", required=True)

    inspect_clarification_parser = subparsers.add_parser(
        "inspect-clarification",
        help="Inspect clarification artifacts in visibility-only mode",
    )
    inspect_clarification_parser.add_argument("--root", default=".", help="Repository root path")
    inspect_clarification_parser.add_argument("--clarification-id", required=True)

    inspect_goal_parser = subparsers.add_parser(
        "inspect-goal",
        help="Inspect goal artifacts in visibility-only mode",
    )
    inspect_goal_parser.add_argument("--root", default=".", help="Repository root path")
    inspect_goal_parser.add_argument("--goal-id", required=True)

    trace_lineage_parser = subparsers.add_parser(
        "trace-lineage",
        help="Trace run-linked repo-local artifacts in visibility-only mode",
    )
    trace_lineage_parser.add_argument("--root", default=".", help="Repository root path")
    _add_trace_lineage_selector_arguments(trace_lineage_parser)

    bootstrap_parser = subparsers.add_parser("bootstrap-run", help="Create baseline run artifacts")
    bootstrap_parser.add_argument("--root", default=".", help="Repository root path")
    bootstrap_parser.add_argument("--run-id", default=_default_run_id())
    bootstrap_parser.add_argument("--work-item-id", default="WI-000")
    bootstrap_parser.add_argument("--work-item-title", default="bootstrap-run")
    bootstrap_parser.add_argument("--pr-id", default="PR-000")

    record_review_parser = subparsers.add_parser("record-review", help="Record review result")
    record_review_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(record_review_parser)
    record_review_parser.add_argument("--status", choices=["pass", "fail"], required=True)
    record_review_parser.add_argument("--summary", required=True)

    record_verification_parser = subparsers.add_parser("record-verification", help="Record verification checks result")
    record_verification_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(record_verification_parser)
    record_verification_parser.add_argument("--lint", choices=["pass", "fail", "pending"], required=True)
    record_verification_parser.add_argument("--tests", choices=["pass", "fail", "pending"], required=True)
    record_verification_parser.add_argument("--type-check", choices=["pass", "fail", "pending"], required=True)
    record_verification_parser.add_argument("--build", choices=["pass", "fail", "pending"], required=True)
    record_verification_parser.add_argument("--summary", required=True)

    record_qa_parser = subparsers.add_parser("record-qa", help="Record QA result")
    record_qa_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(record_qa_parser)
    record_qa_parser.add_argument("--status", choices=["pass", "fail"], required=True)
    record_qa_parser.add_argument("--summary", required=True)

    record_docs_sync_parser = subparsers.add_parser("record-docs-sync", help="Record docs sync result")
    record_docs_sync_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(record_docs_sync_parser)
    record_docs_sync_parser.add_argument("--status", choices=["complete", "required", "not-needed"], required=True)
    record_docs_sync_parser.add_argument("--summary", required=True)

    gate_check_parser = subparsers.add_parser("gate-check", help="Evaluate gate status")
    gate_check_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(gate_check_parser)

    build_approval_parser = subparsers.add_parser("build-approval", help="Build evidence and approval request")
    build_approval_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(build_approval_parser)

    create_goal_parser = subparsers.add_parser("create-goal", help="Create a goal intake artifact")
    create_goal_parser.add_argument("--root", default=".", help="Repository root path")
    create_goal_parser.add_argument("--goal-id", required=True)
    create_goal_parser.add_argument("--title", required=True)
    create_goal_parser.add_argument("--problem", required=True)
    create_goal_parser.add_argument("--outcome", required=True)
    create_goal_parser.add_argument("--constraints")

    draft_clarifications_parser = subparsers.add_parser(
        "draft-clarifications",
        help="Create a deterministic clarification draft artifact without queue mutation",
    )
    draft_clarifications_parser.add_argument("--root", default=".", help="Repository root path")
    draft_clarifications_parser.add_argument("--goal-id", required=True)

    draft_work_items_parser = subparsers.add_parser(
        "draft-work-items",
        help="Draft work item candidates from official clarification artifacts",
    )
    draft_work_items_parser.add_argument("--root", default=".", help="Repository root path")
    draft_work_items_parser.add_argument("--goal-id", required=True)

    promote_clarification_draft_parser = subparsers.add_parser(
        "promote-clarification-draft",
        help="Promote one draft item into an official clarification artifact",
    )
    promote_clarification_draft_parser.add_argument("--root", default=".", help="Repository root path")
    promote_clarification_draft_parser.add_argument("--goal-id", required=True)
    promote_clarification_draft_parser.add_argument("--draft-index", type=int, required=True)
    promote_clarification_draft_parser.add_argument("--clarification-id", required=True)

    create_clarification_parser = subparsers.add_parser(
        "create-clarification",
        help="Create a clarification artifact for a goal",
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
    )
    resolve_clarification_parser.add_argument("--root", default=".", help="Repository root path")
    resolve_clarification_parser.add_argument("--goal-id", required=True)
    resolve_clarification_parser.add_argument("--clarification-id", required=True)
    resolve_clarification_parser.add_argument("--decision", choices=["resolved", "deferred", "escalated"], required=True)
    resolve_clarification_parser.add_argument("--resolution-notes", required=True)
    resolve_clarification_parser.add_argument("--next-action", required=True)
    resolve_clarification_parser.add_argument("--suggested-resolution")

    create_work_item_parser = subparsers.add_parser("create-work-item", help="Create a work item artifact")
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
    )
    work_item_readiness_parser.add_argument("--root", default=".", help="Repository root path")
    work_item_readiness_parser.add_argument("--work-item-id", required=True)

    create_pr_plan_parser = subparsers.add_parser("create-pr-plan", help="Create the single active PR plan artifact")
    create_pr_plan_parser.add_argument("--root", default=".", help="Repository root path")
    create_pr_plan_parser.add_argument("--pr-id", required=True)
    create_pr_plan_parser.add_argument("--work-item-id", required=True)
    create_pr_plan_parser.add_argument("--title", required=True)
    create_pr_plan_parser.add_argument("--summary", required=True)

    activate_pr_parser = subparsers.add_parser("activate-pr", help="Switch the single active PR plan")
    activate_pr_parser.add_argument("--root", default=".", help="Repository root path")
    activate_pr_parser.add_argument("--pr-id", required=True)

    start_execution_parser = subparsers.add_parser(
        "start-execution",
        help="Start a run from the single active PR plan",
    )
    start_execution_parser.add_argument("--root", default=".", help="Repository root path")
    start_execution_parser.add_argument("--run-id", default=_default_run_id())

    resolve_approval_parser = subparsers.add_parser("resolve-approval", help="Resolve pending approval request")
    resolve_approval_parser.add_argument("--root", default=".", help="Repository root path")
    _add_run_selector_arguments(resolve_approval_parser)
    resolve_approval_parser.add_argument("--decision", choices=["approve", "reject", "exception"], required=True)
    resolve_approval_parser.add_argument("--actor", required=True)
    resolve_approval_parser.add_argument("--note", required=True)

    cleanup_parser = subparsers.add_parser(
        "cleanup-rehearsal",
        help="List or remove rehearsal artifacts from repo-local operating paths",
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
        print(path.as_posix())
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
        print(path.as_posix())
        return 0

    if args.command == "record-qa":
        run_id = _resolve_run_id_argument(parser, args)
        path = record_qa(
            root_dir=Path(args.root),
            run_id=run_id,
            status=args.status,
            summary=args.summary,
        )
        print(path.as_posix())
        return 0

    if args.command == "record-docs-sync":
        run_id = _resolve_run_id_argument(parser, args)
        path = record_docs_sync(
            root_dir=Path(args.root),
            run_id=run_id,
            status=args.status,
            summary=args.summary,
        )
        print(path.as_posix())
        return 0

    if args.command == "gate-check":
        run_id = _resolve_run_id_argument(parser, args)
        path = evaluate_gates(root_dir=Path(args.root), run_id=run_id)
        print(path.as_posix())
        return 0

    if args.command == "build-approval":
        run_id = _resolve_run_id_argument(parser, args)
        approval_path, queue_path = build_approval_request(root_dir=Path(args.root), run_id=run_id)
        approval_payload = read_yaml(approval_path).get("approval_request", {})
        readiness_context = approval_payload.get("readiness_context", {})
        print(_render_build_approval_summary(approval_path, queue_path, readiness_context))
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
        print(path.as_posix())
        return 0

    if args.command == "draft-work-items":
        try:
            path = draft_work_items(
                root_dir=Path(args.root),
                goal_id=args.goal_id,
            )
        except (FileNotFoundError, FileExistsError) as exc:
            parser.error(str(exc))
        print(path.as_posix())
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
        print(path.as_posix())
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
        print(run_root.as_posix())
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


if __name__ == "__main__":
    raise SystemExit(main())
