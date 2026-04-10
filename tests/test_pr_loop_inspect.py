from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from orchestrator.cli import main
from orchestrator.yaml_io import write_yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "pr_loop"


def _snapshot_files(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): path.read_text(encoding="utf-8")
        for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file())
    }


def _write_manifest(root: Path) -> None:
    write_yaml(
        root / "tests" / "fixtures" / "pr_loop" / "schema" / "pr-loop-artifact-manifest.yaml",
        {
            "schema_name": "pr-loop-artifact-fixture-manifest",
            "status": "inert_fixture_contract",
            "authority": "none",
            "required_files": [
                {"path": "state.yaml", "type": "yaml"},
                {"path": "observations/checks.yaml", "type": "yaml"},
            ],
        },
    )


class PrLoopInspectCliTest(unittest.TestCase):
    def test_inspect_existing_fixture_summarizes_read_only_facts(self) -> None:
        before = _snapshot_files(FIXTURE_ROOT)
        stdout = StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["pr-loop", "inspect", "--root", str(REPO_ROOT), "--pr-id", "PR-113"])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertEqual(_snapshot_files(FIXTURE_ROOT), before)
        self.assertIn("PR Loop Fixture Inspect:", output)
        self.assertIn("- pr_id: PR-113", output)
        self.assertIn("- source: local_non_runtime_fixture", output)
        self.assertIn("- fixture_status: present", output)
        self.assertIn("- fixture_root: tests/fixtures/pr_loop/examples/artifacts/pr_loop/PR-113", output)
        self.assertIn("- runtime_authority: none", output)
        self.assertIn("- mutation: none", output)
        self.assertIn("- target_pr: PR-113", output)
        self.assertIn("- runner_id: PR-LOOP-FIXTURE-001", output)
        self.assertIn("- phase: initialized", output)
        self.assertIn("- branch: pr/113-pr-loop-slot2-artifact-fixtures", output)
        self.assertIn("- reviews_state: fixture_unknown", output)
        self.assertIn("- checks_state: fixture_unknown", output)
        self.assertIn("- missing_file: none", output)
        self.assertNotIn("artifact_root_value", output)
        self.assertNotIn("fixture_artifact_root_hint", output)
        self.assertNotIn("merge_allowed", output)
        self.assertNotIn("approval-ready", output)
        self.assertNotIn("safe to merge", output)
        self.assertNotIn("gate satisfied", output)

    def test_absent_fixture_is_graceful_read_only_summary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(root)
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["pr-loop", "inspect", "--root", str(root), "--pr-id", "PR-114"])

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("- pr_id: PR-114", output)
            self.assertIn("- fixture_status: absent", output)
            self.assertIn("- required_file_count: 0", output)
            self.assertIn("- present_file_count: 0", output)
            self.assertIn("Read Only Note: fixture root absent", output)

    def test_incomplete_fixture_is_graceful_read_only_summary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(root)
            fixture_root = root / "tests" / "fixtures" / "pr_loop" / "examples" / "artifacts" / "pr_loop" / "PR-114"
            write_yaml(
                fixture_root / "state.yaml",
                {
                    "runner_id": "PR-LOOP-FIXTURE-114",
                    "target_pr": "PR-114",
                    "fixture_notice": {"inert": True, "runtime_authority": "none"},
                },
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["pr-loop", "inspect", "--root", str(root), "--pr-id", "PR-114"])

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("- fixture_status: incomplete", output)
            self.assertIn("- required_file_count: 2", output)
            self.assertIn("- present_file_count: 1", output)
            self.assertIn("- missing_file: observations/checks.yaml", output)
            self.assertIn("- target_pr: PR-114", output)

    def test_unreadable_yaml_fixture_is_graceful_read_only_summary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(root)
            fixture_root = root / "tests" / "fixtures" / "pr_loop" / "examples" / "artifacts" / "pr_loop" / "PR-114"
            (fixture_root / "observations").mkdir(parents=True, exist_ok=True)
            (fixture_root / "state.yaml").write_text("runner_id: [\n", encoding="utf-8")
            (fixture_root / "observations" / "checks.yaml").write_text("checks:\n  state: fixture_unknown\n", encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["pr-loop", "inspect", "--root", str(root), "--pr-id", "PR-114"])

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("- fixture_status: incomplete", output)
            self.assertIn("- required_file_count: 2", output)
            self.assertIn("- present_file_count: 2", output)
            self.assertIn("Read Only Note: state fixture missing or unreadable", output)

    def test_pr_id_is_required_and_non_canonical_selectors_are_refused(self) -> None:
        for pr_id in ("latest", "current", "PR-1A", "PR-1-FOO"):
            with self.subTest(pr_id=pr_id):
                stdout = StringIO()
                stderr = StringIO()

                with redirect_stdout(stdout), redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as exc_info:
                        main(["pr-loop", "inspect", "--root", str(REPO_ROOT), "--pr-id", pr_id])

                self.assertEqual(exc_info.exception.code, 2)
                self.assertIn("requires explicit --pr-id in the form PR-<number>", stderr.getvalue())
                self.assertEqual(stdout.getvalue(), "")
