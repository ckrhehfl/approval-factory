from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from orchestrator.cli import main
from orchestrator.yaml_io import read_yaml


class PipelineApprovalLoopTest(unittest.TestCase):
    def _prepare_root(self, root: Path) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        (root / "config").mkdir(parents=True, exist_ok=True)
        (root / "approval_queue" / "pending").mkdir(parents=True, exist_ok=True)
        (root / "docs").mkdir(parents=True, exist_ok=True)
        (root / "config" / "gates.yaml").write_text(
            (repo_root / "config" / "gates.yaml").read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    def _bootstrap(self, root: Path, run_id: str) -> None:
        exit_code = main(
            [
                "bootstrap-run",
                "--root",
                str(root),
                "--run-id",
                run_id,
                "--pr-id",
                "PR-002",
                "--work-item-id",
                "WI-002",
                "--work-item-title",
                "verification gate hardening",
            ]
        )
        self.assertEqual(exit_code, 0)

    def _record_verification(
        self,
        root: Path,
        run_id: str,
        *,
        lint: str = "pass",
        tests: str = "pass",
        type_check: str = "pass",
        build: str = "pass",
    ) -> None:
        self.assertEqual(
            main(
                [
                    "record-verification",
                    "--root",
                    str(root),
                    "--run-id",
                    run_id,
                    "--lint",
                    lint,
                    "--tests",
                    tests,
                    "--type-check",
                    type_check,
                    "--build",
                    build,
                    "--summary",
                    "verification recorded",
                ]
            ),
            0,
        )

    def _record_non_verification_ready(self, root: Path, run_id: str) -> None:
        self.assertEqual(
            main(["record-review", "--root", str(root), "--run-id", run_id, "--status", "pass", "--summary", "review ok"]),
            0,
        )
        self.assertEqual(main(["record-qa", "--root", str(root), "--run-id", run_id, "--status", "pass", "--summary", "qa ok"]), 0)
        self.assertEqual(
            main(["record-docs-sync", "--root", str(root), "--run-id", run_id, "--status", "complete", "--summary", "docs synced"]),
            0,
        )

    def _build_approval(self, root: Path, run_id: str) -> None:
        self.assertEqual(main(["build-approval", "--root", str(root), "--run-id", run_id]), 0)

    def test_happy_path(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-HAPPY"
            self._prepare_root(root)
            self._bootstrap(root, run_id)

            self._record_verification(root, run_id)
            self._record_non_verification_ready(root, run_id)
            self._build_approval(root, run_id)

            evidence = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "evidence-bundle.yaml")
            gate = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "gate-status.yaml")
            approval = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "approval-request.yaml")

            self.assertEqual(evidence["evidence_bundle"]["checks"]["type_check"]["status"], "pass")
            self.assertEqual(gate["gate_status"]["gates"]["merge_approval"], "ready")
            self.assertEqual(approval["approval_request"]["recommended_decision"], "approve")
            self.assertTrue((root / "approval_queue" / "pending" / f"APR-{run_id}.yaml").exists())

    def test_lint_fail(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-LINT-FAIL"
            self._prepare_root(root)
            self._bootstrap(root, run_id)

            self._record_verification(root, run_id, lint="fail")
            self._record_non_verification_ready(root, run_id)
            self._build_approval(root, run_id)

            gate = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "gate-status.yaml")
            self.assertEqual(gate["gate_status"]["gates"]["merge_approval"], "exception_required")
            self.assertNotEqual(gate["gate_status"]["gates"]["merge_approval"], "ready")

    def test_tests_fail(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-TESTS-FAIL"
            self._prepare_root(root)
            self._bootstrap(root, run_id)

            self._record_verification(root, run_id, tests="fail")
            self._record_non_verification_ready(root, run_id)
            self._build_approval(root, run_id)

            gate = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "gate-status.yaml")
            self.assertEqual(gate["gate_status"]["gates"]["merge_approval"], "exception_required")
            self.assertNotEqual(gate["gate_status"]["gates"]["merge_approval"], "ready")

    def test_type_check_fail(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-TYPE-CHECK-FAIL"
            self._prepare_root(root)
            self._bootstrap(root, run_id)

            self._record_verification(root, run_id, type_check="fail")
            self._record_non_verification_ready(root, run_id)
            self._build_approval(root, run_id)

            gate = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "gate-status.yaml")
            self.assertEqual(gate["gate_status"]["gates"]["merge_approval"], "exception_required")
            self.assertNotEqual(gate["gate_status"]["gates"]["merge_approval"], "ready")

    def test_build_fail(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-BUILD-FAIL"
            self._prepare_root(root)
            self._bootstrap(root, run_id)

            self._record_verification(root, run_id, build="fail")
            self._record_non_verification_ready(root, run_id)
            self._build_approval(root, run_id)

            gate = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "gate-status.yaml")
            self.assertEqual(gate["gate_status"]["gates"]["merge_approval"], "exception_required")
            self.assertNotEqual(gate["gate_status"]["gates"]["merge_approval"], "ready")

    def test_verification_missing(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-VERIFICATION-MISSING"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            self._record_non_verification_ready(root, run_id)

            verification_path = root / "runs" / "latest" / run_id / "artifacts" / "verification-report.yaml"
            verification_path.unlink()

            with self.assertRaises(ValueError):
                main(["build-approval", "--root", str(root), "--run-id", run_id])

            self.assertFalse((root / "approval_queue" / "pending" / f"APR-{run_id}.yaml").exists())


if __name__ == "__main__":
    unittest.main()
