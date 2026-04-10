from __future__ import annotations

from pathlib import Path

from orchestrator.pr_loop.gate_check import evaluate_pr_loop_fixture_gate
from orchestrator.pr_loop.inspect import inspect_pr_loop_fixture, validate_pr_id
from orchestrator.pr_loop.render_review import render_pr_loop_review_packet


def summarize_pr_loop_merge_dry_run(*, root_dir: Path, pr_id: str) -> dict[str, object]:
    pr_id = validate_pr_id(pr_id)
    inspection = inspect_pr_loop_fixture(root_dir=root_dir, pr_id=pr_id)
    gate_check = evaluate_pr_loop_fixture_gate(root_dir=root_dir, pr_id=pr_id)
    review_packet = render_pr_loop_review_packet(root_dir=root_dir, pr_id=pr_id)

    fixture_status = str(inspection.get("fixture_status") or "incomplete")
    gate_status = str(gate_check.get("gate_status") or "incomplete")
    preconditions = [
        _precondition(
            "fixture_present",
            fixture_status == "present",
            f"fixture_status is {fixture_status}",
        ),
        _precondition(
            "gate_status_pass",
            gate_status == "pass",
            f"gate_status is {gate_status}",
        ),
        _precondition(
            "review_packet_surface_available",
            bool(review_packet.strip()),
            "review packet surface is unavailable",
        ),
        _precondition(
            "non_authority_posture",
            _all_none(inspection, ("runtime_authority", "mutation"))
            and _all_none(gate_check, ("runtime_authority", "merge_authority", "decision_authority", "mutation")),
            "read-only non-authority posture is incomplete",
        ),
    ]
    failed_preconditions = [
        precondition
        for precondition in preconditions
        if not bool(precondition["passed"])
    ]

    if fixture_status == "absent":
        dry_run_status = "absent"
    elif fixture_status == "incomplete" or gate_status == "incomplete":
        dry_run_status = "incomplete"
    elif failed_preconditions:
        dry_run_status = "fail"
    else:
        dry_run_status = "pass"

    return {
        "pr_id": pr_id,
        "source": "local_non_runtime_fixture",
        "fixture_status": fixture_status,
        "gate_status": gate_status,
        "merge_dry_run_status": dry_run_status,
        "evaluated_precondition_count": len(preconditions),
        "failed_precondition_count": len(failed_preconditions),
        "failed_preconditions": failed_preconditions,
        "runtime_authority": "none",
        "merge_authority": "none",
        "approval_authority": "none",
        "mutation": "none",
        "note": (
            "fixture-backed read-only summary only; not runtime state, gate evidence, "
            "approval authority, or merge authority"
        ),
    }


def _precondition(name: str, passed: bool, reason: str) -> dict[str, object]:
    return {"name": name, "passed": passed, "reason": reason}


def _all_none(payload: dict[str, object], keys: tuple[str, ...]) -> bool:
    return all(payload.get(key) == "none" for key in keys)
