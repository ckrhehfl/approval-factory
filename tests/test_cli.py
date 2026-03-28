from __future__ import annotations

from tempfile import TemporaryDirectory
import unittest

from orchestrator.cli import main


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


class CreateWorkItemCliTest(unittest.TestCase):
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


class CreatePrPlanCliTest(unittest.TestCase):
    def test_create_pr_plan_creates_markdown_artifact(self) -> None:
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

    def test_create_pr_plan_rejects_when_active_pr_already_exists(self) -> None:
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

            with self.assertRaises(SystemExit) as exc_info:
                main(
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
                        "This should fail because one active PR already exists.",
                    ]
                )

            self.assertEqual(exc_info.exception.code, 2)

    def test_create_pr_plan_rejects_duplicate_pr_id(self) -> None:
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
