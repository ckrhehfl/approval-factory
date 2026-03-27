from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def read_yaml(path: Path) -> Any:
    """Read a YAML file into a Python object."""
    with path.open("r", encoding="utf-8") as fp:
        data = yaml.safe_load(fp)
    return data


def write_yaml(path: Path, payload: Any) -> None:
    """Write a Python object as YAML with stable formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fp:
        yaml.safe_dump(payload, fp, sort_keys=False, allow_unicode=False)
