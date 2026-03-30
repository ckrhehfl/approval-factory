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
VALID_CLARIFICATION_DECISIONS = {"resolved", "deferred", "escalated"}
CLARIFICATION_SECTION_ORDER = (
    "Clarification ID",
    "Goal ID",
    "Title",
    "Status",
    "Category",
    "Question",
    "Suggested Resolution",
    "Escalation Required",
    "Resolution Notes",
    "Next Action",
)

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


def _normalize_markdown_section_text(value: str | None, *, default: str = "- TBD") -> list[str]:
    text = (value or "").strip()
    if not text:
        return [default]
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


def _latest_run_summary(root_dir: Path) -> dict[str, str] | None:
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
    run_id = str(latest.get("run_id", ""))
    return {
        "run_id": run_id,
        "state": str(latest.get("state", "unknown")),
        "path": (_run_root(root_dir, run_id) if run_id else latest_dir).as_posix(),
    }


def resolve_latest_run_id(root_dir: Path) -> str:
    latest = _latest_run_summary(root_dir)
    if latest is None:
        raise ValueError(
            "no latest run found under runs/latest/*/run.yaml; run start-execution first or pass --run-id <id>"
        )
    return latest["run_id"]


def _read_active_pr_summary(root_dir: Path) -> dict[str, str] | None:
    plans = sorted(_pr_active_dir(root_dir).glob("*.md"))
    if not plans:
        return None

    sections = _parse_markdown_sections(plans[0])
    return {
        "pr_id": sections.get("PR ID", plans[0].stem),
        "work_item_id": sections.get("Work Item ID", "unknown"),
        "path": plans[0].as_posix(),
    }


def _read_approval_summary(root_dir: Path, run_id: str | None) -> dict[str, str]:
    if not run_id:
        return {"status": "none"}

    approval_id = f"APR-{run_id}.yaml"
    approved_path = root_dir / "approval_queue" / "approved" / approval_id
    pending_path = root_dir / "approval_queue" / "pending" / approval_id
    decision_path = _artifact_path(root_dir, run_id, "approval-decision.yaml")

    if approved_path.exists():
        return {"status": "approved", "path": approved_path.as_posix()}
    if pending_path.exists():
        return {"status": "pending", "path": pending_path.as_posix()}
    if decision_path.exists():
        decision = read_yaml(decision_path).get("approval_decision", {}).get("decision")
        if decision == "approve":
            return {"status": "approved", "path": decision_path.as_posix()}
    return {"status": "none"}


def _approval_queue_run_id(queue_item: Path) -> str:
    match = re.fullmatch(r"APR-(.+?)(?:--r\d+)?\.yaml", queue_item.name)
    if not match:
        return queue_item.stem.removeprefix("APR-")
    return match.group(1)


def _read_approval_queue_visibility(root_dir: Path, latest_run_id: str | None) -> dict[str, Any]:
    pending_items = sorted((root_dir / "approval_queue" / "pending").glob("APR-*.yaml"))
    stale_items: list[Path] = []
    latest_run_has_pending = False

    for pending_item in pending_items:
        queue_run_id = _approval_queue_run_id(pending_item)
        if latest_run_id and queue_run_id == latest_run_id:
            latest_run_has_pending = True
            continue
        stale_items.append(pending_item)

    return {
        "pending_total": len(pending_items),
        "latest_run_id": latest_run_id,
        "latest_run_has_pending": latest_run_has_pending if latest_run_id else "unavailable",
        "stale_pending_count": len(stale_items),
        "stale_pending_run_ids": [_approval_queue_run_id(path) for path in stale_items],
        "stale_pending_paths": [path.as_posix() for path in stale_items],
    }


def _read_open_clarifications(root_dir: Path) -> list[str]:
    clarifications: list[str] = []
    for clarification_path in sorted((root_dir / "clarifications").glob("*/*.md")):
        sections = _parse_markdown_sections(clarification_path)
        if sections.get("Status") != CLARIFICATION_STATUS:
            continue
        clarifications.append(sections.get("Clarification ID", clarification_path.stem))
    return clarifications


def _dedupe_preserving_order(values: Iterable[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


def _clarification_path(root_dir: Path, goal_id: str, clarification_id: str) -> Path:
    return root_dir / "clarifications" / goal_id / f"{clarification_id}.md"


def _load_work_item_clarifications(
    root_dir: Path,
    goal_id: str,
    clarification_ids: Iterable[str] | None,
) -> list[dict[str, str]]:
    linked_clarifications: list[dict[str, str]] = []
    for clarification_id in _dedupe_preserving_order(clarification_ids or []):
        clarification_path = _clarification_path(root_dir, goal_id, clarification_id)
        if not clarification_path.exists():
            sibling_matches = sorted((root_dir / "clarifications").glob(f"*/{clarification_id}.md"))
            if sibling_matches:
                candidate_list = ", ".join(path.as_posix() for path in sibling_matches)
                raise FileNotFoundError(
                    "cannot create work item because the clarification does not exist under the requested goal: "
                    f"goal-id '{goal_id}', clarification-id '{clarification_id}'. "
                    f"Expected path: {clarification_path.as_posix()}. "
                    f"Found with a different goal at: {candidate_list}. "
                    f"Next action: use a clarification from goal '{goal_id}' or create the correct artifact first."
                )
            raise FileNotFoundError(
                "cannot create work item because the clarification artifact was not found: "
                f"goal-id '{goal_id}', clarification-id '{clarification_id}'. "
                f"Expected path: {clarification_path.as_posix()}. "
                f"Next action: check the ID or create it first with `factory create-clarification --root {root_dir.as_posix()} --goal-id {goal_id} --clarification-id {clarification_id} ...`"
            )

        sections = _parse_markdown_sections(clarification_path)
        artifact_goal_id = sections.get("Goal ID", "").strip()
        if artifact_goal_id and artifact_goal_id != goal_id:
            raise ValueError(
                "cannot create work item because the clarification goal linkage is inconsistent: "
                f"{clarification_path.as_posix()} declares Goal ID '{artifact_goal_id}', expected '{goal_id}'. "
                "Next action: fix the clarification artifact or choose a clarification that matches the work item goal."
            )

        linked_clarifications.append(
            {
                "clarification_id": sections.get("Clarification ID", clarification_id).strip() or clarification_id,
                "status": sections.get("Status", "unknown").strip() or "unknown",
            }
        )
    return linked_clarifications


def _render_related_clarifications_section(linked_clarifications: Iterable[dict[str, str]]) -> list[str]:
    entries = list(linked_clarifications)
    if not entries:
        return ["- none"]
    return [f"- {entry['clarification_id']} ({entry['status']})" for entry in entries]


def _read_required_markdown_section(path: Path, heading: str) -> str:
    sections = _parse_markdown_sections(path)
    if heading not in sections:
        raise ValueError(f"required section '## {heading}' not found in {path.as_posix()}")
    return sections[heading]


def _parse_related_clarification_ids(path: Path) -> list[str]:
    related = _read_required_markdown_section(path, "Related Clarifications")
    lines = [line.strip() for line in related.splitlines() if line.strip()]
    if not lines or lines == ["- none"]:
        return []

    clarification_ids: list[str] = []
    for line in lines:
        match = re.fullmatch(r"-\s+([^\s(]+)\s+\(([^)]+)\)", line)
        if match is None:
            raise ValueError(
                "cannot read work item readiness because the Related Clarifications section is malformed in "
                f"{path.as_posix()}: expected '- <clarification-id> (<status>)', got '{line}'"
            )
        clarification_ids.append(match.group(1).strip())
    return clarification_ids


def get_work_item_readiness(*, root_dir: Path, work_item_id: str) -> dict[str, Any]:
    work_item_path = root_dir / "docs" / "work-items" / f"{work_item_id}.md"
    if not work_item_path.exists():
        raise FileNotFoundError(
            "cannot read work item readiness because the work item artifact was not found at "
            f"{work_item_path.as_posix()}. Next action: check the work-item-id or create the artifact first."
        )

    sections = _parse_markdown_sections(work_item_path)
    goal_id = sections.get("Goal ID", "").strip()
    if not goal_id:
        raise ValueError(
            "cannot read work item readiness because the work item is missing a Goal ID section value: "
            f"{work_item_path.as_posix()}"
        )

    clarification_ids = _parse_related_clarification_ids(work_item_path)
    linked_clarifications: list[dict[str, str]] = []
    for clarification_id in clarification_ids:
        clarification_path = _clarification_path(root_dir, goal_id, clarification_id)
        if not clarification_path.exists():
            raise FileNotFoundError(
                "cannot read work item readiness because a linked clarification artifact was not found: "
                f"goal-id '{goal_id}', clarification-id '{clarification_id}', expected at "
                f"{clarification_path.as_posix()}. Next action: restore the clarification artifact or update the "
                "work item linkage."
            )
        clarification_sections = _parse_markdown_sections(clarification_path)
        status = clarification_sections.get("Status", "").strip()
        if not status:
            raise ValueError(
                "cannot read work item readiness because a linked clarification is missing Status: "
                f"{clarification_path.as_posix()}"
            )
        linked_clarifications.append(
            {
                "clarification_id": clarification_sections.get("Clarification ID", clarification_id).strip()
                or clarification_id,
                "status": status,
            }
        )

    statuses = {entry["status"] for entry in linked_clarifications}
    if not linked_clarifications:
        readiness_summary = "no-linked-clarifications"
    elif statuses.issubset({"resolved"}):
        readiness_summary = "ready"
    elif {"open", "deferred", "escalated"} & statuses:
        readiness_summary = "attention-needed"
    else:
        readiness_summary = "attention-needed"

    return {
        "work_item_id": work_item_id,
        "goal_id": goal_id,
        "linked_clarification_count": len(linked_clarifications),
        "clarifications": linked_clarifications,
        "overall_readiness_summary": readiness_summary,
        "work_item_path": work_item_path.as_posix(),
    }


def _build_readiness_context(*, root_dir: Path, work_item_id: str, pr_id: str) -> dict[str, Any]:
    readiness_source = {
        "work_item_id": work_item_id,
        "pr_id": pr_id,
    }
    try:
        readiness = get_work_item_readiness(root_dir=root_dir, work_item_id=work_item_id)
    except (FileNotFoundError, ValueError) as exc:
        return {
            "status": "unavailable",
            "reason": str(exc),
            "readiness_source": readiness_source,
        }

    return {
        "status": "available",
        "readiness_summary": readiness["overall_readiness_summary"],
        "linked_clarification_count": readiness["linked_clarification_count"],
        "linked_clarifications": readiness["clarifications"],
        "readiness_source": readiness_source,
    }


def _render_pr_plan_readiness_lines(readiness: dict[str, Any]) -> list[str]:
    lines = [
        "## Work Item Readiness",
        f"- summary: {readiness['overall_readiness_summary']}",
        f"- linked_clarification_count: {readiness['linked_clarification_count']}",
        "",
        "## Linked Clarifications",
    ]
    clarifications = readiness["clarifications"]
    if isinstance(clarifications, list) and clarifications:
        for clarification in clarifications:
            lines.append(f"- {clarification['clarification_id']} ({clarification['status']})")
    else:
        lines.append("- none")
    lines.append("")
    return lines


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
    latest_run = _latest_run_summary(root_dir)
    latest_run_id = latest_run["run_id"] if latest_run else None
    active_pr_readiness: dict[str, Any] | None = None
    if isinstance(active_pr, dict):
        work_item_id = str(active_pr.get("work_item_id", "")).strip()
        if work_item_id:
            try:
                readiness = get_work_item_readiness(root_dir=root_dir, work_item_id=work_item_id)
                active_pr_readiness = {
                    "work_item_id": readiness["work_item_id"],
                    "linked_clarification_count": readiness["linked_clarification_count"],
                    "overall_readiness_summary": readiness["overall_readiness_summary"],
                }
            except (FileNotFoundError, ValueError) as exc:
                active_pr_readiness = {
                    "work_item_id": work_item_id,
                    "error": str(exc),
                }
    return {
        "active_pr": active_pr,
        "active_pr_readiness": active_pr_readiness,
        "latest_run": latest_run,
        "approval": _read_approval_summary(root_dir, latest_run_id),
        "approval_queue": _read_approval_queue_visibility(root_dir, latest_run_id),
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
        raise ValueError(
            f"cannot build approval request for run {run_id}: missing {name} at {path.as_posix()}; "
            f"run `factory {command} --run-id {run_id}` first"
        )

    payload = read_yaml(path)[key]
    if not payload.get("recorded_at"):
        raise ValueError(
            f"cannot build approval request for run {run_id} before {command} records {name}; "
            f"run `factory {command} --run-id {run_id}` first"
        )
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

    lines = _render_clarification_lines(
        clarification_id=clarification_id,
        goal_id=goal_id,
        title=title,
        status=CLARIFICATION_STATUS,
        category=normalized_category,
        question=question,
        suggested_resolution=None,
        escalation_required="yes" if escalation else "no",
        resolution_notes=None,
        next_action=None,
    )
    clarification_path.parent.mkdir(parents=True, exist_ok=True)
    clarification_path.write_text("\n".join(lines), encoding="utf-8")
    return clarification_path


def _render_clarification_lines(
    *,
    clarification_id: str,
    goal_id: str,
    title: str,
    status: str,
    category: str,
    question: str,
    suggested_resolution: str | None,
    escalation_required: str,
    resolution_notes: str | None,
    next_action: str | None,
) -> list[str]:
    section_values = {
        "Clarification ID": clarification_id,
        "Goal ID": goal_id,
        "Title": title,
        "Status": status,
        "Category": category,
        "Question": question,
        "Suggested Resolution": suggested_resolution,
        "Escalation Required": escalation_required,
        "Resolution Notes": resolution_notes,
        "Next Action": next_action,
    }

    lines = [f"# {clarification_id}: {title}", ""]
    for heading in CLARIFICATION_SECTION_ORDER:
        lines.append(f"## {heading}")
        lines.extend(_normalize_markdown_section_text(section_values.get(heading)))
        lines.append("")
    return lines


def resolve_clarification(
    *,
    root_dir: Path,
    goal_id: str,
    clarification_id: str,
    decision: str,
    resolution_notes: str,
    next_action: str,
    suggested_resolution: str | None = None,
) -> Path:
    normalized_decision = decision.strip()
    if normalized_decision not in VALID_CLARIFICATION_DECISIONS:
        allowed = ", ".join(sorted(VALID_CLARIFICATION_DECISIONS))
        raise ValueError(f"clarification decision must be one of {allowed} (got: {normalized_decision or decision})")

    clarification_path = root_dir / "clarifications" / goal_id / f"{clarification_id}.md"
    if not clarification_path.exists():
        raise FileNotFoundError(
            "cannot resolve clarification because the artifact was not found "
            f"at {clarification_path.as_posix()} for goal-id '{goal_id}' and clarification-id '{clarification_id}'. "
            f"Next action: check the IDs or create it first with `factory create-clarification --root {root_dir.as_posix()} --goal-id {goal_id} --clarification-id {clarification_id} ...`"
        )

    sections = _parse_markdown_sections(clarification_path)
    current_status = sections.get("Status", "").strip() or "missing"
    if current_status != CLARIFICATION_STATUS:
        raise ValueError(
            "cannot resolve clarification because only open artifacts can be updated: "
            f"{clarification_path.as_posix()} currently has Status={current_status}. "
            "Next action: inspect the artifact and create a new clarification if a new open question is needed."
        )

    updated_lines = _render_clarification_lines(
        clarification_id=sections.get("Clarification ID", clarification_id),
        goal_id=sections.get("Goal ID", goal_id),
        title=sections.get("Title", clarification_id),
        status=normalized_decision,
        category=sections.get("Category", ""),
        question=sections.get("Question", ""),
        suggested_resolution=(
            suggested_resolution if suggested_resolution is not None else sections.get("Suggested Resolution", "")
        ),
        escalation_required="yes" if normalized_decision == "escalated" else "no",
        resolution_notes=resolution_notes,
        next_action=next_action,
    )
    clarification_path.write_text("\n".join(updated_lines), encoding="utf-8")
    return clarification_path


def create_work_item(
    *,
    root_dir: Path,
    work_item_id: str,
    title: str,
    goal_id: str,
    description: str,
    acceptance_criteria: str | None = None,
    clarification_ids: Iterable[str] | None = None,
) -> Path:
    work_item_path = root_dir / "docs" / "work-items" / f"{work_item_id}.md"
    if work_item_path.exists():
        raise FileExistsError(
            f"Work item artifact already exists for work-item-id '{work_item_id}': {work_item_path.as_posix()}"
        )

    acceptance_criteria_lines = _normalize_multiline_text(acceptance_criteria)
    linked_clarifications = _load_work_item_clarifications(root_dir, goal_id, clarification_ids)
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
        "## Related Clarifications",
        *_render_related_clarifications_section(linked_clarifications),
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
) -> dict[str, Any]:
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

    readiness = get_work_item_readiness(root_dir=root_dir, work_item_id=work_item_id)
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
        *_render_pr_plan_readiness_lines(readiness),
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
    return {
        "path": pr_plan_path,
        "readiness": readiness,
    }


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
            "activate-pr requires an existing PR plan artifact for "
            f"pr-id '{pr_id}', but none was found under {target_active_path.as_posix()} "
            f"or {target_archive_path.as_posix()}"
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
                "readiness_context": {
                    "status": "unavailable",
                    "reason": "source work item readiness has not been evaluated yet",
                    "readiness_source": {
                        "work_item_id": work_item_id,
                        "pr_id": pr_id,
                    },
                },
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
                "readiness_context": {
                    "status": "unavailable",
                    "reason": "source work item readiness has not been evaluated yet",
                    "readiness_source": {
                        "work_item_id": work_item_id,
                        "pr_id": pr_id,
                    },
                },
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
    readiness_context = _build_readiness_context(
        root_dir=root_dir,
        work_item_id=str(run.get("work_item_id", "")),
        pr_id=str(run.get("pr_id", "")),
    )

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
            "readiness_context": readiness_context,
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
    readiness_context = _build_readiness_context(
        root_dir=root_dir,
        work_item_id=str(run.get("work_item_id", "")),
        pr_id=str(run.get("pr_id", "")),
    )

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
            "readiness_context": readiness_context,
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
        raise ValueError(
            f"cannot resolve approval for run {run_id}: missing approval request artifact at {approval_path.as_posix()}; "
            f"run `factory build-approval --run-id {run_id}` first"
        )

    approval_request = read_yaml(approval_path).get("approval_request", {})
    if not approval_request.get("evidence_bundle"):
        raise ValueError(
            f"cannot resolve approval for run {run_id} before build-approval creates a populated approval request artifact; "
            f"run `factory build-approval --run-id {run_id}` first"
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
            raise ValueError(
                f"cannot resolve approval for run {run_id} without pending queue item: {source_relative}; "
                f"run `factory build-approval --run-id {run_id}` first"
            )

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
