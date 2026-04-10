from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from orchestrator.yaml_io import read_yaml


_PR_ID_PATTERN = re.compile(r"^PR-[0-9]+$")
_FIXTURE_BASE = Path("tests") / "fixtures" / "pr_loop"
_MANIFEST_PATH = _FIXTURE_BASE / "schema" / "pr-loop-artifact-manifest.yaml"
_EXAMPLE_PR_LOOP_ROOT = _FIXTURE_BASE / "examples" / "artifacts" / "pr_loop"


def validate_pr_id(pr_id: str) -> str:
    if not _PR_ID_PATTERN.fullmatch(pr_id):
        raise ValueError("pr-loop inspect requires explicit --pr-id in the form PR-<number>")
    return pr_id


def inspect_pr_loop_fixture(*, root_dir: Path, pr_id: str) -> dict[str, object]:
    pr_id = validate_pr_id(pr_id)
    root_dir = root_dir.resolve()
    fixture_root = root_dir / _EXAMPLE_PR_LOOP_ROOT / pr_id
    manifest_path = root_dir / _MANIFEST_PATH

    inspection: dict[str, object] = {
        "pr_id": pr_id,
        "source": "local_non_runtime_fixture",
        "fixture_root": _relative_or_absolute(fixture_root, root_dir),
        "manifest_path": _relative_or_absolute(manifest_path, root_dir),
        "runtime_authority": "none",
        "mutation": "none",
    }

    if not manifest_path.is_file():
        inspection.update(
            {
                "fixture_status": "incomplete",
                "note": "manifest fixture missing",
                "required_file_count": 0,
                "present_file_count": 0,
                "missing_files": [],
            }
        )
        return inspection

    if not fixture_root.exists():
        inspection.update(
            {
                "fixture_status": "absent",
                "note": "fixture root absent",
                "required_file_count": 0,
                "present_file_count": 0,
                "missing_files": [],
            }
        )
        return inspection

    manifest = _read_yaml_or_none(manifest_path)
    if manifest is None:
        inspection.update(
            {
                "fixture_status": "incomplete",
                "note": "manifest fixture unreadable",
                "required_file_count": 0,
                "present_file_count": 0,
                "missing_files": [],
            }
        )
        return inspection

    required_files = _required_files(manifest)
    missing_files = [
        relative_path
        for relative_path in required_files
        if not (fixture_root / relative_path).is_file()
    ]
    inspection.update(
        {
            "required_file_count": len(required_files),
            "present_file_count": len(required_files) - len(missing_files),
            "missing_files": missing_files,
        }
    )

    state_path = fixture_root / "state.yaml"
    state: dict[str, Any] = {}
    if state_path.is_file():
        payload = _read_yaml_or_none(state_path)
        if isinstance(payload, dict):
            state = payload

    if missing_files:
        fixture_status = "incomplete"
        note = "required fixture files missing"
    elif not state:
        fixture_status = "incomplete"
        note = "state fixture missing or unreadable"
    else:
        fixture_status = "present"
        note = "none"

    inspection.update(
        {
            "fixture_status": fixture_status,
            "note": note,
            "target_pr": _string_or_none(state.get("target_pr")),
            "runner_id": _string_or_none(state.get("runner_id")),
            "phase": _string_or_none(state.get("phase")),
            "policy_source_status": _nested_string_or_none(state, ("policy_source", "status")),
            "policy_source_authority": _nested_string_or_none(state, ("policy_source", "authority")),
            "repo": _nested_string_or_none(state, ("runtime_refs", "repo")),
            "branch": _nested_string_or_none(state, ("runtime_refs", "branch")),
            "base": _nested_string_or_none(state, ("runtime_refs", "base")),
            "reviews_required": _nested_value_or_none(state, ("observations", "reviews", "required")),
            "reviews_state": _nested_string_or_none(state, ("observations", "reviews", "state")),
            "checks_required": _nested_value_or_none(state, ("observations", "checks", "required")),
            "checks_state": _nested_string_or_none(state, ("observations", "checks", "state")),
            "fixture_notice_inert": _nested_value_or_none(state, ("fixture_notice", "inert")),
            "fixture_notice_runtime_authority": _nested_string_or_none(state, ("fixture_notice", "runtime_authority")),
        }
    )
    return inspection


def _read_yaml_or_none(path: Path) -> object | None:
    try:
        return read_yaml(path)
    except (OSError, yaml.YAMLError):
        return None


def _required_files(manifest: object) -> list[str]:
    if not isinstance(manifest, dict):
        return []
    required_files = manifest.get("required_files")
    if not isinstance(required_files, list):
        return []

    paths: list[str] = []
    for item in required_files:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        if isinstance(path, str) and path and not Path(path).is_absolute():
            paths.append(path)
    return paths


def _relative_or_absolute(path: Path, root_dir: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _string_or_none(value: object) -> str | None:
    if isinstance(value, str):
        return value
    return None


def _nested_value_or_none(payload: dict[str, Any], keys: tuple[str, ...]) -> object | None:
    current: object = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _nested_string_or_none(payload: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    return _string_or_none(_nested_value_or_none(payload, keys))
