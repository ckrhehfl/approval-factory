from __future__ import annotations

from pathlib import Path
import unittest

import yaml


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "pr_loop"
MANIFEST_PATH = FIXTURE_ROOT / "schema" / "pr-loop-artifact-manifest.yaml"


def _read_yaml(path: Path) -> object:
    with path.open("r", encoding="utf-8") as fp:
        return yaml.safe_load(fp)


def _lookup_path(payload: object, dotted_path: str) -> object:
    current = payload
    for part in dotted_path.split("."):
        if not isinstance(current, dict):
            raise AssertionError(f"{dotted_path} crosses non-mapping value at {part}")
        if part not in current:
            raise AssertionError(f"{dotted_path} missing at {part}")
        current = current[part]
    return current


class PrLoopFixtureExamplesTest(unittest.TestCase):
    def test_manifest_marks_examples_as_inert_and_non_runtime(self) -> None:
        manifest = _read_yaml(MANIFEST_PATH)

        self.assertEqual(manifest["status"], "inert_fixture_contract")
        self.assertEqual(manifest["authority"], "none")
        self.assertEqual(manifest["future_runtime_root"], "artifacts/pr_loop/<PR-ID>")
        self.assertEqual(manifest["example_root"], "examples/artifacts/pr_loop/PR-113")
        self.assertTrue(manifest["required_files"])
        self.assertFalse((FIXTURE_ROOT / "artifacts").exists())

    def test_fixture_files_exist_under_non_runtime_example_root(self) -> None:
        manifest = _read_yaml(MANIFEST_PATH)
        example_root = FIXTURE_ROOT / manifest["example_root"]

        for required_file in manifest["required_files"]:
            relative_path = Path(required_file["path"])
            self.assertFalse(relative_path.is_absolute())
            candidate = (example_root / relative_path).resolve()
            self.assertTrue(candidate.is_relative_to(example_root.resolve()))
            self.assertTrue(candidate.is_file(), required_file["path"])

    def test_yaml_fixture_examples_include_required_low_level_fields(self) -> None:
        manifest = _read_yaml(MANIFEST_PATH)
        example_root = FIXTURE_ROOT / manifest["example_root"]

        for required_file in manifest["required_files"]:
            if required_file["type"] != "yaml":
                continue

            payload = _read_yaml(example_root / required_file["path"])
            for required_path in required_file["required_paths"]:
                value = _lookup_path(payload, required_path)
                self.assertIsNotNone(value, f"{required_file['path']}:{required_path}")

    def test_markdown_fixture_examples_include_inert_authority_wording(self) -> None:
        manifest = _read_yaml(MANIFEST_PATH)
        example_root = FIXTURE_ROOT / manifest["example_root"]

        for required_file in manifest["required_files"]:
            if required_file["type"] != "markdown":
                continue

            text = (example_root / required_file["path"]).read_text(encoding="utf-8")
            for required_text in required_file["required_text"]:
                self.assertIn(required_text, text)
