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
                {"path": "observations/reviews.yaml", "type": "yaml"},
                {"path": "observations/checks.yaml", "type": "yaml"},
            ],
        },
    )


class PrLoopGateCheckCliTest(unittest.TestCase):
    def test_existing_fixture_evaluates_neutral_read_only_conditions(self) -> None:
        before = _snapshot_files(FIXTURE_ROOT)
        stdout = StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["pr-loop", "gate-check", "--root", str(REPO_ROOT), "--pr-id", "PR-113"])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertEqual(_snapshot_files(FIXTURE_ROOT), before)
        self.assertIn("PR Loop Fixture Gate Check:", output)
        self.assertIn("- pr_id: PR-113", output)
        self.assertIn("- source: local_non_runtime_fixture", output)
        self.assertIn("- fixture_status: present", output)
        self.assertIn("- gate_status: fail", output)
        self.assertIn("- runtime_authority: none", output)
        self.assertIn("- merge_authority: none", output)
        self.assertIn("- decision_authority: none", output)
        self.assertIn("- mutation: none", output)
        self.assertIn("- failed_condition: reviews_state_known_pass", output)
        self.assertIn("- failed_condition: checks_state_known_pass", output)
        self.assertIn("reviews state is not a known pass fact", output)
        self.assertIn("fixture-backed read-only evaluation only", output)
        self.assertNotIn("artifact_root_value", output)
        self.assertNotIn("fixture_artifact_root_hint", output)
        self.assertNotIn("merge_allowed", output)
        self.assertNotIn("safe to merge", output.lower())
        self.assertNotIn("approved", output.lower())
        self.assertNotIn("merge now", output.lower())

    def test_absent_fixture_is_graceful_summary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(root)
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["pr-loop", "gate-check", "--root", str(root), "--pr-id", "PR-115"])

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("- pr_id: PR-115", output)
            self.assertIn("- fixture_status: absent", output)
            self.assertIn("- gate_status: absent", output)
            self.assertIn("- failed_condition: fixture_root_present", output)
            self.assertFalse((root / "artifacts").exists())

    def test_incomplete_fixture_is_graceful_summary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(root)
            fixture_root = root / "tests" / "fixtures" / "pr_loop" / "examples" / "artifacts" / "pr_loop" / "PR-115"
            write_yaml(
                fixture_root / "state.yaml",
                {
                    "runner_id": "PR-LOOP-FIXTURE-115",
                    "target_pr": "PR-115",
                    "policy_source": {"authority": "none"},
                    "fixture_notice": {"inert": True, "runtime_authority": "none"},
                },
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["pr-loop", "gate-check", "--root", str(root), "--pr-id", "PR-115"])

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("- fixture_status: incomplete", output)
            self.assertIn("- gate_status: incomplete", output)
            self.assertIn("- failed_condition: manifest_required_files_complete", output)
            self.assertIn("- failed_condition: phase_present", output)
            self.assertIn("- failed_condition: reviews_required_field_present", output)
            self.assertIn("- failed_condition: checks_required_field_present", output)
            self.assertFalse((root / "artifacts").exists())

    def test_non_canonical_selectors_are_refused(self) -> None:
        for pr_id in ("latest", "current", "PR-1A", "PR-1-FOO"):
            with self.subTest(pr_id=pr_id):
                stdout = StringIO()
                stderr = StringIO()

                with redirect_stdout(stdout), redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as exc_info:
                        main(["pr-loop", "gate-check", "--root", str(REPO_ROOT), "--pr-id", pr_id])

                self.assertEqual(exc_info.exception.code, 2)
                self.assertIn("requires explicit --pr-id in the form PR-<number>", stderr.getvalue())
                self.assertEqual(stdout.getvalue(), "")

    def test_help_and_output_do_not_claim_runtime_or_merge_authority(self) -> None:
        stdout = StringIO()

        with redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as exc_info:
                main(["pr-loop", "gate-check", "--help"])

        output = stdout.getvalue()
        self.assertEqual(exc_info.exception.code, 0)
        self.assertIn("local non-runtime fixture", output)
        self.assertIn("no runtime artifacts", output)
        self.assertIn("no runtime artifacts, queue state, merge authority, approval authority", output)
        self.assertNotIn("safe to merge", output.lower())
        self.assertNotIn("approved", output.lower())
        self.assertNotIn("merge now", output.lower())
