from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
import shutil
import re
from typing import Any, Iterable

from orchestrator.models import RunRecord
from orchestrator.yaml_io import read_yaml, write_yaml


class PipelineState(StrEnum):
    draft = "draft"
    in_progress = "in_progress"
    approval_pending = "approval_pending"
    approved = "approved"
    rejected = "rejected"


ARTIFACT_FILENAMES = (
    "work-item.yaml",
    "pr-plan.yaml",
    "verification-report.yaml",
    "review-report.yaml",
    "qa-report.yaml",
    "docs-sync-report.yaml",
    "evidence-bundle.yaml",
    "approval-request.yaml",
    "gate-status.yaml",
)

PR_DOC_FILENAMES = (
    "scope.md",
    "plan.md",
    "review.md",
    "qa.md",
    "docs-sync.md",
    "evidence.md",
    "decision.md",
)

GOAL_STATUS = "draft"
CLARIFICATION_STATUS = "open"
WORK_ITEM_STATUS = "draft"
PR_PLAN_STATUS = "planned"
VALID_CLARIFICATION_CATEGORIES = {
    "scope",
    "design",
    "dependency",
    "constraint",
    "approval-required",
}

CLEANUP_REHEARSAL_SPECS: tuple[tuple[str, str], ...] = (
    ("runs", "runs/latest/RUN-RH-*"),
    ("approval_queue_pending", "approval_queue/pending/APR-RUN-RH-*.yaml"),
    ("approval_queue_approved", "approval_queue/approved/APR-RUN-RH-*.yaml"),
    ("approval_queue_rejected", "approval_queue/rejected/APR-RUN-RH-*.yaml"),
    ("approval_queue_exceptions", "approval_queue/exceptions/APR-RUN-RH-*.yaml"),
    ("goals", "goals/GOAL-RH-*.md"),
    ("clarifications", "clarifications/GOAL-RH-*"),
    ("work_items", "docs/work-items/WI-RH-*.md"),
    ("prs_active", "prs/active/PR-RH-*.md"),
    ("prs_archive", "prs/archive/PR-RH-*.md"),
)

CLEANUP_DEMO_SPECS: tuple[tuple[str, str], ...] = (
    ("runs_demo_prefix", "runs/latest/RUN-DEMO-*"),
    ("runs_demo_suffix", "runs/latest/RUN-*-DEMO*"),
    ("approval_queue_pending_demo_prefix", "approval_queue/pending/APR-RUN-DEMO-*.yaml"),
    ("approval_queue_pending_demo_suffix", "approval_queue/pending/APR-RUN-*-DEMO*.yaml"),
    ("approval_queue_approved_demo_prefix", "approval_queue/approved/APR-RUN-DEMO-*.yaml"),
    ("approval_queue_approved_demo_suffix", "approval_queue/approved/APR-RUN-*-DEMO*.yaml"),
    ("approval_queue_rejected_demo_prefix", "approval_queue/rejected/APR-RUN-DEMO-*.yaml"),
    ("approval_queue_rejected_demo_suffix", "approval_queue/rejected/APR-RUN-*-DEMO*.yaml"),
    ("approval_queue_exceptions_demo_prefix", "approval_queue/exceptions/APR-RUN-DEMO-*.yaml"),
    ("approval_queue_exceptions_demo_suffix", "approval_queue/exceptions/APR-RUN-*-DEMO*.yaml"),
    ("goals_demo", "goals/*DEMO*.md"),
    ("clarifications_demo", "clarifications/*DEMO*"),
    ("work_items_demo", "docs/work-items/*DEMO*.md"),
    ("prs_active_demo", "prs/active/*DEMO*.md"),
    ("prs_archive_demo", "prs/archive/*DEMO*.md"),
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _slugify(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    return "-".join(filter(None, slug.split("-"))) or "untitled"


def _ensure_text_file(path: Path, lines: Iterable[str]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _normalize_multiline_text(value: str | None) -> list[str]:
    text = (value or "").strip()
    if not text:
        return ["TBD"]
    return text.splitlines()


def _run_root(root_dir: Path, run_id: str) -> Path:
    return root_dir / "runs" / "latest" / run_id


def _artifacts_dir(root_dir: Path, run_id: str) -> Path:
    return _run_root(root_dir, run_id) / "artifacts"


def _load_run(root_dir: Path, run_id: str) -> dict[str, Any]:
    return read_yaml(_run_root(root_dir, run_id) / "run.yaml")


def _write_run(root_dir: Path, run_id: str, payload: dict[str, Any]) -> None:
    write_yaml(_run_root(root_dir, run_id) / "run.yaml", payload)


def _record_run_operation(root_dir: Path, run_id: str, operation: str, details: dict[str, Any] | None = None) -> None:
    run_payload = _load_run(root_dir, run_id)
    run = run_payload["run"]
    operations = run.setdefault("operations", {})
    operation_state = operations.setdefault(operation, {"count": 0})
    operation_state["count"] = int(operation_state.get("count", 0)) + 1
    operation_state["last_at"] = _now_iso()
    if details:
        operation_state["last_details"] = details
    _write_run(root_dir, run_id, run_payload)


def _artifact_path(root_dir: Path, run_id: str, name: str) -> Path:
    return _artifacts_dir(root_dir, run_id) / name


def _read_artifact(root_dir: Path, run_id: str, name: str) -> dict[str, Any]:
    return read_yaml(_artifact_path(root_dir, run_id, name))


def _write_artifact(root_dir: Path, run_id: str, name: str, payload: dict[str, Any]) -> None:
    write_yaml(_artifact_path(root_dir, run_id, name), payload)


def _ensure_artifact(root_dir: Path, run_id: str, name: str, payload: dict[str, Any]) -> None:
    path = _artifact_path(root_dir, run_id, name)
    if path.exists():
        return
    write_yaml(path, payload)


def _update_pipeline_state(root_dir: Path, run_id: str, state: PipelineState) -> None:
    run_payload = _load_run(root_dir, run_id)
    run_payload["run"]["state"] = state.value
    run_payload["run"]["updated_at"] = _now_iso()
    _write_run(root_dir, run_id, run_payload)


def _set_docs_sync_verdict(root_dir: Path, run_id: str, verdict: str, summary: str) -> None:
    run_payload = _load_run(root_dir, run_id)
    run_payload["run"]["docs_sync_verdict"] = verdict
    run_payload["run"]["docs_sync_summary"] = summary
    run_payload["run"]["docs_sync_recorded_at"] = _now_iso()
    _write_run(root_dir, run_id, run_payload)


def _docs_sync_complete(status: str) -> bool:
    return status in {"complete", "not-needed"}


def _verification_status(value: Any) -> str:
    status = str(value or "pending")
    if status not in {"pass", "fail", "pending"}:
        raise ValueError(f"verification status must be pass|fail|pending (got: {status})")
    return status


def _read_verification_report(root_dir: Path, run_id: str) -> dict[str, Any]:
    return _read_artifact(root_dir, run_id, "verification-report.yaml")["verification_report"]


def _verification_payload_or_pending(root_dir: Path, run_id: str) -> dict[str, Any]:
    report_path = _artifact_path(root_dir, run_id, "verification-report.yaml")
    if not report_path.exists():
        return {
            "lint": "pending",
            "tests": "pending",
            "type_check": "pending",
            "build": "pending",
            "summary": "verification artifact missing",
        }
    return _read_verification_report(root_dir, run_id)


def _queue_path_for_approval(root_dir: Path, approval: dict[str, Any]) -> tuple[Path, bool]:
    approval_request = approval["approval_request"]
    queue_dir = root_dir / "approval_queue" / "pending"
    queue_dir.mkdir(parents=True, exist_ok=True)

    primary = queue_dir / f"{approval_request['id']}.yaml"
    if not primary.exists():
        return primary, True
    if read_yaml(primary) == approval:
        return primary, False

    retry = 2
    while True:
        candidate = queue_dir / f"{approval_request['id']}--r{retry}.yaml"
        if not candidate.exists():
            return candidate, True
        if read_yaml(candidate) == approval:
            return candidate, False
        retry += 1


def _pr_active_dir(root_dir: Path) -> Path:
    return root_dir / "prs" / "active"


def _pr_archive_dir(root_dir: Path) -> Path:
    return root_dir / "prs" / "archive"


def _find_active_pr_plan(root_dir: Path) -> Path:
    active_dir = _pr_active_dir(root_dir)
    plans = sorted(active_dir.glob("*.md"))
    if not plans:
        raise ValueError("start-execution requires exactly one active PR plan under prs/active/, found none")
    if len(plans) > 1:
        plan_list = ", ".join(path.as_posix() for path in plans)
        raise ValueError(
            "start-execution requires exactly one active PR plan under prs/active/, "
            f"found {len(plans)}: {plan_list}"
        )
    return plans[0]


def _parse_markdown_sections(path: Path) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current_heading: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("## "):
            current_heading = raw_line[3:].strip()
            sections[current_heading] = []
            continue
        if current_heading is None:
            continue
        sections[current_heading].append(raw_line)

    return {heading: "\n".join(lines).strip() for heading, lines in sections.items()}


def _parse_iso_for_sort(value: Any) -> datetime:
    text = str(value or "").strip()
    if not text:
        return datetime.min.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(text)


def _read_active_pr_summary(root_dir: Path) -> dict[str, str] | None:
    plans = sorted(_pr_active_dir(root_dir).glob("*.md"))
    if not plans:
        return None

    sections = _parse_markdown_sections(plans[0])
    return {
        "pr_id": sections.get("PR ID", plans[0].stem),
        "work_item_id": sections.get("Work Item ID", "unknown"),
    }


def _read_latest_run_summary(root_dir: Path) -> dict[str, str] | None:
    candidates: list[tuple[datetime, str, dict[str, Any]]] = []
    latest_dir = root_dir / "runs" / "latest"
    for run_file in sorted(latest_dir.glob("*/run.yaml")):
        payload = read_yaml(run_file).get("run", {})
        timestamp = _parse_iso_for_sort(payload.get("updated_at") or payload.get("created_at"))
        run_id = str(payload.get("run_id", run_file.parent.name))
        candidates.append((timestamp, run_id, payload))

    if not candidates:
        return None

    _, _, latest = max(candidates, key=lambda item: (item[0], item[1]))
    return {
        "run_id": str(latest.get("run_id", "")),
        "state": str(latest.get("state", "unknown")),
    }


def _read_approval_status(root_dir: Path, run_id: str | None) -> str:
    if not run_id:
        return "none"

    approval_id = f"APR-{run_id}.yaml"
    approved_path = root_dir / "approval_queue" / "approved" / approval_id
    pending_path = root_dir / "approval_queue" / "pending" / approval_id
    decision_path = _artifact_path(root_dir, run_id, "approval-decision.yaml")

    if approved_path.exists():
        return "approved"
    if pending_path.exists():
        return "pending"
    if decision_path.exists():
        decision = read_yaml(decision_path).get("approval_decision", {}).get("decision")
        if decision == "approve":
            return "approved"
    return "none"


def _read_open_clarifications(root_dir: Path) -> list[str]:
    clarifications: list[str] = []
    for clarification_path in sorted((root_dir / "clarifications").glob("*/*.md")):
        sections = _parse_markdown_sections(clarification_path)
        if sections.get("Status") != CLARIFICATION_STATUS:
            continue
        clarifications.append(sections.get("Clarification ID", clarification_path.stem))
    return clarifications


def _collect_cleanup_targets(root_dir: Path, specs: Iterable[tuple[str, str]]) -> list[dict[str, str]]:
    targets: list[dict[str, str]] = []
    seen: set[str] = set()
    for category, pattern in specs:
        for path in sorted(root_dir.glob(pattern)):
            relative_path = path.relative_to(root_dir).as_posix()
            if relative_path in seen:
                continue
            seen.add(relative_path)
            targets.append(
                {
                    "category": category,
                    "path": relative_path,
                    "kind": "dir" if path.is_dir() else "file",
                }
            )
    return targets


def cleanup_rehearsal_artifacts(*, root_dir: Path, apply: bool = False, include_demo: bool = False) -> dict[str, Any]:
    specs = list(CLEANUP_REHEARSAL_SPECS)
    if include_demo:
        specs.extend(CLEANUP_DEMO_SPECS)

    targets = _collect_cleanup_targets(root_dir, specs)
    if apply:
        for target in sorted(targets, key=lambda item: (len(item["path"]), item["path"]), reverse=True):
            path = root_dir / target["path"]
            if not path.exists():
                continue
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    return {
        "mode": "apply" if apply else "dry-run",
        "include_demo": include_demo,
        "matched_count": len(targets),
        "targets": targets,
    }


def get_factory_status(root_dir: Path) -> dict[str, Any]:
    active_pr = _read_active_pr_summary(root_dir)
    latest_run = _read_latest_run_summary(root_dir)
    return {
        "active_pr": active_pr,
        "latest_run": latest_run,
        "approval": {
            "status": _read_approval_status(root_dir, latest_run["run_id"] if latest_run else None),
        },
        "open_clarifications": _read_open_clarifications(root_dir),
    }


def _find_work_item_artifact(root_dir: Path, work_item_id: str) -> Path:
    work_items_dir = root_dir / "docs" / "work-items"
    exact_path = work_items_dir / f"{work_item_id}.md"
    if exact_path.exists():
        return exact_path

    matches = sorted(work_items_dir.glob(f"{work_item_id}-*.md"))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise ValueError(
            "start-execution requires the active PR work_item_id to link to a work item artifact under "
            f"docs/work-items/ (missing: {work_item_id})"
        )

    match_list = ", ".join(path.as_posix() for path in matches)
    raise ValueError(
        "start-execution requires the active PR work_item_id to link to exactly one work item artifact under "
        f"docs/work-items/; found {len(matches)} matches for {work_item_id}: {match_list}"
    )


def _require_recorded_artifact(root_dir: Path, run_id: str, name: str, key: str, command: str) -> dict[str, Any]:
    path = _artifact_path(root_dir, run_id, name)
    if not path.exists():
        raise ValueError(f"cannot build approval request without {name}")

    payload = read_yaml(path)[key]
    if not payload.get("recorded_at"):
        raise ValueError(f"cannot build approval request before {command} records {name}")
    return payload


def _require_build_approval_prerequisites(root_dir: Path, run_id: str) -> dict[str, dict[str, Any]]:
    verification = _require_recorded_artifact(
        root_dir,
        run_id,
        "verification-report.yaml",
        "verification_report",
        "record-verification",
    )
    review = _require_recorded_artifact(
        root_dir,
        run_id,
        "review-report.yaml",
        "review_report",
        "record-review",
    )
    qa = _require_recorded_artifact(
        root_dir,
        run_id,
        "qa-report.yaml",
        "qa_report",
        "record-qa",
    )
    docs_sync = _require_recorded_artifact(
        root_dir,
        run_id,
        "docs-sync-report.yaml",
        "docs_sync_report",
        "record-docs-sync",
    )
    return {
        "verification": verification,
        "review": review,
        "qa": qa,
        "docs_sync": docs_sync,
    }


def _read_markdown_section(path: Path, heading: str) -> str:
    content = path.read_text(encoding="utf-8")
    pattern = rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError(f"Required section '## {heading}' not found in active PR plan: {path.as_posix()}")
    return match.group(1).strip()


def _read_active_pr_plan(path: Path) -> dict[str, str]:
    pr_id = _read_markdown_section(path, "PR ID")
    work_item_id = _read_markdown_section(path, "Work Item ID")
    title = _read_markdown_section(path, "Title")
    return {
        "pr_id": pr_id,
        "work_item_id": work_item_id,
        "title": title,
        "pr_plan_path": path.as_posix(),
    }


def create_goal(
    *,
    root_dir: Path,
    goal_id: str,
    title: str,
    problem: str,
    outcome: str,
    constraints: str | None = None,
) -> Path:
    goal_path = root_dir / "goals" / f"{goal_id}.md"
    if goal_path.exists():
        raise FileExistsError(f"Goal artifact already exists for goal-id '{goal_id}': {goal_path.as_posix()}")

    constraint_lines = _normalize_multiline_text(constraints)
    lines = [
        f"# {goal_id}: {title}",
        "",
        "## Goal ID",
        goal_id,
        "",
        "## Title",
        title,
        "",
        "## Status",
        GOAL_STATUS,
        "",
        "## Problem",
        *problem.splitlines(),
        "",
        "## Desired Outcome",
        *outcome.splitlines(),
        "",
        "## Non-Goals",
        "- TBD",
        "",
        "## Constraints",
        *constraint_lines,
        "",
        "## Risks",
        "- TBD",
        "",
        "## Open Questions",
        "- TBD",
        "",
        "## Approval-Required Decisions",
        "- TBD",
        "",
        "## Success Criteria",
        "- TBD",
        "",
    ]
    goal_path.parent.mkdir(parents=True, exist_ok=True)
    goal_path.write_text("\n".join(lines), encoding="utf-8")
    return goal_path


def create_clarification(
    *,
    root_dir: Path,
    goal_id: str,
    clarification_id: str,
    title: str,
    category: str,
    question: str,
    escalation: bool = False,
) -> Path:
    normalized_category = category.strip()
    if normalized_category not in VALID_CLARIFICATION_CATEGORIES:
        allowed = ", ".join(sorted(VALID_CLARIFICATION_CATEGORIES))
        raise ValueError(
            f"clarification category must be one of {allowed} (got: {normalized_category or category})"
        )

    clarification_path = root_dir / "clarifications" / goal_id / f"{clarification_id}.md"
    if clarification_path.exists():
        raise FileExistsError(
            "Clarification artifact already exists "
            f"for goal-id '{goal_id}' and clarification-id '{clarification_id}': "
            f"{clarification_path.as_posix()}"
        )

    lines = [
        f"# {clarification_id}: {title}",
        "",
        "## Clarification ID",
        clarification_id,
        "",
        "## Goal ID",
        goal_id,
        "",
        "## Title",
        title,
        "",
        "## Status",
        CLARIFICATION_STATUS,
        "",
        "## Category",
        normalized_category,
        "",
        "## Question",
        *question.splitlines(),
        "",
        "## Suggested Resolution",
        "- TBD",
        "",
        "## Escalation Required",
        "yes" if escalation else "no",
        "",
        "## Resolution Notes",
        "- TBD",
        "",
        "## Next Action",
        "- TBD",
        "",
    ]
    clarification_path.parent.mkdir(parents=True, exist_ok=True)
    clarification_path.write_text("\n".join(lines), encoding="utf-8")
    return clarification_path


def create_work_item(
    *,
    root_dir: Path,
    work_item_id: str,
    title: str,
    goal_id: str,
    description: str,
    acceptance_criteria: str | None = None,
) -> Path:
    work_item_path = root_dir / "docs" / "work-items" / f"{work_item_id}.md"
    if work_item_path.exists():
        raise FileExistsError(
            f"Work item artifact already exists for work-item-id '{work_item_id}': {work_item_path.as_posix()}"
        )

    acceptance_criteria_lines = _normalize_multiline_text(acceptance_criteria)
    lines = [
        f"# {work_item_id}: {title}",
        "",
        "## Work Item ID",
        work_item_id,
        "",
        "## Goal ID",
        goal_id,
        "",
        "## Title",
        title,
        "",
        "## Status",
        WORK_ITEM_STATUS,
        "",
        "## Description",
        *description.splitlines(),
        "",
        "## Scope",
        "- TBD",
        "",
        "## Out of Scope",
        "- TBD",
        "",
        "## Acceptance Criteria",
        *acceptance_criteria_lines,
        "",
        "## Dependencies",
        "- TBD",
        "",
        "## Risks",
        "- TBD",
        "",
        "## Notes",
        "- TBD",
        "",
    ]
    work_item_path.parent.mkdir(parents=True, exist_ok=True)
    work_item_path.write_text("\n".join(lines), encoding="utf-8")
    return work_item_path


def create_pr_plan(
    *,
    root_dir: Path,
    pr_id: str,
    work_item_id: str,
    title: str,
    summary: str,
) -> Path:
    active_dir = _pr_active_dir(root_dir)
    archive_dir = _pr_archive_dir(root_dir)
    active_pr_plan_path = active_dir / f"{pr_id}.md"
    if active_pr_plan_path.exists():
        raise FileExistsError(
            f"PR plan artifact already exists for pr-id '{pr_id}': {active_pr_plan_path.as_posix()}"
        )
    archive_pr_plan_path = archive_dir / f"{pr_id}.md"
    if archive_pr_plan_path.exists():
        raise FileExistsError(
            f"PR plan artifact already exists for pr-id '{pr_id}': {archive_pr_plan_path.as_posix()}"
        )

    existing_active_plans = sorted(active_dir.glob("*.md"))
    pr_plan_path = active_pr_plan_path if not existing_active_plans else archive_pr_plan_path

    lines = [
        f"# {pr_id}: {title}",
        "",
        "## PR ID",
        pr_id,
        "",
        "## Work Item ID",
        work_item_id,
        "",
        "## Title",
        title,
        "",
        "## Status",
        PR_PLAN_STATUS,
        "",
        "## Summary",
        *summary.splitlines(),
        "",
        "## Scope",
        "- TBD",
        "",
        "## Out of Scope",
        "- TBD",
        "",
        "## Implementation Notes",
        "- TBD",
        "",
        "## Risks",
        "- TBD",
        "",
        "## Open Questions",
        "- TBD",
        "",
    ]
    pr_plan_path.parent.mkdir(parents=True, exist_ok=True)
    pr_plan_path.write_text("\n".join(lines), encoding="utf-8")
    return pr_plan_path


def activate_pr(*, root_dir: Path, pr_id: str) -> Path:
    active_dir = _pr_active_dir(root_dir)
    archive_dir = _pr_archive_dir(root_dir)
    active_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    target_active_path = active_dir / f"{pr_id}.md"
    target_archive_path = archive_dir / f"{pr_id}.md"
    target_exists_in_active = target_active_path.exists()
    target_exists_in_archive = target_archive_path.exists()

    if target_exists_in_active and target_exists_in_archive:
        raise ValueError(
            "activate-pr found duplicate PR plan artifacts for "
            f"'{pr_id}' in both active and archive: {target_active_path.as_posix()}, "
            f"{target_archive_path.as_posix()}"
        )
    if not target_exists_in_active and not target_exists_in_archive:
        raise FileNotFoundError(
            f"activate-pr requires an existing PR plan artifact for pr-id '{pr_id}' under prs/active/ or prs/archive/"
        )

    for active_plan in sorted(active_dir.glob("*.md")):
        if active_plan.name == f"{pr_id}.md":
            continue
        active_plan.replace(archive_dir / active_plan.name)

    if target_exists_in_archive:
        target_archive_path.replace(target_active_path)

    return target_active_path


def _queue_item_name(run_id: str) -> str:
    return f"APR-{run_id}.yaml"


def _queue_item_relative_path(queue_name: str, run_id: str) -> str:
    return f"approval_queue/{queue_name}/{_queue_item_name(run_id)}"


def _decision_to_queue(decision: str) -> str:
    mapping = {
        "approve": "approved",
        "reject": "rejected",
        "exception": "exceptions",
    }
    if decision not in mapping:
        raise ValueError(f"decision must be approve|reject|exception (got: {decision})")
    return mapping[decision]


def _resolved_at_now() -> str:
    return _now_iso()


def bootstrap_run(
    *,
    root_dir: Path,
    run_id: str,
    work_item_id: str,
    pr_id: str,
    work_item_title: str = "bootstrap-run",
    pr_plan_path: str | None = None,
    source_command: str | None = None,
) -> Path:
    run_root = root_dir / "runs" / "latest" / run_id
    _artifacts_dir(root_dir, run_id).mkdir(parents=True, exist_ok=True)

    run_file = run_root / "run.yaml"
    if not run_file.exists():
        run_record = RunRecord.new(
            run_id=run_id,
            work_item_id=work_item_id,
            pr_id=pr_id,
            state=PipelineState.draft.value,
            pr_plan_path=pr_plan_path,
            pr_title=work_item_title,
            source_command=source_command,
        )
        write_yaml(run_file, run_record.as_payload())

    _ensure_artifact(
        root_dir,
        run_id,
        "work-item.yaml",
        {
            "work_item": {
                "id": work_item_id,
                "title": work_item_title,
                "status": PipelineState.draft.value,
            }
        },
    )
    _ensure_artifact(
        root_dir,
        run_id,
        "pr-plan.yaml",
        {
            "pr_plan": {
                "pr_id": pr_id,
                "work_item_id": work_item_id,
                "title": work_item_title,
                "source_pr_plan_path": pr_plan_path or "",
                "scope": "",
                "status": PipelineState.draft.value,
            }
        },
    )
    _ensure_artifact(
        root_dir,
        run_id,
        "verification-report.yaml",
        {
            "verification_report": {
                "pr_id": pr_id,
                "summary": "",
                "lint": "pending",
                "tests": "pending",
                "type_check": "pending",
                "build": "pending",
            }
        },
    )
    _ensure_artifact(
        root_dir,
        run_id,
        "review-report.yaml",
        {
            "review_report": {
                "pr_id": pr_id,
                "status": "pending",
                "summary": "",
                "findings": [],
            }
        },
    )
    _ensure_artifact(
        root_dir,
        run_id,
        "qa-report.yaml",
        {
            "qa_report": {
                "pr_id": pr_id,
                "status": "pending",
                "summary": "",
                "findings": [],
            }
        },
    )
    _ensure_artifact(
        root_dir,
        run_id,
        "docs-sync-report.yaml",
        {
            "docs_sync_report": {
                "pr_id": pr_id,
                "required": True,
                "status": "pending",
                "summary": "",
                "changed_docs": [],
            }
        },
    )
    _ensure_artifact(
        root_dir,
        run_id,
        "evidence-bundle.yaml",
        {
            "evidence_bundle": {
                "id": f"EV-{run_id}",
                "work_item_id": work_item_id,
                "pr_id": pr_id,
                "summary": "",
                "checks": {
                    "lint": {"status": "pending", "notes": ""},
                    "tests": {"status": "pending", "notes": ""},
                    "type_check": {"status": "pending", "notes": ""},
                    "build": {"status": "pending", "notes": ""},
                },
                "review_findings": [],
                "qa_findings": [],
                "docs_sync": {
                    "required": True,
                    "status": "pending",
                    "changed_docs": [],
                },
                "residual_risks": [],
                "status": "pending",
            }
        },
    )
    _ensure_artifact(
        root_dir,
        run_id,
        "approval-request.yaml",
        {
            "approval_request": {
                "id": f"APR-{run_id}",
                "work_item_id": work_item_id,
                "pr_id": pr_id,
                "gate_type": "merge_approval",
                "decision_required": [
                    "approve",
                    "reject",
                    "request_changes",
                    "approve_with_exception",
                ],
                "summary": {
                    "problem": "",
                    "proposed_change": "",
                    "user_impact": "",
                },
                "checks": {
                    "lint": "pending",
                    "tests": "pending",
                    "type_check": "pending",
                    "build": "pending",
                    "review": "pending",
                    "qa": "pending",
                    "docs_sync": "pending",
                },
                "risks": [],
                "exceptions": [],
                "changed_docs": [],
                "changed_files": [],
                "adr_refs": [],
                "evidence_bundle": "",
                "recommended_decision": "",
            }
        },
    )
    _ensure_artifact(
        root_dir,
        run_id,
        "gate-status.yaml",
        {
            "gate_status": {
                "pr_id": pr_id,
                "current_state": PipelineState.draft.value,
                "states": [state.value for state in PipelineState],
                "gates": {
                    "scope_approval": "pending",
                    "architecture_approval": "pending",
                    "exception_approval": "pending",
                    "merge_approval": "pending",
                    "release_approval": "pending",
                },
                "prerequisite_results": {},
            }
        },
    )

    pr_docs_dir = root_dir / "docs" / "prs" / pr_id
    for name in PR_DOC_FILENAMES:
        _ensure_text_file(
            pr_docs_dir / name,
            [f"# {pr_id} {name.replace('.md', '').replace('-', ' ').title()}", ""],
        )

    slug = _slugify(work_item_title)
    work_item_doc = root_dir / "docs" / "work-items" / f"{work_item_id}-{slug}.md"
    _ensure_text_file(work_item_doc, [f"# {work_item_id}: {work_item_title}", "", "## Status", "Draft"])

    return run_root


def start_execution(*, root_dir: Path, run_id: str) -> Path:
    pr_plan_path = _find_active_pr_plan(root_dir)
    pr_plan = _read_active_pr_plan(pr_plan_path)
    work_item_path = _find_work_item_artifact(root_dir, pr_plan["work_item_id"])
    run_root = bootstrap_run(
        root_dir=root_dir,
        run_id=run_id,
        work_item_id=pr_plan["work_item_id"],
        pr_id=pr_plan["pr_id"],
        work_item_title=pr_plan["title"],
        pr_plan_path=pr_plan["pr_plan_path"],
        source_command="start-execution",
    )

    run_payload = _load_run(root_dir, run_id)
    run_payload["run"]["pr_plan_path"] = pr_plan["pr_plan_path"]
    run_payload["run"]["pr_title"] = pr_plan["title"]
    run_payload["run"]["source_command"] = "start-execution"
    run_payload["run"]["work_item_path"] = work_item_path.as_posix()
    run_payload["run"]["state"] = PipelineState.in_progress.value
    run_payload["run"]["updated_at"] = _now_iso()
    _write_run(root_dir, run_id, run_payload)

    pr_plan_artifact = _read_artifact(root_dir, run_id, "pr-plan.yaml")
    pr_plan_artifact["pr_plan"]["work_item_id"] = pr_plan["work_item_id"]
    pr_plan_artifact["pr_plan"]["title"] = pr_plan["title"]
    pr_plan_artifact["pr_plan"]["source_pr_plan_path"] = pr_plan["pr_plan_path"]
    pr_plan_artifact["pr_plan"]["status"] = PipelineState.in_progress.value
    _write_artifact(root_dir, run_id, "pr-plan.yaml", pr_plan_artifact)

    work_item_artifact = _read_artifact(root_dir, run_id, "work-item.yaml")
    work_item_artifact["work_item"]["status"] = PipelineState.in_progress.value
    work_item_artifact["work_item"]["source_work_item_path"] = work_item_path.as_posix()
    _write_artifact(root_dir, run_id, "work-item.yaml", work_item_artifact)
    return run_root


def record_review(*, root_dir: Path, run_id: str, status: str, summary: str) -> Path:
    if status not in {"pass", "fail"}:
        raise ValueError("review status must be pass|fail")

    report = _read_artifact(root_dir, run_id, "review-report.yaml")
    report["review_report"]["status"] = status
    report["review_report"]["summary"] = summary
    report["review_report"]["recorded_at"] = _now_iso()
    _write_artifact(root_dir, run_id, "review-report.yaml", report)

    _update_pipeline_state(root_dir, run_id, PipelineState.in_progress)
    return _artifact_path(root_dir, run_id, "review-report.yaml")


def record_verification(
    *,
    root_dir: Path,
    run_id: str,
    lint: str,
    tests: str,
    type_check: str,
    build: str,
    summary: str,
) -> Path:
    report = _read_artifact(root_dir, run_id, "verification-report.yaml")
    verification = report["verification_report"]
    verification["lint"] = _verification_status(lint)
    verification["tests"] = _verification_status(tests)
    verification["type_check"] = _verification_status(type_check)
    verification["build"] = _verification_status(build)
    verification["summary"] = summary
    verification["recorded_at"] = _now_iso()
    _write_artifact(root_dir, run_id, "verification-report.yaml", report)

    _update_pipeline_state(root_dir, run_id, PipelineState.in_progress)
    return _artifact_path(root_dir, run_id, "verification-report.yaml")


def record_qa(*, root_dir: Path, run_id: str, status: str, summary: str) -> Path:
    if status not in {"pass", "fail"}:
        raise ValueError("qa status must be pass|fail")

    report = _read_artifact(root_dir, run_id, "qa-report.yaml")
    report["qa_report"]["status"] = status
    report["qa_report"]["summary"] = summary
    report["qa_report"]["recorded_at"] = _now_iso()
    _write_artifact(root_dir, run_id, "qa-report.yaml", report)

    _update_pipeline_state(root_dir, run_id, PipelineState.in_progress)
    return _artifact_path(root_dir, run_id, "qa-report.yaml")


def record_docs_sync(*, root_dir: Path, run_id: str, status: str, summary: str) -> Path:
    if status not in {"complete", "required", "not-needed"}:
        raise ValueError("docs sync status must be complete|required|not-needed")

    report = _read_artifact(root_dir, run_id, "docs-sync-report.yaml")
    report["docs_sync_report"]["status"] = status
    report["docs_sync_report"]["required"] = status != "not-needed"
    report["docs_sync_report"]["summary"] = summary
    report["docs_sync_report"]["recorded_at"] = _now_iso()
    _write_artifact(root_dir, run_id, "docs-sync-report.yaml", report)

    _set_docs_sync_verdict(root_dir, run_id, status, summary)
    _update_pipeline_state(root_dir, run_id, PipelineState.in_progress)
    return _artifact_path(root_dir, run_id, "docs-sync-report.yaml")


def build_evidence_bundle(*, root_dir: Path, run_id: str) -> Path:
    run_payload = _load_run(root_dir, run_id)
    run = run_payload["run"]

    review = _read_artifact(root_dir, run_id, "review-report.yaml")["review_report"]
    qa = _read_artifact(root_dir, run_id, "qa-report.yaml")["qa_report"]
    docs_sync = _read_artifact(root_dir, run_id, "docs-sync-report.yaml")["docs_sync_report"]
    verification = _verification_payload_or_pending(root_dir, run_id)

    existing = _read_artifact(root_dir, run_id, "evidence-bundle.yaml").get("evidence_bundle", {})
    lint = {
        "status": _verification_status(verification.get("lint", "pending")),
        "notes": str(verification.get("lint_notes", "")),
    }
    tests = {
        "status": _verification_status(verification.get("tests", "pending")),
        "notes": str(verification.get("tests_notes", "")),
    }
    type_check = {
        "status": _verification_status(verification.get("type_check", "pending")),
        "notes": str(verification.get("type_check_notes", "")),
    }
    build = {
        "status": _verification_status(verification.get("build", "pending")),
        "notes": str(verification.get("build_notes", "")),
    }

    docs_sync_status = str(docs_sync.get("status", "pending"))
    complete = (
        review.get("status") == "pass"
        and qa.get("status") == "pass"
        and lint["status"] == "pass"
        and tests["status"] == "pass"
        and type_check["status"] == "pass"
        and build["status"] == "pass"
        and _docs_sync_complete(docs_sync_status)
    )

    evidence_bundle = {
        "evidence_bundle": {
            "id": existing.get("id", f"EV-{run_id}"),
            "work_item_id": run["work_item_id"],
            "pr_id": run["pr_id"],
            "summary": (
                f"review={review.get('status', 'pending')}, "
                f"qa={qa.get('status', 'pending')}, docs_sync={docs_sync_status}, "
                f"verification={verification.get('summary', '')}"
            ),
            "checks": {
                "lint": lint,
                "tests": tests,
                "type_check": type_check,
                "build": build,
            },
            "review_findings": review.get("findings", []),
            "qa_findings": qa.get("findings", []),
            "docs_sync": {
                "required": docs_sync.get("required", True),
                "status": docs_sync_status,
                "changed_docs": docs_sync.get("changed_docs", []),
            },
            "residual_risks": existing.get("residual_risks", []),
            "status": "complete" if complete else "incomplete",
        }
    }
    _write_artifact(root_dir, run_id, "evidence-bundle.yaml", evidence_bundle)
    return _artifact_path(root_dir, run_id, "evidence-bundle.yaml")


def evaluate_gates(*, root_dir: Path, run_id: str, gates_config_path: Path | None = None) -> Path:
    if gates_config_path is None:
        gates_config_path = root_dir / "config" / "gates.yaml"

    config = read_yaml(gates_config_path)
    prerequisites = config["gates"]["merge_approval"].get("prerequisites", [])

    review = _read_artifact(root_dir, run_id, "review-report.yaml")["review_report"]
    qa = _read_artifact(root_dir, run_id, "qa-report.yaml")["qa_report"]
    docs_sync = _read_artifact(root_dir, run_id, "docs-sync-report.yaml")["docs_sync_report"]
    evidence = _read_artifact(root_dir, run_id, "evidence-bundle.yaml")["evidence_bundle"]
    verification = _verification_payload_or_pending(root_dir, run_id)

    prerequisite_results: dict[str, bool] = {}
    for prerequisite in prerequisites:
        if prerequisite == "lint_pass":
            prerequisite_results[prerequisite] = _verification_status(verification.get("lint")) == "pass"
        elif prerequisite == "test_pass":
            prerequisite_results[prerequisite] = _verification_status(verification.get("tests")) == "pass"
        elif prerequisite == "type_check_pass":
            prerequisite_results[prerequisite] = _verification_status(verification.get("type_check")) == "pass"
        elif prerequisite == "build_pass":
            prerequisite_results[prerequisite] = _verification_status(verification.get("build")) == "pass"
        elif prerequisite == "review_complete":
            prerequisite_results[prerequisite] = review.get("status") == "pass"
        elif prerequisite == "qa_complete":
            prerequisite_results[prerequisite] = qa.get("status") == "pass"
        elif prerequisite == "docs_sync_complete":
            prerequisite_results[prerequisite] = _docs_sync_complete(str(docs_sync.get("status", "pending")))
        elif prerequisite == "evidence_bundle_complete":
            prerequisite_results[prerequisite] = evidence.get("status") == "complete"
        else:
            prerequisite_results[prerequisite] = False

    has_review_or_qa_failure = review.get("status") == "fail" or qa.get("status") == "fail"
    has_verification_failure = any(
        _verification_status(verification.get(name)) == "fail" for name in ("lint", "tests", "type_check", "build")
    )

    merge_gate: str
    exception_gate = "pending"
    if has_review_or_qa_failure:
        merge_gate = "blocked"
    elif has_verification_failure:
        merge_gate = "exception_required"
        exception_gate = "required"
    elif all(prerequisite_results.values()):
        merge_gate = "ready"
    else:
        merge_gate = "pending"

    gate_status = _read_artifact(root_dir, run_id, "gate-status.yaml")
    gate_status["gate_status"]["current_state"] = PipelineState.approval_pending.value
    gate_status["gate_status"]["gates"]["merge_approval"] = merge_gate
    gate_status["gate_status"]["gates"]["exception_approval"] = exception_gate
    gate_status["gate_status"]["prerequisite_results"] = prerequisite_results
    _write_artifact(root_dir, run_id, "gate-status.yaml", gate_status)

    _record_run_operation(
        root_dir,
        run_id,
        "gate_check",
        {
            "merge_approval": merge_gate,
            "exception_approval": exception_gate,
        },
    )
    _update_pipeline_state(root_dir, run_id, PipelineState.approval_pending)
    return _artifact_path(root_dir, run_id, "gate-status.yaml")


def build_approval_request(*, root_dir: Path, run_id: str) -> tuple[Path, Path | None]:
    run_payload = _load_run(root_dir, run_id)
    run = run_payload["run"]
    _require_build_approval_prerequisites(root_dir, run_id)

    evidence_path = build_evidence_bundle(root_dir=root_dir, run_id=run_id)
    gate_path = evaluate_gates(root_dir=root_dir, run_id=run_id)

    evidence = read_yaml(evidence_path)["evidence_bundle"]
    gate = read_yaml(gate_path)["gate_status"]
    verification = _read_verification_report(root_dir, run_id)
    review = _read_artifact(root_dir, run_id, "review-report.yaml")["review_report"]
    qa = _read_artifact(root_dir, run_id, "qa-report.yaml")["qa_report"]
    docs_sync = _read_artifact(root_dir, run_id, "docs-sync-report.yaml")["docs_sync_report"]

    merge_gate = gate["gates"]["merge_approval"]
    exceptions: list[str] = []
    if merge_gate == "exception_required":
        exceptions.append("failed quality prerequisite requires exception approval")

    if review.get("status") == "fail" or qa.get("status") == "fail":
        recommended_decision = "request_changes"
    elif merge_gate == "exception_required":
        recommended_decision = "approve_with_exception"
    elif merge_gate == "ready":
        recommended_decision = "approve"
    else:
        recommended_decision = "reject"

    if not evidence:
        raise ValueError("cannot build approval request without evidence bundle")

    docs_sync_status = str(docs_sync.get("status", "pending"))
    approval = {
        "approval_request": {
            "id": f"APR-{run_id}",
            "work_item_id": run["work_item_id"],
            "pr_id": run["pr_id"],
            "gate_type": "exception_approval" if merge_gate == "exception_required" else "merge_approval",
            "decision_required": [
                "approve",
                "reject",
                "request_changes",
                "approve_with_exception",
            ],
            "summary": {
                "problem": f"PR {run['pr_id']} approval decision",
                "proposed_change": "minimal approval loop artifacts and gate evaluation",
                "user_impact": f"merge gate status={merge_gate}",
            },
            "checks": {
                "lint": _verification_status(verification.get("lint")),
                "tests": _verification_status(verification.get("tests")),
                "type_check": _verification_status(verification.get("type_check")),
                "build": _verification_status(verification.get("build")),
                "review": review.get("status", "pending"),
                "qa": qa.get("status", "pending"),
                "docs_sync": docs_sync_status,
            },
            "risks": evidence.get("residual_risks", []),
            "exceptions": exceptions,
            "changed_docs": docs_sync.get("changed_docs", []),
            "changed_files": [],
            "adr_refs": [],
            "evidence_bundle": evidence_path.as_posix(),
            "recommended_decision": recommended_decision,
        }
    }

    approval_path = _artifact_path(root_dir, run_id, "approval-request.yaml")
    _write_artifact(root_dir, run_id, "approval-request.yaml", approval)

    queue_path: Path | None = None
    docs_ready = _docs_sync_complete(docs_sync_status)
    if docs_ready and merge_gate in {"ready", "exception_required"}:
        queue_path, should_write_queue = _queue_path_for_approval(root_dir, approval)
        if should_write_queue:
            write_yaml(queue_path, approval)

    _record_run_operation(
        root_dir,
        run_id,
        "build_approval",
        {
            "recommended_decision": recommended_decision,
            "merge_approval": merge_gate,
            "queued": queue_path.as_posix() if queue_path is not None else "",
        },
    )

    _update_pipeline_state(root_dir, run_id, PipelineState.approval_pending)

    return approval_path, queue_path


def resolve_approval(*, root_dir: Path, run_id: str, decision: str, actor: str, note: str) -> tuple[Path, Path]:
    approval_path = _artifact_path(root_dir, run_id, "approval-request.yaml")
    if not approval_path.exists():
        raise ValueError(f"cannot resolve approval without approval request artifact: {approval_path.as_posix()}")

    approval_request = read_yaml(approval_path).get("approval_request", {})
    if not approval_request.get("evidence_bundle"):
        raise ValueError(
            "cannot resolve approval before build-approval creates a populated approval request artifact"
        )

    source_relative = _queue_item_relative_path("pending", run_id)
    source_path = root_dir / source_relative

    target_queue = _decision_to_queue(decision)
    target_relative = _queue_item_relative_path(target_queue, run_id)
    target_path = root_dir / target_relative
    target_path.parent.mkdir(parents=True, exist_ok=True)

    other_queues = {"approved", "rejected", "exceptions"} - {target_queue}
    already_other = [name for name in sorted(other_queues) if (root_dir / _queue_item_relative_path(name, run_id)).exists()]
    if already_other:
        locations = ", ".join(_queue_item_relative_path(name, run_id) for name in already_other)
        raise ValueError(f"approval already resolved in a different queue: {locations}")

    if source_path.exists():
        payload = read_yaml(source_path)
        if target_path.exists():
            if read_yaml(target_path) != payload:
                raise ValueError(f"target queue item already exists with different content: {target_relative}")
            source_path.unlink()
        else:
            source_path.replace(target_path)
    else:
        if not target_path.exists():
            raise ValueError(f"cannot resolve approval without pending queue item: {source_relative}")

    decision_payload = {
        "approval_decision": {
            "run_id": run_id,
            "decision": decision,
            "actor": actor,
            "note": note,
            "resolved_at": _resolved_at_now(),
            "source_queue_item": source_relative,
            "target_queue_item": target_relative,
        }
    }
    decision_path = _artifact_path(root_dir, run_id, "approval-decision.yaml")
    _write_artifact(root_dir, run_id, "approval-decision.yaml", decision_payload)

    _record_run_operation(
        root_dir,
        run_id,
        "resolve_approval",
        {
            "decision": decision,
            "actor": actor,
            "target_queue_item": target_relative,
        },
    )

    if decision == "approve":
        _update_pipeline_state(root_dir, run_id, PipelineState.approved)
    elif decision == "reject":
        _update_pipeline_state(root_dir, run_id, PipelineState.rejected)
    else:
        _update_pipeline_state(root_dir, run_id, PipelineState.approval_pending)

    return decision_path, target_path
