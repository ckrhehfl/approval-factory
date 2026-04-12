from __future__ import annotations

from pathlib import Path

import yaml

from orchestrator.pr_loop.inspect import validate_pr_id
from orchestrator.pr_loop.models import PrLoopState
from orchestrator.pr_loop.phase_machine import display_pr_loop_phase
from orchestrator.yaml_io import read_yaml, write_yaml


_LIVE_STATE_ROOT = Path("artifacts") / "pr_loop"


def inspect_pr_loop_live_state(*, root_dir: Path, pr_id: str) -> dict[str, object]:
    canonical_pr_id = validate_pr_id(pr_id)
    root_dir = root_dir.resolve()
    state_root = root_dir / _LIVE_STATE_ROOT / canonical_pr_id
    state_path = state_root / "state.yaml"

    summary: dict[str, object] = {
        "pr_id": canonical_pr_id,
        "source": "local_live_runtime_state",
        "state_root": _relative_or_absolute(state_root, root_dir),
        "state_path": _relative_or_absolute(state_path, root_dir),
        "runtime_authority": "state_store_only",
        "mutation": "none",
    }

    if not state_path.is_file():
        summary.update(
            {
                "state_status": "absent",
                "runner_id": None,
                "phase": None,
                "phase_display": None,
                "note": "live state file absent",
            }
        )
        return summary

    try:
        state = PrLoopState.from_payload(read_yaml(state_path), pr_id=canonical_pr_id)
    except (OSError, yaml.YAMLError, ValueError) as exc:
        summary.update(
            {
                "state_status": "invalid",
                "runner_id": None,
                "phase": None,
                "phase_display": None,
                "note": str(exc),
            }
        )
        return summary

    summary.update(
        {
            "state_status": "present",
            "runner_id": state.runner_id,
            "phase": state.phase,
            "phase_display": display_pr_loop_phase(state.phase),
            "note": "minimal live state only; no fixture reuse, gate evidence, or decision authority",
        }
    )
    return summary


def init_pr_loop_live_state(*, root_dir: Path, pr_id: str) -> dict[str, object]:
    canonical_pr_id = validate_pr_id(pr_id)
    summary = inspect_pr_loop_live_state(root_dir=root_dir, pr_id=canonical_pr_id)

    if summary["state_status"] == "present":
        summary["note"] = "existing minimal live state preserved; no fixture reuse, gate evidence, or decision authority"
        return summary
    if summary["state_status"] == "invalid":
        raise ValueError(str(summary["note"]))

    state = PrLoopState.initialize(pr_id=canonical_pr_id)
    save_pr_loop_live_state(root_dir=root_dir, state=state)
    created = inspect_pr_loop_live_state(root_dir=root_dir, pr_id=canonical_pr_id)
    created["mutation"] = "created"
    created["note"] = "minimal live state initialized; no fixture reuse, gate evidence, or decision authority"
    return created


def load_pr_loop_live_state(*, root_dir: Path, pr_id: str) -> PrLoopState | None:
    canonical_pr_id = validate_pr_id(pr_id)
    state_path = pr_loop_live_state_path(root_dir=root_dir, pr_id=canonical_pr_id)
    if not state_path.is_file():
        return None
    return PrLoopState.from_payload(read_yaml(state_path), pr_id=canonical_pr_id)


def save_pr_loop_live_state(*, root_dir: Path, state: PrLoopState) -> Path:
    state_path = pr_loop_live_state_path(root_dir=root_dir, pr_id=state.pr_id)
    write_yaml(state_path, state.as_payload())
    return state_path


def pr_loop_live_state_path(*, root_dir: Path, pr_id: str) -> Path:
    canonical_pr_id = validate_pr_id(pr_id)
    return root_dir.resolve() / _LIVE_STATE_ROOT / canonical_pr_id / "state.yaml"


def _relative_or_absolute(path: Path, root_dir: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()
