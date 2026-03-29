from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from tempfile import TemporaryDirectory
import unittest

from orchestrator.cli import main
from orchestrator.yaml_io import read_yaml


class BootstrapCliTest(unittest.TestCase):
    def test_bootstrap_run_creates_canonical_artifacts(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_id = "RUN-001"
            pr_id = "PR-001"
            work_item_id = "WI-001"

            exit_code = main(
                [
                    "bootstrap-run",
                    "--root",
                    str(root),
                    "--run-id",
                    run_id,
                    "--pr-id",
                    pr_id,
                    "--work-item-id",
                    work_item_id,
                    "--work-item-title",
                    "Contract Artifact IO",
                ]
            )

            self.assertEqual(exit_code, 0)

            run_root = root / "runs" / "latest" / run_id
            self.assertTrue((run_root / "run.yaml").exists())

            artifacts = run_root / "artifacts"
            self.assertTrue((artifacts / "work-item.yaml").exists())
            self.assertTrue((artifacts / "pr-plan.yaml").exists())
            self.assertTrue((artifacts / "verification-report.yaml").exists())
            self.assertTrue((artifacts / "review-report.yaml").exists())
            self.assertTrue((artifacts / "qa-report.yaml").exists())
            self.assertTrue((artifacts / "docs-sync-report.yaml").exists())
            self.assertTrue((artifacts / "evidence-bundle.yaml").exists())
            self.assertTrue((artifacts / "approval-request.yaml").exists())
            self.assertTrue((artifacts / "gate-status.yaml").exists())

            pr_docs = root / "docs" / "prs" / pr_id
            self.assertTrue((pr_docs / "scope.md").exists())
            self.assertTrue((pr_docs / "plan.md").exists())
            self.assertTrue((pr_docs / "review.md").exists())
            self.assertTrue((pr_docs / "qa.md").exists())
            self.assertTrue((pr_docs / "docs-sync.md").exists())
            self.assertTrue((pr_docs / "evidence.md").exists())
            self.assertTrue((pr_docs / "decision.md").exists())


class CreateGoalCliTest(unittest.TestCase):
    def test_create_goal_creates_markdown_artifact(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            exit_code = main(
                [
                    "create-goal",
                    "--root",
                    str(root),
                    "--goal-id",
                    "GOAL-007",
                    "--title",
                    "Goal intake contract",
                    "--problem",
                    "People need a formal way to persist project goals.",
                    "--outcome",
                    "A readable goal artifact exists in the repo.",
                    "--constraints",
                    "repo-local\nfile-based",
                ]
            )

            self.assertEqual(exit_code, 0)

            goal_path = root / "goals" / "GOAL-007.md"
            self.assertTrue(goal_path.exists())

            content = goal_path.read_text(encoding="utf-8")
            self.assertIn("# GOAL-007: Goal intake contract", content)
            self.assertIn("## Goal ID\nGOAL-007", content)
            self.assertIn("## Status\ndraft", content)
            self.assertIn("## Problem\nPeople need a formal way to persist project goals.", content)
            self.assertIn("## Desired Outcome\nA readable goal artifact exists in the repo.", content)
            self.assertIn("## Constraints\nrepo-local\nfile-based", content)
            self.assertIn("## Non-Goals\n- TBD", content)
            self.assertIn("## Risks\n- TBD", content)
            self.assertIn("## Open Questions\n- TBD", content)
            self.assertIn("## Approval-Required Decisions\n- TBD", content)
            self.assertIn("## Success Criteria\n- TBD", content)

    def test_create_goal_rejects_duplicate_goal_id(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            first_exit_code = main(
                [
                    "create-goal",
                    "--root",
                    str(root),
                    "--goal-id",
                    "GOAL-007",
                    "--title",
                    "Goal intake contract",
                    "--problem",
                    "Need a formal intake contract.",
                    "--outcome",
                    "Goal artifact exists.",
                ]
            )
            self.assertEqual(first_exit_code, 0)

            with self.assertRaises(SystemExit) as exc_info:
                main(
                    [
                        "create-goal",
                        "--root",
                        str(root),
                        "--goal-id",
                        "GOAL-007",
                        "--title",
                        "Goal intake contract",
                        "--problem",
                        "Need a formal intake contract.",
                        "--outcome",
                        "Goal artifact exists.",
                    ]
                )

            self.assertEqual(exc_info.exception.code, 2)


class CreateClarificationCliTest(unittest.TestCase):
    def test_create_clarification_creates_markdown_artifact(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            exit_code = main(
                [
                    "create-clarification",
                    "--root",
                    str(root),
                    "--goal-id",
                    "GOAL-008",
                    "--clarification-id",
                    "CLAR-001",
                    "--title",
                    "Need scope boundary",
                    "--category",
                    "scope",
                    "--question",
                    "What is explicitly out of scope for this goal?",
                    "--escalation",
                ]
            )

            self.assertEqual(exit_code, 0)

            clarification_path = root / "clarifications" / "GOAL-008" / "CLAR-001.md"
            self.assertTrue(clarification_path.exists())

            content = clarification_path.read_text(encoding="utf-8")
            self.assertIn("# CLAR-001: Need scope boundary", content)
            self.assertIn("## Clarification ID\nCLAR-001", content)
            self.assertIn("## Goal ID\nGOAL-008", content)
            self.assertIn("## Title\nNeed scope boundary", content)
            self.assertIn("## Status\nopen", content)
            self.assertIn("## Category\nscope", content)
            self.assertIn("## Question\nWhat is explicitly out of scope for this goal?", content)
            self.assertIn("## Suggested Resolution\n- TBD", content)
            self.assertIn("## Escalation Required\nyes", content)
            self.assertIn("## Resolution Notes\n- TBD", content)
            self.assertIn("## Next Action\n- TBD", content)

    def test_create_clarification_rejects_duplicate_clarification_id(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            first_exit_code = main(
                [
                    "create-clarification",
                    "--root",
                    str(root),
                    "--goal-id",
                    "GOAL-008",
                    "--clarification-id",
                    "CLAR-001",
                    "--title",
                    "Need scope boundary",
                    "--category",
                    "scope",
                    "--question",
                    "What is explicitly out of scope for this goal?",
                ]
            )
            self.assertEqual(first_exit_code, 0)

            with self.assertRaises(SystemExit) as exc_info:
                main(
                    [
                        "create-clarification",
                        "--root",
                        str(root),
                        "--goal-id",
                        "GOAL-008",
                        "--clarification-id",
                        "CLAR-001",
                        "--title",
                        "Need scope boundary",
                        "--category",
                        "scope",
                        "--question",
                        "What is explicitly out of scope for this goal?",
                    ]
                )

            self.assertEqual(exc_info.exception.code, 2)

    def test_create_clarification_rejects_invalid_category(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            with self.assertRaises(SystemExit) as exc_info:
                main(
                    [
                        "create-clarification",
                        "--root",
                        str(root),
                        "--goal-id",
                        "GOAL-008",
                        "--clarification-id",
                        "CLAR-001",
                        "--title",
                        "Need scope boundary",
                        "--category",
                        "unknown",
                        "--question",
                        "What is explicitly out of scope for this goal?",
                    ]
                )

            self.assertEqual(exc_info.exception.code, 2)


class ResolveClarificationCliTest(unittest.TestCase):
    def _write_open_clarification(self, root, *, goal_id: str = "GOAL-018", clarification_id: str = "CLAR-001") -> None:
        (root / "clarifications" / goal_id).mkdir(parents=True, exist_ok=True)
        (root / "clarifications" / goal_id / f"{clarification_id}.md").write_text(
            "\n".join(
                [
                    f"# {clarification_id}: clarify resolution contract",
                    "",
                    "## Clarification ID",
                    clarification_id,
                    "",
                    "## Goal ID",
                    goal_id,
                    "",
                    "## Title",
                    "clarify resolution contract",
                    "",
                    "## Status",
                    "open",
                    "",
                    "## Category",
                    "scope",
                    "",
                    "## Question",
                    "How should operators close the clarification queue item?",
                    "",
                    "## Suggested Resolution",
                    "- TBD",
                    "",
                    "## Escalation Required",
                    "no",
                    "",
                    "## Resolution Notes",
                    "- TBD",
                    "",
                    "## Next Action",
                    "- TBD",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def test_resolve_clarification_updates_artifact_fields(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_open_clarification(root)

            exit_code = main(
                [
                    "resolve-clarification",
                    "--root",
                    str(root),
                    "--goal-id",
                    "GOAL-018",
                    "--clarification-id",
                    "CLAR-001",
                    "--decision",
                    "escalated",
                    "--resolution-notes",
                    "Operator cannot decide this without approver input.",
                    "--next-action",
                    "Escalate the scope tradeoff to the approver.",
                    "--suggested-resolution",
                    "Keep manual closure and ask the approver for the boundary.",
                ]
            )

            self.assertEqual(exit_code, 0)

            content = (root / "clarifications" / "GOAL-018" / "CLAR-001.md").read_text(encoding="utf-8")
            self.assertIn("## Status\nescalated", content)
            self.assertIn("## Resolution Notes\nOperator cannot decide this without approver input.", content)
            self.assertIn("## Next Action\nEscalate the scope tradeoff to the approver.", content)
            self.assertIn("## Escalation Required\nyes", content)
            self.assertIn(
                "## Suggested Resolution\nKeep manual closure and ask the approver for the boundary.",
                content,
            )
            self.assertIn("## Question\nHow should operators close the clarification queue item?", content)

    def test_resolved_deferred_and_escalated_clarifications_disappear_from_status(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for goal_id, clarification_id, decision in (
                ("GOAL-018-A", "CLAR-001", "resolved"),
                ("GOAL-018-B", "CLAR-002", "deferred"),
                ("GOAL-018-C", "CLAR-003", "escalated"),
            ):
                self._write_open_clarification(root, goal_id=goal_id, clarification_id=clarification_id)
                self.assertEqual(
                    main(
                        [
                            "resolve-clarification",
                            "--root",
                            str(root),
                            "--goal-id",
                            goal_id,
                            "--clarification-id",
                            clarification_id,
                            "--decision",
                            decision,
                            "--resolution-notes",
                            f"{decision} notes",
                            "--next-action",
                            f"{decision} next action",
                        ]
                    ),
                    0,
                )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["status", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                stdout.getvalue(),
                "\n".join(
                    [
                        "Active PR:",
                        "- none",
                        "",
                        "Latest Run:",
                        "- none",
                        "",
                        "Approval:",
                        "- status: none",
                    ]
                )
                + "\n",
            )

    def test_resolve_clarification_fails_when_artifact_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "resolve-clarification",
                            "--root",
                            str(root),
                            "--goal-id",
                            "GOAL-018",
                            "--clarification-id",
                            "CLAR-404",
                            "--decision",
                            "resolved",
                            "--resolution-notes",
                            "done",
                            "--next-action",
                            "none",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("artifact was not found", error_output)
            self.assertIn((root / "clarifications" / "GOAL-018" / "CLAR-404.md").as_posix(), error_output)
            self.assertIn("create it first with `factory create-clarification", error_output)

    def test_resolve_clarification_fails_when_status_is_not_open(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_open_clarification(root)
            self.assertEqual(
                main(
                    [
                        "resolve-clarification",
                        "--root",
                        str(root),
                        "--goal-id",
                        "GOAL-018",
                        "--clarification-id",
                        "CLAR-001",
                        "--decision",
                        "resolved",
                        "--resolution-notes",
                        "answered by the updated contract",
                        "--next-action",
                        "continue WI planning",
                    ]
                ),
                0,
            )

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "resolve-clarification",
                            "--root",
                            str(root),
                            "--goal-id",
                            "GOAL-018",
                            "--clarification-id",
                            "CLAR-001",
                            "--decision",
                            "resolved",
                            "--resolution-notes",
                            "repeat close",
                            "--next-action",
                            "none",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("only open artifacts can be updated", error_output)
            self.assertIn("Status=resolved", error_output)
            self.assertIn((root / "clarifications" / "GOAL-018" / "CLAR-001.md").as_posix(), error_output)


class CreateWorkItemCliTest(unittest.TestCase):
    def _write_clarification(
        self,
        root,
        *,
        goal_id: str,
        clarification_id: str,
        status: str = "open",
        artifact_goal_id: str | None = None,
    ) -> None:
        effective_goal_id = artifact_goal_id or goal_id
        (root / "clarifications" / goal_id).mkdir(parents=True, exist_ok=True)
        (root / "clarifications" / goal_id / f"{clarification_id}.md").write_text(
            "\n".join(
                [
                    f"# {clarification_id}: linked clarification",
                    "",
                    "## Clarification ID",
                    clarification_id,
                    "",
                    "## Goal ID",
                    effective_goal_id,
                    "",
                    "## Title",
                    "linked clarification",
                    "",
                    "## Status",
                    status,
                    "",
                    "## Category",
                    "scope",
                    "",
                    "## Question",
                    "What should the operator keep visible in the work item?",
                    "",
                    "## Suggested Resolution",
                    "- TBD",
                    "",
                    "## Escalation Required",
                    "no",
                    "",
                    "## Resolution Notes",
                    "- TBD",
                    "",
                    "## Next Action",
                    "- TBD",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def test_create_work_item_creates_markdown_artifact(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            exit_code = main(
                [
                    "create-work-item",
                    "--root",
                    str(root),
                    "--work-item-id",
                    "WI-009",
                    "--title",
                    "Goal to work item decomposition",
                    "--goal-id",
                    "GOAL-009",
                    "--description",
                    "Create a repo-local work item artifact contract.",
                    "--acceptance-criteria",
                    "Artifact exists under docs/work-items.\nDuplicate IDs fail safely.",
                ]
            )

            self.assertEqual(exit_code, 0)

            work_item_path = root / "docs" / "work-items" / "WI-009.md"
            self.assertTrue(work_item_path.exists())

            content = work_item_path.read_text(encoding="utf-8")
            self.assertIn("# WI-009: Goal to work item decomposition", content)
            self.assertIn("## Work Item ID\nWI-009", content)
            self.assertIn("## Goal ID\nGOAL-009", content)
            self.assertIn("## Title\nGoal to work item decomposition", content)
            self.assertIn("## Status\ndraft", content)
            self.assertIn("## Description\nCreate a repo-local work item artifact contract.", content)
            self.assertIn("## Related Clarifications\n- none", content)
            self.assertIn("## Scope\n- TBD", content)
            self.assertIn("## Out of Scope\n- TBD", content)
            self.assertIn(
                "## Acceptance Criteria\nArtifact exists under docs/work-items.\nDuplicate IDs fail safely.",
                content,
            )
            self.assertIn("## Dependencies\n- TBD", content)
            self.assertIn("## Risks\n- TBD", content)
            self.assertIn("## Notes\n- TBD", content)

    def test_create_work_item_defaults_acceptance_criteria_to_tbd(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            exit_code = main(
                [
                    "create-work-item",
                    "--root",
                    str(root),
                    "--work-item-id",
                    "WI-009",
                    "--title",
                    "Goal to work item decomposition",
                    "--goal-id",
                    "GOAL-009",
                    "--description",
                    "Create a repo-local work item artifact contract.",
                ]
            )

            self.assertEqual(exit_code, 0)

            content = (root / "docs" / "work-items" / "WI-009.md").read_text(encoding="utf-8")
            self.assertIn("## Acceptance Criteria\nTBD", content)
            self.assertIn("## Related Clarifications\n- none", content)

    def test_create_work_item_rejects_duplicate_work_item_id(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            first_exit_code = main(
                [
                    "create-work-item",
                    "--root",
                    str(root),
                    "--work-item-id",
                    "WI-009",
                    "--title",
                    "Goal to work item decomposition",
                    "--goal-id",
                    "GOAL-009",
                    "--description",
                    "Create a repo-local work item artifact contract.",
                ]
            )
            self.assertEqual(first_exit_code, 0)

            with self.assertRaises(SystemExit) as exc_info:
                main(
                    [
                        "create-work-item",
                        "--root",
                        str(root),
                        "--work-item-id",
                        "WI-009",
                        "--title",
                        "Goal to work item decomposition",
                        "--goal-id",
                        "GOAL-009",
                        "--description",
                        "Create a repo-local work item artifact contract.",
                    ]
                )

            self.assertEqual(exc_info.exception.code, 2)

    def test_create_work_item_links_single_clarification(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_clarification(root, goal_id="GOAL-019", clarification_id="CLAR-001", status="resolved")

            exit_code = main(
                [
                    "create-work-item",
                    "--root",
                    str(root),
                    "--work-item-id",
                    "WI-019",
                    "--title",
                    "Work item clarification linkage",
                    "--goal-id",
                    "GOAL-019",
                    "--description",
                    "Persist related clarification IDs in the work item artifact.",
                    "--clarification-id",
                    "CLAR-001",
                ]
            )

            self.assertEqual(exit_code, 0)
            content = (root / "docs" / "work-items" / "WI-019.md").read_text(encoding="utf-8")
            self.assertIn("## Related Clarifications\n- CLAR-001 (resolved)", content)

    def test_create_work_item_links_multiple_clarifications_and_dedupes_duplicates(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_clarification(root, goal_id="GOAL-019", clarification_id="CLAR-001", status="open")
            self._write_clarification(root, goal_id="GOAL-019", clarification_id="CLAR-002", status="deferred")

            exit_code = main(
                [
                    "create-work-item",
                    "--root",
                    str(root),
                    "--work-item-id",
                    "WI-019",
                    "--title",
                    "Work item clarification linkage",
                    "--goal-id",
                    "GOAL-019",
                    "--description",
                    "Persist multiple clarification IDs in the work item artifact.",
                    "--clarification-id",
                    "CLAR-001",
                    "--clarification-id",
                    "CLAR-002",
                    "--clarification-id",
                    "CLAR-001",
                ]
            )

            self.assertEqual(exit_code, 0)
            content = (root / "docs" / "work-items" / "WI-019.md").read_text(encoding="utf-8")
            self.assertIn("## Related Clarifications\n- CLAR-001 (open)\n- CLAR-002 (deferred)", content)
            self.assertEqual(content.count("CLAR-001 (open)"), 1)

    def test_create_work_item_fails_when_clarification_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "create-work-item",
                            "--root",
                            str(root),
                            "--work-item-id",
                            "WI-019",
                            "--title",
                            "Work item clarification linkage",
                            "--goal-id",
                            "GOAL-019",
                            "--description",
                            "Persist related clarification IDs in the work item artifact.",
                            "--clarification-id",
                            "CLAR-404",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("clarification artifact was not found", error_output)
            self.assertIn((root / "clarifications" / "GOAL-019" / "CLAR-404.md").as_posix(), error_output)
            self.assertIn("create it first with `factory create-clarification", error_output)

    def test_create_work_item_fails_when_clarification_belongs_to_other_goal(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_clarification(root, goal_id="GOAL-020", clarification_id="CLAR-001", status="open")

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "create-work-item",
                            "--root",
                            str(root),
                            "--work-item-id",
                            "WI-019",
                            "--title",
                            "Work item clarification linkage",
                            "--goal-id",
                            "GOAL-019",
                            "--description",
                            "Persist related clarification IDs in the work item artifact.",
                            "--clarification-id",
                            "CLAR-001",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("does not exist under the requested goal", error_output)
            self.assertIn((root / "clarifications" / "GOAL-019" / "CLAR-001.md").as_posix(), error_output)
            self.assertIn((root / "clarifications" / "GOAL-020" / "CLAR-001.md").as_posix(), error_output)
            self.assertIn("use a clarification from goal 'GOAL-019'", error_output)

    def test_create_work_item_fails_when_clarification_artifact_goal_id_mismatches_path_goal(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_clarification(
                root,
                goal_id="GOAL-019",
                clarification_id="CLAR-001",
                status="resolved",
                artifact_goal_id="GOAL-021",
            )

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "create-work-item",
                            "--root",
                            str(root),
                            "--work-item-id",
                            "WI-019",
                            "--title",
                            "Work item clarification linkage",
                            "--goal-id",
                            "GOAL-019",
                            "--description",
                            "Persist related clarification IDs in the work item artifact.",
                            "--clarification-id",
                            "CLAR-001",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("clarification goal linkage is inconsistent", error_output)
            self.assertIn((root / "clarifications" / "GOAL-019" / "CLAR-001.md").as_posix(), error_output)
            self.assertIn("expected 'GOAL-019'", error_output)


class CreatePrPlanCliTest(unittest.TestCase):
    def test_create_pr_plan_creates_active_markdown_artifact_without_existing_active(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            exit_code = main(
                [
                    "create-pr-plan",
                    "--root",
                    str(root),
                    "--pr-id",
                    "PR-010",
                    "--work-item-id",
                    "WI-010",
                    "--title",
                    "Single active PR planning",
                    "--summary",
                    "Create the minimum repo-local artifact for the single active PR plan.",
                ]
            )

            self.assertEqual(exit_code, 0)

            pr_plan_path = root / "prs" / "active" / "PR-010.md"
            self.assertTrue(pr_plan_path.exists())
            self.assertFalse((root / "prs" / "archive" / "PR-010.md").exists())

            content = pr_plan_path.read_text(encoding="utf-8")
            self.assertIn("# PR-010: Single active PR planning", content)
            self.assertIn("## PR ID\nPR-010", content)
            self.assertIn("## Work Item ID\nWI-010", content)
            self.assertIn("## Title\nSingle active PR planning", content)
            self.assertIn("## Status\nplanned", content)
            self.assertIn(
                "## Summary\nCreate the minimum repo-local artifact for the single active PR plan.",
                content,
            )
            self.assertIn("## Scope\n- TBD", content)
            self.assertIn("## Out of Scope\n- TBD", content)
            self.assertIn("## Implementation Notes\n- TBD", content)
            self.assertIn("## Risks\n- TBD", content)
            self.assertIn("## Open Questions\n- TBD", content)

    def test_create_pr_plan_creates_archive_candidate_when_active_pr_already_exists(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            first_exit_code = main(
                [
                    "create-pr-plan",
                    "--root",
                    str(root),
                    "--pr-id",
                    "PR-010",
                    "--work-item-id",
                    "WI-010",
                    "--title",
                    "Single active PR planning",
                    "--summary",
                    "Create the single active PR plan artifact.",
                ]
            )
            self.assertEqual(first_exit_code, 0)

            second_exit_code = main(
                [
                    "create-pr-plan",
                    "--root",
                    str(root),
                    "--pr-id",
                    "PR-011",
                    "--work-item-id",
                    "WI-011",
                    "--title",
                    "Another PR plan",
                    "--summary",
                    "Create an archive candidate because one active PR already exists.",
                ]
            )

            self.assertEqual(second_exit_code, 0)
            self.assertTrue((root / "prs" / "active" / "PR-010.md").exists())
            archive_pr_plan_path = root / "prs" / "archive" / "PR-011.md"
            self.assertTrue(archive_pr_plan_path.exists())
            content = archive_pr_plan_path.read_text(encoding="utf-8")
            self.assertIn("## PR ID\nPR-011", content)
            self.assertIn("## Work Item ID\nWI-011", content)
            self.assertIn("## Title\nAnother PR plan", content)


class StartExecutionCliTest(unittest.TestCase):
    def test_start_execution_bootstraps_run_from_active_pr_plan(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "prs" / "active").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "work-items").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "work-items" / "WI-011.md").write_text("# WI-011\n", encoding="utf-8")
            (root / "prs" / "active" / "PR-011.md").write_text(
                "\n".join(
                    [
                        "# PR-011: approval-driven execution flow",
                        "",
                        "## PR ID",
                        "PR-011",
                        "",
                        "## Work Item ID",
                        "WI-011",
                        "",
                        "## Title",
                        "approval-driven execution flow",
                        "",
                        "## Status",
                        "planned",
                        "",
                        "## Summary",
                        "Connect the active PR plan to run bootstrap.",
                        "",
                        "## Scope",
                        "- TBD",
                        "",
                        "## Out of Scope",
                        "- TBD",
                        "",
                        "## Implementation Notes",
                        "- TBD",
                        "",
                        "## Risks",
                        "- TBD",
                        "",
                        "## Open Questions",
                        "- TBD",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            exit_code = main(
                [
                    "start-execution",
                    "--root",
                    str(root),
                    "--run-id",
                    "RUN-011",
                ]
            )

            self.assertEqual(exit_code, 0)
            run_root = root / "runs" / "latest" / "RUN-011"
            self.assertTrue((run_root / "run.yaml").exists())

            run_payload = read_yaml(run_root / "run.yaml")
            self.assertEqual(run_payload["run"]["run_id"], "RUN-011")
            self.assertEqual(run_payload["run"]["pr_id"], "PR-011")
            self.assertEqual(run_payload["run"]["work_item_id"], "WI-011")
            self.assertEqual(run_payload["run"]["work_item_path"], (root / "docs" / "work-items" / "WI-011.md").as_posix())
            self.assertEqual(run_payload["run"]["pr_plan_path"], (root / "prs" / "active" / "PR-011.md").as_posix())
            self.assertEqual(run_payload["run"]["source_command"], "start-execution")
            self.assertEqual(run_payload["run"]["state"], "in_progress")

            pr_plan_payload = read_yaml(run_root / "artifacts" / "pr-plan.yaml")
            self.assertEqual(pr_plan_payload["pr_plan"]["pr_id"], "PR-011")
            self.assertEqual(pr_plan_payload["pr_plan"]["work_item_id"], "WI-011")
            self.assertEqual(pr_plan_payload["pr_plan"]["title"], "approval-driven execution flow")
            self.assertEqual(pr_plan_payload["pr_plan"]["status"], "in_progress")
            self.assertEqual(
                pr_plan_payload["pr_plan"]["source_pr_plan_path"],
                (root / "prs" / "active" / "PR-011.md").as_posix(),
            )

            work_item_payload = read_yaml(run_root / "artifacts" / "work-item.yaml")
            self.assertEqual(work_item_payload["work_item"]["status"], "in_progress")
            self.assertEqual(
                work_item_payload["work_item"]["source_work_item_path"],
                (root / "docs" / "work-items" / "WI-011.md").as_posix(),
            )

    def test_start_execution_fails_without_active_pr_plan(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "start-execution",
                            "--root",
                            str(root),
                            "--run-id",
                            "RUN-011",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("there is no active PR plan", error_output)
            self.assertIn("factory create-pr-plan --root . --pr-id PR-XXX", error_output)
            self.assertIn("factory activate-pr --root . --pr-id PR-XXX", error_output)


class StatusCliTest(unittest.TestCase):
    def test_status_shows_active_pr_latest_run_approval_and_open_clarifications(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "prs" / "active").mkdir(parents=True, exist_ok=True)
            (root / "prs" / "active" / "PR-013.md").write_text(
                "\n".join(
                    [
                        "# PR-013: system status visibility",
                        "",
                        "## PR ID",
                        "PR-013",
                        "",
                        "## Work Item ID",
                        "WI-013",
                        "",
                        "## Title",
                        "system status visibility",
                        "",
                        "## Status",
                        "planned",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            (root / "runs" / "latest" / "RUN-013" / "artifacts").mkdir(parents=True, exist_ok=True)
            (root / "runs" / "latest" / "RUN-013" / "run.yaml").write_text(
                "\n".join(
                    [
                        "run:",
                        "  run_id: RUN-013",
                        "  work_item_id: WI-013",
                        "  pr_id: PR-013",
                        "  state: approval_pending",
                        "  created_at: '2026-03-29T00:00:00+00:00'",
                        "  updated_at: '2026-03-29T01:00:00+00:00'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (root / "approval_queue" / "pending").mkdir(parents=True, exist_ok=True)
            (root / "approval_queue" / "pending" / "APR-RUN-013.yaml").write_text(
                "approval_request:\n  id: APR-RUN-013\n",
                encoding="utf-8",
            )
            (root / "clarifications" / "GOAL-013").mkdir(parents=True, exist_ok=True)
            (root / "clarifications" / "GOAL-013" / "CLAR-001.md").write_text(
                "\n".join(
                    [
                        "# CLAR-001: missing scope detail",
                        "",
                        "## Clarification ID",
                        "CLAR-001",
                        "",
                        "## Goal ID",
                        "GOAL-013",
                        "",
                        "## Title",
                        "missing scope detail",
                        "",
                        "## Status",
                        "open",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["status", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                stdout.getvalue(),
                "\n".join(
                    [
                        "Active PR:",
                        "- pr_id: PR-013",
                        "- work_item_id: WI-013",
                        f"- path: {(root / 'prs' / 'active' / 'PR-013.md').as_posix()}",
                        "",
                        "Latest Run:",
                        "- run_id: RUN-013",
                        "- state: approval_pending",
                        f"- path: {(root / 'runs' / 'latest' / 'RUN-013').as_posix()}",
                        "",
                        "Approval:",
                        "- status: pending",
                        f"- path: {(root / 'approval_queue' / 'pending' / 'APR-RUN-013.yaml').as_posix()}",
                        "",
                        "Open Clarifications (1):",
                        "- clarification_id: CLAR-001",
                    ]
                )
                + "\n",
            )


class CleanupRehearsalCliTest(unittest.TestCase):
    def _write_status_fixture(self, root) -> None:
        (root / "runs" / "latest" / "RUN-100").mkdir(parents=True, exist_ok=True)
        (root / "runs" / "latest" / "RUN-100" / "run.yaml").write_text(
            "\n".join(
                [
                    "run:",
                    "  run_id: RUN-100",
                    "  work_item_id: WI-100",
                    "  pr_id: PR-100",
                    "  state: in_progress",
                    "  created_at: '2026-03-29T00:00:00+00:00'",
                    "  updated_at: '2026-03-29T00:00:00+00:00'",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (root / "runs" / "latest" / "RUN-RH-001").mkdir(parents=True, exist_ok=True)
        (root / "runs" / "latest" / "RUN-RH-001" / "run.yaml").write_text(
            "\n".join(
                [
                    "run:",
                    "  run_id: RUN-RH-001",
                    "  work_item_id: WI-RH-001",
                    "  pr_id: PR-RH-001",
                    "  state: approval_pending",
                    "  created_at: '2026-03-29T01:00:00+00:00'",
                    "  updated_at: '2026-03-29T01:00:00+00:00'",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (root / "approval_queue" / "pending").mkdir(parents=True, exist_ok=True)
        (root / "approval_queue" / "pending" / "APR-RUN-RH-001.yaml").write_text(
            "approval_request:\n  id: APR-RUN-RH-001\n",
            encoding="utf-8",
        )
        (root / "prs" / "active").mkdir(parents=True, exist_ok=True)
        (root / "prs" / "active" / "PR-RH-001.md").write_text(
            "\n".join(
                [
                    "# PR-RH-001: rehearsal active",
                    "",
                    "## PR ID",
                    "PR-RH-001",
                    "",
                    "## Work Item ID",
                    "WI-RH-001",
                    "",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (root / "clarifications" / "GOAL-RH-001").mkdir(parents=True, exist_ok=True)
        (root / "clarifications" / "GOAL-RH-001" / "CLAR-RH-001.md").write_text(
            "\n".join(
                [
                    "# CLAR-RH-001: rehearsal clarification",
                    "",
                    "## Clarification ID",
                    "CLAR-RH-001",
                    "",
                    "## Goal ID",
                    "GOAL-RH-001",
                    "",
                    "## Status",
                    "open",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def _write_cleanup_targets(self, root) -> None:
        (root / "runs" / "latest" / "RUN-RH-001" / "artifacts").mkdir(parents=True, exist_ok=True)
        (root / "runs" / "latest" / "RUN-RH-001" / "artifacts" / "placeholder.yaml").write_text("x: 1\n", encoding="utf-8")
        (root / "runs" / "latest" / "RUN-DEMO-001").mkdir(parents=True, exist_ok=True)
        (root / "runs" / "latest" / "RUN-012-DEMO" / "artifacts").mkdir(parents=True, exist_ok=True)
        (root / "runs" / "latest" / "RUN-012-DEMO" / "run.yaml").write_text(
            "\n".join(
                [
                    "run:",
                    "  run_id: RUN-012-DEMO",
                    "  work_item_id: WI-012-DEMO",
                    "  pr_id: PR-012-DEMO",
                    "  state: approval_pending",
                    "  created_at: '2026-03-29T02:00:00+00:00'",
                    "  updated_at: '2026-03-29T02:00:00+00:00'",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (root / "approval_queue" / "pending").mkdir(parents=True, exist_ok=True)
        (root / "approval_queue" / "approved").mkdir(parents=True, exist_ok=True)
        (root / "approval_queue" / "pending" / "APR-RUN-RH-001.yaml").write_text("approval_request:\n  id: APR-RUN-RH-001\n", encoding="utf-8")
        (root / "approval_queue" / "approved" / "APR-RUN-DEMO-001.yaml").write_text(
            "approval_request:\n  id: APR-RUN-DEMO-001\n",
            encoding="utf-8",
        )
        (root / "approval_queue" / "pending" / "APR-RUN-012-DEMO.yaml").write_text(
            "approval_request:\n  id: APR-RUN-012-DEMO\n",
            encoding="utf-8",
        )
        (root / "goals").mkdir(parents=True, exist_ok=True)
        (root / "goals" / "GOAL-RH-001.md").write_text("# GOAL-RH-001\n", encoding="utf-8")
        (root / "goals" / "GOAL-007-DEMO.md").write_text("# GOAL-007-DEMO\n", encoding="utf-8")
        (root / "goals" / "GOAL-101.md").write_text("# GOAL-101\n", encoding="utf-8")
        (root / "clarifications" / "GOAL-RH-001").mkdir(parents=True, exist_ok=True)
        (root / "clarifications" / "GOAL-RH-001" / "CLAR-001.md").write_text("# CLAR-001\n\n## Status\nopen\n", encoding="utf-8")
        (root / "clarifications" / "GOAL-007-DEMO").mkdir(parents=True, exist_ok=True)
        (root / "clarifications" / "GOAL-007-DEMO" / "CLAR-007.md").write_text("# CLAR-007\n\n## Status\nopen\n", encoding="utf-8")
        (root / "docs" / "work-items").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "work-items" / "WI-RH-001.md").write_text("# WI-RH-001\n", encoding="utf-8")
        (root / "docs" / "work-items" / "WI-009-DEMO.md").write_text("# WI-009-DEMO\n", encoding="utf-8")
        (root / "docs" / "work-items" / "WI-100.md").write_text("# WI-100\n", encoding="utf-8")
        (root / "prs" / "active").mkdir(parents=True, exist_ok=True)
        (root / "prs" / "archive").mkdir(parents=True, exist_ok=True)
        (root / "prs" / "active" / "PR-RH-001.md").write_text("# PR-RH-001\n", encoding="utf-8")
        (root / "prs" / "archive" / "PR-010-DEMO.md").write_text("# PR-010-DEMO\n", encoding="utf-8")
        (root / "prs" / "archive" / "PR-100.md").write_text("# PR-100\n", encoding="utf-8")
        (root / "docs" / "prs" / "PR-010-DEMO").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "prs" / "PR-010-DEMO" / "plan.md").write_text("# keep history\n", encoding="utf-8")
        (root / "README.md").write_text("# keep readme\n", encoding="utf-8")

    def _write_demo_status_fixture(self, root) -> None:
        (root / "runs" / "latest" / "RUN-100").mkdir(parents=True, exist_ok=True)
        (root / "runs" / "latest" / "RUN-100" / "run.yaml").write_text(
            "\n".join(
                [
                    "run:",
                    "  run_id: RUN-100",
                    "  work_item_id: WI-100",
                    "  pr_id: PR-100",
                    "  state: in_progress",
                    "  created_at: '2026-03-29T00:00:00+00:00'",
                    "  updated_at: '2026-03-29T00:00:00+00:00'",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (root / "runs" / "latest" / "RUN-012-DEMO").mkdir(parents=True, exist_ok=True)
        (root / "runs" / "latest" / "RUN-012-DEMO" / "run.yaml").write_text(
            "\n".join(
                [
                    "run:",
                    "  run_id: RUN-012-DEMO",
                    "  work_item_id: WI-012-DEMO",
                    "  pr_id: PR-012-DEMO",
                    "  state: approval_pending",
                    "  created_at: '2026-03-29T03:00:00+00:00'",
                    "  updated_at: '2026-03-29T03:00:00+00:00'",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (root / "approval_queue" / "pending").mkdir(parents=True, exist_ok=True)
        (root / "approval_queue" / "pending" / "APR-RUN-012-DEMO.yaml").write_text(
            "approval_request:\n  id: APR-RUN-012-DEMO\n",
            encoding="utf-8",
        )
        (root / "clarifications" / "GOAL-012-DEMO").mkdir(parents=True, exist_ok=True)
        (root / "clarifications" / "GOAL-012-DEMO" / "CLAR-012.md").write_text(
            "\n".join(
                [
                    "# CLAR-012: demo clarification",
                    "",
                    "## Clarification ID",
                    "CLAR-012",
                    "",
                    "## Goal ID",
                    "GOAL-012-DEMO",
                    "",
                    "## Status",
                    "open",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def test_cleanup_rehearsal_dry_run_reports_targets_without_deleting(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_cleanup_targets(root)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["cleanup-rehearsal", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Cleanup Rehearsal:", output)
            self.assertIn("- mode: dry-run", output)
            self.assertIn("- scope: rehearsal-only", output)
            self.assertIn("- runs/latest/RUN-RH-001", output)
            self.assertIn("- approval_queue/pending/APR-RUN-RH-001.yaml", output)
            self.assertNotIn("RUN-DEMO-001", output)
            self.assertTrue((root / "runs" / "latest" / "RUN-RH-001").exists())
            self.assertTrue((root / "goals" / "GOAL-RH-001.md").exists())
            self.assertTrue((root / "docs" / "prs" / "PR-010-DEMO" / "plan.md").exists())

    def test_cleanup_rehearsal_apply_deletes_only_rehearsal_targets(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_cleanup_targets(root)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["cleanup-rehearsal", "--root", str(root), "--apply"])

            self.assertEqual(exit_code, 0)
            self.assertIn("- mode: apply", stdout.getvalue())
            self.assertFalse((root / "runs" / "latest" / "RUN-RH-001").exists())
            self.assertFalse((root / "approval_queue" / "pending" / "APR-RUN-RH-001.yaml").exists())
            self.assertFalse((root / "goals" / "GOAL-RH-001.md").exists())
            self.assertFalse((root / "clarifications" / "GOAL-RH-001").exists())
            self.assertFalse((root / "docs" / "work-items" / "WI-RH-001.md").exists())
            self.assertFalse((root / "prs" / "active" / "PR-RH-001.md").exists())
            self.assertTrue((root / "runs" / "latest" / "RUN-DEMO-001").exists())
            self.assertTrue((root / "runs" / "latest" / "RUN-012-DEMO").exists())
            self.assertTrue((root / "approval_queue" / "pending" / "APR-RUN-012-DEMO.yaml").exists())
            self.assertTrue((root / "approval_queue" / "approved" / "APR-RUN-DEMO-001.yaml").exists())
            self.assertTrue((root / "goals" / "GOAL-007-DEMO.md").exists())
            self.assertTrue((root / "docs" / "work-items" / "WI-009-DEMO.md").exists())
            self.assertTrue((root / "prs" / "archive" / "PR-010-DEMO.md").exists())
            self.assertTrue((root / "docs" / "prs" / "PR-010-DEMO" / "plan.md").exists())
            self.assertTrue((root / "README.md").exists())

    def test_cleanup_rehearsal_include_demo_removes_demo_targets(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_cleanup_targets(root)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["cleanup-rehearsal", "--root", str(root), "--apply", "--include-demo"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- scope: rehearsal+demo", output)
            self.assertFalse((root / "runs" / "latest" / "RUN-DEMO-001").exists())
            self.assertFalse((root / "runs" / "latest" / "RUN-012-DEMO").exists())
            self.assertFalse((root / "approval_queue" / "pending" / "APR-RUN-012-DEMO.yaml").exists())
            self.assertFalse((root / "approval_queue" / "approved" / "APR-RUN-DEMO-001.yaml").exists())
            self.assertFalse((root / "goals" / "GOAL-007-DEMO.md").exists())
            self.assertFalse((root / "clarifications" / "GOAL-007-DEMO").exists())
            self.assertFalse((root / "docs" / "work-items" / "WI-009-DEMO.md").exists())
            self.assertFalse((root / "prs" / "archive" / "PR-010-DEMO.md").exists())
            self.assertTrue((root / "docs" / "prs" / "PR-010-DEMO" / "plan.md").exists())
            self.assertTrue((root / "goals" / "GOAL-101.md").exists())
            self.assertTrue((root / "docs" / "work-items" / "WI-100.md").exists())
            self.assertTrue((root / "prs" / "archive" / "PR-100.md").exists())

    def test_cleanup_rehearsal_apply_clears_stale_status_entries(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_status_fixture(root)

            self.assertEqual(main(["cleanup-rehearsal", "--root", str(root), "--apply"]), 0)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["status", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                stdout.getvalue(),
                "\n".join(
                    [
                        "Active PR:",
                        "- none",
                        "",
                        "Latest Run:",
                        "- run_id: RUN-100",
                        "- state: in_progress",
                        f"- path: {(root / 'runs' / 'latest' / 'RUN-100').as_posix()}",
                        "",
                        "Approval:",
                        "- status: none",
                    ]
                )
                + "\n",
            )

    def test_cleanup_rehearsal_include_demo_clears_suffix_demo_status_entries(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_demo_status_fixture(root)

            self.assertEqual(main(["cleanup-rehearsal", "--root", str(root), "--apply", "--include-demo"]), 0)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["status", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                stdout.getvalue(),
                "\n".join(
                    [
                        "Active PR:",
                        "- none",
                        "",
                        "Latest Run:",
                        "- run_id: RUN-100",
                        "- state: in_progress",
                        f"- path: {(root / 'runs' / 'latest' / 'RUN-100').as_posix()}",
                        "",
                        "Approval:",
                        "- status: none",
                    ]
                )
                + "\n",
            )
    def test_status_handles_missing_active_pr_run_and_approval(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["status", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                stdout.getvalue(),
                "\n".join(
                    [
                        "Active PR:",
                        "- none",
                        "",
                        "Latest Run:",
                        "- none",
                        "",
                        "Approval:",
                        "- status: none",
                    ]
                )
                + "\n",
            )

    def test_start_execution_fails_with_multiple_active_pr_plans(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            active_dir = root / "prs" / "active"
            active_dir.mkdir(parents=True, exist_ok=True)
            (active_dir / "PR-011.md").write_text("# PR-011\n\n## PR ID\nPR-011\n\n## Work Item ID\nWI-011\n\n## Title\none\n", encoding="utf-8")
            (active_dir / "PR-012.md").write_text("# PR-012\n\n## PR ID\nPR-012\n\n## Work Item ID\nWI-012\n\n## Title\ntwo\n", encoding="utf-8")

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "start-execution",
                            "--root",
                            str(root),
                            "--run-id",
                            "RUN-011",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("must contain exactly one active PR plan", error_output)
            self.assertIn("Current active candidates:", error_output)
            self.assertIn("factory start-execution --root . --run-id RUN-011", error_output)

    def test_start_execution_fails_when_work_item_artifact_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            active_dir = root / "prs" / "active"
            active_dir.mkdir(parents=True, exist_ok=True)
            (active_dir / "PR-012.md").write_text(
                "# PR-012\n\n## PR ID\nPR-012\n\n## Work Item ID\nWI-012\n\n## Title\nmissing work item\n",
                encoding="utf-8",
            )

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "start-execution",
                            "--root",
                            str(root),
                            "--run-id",
                            "RUN-012",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("does not resolve to a work item artifact", error_output)
            self.assertIn("docs/work-items/WI-012.md", error_output)
            self.assertIn("factory start-execution --root . --run-id RUN-012", error_output)

    def test_create_pr_plan_rejects_duplicate_pr_id(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stdout = StringIO()
            with redirect_stdout(stdout):
                first_exit_code = main(
                    [
                        "create-pr-plan",
                        "--root",
                        str(root),
                        "--pr-id",
                        "PR-010",
                        "--work-item-id",
                        "WI-010",
                        "--title",
                        "Single active PR planning",
                        "--summary",
                        "Create the single active PR plan artifact.",
                    ]
                )
            self.assertEqual(first_exit_code, 0)
            self.assertIn("- location: active", stdout.getvalue())
            self.assertIn((root / "prs" / "active" / "PR-010.md").as_posix(), stdout.getvalue())

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "create-pr-plan",
                            "--root",
                            str(root),
                            "--pr-id",
                            "PR-010",
                            "--work-item-id",
                            "WI-010",
                            "--title",
                            "Single active PR planning",
                            "--summary",
                            "Duplicate create should fail safely.",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            self.assertIn((root / "prs" / "active" / "PR-010.md").as_posix(), stderr.getvalue())


class ActivatePrCliTest(unittest.TestCase):
    def test_activate_pr_archives_existing_active_pr(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            active_dir = root / "prs" / "active"
            archive_dir = root / "prs" / "archive"
            active_dir.mkdir(parents=True, exist_ok=True)
            archive_dir.mkdir(parents=True, exist_ok=True)
            (active_dir / "PR-010.md").write_text("# PR-010\n", encoding="utf-8")
            (archive_dir / "PR-011.md").write_text("# PR-011\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "activate-pr",
                        "--root",
                        str(root),
                        "--pr-id",
                        "PR-011",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertFalse((active_dir / "PR-010.md").exists())
            self.assertTrue((archive_dir / "PR-010.md").exists())
            self.assertIn("- active_pr_id: PR-011", stdout.getvalue())
            self.assertIn(f"- active_path: {(active_dir / 'PR-011.md').as_posix()}", stdout.getvalue())
            self.assertIn(f"- archived_previous_active: {(archive_dir / 'PR-010.md').as_posix()}", stdout.getvalue())

    def test_activate_pr_promotes_archive_candidate_to_active(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            active_dir = root / "prs" / "active"
            archive_dir = root / "prs" / "archive"

            active_stdout = StringIO()
            with redirect_stdout(active_stdout):
                active_create_exit_code = main(
                    [
                        "create-pr-plan",
                        "--root",
                        str(root),
                        "--pr-id",
                        "PR-010",
                        "--work-item-id",
                        "WI-010",
                        "--title",
                        "Current active PR",
                        "--summary",
                        "This starts as the active PR plan.",
                    ]
                )
            self.assertEqual(active_create_exit_code, 0)

            archive_stdout = StringIO()
            with redirect_stdout(archive_stdout):
                archive_create_exit_code = main(
                    [
                        "create-pr-plan",
                        "--root",
                        str(root),
                        "--pr-id",
                        "PR-011",
                        "--work-item-id",
                        "WI-011",
                        "--title",
                        "Candidate PR",
                        "--summary",
                        "This should be created as an archive candidate.",
                    ]
                )
            self.assertEqual(archive_create_exit_code, 0)
            self.assertIn("- location: archive", archive_stdout.getvalue())
            self.assertIn("active PR already exists", archive_stdout.getvalue())
            self.assertIn("factory activate-pr --root . --pr-id PR-011", archive_stdout.getvalue())

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "activate-pr",
                        "--root",
                        str(root),
                        "--pr-id",
                        "PR-011",
                    ]
                )

            self.assertEqual(exit_code, 0)
            active_plans = sorted(path.name for path in active_dir.glob("*.md"))
            self.assertEqual(active_plans, ["PR-011.md"])
            self.assertTrue((active_dir / "PR-011.md").exists())
            self.assertFalse((archive_dir / "PR-011.md").exists())
            self.assertTrue((archive_dir / "PR-010.md").exists())
            self.assertIn(f"- active_path: {(active_dir / 'PR-011.md').as_posix()}", stdout.getvalue())
            self.assertIn(f"- archived_previous_active: {(archive_dir / 'PR-010.md').as_posix()}", stdout.getvalue())

    def test_activate_pr_missing_target_reports_active_and_archive_paths(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            stderr = StringIO()

            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "activate-pr",
                            "--root",
                            str(root),
                            "--pr-id",
                            "PR-404",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("none was found under", error_output)
            self.assertIn((root / "prs" / "active" / "PR-404.md").as_posix(), error_output)
            self.assertIn((root / "prs" / "archive" / "PR-404.md").as_posix(), error_output)

    def test_start_execution_uses_newly_activated_pr(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            active_dir = root / "prs" / "active"
            work_items_dir = root / "docs" / "work-items"
            work_items_dir.mkdir(parents=True, exist_ok=True)
            (work_items_dir / "WI-010.md").write_text("# WI-010\n", encoding="utf-8")
            (work_items_dir / "WI-011.md").write_text("# WI-011\n", encoding="utf-8")
            first_exit_code = main(
                [
                    "create-pr-plan",
                    "--root",
                    str(root),
                    "--pr-id",
                    "PR-010",
                    "--work-item-id",
                    "WI-010",
                    "--title",
                    "old active",
                    "--summary",
                    "This remains active until an explicit switch happens.",
                ]
            )
            self.assertEqual(first_exit_code, 0)

            second_exit_code = main(
                [
                    "create-pr-plan",
                    "--root",
                    str(root),
                    "--pr-id",
                    "PR-011",
                    "--work-item-id",
                    "WI-011",
                    "--title",
                    "newly activated",
                    "--summary",
                    "This should be created as an archive candidate first.",
                ]
            )
            self.assertEqual(second_exit_code, 0)
            self.assertTrue((root / "prs" / "archive" / "PR-011.md").exists())

            activate_exit_code = main(
                [
                    "activate-pr",
                    "--root",
                    str(root),
                    "--pr-id",
                    "PR-011",
                ]
            )
            self.assertEqual(activate_exit_code, 0)

            start_exit_code = main(
                [
                    "start-execution",
                    "--root",
                    str(root),
                    "--run-id",
                    "RUN-011",
                ]
            )

            self.assertEqual(start_exit_code, 0)
            run_payload = read_yaml(root / "runs" / "latest" / "RUN-011" / "run.yaml")
            self.assertEqual(run_payload["run"]["pr_id"], "PR-011")
            self.assertEqual(run_payload["run"]["work_item_id"], "WI-011")
            self.assertEqual(run_payload["run"]["pr_plan_path"], (active_dir / "PR-011.md").as_posix())


class LatestRunCliTest(unittest.TestCase):
    def _prepare_gates_config(self, root) -> None:
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[1]
        (root / "config").mkdir(parents=True, exist_ok=True)
        (root / "approval_queue" / "pending").mkdir(parents=True, exist_ok=True)
        (root / "config" / "gates.yaml").write_text(
            (repo_root / "config" / "gates.yaml").read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    def _bootstrap_run(self, root, run_id: str, updated_at: str) -> None:
        exit_code = main(
            [
                "bootstrap-run",
                "--root",
                str(root),
                "--run-id",
                run_id,
                "--pr-id",
                f"PR-{run_id}",
                "--work-item-id",
                f"WI-{run_id}",
                "--work-item-title",
                f"title for {run_id}",
            ]
        )
        self.assertEqual(exit_code, 0)

        run_path = root / "runs" / "latest" / run_id / "run.yaml"
        payload = read_yaml(run_path)
        payload["run"]["created_at"] = updated_at
        payload["run"]["updated_at"] = updated_at
        from orchestrator.yaml_io import write_yaml

        write_yaml(run_path, payload)

    def test_run_scoped_commands_support_latest(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prepare_gates_config(root)
            self._bootstrap_run(root, "RUN-OLD", "2026-03-29T00:00:00+00:00")
            self._bootstrap_run(root, "RUN-NEW", "2026-03-29T01:00:00+00:00")

            self.assertEqual(
                main(["record-review", "--root", str(root), "--latest", "--status", "pass", "--summary", "review ok"]),
                0,
            )
            self.assertEqual(
                main(["record-qa", "--root", str(root), "--latest", "--status", "pass", "--summary", "qa ok"]),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "record-docs-sync",
                        "--root",
                        str(root),
                        "--latest",
                        "--status",
                        "complete",
                        "--summary",
                        "docs synced",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "record-verification",
                        "--root",
                        str(root),
                        "--latest",
                        "--lint",
                        "pass",
                        "--tests",
                        "pass",
                        "--type-check",
                        "pass",
                        "--build",
                        "pass",
                        "--summary",
                        "all checks green",
                    ]
                ),
                0,
            )
            self.assertEqual(main(["gate-check", "--root", str(root), "--latest"]), 0)
            self.assertEqual(main(["build-approval", "--root", str(root), "--latest"]), 0)
            self.assertEqual(
                main(
                    [
                        "resolve-approval",
                        "--root",
                        str(root),
                        "--latest",
                        "--decision",
                        "approve",
                        "--actor",
                        "approver.local",
                        "--note",
                        "approved latest run",
                    ]
                ),
                0,
            )

            latest_review = read_yaml(root / "runs" / "latest" / "RUN-NEW" / "artifacts" / "review-report.yaml")
            old_review = read_yaml(root / "runs" / "latest" / "RUN-OLD" / "artifacts" / "review-report.yaml")
            self.assertEqual(latest_review["review_report"]["status"], "pass")
            self.assertNotIn("recorded_at", old_review["review_report"])
            self.assertTrue((root / "approval_queue" / "approved" / "APR-RUN-NEW.yaml").exists())
            self.assertFalse((root / "approval_queue" / "approved" / "APR-RUN-OLD.yaml").exists())

    def test_latest_selector_matches_status_selection_rule(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._bootstrap_run(root, "RUN-100", "2026-03-29T01:00:00+00:00")
            self._bootstrap_run(root, "RUN-200", "2026-03-29T01:00:00+00:00")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["status", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            self.assertIn("- run_id: RUN-200", stdout.getvalue())
            self.assertEqual(
                main(["record-review", "--root", str(root), "--latest", "--status", "pass", "--summary", "review ok"]),
                0,
            )

            picked = read_yaml(root / "runs" / "latest" / "RUN-200" / "artifacts" / "review-report.yaml")
            other = read_yaml(root / "runs" / "latest" / "RUN-100" / "artifacts" / "review-report.yaml")
            self.assertIn("recorded_at", picked["review_report"])
            self.assertNotIn("recorded_at", other["review_report"])

    def test_latest_requires_existing_run(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            stderr = StringIO()

            with self.assertRaises(SystemExit) as exc_info, redirect_stderr(stderr):
                main(["record-review", "--root", str(root), "--latest", "--status", "pass", "--summary", "review ok"])

            self.assertEqual(exc_info.exception.code, 2)
            self.assertIn("no latest run found under runs/latest/*/run.yaml", stderr.getvalue())

    def test_run_id_and_latest_are_mutually_exclusive(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            stderr = StringIO()

            with self.assertRaises(SystemExit) as exc_info, redirect_stderr(stderr):
                main(
                    [
                        "record-review",
                        "--root",
                        str(root),
                        "--run-id",
                        "RUN-001",
                        "--latest",
                        "--status",
                        "pass",
                        "--summary",
                        "review ok",
                    ]
                )

            self.assertEqual(exc_info.exception.code, 2)
            self.assertIn("not allowed with argument --run-id", stderr.getvalue())

    def test_build_approval_latest_reports_missing_prerequisite_with_next_step(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prepare_gates_config(root)
            self._bootstrap_run(root, "RUN-LATEST", "2026-03-29T01:00:00+00:00")

            self.assertEqual(
                main(
                    [
                        "record-verification",
                        "--root",
                        str(root),
                        "--latest",
                        "--lint",
                        "pass",
                        "--tests",
                        "pass",
                        "--type-check",
                        "pass",
                        "--build",
                        "pass",
                        "--summary",
                        "verification ok",
                    ]
                ),
                0,
            )

            with self.assertRaisesRegex(
                ValueError,
                r"run `factory record-review --run-id RUN-LATEST` first",
            ):
                main(["build-approval", "--root", str(root), "--latest"])
