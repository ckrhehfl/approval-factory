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

    def _write_work_item(
        self,
        root: Path,
        *,
        work_item_id: str,
        goal_id: str,
        related_lines: list[str] | None = None,
    ) -> None:
        (root / "docs" / "work-items").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "work-items" / f"{work_item_id}.md").write_text(
            "\n".join(
                [
                    f"# {work_item_id}: readiness source",
                    "",
                    "## Work Item ID",
                    work_item_id,
                    "",
                    "## Goal ID",
                    goal_id,
                    "",
                    "## Title",
                    "readiness source",
                    "",
                    "## Status",
                    "draft",
                    "",
                    "## Description",
                    "Source work item for approval readiness visibility tests.",
                    "",
                    "## Related Clarifications",
                    *(related_lines or ["- none"]),
                    "",
                    "## Scope",
                    "- TBD",
                    "",
                    "## Out of Scope",
                    "- TBD",
                    "",
                    "## Acceptance Criteria",
                    "TBD",
                    "",
                    "## Dependencies",
                    "- TBD",
                    "",
                    "## Risks",
                    "- TBD",
                    "",
                    "## Notes",
                    "- TBD",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def _write_clarification(self, root: Path, *, goal_id: str, clarification_id: str, status: str) -> None:
        (root / "clarifications" / goal_id).mkdir(parents=True, exist_ok=True)
        (root / "clarifications" / goal_id / f"{clarification_id}.md").write_text(
            "\n".join(
                [
                    f"# {clarification_id}: readiness detail",
                    "",
                    "## Clarification ID",
                    clarification_id,
                    "",
                    "## Goal ID",
                    goal_id,
                    "",
                    "## Title",
                    "readiness detail",
                    "",
                    "## Status",
                    status,
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def _resolve_approval(self, root: Path, run_id: str, decision: str) -> None:
        self.assertEqual(
            main(
                [
                    "resolve-approval",
                    "--root",
                    str(root),
                    "--run-id",
                    run_id,
                    "--decision",
                    decision,
                    "--actor",
                    "approver.local",
                    "--note",
                    f"{decision} recorded",
                ]
            ),
            0,
        )

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

    def test_build_approval_fails_when_review_was_not_recorded(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-REVIEW-MISSING"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            self._record_verification(root, run_id)
            self.assertEqual(main(["record-qa", "--root", str(root), "--run-id", run_id, "--status", "pass", "--summary", "qa ok"]), 0)
            self.assertEqual(
                main(["record-docs-sync", "--root", str(root), "--run-id", run_id, "--status", "complete", "--summary", "docs synced"]),
                0,
            )

            with self.assertRaisesRegex(ValueError, "record-review"):
                main(["build-approval", "--root", str(root), "--run-id", run_id])

    def test_build_approval_fails_when_docs_sync_was_not_recorded(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-DOCS-MISSING"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            self._record_verification(root, run_id)
            self.assertEqual(
                main(["record-review", "--root", str(root), "--run-id", run_id, "--status", "pass", "--summary", "review ok"]),
                0,
            )
            self.assertEqual(main(["record-qa", "--root", str(root), "--run-id", run_id, "--status", "pass", "--summary", "qa ok"]), 0)

            with self.assertRaisesRegex(ValueError, "record-docs-sync"):
                main(["build-approval", "--root", str(root), "--run-id", run_id])

    def test_duplicate_build_approval_is_idempotent(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-DUP-BUILD"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            self._record_verification(root, run_id)
            self._record_non_verification_ready(root, run_id)

            self._build_approval(root, run_id)
            self._build_approval(root, run_id)

            queue_files = sorted((root / "approval_queue" / "pending").glob(f"APR-{run_id}*.yaml"))
            self.assertEqual(len(queue_files), 1)
            run_payload = read_yaml(root / "runs" / "latest" / run_id / "run.yaml")
            self.assertEqual(run_payload["run"]["operations"]["build_approval"]["count"], 2)

    def test_duplicate_gate_check_keeps_single_canonical_artifact(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-DUP-GATE"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            self._record_verification(root, run_id)
            self._record_non_verification_ready(root, run_id)

            self.assertEqual(main(["gate-check", "--root", str(root), "--run-id", run_id]), 0)
            self.assertEqual(main(["gate-check", "--root", str(root), "--run-id", run_id]), 0)

            gate = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "gate-status.yaml")
            self.assertEqual(gate["gate_status"]["gates"]["merge_approval"], "pending")
            self.assertEqual(len(list((root / "runs" / "latest" / run_id / "artifacts").glob("gate-status*.yaml"))), 1)
            run_payload = read_yaml(root / "runs" / "latest" / run_id / "run.yaml")
            self.assertEqual(run_payload["run"]["operations"]["gate_check"]["count"], 2)

    def test_queue_file_collision_creates_retry_suffix(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-COLLISION"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            self._record_verification(root, run_id)
            self._record_non_verification_ready(root, run_id)

            pending = root / "approval_queue" / "pending"
            (pending / f"APR-{run_id}.yaml").write_text(
                "approval_request:\n  id: APR-RUN-COLLISION\n  recommended_decision: reject\n",
                encoding="utf-8",
            )

            self._build_approval(root, run_id)

            self.assertTrue((pending / f"APR-{run_id}.yaml").exists())
            self.assertTrue((pending / f"APR-{run_id}--r2.yaml").exists())

    def test_bootstrap_rerun_does_not_reset_existing_artifacts(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-RERUN-SAFE"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            self._record_verification(root, run_id, lint="fail")

            self._bootstrap(root, run_id)

            verification = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "verification-report.yaml")
            self.assertEqual(verification["verification_report"]["lint"], "fail")

    def test_resolve_approval_approve_moves_queue_and_records_decision(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-RESOLVE-APPROVE"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            self._record_verification(root, run_id)
            self._record_non_verification_ready(root, run_id)
            self._build_approval(root, run_id)

            self._resolve_approval(root, run_id, "approve")

            self.assertFalse((root / "approval_queue" / "pending" / f"APR-{run_id}.yaml").exists())
            self.assertTrue((root / "approval_queue" / "approved" / f"APR-{run_id}.yaml").exists())
            decision = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "approval-decision.yaml")
            payload = decision["approval_decision"]
            self.assertEqual(payload["run_id"], run_id)
            self.assertEqual(payload["decision"], "approve")
            self.assertEqual(payload["actor"], "approver.local")
            self.assertEqual(payload["source_queue_item"], f"approval_queue/pending/APR-{run_id}.yaml")
            self.assertEqual(payload["target_queue_item"], f"approval_queue/approved/APR-{run_id}.yaml")

    def test_resolve_approval_reject_moves_queue_and_records_decision(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-RESOLVE-REJECT"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            self._record_verification(root, run_id)
            self._record_non_verification_ready(root, run_id)
            self._build_approval(root, run_id)

            self._resolve_approval(root, run_id, "reject")

            self.assertFalse((root / "approval_queue" / "pending" / f"APR-{run_id}.yaml").exists())
            self.assertTrue((root / "approval_queue" / "rejected" / f"APR-{run_id}.yaml").exists())
            decision = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "approval-decision.yaml")
            self.assertEqual(decision["approval_decision"]["decision"], "reject")

    def test_resolve_approval_exception_moves_queue_and_records_decision(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-RESOLVE-EXCEPTION"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            self._record_verification(root, run_id, tests="fail")
            self._record_non_verification_ready(root, run_id)
            self._build_approval(root, run_id)

            self._resolve_approval(root, run_id, "exception")

            self.assertFalse((root / "approval_queue" / "pending" / f"APR-{run_id}.yaml").exists())
            self.assertTrue((root / "approval_queue" / "exceptions" / f"APR-{run_id}.yaml").exists())
            decision = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "approval-decision.yaml")
            self.assertEqual(decision["approval_decision"]["decision"], "exception")

    def test_resolve_approval_is_idempotent_after_first_resolution(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-RESOLVE-IDEMPOTENT"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            self._record_verification(root, run_id)
            self._record_non_verification_ready(root, run_id)
            self._build_approval(root, run_id)

            self._resolve_approval(root, run_id, "approve")
            self._resolve_approval(root, run_id, "approve")

            self.assertFalse((root / "approval_queue" / "pending" / f"APR-{run_id}.yaml").exists())
            self.assertTrue((root / "approval_queue" / "approved" / f"APR-{run_id}.yaml").exists())
            run_payload = read_yaml(root / "runs" / "latest" / run_id / "run.yaml")
            self.assertEqual(run_payload["run"]["operations"]["resolve_approval"]["count"], 2)

    def test_resolve_approval_fails_without_pending_queue_item(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-NO-PENDING"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            self._record_verification(root, run_id)
            self._record_non_verification_ready(root, run_id)
            main(["build-approval", "--root", str(root), "--run-id", run_id])
            (root / "approval_queue" / "pending" / f"APR-{run_id}.yaml").unlink()

            with self.assertRaisesRegex(ValueError, "pending queue item"):
                main(
                    [
                        "resolve-approval",
                        "--root",
                        str(root),
                        "--run-id",
                        run_id,
                        "--decision",
                        "approve",
                        "--actor",
                        "approver.local",
                        "--note",
                        "approve without queue item",
                    ]
                )

    def test_resolve_approval_fails_without_built_approval_request(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-NO-APPROVAL-REQUEST"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            approval_path = root / "runs" / "latest" / run_id / "artifacts" / "approval-request.yaml"
            approval_path.unlink()

            with self.assertRaisesRegex(ValueError, "approval request artifact"):
                main(
                    [
                        "resolve-approval",
                        "--root",
                        str(root),
                        "--run-id",
                        run_id,
                        "--decision",
                        "approve",
                        "--actor",
                        "approver.local",
                        "--note",
                        "approve without approval request",
                    ]
                )

    def test_resolve_approval_fails_when_already_resolved_to_other_queue(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-RESOLVE-CONFLICT"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            self._record_verification(root, run_id)
            self._record_non_verification_ready(root, run_id)
            self._build_approval(root, run_id)

            self._resolve_approval(root, run_id, "approve")
            with self.assertRaises(ValueError):
                main(
                    [
                        "resolve-approval",
                        "--root",
                        str(root),
                        "--run-id",
                        run_id,
                        "--decision",
                        "reject",
                        "--actor",
                        "approver.local",
                        "--note",
                        "reject after approval",
                    ]
                )

    def test_state_transitions_follow_execution_flow(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-STATE"
            self._prepare_root(root)
            self._bootstrap(root, run_id)

            run_payload = read_yaml(root / "runs" / "latest" / run_id / "run.yaml")
            self.assertEqual(run_payload["run"]["state"], "draft")

            self._record_verification(root, run_id)
            run_payload = read_yaml(root / "runs" / "latest" / run_id / "run.yaml")
            self.assertEqual(run_payload["run"]["state"], "in_progress")

            self._record_non_verification_ready(root, run_id)
            run_payload = read_yaml(root / "runs" / "latest" / run_id / "run.yaml")
            self.assertEqual(run_payload["run"]["state"], "in_progress")

            self._build_approval(root, run_id)
            run_payload = read_yaml(root / "runs" / "latest" / run_id / "run.yaml")
            self.assertEqual(run_payload["run"]["state"], "approval_pending")

            self._resolve_approval(root, run_id, "approve")
            run_payload = read_yaml(root / "runs" / "latest" / run_id / "run.yaml")
            self.assertEqual(run_payload["run"]["state"], "approved")

    def test_build_approval_records_no_linked_clarifications_readiness_context(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-READINESS-NONE"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            self._write_work_item(root, work_item_id="WI-002", goal_id="GOAL-002")
            self._record_verification(root, run_id)
            self._record_non_verification_ready(root, run_id)

            self._build_approval(root, run_id)

            evidence = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "evidence-bundle.yaml")
            approval = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "approval-request.yaml")
            evidence_readiness = evidence["evidence_bundle"]["readiness_context"]
            approval_readiness = approval["approval_request"]["readiness_context"]

            self.assertEqual(evidence_readiness["status"], "available")
            self.assertEqual(evidence_readiness["readiness_summary"], "no-linked-clarifications")
            self.assertEqual(evidence_readiness["linked_clarification_count"], 0)
            self.assertEqual(evidence_readiness["readiness_source"]["work_item_id"], "WI-002")
            self.assertEqual(approval_readiness["readiness_summary"], "no-linked-clarifications")

    def test_build_approval_records_ready_readiness_context(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-READINESS-READY"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            self._write_work_item(
                root,
                work_item_id="WI-002",
                goal_id="GOAL-READY",
                related_lines=["- CLAR-001 (open)", "- CLAR-002 (resolved)"],
            )
            self._write_clarification(root, goal_id="GOAL-READY", clarification_id="CLAR-001", status="resolved")
            self._write_clarification(root, goal_id="GOAL-READY", clarification_id="CLAR-002", status="resolved")
            self._record_verification(root, run_id)
            self._record_non_verification_ready(root, run_id)

            self._build_approval(root, run_id)

            approval = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "approval-request.yaml")
            readiness = approval["approval_request"]["readiness_context"]
            self.assertEqual(readiness["status"], "available")
            self.assertEqual(readiness["readiness_summary"], "ready")
            self.assertEqual(readiness["linked_clarification_count"], 2)
            self.assertEqual(
                readiness["linked_clarifications"],
                [
                    {"clarification_id": "CLAR-001", "status": "resolved"},
                    {"clarification_id": "CLAR-002", "status": "resolved"},
                ],
            )
            self.assertTrue((root / "approval_queue" / "pending" / f"APR-{run_id}.yaml").exists())

    def test_build_approval_records_attention_needed_readiness_context_without_changing_queue_semantics(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-READINESS-ATTN"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            self._write_work_item(
                root,
                work_item_id="WI-002",
                goal_id="GOAL-ATTN",
                related_lines=["- CLAR-001 (resolved)", "- CLAR-002 (resolved)", "- CLAR-003 (resolved)"],
            )
            self._write_clarification(root, goal_id="GOAL-ATTN", clarification_id="CLAR-001", status="open")
            self._write_clarification(root, goal_id="GOAL-ATTN", clarification_id="CLAR-002", status="deferred")
            self._write_clarification(root, goal_id="GOAL-ATTN", clarification_id="CLAR-003", status="escalated")
            self._record_verification(root, run_id)
            self._record_non_verification_ready(root, run_id)

            self._build_approval(root, run_id)

            evidence = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "evidence-bundle.yaml")
            gate = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "gate-status.yaml")
            readiness = evidence["evidence_bundle"]["readiness_context"]
            self.assertEqual(readiness["status"], "available")
            self.assertEqual(readiness["readiness_summary"], "attention-needed")
            self.assertEqual(readiness["linked_clarification_count"], 3)
            self.assertEqual(gate["gate_status"]["gates"]["merge_approval"], "ready")
            self.assertTrue((root / "approval_queue" / "pending" / f"APR-{run_id}.yaml").exists())

    def test_build_approval_marks_readiness_unavailable_without_failing_or_changing_queue_semantics(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-READINESS-UNAVAILABLE"
            self._prepare_root(root)
            self._bootstrap(root, run_id)
            self._record_verification(root, run_id)
            self._record_non_verification_ready(root, run_id)

            self._build_approval(root, run_id)

            evidence = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "evidence-bundle.yaml")
            approval = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "approval-request.yaml")
            gate = read_yaml(root / "runs" / "latest" / run_id / "artifacts" / "gate-status.yaml")
            self.assertEqual(evidence["evidence_bundle"]["readiness_context"]["status"], "unavailable")
            self.assertIn("work item artifact was not found", evidence["evidence_bundle"]["readiness_context"]["reason"])
            self.assertEqual(approval["approval_request"]["readiness_context"]["status"], "unavailable")
            self.assertEqual(gate["gate_status"]["gates"]["merge_approval"], "ready")
            self.assertTrue((root / "approval_queue" / "pending" / f"APR-{run_id}.yaml").exists())


if __name__ == "__main__":
    unittest.main()
