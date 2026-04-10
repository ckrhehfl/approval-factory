from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from orchestrator.pr_loop.inspect import inspect_pr_loop_fixture, validate_pr_id
from orchestrator.yaml_io import read_yaml


_FIXTURE_BASE = Path("tests") / "fixtures" / "pr_loop"
_EXAMPLE_PR_LOOP_ROOT = _FIXTURE_BASE / "examples" / "artifacts" / "pr_loop"
_KNOWN_PASS_STATES = {"pass", "passed", "success", "succeeded"}


def evaluate_pr_loop_fixture_gate(*, root_dir: Path, pr_id: str) -> dict[str, object]:
    pr_id = validate_pr_id(pr_id)
    root_dir = root_dir.resolve()
    fixture_root = root_dir / _EXAMPLE_PR_LOOP_ROOT / pr_id
    inspection = inspect_pr_loop_fixture(root_dir=root_dir, pr_id=pr_id)

    result: dict[str, object] = {
        "pr_id": pr_id,
        "source": "local_non_runtime_fixture",
        "fixture_status": inspection["fixture_status"],
        "fixture_root": inspection["fixture_root"],
        "manifest_path": inspection["manifest_path"],
        "runtime_authority": "none",
        "merge_authority": "none",
        "decision_authority": "none",
        "mutation": "none",
        "note": "fixture-backed read-only evaluation only; not merge authority, approval authority, or runtime gate evidence",
    }

    fixture_status = str(inspection["fixture_status"])
    if fixture_status == "absent":
        return _with_conditions(
            result,
            "absent",
            [
                _condition(
                    "fixture_root_present",
                    False,
                    "local non-runtime fixture root is absent",
                )
            ],
        )

    state = _read_mapping(fixture_root / "state.yaml")
    reviews_observation = _read_mapping(fixture_root / "observations" / "reviews.yaml")
    checks_observation = _read_mapping(fixture_root / "observations" / "checks.yaml")

    conditions = [
        _condition(
            "manifest_required_files_complete",
            fixture_status == "present",
            _manifest_missing_reason(inspection),
        ),
        _condition(
            "target_pr_present",
            _nested_value(state, ("target_pr",)) == pr_id,
            "state target_pr is absent or does not match the explicit PR id",
        ),
        _condition(
            "phase_present",
            isinstance(_nested_value(state, ("phase",)), str) and bool(_nested_value(state, ("phase",))),
            "state phase is absent",
        ),
        _condition(
            "policy_source_authority_none",
            _nested_value(state, ("policy_source", "authority")) == "none",
            "policy source authority is absent or not none",
        ),
        _condition(
            "fixture_notice_inert_true",
            _nested_value(state, ("fixture_notice", "inert")) is True,
            "state fixture notice inert flag is absent or not true",
        ),
        _condition(
            "fixture_notice_runtime_authority_none",
            _nested_value(state, ("fixture_notice", "runtime_authority")) == "none",
            "state fixture notice runtime authority is absent or not none",
        ),
        _condition(
            "reviews_required_field_present",
            _nested_value(state, ("observations", "reviews", "required")) is not None,
            "state reviews required field is absent",
        ),
        _condition(
            "checks_required_field_present",
            _nested_value(state, ("observations", "checks", "required")) is not None,
            "state checks required field is absent",
        ),
        _condition(
            "reviews_state_known_pass",
            _is_known_pass(_nested_value(state, ("observations", "reviews", "state"))),
            "reviews state is not a known pass fact",
        ),
        _condition(
            "checks_state_known_pass",
            _is_known_pass(_nested_value(state, ("observations", "checks", "state"))),
            "checks state is not a known pass fact",
        ),
        _condition(
            "reviews_observation_target_pr_matches",
            _nested_value(reviews_observation, ("target_pr",)) == pr_id,
            "reviews observation target_pr is absent or does not match the explicit PR id",
        ),
        _condition(
            "checks_observation_target_pr_matches",
            _nested_value(checks_observation, ("target_pr",)) == pr_id,
            "checks observation target_pr is absent or does not match the explicit PR id",
        ),
        _condition(
            "reviews_observation_fixture_inert_true",
            _nested_value(reviews_observation, ("fixture_notice", "inert")) is True,
            "reviews observation fixture notice inert flag is absent or not true",
        ),
        _condition(
            "checks_observation_fixture_inert_true",
            _nested_value(checks_observation, ("fixture_notice", "inert")) is True,
            "checks observation fixture notice inert flag is absent or not true",
        ),
    ]

    if fixture_status == "incomplete":
        gate_status = "incomplete"
    elif any(not bool(condition["passed"]) for condition in conditions):
        gate_status = "fail"
    else:
        gate_status = "pass"

    return _with_conditions(result, gate_status, conditions)


def _with_conditions(
    result: dict[str, object],
    gate_status: str,
    conditions: list[dict[str, object]],
) -> dict[str, object]:
    failed_conditions = [condition for condition in conditions if not bool(condition["passed"])]
    result.update(
        {
            "gate_status": gate_status,
            "evaluated_condition_count": len(conditions),
            "failed_condition_count": len(failed_conditions),
            "failed_conditions": failed_conditions,
        }
    )
    return result


def _condition(name: str, passed: bool, reason: str) -> dict[str, object]:
    return {"name": name, "passed": passed, "reason": reason}


def _manifest_missing_reason(inspection: dict[str, object]) -> str:
    missing_files = inspection.get("missing_files")
    if isinstance(missing_files, list) and missing_files:
        return "required fixture files missing: " + ", ".join(str(item) for item in missing_files)
    note = inspection.get("note")
    if isinstance(note, str) and note != "none":
        return note
    return "manifest required file set is incomplete"


def _read_mapping(path: Path) -> dict[str, Any]:
    try:
        payload = read_yaml(path)
    except (OSError, yaml.YAMLError):
        return {}
    if isinstance(payload, dict):
        return payload
    return {}


def _nested_value(payload: dict[str, Any], keys: tuple[str, ...]) -> object | None:
    current: object = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _is_known_pass(value: object) -> bool:
    return isinstance(value, str) and value.strip().lower() in _KNOWN_PASS_STATES
