from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from orchestrator.cli import main
from orchestrator.yaml_io import read_yaml, write_yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "pr_loop"


def _snapshot_files(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}
    return {
        str(path.relative_to(root)): path.read_text(encoding="utf-8")
        for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file())
    }


class PrLoopStateCliTest(unittest.TestCase):
    def test_state_init_creates_minimal_live_state_under_canonical_pr_path(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["pr-loop", "state", "init", "--root", str(root), "--pr-id", "PR-123"])

            output = stdout.getvalue()
            state_path = root / "artifacts" / "pr_loop" / "PR-123" / "state.yaml"
            self.assertEqual(exit_code, 0)
            self.assertTrue(state_path.is_file())
            self.assertIn("PR Loop Live State Init:", output)
            self.assertIn("- pr_id: PR-123", output)
            self.assertIn("- source: local_live_runtime_state", output)
            self.assertIn("- state_status: present", output)
            self.assertIn("- state_path: artifacts/pr_loop/PR-123/state.yaml", output)
            self.assertIn("- runtime_authority: state_store_only", output)
            self.assertIn("- mutation: created", output)
            self.assertIn("- runner_id: PR-LOOP-RUNTIME-123", output)
            self.assertIn("- phase: initialized", output)
            self.assertIn("- phase_display: Initialized", output)
            self.assertIn("no fixture reuse", output)

            self.assertEqual(
                read_yaml(state_path),
                {
                    "target_pr": "PR-123",
                    "runner_id": "PR-LOOP-RUNTIME-123",
                    "phase": "initialized",
                },
            )

    def test_state_init_is_idempotent_when_live_state_already_exists(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_path = root / "artifacts" / "pr_loop" / "PR-123" / "state.yaml"
            write_yaml(
                state_path,
                {
                    "target_pr": "PR-123",
                    "runner_id": "PR-LOOP-RUNTIME-123",
                    "phase": "initialized",
                },
            )
            before = state_path.read_text(encoding="utf-8")
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["pr-loop", "state", "init", "--root", str(root), "--pr-id", "PR-123"])

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertEqual(state_path.read_text(encoding="utf-8"), before)
            self.assertIn("- mutation: none", output)
            self.assertIn("existing minimal live state preserved", output)

    def test_state_show_reads_live_state_only_and_does_not_reuse_fixture(self) -> None:
        before = _snapshot_files(FIXTURE_ROOT)
        stdout = StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["pr-loop", "state", "show", "--root", str(REPO_ROOT), "--pr-id", "PR-113"])

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertEqual(_snapshot_files(FIXTURE_ROOT), before)
        self.assertIn("PR Loop Live State:", output)
        self.assertIn("- pr_id: PR-113", output)
        self.assertIn("- source: local_live_runtime_state", output)
        self.assertIn("- state_status: absent", output)
        self.assertIn("- state_path: artifacts/pr_loop/PR-113/state.yaml", output)
        self.assertIn("State Note: live state file absent", output)
        self.assertNotIn("local_non_runtime_fixture", output)
        self.assertNotIn("tests/fixtures/pr_loop/examples/artifacts/pr_loop/PR-113", output)

    def test_state_show_reports_invalid_live_state_when_target_pr_breaks_anchor(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_yaml(
                root / "artifacts" / "pr_loop" / "PR-123" / "state.yaml",
                {
                    "target_pr": "PR-999",
                    "runner_id": "PR-LOOP-RUNTIME-123",
                    "phase": "initialized",
                },
            )
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["pr-loop", "state", "show", "--root", str(root), "--pr-id", "PR-123"])

            output = stdout.getvalue()
            self.assertEqual(exit_code, 0)
            self.assertIn("- state_status: invalid", output)
            self.assertIn(
                "State Note: pr-loop state target_pr must match the canonical PR id anchored path",
                output,
            )

    def test_state_init_refuses_invalid_existing_live_state(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_yaml(
                root / "artifacts" / "pr_loop" / "PR-123" / "state.yaml",
                {
                    "target_pr": "PR-123",
                    "runner_id": "",
                    "phase": "initialized",
                },
            )
            stdout = StringIO()
            stderr = StringIO()

            with redirect_stdout(stdout), redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(["pr-loop", "state", "init", "--root", str(root), "--pr-id", "PR-123"])

            self.assertEqual(exc_info.exception.code, 2)
            self.assertEqual(stdout.getvalue(), "")
            self.assertIn("runner_id must be a non-empty string", stderr.getvalue())

    def test_state_subcommands_refuse_non_canonical_selectors(self) -> None:
        for pr_id in ("latest", "current", "PR-1A", "PR-1-FOO"):
            for subcommand in ("init", "show"):
                with self.subTest(pr_id=pr_id, subcommand=subcommand):
                    stdout = StringIO()
                    stderr = StringIO()

                    with redirect_stdout(stdout), redirect_stderr(stderr):
                        with self.assertRaises(SystemExit) as exc_info:
                            main(["pr-loop", "state", subcommand, "--root", str(REPO_ROOT), "--pr-id", pr_id])

                    self.assertEqual(exc_info.exception.code, 2)
                    self.assertEqual(stdout.getvalue(), "")
                    self.assertIn("requires explicit --pr-id in the form PR-<number>", stderr.getvalue())

    def test_state_help_keeps_scope_narrow_and_non_authoritative(self) -> None:
        stdout = StringIO()

        with redirect_stdout(stdout):
            with self.assertRaises(SystemExit) as exc_info:
                main(["pr-loop", "state", "init", "--help"])

        output = stdout.getvalue()
        self.assertEqual(exc_info.exception.code, 0)
        self.assertIn("artifacts/pr_loop/PR-<number>/state.yaml only", output)
        self.assertIn("no latest/current selector fallback", output)
        self.assertIn("no fixture reuse", output)
        self.assertIn("merge authority", output)
        self.assertIn("approval authority", output)
        self.assertNotIn("latest-queue-item", output)
        self.assertNotIn("current-branch", output)

