from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Iterable

from orchestrator.models import RunRecord
from orchestrator.yaml_io import write_yaml


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


def _slugify(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    return "-".join(filter(None, slug.split("-"))) or "untitled"


def _ensure_text_file(path: Path, lines: Iterable[str]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


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
        artifacts_dir / "review-report.yaml",
        {"review_report": {"pr_id": pr_id, "status": "pending", "findings": []}},
    )
    write_yaml(
        artifacts_dir / "qa-report.yaml",
        {"qa_report": {"pr_id": pr_id, "status": "pending", "findings": []}},
    )
    write_yaml(
        artifacts_dir / "docs-sync-report.yaml",
        {
            "docs_sync_report": {
                "pr_id": pr_id,
                "required": True,
                "status": "pending",
                "changed_docs": [],
            }
        },
    )
    write_yaml(
        artifacts_dir / "evidence-bundle.yaml",
        {
            "evidence_bundle": {
                "pr_id": pr_id,
                "checks": {
                    "lint": "pending",
                    "test": "pending",
                    "build": "pending",
                    "docs_sync": "pending",
                },
                "residual_risks": [],
            }
        },
    )
    write_yaml(
        artifacts_dir / "approval-request.yaml",
        {
            "approval_request": {
                "pr_id": pr_id,
                "gate_type": "merge_approval",
                "checks": {
                    "review": "pending",
                    "qa": "pending",
                    "docs_sync": "pending",
                    "evidence_bundle": "pending",
                },
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
