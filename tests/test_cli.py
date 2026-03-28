from __future__ import annotations

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

    def test_start_execution_fails_with_multiple_active_pr_plans(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            active_dir = root / "prs" / "active"
            active_dir.mkdir(parents=True, exist_ok=True)
            (active_dir / "PR-011.md").write_text("# PR-011\n\n## PR ID\nPR-011\n\n## Work Item ID\nWI-011\n\n## Title\none\n", encoding="utf-8")
            (active_dir / "PR-012.md").write_text("# PR-012\n\n## PR ID\nPR-012\n\n## Work Item ID\nWI-012\n\n## Title\ntwo\n", encoding="utf-8")

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

    def test_activate_pr_promotes_archive_candidate_to_active(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            active_dir = root / "prs" / "active"
            archive_dir = root / "prs" / "archive"

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
