from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable

from orchestrator.models import RunRecord
from orchestrator.yaml_io import read_yaml, write_yaml


class PipelineState(StrEnum):
    draft = "draft"
    planned = "planned"
    in_progress = "in_progress"
    review = "review"
    qa = "qa"
    docs_sync = "docs_sync"
    approval_pending = "approval_pending"
    approved = "approved"
    merged = "merged"
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


def _run_root(root_dir: Path, run_id: str) -> Path:
    return root_dir / "runs" / "latest" / run_id


def _artifacts_dir(root_dir: Path, run_id: str) -> Path:
    return _run_root(root_dir, run_id) / "artifacts"


def _load_run(root_dir: Path, run_id: str) -> dict[str, Any]:
    return read_yaml(_run_root(root_dir, run_id) / "run.yaml")


def _write_run(root_dir: Path, run_id: str, payload: dict[str, Any]) -> None:
    write_yaml(_run_root(root_dir, run_id) / "run.yaml", payload)


def _artifact_path(root_dir: Path, run_id: str, name: str) -> Path:
    return _artifacts_dir(root_dir, run_id) / name


def _read_artifact(root_dir: Path, run_id: str, name: str) -> dict[str, Any]:
    return read_yaml(_artifact_path(root_dir, run_id, name))


def _write_artifact(root_dir: Path, run_id: str, name: str, payload: dict[str, Any]) -> None:
    write_yaml(_artifact_path(root_dir, run_id, name), payload)


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


def bootstrap_run(
    *,
    root_dir: Path,
    run_id: str,
    work_item_id: str,
    pr_id: str,
    work_item_title: str = "bootstrap-run",
) -> Path:
    run_root = root_dir / "runs" / "latest" / run_id
    artifacts_dir = run_root / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    initial_state = PipelineState.draft
    run_record = RunRecord.new(
        run_id=run_id,
        work_item_id=work_item_id,
        pr_id=pr_id,
        state=initial_state.value,
    )
    write_yaml(run_root / "run.yaml", run_record.as_payload())

    write_yaml(
        artifacts_dir / "work-item.yaml",
        {
            "work_item": {
                "id": work_item_id,
                "title": work_item_title,
                "status": PipelineState.draft.value,
            }
        },
    )
    write_yaml(
        artifacts_dir / "pr-plan.yaml",
        {
            "pr_plan": {
                "pr_id": pr_id,
                "scope": "",
                "status": PipelineState.planned.value,
            }
        },
    )
    write_yaml(
        artifacts_dir / "verification-report.yaml",
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
    write_yaml(
        artifacts_dir / "review-report.yaml",
        {
            "review_report": {
                "pr_id": pr_id,
                "status": "pending",
                "summary": "",
                "findings": [],
            }
        },
    )
    write_yaml(
        artifacts_dir / "qa-report.yaml",
        {
            "qa_report": {
                "pr_id": pr_id,
                "status": "pending",
                "summary": "",
                "findings": [],
            }
        },
    )
    write_yaml(
        artifacts_dir / "docs-sync-report.yaml",
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
    write_yaml(
        artifacts_dir / "evidence-bundle.yaml",
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
    write_yaml(
        artifacts_dir / "approval-request.yaml",
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
    write_yaml(
        artifacts_dir / "gate-status.yaml",
        {
            "gate_status": {
                "pr_id": pr_id,
                "current_state": initial_state.value,
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


def record_review(*, root_dir: Path, run_id: str, status: str, summary: str) -> Path:
    if status not in {"pass", "fail"}:
        raise ValueError("review status must be pass|fail")

    report = _read_artifact(root_dir, run_id, "review-report.yaml")
    report["review_report"]["status"] = status
    report["review_report"]["summary"] = summary
    report["review_report"]["recorded_at"] = _now_iso()
    _write_artifact(root_dir, run_id, "review-report.yaml", report)

    _update_pipeline_state(root_dir, run_id, PipelineState.review)
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

    _update_pipeline_state(root_dir, run_id, PipelineState.qa)
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
    _update_pipeline_state(root_dir, run_id, PipelineState.docs_sync)
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

    _update_pipeline_state(root_dir, run_id, PipelineState.approval_pending)
    return _artifact_path(root_dir, run_id, "gate-status.yaml")


def build_approval_request(*, root_dir: Path, run_id: str) -> tuple[Path, Path | None]:
    run_payload = _load_run(root_dir, run_id)
    run = run_payload["run"]
    verification_path = _artifact_path(root_dir, run_id, "verification-report.yaml")
    if not verification_path.exists():
        raise ValueError("cannot build approval request without verification report")

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
        queue_path = root_dir / "approval_queue" / "pending" / f"APR-{run_id}.yaml"
        write_yaml(queue_path, approval)

    return approval_path, queue_path
