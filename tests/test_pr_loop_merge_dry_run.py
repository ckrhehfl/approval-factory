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
FORBIDDEN_OUTPUT_WORDING = (
    "approved",
    "safe to merge",
    "recommended decision",
    "merge now",
    "clear to merge",
    "ready now",
    "proceed",
)


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


def _write_pass_fixture(root: Path, pr_id: str) -> None:
    fixture_root = root / "tests" / "fixtures" / "pr_loop" / "examples" / "artifacts" / "pr_loop" / pr_id
    write_yaml(
        fixture_root / "state.yaml",
        {
            "runner_id": f"PR-LOOP-FIXTURE-{pr_id.removeprefix('PR-')}",
            "target_pr": pr_id,
            "phase": "fixture_pass",
            "policy_source": {"status": "fixture_only", "authority": "none"},
            "runtime_refs": {"repo": "approval-factory", "branch": "fixture", "base": "main"},
            "observations": {
                "reviews": {"required": True, "state": "pass"},
                "checks": {"required": True, "state": "pass"},
            },
            "gate": {"merge_allowed": False, "reason": "inert fixture only; no runtime authority"},
            "artifacts": {"root": f"artifacts/pr_loop/{pr_id}"},
            "fixture_notice": {
                "inert": True,
                "runtime_authority": "none",
                "fixture_root": f"tests/fixtures/pr_loop/examples/artifacts/pr_loop/{pr_id}",
            },
        },
    )
    write_yaml(
        fixture_root / "observations" / "reviews.yaml",
        {
            "target_pr": pr_id,
            "reviews": {"required": True, "state": "pass"},
            "fixture_notice": {"inert": True, "runtime_authority": "none"},
        },
    )
    write_yaml(
        fixture_root / "observations" / "checks.yaml",
        {
            "target_pr": pr_id,
            "checks": {"required": True, "state": "pass"},
            "fixture_notice": {"inert": True, "runtime_authority": "none"},
        },
    )
    write_yaml(
        fixture_root / "observations" / "pr-metadata.yaml",
        {
            "target_pr": pr_id,
            "source": "local_non_runtime_fixture",
            "observed_state": "fixture_pass",
            "fixture_notice": {"inert": True, "runtime_authority": "none"},
        },
    )
    write_yaml(
        fixture_root / "observations" / "docs-sync.yaml",
        {
            "target_pr": pr_id,
            "docs_sync": {"state": "fixture_pass", "policy_status": "fixture_only"},
            "fixture_notice": {"inert": True, "runtime_authority": "none"},
        },
    )
    write_yaml(
        fixture_root / "gates" / "merge-gate.yaml",
        {
            "target_pr": pr_id,
            "gate": {"merge_allowed": False, "reason": "inert fixture only; no runtime authority"},
            "decision_authority": "none",
            "fixture_notice": {"inert": True, "runtime_authority": "none"},
        },
    )
    _write_text(fixture_root / "policy-snapshot.md", "inert fixture\nno runtime authority\n")
    _write_text(fixture_root / "rendering" / "review-packet.md", "fixture-only review packet\nnot a gate input\n")
    _write_text(
        fixture_root / "rendering" / "operator-summary.md",
        "fixture-only operator summary\nnot an approval decision\n",
    )
    _write_text(fixture_root / "gates" / "blocked-reasons.md", "fixture-only blocked reasons\nno merge authority\n")
    _write_text(fixture_root / "evidence" / "commands.md", "fixture-only command log\nnot execution evidence\n")
    _write_text(fixture_root / "evidence" / "diff-summary.md", "fixture-only diff summary\nnot review evidence\n")


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


class PrLoopMergeDryRunCliTest(unittest.TestCase):
    def test_existing_fixture_renders_neutral_dry_run_summary(self) -> None:
        before = _snapshot_files(FIXTURE_ROOT)
        stdout = StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["pr-loop", "merge", "--root", str(REPO_ROOT), "--pr-id", "PR-113", "--dry-run"])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertEqual(_snapshot_files(FIXTURE_ROOT), before)
        self.assertIn("PR Loop Merge Dry Run Summary:", output)
        self.assertIn("- pr_id: PR-113", output)
        self.assertIn("- source: local_non_runtime_fixture", output)
        self.assertIn("- fixture_status: present", output)
        self.assertIn("- gate_status: fail", output)
        self.assertIn("- merge_dry_run_status: fail", output)
        self.assertIn("- evaluated_precondition_count: 4", output)
        self.assertIn("- failed_precondition_count: 1", output)
        self.assertIn("- failed_precondition: gate_status_pass", output)
        self.assertIn("gate_status is fail", output)
        self.assertIn("- runtime_authority: none", output)
        self.assertIn("- merge_authority: none", output)
        self.assertIn("- approval_authority: none", output)
        self.assertIn("- mutation: none", output)
        self.assertIn("fixture-backed read-only summary only", output)
        self.assertNotIn("artifact_root_value", output)
        self.assertNotIn("fixture_artifact_root_hint", output)
        self.assertNotIn("merge_allowed", output)
        self.assertFalse((REPO_ROOT / "artifacts" / "pr_loop").exists())
        _assert_forbidden_wording_absent(self, output)

    def test_pass_fixture_renders_neutral_non_authoritative_summary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(root)
            _write_pass_fixture(root, "PR-117")
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["pr-loop", "merge", "--root", str(root), "--pr-id", "PR-117", "--dry-run"])

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("PR Loop Merge Dry Run Summary:", output)
            self.assertIn("- pr_id: PR-117", output)
            self.assertIn("- source: local_non_runtime_fixture", output)
            self.assertIn("- fixture_status: present", output)
            self.assertIn("- gate_status: pass", output)
            self.assertIn("- merge_dry_run_status: pass", output)
            self.assertIn("- evaluated_precondition_count: 4", output)
            self.assertIn("- failed_precondition_count: 0", output)
            self.assertIn("- failed_precondition: none", output)
            self.assertIn("- runtime_authority: none", output)
            self.assertIn("- merge_authority: none", output)
            self.assertIn("- approval_authority: none", output)
            self.assertIn("- mutation: none", output)
            self.assertIn("fixture-backed read-only summary only", output)
            self.assertFalse((root / "artifacts").exists())
            _assert_forbidden_wording_absent(self, output)

    def test_absent_fixture_renders_graceful_dry_run_summary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(root)
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["pr-loop", "merge", "--root", str(root), "--pr-id", "PR-117", "--dry-run"])

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("- pr_id: PR-117", output)
            self.assertIn("- fixture_status: absent", output)
            self.assertIn("- gate_status: absent", output)
            self.assertIn("- merge_dry_run_status: absent", output)
            self.assertIn("- failed_precondition: fixture_present", output)
            self.assertIn("- failed_precondition: gate_status_pass", output)
            self.assertFalse((root / "artifacts").exists())
            _assert_forbidden_wording_absent(self, output)

    def test_incomplete_fixture_renders_graceful_dry_run_summary(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_manifest(root)
            fixture_root = root / "tests" / "fixtures" / "pr_loop" / "examples" / "artifacts" / "pr_loop" / "PR-117"
            write_yaml(
                fixture_root / "state.yaml",
                {
                    "runner_id": "PR-LOOP-FIXTURE-117",
                    "target_pr": "PR-117",
                    "policy_source": {"authority": "none"},
                    "fixture_notice": {"inert": True, "runtime_authority": "none"},
                },
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["pr-loop", "merge", "--root", str(root), "--pr-id", "PR-117", "--dry-run"])

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("- fixture_status: incomplete", output)
            self.assertIn("- gate_status: incomplete", output)
            self.assertIn("- merge_dry_run_status: incomplete", output)
            self.assertIn("- failed_precondition: fixture_present", output)
            self.assertIn("- failed_precondition: gate_status_pass", output)
            self.assertFalse((root / "artifacts").exists())
            _assert_forbidden_wording_absent(self, output)

    def test_non_canonical_selectors_are_refused(self) -> None:
        for pr_id in ("latest", "current", "PR-1A", "PR-1-FOO"):
            with self.subTest(pr_id=pr_id):
                stdout = StringIO()
                stderr = StringIO()

                with redirect_stdout(stdout), redirect_stderr(stderr):
                    with self.assertRaises(SystemExit) as exc_info:
                        main(["pr-loop", "merge", "--root", str(REPO_ROOT), "--pr-id", pr_id, "--dry-run"])

                self.assertEqual(exc_info.exception.code, 2)
                self.assertIn("requires explicit --pr-id in the form PR-<number>", stderr.getvalue())
                self.assertEqual(stdout.getvalue(), "")

    def test_merge_requires_dry_run(self) -> None:
        stdout = StringIO()
        stderr = StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as exc_info:
                main(["pr-loop", "merge", "--root", str(REPO_ROOT), "--pr-id", "PR-113"])

        self.assertEqual(exc_info.exception.code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("the following arguments are required: --dry-run", stderr.getvalue())

    def test_help_and_output_guardrails(self) -> None:
        stdout = StringIO()

        with redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as exc_info:
                main(["pr-loop", "merge", "--help"])

        help_output = stdout.getvalue()
        self.assertEqual(exc_info.exception.code, 0)
        self.assertIn("local non-runtime fixture", help_output)
        self.assertIn("requires --dry-run", help_output)
        self.assertIn("no runtime artifacts", help_output)
        self.assertIn("merge authority", help_output)
        self.assertIn("approval authority", help_output)
        _assert_forbidden_wording_absent(self, help_output)

        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = main(["pr-loop", "merge", "--root", str(REPO_ROOT), "--pr-id", "PR-113", "--dry-run"])

        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        self.assertIn("- merge_authority: none", output)
        self.assertIn("- approval_authority: none", output)
        self.assertIn("- mutation: none", output)
        self.assertFalse((REPO_ROOT / "artifacts" / "pr_loop").exists())
        _assert_forbidden_wording_absent(self, output)


def _assert_forbidden_wording_absent(test_case: unittest.TestCase, output: str) -> None:
    lowered = output.lower()
    for forbidden in FORBIDDEN_OUTPUT_WORDING:
        test_case.assertNotIn(forbidden, lowered)
