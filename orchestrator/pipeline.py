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

RUN_INSPECTION_ARTIFACTS: tuple[tuple[str, str], ...] = (
    ("review", "review-report.yaml"),
    ("qa", "qa-report.yaml"),
    ("docs-sync", "docs-sync-report.yaml"),
    ("verification", "verification-report.yaml"),
    ("gate-check", "gate-status.yaml"),
    ("approval-request", "approval-request.yaml"),
    ("evidence-bundle", "evidence-bundle.yaml"),
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
CLARIFICATION_DRAFT_STATUS = "draft-only"
CLARIFICATION_STATUS = "open"
WORK_ITEM_STATUS = "draft"
WORK_ITEM_DRAFT_STATUS = "draft-only"
PR_PLAN_DRAFT_STATUS = "draft-only"
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
CLARIFICATION_OPTIONAL_SECTION_ORDER = (
    "Rationale",
    "Source Provenance",
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

RUN_ID_PATTERN = re.compile(r"RUN-[A-Z0-9][A-Z0-9-]*")
APPROVAL_ID_PATTERN = re.compile(r"APR-(RUN-[A-Z0-9][A-Z0-9-]*)")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def is_exact_run_id(value: str) -> bool:
    return bool(RUN_ID_PATTERN.fullmatch(value.strip()))


def is_exact_approval_id(value: str) -> bool:
    return bool(APPROVAL_ID_PATTERN.fullmatch(value.strip()))


def parse_hygiene_approval_queue_selector(*, run_id: str | None, approval_id: str | None) -> dict[str, str]:
    provided = [name for name, value in (("run_id", run_id), ("approval_id", approval_id)) if value is not None]
    if len(provided) != 1:
        raise ValueError("hygiene-approval-queue requires exactly one selector: --run-id <RUN-...> or --approval-id <APR-RUN-...>")

    if run_id is not None:
        normalized_run_id = run_id.strip()
        if not is_exact_run_id(normalized_run_id):
            raise ValueError(
                "hygiene-approval-queue requires an exact --run-id value in the form RUN-...; "
                "heuristic or pseudo selectors such as stale/latest are not allowed"
            )
        return {
            "selector_family": "run-id",
            "run_id": normalized_run_id,
            "approval_id": f"APR-{normalized_run_id}",
        }

    normalized_approval_id = str(approval_id).strip()
    match = APPROVAL_ID_PATTERN.fullmatch(normalized_approval_id)
    if match is None:
        raise ValueError(
            "hygiene-approval-queue requires an exact --approval-id value in the form APR-RUN-...; "
            "heuristic or pseudo selectors such as stale/latest are not allowed"
        )
    normalized_run_id = match.group(1)
    return {
        "selector_family": "approval-id",
        "run_id": normalized_run_id,
        "approval_id": normalized_approval_id,
    }


def resolve_hygiene_approval_queue_dry_run_target(
    *,
    root_dir: Path,
    selection: dict[str, str],
) -> dict[str, str]:
    approval_id = str(selection["approval_id"]).strip()
    pending_dir = root_dir / "approval_queue" / "pending"
    match_pattern = re.compile(rf"{re.escape(approval_id)}(?:--r\d+)?\.yaml")
    matches = sorted(path for path in pending_dir.glob(f"{approval_id}*.yaml") if match_pattern.fullmatch(path.name))

    if not matches:
        raise ValueError(
            "hygiene-approval-queue found no matching queue artifact under approval_queue/pending/ for "
            f"{selection['selector_family']} '{selection[selection['selector_family'].replace('-', '_')]}': {approval_id}"
        )

    if len(matches) > 1:
        match_list = ", ".join(path.as_posix() for path in matches)
        raise ValueError(
            "hygiene-approval-queue found multiple matching queue artifacts under approval_queue/pending/ for "
            f"approval-id '{approval_id}': {match_list}"
        )

    queue_item = matches[0]
    try:
        queue_item_path = queue_item.relative_to(root_dir).as_posix()
    except ValueError:
        queue_item_path = queue_item.as_posix()

    return {
        "selector_family": str(selection["selector_family"]),
        "run_id": str(selection["run_id"]),
        "approval_id": approval_id,
        "queue_item_path": queue_item_path,
    }


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


def _normalize_markdown_section_lines(value: str | None, *, default: str = "- TBD") -> list[str]:
    return [line.rstrip() for line in _normalize_markdown_section_text(value, default=default)]


def _normalize_section_lines(value: str | None) -> list[str]:
    text = (value or "").strip()
    if not text:
        return []
    return [line.strip() for line in text.splitlines() if line.strip()]


def _meaningful_goal_lines(value: str | None) -> list[str]:
    meaningful: list[str] = []
    for line in _normalize_section_lines(value):
        normalized = line.removeprefix("-").strip()
        lowered = normalized.lower()
        if lowered in {"tbd", "none", "n/a"}:
            continue
        meaningful.append(normalized)
    return meaningful


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


def _parse_clarification_draft_items(path: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("### Draft "):
            if current is not None:
                items.append(current)
            match = re.fullmatch(r"### Draft (\d+)", raw_line.strip())
            current = {"draft_index": str(int(match.group(1))) if match else ""}
            continue

        if current is None:
            continue

        if raw_line.startswith("## "):
            items.append(current)
            current = None
            continue

        if not raw_line.startswith("- "):
            continue

        key, separator, value = raw_line[2:].partition(":")
        if separator:
            current[key.strip()] = value.strip()

    if current is not None:
        items.append(current)

    return [
        item
        for item in items
        if item.get("draft_index")
        and item.get("category")
        and item.get("title")
        and item.get("question")
        and item.get("source_rule")
    ]


def _parse_work_item_draft_items(path: Path) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("### Candidate "):
            if current is not None:
                items.append(current)
            match = re.fullmatch(r"### Candidate (\d+)", raw_line.strip())
            current = {"draft_index": str(int(match.group(1))) if match else ""}
            continue

        if current is None:
            continue

        if raw_line.startswith("## "):
            items.append(current)
            current = None
            continue

        if not raw_line.startswith("- "):
            continue

        key, separator, value = raw_line[2:].partition(":")
        if separator:
            current[key.strip()] = value.strip()

    if current is not None:
        items.append(current)

    return [
        item
        for item in items
        if item.get("draft_index")
        and item.get("title")
        and item.get("summary")
        and item.get("acceptance_focus")
        and item.get("source_rule")
    ]


def _derive_pr_id_from_work_item_id(work_item_id: str) -> str:
    normalized = work_item_id.strip()
    if normalized.startswith("WI"):
        return f"PR{normalized[2:]}"
    return f"PR-{normalized}"


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


def _parse_pending_approval_run_id(queue_item: Path) -> str | None:
    match = re.fullmatch(r"APR-([A-Za-z0-9][A-Za-z0-9-]*)(?:--r\d+)?\.yaml", queue_item.name)
    if match is None:
        return None
    run_id = match.group(1).strip()
    return run_id or None


def _safe_read_approval_queue_item(queue_item: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = read_yaml(queue_item)
    except Exception as exc:  # pragma: no cover - defensive visibility fallback
        return None, f"queue item unreadable: {exc}"
    if not isinstance(payload, dict):
        return None, "queue item payload is not a mapping"
    return payload, None


def _safe_read_mapping(path: Path, *, label: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = read_yaml(path)
    except Exception as exc:  # pragma: no cover - defensive visibility fallback
        return None, f"{label} unreadable: {exc}"
    if not isinstance(payload, dict):
        return None, f"{label} payload is not a mapping"
    return payload, None


def inspect_approval_queue(root_dir: Path) -> dict[str, Any]:
    latest_run = _latest_run_summary(root_dir)
    latest_run_id = latest_run["run_id"] if latest_run else None
    pending_items = sorted((root_dir / "approval_queue" / "pending").glob("APR-*.yaml"))
    items: list[dict[str, Any]] = []
    relation_counts = {
        "latest": 0,
        "stale": 0,
        "no-latest-run": 0,
        "unparseable": 0,
    }

    for pending_item in pending_items:
        parsed_run_id = _parse_pending_approval_run_id(pending_item)
        relation = "unparseable"
        if parsed_run_id is not None:
            relation = "no-latest-run" if latest_run_id is None else ("latest" if parsed_run_id == latest_run_id else "stale")
        relation_counts[relation] += 1

        payload, payload_note = _safe_read_approval_queue_item(pending_item)
        approval_request = payload.get("approval_request", {}) if isinstance(payload, dict) else {}
        readiness_context = approval_request.get("readiness_context", {}) if isinstance(approval_request, dict) else {}
        readiness_presence = "present" if isinstance(readiness_context, dict) and readiness_context else "absent"

        matching_run_path: str | None = None
        matching_run_state: str | None = None
        matching_pr_id: str | None = None
        note_parts: list[str] = []
        if payload_note:
            note_parts.append(payload_note)

        if parsed_run_id is None:
            note_parts.append("could not parse run_id from pending approval filename")
        else:
            run_path = _run_root(root_dir, parsed_run_id) / "run.yaml"
            if run_path.exists():
                matching_run_path = run_path.as_posix()
                try:
                    run_payload = read_yaml(run_path).get("run", {})
                except Exception as exc:  # pragma: no cover - defensive visibility fallback
                    note_parts.append(f"matching run unreadable: {exc}")
                else:
                    matching_run_state = str(run_payload.get("state", "unknown"))
                    pr_id = run_payload.get("pr_id")
                    if pr_id is not None:
                        matching_pr_id = str(pr_id)
            else:
                note_parts.append(f"matching run missing from filesystem: {run_path.as_posix()}")

        items.append(
            {
                "path": pending_item.as_posix(),
                "parsed_run_id": parsed_run_id,
                "latest_relation": relation,
                "matching_run_path": matching_run_path,
                "matching_pr_id": matching_pr_id,
                "matching_run_state": matching_run_state,
                "readiness_context_presence": readiness_presence,
                "note": "; ".join(note_parts) if note_parts else None,
            }
        )

    return {
        "latest_run_id": latest_run_id,
        "latest_run_path": latest_run.get("path") if latest_run else None,
        "pending_total": len(pending_items),
        "latest_relation_summary": {
            "latest_relation_count_latest": relation_counts["latest"],
            "latest_relation_count_stale": relation_counts["stale"],
            "latest_relation_count_no_latest_run": relation_counts["no-latest-run"],
            "latest_relation_count_unparseable": relation_counts["unparseable"],
        },
        "items": items,
    }


def inspect_approval(*, root_dir: Path, run_id: str | None) -> dict[str, Any]:
    approval_path = _artifact_path(root_dir, run_id, "approval-request.yaml") if run_id else None
    evidence_path: Path | None = None
    run_path = _run_root(root_dir, run_id) / "run.yaml" if run_id else None

    notes: list[str] = []
    run_state: str | None = None
    approval_request_status: str | None = None
    readiness_summary: str | None = None

    run_exists = bool(run_path and run_path.exists())
    approval_exists = bool(approval_path and approval_path.exists())

    if run_id is None:
        notes.append("no latest run found under runs/latest/*/run.yaml")

    if run_path is not None:
        if run_exists:
            run_payload, run_note = _safe_read_mapping(run_path, label="run artifact")
            if run_note:
                notes.append(run_note)
            run = run_payload.get("run", {}) if isinstance(run_payload, dict) else {}
            if isinstance(run, dict) and run:
                run_state = str(run.get("state", "unknown"))
            elif run_exists:
                notes.append("run artifact missing run mapping")
        else:
            notes.append(f"run artifact missing: {run_path.as_posix()}")

    if approval_path is not None:
        if approval_exists:
            approval_payload, approval_note = _safe_read_mapping(approval_path, label="approval request artifact")
            if approval_note:
                notes.append(approval_note)
            approval_request = approval_payload.get("approval_request", {}) if isinstance(approval_payload, dict) else {}
            if isinstance(approval_request, dict) and approval_request:
                status = approval_request.get("status")
                if status is not None:
                    approval_request_status = str(status)
                evidence_raw = approval_request.get("evidence_bundle")
                if isinstance(evidence_raw, str) and evidence_raw.strip():
                    evidence_path = Path(evidence_raw)
                else:
                    notes.append("approval request missing evidence bundle path")
                readiness_context = approval_request.get("readiness_context", {})
                if isinstance(readiness_context, dict) and readiness_context:
                    if "readiness_summary" in readiness_context:
                        readiness_summary = str(readiness_context.get("readiness_summary"))
                    elif "status" in readiness_context:
                        readiness_summary = str(readiness_context.get("status"))
                elif approval_exists:
                    notes.append("approval request missing readiness_context summary")
            elif approval_exists:
                notes.append("approval request artifact missing approval_request mapping")
        else:
            notes.append(f"approval request artifact missing: {approval_path.as_posix()}")

    if evidence_path is None and run_id is not None:
        evidence_path = _artifact_path(root_dir, run_id, "evidence-bundle.yaml")

    evidence_exists = bool(evidence_path and evidence_path.exists())
    if evidence_path is not None:
        if evidence_exists:
            _, evidence_note = _safe_read_mapping(evidence_path, label="evidence bundle artifact")
            if evidence_note:
                notes.append(evidence_note)
        else:
            notes.append(f"evidence bundle artifact missing: {evidence_path.as_posix()}")

    return {
        "run_id": run_id,
        "run_path": run_path.as_posix() if run_path is not None else None,
        "run_exists": run_exists,
        "run_state": run_state,
        "approval_request_path": approval_path.as_posix() if approval_path is not None else None,
        "approval_request_exists": approval_exists,
        "approval_request_status": approval_request_status,
        "evidence_bundle_path": evidence_path.as_posix() if evidence_path is not None else None,
        "evidence_bundle_exists": evidence_exists,
        "readiness_summary": readiness_summary,
        "degraded_note": "; ".join(notes) if notes else None,
    }


def _inspect_run_artifact(*, root_dir: Path, run_id: str, artifact_name: str, filename: str) -> dict[str, Any]:
    artifact_path = _artifact_path(root_dir, run_id, filename)
    note_parts: list[str] = []
    status: str | None = None
    exists = artifact_path.exists()

    if exists:
        payload, payload_note = _safe_read_mapping(artifact_path, label=f"{artifact_name} artifact")
        if payload_note:
            note_parts.append(payload_note)

        if artifact_name == "review":
            review = payload.get("review_report", {}) if isinstance(payload, dict) else {}
            if isinstance(review, dict) and review:
                raw_status = review.get("status")
                if raw_status is not None:
                    status = str(raw_status)
                else:
                    note_parts.append("review artifact missing review status")
            else:
                note_parts.append("review artifact missing review_report mapping")
        elif artifact_name == "qa":
            qa = payload.get("qa_report", {}) if isinstance(payload, dict) else {}
            if isinstance(qa, dict) and qa:
                raw_status = qa.get("status")
                if raw_status is not None:
                    status = str(raw_status)
                else:
                    note_parts.append("qa artifact missing qa status")
            else:
                note_parts.append("qa artifact missing qa_report mapping")
        elif artifact_name == "docs-sync":
            docs_sync = payload.get("docs_sync_report", {}) if isinstance(payload, dict) else {}
            if isinstance(docs_sync, dict) and docs_sync:
                raw_status = docs_sync.get("status")
                if raw_status is not None:
                    status = str(raw_status)
                else:
                    note_parts.append("docs-sync artifact missing docs_sync status")
            else:
                note_parts.append("docs-sync artifact missing docs_sync_report mapping")
        elif artifact_name == "verification":
            verification = payload.get("verification_report", {}) if isinstance(payload, dict) else {}
            if isinstance(verification, dict) and verification:
                try:
                    status = ",".join(
                        [
                            f"lint={_verification_status(verification.get('lint'))}",
                            f"tests={_verification_status(verification.get('tests'))}",
                            f"type_check={_verification_status(verification.get('type_check'))}",
                            f"build={_verification_status(verification.get('build'))}",
                        ]
                    )
                except ValueError as exc:
                    note_parts.append(f"verification artifact invalid: {exc}")
            else:
                note_parts.append("verification artifact missing verification_report mapping")
        elif artifact_name == "gate-check":
            gate_status = payload.get("gate_status", {}) if isinstance(payload, dict) else {}
            if isinstance(gate_status, dict) and gate_status:
                raw_status = gate_status.get("current_state")
                if raw_status is not None:
                    status = str(raw_status)
                else:
                    note_parts.append("gate-check artifact missing current_state")
            else:
                note_parts.append("gate-check artifact missing gate_status mapping")
        elif artifact_name == "approval-request":
            approval_request = payload.get("approval_request", {}) if isinstance(payload, dict) else {}
            if isinstance(approval_request, dict) and approval_request:
                raw_status = approval_request.get("status")
                if raw_status is not None:
                    status = str(raw_status)
                else:
                    status = "none"
            else:
                note_parts.append("approval-request artifact missing approval_request mapping")
        elif artifact_name == "evidence-bundle":
            evidence_bundle = payload.get("evidence_bundle", {}) if isinstance(payload, dict) else {}
            if isinstance(evidence_bundle, dict) and evidence_bundle:
                raw_status = evidence_bundle.get("status")
                if raw_status is not None:
                    status = str(raw_status)
                else:
                    note_parts.append("evidence-bundle artifact missing evidence_bundle status")
            else:
                note_parts.append("evidence-bundle artifact missing evidence_bundle mapping")
    else:
        note_parts.append(f"{artifact_name} artifact missing: {artifact_path.as_posix()}")

    return {
        "artifact": artifact_name,
        "path": artifact_path.as_posix(),
        "exists": exists,
        "status": status,
        "note": "; ".join(note_parts) if note_parts else None,
    }


def inspect_run(*, root_dir: Path, run_id: str | None) -> dict[str, Any]:
    notes: list[str] = []
    latest_run_id: str | None = None
    latest_relation = "unavailable"
    try:
        latest_run = _latest_run_summary(root_dir)
    except Exception as exc:  # pragma: no cover - defensive visibility fallback
        latest_run = None
        notes.append(f"latest run relation unavailable: {exc}")
    else:
        latest_run_id = latest_run["run_id"] if latest_run else None
        latest_relation = "no-latest-run" if latest_run_id is None else ("latest" if run_id == latest_run_id else "non-latest")

    run_path = _run_root(root_dir, run_id) / "run.yaml" if run_id else None
    run_exists = bool(run_path and run_path.exists())
    run_state: str | None = None

    if run_id is None:
        notes.append("no latest run found under runs/latest/*/run.yaml")

    run_payload: dict[str, Any] | None = None
    if run_path is not None:
        if run_exists:
            run_payload, run_note = _safe_read_mapping(run_path, label="run artifact")
            if run_note:
                notes.append(run_note)
            run = run_payload.get("run", {}) if isinstance(run_payload, dict) else {}
            if isinstance(run, dict) and run:
                run_state = str(run.get("state", "unknown"))
            else:
                notes.append("run artifact missing run mapping")
        else:
            notes.append(f"run artifact missing: {run_path.as_posix()}")

    active_pr_relation = "unavailable"
    active_pr = _read_active_pr_summary(root_dir)
    if active_pr is None:
        active_pr_relation = "no-active-pr"
    elif run_payload is not None:
        run = run_payload.get("run", {}) if isinstance(run_payload, dict) else {}
        if isinstance(run, dict) and run:
            run_pr_id = str(run.get("pr_id", "")).strip()
            run_work_item_id = str(run.get("work_item_id", "")).strip()
            active_pr_id = str(active_pr.get("pr_id", "")).strip()
            active_work_item_id = str(active_pr.get("work_item_id", "")).strip()
            if run_pr_id and active_pr_id and run_pr_id == active_pr_id:
                active_pr_relation = "linked-by-pr"
            elif run_work_item_id and active_work_item_id and run_work_item_id == active_work_item_id:
                active_pr_relation = "linked-by-work-item"
            else:
                active_pr_relation = "unlinked"

    artifacts = [_inspect_run_artifact(root_dir=root_dir, run_id=run_id, artifact_name=name, filename=filename) for name, filename in RUN_INSPECTION_ARTIFACTS] if run_id is not None else []
    for artifact in artifacts:
        if artifact.get("note"):
            notes.append(str(artifact["note"]))

    return {
        "run_id": run_id,
        "run_path": run_path.as_posix() if run_path is not None else None,
        "run_exists": run_exists,
        "run_state": run_state,
        "latest_relation": latest_relation,
        "active_pr_relation": active_pr_relation,
        "artifacts": artifacts,
        "degraded_note": "; ".join(notes) if notes else None,
    }


def _parse_pr_plan_linked_clarifications(sections: dict[str, str], notes: list[str]) -> list[str]:
    linked = sections.get("Linked Clarifications", "").strip()
    if not linked:
        return []

    lines = [line.strip() for line in linked.splitlines() if line.strip()]
    if not lines or lines == ["- none"]:
        return []

    clarification_ids: list[str] = []
    for line in lines:
        match = re.fullmatch(r"-\s+([^\s(]+)(?:\s+\(([^)]+)\))?", line)
        if match is None:
            notes.append(f"linked clarifications section malformed: {line}")
            continue
        clarification_ids.append(match.group(1).strip())
    return clarification_ids


def _parse_pr_plan_readiness_visibility(sections: dict[str, str], notes: list[str]) -> dict[str, Any] | None:
    raw_readiness = sections.get("Work Item Readiness", "").strip()
    if not raw_readiness:
        return None

    readiness: dict[str, Any] = {"context": []}
    for line in [item.strip() for item in raw_readiness.splitlines() if item.strip()]:
        if not line.startswith("- "):
            notes.append(f"work item readiness section malformed: {line}")
            continue
        content = line[2:]
        if ":" not in content:
            notes.append(f"work item readiness entry malformed: {line}")
            continue
        key, value = content.split(":", 1)
        normalized_key = key.strip().replace("-", "_").replace(" ", "_")
        normalized_value = value.strip()
        readiness["context"].append({"label": key.strip(), "value": normalized_value})
        if normalized_key == "summary":
            readiness["summary"] = normalized_value
        elif normalized_key in {"linked_clarification_count", "linked_clarifications"}:
            readiness["linked_clarification_count"] = normalized_value
    return readiness


def _pr_plan_metadata_value(sections: dict[str, str]) -> str | None:
    for key in ("Created At", "Updated At", "Recorded At", "Created", "Updated"):
        value = sections.get(key, "").strip()
        if value:
            return value
    return None


def _parse_work_item_linked_clarifications(sections: dict[str, str], notes: list[str]) -> list[str]:
    raw_related = sections.get("Related Clarifications", "").strip()
    if not raw_related:
        return []

    lines = [line.strip() for line in raw_related.splitlines() if line.strip()]
    if not lines or lines == ["- none"]:
        return []

    clarification_ids: list[str] = []
    for line in lines:
        match = re.fullmatch(r"-\s+([^\s(]+)(?:\s+\(([^)]+)\))?", line)
        if match is None:
            notes.append(
                "work item related clarifications section malformed: "
                f"{line}"
            )
            continue
        clarification_ids.append(match.group(1).strip())
    return clarification_ids


def _clarification_locator(root_dir: Path, clarification_id: str) -> Path:
    return root_dir / "clarifications" / "*" / f"{clarification_id}.md"


def _find_clarification_artifact(root_dir: Path, clarification_id: str, notes: list[str]) -> Path | None:
    matches = sorted((root_dir / "clarifications").glob(f"*/{clarification_id}.md"))
    if not matches:
        expected_path = _clarification_locator(root_dir, clarification_id).as_posix()
        notes.append(
            "clarification artifact missing for clarification-id "
            f"'{clarification_id}': expected {expected_path}"
        )
        return None
    if len(matches) > 1:
        match_list = ", ".join(path.as_posix() for path in matches)
        notes.append(
            "clarification artifact lookup is ambiguous for clarification-id "
            f"'{clarification_id}': found {len(matches)} matches: {match_list}"
        )
        return None
    return matches[0]


def _find_linked_work_item_ids(
    root_dir: Path,
    *,
    clarification_id: str,
    goal_id: str | None,
    notes: list[str],
) -> list[str]:
    work_item_ids: list[str] = []
    for work_item_path in sorted((root_dir / "docs" / "work-items").glob("*.md")):
        try:
            sections = _parse_markdown_sections(work_item_path)
        except Exception as exc:  # pragma: no cover - defensive visibility fallback
            notes.append(f"linked work item artifact unreadable: {work_item_path.as_posix()}: {exc}")
            continue

        if not sections:
            continue

        if goal_id is not None:
            work_item_goal_id = sections.get("Goal ID", "").strip()
            if work_item_goal_id and work_item_goal_id != goal_id:
                continue

        related_notes: list[str] = []
        related_clarification_ids = _parse_work_item_linked_clarifications(sections, related_notes)
        if related_notes:
            notes.extend(f"{work_item_path.as_posix()}: {note}" for note in related_notes)
        if clarification_id not in related_clarification_ids:
            continue

        parsed_work_item_id = sections.get("Work Item ID", "").strip() or work_item_path.stem
        work_item_ids.append(parsed_work_item_id)

    return _dedupe_preserving_order(work_item_ids)


def _find_goal_linked_clarification_ids(root_dir: Path, *, goal_id: str, notes: list[str]) -> list[str]:
    clarification_dir = root_dir / "clarifications" / goal_id
    if not clarification_dir.exists():
        return []

    clarification_ids: list[str] = []
    for clarification_path in sorted(clarification_dir.glob("*.md")):
        clarification_ids.append(clarification_path.stem)
        try:
            sections = _parse_markdown_sections(clarification_path)
        except Exception as exc:  # pragma: no cover - defensive visibility fallback
            notes.append(f"linked clarification artifact unreadable: {clarification_path.as_posix()}: {exc}")
            continue

        artifact_goal_id = sections.get("Goal ID", "").strip()
        if sections and artifact_goal_id and artifact_goal_id != goal_id:
            notes.append(
                "linked clarification goal mismatch: "
                f"{clarification_path.as_posix()} declares Goal ID '{artifact_goal_id}', expected '{goal_id}'"
            )

    return _dedupe_preserving_order(clarification_ids)


def _find_goal_linked_work_item_ids(root_dir: Path, *, goal_id: str, notes: list[str]) -> list[str]:
    work_item_ids: list[str] = []
    for work_item_path in sorted((root_dir / "docs" / "work-items").glob("*.md")):
        try:
            sections = _parse_markdown_sections(work_item_path)
        except Exception as exc:  # pragma: no cover - defensive visibility fallback
            notes.append(f"linked work item artifact unreadable: {work_item_path.as_posix()}: {exc}")
            continue

        if not sections:
            continue

        work_item_goal_id = sections.get("Goal ID", "").strip()
        if work_item_goal_id != goal_id:
            continue

        parsed_work_item_id = sections.get("Work Item ID", "").strip() or work_item_path.stem
        work_item_ids.append(parsed_work_item_id)

    return _dedupe_preserving_order(work_item_ids)


def inspect_goal(*, root_dir: Path, goal_id: str) -> dict[str, Any]:
    goal_path = root_dir / "goals" / f"{goal_id}.md"
    notes: list[str] = []
    exists = goal_path.exists()
    sections: dict[str, str] = {}

    if exists:
        try:
            sections = _parse_markdown_sections(goal_path)
        except Exception as exc:  # pragma: no cover - defensive visibility fallback
            notes.append(f"goal artifact unreadable: {exc}")
            sections = {}
        else:
            if not sections:
                notes.append("goal artifact missing markdown sections")
            if "Goal ID" not in sections:
                notes.append("goal artifact missing Goal ID section")
    else:
        notes.append(f"goal artifact missing: {goal_path.as_posix()}")

    parsed_goal_id = sections.get("Goal ID", "").strip() if sections else ""
    resolved_goal_id = parsed_goal_id or goal_id

    linked_clarification_ids = (
        _find_goal_linked_clarification_ids(root_dir, goal_id=resolved_goal_id, notes=notes)
        if exists
        else []
    )
    linked_work_item_ids = (
        _find_goal_linked_work_item_ids(root_dir, goal_id=resolved_goal_id, notes=notes)
        if exists
        else []
    )

    return {
        "goal_id": resolved_goal_id,
        "goal_path": goal_path.as_posix(),
        "exists": exists,
        "title": sections.get("Title", "").strip() or None,
        "summary": sections.get("Summary", "").strip() or None,
        "status": sections.get("Status", "").strip() or None,
        "linked_clarification_ids": linked_clarification_ids,
        "linked_work_item_ids": linked_work_item_ids,
        "metadata_timestamp": _pr_plan_metadata_value(sections) if sections else None,
        "degraded_note": "; ".join(notes) if notes else None,
    }


def inspect_clarification(*, root_dir: Path, clarification_id: str) -> dict[str, Any]:
    notes: list[str] = []
    selected_path = _find_clarification_artifact(root_dir, clarification_id, notes)
    exists = bool(selected_path and selected_path.exists())
    sections: dict[str, str] = {}

    if selected_path is not None and exists:
        try:
            sections = _parse_markdown_sections(selected_path)
        except Exception as exc:  # pragma: no cover - defensive visibility fallback
            notes.append(f"clarification artifact unreadable: {exc}")
            sections = {}
        else:
            if not sections:
                notes.append("clarification artifact missing markdown sections")
            if "Clarification ID" not in sections:
                notes.append("clarification artifact missing Clarification ID section")

    parsed_clarification_id = sections.get("Clarification ID", "").strip() if sections else ""
    goal_id = sections.get("Goal ID", "").strip() if sections else ""
    linked_work_item_ids = (
        _find_linked_work_item_ids(
            root_dir,
            clarification_id=parsed_clarification_id or clarification_id,
            goal_id=goal_id or None,
            notes=notes,
        )
        if selected_path is not None and exists
        else []
    )

    return {
        "clarification_id": parsed_clarification_id or clarification_id,
        "clarification_path": (
            selected_path.as_posix()
            if selected_path is not None
            else _clarification_locator(root_dir, clarification_id).as_posix()
        ),
        "exists": exists,
        "title": sections.get("Title", "").strip() or None,
        "question": sections.get("Question", "").strip() or None,
        "summary": sections.get("Summary", "").strip() or None,
        "status": sections.get("Status", "").strip() or None,
        "goal_id": goal_id or None,
        "linked_work_item_ids": linked_work_item_ids,
        "metadata_timestamp": _pr_plan_metadata_value(sections) if sections else None,
        "degraded_note": "; ".join(notes) if notes else None,
    }


def inspect_work_item(*, root_dir: Path, work_item_id: str) -> dict[str, Any]:
    work_item_path = root_dir / "docs" / "work-items" / f"{work_item_id}.md"
    notes: list[str] = []
    exists = work_item_path.exists()
    sections: dict[str, str] = {}

    if exists:
        try:
            sections = _parse_markdown_sections(work_item_path)
        except Exception as exc:  # pragma: no cover - defensive visibility fallback
            notes.append(f"work item artifact unreadable: {exc}")
            sections = {}
        else:
            if not sections:
                notes.append("work item artifact missing markdown sections")
            if "Work Item ID" not in sections:
                notes.append("work item artifact missing Work Item ID section")
            if "Goal ID" not in sections:
                notes.append("work item artifact missing Goal ID section")
    else:
        notes.append(f"work item artifact missing: {work_item_path.as_posix()}")

    parsed_work_item_id = sections.get("Work Item ID", "").strip() if sections else ""
    title = sections.get("Title", "").strip() if sections else ""
    summary = sections.get("Summary", "").strip() if sections else ""
    goal_id = sections.get("Goal ID", "").strip() if sections else ""
    linked_clarification_ids = _parse_work_item_linked_clarifications(sections, notes) if sections else []
    metadata_timestamp = _pr_plan_metadata_value(sections) if sections else None

    readiness_visibility: dict[str, Any] | None = None
    if exists:
        try:
            readiness = get_work_item_readiness(root_dir=root_dir, work_item_id=parsed_work_item_id or work_item_id)
        except (FileNotFoundError, ValueError) as exc:
            notes.append(str(exc))
        else:
            readiness_visibility = {
                "summary": readiness["overall_readiness_summary"],
                "linked_clarification_count": readiness["linked_clarification_count"],
                "context": readiness["clarifications"],
            }

    return {
        "work_item_id": parsed_work_item_id or work_item_id,
        "work_item_path": work_item_path.as_posix(),
        "exists": exists,
        "title": title or None,
        "summary": summary or None,
        "goal_id": goal_id or None,
        "linked_clarification_ids": linked_clarification_ids,
        "readiness_visibility": readiness_visibility,
        "metadata_timestamp": metadata_timestamp,
        "degraded_note": "; ".join(notes) if notes else None,
    }


def inspect_pr_plan(*, root_dir: Path, pr_id: str | None = None, active: bool = False) -> dict[str, Any]:
    notes: list[str] = []
    selected_path: Path | None = None
    active_relation = "unknown"

    if active:
        plans = sorted(_pr_active_dir(root_dir).glob("*.md"))
        if not plans:
            active_relation = "no-active-pr"
            notes.append("no active PR plan found under prs/active/*.md")
        elif len(plans) > 1:
            active_relation = "ambiguous-active"
            plan_list = ", ".join(path.as_posix() for path in plans)
            notes.append(f"prs/active/ must contain exactly one active PR plan for --active inspection; found {len(plans)}: {plan_list}")
        else:
            selected_path = plans[0]
            active_relation = "active"
            pr_id = pr_id or selected_path.stem
    elif pr_id is not None:
        active_path = _pr_active_dir(root_dir) / f"{pr_id}.md"
        archive_path = _pr_archive_dir(root_dir) / f"{pr_id}.md"
        active_exists = active_path.exists()
        archive_exists = archive_path.exists()
        if active_exists and archive_exists:
            selected_path = active_path
            active_relation = "duplicate-active-and-archive"
            notes.append(
                "PR plan artifact exists in both active and archive; preferring active for inspection: "
                f"{active_path.as_posix()}, {archive_path.as_posix()}"
            )
        elif active_exists:
            selected_path = active_path
            active_relation = "active"
        elif archive_exists:
            selected_path = archive_path
            active_relation = "archived"
        else:
            active_relation = "not-found"
            notes.append(
                "PR plan artifact missing for pr-id "
                f"'{pr_id}': expected {active_path.as_posix()} or {archive_path.as_posix()}"
            )

    exists = bool(selected_path and selected_path.exists())
    sections: dict[str, str] = {}
    if selected_path is not None and exists:
        try:
            sections = _parse_markdown_sections(selected_path)
        except Exception as exc:  # pragma: no cover - defensive visibility fallback
            notes.append(f"PR plan artifact unreadable: {exc}")
            sections = {}
        else:
            if not sections:
                notes.append("PR plan artifact missing markdown sections")
            if "PR ID" not in sections:
                notes.append("PR plan artifact missing PR ID section")
            if "Work Item ID" not in sections:
                notes.append("PR plan artifact missing Work Item ID section")

    parsed_pr_id = sections.get("PR ID", "").strip() if sections else ""
    work_item_id = sections.get("Work Item ID", "").strip() if sections else ""
    source_goal_id = (
        sections.get("Source Goal ID", "").strip()
        or sections.get("Goal ID", "").strip()
        or sections.get("Source Goal", "").strip()
    )
    source_work_item_id = (
        sections.get("Source Work Item ID", "").strip()
        or work_item_id
        or sections.get("Work Item ID", "").strip()
    )
    linked_clarification_ids = _parse_pr_plan_linked_clarifications(sections, notes) if sections else []
    readiness_visibility = _parse_pr_plan_readiness_visibility(sections, notes) if sections else None
    metadata_value = _pr_plan_metadata_value(sections) if sections else None

    return {
        "pr_id": parsed_pr_id or pr_id,
        "plan_path": selected_path.as_posix() if selected_path is not None else None,
        "exists": exists,
        "active_relation": active_relation,
        "source_goal_id": source_goal_id or None,
        "source_work_item_id": source_work_item_id or None,
        "linked_clarification_ids": linked_clarification_ids,
        "readiness_visibility": readiness_visibility,
        "metadata_timestamp": metadata_value,
        "degraded_note": "; ".join(notes) if notes else None,
    }


def _collect_degraded_notes(note: str | None, sink: list[str]) -> None:
    if not note:
        return
    for item in [part.strip() for part in note.split(";")]:
        if item:
            sink.append(item)


def trace_lineage(*, root_dir: Path, run_id: str | None) -> dict[str, Any]:
    notes: list[str] = []
    approval_inspection = inspect_approval(root_dir=root_dir, run_id=run_id)
    _collect_degraded_notes(approval_inspection.get("degraded_note"), notes)

    run_pr_id: str | None = None
    run_work_item_id: str | None = None
    run_path = _run_root(root_dir, run_id) / "run.yaml" if run_id is not None else None
    run_state: str | None = None
    if run_id is not None:
        if run_path is not None and run_path.exists():
            run_payload, run_note = _safe_read_mapping(run_path, label="run artifact")
            if run_note:
                notes.append(run_note)
            run_mapping = run_payload.get("run", {}) if isinstance(run_payload, dict) else {}
            if isinstance(run_mapping, dict) and run_mapping:
                raw_run_state = str(run_mapping.get("state", "")).strip()
                raw_pr_id = str(run_mapping.get("pr_id", "")).strip()
                raw_work_item_id = str(run_mapping.get("work_item_id", "")).strip()
                run_state = raw_run_state or None
                run_pr_id = raw_pr_id or None
                run_work_item_id = raw_work_item_id or None
            else:
                notes.append("run artifact missing run mapping")
            if run_pr_id is None:
                notes.append("run artifact missing pr_id linkage")
            if run_work_item_id is None:
                notes.append("run artifact missing work_item_id linkage")
        elif run_path is not None:
            notes.append(f"run artifact missing: {run_path.as_posix()}")
    else:
        notes.append("no latest run found under runs/latest/*/run.yaml")

    pr_plan_inspection: dict[str, Any] | None = None
    pr_id = run_pr_id
    if pr_id:
        pr_plan_inspection = inspect_pr_plan(root_dir=root_dir, pr_id=pr_id)
        _collect_degraded_notes(pr_plan_inspection.get("degraded_note"), notes)
    elif run_id is not None:
        notes.append("PR plan linkage unavailable because run artifact did not yield pr_id")

    work_item_inspection: dict[str, Any] | None = None
    work_item_id = run_work_item_id
    if work_item_id is None and isinstance(pr_plan_inspection, dict):
        derived_work_item_id = str(pr_plan_inspection.get("source_work_item_id") or "").strip()
        work_item_id = derived_work_item_id or None
        if work_item_id:
            notes.append("work item linkage derived from PR plan because run artifact did not yield work_item_id")
    if work_item_id:
        work_item_inspection = inspect_work_item(root_dir=root_dir, work_item_id=work_item_id)
        _collect_degraded_notes(work_item_inspection.get("degraded_note"), notes)
    elif run_id is not None:
        notes.append("work item linkage unavailable because no source work_item_id was derivable")

    queue_path: str | None = None
    queue_status: str | None = None
    if run_id:
        queue_candidates = (
            ("pending", root_dir / "approval_queue" / "pending" / f"APR-{run_id}.yaml"),
            ("approved", root_dir / "approval_queue" / "approved" / f"APR-{run_id}.yaml"),
            ("rejected", root_dir / "approval_queue" / "rejected" / f"APR-{run_id}.yaml"),
            ("exception", root_dir / "approval_queue" / "exceptions" / f"APR-{run_id}.yaml"),
        )
        for candidate_status, candidate_path in queue_candidates:
            if candidate_path.exists():
                queue_path = candidate_path.as_posix()
                queue_status = candidate_status
                break

    goal_id = str((work_item_inspection or {}).get("goal_id") or "").strip() or None
    goal_path: str | None = None
    if goal_id:
        candidate_goal_path = root_dir / "goals" / f"{goal_id}.md"
        if candidate_goal_path.exists():
            goal_path = candidate_goal_path.as_posix()
        else:
            goal_path = candidate_goal_path.as_posix()
            notes.append(f"goal artifact missing: {candidate_goal_path.as_posix()}")
    elif work_item_inspection is not None:
        notes.append("goal linkage unavailable because work item artifact did not yield goal_id")

    linked_clarification_ids: list[str] = []
    if isinstance(pr_plan_inspection, dict):
        linked_clarification_ids.extend(pr_plan_inspection.get("linked_clarification_ids") or [])
    if isinstance(work_item_inspection, dict):
        linked_clarification_ids.extend(work_item_inspection.get("linked_clarification_ids") or [])
    clarification_ids = _dedupe_preserving_order([str(item) for item in linked_clarification_ids])
    if not clarification_ids and run_id is not None:
        if pr_plan_inspection is None and work_item_inspection is None:
            notes.append("clarification linkage unavailable because PR plan and work item links were not derivable")
        else:
            notes.append("no linked clarification ids were derivable from the available artifacts")

    return {
        "run": {
            "run_id": run_id,
            "run_path": run_path.as_posix() if run_path is not None else None,
            "run_state": run_state,
        },
        "approval": {
            "approval_request_path": approval_inspection.get("approval_request_path"),
            "approval_request_status": approval_inspection.get("approval_request_status"),
            "queue_path": queue_path,
            "queue_status": queue_status,
        },
        "pr_plan": {
            "pr_id": (pr_plan_inspection or {}).get("pr_id") or pr_id,
            "plan_path": (pr_plan_inspection or {}).get("plan_path"),
            "active_relation": (pr_plan_inspection or {}).get("active_relation"),
        },
        "work_item": {
            "work_item_id": (work_item_inspection or {}).get("work_item_id") or work_item_id,
            "work_item_path": (work_item_inspection or {}).get("work_item_path"),
            "readiness_visibility": (work_item_inspection or {}).get("readiness_visibility"),
        },
        "goal": {
            "goal_id": goal_id,
            "goal_path": goal_path,
        },
        "clarifications": {
            "linked_clarification_ids": clarification_ids,
        },
        "degraded_notes": _dedupe_preserving_order(notes),
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


def _classify_clarification_category(question: str) -> str:
    lowered = question.lower()
    if any(token in lowered for token in ("approve", "approval", "sign-off", "exception", "decision")):
        return "approval-required"
    if any(token in lowered for token in ("dependency", "dependencies", "external", "vendor", "integration", "api")):
        return "dependency"
    if any(token in lowered for token in ("design", "architecture", "schema", "interface", "model")):
        return "design"
    if any(token in lowered for token in ("constraint", "limit", "budget", "cost", "latency", "security")):
        return "constraint"
    return "scope"


def _draft_title_from_question(question: str) -> str:
    text = question.strip().rstrip("?.!").strip()
    if not text:
        return "Clarification needed"
    if len(text) <= 72:
        return text[0].upper() + text[1:]
    truncated = text[:69].rstrip()
    if " " in truncated:
        truncated = truncated.rsplit(" ", 1)[0]
    return (truncated or text[:69]).rstrip(" -") + "..."


def _derive_clarification_draft_items(goal_sections: dict[str, str]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []

    if not _meaningful_goal_lines(goal_sections.get("Non-Goals")):
        question = "What is explicitly out of scope for this goal?"
        items.append(
            {
                "category": "scope",
                "title": "Clarify explicit non-goals",
                "question": question,
                "source": "Non-Goals section is missing or still TBD.",
                "escalation_required": "no",
            }
        )

    if not _meaningful_goal_lines(goal_sections.get("Constraints")):
        question = "Which constraints are fixed for this goal and cannot be relaxed?"
        items.append(
            {
                "category": "constraint",
                "title": "Clarify fixed constraints",
                "question": question,
                "source": "Constraints section is missing or still TBD.",
                "escalation_required": "no",
            }
        )

    if not _meaningful_goal_lines(goal_sections.get("Success Criteria")):
        question = "What observable success criteria define done for this goal?"
        items.append(
            {
                "category": "scope",
                "title": "Clarify success criteria",
                "question": question,
                "source": "Success Criteria section is missing or still TBD.",
                "escalation_required": "no",
            }
        )

    for entry in _meaningful_goal_lines(goal_sections.get("Open Questions")):
        normalized_question = entry if entry.endswith("?") else f"{entry}?"
        items.append(
            {
                "category": _classify_clarification_category(normalized_question),
                "title": _draft_title_from_question(normalized_question),
                "question": normalized_question,
                "source": "Derived from Goal/Open Questions.",
                "escalation_required": "no",
            }
        )

    for entry in _meaningful_goal_lines(goal_sections.get("Approval-Required Decisions")):
        normalized_question = f"What approval decision is required for: {entry}?"
        items.append(
            {
                "category": "approval-required",
                "title": _draft_title_from_question(entry),
                "question": normalized_question,
                "source": "Derived from Goal/Approval-Required Decisions.",
                "escalation_required": "yes",
            }
        )

    deduped: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        key = (item["category"], item["question"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def _normalize_inline_markdown_value(value: str | None, *, default: str) -> str:
    text = str(value or "").strip()
    if not text:
        return default
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    return first_line or default


def _load_official_clarification_draft_sources(root_dir: Path, goal_id: str) -> list[dict[str, str]]:
    clarifications_dir = root_dir / "clarifications" / goal_id
    sources: list[dict[str, str]] = []
    for clarification_path in sorted(clarifications_dir.glob("*.md")):
        sections = _parse_markdown_sections(clarification_path)
        clarification_id = sections.get("Clarification ID", "").strip() or clarification_path.stem
        status = sections.get("Status", "").strip() or "unknown"
        title = _normalize_inline_markdown_value(sections.get("Title"), default=clarification_id)
        question = _normalize_inline_markdown_value(
            sections.get("Question"),
            default=f"Review official clarification {clarification_id}.",
        )
        sources.append(
            {
                "clarification_id": clarification_id,
                "status": status,
                "title": title,
                "question": question,
                "path": clarification_path.as_posix(),
            }
        )
    return sources


def _derive_work_item_draft_candidates(
    goal_sections: dict[str, str],
    clarification_sources: list[dict[str, str]],
) -> list[dict[str, str]]:
    goal_title = _normalize_inline_markdown_value(goal_sections.get("Title"), default="goal")
    candidates: list[dict[str, str]] = []
    for source in clarification_sources:
        clarification_id = source["clarification_id"]
        clarification_status = source["status"]
        title = f"{source['title']} implementation"
        summary = (
            f"Prepare the smallest work item for {clarification_id} under goal '{goal_title}' "
            f"using the official clarification as the source of truth."
        )
        acceptance_focus = (
            f"Operator can create one official work item linked to {clarification_id} "
            f"without changing readiness, approval, queue, selector, active PR, or lifecycle semantics."
        )
        source_rule = (
            "Derived from official clarification Title/Question/Status. "
            f"Current clarification status: {clarification_status}."
        )
        candidates.append(
            {
                "title": title,
                "summary": summary,
                "acceptance_focus": acceptance_focus,
                "source_clarification_id": clarification_id,
                "source_clarification_status": clarification_status,
                "source_clarification_path": source["path"],
                "source_rule": source_rule,
            }
        )
    return candidates


def draft_clarifications(*, root_dir: Path, goal_id: str) -> Path:
    goal_path = root_dir / "goals" / f"{goal_id}.md"
    if not goal_path.exists():
        raise FileNotFoundError(
            "cannot draft clarifications because the goal artifact was not found "
            f"at {goal_path.as_posix()} for goal-id '{goal_id}'. "
            f"Next action: create it first with `factory create-goal --root {root_dir.as_posix()} --goal-id {goal_id} ...`"
        )

    draft_path = root_dir / "clarification_drafts" / f"{goal_id}.md"
    if draft_path.exists():
        raise FileExistsError(
            "clarification draft artifact already exists "
            f"for goal-id '{goal_id}': {draft_path.as_posix()}"
        )

    sections = _parse_markdown_sections(goal_path)
    goal_title = sections.get("Title", "").strip() or goal_id
    draft_items = _derive_clarification_draft_items(sections)

    lines = [
        f"# Clarification Draft: {goal_id}",
        "",
        "## Goal ID",
        goal_id,
        "",
        "## Goal Title",
        goal_title,
        "",
        "## Source Goal",
        goal_path.as_posix(),
        "",
        "## Draft Status",
        CLARIFICATION_DRAFT_STATUS,
        "",
        "## Draft Method",
        "deterministic-rule-based",
        "",
        "## Operator Notes",
        "- This file is a local drafting aid only.",
        "- It does not create or update official clarification queue artifacts.",
        "- Promote items manually into `clarifications/<goal-id>/` only when the operator decides to do so.",
        "",
        "## Suggested Clarifications",
    ]

    if draft_items:
        for index, item in enumerate(draft_items, start=1):
            lines.extend(
                [
                    "",
                    f"### Draft {index:02d}",
                    f"- category: {item['category']}",
                    f"- title: {item['title']}",
                    f"- question: {item['question']}",
                    f"- escalation_required: {item['escalation_required']}",
                    f"- source_rule: {item['source']}",
                ]
            )
    else:
        lines.extend(["", "- No clarification prompts were derived from the current goal artifact."])

    lines.extend(
        [
            "",
            "## Promotion Guidance",
            "- Review each draft item manually.",
            "- Create official clarification artifacts only with `factory create-clarification`.",
            "- This draft file never changes readiness, approval, queue, selector, or lifecycle semantics.",
            "",
        ]
    )

    draft_path.parent.mkdir(parents=True, exist_ok=True)
    draft_path.write_text("\n".join(lines), encoding="utf-8")
    return draft_path


def draft_work_items(*, root_dir: Path, goal_id: str) -> Path:
    goal_path = root_dir / "goals" / f"{goal_id}.md"
    if not goal_path.exists():
        raise FileNotFoundError(
            "cannot draft work items because the goal artifact was not found "
            f"at {goal_path.as_posix()} for goal-id '{goal_id}'. "
            f"Next action: create it first with `factory create-goal --root {root_dir.as_posix()} --goal-id {goal_id} ...`"
        )

    draft_path = root_dir / "work_item_drafts" / f"{goal_id}.md"
    if draft_path.exists():
        raise FileExistsError(
            "work item draft artifact already exists "
            f"for goal-id '{goal_id}': {draft_path.as_posix()}"
        )

    sections = _parse_markdown_sections(goal_path)
    goal_title = sections.get("Title", "").strip() or goal_id
    clarification_sources = _load_official_clarification_draft_sources(root_dir, goal_id)
    draft_candidates = _derive_work_item_draft_candidates(sections, clarification_sources)

    lines = [
        f"# Work Item Draft: {goal_id}",
        "",
        "## Goal ID",
        goal_id,
        "",
        "## Goal Title",
        goal_title,
        "",
        "## Source Goal",
        goal_path.as_posix(),
        "",
        "## Source Clarifications",
    ]

    if clarification_sources:
        for source in clarification_sources:
            lines.append(f"- {source['clarification_id']} ({source['status']}): {source['path']}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Draft Status",
            WORK_ITEM_DRAFT_STATUS,
            "",
            "## Draft Method",
            "deterministic-rule-based",
            "",
            "## Operator Notes",
            "- This file is a local drafting aid only.",
            "- Official clarification artifacts under `clarifications/<goal-id>/` are the source of truth for candidate generation.",
            "- This command never reads `clarification_drafts/`.",
            "- It does not create or update official work item artifacts under `docs/work-items/`.",
            "",
            "## Candidate Work Items",
        ]
    )

    if draft_candidates:
        for index, item in enumerate(draft_candidates, start=1):
            lines.extend(
                [
                    "",
                    f"### Candidate {index:02d}",
                    f"- title: {item['title']}",
                    f"- source_clarification_id: {item['source_clarification_id']}",
                    f"- source_clarification_status: {item['source_clarification_status']}",
                    f"- source_clarification_path: {item['source_clarification_path']}",
                    f"- summary: {item['summary']}",
                    f"- acceptance_focus: {item['acceptance_focus']}",
                    f"- source_rule: {item['source_rule']}",
                ]
            )
    else:
        lines.extend(["", "- No work item candidates were derived from official clarification artifacts for this goal."])

    lines.extend(
        [
            "",
            "## Promotion Guidance",
            "- Review each candidate manually.",
            "- Create official work item artifacts only with `factory create-work-item`.",
            "- This draft file never changes readiness, approval, queue, selector, active PR, or lifecycle semantics.",
            "",
        ]
    )

    draft_path.parent.mkdir(parents=True, exist_ok=True)
    draft_path.write_text("\n".join(lines), encoding="utf-8")
    return draft_path


def draft_pr_plan(*, root_dir: Path, work_item_id: str) -> Path:
    work_item_path = root_dir / "docs" / "work-items" / f"{work_item_id}.md"
    if not work_item_path.exists():
        raise FileNotFoundError(
            "cannot draft PR plan because the official work item artifact was not found "
            f"at {work_item_path.as_posix()} for work-item-id '{work_item_id}'. "
            f"Next action: create it first with `factory create-work-item --root {root_dir.as_posix()} --work-item-id {work_item_id} ...`"
        )

    draft_path = root_dir / "pr_plan_drafts" / f"{work_item_id}.md"
    if draft_path.exists():
        raise FileExistsError(
            "PR plan draft artifact already exists "
            f"for work-item-id '{work_item_id}': {draft_path.as_posix()}"
        )

    sections = _parse_markdown_sections(work_item_path)
    goal_id = sections.get("Goal ID", "").strip() or "unknown"
    title = sections.get("Title", "").strip() or work_item_id
    description_lines = _normalize_markdown_section_lines(sections.get("Description"))
    related_clarification_lines = _normalize_markdown_section_lines(
        sections.get("Related Clarifications"),
        default="- none",
    )
    scope_lines = _normalize_markdown_section_lines(sections.get("Scope"))
    out_of_scope_lines = _normalize_markdown_section_lines(sections.get("Out of Scope"))
    acceptance_lines = _normalize_markdown_section_lines(sections.get("Acceptance Criteria"), default="TBD")
    dependency_lines = _normalize_markdown_section_lines(sections.get("Dependencies"))
    risk_lines = _normalize_markdown_section_lines(sections.get("Risks"))
    note_lines = _normalize_markdown_section_lines(sections.get("Notes"))

    lines = [
        f"# PR Plan Draft: {work_item_id}",
        "",
        "## Work Item ID",
        work_item_id,
        "",
        "## Goal ID",
        goal_id,
        "",
        "## Work Item Title",
        title,
        "",
        "## Source Work Item",
        work_item_path.as_posix(),
        "",
        "## Draft Status",
        PR_PLAN_DRAFT_STATUS,
        "",
        "## Draft Method",
        "deterministic-rule-based",
        "",
        "## Operator Notes",
        "- This file is a local drafting aid only.",
        "- The official work item artifact under `docs/work-items/` is the source of truth for draft generation.",
        "- This command never reads `work_item_drafts/`.",
        "- It does not create or update `prs/active/` or `prs/archive/`.",
        "",
        "## Suggested PR Title",
        title,
        "",
        "## Suggested PR Summary",
        f"Implement {work_item_id} using the official work item artifact as the source of truth.",
        "",
        "## Source Description",
        *description_lines,
        "",
        "## Linked Clarifications",
        *related_clarification_lines,
        "",
        "## Scope Seed",
        *scope_lines,
        "",
        "## Out of Scope Seed",
        *out_of_scope_lines,
        "",
        "## Acceptance Seed",
        *acceptance_lines,
        "",
        "## Dependency Seed",
        *dependency_lines,
        "",
        "## Risk Seed",
        *risk_lines,
        "",
        "## Note Seed",
        *note_lines,
        "",
        "## Promotion Guidance",
        "- Review this draft manually.",
        "- Create the official PR plan only with `factory create-pr-plan`.",
        "- This draft file never changes readiness, approval, queue, selector, active PR, or lifecycle semantics.",
        "",
    ]

    draft_path.parent.mkdir(parents=True, exist_ok=True)
    draft_path.write_text("\n".join(lines), encoding="utf-8")
    return draft_path


def _render_pr_plan_promotion_notes(*, acceptance_seed: str | None, dependency_seed: str | None, note_seed: str | None) -> str:
    lines: list[str] = []
    for line in _meaningful_goal_lines(acceptance_seed):
        lines.append(f"- validation intent: {line}")
    for line in _meaningful_goal_lines(dependency_seed):
        lines.append(f"- dependency seed: {line}")
    for line in _meaningful_goal_lines(note_seed):
        lines.append(f"- note seed: {line}")
    return "\n".join(lines) if lines else "- TBD"


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


def promote_clarification_draft(
    *,
    root_dir: Path,
    goal_id: str,
    draft_index: int,
    clarification_id: str,
) -> Path:
    draft_path = root_dir / "clarification_drafts" / f"{goal_id}.md"
    if not draft_path.exists():
        raise FileNotFoundError(
            "cannot promote clarification draft because the draft artifact was not found "
            f"at {draft_path.as_posix()} for goal-id '{goal_id}'. "
            f"Next action: create it first with `factory draft-clarifications --root {root_dir.as_posix()} --goal-id {goal_id}`"
        )

    draft_items = _parse_clarification_draft_items(draft_path)
    selected_item = next((item for item in draft_items if int(item["draft_index"]) == draft_index), None)
    if selected_item is None:
        available_indexes = ", ".join(item["draft_index"] for item in draft_items) or "none"
        raise IndexError(
            "cannot promote clarification draft because the requested draft index was not found "
            f"in {draft_path.as_posix()} for goal-id '{goal_id}': draft-index '{draft_index}'. "
            f"Available indexes: {available_indexes}"
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
        title=selected_item["title"],
        status=CLARIFICATION_STATUS,
        category=selected_item["category"],
        question=selected_item["question"],
        suggested_resolution=None,
        escalation_required=selected_item.get("escalation_required", "no"),
        resolution_notes=None,
        next_action=None,
        rationale=selected_item["source_rule"],
        source_provenance="\n".join(
            [
                f"- draft_path: {draft_path.as_posix()}",
                f"- draft_index: {draft_index}",
            ]
        ),
    )
    clarification_path.parent.mkdir(parents=True, exist_ok=True)
    clarification_path.write_text("\n".join(lines), encoding="utf-8")
    return clarification_path


def promote_work_item_draft(
    *,
    root_dir: Path,
    goal_id: str,
    draft_index: int,
    work_item_id: str,
) -> Path:
    draft_path = root_dir / "work_item_drafts" / f"{goal_id}.md"
    if not draft_path.exists():
        raise FileNotFoundError(
            "cannot promote work item draft because the draft artifact was not found "
            f"at {draft_path.as_posix()} for goal-id '{goal_id}'. "
            f"Next action: create it first with `factory draft-work-items --root {root_dir.as_posix()} --goal-id {goal_id}`"
        )

    draft_items = _parse_work_item_draft_items(draft_path)
    selected_item = next((item for item in draft_items if int(item["draft_index"]) == draft_index), None)
    if selected_item is None:
        available_indexes = ", ".join(item["draft_index"] for item in draft_items) or "none"
        raise IndexError(
            "cannot promote work item draft because the requested draft index was not found "
            f"in {draft_path.as_posix()} for goal-id '{goal_id}': draft-index '{draft_index}'. "
            f"Available indexes: {available_indexes}"
        )

    work_item_path = root_dir / "docs" / "work-items" / f"{work_item_id}.md"
    if work_item_path.exists():
        raise FileExistsError(
            f"Work item artifact already exists for work-item-id '{work_item_id}': {work_item_path.as_posix()}"
        )

    source_clarification_id = selected_item.get("source_clarification_id", "").strip()
    clarification_ids = [source_clarification_id] if source_clarification_id and source_clarification_id != "none" else []
    return create_work_item(
        root_dir=root_dir,
        work_item_id=work_item_id,
        title=selected_item["title"],
        goal_id=goal_id,
        description=selected_item["summary"],
        acceptance_criteria=selected_item["acceptance_focus"],
        clarification_ids=clarification_ids,
    )


def promote_pr_plan_draft(
    *,
    root_dir: Path,
    work_item_id: str,
) -> dict[str, Any]:
    draft_path = root_dir / "pr_plan_drafts" / f"{work_item_id}.md"
    if not draft_path.exists():
        raise FileNotFoundError(
            "cannot promote PR plan draft because the draft artifact was not found "
            f"at {draft_path.as_posix()} for work-item-id '{work_item_id}'. "
            f"Next action: create it first with `factory draft-pr-plan --root {root_dir.as_posix()} --work-item-id {work_item_id}`"
        )

    sections = _parse_markdown_sections(draft_path)
    draft_work_item_id = sections.get("Work Item ID", "").strip()
    if draft_work_item_id and draft_work_item_id != work_item_id:
        raise ValueError(
            "cannot promote PR plan draft because the draft artifact does not match the requested work-item-id: "
            f"{draft_path.as_posix()} declares '{draft_work_item_id}', requested '{work_item_id}'."
        )

    return create_pr_plan(
        root_dir=root_dir,
        pr_id=_derive_pr_id_from_work_item_id(work_item_id),
        work_item_id=work_item_id,
        title=(sections.get("Suggested PR Title", "").strip() or sections.get("Work Item Title", "").strip() or work_item_id),
        summary=(
            sections.get("Suggested PR Summary", "").strip()
            or sections.get("Source Description", "").strip()
            or f"Implement {work_item_id}."
        ),
        scope=sections.get("Scope Seed"),
        out_of_scope=sections.get("Out of Scope Seed"),
        implementation_notes=_render_pr_plan_promotion_notes(
            acceptance_seed=sections.get("Acceptance Seed"),
            dependency_seed=sections.get("Dependency Seed"),
            note_seed=sections.get("Note Seed"),
        ),
        risks=sections.get("Risk Seed"),
    )


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
    rationale: str | None = None,
    source_provenance: str | None = None,
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
    optional_section_values = {
        "Rationale": rationale,
        "Source Provenance": source_provenance,
    }

    lines = [f"# {clarification_id}: {title}", ""]
    for heading in CLARIFICATION_SECTION_ORDER:
        lines.append(f"## {heading}")
        lines.extend(_normalize_markdown_section_text(section_values.get(heading)))
        lines.append("")
    for heading in CLARIFICATION_OPTIONAL_SECTION_ORDER:
        value = optional_section_values.get(heading)
        if value is None or not str(value).strip():
            continue
        lines.append(f"## {heading}")
        lines.extend(_normalize_markdown_section_text(value))
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
        rationale=sections.get("Rationale"),
        source_provenance=sections.get("Source Provenance"),
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
    scope: str | None = None,
    out_of_scope: str | None = None,
    implementation_notes: str | None = None,
    risks: str | None = None,
    open_questions: str | None = None,
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
    scope_lines = _normalize_markdown_section_lines(scope)
    out_of_scope_lines = _normalize_markdown_section_lines(out_of_scope)
    implementation_note_lines = _normalize_markdown_section_lines(implementation_notes)
    risk_lines = _normalize_markdown_section_lines(risks)
    open_question_lines = _normalize_markdown_section_lines(open_questions)

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
        *scope_lines,
        "",
        "## Out of Scope",
        *out_of_scope_lines,
        "",
        "## Implementation Notes",
        *implementation_note_lines,
        "",
        "## Risks",
        *risk_lines,
        "",
        "## Open Questions",
        *open_question_lines,
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
