from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from orchestrator.cli import main
from orchestrator.yaml_io import read_yaml, write_yaml


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

    def _bootstrap(self, root: Path, run_id: str = "RUN-LOOP") -> None:
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
                "minimal approval loop",
            ]
        )
        self.assertEqual(exit_code, 0)

    def test_happy_path(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prepare_root(root)
            self._bootstrap(root, "RUN-HAPPY")

            self.assertEqual(main(["record-review", "--root", str(root), "--run-id", "RUN-HAPPY", "--status", "pass", "--summary", "review ok"]), 0)
            self.assertEqual(main(["record-qa", "--root", str(root), "--run-id", "RUN-HAPPY", "--status", "pass", "--summary", "qa ok"]), 0)
            self.assertEqual(main(["record-docs-sync", "--root", str(root), "--run-id", "RUN-HAPPY", "--status", "complete", "--summary", "docs synced"]), 0)
            self.assertEqual(main(["build-approval", "--root", str(root), "--run-id", "RUN-HAPPY"]), 0)

            evidence = read_yaml(root / "runs" / "latest" / "RUN-HAPPY" / "artifacts" / "evidence-bundle.yaml")
            gate = read_yaml(root / "runs" / "latest" / "RUN-HAPPY" / "artifacts" / "gate-status.yaml")
            approval = read_yaml(root / "runs" / "latest" / "RUN-HAPPY" / "artifacts" / "approval-request.yaml")
            run = read_yaml(root / "runs" / "latest" / "RUN-HAPPY" / "run.yaml")

            self.assertEqual(evidence["evidence_bundle"]["status"], "complete")
            self.assertEqual(gate["gate_status"]["gates"]["merge_approval"], "ready")
            self.assertEqual(approval["approval_request"]["recommended_decision"], "approve")
            self.assertTrue((root / "approval_queue" / "pending" / "APR-RUN-HAPPY.yaml").exists())
            self.assertEqual(run["run"]["docs_sync_verdict"], "complete")

    def test_review_fail(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prepare_root(root)
            self._bootstrap(root, "RUN-REVIEW-FAIL")

            self.assertEqual(main(["record-review", "--root", str(root), "--run-id", "RUN-REVIEW-FAIL", "--status", "fail", "--summary", "must fix"]), 0)
            self.assertEqual(main(["record-qa", "--root", str(root), "--run-id", "RUN-REVIEW-FAIL", "--status", "pass", "--summary", "qa ok"]), 0)
            self.assertEqual(main(["record-docs-sync", "--root", str(root), "--run-id", "RUN-REVIEW-FAIL", "--status", "complete", "--summary", "docs synced"]), 0)
            self.assertEqual(main(["build-approval", "--root", str(root), "--run-id", "RUN-REVIEW-FAIL"]), 0)

            gate = read_yaml(root / "runs" / "latest" / "RUN-REVIEW-FAIL" / "artifacts" / "gate-status.yaml")
            approval = read_yaml(root / "runs" / "latest" / "RUN-REVIEW-FAIL" / "artifacts" / "approval-request.yaml")

            self.assertEqual(gate["gate_status"]["gates"]["merge_approval"], "blocked")
            self.assertEqual(approval["approval_request"]["recommended_decision"], "request_changes")
            self.assertFalse((root / "approval_queue" / "pending" / "APR-RUN-REVIEW-FAIL.yaml").exists())

    def test_qa_fail(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prepare_root(root)
            self._bootstrap(root, "RUN-QA-FAIL")

            self.assertEqual(main(["record-review", "--root", str(root), "--run-id", "RUN-QA-FAIL", "--status", "pass", "--summary", "review ok"]), 0)
            self.assertEqual(main(["record-qa", "--root", str(root), "--run-id", "RUN-QA-FAIL", "--status", "fail", "--summary", "regression found"]), 0)
            self.assertEqual(main(["record-docs-sync", "--root", str(root), "--run-id", "RUN-QA-FAIL", "--status", "complete", "--summary", "docs synced"]), 0)
            self.assertEqual(main(["build-approval", "--root", str(root), "--run-id", "RUN-QA-FAIL"]), 0)

            gate = read_yaml(root / "runs" / "latest" / "RUN-QA-FAIL" / "artifacts" / "gate-status.yaml")
            approval = read_yaml(root / "runs" / "latest" / "RUN-QA-FAIL" / "artifacts" / "approval-request.yaml")

            self.assertEqual(gate["gate_status"]["gates"]["merge_approval"], "blocked")
            self.assertEqual(approval["approval_request"]["recommended_decision"], "request_changes")
            self.assertFalse((root / "approval_queue" / "pending" / "APR-RUN-QA-FAIL.yaml").exists())

    def test_docs_sync_incomplete(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prepare_root(root)
            self._bootstrap(root, "RUN-DOCS-PENDING")

            self.assertEqual(main(["record-review", "--root", str(root), "--run-id", "RUN-DOCS-PENDING", "--status", "pass", "--summary", "review ok"]), 0)
            self.assertEqual(main(["record-qa", "--root", str(root), "--run-id", "RUN-DOCS-PENDING", "--status", "pass", "--summary", "qa ok"]), 0)
            self.assertEqual(main(["record-docs-sync", "--root", str(root), "--run-id", "RUN-DOCS-PENDING", "--status", "required", "--summary", "docs pending"]), 0)
            self.assertEqual(main(["build-approval", "--root", str(root), "--run-id", "RUN-DOCS-PENDING"]), 0)

            gate = read_yaml(root / "runs" / "latest" / "RUN-DOCS-PENDING" / "artifacts" / "gate-status.yaml")
            approval = read_yaml(root / "runs" / "latest" / "RUN-DOCS-PENDING" / "artifacts" / "approval-request.yaml")

            self.assertEqual(gate["gate_status"]["gates"]["merge_approval"], "pending")
            self.assertEqual(approval["approval_request"]["recommended_decision"], "reject")
            self.assertFalse((root / "approval_queue" / "pending" / "APR-RUN-DOCS-PENDING.yaml").exists())

    def test_exception_required(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prepare_root(root)
            self._bootstrap(root, "RUN-EXCEPTION")

            self.assertEqual(main(["record-review", "--root", str(root), "--run-id", "RUN-EXCEPTION", "--status", "pass", "--summary", "review ok"]), 0)
            self.assertEqual(main(["record-qa", "--root", str(root), "--run-id", "RUN-EXCEPTION", "--status", "pass", "--summary", "qa ok"]), 0)
            self.assertEqual(main(["record-docs-sync", "--root", str(root), "--run-id", "RUN-EXCEPTION", "--status", "complete", "--summary", "docs synced"]), 0)

            evidence_path = root / "runs" / "latest" / "RUN-EXCEPTION" / "artifacts" / "evidence-bundle.yaml"
            evidence = read_yaml(evidence_path)
            evidence["evidence_bundle"]["checks"]["test"] = {"status": "fail", "notes": "flake"}
            evidence["evidence_bundle"]["checks"]["lint"] = {"status": "pass", "notes": "ok"}
            evidence["evidence_bundle"]["checks"]["build"] = {"status": "pass", "notes": "ok"}
            write_yaml(evidence_path, evidence)

            self.assertEqual(main(["build-approval", "--root", str(root), "--run-id", "RUN-EXCEPTION"]), 0)

            gate = read_yaml(root / "runs" / "latest" / "RUN-EXCEPTION" / "artifacts" / "gate-status.yaml")
            approval = read_yaml(root / "runs" / "latest" / "RUN-EXCEPTION" / "artifacts" / "approval-request.yaml")

            self.assertEqual(gate["gate_status"]["gates"]["merge_approval"], "exception_required")
            self.assertEqual(gate["gate_status"]["gates"]["exception_approval"], "required")
            self.assertEqual(approval["approval_request"]["gate_type"], "exception_approval")
            self.assertEqual(approval["approval_request"]["recommended_decision"], "approve_with_exception")
            self.assertTrue((root / "approval_queue" / "pending" / "APR-RUN-EXCEPTION.yaml").exists())


if __name__ == "__main__":
    unittest.main()
