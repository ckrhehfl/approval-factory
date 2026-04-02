from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from tempfile import TemporaryDirectory
import unittest

from orchestrator.cli import main
from orchestrator.yaml_io import read_yaml


def _write_minimal_work_item(root, *, work_item_id: str, goal_id: str = "GOAL-TEST") -> None:
    (root / "docs" / "work-items").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "work-items" / f"{work_item_id}.md").write_text(
        "\n".join(
            [
                f"# {work_item_id}: minimal work item",
                "",
                "## Work Item ID",
                work_item_id,
                "",
                "## Goal ID",
                goal_id,
                "",
                "## Title",
                "minimal work item",
                "",
                "## Status",
                "draft",
                "",
                "## Description",
                "Minimal source work item for PR planning tests.",
                "",
                "## Related Clarifications",
                "- none",
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


class DraftClarificationsCliTest(unittest.TestCase):
    def _write_goal(self, root, *, goal_id: str = "GOAL-034") -> None:
        (root / "goals").mkdir(parents=True, exist_ok=True)
        (root / "goals" / f"{goal_id}.md").write_text(
            "\n".join(
                [
                    f"# {goal_id}: clarification drafting",
                    "",
                    "## Goal ID",
                    goal_id,
                    "",
                    "## Title",
                    "clarification drafting",
                    "",
                    "## Status",
                    "draft",
                    "",
                    "## Problem",
                    "Operators need a minimum deterministic drafting step.",
                    "",
                    "## Desired Outcome",
                    "A repo-local draft artifact exists before manual clarification creation.",
                    "",
                    "## Non-Goals",
                    "- TBD",
                    "",
                    "## Constraints",
                    "- repo-local only",
                    "- deterministic",
                    "",
                    "## Risks",
                    "- Users may confuse drafts with official queue items.",
                    "",
                    "## Open Questions",
                    "- Which operator workflow should create official clarification artifacts?",
                    "- What must stay out of scope for the first draft step?",
                    "",
                    "## Approval-Required Decisions",
                    "- Whether draft artifacts can ever auto-promote into clarifications",
                    "",
                    "## Success Criteria",
                    "- TBD",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def test_draft_clarifications_creates_repo_local_draft_only_artifact(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_goal(root)

            exit_code = main(
                [
                    "draft-clarifications",
                    "--root",
                    str(root),
                    "--goal-id",
                    "GOAL-034",
                ]
            )

            self.assertEqual(exit_code, 0)

            draft_path = root / "clarification_drafts" / "GOAL-034.md"
            self.assertTrue(draft_path.exists())
            self.assertFalse((root / "clarifications").exists())
            self.assertFalse((root / "approval_queue").exists())

            content = draft_path.read_text(encoding="utf-8")
            self.assertIn("# Clarification Draft: GOAL-034", content)
            self.assertIn("## Goal ID\nGOAL-034", content)
            self.assertIn("## Draft Status\ndraft-only", content)
            self.assertIn("## Draft Method\ndeterministic-rule-based", content)
            self.assertIn("- category: scope", content)
            self.assertIn("- category: approval-required", content)
            self.assertIn("- escalation_required: yes", content)
            self.assertIn("Create official clarification artifacts only with `factory create-clarification`.", content)
            self.assertIn("never changes readiness, approval, queue, selector, or lifecycle semantics", content)

    def test_draft_clarifications_fails_when_goal_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "draft-clarifications",
                            "--root",
                            str(root),
                            "--goal-id",
                            "GOAL-404",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("goal artifact was not found", error_output)
            self.assertIn((root / "goals" / "GOAL-404.md").as_posix(), error_output)
            self.assertIn("factory create-goal", error_output)

    def test_draft_clarifications_fails_when_draft_already_exists(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_goal(root)
            (root / "clarification_drafts").mkdir(parents=True, exist_ok=True)
            existing_path = root / "clarification_drafts" / "GOAL-034.md"
            existing_path.write_text("# existing draft\n", encoding="utf-8")

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "draft-clarifications",
                            "--root",
                            str(root),
                            "--goal-id",
                            "GOAL-034",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("clarification draft artifact already exists", error_output)
            self.assertIn(existing_path.as_posix(), error_output)


class DraftWorkItemsCliTest(unittest.TestCase):
    def _write_goal(self, root, *, goal_id: str = "GOAL-036") -> None:
        DraftClarificationsCliTest()._write_goal(root, goal_id=goal_id)

    def _write_official_clarification(
        self,
        root,
        *,
        goal_id: str = "GOAL-036",
        clarification_id: str = "CLAR-036",
        title: str = "Define manual promotion boundary",
        status: str = "resolved",
        question: str = "What manual boundary must remain in place for work item drafting?",
    ) -> None:
        (root / "clarifications" / goal_id).mkdir(parents=True, exist_ok=True)
        (root / "clarifications" / goal_id / f"{clarification_id}.md").write_text(
            "\n".join(
                [
                    f"# {clarification_id}: {title}",
                    "",
                    "## Clarification ID",
                    clarification_id,
                    "",
                    "## Goal ID",
                    goal_id,
                    "",
                    "## Title",
                    title,
                    "",
                    "## Status",
                    status,
                    "",
                    "## Category",
                    "scope",
                    "",
                    "## Question",
                    question,
                    "",
                    "## Suggested Resolution",
                    "Keep work item drafting artifact-only.",
                    "",
                    "## Escalation Required",
                    "no",
                    "",
                    "## Resolution Notes",
                    "Operator keeps manual control.",
                    "",
                    "## Next Action",
                    "Use the clarification as the source of truth for drafting.",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def test_draft_work_items_creates_artifact_only_draft_from_official_clarifications(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            goal_id = "GOAL-036"
            self._write_goal(root, goal_id=goal_id)
            self._write_official_clarification(root, goal_id=goal_id)
            (root / "clarification_drafts").mkdir(parents=True, exist_ok=True)
            (root / "clarification_drafts" / f"{goal_id}.md").write_text("# ignored draft\n", encoding="utf-8")

            exit_code = main(
                [
                    "draft-work-items",
                    "--root",
                    str(root),
                    "--goal-id",
                    goal_id,
                ]
            )

            self.assertEqual(exit_code, 0)

            draft_path = root / "work_item_drafts" / f"{goal_id}.md"
            self.assertTrue(draft_path.exists())
            self.assertFalse((root / "docs" / "work-items").exists())

            content = draft_path.read_text(encoding="utf-8")
            self.assertIn(f"# Work Item Draft: {goal_id}", content)
            self.assertIn(f"## Goal ID\n{goal_id}", content)
            self.assertIn("## Draft Status\ndraft-only", content)
            self.assertIn("## Draft Method\ndeterministic-rule-based", content)
            self.assertIn("- CLAR-036 (resolved):", content)
            self.assertIn("This command never reads `clarification_drafts/`.", content)
            self.assertIn("It does not create or update official work item artifacts under `docs/work-items/`.", content)
            self.assertIn("### Candidate 01", content)
            self.assertIn("- source_clarification_id: CLAR-036", content)
            self.assertIn("- source_clarification_status: resolved", content)
            self.assertIn("Create official work item artifacts only with `factory create-work-item`.", content)
            self.assertIn("never changes readiness, approval, queue, selector, active PR, or lifecycle semantics", content)

    def test_draft_work_items_creates_zero_candidate_artifact_without_official_clarifications(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            goal_id = "GOAL-036-ZERO"
            self._write_goal(root, goal_id=goal_id)

            exit_code = main(
                [
                    "draft-work-items",
                    "--root",
                    str(root),
                    "--goal-id",
                    goal_id,
                ]
            )

            self.assertEqual(exit_code, 0)

            content = (root / "work_item_drafts" / f"{goal_id}.md").read_text(encoding="utf-8")
            self.assertIn("## Source Clarifications\n- none", content)
            self.assertIn(
                "No work item candidates were derived from official clarification artifacts for this goal.",
                content,
            )
            self.assertNotIn("### Candidate", content)

    def test_draft_work_items_fails_when_goal_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "draft-work-items",
                            "--root",
                            str(root),
                            "--goal-id",
                            "GOAL-404",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("cannot draft work items because the goal artifact was not found", error_output)
            self.assertIn((root / "goals" / "GOAL-404.md").as_posix(), error_output)
            self.assertIn("factory create-goal", error_output)

    def test_draft_work_items_fails_when_draft_already_exists(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            goal_id = "GOAL-036"
            self._write_goal(root, goal_id=goal_id)
            (root / "work_item_drafts").mkdir(parents=True, exist_ok=True)
            existing_path = root / "work_item_drafts" / f"{goal_id}.md"
            existing_path.write_text("# existing work item draft\n", encoding="utf-8")

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "draft-work-items",
                            "--root",
                            str(root),
                            "--goal-id",
                            goal_id,
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("work item draft artifact already exists", error_output)
            self.assertIn(existing_path.as_posix(), error_output)


class PromoteClarificationDraftCliTest(unittest.TestCase):
    def _write_goal_and_draft(self, root, *, goal_id: str = "GOAL-035") -> None:
        DraftClarificationsCliTest()._write_goal(root, goal_id=goal_id)
        exit_code = main(
            [
                "draft-clarifications",
                "--root",
                str(root),
                "--goal-id",
                goal_id,
            ]
        )
        self.assertEqual(exit_code, 0)

    def test_promote_clarification_draft_creates_one_official_artifact_with_provenance(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            goal_id = "GOAL-035"
            self._write_goal_and_draft(root, goal_id=goal_id)

            draft_path = root / "clarification_drafts" / f"{goal_id}.md"
            original_draft_content = draft_path.read_text(encoding="utf-8")

            exit_code = main(
                [
                    "promote-clarification-draft",
                    "--root",
                    str(root),
                    "--goal-id",
                    goal_id,
                    "--draft-index",
                    "1",
                    "--clarification-id",
                    "CLAR-035",
                ]
            )

            self.assertEqual(exit_code, 0)

            clarification_path = root / "clarifications" / goal_id / "CLAR-035.md"
            self.assertTrue(clarification_path.exists())
            self.assertEqual(draft_path.read_text(encoding="utf-8"), original_draft_content)

            content = clarification_path.read_text(encoding="utf-8")
            self.assertIn("# CLAR-035: Clarify explicit non-goals", content)
            self.assertIn("## Clarification ID\nCLAR-035", content)
            self.assertIn(f"## Goal ID\n{goal_id}", content)
            self.assertIn("## Status\nopen", content)
            self.assertIn("## Category\nscope", content)
            self.assertIn("## Question\nWhat is explicitly out of scope for this goal?", content)
            self.assertIn("## Rationale\nNon-Goals section is missing or still TBD.", content)
            self.assertIn("## Source Provenance", content)
            self.assertIn(f"- draft_path: {draft_path.as_posix()}", content)
            self.assertIn("- draft_index: 1", content)

    def test_promote_clarification_draft_fails_when_draft_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "promote-clarification-draft",
                            "--root",
                            str(root),
                            "--goal-id",
                            "GOAL-404",
                            "--draft-index",
                            "1",
                            "--clarification-id",
                            "CLAR-404",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("draft artifact was not found", error_output)
            self.assertIn((root / "clarification_drafts" / "GOAL-404.md").as_posix(), error_output)
            self.assertIn("factory draft-clarifications", error_output)

    def test_promote_clarification_draft_fails_when_index_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_goal_and_draft(root)

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "promote-clarification-draft",
                            "--root",
                            str(root),
                            "--goal-id",
                            "GOAL-035",
                            "--draft-index",
                            "99",
                            "--clarification-id",
                            "CLAR-099",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("requested draft index was not found", error_output)
            self.assertIn("Available indexes:", error_output)

    def test_promote_clarification_draft_fails_when_target_exists(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            goal_id = "GOAL-035"
            clarification_id = "CLAR-035"
            self._write_goal_and_draft(root, goal_id=goal_id)
            (root / "clarifications" / goal_id).mkdir(parents=True, exist_ok=True)
            existing_path = root / "clarifications" / goal_id / f"{clarification_id}.md"
            existing_path.write_text("# existing clarification\n", encoding="utf-8")

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "promote-clarification-draft",
                            "--root",
                            str(root),
                            "--goal-id",
                            goal_id,
                            "--draft-index",
                            "1",
                            "--clarification-id",
                            clarification_id,
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("Clarification artifact already exists", error_output)
            self.assertIn(existing_path.as_posix(), error_output)


class PromoteWorkItemDraftCliTest(unittest.TestCase):
    def _write_goal_and_draft(self, root, *, goal_id: str = "GOAL-037") -> None:
        DraftWorkItemsCliTest()._write_goal(root, goal_id=goal_id)
        DraftWorkItemsCliTest()._write_official_clarification(
            root,
            goal_id=goal_id,
            clarification_id="CLAR-037",
            status="resolved",
        )
        exit_code = main(
            [
                "draft-work-items",
                "--root",
                str(root),
                "--goal-id",
                goal_id,
            ]
        )
        self.assertEqual(exit_code, 0)

    def test_promote_work_item_draft_creates_one_official_artifact_via_create_path(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            goal_id = "GOAL-037"
            self._write_goal_and_draft(root, goal_id=goal_id)

            draft_path = root / "work_item_drafts" / f"{goal_id}.md"
            original_draft_content = draft_path.read_text(encoding="utf-8")

            exit_code = main(
                [
                    "promote-work-item-draft",
                    "--root",
                    str(root),
                    "--goal-id",
                    goal_id,
                    "--draft-index",
                    "1",
                    "--work-item-id",
                    "WI-037",
                ]
            )

            self.assertEqual(exit_code, 0)

            work_item_path = root / "docs" / "work-items" / "WI-037.md"
            self.assertTrue(work_item_path.exists())
            self.assertEqual(draft_path.read_text(encoding="utf-8"), original_draft_content)

            content = work_item_path.read_text(encoding="utf-8")
            self.assertIn("# WI-037: Define manual promotion boundary implementation", content)
            self.assertIn("## Work Item ID\nWI-037", content)
            self.assertIn(f"## Goal ID\n{goal_id}", content)
            self.assertIn("## Title\nDefine manual promotion boundary implementation", content)
            self.assertIn("## Status\ndraft", content)
            self.assertIn(
                "## Description\nPrepare the smallest work item for CLAR-037 under goal 'clarification drafting'",
                content,
            )
            self.assertIn("## Related Clarifications\n- CLAR-037 (resolved)", content)
            self.assertIn(
                "## Acceptance Criteria\nOperator can create one official work item linked to CLAR-037 "
                "without changing readiness, approval, queue, selector, active PR, or lifecycle semantics.",
                content,
            )
            self.assertNotIn("## Acceptance Criteria\nTBD", content)

    def test_promote_work_item_draft_fails_when_draft_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "promote-work-item-draft",
                            "--root",
                            str(root),
                            "--goal-id",
                            "GOAL-404",
                            "--draft-index",
                            "1",
                            "--work-item-id",
                            "WI-404",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("draft artifact was not found", error_output)
            self.assertIn((root / "work_item_drafts" / "GOAL-404.md").as_posix(), error_output)
            self.assertIn("factory draft-work-items", error_output)

    def test_promote_work_item_draft_fails_when_index_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_goal_and_draft(root)

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "promote-work-item-draft",
                            "--root",
                            str(root),
                            "--goal-id",
                            "GOAL-037",
                            "--draft-index",
                            "99",
                            "--work-item-id",
                            "WI-099",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("requested draft index was not found", error_output)
            self.assertIn("Available indexes:", error_output)

    def test_promote_work_item_draft_fails_when_target_exists(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            goal_id = "GOAL-037"
            work_item_id = "WI-037"
            self._write_goal_and_draft(root, goal_id=goal_id)
            (root / "docs" / "work-items").mkdir(parents=True, exist_ok=True)
            existing_path = root / "docs" / "work-items" / f"{work_item_id}.md"
            existing_path.write_text("# existing work item\n", encoding="utf-8")

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "promote-work-item-draft",
                            "--root",
                            str(root),
                            "--goal-id",
                            goal_id,
                            "--draft-index",
                            "1",
                            "--work-item-id",
                            work_item_id,
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("Work item artifact already exists", error_output)
            self.assertIn(existing_path.as_posix(), error_output)


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
                        "",
                        "Approval Queue:",
                        "- pending_total: 0",
                        "- latest_run_has_pending: unavailable",
                        "- stale_pending_count: 0",
                        "- stale_pending_run_ids: none",
                        "- stale_pending_path: none",
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


class WorkItemReadinessCliTest(unittest.TestCase):
    def _write_work_item(self, root, *, work_item_id: str, goal_id: str, related_lines: list[str] | None = None) -> None:
        (root / "docs" / "work-items").mkdir(parents=True, exist_ok=True)
        lines = [
            f"# {work_item_id}: readiness visibility",
            "",
            "## Work Item ID",
            work_item_id,
            "",
            "## Goal ID",
            goal_id,
            "",
            "## Title",
            "readiness visibility",
            "",
            "## Status",
            "draft",
            "",
            "## Description",
            "Show linked clarification readiness without changing semantics.",
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
        (root / "docs" / "work-items" / f"{work_item_id}.md").write_text("\n".join(lines), encoding="utf-8")

    def _write_clarification(self, root, *, goal_id: str, clarification_id: str, status: str) -> None:
        (root / "clarifications" / goal_id).mkdir(parents=True, exist_ok=True)
        (root / "clarifications" / goal_id / f"{clarification_id}.md").write_text(
            "\n".join(
                [
                    f"# {clarification_id}: readiness visibility",
                    "",
                    "## Clarification ID",
                    clarification_id,
                    "",
                    "## Goal ID",
                    goal_id,
                    "",
                    "## Title",
                    "readiness visibility",
                    "",
                    "## Status",
                    status,
                    "",
                    "## Category",
                    "scope",
                    "",
                    "## Question",
                    "Can the operator proceed?",
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

    def test_work_item_readiness_returns_no_linked_clarifications(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_work_item(root, work_item_id="WI-020", goal_id="GOAL-020")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["work-item-readiness", "--root", str(root), "--work-item-id", "WI-020"])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                stdout.getvalue(),
                "\n".join(
                    [
                        "Work Item Readiness:",
                        "- work_item_id: WI-020",
                        "- goal_id: GOAL-020",
                        "- linked_clarification_count: 0",
                        "",
                        "Clarifications:",
                        "- none",
                        "",
                        "Overall Readiness:",
                        "- summary: no-linked-clarifications",
                    ]
                )
                + "\n",
            )

    def test_work_item_readiness_returns_ready_when_all_linked_clarifications_are_resolved(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_work_item(
                root,
                work_item_id="WI-020",
                goal_id="GOAL-020",
                related_lines=["- CLAR-001 (open)", "- CLAR-002 (resolved)"],
            )
            self._write_clarification(root, goal_id="GOAL-020", clarification_id="CLAR-001", status="resolved")
            self._write_clarification(root, goal_id="GOAL-020", clarification_id="CLAR-002", status="resolved")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["work-item-readiness", "--root", str(root), "--work-item-id", "WI-020"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- CLAR-001: resolved", output)
            self.assertIn("- CLAR-002: resolved", output)
            self.assertIn("- summary: ready", output)

    def test_work_item_readiness_returns_attention_needed_when_open_deferred_or_escalated_exists(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_work_item(
                root,
                work_item_id="WI-020",
                goal_id="GOAL-020",
                related_lines=["- CLAR-001 (resolved)", "- CLAR-002 (resolved)", "- CLAR-003 (resolved)"],
            )
            self._write_clarification(root, goal_id="GOAL-020", clarification_id="CLAR-001", status="open")
            self._write_clarification(root, goal_id="GOAL-020", clarification_id="CLAR-002", status="deferred")
            self._write_clarification(root, goal_id="GOAL-020", clarification_id="CLAR-003", status="escalated")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["work-item-readiness", "--root", str(root), "--work-item-id", "WI-020"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- CLAR-001: open", output)
            self.assertIn("- CLAR-002: deferred", output)
            self.assertIn("- CLAR-003: escalated", output)
            self.assertIn("- summary: attention-needed", output)

    def test_work_item_readiness_fails_when_work_item_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(["work-item-readiness", "--root", str(root), "--work-item-id", "WI-404"])

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("work item artifact was not found", error_output)
            self.assertIn((root / "docs" / "work-items" / "WI-404.md").as_posix(), error_output)

    def test_work_item_readiness_fails_when_linked_clarification_artifact_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_work_item(
                root,
                work_item_id="WI-020",
                goal_id="GOAL-020",
                related_lines=["- CLAR-404 (open)"],
            )

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(["work-item-readiness", "--root", str(root), "--work-item-id", "WI-020"])

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("linked clarification artifact was not found", error_output)
            self.assertIn((root / "clarifications" / "GOAL-020" / "CLAR-404.md").as_posix(), error_output)


class CreatePrPlanCliTest(unittest.TestCase):
    def _write_work_item(self, root, *, work_item_id: str, goal_id: str, related_lines: list[str] | None = None) -> None:
        (root / "docs" / "work-items").mkdir(parents=True, exist_ok=True)
        lines = [
            f"# {work_item_id}: pr plan readiness visibility",
            "",
            "## Work Item ID",
            work_item_id,
            "",
            "## Goal ID",
            goal_id,
            "",
            "## Title",
            "pr plan readiness visibility",
            "",
            "## Status",
            "draft",
            "",
            "## Description",
            "Persist readiness visibility into the PR plan artifact.",
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
        (root / "docs" / "work-items" / f"{work_item_id}.md").write_text("\n".join(lines), encoding="utf-8")

    def _write_clarification(self, root, *, goal_id: str, clarification_id: str, status: str) -> None:
        (root / "clarifications" / goal_id).mkdir(parents=True, exist_ok=True)
        (root / "clarifications" / goal_id / f"{clarification_id}.md").write_text(
            "\n".join(
                [
                    f"# {clarification_id}: pr plan readiness visibility",
                    "",
                    "## Clarification ID",
                    clarification_id,
                    "",
                    "## Goal ID",
                    goal_id,
                    "",
                    "## Title",
                    "pr plan readiness visibility",
                    "",
                    "## Status",
                    status,
                    "",
                    "## Category",
                    "scope",
                    "",
                    "## Question",
                    "Should this plan move forward?",
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

    def test_create_pr_plan_creates_active_markdown_artifact_without_existing_active(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_work_item(root, work_item_id="WI-010", goal_id="GOAL-010")

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
            self.assertIn("## Work Item Readiness\n- summary: no-linked-clarifications", content)
            self.assertIn("## Linked Clarifications\n- none", content)
            self.assertIn("## Scope\n- TBD", content)
            self.assertIn("## Out of Scope\n- TBD", content)
            self.assertIn("## Implementation Notes\n- TBD", content)
            self.assertIn("## Risks\n- TBD", content)
            self.assertIn("## Open Questions\n- TBD", content)

    def test_create_pr_plan_creates_archive_candidate_when_active_pr_already_exists(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_work_item(root, work_item_id="WI-010", goal_id="GOAL-010")
            self._write_work_item(root, work_item_id="WI-011", goal_id="GOAL-011")

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

    def test_create_pr_plan_records_ready_linked_clarifications_in_markdown_and_output(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_work_item(
                root,
                work_item_id="WI-021",
                goal_id="GOAL-021",
                related_lines=["- CLAR-001 (open)", "- CLAR-002 (resolved)"],
            )
            self._write_clarification(root, goal_id="GOAL-021", clarification_id="CLAR-001", status="resolved")
            self._write_clarification(root, goal_id="GOAL-021", clarification_id="CLAR-002", status="resolved")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "create-pr-plan",
                        "--root",
                        str(root),
                        "--pr-id",
                        "PR-021",
                        "--work-item-id",
                        "WI-021",
                        "--title",
                        "PR plan readiness visibility",
                        "--summary",
                        "Persist source work item readiness context in the PR plan artifact.",
                    ]
                )

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- work_item_readiness: ready", output)
            self.assertIn("- linked_clarifications: 2", output)

            content = (root / "prs" / "active" / "PR-021.md").read_text(encoding="utf-8")
            self.assertIn("## Work Item Readiness\n- summary: ready\n- linked_clarification_count: 2", content)
            self.assertIn("## Linked Clarifications\n- CLAR-001 (resolved)\n- CLAR-002 (resolved)", content)

    def test_create_pr_plan_records_attention_needed_without_blocking_creation(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_work_item(
                root,
                work_item_id="WI-022",
                goal_id="GOAL-022",
                related_lines=["- CLAR-001 (resolved)", "- CLAR-002 (resolved)", "- CLAR-003 (resolved)"],
            )
            self._write_clarification(root, goal_id="GOAL-022", clarification_id="CLAR-001", status="open")
            self._write_clarification(root, goal_id="GOAL-022", clarification_id="CLAR-002", status="deferred")
            self._write_clarification(root, goal_id="GOAL-022", clarification_id="CLAR-003", status="escalated")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "create-pr-plan",
                        "--root",
                        str(root),
                        "--pr-id",
                        "PR-022",
                        "--work-item-id",
                        "WI-022",
                        "--title",
                        "Non-blocking readiness visibility",
                        "--summary",
                        "Add visibility without changing PR planning semantics.",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertTrue((root / "prs" / "active" / "PR-022.md").exists())
            output = stdout.getvalue()
            self.assertIn("- work_item_readiness: attention-needed", output)
            self.assertIn("- linked_clarifications: 3", output)

            content = (root / "prs" / "active" / "PR-022.md").read_text(encoding="utf-8")
            self.assertIn("## Work Item Readiness\n- summary: attention-needed", content)
            self.assertIn("- CLAR-001 (open)", content)
            self.assertIn("- CLAR-002 (deferred)", content)
            self.assertIn("- CLAR-003 (escalated)", content)

    def test_create_pr_plan_fails_when_source_work_item_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "create-pr-plan",
                            "--root",
                            str(root),
                            "--pr-id",
                            "PR-404",
                            "--work-item-id",
                            "WI-404",
                            "--title",
                            "Missing source work item",
                            "--summary",
                            "This should fail clearly.",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("work item artifact was not found", error_output)
            self.assertIn((root / "docs" / "work-items" / "WI-404.md").as_posix(), error_output)


class DraftPrPlanCliTest(unittest.TestCase):
    def _write_work_item(self, root, *, work_item_id: str, goal_id: str) -> None:
        (root / "docs" / "work-items").mkdir(parents=True, exist_ok=True)
        lines = [
            f"# {work_item_id}: official draft source",
            "",
            "## Work Item ID",
            work_item_id,
            "",
            "## Goal ID",
            goal_id,
            "",
            "## Title",
            "official draft source",
            "",
            "## Status",
            "draft",
            "",
            "## Description",
            "Use the official work item as the PR draft source of truth.",
            "",
            "## Related Clarifications",
            "- CLAR-038 (resolved)",
            "",
            "## Scope",
            "- add CLI entrypoint",
            "",
            "## Out of Scope",
            "- mutate active PR lifecycle",
            "",
            "## Acceptance Criteria",
            "- artifact is written under pr_plan_drafts/",
            "",
            "## Dependencies",
            "- docs sync",
            "",
            "## Risks",
            "- operator may confuse draft with official PR plan",
            "",
            "## Notes",
            "- keep create-pr-plan semantics unchanged",
            "",
        ]
        (root / "docs" / "work-items" / f"{work_item_id}.md").write_text("\n".join(lines), encoding="utf-8")

    def test_draft_pr_plan_creates_artifact_only_draft_from_official_work_item(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_work_item(root, work_item_id="WI-038", goal_id="GOAL-038")
            (root / "work_item_drafts").mkdir(parents=True, exist_ok=True)
            (root / "work_item_drafts" / "GOAL-038.md").write_text(
                "# misleading draft\n\n## Candidate Work Items\n\n### Candidate 01\n- title: do not read me\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "draft-pr-plan",
                        "--root",
                        str(root),
                        "--work-item-id",
                        "WI-038",
                    ]
                )

            self.assertEqual(exit_code, 0)

            draft_path = root / "pr_plan_drafts" / "WI-038.md"
            self.assertTrue(draft_path.exists())
            self.assertFalse((root / "prs" / "active").exists())
            self.assertFalse((root / "prs" / "archive").exists())

            content = draft_path.read_text(encoding="utf-8")
            self.assertIn("# PR Plan Draft: WI-038", content)
            self.assertIn("## Work Item ID\nWI-038", content)
            self.assertIn("## Goal ID\nGOAL-038", content)
            self.assertIn("## Work Item Title\nofficial draft source", content)
            self.assertIn("## Source Work Item\n" + (root / "docs" / "work-items" / "WI-038.md").as_posix(), content)
            self.assertIn("## Draft Status\ndraft-only", content)
            self.assertIn("## Draft Method\ndeterministic-rule-based", content)
            self.assertIn("## Suggested PR Title\nofficial draft source", content)
            self.assertIn("## Source Description\nUse the official work item as the PR draft source of truth.", content)
            self.assertIn("## Linked Clarifications\n- CLAR-038 (resolved)", content)
            self.assertIn("## Scope Seed\n- add CLI entrypoint", content)
            self.assertIn("## Out of Scope Seed\n- mutate active PR lifecycle", content)
            self.assertIn("## Acceptance Seed\n- artifact is written under pr_plan_drafts/", content)
            self.assertIn("## Dependency Seed\n- docs sync", content)
            self.assertIn("## Risk Seed\n- operator may confuse draft with official PR plan", content)
            self.assertIn("## Note Seed\n- keep create-pr-plan semantics unchanged", content)
            self.assertIn("never reads `work_item_drafts/`", content)
            self.assertNotIn("do not read me", content)

            output = stdout.getvalue()
            self.assertIn("PR Plan Draft Created:", output)
            self.assertIn("- work_item_id: WI-038", output)
            self.assertIn(draft_path.as_posix(), output)

    def test_draft_pr_plan_fails_when_work_item_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(["draft-pr-plan", "--root", str(root), "--work-item-id", "WI-404"])

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("official work item artifact was not found", error_output)
            self.assertIn((root / "docs" / "work-items" / "WI-404.md").as_posix(), error_output)

    def test_draft_pr_plan_fails_when_draft_artifact_already_exists(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_work_item(root, work_item_id="WI-038", goal_id="GOAL-038")
            (root / "pr_plan_drafts").mkdir(parents=True, exist_ok=True)
            existing_path = root / "pr_plan_drafts" / "WI-038.md"
            existing_path.write_text("# existing draft\n", encoding="utf-8")

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(["draft-pr-plan", "--root", str(root), "--work-item-id", "WI-038"])

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("PR plan draft artifact already exists", error_output)
            self.assertIn(existing_path.as_posix(), error_output)


class PromotePrPlanDraftCliTest(unittest.TestCase):
    def _write_work_item(self, root, *, work_item_id: str = "WI-039", goal_id: str = "GOAL-039") -> None:
        DraftPrPlanCliTest()._write_work_item(root, work_item_id=work_item_id, goal_id=goal_id)
        (root / "clarifications" / goal_id).mkdir(parents=True, exist_ok=True)
        (root / "clarifications" / goal_id / "CLAR-038.md").write_text(
            "\n".join(
                [
                    "# CLAR-038: linked clarification",
                    "",
                    "## Clarification ID",
                    "CLAR-038",
                    "",
                    "## Goal ID",
                    goal_id,
                    "",
                    "## Title",
                    "linked clarification",
                    "",
                    "## Status",
                    "resolved",
                    "",
                    "## Category",
                    "scope",
                    "",
                    "## Question",
                    "Is the source linkage ready?",
                    "",
                    "## Suggested Resolution",
                    "- yes",
                    "",
                    "## Escalation Required",
                    "no",
                    "",
                    "## Resolution Notes",
                    "- captured for readiness",
                    "",
                    "## Next Action",
                    "- proceed",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def _write_draft(self, root, *, work_item_id: str = "WI-039") -> None:
        exit_code = main(
            [
                "draft-pr-plan",
                "--root",
                str(root),
                "--work-item-id",
                work_item_id,
            ]
        )
        self.assertEqual(exit_code, 0)

    def test_promote_pr_plan_draft_creates_one_official_artifact_via_create_path(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_work_item(root, work_item_id="WI-039", goal_id="GOAL-039")
            self._write_draft(root, work_item_id="WI-039")

            draft_path = root / "pr_plan_drafts" / "WI-039.md"
            original_draft_content = draft_path.read_text(encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "promote-pr-plan-draft",
                        "--root",
                        str(root),
                        "--work-item-id",
                        "WI-039",
                    ]
                )

            self.assertEqual(exit_code, 0)

            pr_plan_path = root / "prs" / "active" / "PR-039.md"
            self.assertTrue(pr_plan_path.exists())
            self.assertEqual(draft_path.read_text(encoding="utf-8"), original_draft_content)

            content = pr_plan_path.read_text(encoding="utf-8")
            self.assertIn("# PR-039: official draft source", content)
            self.assertIn("## PR ID\nPR-039", content)
            self.assertIn("## Work Item ID\nWI-039", content)
            self.assertIn("## Title\nofficial draft source", content)
            self.assertIn(
                "## Summary\nImplement WI-039 using the official work item artifact as the source of truth.",
                content,
            )
            self.assertIn("## Scope\n- add CLI entrypoint", content)
            self.assertIn("## Out of Scope\n- mutate active PR lifecycle", content)
            self.assertIn("## Implementation Notes\n- validation intent: artifact is written under pr_plan_drafts/", content)
            self.assertIn("- dependency seed: docs sync", content)
            self.assertIn("- note seed: keep create-pr-plan semantics unchanged", content)
            self.assertIn("## Risks\n- operator may confuse draft with official PR plan", content)
            self.assertIn("## Open Questions\n- TBD", content)

            output = stdout.getvalue()
            self.assertIn("PR Plan Draft Promoted:", output)
            self.assertIn("- pr_id: PR-039", output)
            self.assertIn("- location: active", output)
            self.assertIn(pr_plan_path.as_posix(), output)

    def test_promote_pr_plan_draft_respects_existing_active_archive_semantics(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_work_item(root, work_item_id="WI-039", goal_id="GOAL-039")
            self._write_draft(root, work_item_id="WI-039")
            (root / "prs" / "active").mkdir(parents=True, exist_ok=True)
            (root / "prs" / "active" / "PR-000.md").write_text("# existing active\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(
                    [
                        "promote-pr-plan-draft",
                        "--root",
                        str(root),
                        "--work-item-id",
                        "WI-039",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertTrue((root / "prs" / "archive" / "PR-039.md").exists())
            self.assertFalse((root / "prs" / "active" / "PR-039.md").exists())
            self.assertIn("- location: archive", stdout.getvalue())

    def test_promote_pr_plan_draft_fails_when_draft_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "promote-pr-plan-draft",
                            "--root",
                            str(root),
                            "--work-item-id",
                            "WI-404",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("draft artifact was not found", error_output)
            self.assertIn((root / "pr_plan_drafts" / "WI-404.md").as_posix(), error_output)
            self.assertIn("factory draft-pr-plan", error_output)

    def test_promote_pr_plan_draft_fails_when_create_pr_plan_constraints_conflict(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_work_item(root, work_item_id="WI-039", goal_id="GOAL-039")
            self._write_draft(root, work_item_id="WI-039")
            (root / "prs" / "active").mkdir(parents=True, exist_ok=True)
            existing_path = root / "prs" / "active" / "PR-039.md"
            existing_path.write_text("# existing plan\n", encoding="utf-8")

            stderr = StringIO()
            with redirect_stderr(stderr):
                with self.assertRaises(SystemExit) as exc_info:
                    main(
                        [
                            "promote-pr-plan-draft",
                            "--root",
                            str(root),
                            "--work-item-id",
                            "WI-039",
                        ]
                    )

            self.assertEqual(exc_info.exception.code, 2)
            error_output = stderr.getvalue()
            self.assertIn("PR plan artifact already exists", error_output)
            self.assertIn(existing_path.as_posix(), error_output)


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
            _write_minimal_work_item(root, work_item_id="WI-013", goal_id="GOAL-013")
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
                        "Work Item Readiness:",
                        "- summary: no-linked-clarifications",
                        "- linked_clarifications: 0",
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
                        "Approval Queue:",
                        "- pending_total: 1",
                        "- latest_run_has_pending: True",
                        "- stale_pending_count: 0",
                        "- stale_pending_run_ids: none",
                        "- stale_pending_path: none",
                        "",
                        "Open Clarifications (1):",
                        "- clarification_id: CLAR-001",
                    ]
                )
                + "\n",
            )

    def test_status_keeps_existing_output_when_no_active_pr_exists(self) -> None:
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
                        "",
                        "Approval Queue:",
                        "- pending_total: 0",
                        "- latest_run_has_pending: unavailable",
                        "- stale_pending_count: 0",
                        "- stale_pending_run_ids: none",
                        "- stale_pending_path: none",
                    ]
                )
                + "\n",
            )

    def test_status_shows_no_linked_clarifications_for_active_pr_work_item(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_minimal_work_item(root, work_item_id="WI-022", goal_id="GOAL-022")
            (root / "prs" / "active").mkdir(parents=True, exist_ok=True)
            (root / "prs" / "active" / "PR-022.md").write_text(
                "# PR-022\n\n## PR ID\nPR-022\n\n## Work Item ID\nWI-022\n\n## Title\nstatus readiness\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["status", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Work Item Readiness:", output)
            self.assertIn("- summary: no-linked-clarifications", output)
            self.assertIn("- linked_clarifications: 0", output)

    def test_status_shows_ready_for_active_pr_work_item_when_all_linked_clarifications_are_resolved(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "work-items").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "work-items" / "WI-023.md").write_text(
                "\n".join(
                    [
                        "# WI-023: readiness visibility",
                        "",
                        "## Work Item ID",
                        "WI-023",
                        "",
                        "## Goal ID",
                        "GOAL-023",
                        "",
                        "## Title",
                        "readiness visibility",
                        "",
                        "## Status",
                        "draft",
                        "",
                        "## Description",
                        "Status should reuse readiness visibility.",
                        "",
                        "## Related Clarifications",
                        "- CLAR-001 (open)",
                        "- CLAR-002 (resolved)",
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
            (root / "clarifications" / "GOAL-023").mkdir(parents=True, exist_ok=True)
            (root / "clarifications" / "GOAL-023" / "CLAR-001.md").write_text(
                "# CLAR-001\n\n## Clarification ID\nCLAR-001\n\n## Goal ID\nGOAL-023\n\n## Status\nresolved\n",
                encoding="utf-8",
            )
            (root / "clarifications" / "GOAL-023" / "CLAR-002.md").write_text(
                "# CLAR-002\n\n## Clarification ID\nCLAR-002\n\n## Goal ID\nGOAL-023\n\n## Status\nresolved\n",
                encoding="utf-8",
            )
            (root / "prs" / "active").mkdir(parents=True, exist_ok=True)
            (root / "prs" / "active" / "PR-023.md").write_text(
                "# PR-023\n\n## PR ID\nPR-023\n\n## Work Item ID\nWI-023\n\n## Title\nstatus readiness\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["status", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- summary: ready", output)
            self.assertIn("- linked_clarifications: 2", output)

    def test_status_shows_attention_needed_for_active_pr_work_item_when_open_deferred_or_escalated_exists(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "work-items").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "work-items" / "WI-024.md").write_text(
                "\n".join(
                    [
                        "# WI-024: readiness visibility",
                        "",
                        "## Work Item ID",
                        "WI-024",
                        "",
                        "## Goal ID",
                        "GOAL-024",
                        "",
                        "## Title",
                        "readiness visibility",
                        "",
                        "## Status",
                        "draft",
                        "",
                        "## Description",
                        "Status should show attention-needed without blocking.",
                        "",
                        "## Related Clarifications",
                        "- CLAR-001 (resolved)",
                        "- CLAR-002 (resolved)",
                        "- CLAR-003 (resolved)",
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
            (root / "clarifications" / "GOAL-024").mkdir(parents=True, exist_ok=True)
            (root / "clarifications" / "GOAL-024" / "CLAR-001.md").write_text(
                "# CLAR-001\n\n## Clarification ID\nCLAR-001\n\n## Goal ID\nGOAL-024\n\n## Status\nopen\n",
                encoding="utf-8",
            )
            (root / "clarifications" / "GOAL-024" / "CLAR-002.md").write_text(
                "# CLAR-002\n\n## Clarification ID\nCLAR-002\n\n## Goal ID\nGOAL-024\n\n## Status\ndeferred\n",
                encoding="utf-8",
            )
            (root / "clarifications" / "GOAL-024" / "CLAR-003.md").write_text(
                "# CLAR-003\n\n## Clarification ID\nCLAR-003\n\n## Goal ID\nGOAL-024\n\n## Status\nescalated\n",
                encoding="utf-8",
            )
            (root / "prs" / "active").mkdir(parents=True, exist_ok=True)
            (root / "prs" / "active" / "PR-024.md").write_text(
                "# PR-024\n\n## PR ID\nPR-024\n\n## Work Item ID\nWI-024\n\n## Title\nstatus readiness\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["status", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- summary: attention-needed", output)
            self.assertIn("- linked_clarifications: 3", output)

    def test_status_limits_readiness_failure_to_readiness_section(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "work-items").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "work-items" / "WI-025.md").write_text(
                "\n".join(
                    [
                        "# WI-025: readiness visibility",
                        "",
                        "## Work Item ID",
                        "WI-025",
                        "",
                        "## Goal ID",
                        "GOAL-025",
                        "",
                        "## Title",
                        "readiness visibility",
                        "",
                        "## Status",
                        "draft",
                        "",
                        "## Description",
                        "Status should degrade safely if readiness artifacts are missing.",
                        "",
                        "## Related Clarifications",
                        "- CLAR-404 (open)",
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
            (root / "prs" / "active").mkdir(parents=True, exist_ok=True)
            (root / "prs" / "active" / "PR-025.md").write_text(
                "# PR-025\n\n## PR ID\nPR-025\n\n## Work Item ID\nWI-025\n\n## Title\nstatus readiness\n",
                encoding="utf-8",
            )
            (root / "runs" / "latest" / "RUN-025").mkdir(parents=True, exist_ok=True)
            (root / "runs" / "latest" / "RUN-025" / "run.yaml").write_text(
                "\n".join(
                    [
                        "run:",
                        "  run_id: RUN-025",
                        "  work_item_id: WI-025",
                        "  pr_id: PR-025",
                        "  state: in_progress",
                        "  created_at: '2026-03-29T00:00:00+00:00'",
                        "  updated_at: '2026-03-29T00:00:00+00:00'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["status", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Work Item Readiness:", output)
            self.assertIn("- status: unavailable", output)
            self.assertIn("- work_item_id: WI-025", output)
            self.assertIn("linked clarification artifact was not found", output)
            self.assertIn("Latest Run:", output)
            self.assertIn("- run_id: RUN-025", output)
            self.assertIn("Approval:", output)


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
                        "",
                        "Approval Queue:",
                        "- pending_total: 0",
                        "- latest_run_has_pending: False",
                        "- stale_pending_count: 0",
                        "- stale_pending_run_ids: none",
                        "- stale_pending_path: none",
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
                        "",
                        "Approval Queue:",
                        "- pending_total: 0",
                        "- latest_run_has_pending: False",
                        "- stale_pending_count: 0",
                        "- stale_pending_run_ids: none",
                        "- stale_pending_path: none",
                    ]
                )
                + "\n",
            )

    def test_status_shows_approval_queue_visibility_when_latest_run_has_only_matching_pending_item(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "runs" / "latest" / "RUN-101").mkdir(parents=True, exist_ok=True)
            (root / "runs" / "latest" / "RUN-101" / "run.yaml").write_text(
                "\n".join(
                    [
                        "run:",
                        "  run_id: RUN-101",
                        "  work_item_id: WI-101",
                        "  pr_id: PR-101",
                        "  state: approval_pending",
                        "  created_at: '2026-03-29T01:00:00+00:00'",
                        "  updated_at: '2026-03-29T01:00:00+00:00'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (root / "approval_queue" / "pending").mkdir(parents=True, exist_ok=True)
            (root / "approval_queue" / "pending" / "APR-RUN-101.yaml").write_text(
                "approval_request:\n  id: APR-RUN-101\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["status", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Approval Queue:", output)
            self.assertIn("- pending_total: 1", output)
            self.assertIn("- latest_run_has_pending: True", output)
            self.assertIn("- stale_pending_count: 0", output)
            self.assertIn("- stale_pending_run_ids: none", output)
            self.assertIn("- stale_pending_path: none", output)
            self.assertIn("Latest Run:\n- run_id: RUN-101", output)
            self.assertIn("Approval:\n- status: pending", output)

    def test_status_shows_stale_pending_visibility_without_changing_latest_approval_semantics(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "runs" / "latest" / "RUN-200").mkdir(parents=True, exist_ok=True)
            (root / "runs" / "latest" / "RUN-200" / "run.yaml").write_text(
                "\n".join(
                    [
                        "run:",
                        "  run_id: RUN-200",
                        "  work_item_id: WI-200",
                        "  pr_id: PR-200",
                        "  state: approval_pending",
                        "  created_at: '2026-03-29T02:00:00+00:00'",
                        "  updated_at: '2026-03-29T02:00:00+00:00'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (root / "approval_queue" / "pending").mkdir(parents=True, exist_ok=True)
            matching = root / "approval_queue" / "pending" / "APR-RUN-200.yaml"
            stale = root / "approval_queue" / "pending" / "APR-RUN-150.yaml"
            matching.write_text("approval_request:\n  id: APR-RUN-200\n", encoding="utf-8")
            stale.write_text("approval_request:\n  id: APR-RUN-150\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["status", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- status: pending", output)
            self.assertIn(f"- path: {matching.as_posix()}", output)
            self.assertIn("Approval Queue:", output)
            self.assertIn("- pending_total: 2", output)
            self.assertIn("- latest_run_has_pending: True", output)
            self.assertIn("- stale_pending_count: 1", output)
            self.assertIn("- stale_pending_run_ids: RUN-150", output)
            self.assertIn(f"- stale_pending_path: {stale.as_posix()}", output)

    def test_status_reports_pending_queue_visibility_when_latest_run_is_absent(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "approval_queue" / "pending").mkdir(parents=True, exist_ok=True)
            older = root / "approval_queue" / "pending" / "APR-RUN-OLD.yaml"
            retried = root / "approval_queue" / "pending" / "APR-RUN-OLD--r2.yaml"
            older.write_text("approval_request:\n  id: APR-RUN-OLD\n", encoding="utf-8")
            retried.write_text("approval_request:\n  id: APR-RUN-OLD\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["status", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Latest Run:\n- none", output)
            self.assertIn("Approval:\n- status: none", output)
            self.assertIn("Approval Queue:", output)
            self.assertIn("- pending_total: 2", output)
            self.assertIn("- latest_run_has_pending: unavailable", output)
            self.assertIn("- stale_pending_count: 2", output)
            self.assertIn("- stale_pending_run_ids: RUN-OLD, RUN-OLD", output)
            self.assertIn(f"- stale_pending_path: {older.as_posix()}", output)
            self.assertIn(f"- stale_pending_path: {retried.as_posix()}", output)

    def test_inspect_approval_queue_shows_none_when_pending_queue_is_empty(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-approval-queue", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                stdout.getvalue(),
                "\n".join(
                    [
                        "Approval Queue Inspection:",
                        "- latest_run_id: none",
                        "- pending_total: 0",
                        "",
                        "Pending Approvals:",
                        "- none",
                    ]
                )
                + "\n",
            )

    def test_inspect_approval_queue_shows_one_pending_item_matching_latest_run(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs" / "latest" / "RUN-301"
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "run.yaml").write_text(
                "\n".join(
                    [
                        "run:",
                        "  run_id: RUN-301",
                        "  work_item_id: WI-301",
                        "  pr_id: PR-301",
                        "  state: approval_pending",
                        "  created_at: '2026-03-29T03:00:00+00:00'",
                        "  updated_at: '2026-03-29T03:00:00+00:00'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            pending = root / "approval_queue" / "pending"
            pending.mkdir(parents=True, exist_ok=True)
            queue_item = pending / "APR-RUN-301.yaml"
            queue_item.write_text(
                "\n".join(
                    [
                        "approval_request:",
                        "  id: APR-RUN-301",
                        "  readiness_context:",
                        "    status: available",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-approval-queue", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Approval Queue Inspection:", output)
            self.assertIn("- latest_run_id: RUN-301", output)
            self.assertIn("- pending_total: 1", output)
            self.assertIn("- item: 1", output)
            self.assertIn(f"  path: {queue_item.as_posix()}", output)
            self.assertIn("  parsed_run_id: RUN-301", output)
            self.assertIn("  latest_relation: latest", output)
            self.assertIn(f"  matching_run_path: {(run_dir / 'run.yaml').as_posix()}", output)
            self.assertIn("  matching_run_state: approval_pending", output)
            self.assertIn("  readiness_context: present", output)
            self.assertIn("  note: none", output)

    def test_inspect_approval_queue_shows_latest_and_stale_pending_items(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            latest_dir = root / "runs" / "latest" / "RUN-410"
            latest_dir.mkdir(parents=True, exist_ok=True)
            (latest_dir / "run.yaml").write_text(
                "\n".join(
                    [
                        "run:",
                        "  run_id: RUN-410",
                        "  work_item_id: WI-410",
                        "  pr_id: PR-410",
                        "  state: approval_pending",
                        "  created_at: '2026-03-29T04:10:00+00:00'",
                        "  updated_at: '2026-03-29T04:10:00+00:00'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            stale_dir = root / "runs" / "latest" / "RUN-405"
            stale_dir.mkdir(parents=True, exist_ok=True)
            (stale_dir / "run.yaml").write_text(
                "\n".join(
                    [
                        "run:",
                        "  run_id: RUN-405",
                        "  work_item_id: WI-405",
                        "  pr_id: PR-405",
                        "  state: in_progress",
                        "  created_at: '2026-03-29T04:05:00+00:00'",
                        "  updated_at: '2026-03-29T04:05:00+00:00'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            pending = root / "approval_queue" / "pending"
            pending.mkdir(parents=True, exist_ok=True)
            (pending / "APR-RUN-410.yaml").write_text("approval_request:\n  id: APR-RUN-410\n", encoding="utf-8")
            stale_item = pending / "APR-RUN-405.yaml"
            stale_item.write_text("approval_request:\n  id: APR-RUN-405\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-approval-queue", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- latest_run_id: RUN-410", output)
            self.assertIn("- pending_total: 2", output)
            self.assertIn("  latest_relation: latest", output)
            self.assertIn(f"  path: {stale_item.as_posix()}", output)
            self.assertIn("  parsed_run_id: RUN-405", output)
            self.assertIn("  latest_relation: stale", output)
            self.assertIn(f"  matching_run_path: {(stale_dir / 'run.yaml').as_posix()}", output)
            self.assertIn("  matching_run_state: in_progress", output)
            self.assertIn("  readiness_context: absent", output)

    def test_inspect_approval_queue_reports_no_latest_run_when_pending_items_exist(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            pending = root / "approval_queue" / "pending"
            pending.mkdir(parents=True, exist_ok=True)
            queue_item = pending / "APR-RUN-501.yaml"
            queue_item.write_text("approval_request:\n  id: APR-RUN-501\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-approval-queue", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- latest_run_id: none", output)
            self.assertIn(f"  path: {queue_item.as_posix()}", output)
            self.assertIn("  parsed_run_id: RUN-501", output)
            self.assertIn("  latest_relation: no-latest-run", output)
            self.assertIn("  matching_run_path: none", output)
            self.assertIn("  matching_run_state: none", output)
            self.assertIn("matching run missing from filesystem", output)

    def test_inspect_approval_queue_degrades_safely_for_unparseable_run_id(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            pending = root / "approval_queue" / "pending"
            pending.mkdir(parents=True, exist_ok=True)
            queue_item = pending / "APR---r2.yaml"
            queue_item.write_text("approval_request:\n  id: APR-UNKNOWN\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-approval-queue", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn(f"  path: {queue_item.as_posix()}", output)
            self.assertIn("  parsed_run_id: unparseable", output)
            self.assertIn("  latest_relation: unparseable", output)
            self.assertIn("  matching_run_path: none", output)
            self.assertIn("  matching_run_state: none", output)
            self.assertIn("could not parse run_id from pending approval filename", output)

    def test_inspect_approval_queue_degrades_safely_when_matching_run_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            latest_dir = root / "runs" / "latest" / "RUN-601"
            latest_dir.mkdir(parents=True, exist_ok=True)
            (latest_dir / "run.yaml").write_text(
                "\n".join(
                    [
                        "run:",
                        "  run_id: RUN-601",
                        "  work_item_id: WI-601",
                        "  pr_id: PR-601",
                        "  state: approval_pending",
                        "  created_at: '2026-03-29T06:01:00+00:00'",
                        "  updated_at: '2026-03-29T06:01:00+00:00'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            pending = root / "approval_queue" / "pending"
            pending.mkdir(parents=True, exist_ok=True)
            queue_item = pending / "APR-RUN-600.yaml"
            queue_item.write_text("approval_request:\n  id: APR-RUN-600\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-approval-queue", "--root", str(root)])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn(f"  path: {queue_item.as_posix()}", output)
            self.assertIn("  parsed_run_id: RUN-600", output)
            self.assertIn("  latest_relation: stale", output)
            self.assertIn("  matching_run_path: none", output)
            self.assertIn("  matching_run_state: none", output)
            self.assertIn("matching run missing from filesystem", output)

    def test_inspect_approval_latest_successfully(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs" / "latest" / "RUN-701"
            artifacts = run_dir / "artifacts"
            artifacts.mkdir(parents=True, exist_ok=True)
            (run_dir / "run.yaml").write_text(
                "\n".join(
                    [
                        "run:",
                        "  run_id: RUN-701",
                        "  work_item_id: WI-701",
                        "  pr_id: PR-701",
                        "  state: approval_pending",
                        "  created_at: '2026-03-29T07:01:00+00:00'",
                        "  updated_at: '2026-03-29T07:01:00+00:00'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            evidence_path = artifacts / "evidence-bundle.yaml"
            evidence_path.write_text("evidence_bundle:\n  run_id: RUN-701\n", encoding="utf-8")
            approval_path = artifacts / "approval-request.yaml"
            approval_path.write_text(
                "\n".join(
                    [
                        "approval_request:",
                        "  id: APR-RUN-701",
                        "  status: pending",
                        f"  evidence_bundle: {evidence_path.as_posix()}",
                        "  readiness_context:",
                        "    status: available",
                        "    readiness_summary: ready",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-approval", "--root", str(root), "--latest"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Approval Inspection:", output)
            self.assertIn("- run_id: RUN-701", output)
            self.assertIn(f"- approval_request_path: {approval_path.as_posix()}", output)
            self.assertIn("- approval_request_exists: True", output)
            self.assertIn("- approval_request_status: pending", output)
            self.assertIn(f"- evidence_bundle_path: {evidence_path.as_posix()}", output)
            self.assertIn("- evidence_bundle_exists: True", output)
            self.assertIn("- run_state: approval_pending", output)
            self.assertIn("- readiness_summary: ready", output)
            self.assertIn("- degraded_note: none", output)

    def test_inspect_approval_by_run_id_successfully(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs" / "latest" / "RUN-702"
            artifacts = run_dir / "artifacts"
            artifacts.mkdir(parents=True, exist_ok=True)
            (run_dir / "run.yaml").write_text(
                "\n".join(
                    [
                        "run:",
                        "  run_id: RUN-702",
                        "  work_item_id: WI-702",
                        "  pr_id: PR-702",
                        "  state: approved",
                        "  created_at: '2026-03-29T07:02:00+00:00'",
                        "  updated_at: '2026-03-29T07:02:00+00:00'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            evidence_path = artifacts / "evidence-bundle.yaml"
            evidence_path.write_text("evidence_bundle:\n  run_id: RUN-702\n", encoding="utf-8")
            approval_path = artifacts / "approval-request.yaml"
            approval_path.write_text(
                "\n".join(
                    [
                        "approval_request:",
                        "  id: APR-RUN-702",
                        f"  evidence_bundle: {evidence_path.as_posix()}",
                        "  readiness_context:",
                        "    status: unavailable",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-approval", "--root", str(root), "--run-id", "RUN-702"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- run_id: RUN-702", output)
            self.assertIn("- run_state: approved", output)
            self.assertIn("- approval_request_exists: True", output)
            self.assertIn("- approval_request_status: none", output)
            self.assertIn("- readiness_summary: unavailable", output)
            self.assertIn("- degraded_note: none", output)

    def test_inspect_approval_degrades_safely_when_approval_request_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs" / "latest" / "RUN-703"
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "run.yaml").write_text(
                "\n".join(
                    [
                        "run:",
                        "  run_id: RUN-703",
                        "  work_item_id: WI-703",
                        "  pr_id: PR-703",
                        "  state: approval_pending",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-approval", "--root", str(root), "--run-id", "RUN-703"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- approval_request_exists: False", output)
            self.assertIn("- evidence_bundle_exists: False", output)
            self.assertIn("approval request artifact missing:", output)

    def test_inspect_approval_degrades_safely_when_evidence_bundle_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs" / "latest" / "RUN-704"
            artifacts = run_dir / "artifacts"
            artifacts.mkdir(parents=True, exist_ok=True)
            (run_dir / "run.yaml").write_text(
                "\n".join(
                    [
                        "run:",
                        "  run_id: RUN-704",
                        "  work_item_id: WI-704",
                        "  pr_id: PR-704",
                        "  state: approval_pending",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            approval_path = artifacts / "approval-request.yaml"
            missing_evidence = artifacts / "evidence-bundle.yaml"
            approval_path.write_text(
                "\n".join(
                    [
                        "approval_request:",
                        "  id: APR-RUN-704",
                        f"  evidence_bundle: {missing_evidence.as_posix()}",
                        "  readiness_context:",
                        "    readiness_summary: attention-needed",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-approval", "--root", str(root), "--run-id", "RUN-704"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- approval_request_exists: True", output)
            self.assertIn(f"- evidence_bundle_path: {missing_evidence.as_posix()}", output)
            self.assertIn("- evidence_bundle_exists: False", output)
            self.assertIn("- readiness_summary: attention-needed", output)
            self.assertIn("evidence bundle artifact missing:", output)

    def test_inspect_approval_latest_degrades_safely_when_no_latest_run_exists(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-approval", "--root", str(root), "--latest"])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                stdout.getvalue(),
                "\n".join(
                    [
                        "Approval Inspection:",
                        "- run_id: none",
                        "- run_path: none",
                        "- run_exists: False",
                        "- run_state: none",
                        "- approval_request_path: none",
                        "- approval_request_exists: False",
                        "- approval_request_status: none",
                        "- evidence_bundle_path: none",
                        "- evidence_bundle_exists: False",
                        "- readiness_summary: none",
                        "- degraded_note: no latest run found under runs/latest/*/run.yaml",
                    ]
                )
                + "\n",
            )

    def test_inspect_approval_degrades_safely_for_unreadable_or_partial_artifacts(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs" / "latest" / "RUN-705"
            artifacts = run_dir / "artifacts"
            artifacts.mkdir(parents=True, exist_ok=True)
            (run_dir / "run.yaml").write_text("run: [\n", encoding="utf-8")
            approval_path = artifacts / "approval-request.yaml"
            approval_path.write_text("approval_request:\n  id: APR-RUN-705\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-approval", "--root", str(root), "--run-id", "RUN-705"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- run_exists: True", output)
            self.assertIn("- run_state: none", output)
            self.assertIn("- approval_request_exists: True", output)
            self.assertIn("- evidence_bundle_exists: False", output)
            self.assertIn("run artifact unreadable:", output)
            self.assertIn("approval request missing evidence bundle path", output)
            self.assertIn("approval request missing readiness_context summary", output)

    def test_inspect_pr_plan_active_successfully(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = root / "prs" / "active" / "PR-750.md"
            plan_path.parent.mkdir(parents=True, exist_ok=True)
            plan_path.write_text(
                "\n".join(
                    [
                        "# PR-750: inspect active plan",
                        "",
                        "## PR ID",
                        "PR-750",
                        "",
                        "## Work Item ID",
                        "WI-750",
                        "",
                        "## Title",
                        "inspect active plan",
                        "",
                        "## Created At",
                        "2026-03-30T09:15:00+00:00",
                        "",
                        "## Work Item Readiness",
                        "- summary: attention-needed",
                        "- linked_clarification_count: 2",
                        "",
                        "## Linked Clarifications",
                        "- CLAR-101 (open)",
                        "- CLAR-102 (resolved)",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-pr-plan", "--root", str(root), "--active"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("PR Plan Inspection:", output)
            self.assertIn("- pr_id: PR-750", output)
            self.assertIn(f"- plan_path: {plan_path.as_posix()}", output)
            self.assertIn("- exists: True", output)
            self.assertIn("- active_relation: active", output)
            self.assertIn("- source_work_item_id: WI-750", output)
            self.assertIn("- metadata_timestamp: 2026-03-30T09:15:00+00:00", output)
            self.assertIn("- clarification_id: CLAR-101", output)
            self.assertIn("- clarification_id: CLAR-102", output)
            self.assertIn("- summary: attention-needed", output)
            self.assertIn("- linked_clarification_count: 2", output)
            self.assertIn("- context: summary = attention-needed", output)
            self.assertIn("- degraded_note: none", output)

    def test_inspect_pr_plan_by_pr_id_successfully(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = root / "prs" / "archive" / "PR-751.md"
            plan_path.parent.mkdir(parents=True, exist_ok=True)
            plan_path.write_text(
                "\n".join(
                    [
                        "# PR-751: inspect archived plan",
                        "",
                        "## PR ID",
                        "PR-751",
                        "",
                        "## Source Goal ID",
                        "GOAL-751",
                        "",
                        "## Work Item ID",
                        "WI-751",
                        "",
                        "## Work Item Readiness",
                        "- summary: ready",
                        "- linked_clarification_count: 0",
                        "",
                        "## Linked Clarifications",
                        "- none",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-pr-plan", "--root", str(root), "--pr-id", "PR-751"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- pr_id: PR-751", output)
            self.assertIn(f"- plan_path: {plan_path.as_posix()}", output)
            self.assertIn("- active_relation: archived", output)
            self.assertIn("- source_goal_id: GOAL-751", output)
            self.assertIn("- source_work_item_id: WI-751", output)
            self.assertIn("Linked Clarifications:\n- none", output)
            self.assertIn("- summary: ready", output)
            self.assertIn("- linked_clarification_count: 0", output)

    def test_inspect_pr_plan_active_degrades_safely_when_no_active_pr_exists(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-pr-plan", "--root", str(root), "--active"])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                stdout.getvalue(),
                "\n".join(
                    [
                        "PR Plan Inspection:",
                        "- pr_id: none",
                        "- plan_path: none",
                        "- exists: False",
                        "- active_relation: no-active-pr",
                        "- source_goal_id: none",
                        "- source_work_item_id: none",
                        "- metadata_timestamp: none",
                        "- degraded_note: no active PR plan found under prs/active/*.md",
                        "",
                        "Linked Clarifications:",
                        "- none",
                        "",
                        "Readiness Visibility:",
                        "- none",
                    ]
                )
                + "\n",
            )

    def test_inspect_pr_plan_degrades_safely_when_artifact_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-pr-plan", "--root", str(root), "--pr-id", "PR-752"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- pr_id: PR-752", output)
            self.assertIn("- exists: False", output)
            self.assertIn("- active_relation: not-found", output)
            self.assertIn("PR plan artifact missing for pr-id 'PR-752'", output)

    def test_inspect_pr_plan_degrades_safely_for_partial_or_unreadable_artifact(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            partial_plan = root / "prs" / "archive" / "PR-753.md"
            partial_plan.parent.mkdir(parents=True, exist_ok=True)
            partial_plan.write_text("# partial only\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-pr-plan", "--root", str(root), "--pr-id", "PR-753"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- exists: True", output)
            self.assertIn("- active_relation: archived", output)
            self.assertIn("PR plan artifact missing markdown sections", output)
            self.assertIn("PR plan artifact missing PR ID section", output)
            self.assertIn("PR plan artifact missing Work Item ID section", output)

    def test_inspect_pr_plan_shows_readiness_as_visibility_only(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            active_plan = root / "prs" / "active" / "PR-754.md"
            active_plan.parent.mkdir(parents=True, exist_ok=True)
            active_plan.write_text(
                "\n".join(
                    [
                        "# PR-754: visibility only",
                        "",
                        "## PR ID",
                        "PR-754",
                        "",
                        "## Work Item ID",
                        "WI-754",
                        "",
                        "## Work Item Readiness",
                        "- summary: no-linked-clarifications",
                        "- linked_clarification_count: 0",
                        "",
                        "## Linked Clarifications",
                        "- none",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            status_stdout = StringIO()
            with redirect_stdout(status_stdout):
                status_exit_code = main(["status", "--root", str(root)])

            inspect_stdout = StringIO()
            with redirect_stdout(inspect_stdout):
                inspect_exit_code = main(["inspect-pr-plan", "--root", str(root), "--active"])

            self.assertEqual(status_exit_code, 0)
            self.assertEqual(inspect_exit_code, 0)
            self.assertIn("- summary: no-linked-clarifications", inspect_stdout.getvalue())
            self.assertIn("Active PR:\n- pr_id: PR-754", status_stdout.getvalue())

    def test_inspect_work_item_successfully_by_id(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_item_path = root / "docs" / "work-items" / "WI-760.md"
            work_item_path.parent.mkdir(parents=True, exist_ok=True)
            work_item_path.write_text(
                "\n".join(
                    [
                        "# WI-760: inspect work item",
                        "",
                        "## Work Item ID",
                        "WI-760",
                        "",
                        "## Goal ID",
                        "GOAL-760",
                        "",
                        "## Title",
                        "inspect work item",
                        "",
                        "## Related Clarifications",
                        "- CLAR-201 (resolved)",
                        "- CLAR-202 (open)",
                        "",
                        "## Created At",
                        "2026-03-30T10:00:00+00:00",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (root / "clarifications" / "GOAL-760").mkdir(parents=True, exist_ok=True)
            (root / "clarifications" / "GOAL-760" / "CLAR-201.md").write_text(
                "# CLAR-201\n\n## Clarification ID\nCLAR-201\n\n## Status\nresolved\n",
                encoding="utf-8",
            )
            (root / "clarifications" / "GOAL-760" / "CLAR-202.md").write_text(
                "# CLAR-202\n\n## Clarification ID\nCLAR-202\n\n## Status\nopen\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-work-item", "--root", str(root), "--work-item-id", "WI-760"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Work Item Inspection:", output)
            self.assertIn("- work_item_id: WI-760", output)
            self.assertIn(f"- work_item_path: {work_item_path.as_posix()}", output)
            self.assertIn("- exists: True", output)
            self.assertIn("- title: inspect work item", output)
            self.assertIn("- goal_id: GOAL-760", output)
            self.assertIn("- metadata_timestamp: 2026-03-30T10:00:00+00:00", output)
            self.assertIn("- clarification_id: CLAR-201", output)
            self.assertIn("- clarification_id: CLAR-202", output)
            self.assertIn("- summary: attention-needed", output)
            self.assertIn("- linked_clarification_count: 2", output)
            self.assertIn("- degraded_note: none", output)

    def test_inspect_clarification_successfully_by_id(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            clarification_path = root / "clarifications" / "GOAL-770" / "CLAR-770.md"
            clarification_path.parent.mkdir(parents=True, exist_ok=True)
            clarification_path.write_text(
                "\n".join(
                    [
                        "# CLAR-770: inspect clarification",
                        "",
                        "## Clarification ID",
                        "CLAR-770",
                        "",
                        "## Goal ID",
                        "GOAL-770",
                        "",
                        "## Title",
                        "inspect clarification",
                        "",
                        "## Status",
                        "open",
                        "",
                        "## Question",
                        "What contract must remain visibility-only?",
                        "",
                        "## Summary",
                        "Operator wants direct clarification inspection.",
                        "",
                        "## Created At",
                        "2026-03-30T11:00:00+00:00",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (root / "docs" / "work-items").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "work-items" / "WI-770.md").write_text(
                "\n".join(
                    [
                        "# WI-770: linked clarification",
                        "",
                        "## Work Item ID",
                        "WI-770",
                        "",
                        "## Goal ID",
                        "GOAL-770",
                        "",
                        "## Related Clarifications",
                        "- CLAR-770 (open)",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-clarification", "--root", str(root), "--clarification-id", "CLAR-770"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Clarification Inspection:", output)
            self.assertIn("- clarification_id: CLAR-770", output)
            self.assertIn(f"- clarification_path: {clarification_path.as_posix()}", output)
            self.assertIn("- exists: True", output)
            self.assertIn("- title: inspect clarification", output)
            self.assertIn("- question: What contract must remain visibility-only?", output)
            self.assertIn("- summary: Operator wants direct clarification inspection.", output)
            self.assertIn("- status: open", output)
            self.assertIn("- goal_id: GOAL-770", output)
            self.assertIn("- metadata_timestamp: 2026-03-30T11:00:00+00:00", output)
            self.assertIn("- work_item_id: WI-770", output)
            self.assertIn("- degraded_note: none", output)

    def test_inspect_clarification_degrades_safely_when_artifact_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-clarification", "--root", str(root), "--clarification-id", "CLAR-771"])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                stdout.getvalue(),
                "\n".join(
                    [
                        "Clarification Inspection:",
                        "- clarification_id: CLAR-771",
                        f"- clarification_path: {(root / 'clarifications' / '*' / 'CLAR-771.md').as_posix()}",
                        "- exists: False",
                        "- title: none",
                        "- question: none",
                        "- summary: none",
                        "- status: none",
                        "- goal_id: none",
                        "- metadata_timestamp: none",
                        (
                            "- degraded_note: clarification artifact missing for clarification-id 'CLAR-771': "
                            f"expected {(root / 'clarifications' / '*' / 'CLAR-771.md').as_posix()}"
                        ),
                        "",
                        "Linked Work Items:",
                        "- none",
                    ]
                )
                + "\n",
            )

    def test_inspect_clarification_degrades_safely_for_partial_or_unreadable_artifact(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            clarification_path = root / "clarifications" / "GOAL-772" / "CLAR-772.md"
            clarification_path.parent.mkdir(parents=True, exist_ok=True)
            clarification_path.write_bytes(b"\xff\xfe")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-clarification", "--root", str(root), "--clarification-id", "CLAR-772"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- exists: True", output)
            self.assertIn(f"- clarification_path: {clarification_path.as_posix()}", output)
            self.assertIn("clarification artifact unreadable:", output)
            self.assertIn("- status: none", output)
            self.assertIn("Linked Work Items:\n- none", output)

    def test_inspect_clarification_shows_linked_references_only_as_visibility(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            clarification_path = root / "clarifications" / "GOAL-773" / "CLAR-773.md"
            clarification_path.parent.mkdir(parents=True, exist_ok=True)
            clarification_path.write_text(
                "\n".join(
                    [
                        "# CLAR-773: linked refs only",
                        "",
                        "## Clarification ID",
                        "CLAR-773",
                        "",
                        "## Goal ID",
                        "GOAL-773",
                        "",
                        "## Title",
                        "linked refs only",
                        "",
                        "## Status",
                        "resolved",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (root / "docs" / "work-items").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "work-items" / "WI-773A.md").write_text(
                "\n".join(
                    [
                        "# WI-773A",
                        "",
                        "## Work Item ID",
                        "WI-773A",
                        "",
                        "## Goal ID",
                        "GOAL-773",
                        "",
                        "## Related Clarifications",
                        "- CLAR-773 (resolved)",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            status_before = StringIO()
            with redirect_stdout(status_before):
                before_exit_code = main(["status", "--root", str(root)])

            inspect_stdout = StringIO()
            with redirect_stdout(inspect_stdout):
                inspect_exit_code = main(["inspect-clarification", "--root", str(root), "--clarification-id", "CLAR-773"])

            status_after = StringIO()
            with redirect_stdout(status_after):
                after_exit_code = main(["status", "--root", str(root)])

            self.assertEqual(before_exit_code, 0)
            self.assertEqual(inspect_exit_code, 0)
            self.assertEqual(after_exit_code, 0)
            self.assertIn("- goal_id: GOAL-773", inspect_stdout.getvalue())
            self.assertIn("- work_item_id: WI-773A", inspect_stdout.getvalue())
            self.assertEqual(status_before.getvalue(), status_after.getvalue())

    def test_inspect_clarification_shows_status_only_as_visibility(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            clarification_path = root / "clarifications" / "GOAL-774" / "CLAR-774.md"
            clarification_path.parent.mkdir(parents=True, exist_ok=True)
            clarification_path.write_text(
                "\n".join(
                    [
                        "# CLAR-774: visibility status",
                        "",
                        "## Clarification ID",
                        "CLAR-774",
                        "",
                        "## Goal ID",
                        "GOAL-774",
                        "",
                        "## Title",
                        "visibility status",
                        "",
                        "## Status",
                        "deferred",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            inspect_stdout = StringIO()
            with redirect_stdout(inspect_stdout):
                inspect_exit_code = main(["inspect-clarification", "--root", str(root), "--clarification-id", "CLAR-774"])

            queue_stdout = StringIO()
            with redirect_stdout(queue_stdout):
                queue_exit_code = main(["inspect-approval-queue", "--root", str(root)])

            self.assertEqual(inspect_exit_code, 0)
            self.assertEqual(queue_exit_code, 0)
            self.assertIn("- status: deferred", inspect_stdout.getvalue())
            self.assertEqual(
                queue_stdout.getvalue(),
                "Approval Queue Inspection:\n- latest_run_id: none\n- pending_total: 0\n\nPending Approvals:\n- none\n",
            )

    def test_inspect_goal_successfully_by_id(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            goal_path = root / "goals" / "GOAL-751.md"
            goal_path.parent.mkdir(parents=True, exist_ok=True)
            goal_path.write_text(
                "\n".join(
                    [
                        "# GOAL-751: inspect goal visibility",
                        "",
                        "## Goal ID",
                        "GOAL-751",
                        "",
                        "## Title",
                        "inspect goal visibility",
                        "",
                        "## Summary",
                        "Operator-facing goal inspection only.",
                        "",
                        "## Status",
                        "draft",
                        "",
                        "## Updated At",
                        "2026-03-31T10:00:00+00:00",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (root / "clarifications" / "GOAL-751").mkdir(parents=True, exist_ok=True)
            (root / "clarifications" / "GOAL-751" / "CLAR-751A.md").write_text(
                "# CLAR-751A\n\n## Clarification ID\nCLAR-751A\n\n## Goal ID\nGOAL-751\n",
                encoding="utf-8",
            )
            (root / "docs" / "work-items").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "work-items" / "WI-751A.md").write_text(
                "\n".join(
                    [
                        "# WI-751A",
                        "",
                        "## Work Item ID",
                        "WI-751A",
                        "",
                        "## Goal ID",
                        "GOAL-751",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-goal", "--root", str(root), "--goal-id", "GOAL-751"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Goal Inspection:", output)
            self.assertIn("- goal_id: GOAL-751", output)
            self.assertIn(f"- goal_path: {goal_path.as_posix()}", output)
            self.assertIn("- exists: True", output)
            self.assertIn("- title: inspect goal visibility", output)
            self.assertIn("- summary: Operator-facing goal inspection only.", output)
            self.assertIn("- status: draft", output)
            self.assertIn("- metadata_timestamp: 2026-03-31T10:00:00+00:00", output)
            self.assertIn("- clarification_id: CLAR-751A", output)
            self.assertIn("- work_item_id: WI-751A", output)

    def test_inspect_goal_degrades_safely_when_artifact_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-goal", "--root", str(root), "--goal-id", "GOAL-752"])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                stdout.getvalue(),
                "\n".join(
                    [
                        "Goal Inspection:",
                        "- goal_id: GOAL-752",
                        f"- goal_path: {(root / 'goals' / 'GOAL-752.md').as_posix()}",
                        "- exists: False",
                        "- title: none",
                        "- summary: none",
                        "- status: none",
                        "- metadata_timestamp: none",
                        f"- degraded_note: goal artifact missing: {(root / 'goals' / 'GOAL-752.md').as_posix()}",
                        "",
                        "Linked Clarifications:",
                        "- none",
                        "",
                        "Linked Work Items:",
                        "- none",
                    ]
                )
                + "\n",
            )

    def test_inspect_goal_degrades_safely_for_partial_or_unreadable_artifact(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            goal_path = root / "goals" / "GOAL-753.md"
            goal_path.parent.mkdir(parents=True, exist_ok=True)
            goal_path.write_text("# partial only\n", encoding="utf-8")
            (root / "clarifications" / "GOAL-753").mkdir(parents=True, exist_ok=True)
            (root / "clarifications" / "GOAL-753" / "CLAR-753A.md").write_text("# CLAR-753A\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-goal", "--root", str(root), "--goal-id", "GOAL-753"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- exists: True", output)
            self.assertIn("goal artifact missing markdown sections", output)
            self.assertIn("goal artifact missing Goal ID section", output)
            self.assertIn("- clarification_id: CLAR-753A", output)

    def test_inspect_goal_shows_linked_refs_only_as_visibility(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            goal_path = root / "goals" / "GOAL-754.md"
            goal_path.parent.mkdir(parents=True, exist_ok=True)
            goal_path.write_text(
                "\n".join(
                    [
                        "# GOAL-754: linked refs visibility",
                        "",
                        "## Goal ID",
                        "GOAL-754",
                        "",
                        "## Title",
                        "linked refs visibility",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (root / "clarifications" / "GOAL-754").mkdir(parents=True, exist_ok=True)
            (root / "clarifications" / "GOAL-754" / "CLAR-754A.md").write_text(
                "# CLAR-754A\n\n## Clarification ID\nCLAR-754A\n\n## Goal ID\nGOAL-754\n",
                encoding="utf-8",
            )
            (root / "docs" / "work-items").mkdir(parents=True, exist_ok=True)
            (root / "docs" / "work-items" / "WI-754A.md").write_text(
                "\n".join(
                    [
                        "# WI-754A",
                        "",
                        "## Work Item ID",
                        "WI-754A",
                        "",
                        "## Goal ID",
                        "GOAL-754",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            status_stdout = StringIO()
            with redirect_stdout(status_stdout):
                status_exit_code = main(["status", "--root", str(root)])

            inspect_stdout = StringIO()
            with redirect_stdout(inspect_stdout):
                inspect_exit_code = main(["inspect-goal", "--root", str(root), "--goal-id", "GOAL-754"])

            self.assertEqual(status_exit_code, 0)
            self.assertEqual(inspect_exit_code, 0)
            output = inspect_stdout.getvalue()
            self.assertIn("- clarification_id: CLAR-754A", output)
            self.assertIn("- work_item_id: WI-754A", output)
            self.assertNotIn("auto-resolve", output)
            self.assertIn("Latest Run:\n- none", status_stdout.getvalue())

    def test_inspect_goal_shows_status_only_as_visibility(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            goal_path = root / "goals" / "GOAL-755.md"
            goal_path.parent.mkdir(parents=True, exist_ok=True)
            goal_path.write_text(
                "\n".join(
                    [
                        "# GOAL-755: visibility status",
                        "",
                        "## Goal ID",
                        "GOAL-755",
                        "",
                        "## Title",
                        "visibility status",
                        "",
                        "## Status",
                        "in_review",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            inspect_stdout = StringIO()
            with redirect_stdout(inspect_stdout):
                inspect_exit_code = main(["inspect-goal", "--root", str(root), "--goal-id", "GOAL-755"])

            queue_stdout = StringIO()
            with redirect_stdout(queue_stdout):
                queue_exit_code = main(["inspect-approval-queue", "--root", str(root)])

            self.assertEqual(inspect_exit_code, 0)
            self.assertEqual(queue_exit_code, 0)
            self.assertIn("- status: in_review", inspect_stdout.getvalue())
            self.assertEqual(
                queue_stdout.getvalue(),
                "Approval Queue Inspection:\n- latest_run_id: none\n- pending_total: 0\n\nPending Approvals:\n- none\n",
            )

    def test_inspect_goal_keeps_existing_visibility_commands_unchanged(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs" / "latest" / "RUN-756"
            artifacts = run_dir / "artifacts"
            artifacts.mkdir(parents=True, exist_ok=True)
            (run_dir / "run.yaml").write_text(
                "\n".join(
                    [
                        "run:",
                        "  run_id: RUN-756",
                        "  pr_id: PR-756",
                        "  work_item_id: WI-756",
                        "  state: approval_pending",
                        "  updated_at: 2026-03-31T12:00:00+00:00",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (artifacts / "approval-request.yaml").write_text("approval_request:\n  status: pending\n", encoding="utf-8")
            (artifacts / "evidence-bundle.yaml").write_text("evidence_bundle:\n  status: complete\n", encoding="utf-8")
            (root / "goals").mkdir(parents=True, exist_ok=True)
            (root / "goals" / "GOAL-756.md").write_text("# GOAL-756\n\n## Goal ID\nGOAL-756\n", encoding="utf-8")

            status_before = StringIO()
            with redirect_stdout(status_before):
                self.assertEqual(main(["status", "--root", str(root)]), 0)

            run_before = StringIO()
            with redirect_stdout(run_before):
                self.assertEqual(main(["inspect-run", "--root", str(root), "--run-id", "RUN-756"]), 0)

            with redirect_stdout(StringIO()):
                self.assertEqual(main(["inspect-goal", "--root", str(root), "--goal-id", "GOAL-756"]), 0)

            status_after = StringIO()
            with redirect_stdout(status_after):
                self.assertEqual(main(["status", "--root", str(root)]), 0)

            run_after = StringIO()
            with redirect_stdout(run_after):
                self.assertEqual(main(["inspect-run", "--root", str(root), "--run-id", "RUN-756"]), 0)

            self.assertEqual(status_before.getvalue(), status_after.getvalue())
            self.assertEqual(run_before.getvalue(), run_after.getvalue())

    def test_inspect_work_item_degrades_safely_when_artifact_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-work-item", "--root", str(root), "--work-item-id", "WI-761"])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                stdout.getvalue(),
                "\n".join(
                    [
                        "Work Item Inspection:",
                        "- work_item_id: WI-761",
                        f"- work_item_path: {(root / 'docs' / 'work-items' / 'WI-761.md').as_posix()}",
                        "- exists: False",
                        "- title: none",
                        "- summary: none",
                        "- goal_id: none",
                        "- metadata_timestamp: none",
                        f"- degraded_note: work item artifact missing: {(root / 'docs' / 'work-items' / 'WI-761.md').as_posix()}",
                        "",
                        "Linked Clarifications:",
                        "- none",
                        "",
                        "Readiness Visibility:",
                        "- none",
                    ]
                )
                + "\n",
            )

    def test_inspect_work_item_degrades_safely_for_partial_or_unreadable_artifact(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_item_path = root / "docs" / "work-items" / "WI-762.md"
            work_item_path.parent.mkdir(parents=True, exist_ok=True)
            work_item_path.write_text("# partial only\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-work-item", "--root", str(root), "--work-item-id", "WI-762"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- exists: True", output)
            self.assertIn("work item artifact missing markdown sections", output)
            self.assertIn("work item artifact missing Work Item ID section", output)
            self.assertIn("work item artifact missing Goal ID section", output)
            self.assertIn("cannot read work item readiness because the work item is missing a Goal ID section value", output)

    def test_inspect_work_item_shows_linked_clarifications_only_as_visibility(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_item_path = root / "docs" / "work-items" / "WI-763.md"
            work_item_path.parent.mkdir(parents=True, exist_ok=True)
            work_item_path.write_text(
                "\n".join(
                    [
                        "# WI-763: visibility only clarifications",
                        "",
                        "## Work Item ID",
                        "WI-763",
                        "",
                        "## Goal ID",
                        "GOAL-763",
                        "",
                        "## Title",
                        "visibility only clarifications",
                        "",
                        "## Related Clarifications",
                        "- CLAR-301 (open)",
                        "- CLAR-302 (deferred)",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (root / "clarifications" / "GOAL-763").mkdir(parents=True, exist_ok=True)
            (root / "clarifications" / "GOAL-763" / "CLAR-301.md").write_text(
                "# CLAR-301\n\n## Clarification ID\nCLAR-301\n\n## Status\nopen\n",
                encoding="utf-8",
            )
            (root / "clarifications" / "GOAL-763" / "CLAR-302.md").write_text(
                "# CLAR-302\n\n## Clarification ID\nCLAR-302\n\n## Status\ndeferred\n",
                encoding="utf-8",
            )

            status_stdout = StringIO()
            with redirect_stdout(status_stdout):
                status_exit_code = main(["status", "--root", str(root)])

            inspect_stdout = StringIO()
            with redirect_stdout(inspect_stdout):
                inspect_exit_code = main(["inspect-work-item", "--root", str(root), "--work-item-id", "WI-763"])

            self.assertEqual(status_exit_code, 0)
            self.assertEqual(inspect_exit_code, 0)
            output = inspect_stdout.getvalue()
            self.assertIn("- clarification_id: CLAR-301", output)
            self.assertIn("- clarification_id: CLAR-302", output)
            self.assertNotIn("auto-resolve", output)
            self.assertIn("Active PR:\n- none", status_stdout.getvalue())

    def test_inspect_work_item_shows_readiness_only_as_visibility(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            work_item_path = root / "docs" / "work-items" / "WI-764.md"
            work_item_path.parent.mkdir(parents=True, exist_ok=True)
            work_item_path.write_text(
                "\n".join(
                    [
                        "# WI-764: readiness visibility only",
                        "",
                        "## Work Item ID",
                        "WI-764",
                        "",
                        "## Goal ID",
                        "GOAL-764",
                        "",
                        "## Title",
                        "readiness visibility only",
                        "",
                        "## Related Clarifications",
                        "- none",
                        "",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            inspect_stdout = StringIO()
            with redirect_stdout(inspect_stdout):
                inspect_exit_code = main(["inspect-work-item", "--root", str(root), "--work-item-id", "WI-764"])

            status_stdout = StringIO()
            with redirect_stdout(status_stdout):
                status_exit_code = main(["status", "--root", str(root)])

            self.assertEqual(inspect_exit_code, 0)
            self.assertEqual(status_exit_code, 0)
            self.assertIn("- summary: no-linked-clarifications", inspect_stdout.getvalue())
            self.assertIn("- linked_clarification_count: 0", inspect_stdout.getvalue())
            self.assertIn("Latest Run:\n- none", status_stdout.getvalue())

    def test_inspect_run_latest_successfully(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            active_pr = root / "prs" / "active" / "PR-801.md"
            active_pr.parent.mkdir(parents=True, exist_ok=True)
            active_pr.write_text(
                "# PR-801\n\n## PR ID\nPR-801\n\n## Work Item ID\nWI-801\n\n## Title\ninspect run\n",
                encoding="utf-8",
            )
            run_dir = root / "runs" / "latest" / "RUN-801"
            artifacts = run_dir / "artifacts"
            artifacts.mkdir(parents=True, exist_ok=True)
            (run_dir / "run.yaml").write_text(
                "\n".join(
                    [
                        "run:",
                        "  run_id: RUN-801",
                        "  work_item_id: WI-801",
                        "  pr_id: PR-801",
                        "  state: approval_pending",
                        "  created_at: '2026-03-29T08:01:00+00:00'",
                        "  updated_at: '2026-03-29T08:05:00+00:00'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (artifacts / "review-report.yaml").write_text("review_report:\n  status: pass\n", encoding="utf-8")
            (artifacts / "qa-report.yaml").write_text("qa_report:\n  status: pass\n", encoding="utf-8")
            (artifacts / "docs-sync-report.yaml").write_text("docs_sync_report:\n  status: complete\n", encoding="utf-8")
            (artifacts / "verification-report.yaml").write_text(
                "\n".join(
                    [
                        "verification_report:",
                        "  lint: pass",
                        "  tests: pass",
                        "  type_check: pass",
                        "  build: pass",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (artifacts / "gate-status.yaml").write_text("gate_status:\n  current_state: approval_pending\n", encoding="utf-8")
            (artifacts / "approval-request.yaml").write_text("approval_request:\n  id: APR-RUN-801\n", encoding="utf-8")
            (artifacts / "evidence-bundle.yaml").write_text("evidence_bundle:\n  status: complete\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-run", "--root", str(root), "--latest"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Run Inspection:", output)
            self.assertIn("- run_id: RUN-801", output)
            self.assertIn("- run_exists: True", output)
            self.assertIn("- run_state: approval_pending", output)
            self.assertIn("- latest_relation: latest", output)
            self.assertIn("- active_pr_relation: linked-by-pr", output)
            self.assertIn("- degraded_note: none", output)
            self.assertIn("- artifact: review", output)
            self.assertIn("  status: pass", output)
            self.assertIn("- artifact: verification", output)
            self.assertIn("  status: lint=pass,tests=pass,type_check=pass,build=pass", output)

    def test_inspect_run_by_run_id_successfully(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            latest_run_dir = root / "runs" / "latest" / "RUN-810"
            latest_run_dir.mkdir(parents=True, exist_ok=True)
            (latest_run_dir / "run.yaml").write_text(
                "\n".join(
                    [
                        "run:",
                        "  run_id: RUN-810",
                        "  work_item_id: WI-810",
                        "  pr_id: PR-810",
                        "  state: approved",
                        "  created_at: '2026-03-29T08:10:00+00:00'",
                        "  updated_at: '2026-03-29T08:10:00+00:00'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            run_dir = root / "runs" / "latest" / "RUN-802"
            artifacts = run_dir / "artifacts"
            artifacts.mkdir(parents=True, exist_ok=True)
            (run_dir / "run.yaml").write_text(
                "\n".join(
                    [
                        "run:",
                        "  run_id: RUN-802",
                        "  work_item_id: WI-802",
                        "  pr_id: PR-802",
                        "  state: in_progress",
                        "  created_at: '2026-03-29T08:02:00+00:00'",
                        "  updated_at: '2026-03-29T08:02:00+00:00'",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (artifacts / "review-report.yaml").write_text("review_report:\n  status: pending\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-run", "--root", str(root), "--run-id", "RUN-802"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- run_id: RUN-802", output)
            self.assertIn("- run_state: in_progress", output)
            self.assertIn("- latest_relation: non-latest", output)
            self.assertIn("- artifact: review", output)
            self.assertIn("  status: pending", output)

    def test_inspect_run_degrades_safely_when_run_artifact_is_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            stdout = StringIO()

            with redirect_stdout(stdout):
                exit_code = main(["inspect-run", "--root", str(root), "--run-id", "RUN-803"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- run_id: RUN-803", output)
            self.assertIn("- run_exists: False", output)
            self.assertIn("- run_state: none", output)
            self.assertIn("run artifact missing:", output)

    def test_inspect_run_degrades_safely_when_run_related_artifacts_are_missing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs" / "latest" / "RUN-804"
            run_dir.mkdir(parents=True, exist_ok=True)
            (run_dir / "run.yaml").write_text(
                "\n".join(
                    [
                        "run:",
                        "  run_id: RUN-804",
                        "  work_item_id: WI-804",
                        "  pr_id: PR-804",
                        "  state: in_progress",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-run", "--root", str(root), "--run-id", "RUN-804"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- artifact: review", output)
            self.assertIn("review artifact missing:", output)
            self.assertIn("qa artifact missing:", output)
            self.assertIn("docs-sync artifact missing:", output)
            self.assertIn("verification artifact missing:", output)
            self.assertIn("gate-check artifact missing:", output)
            self.assertIn("approval-request artifact missing:", output)
            self.assertIn("evidence-bundle artifact missing:", output)

    def test_inspect_run_latest_degrades_safely_when_no_latest_run_exists(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-run", "--root", str(root), "--latest"])

            self.assertEqual(exit_code, 0)
            self.assertEqual(
                stdout.getvalue(),
                "\n".join(
                    [
                        "Run Inspection:",
                        "- run_id: none",
                        "- run_path: none",
                        "- run_exists: False",
                        "- run_state: none",
                        "- latest_relation: no-latest-run",
                        "- active_pr_relation: no-active-pr",
                        "- degraded_note: no latest run found under runs/latest/*/run.yaml",
                        "",
                        "Artifacts:",
                        "- none",
                    ]
                )
                + "\n",
            )

    def test_inspect_run_degrades_safely_for_unreadable_or_partial_artifacts(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs" / "latest" / "RUN-805"
            artifacts = run_dir / "artifacts"
            artifacts.mkdir(parents=True, exist_ok=True)
            (run_dir / "run.yaml").write_text("run: [\n", encoding="utf-8")
            (artifacts / "review-report.yaml").write_text("review_report:\n  pr_id: PR-805\n", encoding="utf-8")
            (artifacts / "verification-report.yaml").write_text(
                "\n".join(
                    [
                        "verification_report:",
                        "  lint: weird",
                        "  tests: pass",
                        "  type_check: pass",
                        "  build: pass",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            (artifacts / "qa-report.yaml").write_text("qa_report: []\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["inspect-run", "--root", str(root), "--run-id", "RUN-805"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("- run_exists: True", output)
            self.assertIn("- run_state: none", output)
            self.assertIn("run artifact unreadable:", output)
            self.assertIn("review artifact missing review status", output)
            self.assertIn("qa artifact missing qa_report mapping", output)
            self.assertIn("verification artifact invalid:", output)

    def test_trace_lineage_latest_run_successfully(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_trace_run(root, run_id="RUN-899", pr_id="PR-899", work_item_id="WI-899", updated_at="2026-03-29T08:59:00+00:00")
            self._write_trace_run(root, run_id="RUN-900", pr_id="PR-900", work_item_id="WI-900", updated_at="2026-03-29T09:00:00+00:00")
            self._write_trace_pr_plan(root, pr_id="PR-900", work_item_id="WI-900", clarification_ids=["CLAR-900A", "CLAR-900B"])
            self._write_trace_work_item(root, work_item_id="WI-900", goal_id="GOAL-900", clarification_ids=["CLAR-900A", "CLAR-900B"])
            self._write_trace_goal(root, goal_id="GOAL-900")
            self._write_trace_clarification(root, goal_id="GOAL-900", clarification_id="CLAR-900A", status="resolved")
            self._write_trace_clarification(root, goal_id="GOAL-900", clarification_id="CLAR-900B", status="open")
            self._write_trace_approval(root, run_id="RUN-900", status="pending", queue_status="pending")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["trace-lineage", "--root", str(root), "--latest-run"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Lineage Trace:", output)
            self.assertIn("Run:\n- run_id: RUN-900", output)
            self.assertIn("Approval:\n- approval_request_path:", output)
            self.assertIn("- approval_request_status: pending", output)
            self.assertIn("- queue_status: pending", output)
            self.assertIn("PR Plan:\n- pr_id: PR-900", output)
            self.assertIn("- active_relation: active", output)
            self.assertIn("Work Item:\n- work_item_id: WI-900", output)
            self.assertIn("- readiness_visibility: attention-needed", output)
            self.assertIn("Goal:\n- goal_id: GOAL-900", output)
            self.assertIn("Clarifications:\n- clarification_id: CLAR-900A\n- clarification_id: CLAR-900B", output)
            self.assertIn("Degraded Notes:\n- none", output)

    def test_trace_lineage_by_run_id_successfully(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_trace_run(root, run_id="RUN-901", pr_id="PR-901", work_item_id="WI-901", updated_at="2026-03-29T09:01:00+00:00")
            self._write_trace_pr_plan(root, pr_id="PR-901", work_item_id="WI-901", archived=True)
            self._write_trace_work_item(root, work_item_id="WI-901", goal_id="GOAL-901")
            self._write_trace_goal(root, goal_id="GOAL-901")
            self._write_trace_approval(root, run_id="RUN-901", status="approved", queue_status="approved")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["trace-lineage", "--root", str(root), "--run-id", "RUN-901"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Run:\n- run_id: RUN-901", output)
            self.assertIn("- approval_request_status: approved", output)
            self.assertIn("- queue_status: approved", output)
            self.assertIn("- pr_id: PR-901", output)
            self.assertIn("- active_relation: archived", output)
            self.assertIn("- work_item_id: WI-901", output)
            self.assertIn("- goal_id: GOAL-901", output)

    def test_trace_lineage_missing_pr_plan_link_degrades_safely(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_trace_run(root, run_id="RUN-902", pr_id="PR-902", work_item_id="WI-902", updated_at="2026-03-29T09:02:00+00:00")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["trace-lineage", "--root", str(root), "--run-id", "RUN-902"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("PR Plan:\n- pr_id: PR-902", output)
            self.assertIn("- plan_path: none", output)
            self.assertIn("PR plan artifact missing for pr-id 'PR-902'", output)

    def test_trace_lineage_missing_work_item_link_degrades_safely(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_trace_run(root, run_id="RUN-903", pr_id="PR-903", work_item_id=None, updated_at="2026-03-29T09:03:00+00:00")
            self._write_trace_pr_plan(root, pr_id="PR-903", work_item_id=None)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["trace-lineage", "--root", str(root), "--run-id", "RUN-903"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Work Item:\n- work_item_id: none", output)
            self.assertIn("PR plan artifact missing Work Item ID section", output)
            self.assertIn("work item linkage unavailable because no source work_item_id was derivable", output)

    def test_trace_lineage_missing_goal_link_degrades_safely(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_trace_run(root, run_id="RUN-904", pr_id="PR-904", work_item_id="WI-904", updated_at="2026-03-29T09:04:00+00:00")
            self._write_trace_pr_plan(root, pr_id="PR-904", work_item_id="WI-904")
            self._write_trace_work_item(root, work_item_id="WI-904", goal_id=None)

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["trace-lineage", "--root", str(root), "--run-id", "RUN-904"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Goal:\n- goal_id: none\n- goal_path: none", output)
            self.assertIn("work item artifact missing Goal ID section", output)
            self.assertIn("goal linkage unavailable because work item artifact did not yield goal_id", output)

    def test_trace_lineage_missing_clarification_linkage_degrades_safely(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_trace_run(root, run_id="RUN-905", pr_id="PR-905", work_item_id="WI-905", updated_at="2026-03-29T09:05:00+00:00")
            self._write_trace_pr_plan(root, pr_id="PR-905", work_item_id="WI-905")
            self._write_trace_work_item(root, work_item_id="WI-905", goal_id="GOAL-905")
            self._write_trace_goal(root, goal_id="GOAL-905")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["trace-lineage", "--root", str(root), "--run-id", "RUN-905"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Clarifications:\n- none", output)
            self.assertIn("no linked clarification ids were derivable from the available artifacts", output)

    def test_trace_lineage_missing_approval_artifact_degrades_safely(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_trace_run(root, run_id="RUN-906", pr_id="PR-906", work_item_id="WI-906", updated_at="2026-03-29T09:06:00+00:00")
            self._write_trace_pr_plan(root, pr_id="PR-906", work_item_id="WI-906")
            self._write_trace_work_item(root, work_item_id="WI-906", goal_id="GOAL-906")
            self._write_trace_goal(root, goal_id="GOAL-906")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["trace-lineage", "--root", str(root), "--run-id", "RUN-906"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Approval:\n- approval_request_path:", output)
            self.assertIn("- approval_request_status: none", output)
            self.assertIn("- queue_path: none", output)
            self.assertIn("- queue_status: none", output)
            self.assertIn("approval request artifact missing:", output)

    def test_trace_lineage_old_format_artifacts_degrade_safely(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "runs" / "latest" / "RUN-907"
            artifacts = run_dir / "artifacts"
            artifacts.mkdir(parents=True, exist_ok=True)
            (run_dir / "run.yaml").write_text("run: [\n", encoding="utf-8")
            approval_path = artifacts / "approval-request.yaml"
            approval_path.write_text("approval_request:\n  id: APR-RUN-907\n", encoding="utf-8")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["trace-lineage", "--root", str(root), "--run-id", "RUN-907"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Run:\n- run_id: RUN-907", output)
            self.assertIn("- run_state: none", output)
            self.assertIn("run artifact unreadable:", output)
            self.assertIn("run artifact missing pr_id linkage", output)
            self.assertIn("PR plan linkage unavailable because run artifact did not yield pr_id", output)

    def test_trace_lineage_keeps_existing_status_and_inspect_run_behavior_unchanged(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_trace_run(root, run_id="RUN-908", pr_id="PR-908", work_item_id="WI-908", updated_at="2026-03-29T09:08:00+00:00")
            self._write_trace_pr_plan(root, pr_id="PR-908", work_item_id="WI-908")
            self._write_trace_work_item(root, work_item_id="WI-908", goal_id="GOAL-908")
            self._write_trace_goal(root, goal_id="GOAL-908")
            self._write_trace_approval(root, run_id="RUN-908", status="pending", queue_status="pending")

            status_before = StringIO()
            with redirect_stdout(status_before):
                self.assertEqual(main(["status", "--root", str(root)]), 0)

            inspect_before = StringIO()
            with redirect_stdout(inspect_before):
                self.assertEqual(main(["inspect-run", "--root", str(root), "--run-id", "RUN-908"]), 0)

            trace_stdout = StringIO()
            with redirect_stdout(trace_stdout):
                self.assertEqual(main(["trace-lineage", "--root", str(root), "--run-id", "RUN-908"]), 0)

            status_after = StringIO()
            with redirect_stdout(status_after):
                self.assertEqual(main(["status", "--root", str(root)]), 0)

            inspect_after = StringIO()
            with redirect_stdout(inspect_after):
                self.assertEqual(main(["inspect-run", "--root", str(root), "--run-id", "RUN-908"]), 0)

            self.assertEqual(status_before.getvalue(), status_after.getvalue())
            self.assertEqual(inspect_before.getvalue(), inspect_after.getvalue())

    def _write_trace_run(
        self,
        root,
        *,
        run_id: str,
        pr_id: str | None,
        work_item_id: str | None,
        updated_at: str,
        state: str = "approval_pending",
    ) -> None:
        run_dir = root / "runs" / "latest" / run_id
        (run_dir / "artifacts").mkdir(parents=True, exist_ok=True)
        lines = [
            "run:",
            f"  run_id: {run_id}",
            f"  state: {state}",
            "  created_at: '2026-03-29T00:00:00+00:00'",
            f"  updated_at: '{updated_at}'",
        ]
        if work_item_id is not None:
            lines.insert(2, f"  work_item_id: {work_item_id}")
        if pr_id is not None:
            lines.insert(2, f"  pr_id: {pr_id}")
        (run_dir / "run.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_trace_pr_plan(
        self,
        root,
        *,
        pr_id: str,
        work_item_id: str | None,
        archived: bool = False,
        clarification_ids: list[str] | None = None,
    ) -> None:
        plan_path = root / "prs" / ("archive" if archived else "active") / f"{pr_id}.md"
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            f"# {pr_id}: trace lineage",
            "",
            "## PR ID",
            pr_id,
            "",
        ]
        if work_item_id is not None:
            lines.extend(
                [
                    "## Work Item ID",
                    work_item_id,
                    "",
                ]
            )
        lines.extend(
            [
                "## Work Item Readiness",
                "- summary: attention-needed" if work_item_id else "- summary: unavailable",
                f"- linked_clarification_count: {len(clarification_ids or [])}" if work_item_id else "- linked_clarification_count: none",
                "",
                "## Linked Clarifications",
            ]
        )
        if clarification_ids:
            for clarification_id in clarification_ids:
                status = "resolved" if clarification_id.endswith("A") else "open"
                lines.append(f"- {clarification_id} ({status})")
        else:
            lines.append("- none")
        lines.append("")
        plan_path.write_text("\n".join(lines), encoding="utf-8")

    def _write_trace_work_item(
        self,
        root,
        *,
        work_item_id: str,
        goal_id: str | None,
        clarification_ids: list[str] | None = None,
    ) -> None:
        work_item_path = root / "docs" / "work-items" / f"{work_item_id}.md"
        work_item_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            f"# {work_item_id}: trace lineage",
            "",
            "## Work Item ID",
            work_item_id,
            "",
        ]
        if goal_id is not None:
            lines.extend(["## Goal ID", goal_id, ""])
        lines.extend(["## Title", "trace lineage", "", "## Related Clarifications"])
        if clarification_ids:
            for clarification_id in clarification_ids:
                status = "resolved" if clarification_id.endswith("A") else "open"
                lines.append(f"- {clarification_id} ({status})")
        else:
            lines.append("- none")
        lines.append("")
        work_item_path.write_text("\n".join(lines), encoding="utf-8")

    def _write_trace_goal(self, root, *, goal_id: str) -> None:
        goal_path = root / "goals" / f"{goal_id}.md"
        goal_path.parent.mkdir(parents=True, exist_ok=True)
        goal_path.write_text(f"# {goal_id}: trace lineage\n", encoding="utf-8")

    def _write_trace_clarification(self, root, *, goal_id: str, clarification_id: str, status: str) -> None:
        clarification_path = root / "clarifications" / goal_id / f"{clarification_id}.md"
        clarification_path.parent.mkdir(parents=True, exist_ok=True)
        clarification_path.write_text(
            "\n".join(
                [
                    f"# {clarification_id}: trace lineage",
                    "",
                    "## Clarification ID",
                    clarification_id,
                    "",
                    "## Goal ID",
                    goal_id,
                    "",
                    "## Status",
                    status,
                    "",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    def _write_trace_approval(self, root, *, run_id: str, status: str, queue_status: str) -> None:
        artifacts = root / "runs" / "latest" / run_id / "artifacts"
        artifacts.mkdir(parents=True, exist_ok=True)
        evidence_path = artifacts / "evidence-bundle.yaml"
        evidence_path.write_text("evidence_bundle:\n  status: complete\n", encoding="utf-8")
        (artifacts / "approval-request.yaml").write_text(
            "\n".join(
                [
                    "approval_request:",
                    f"  id: APR-{run_id}",
                    f"  status: {status}",
                    f"  evidence_bundle: {evidence_path.as_posix()}",
                    "  readiness_context:",
                    "    status: available",
                    "    readiness_summary: ready" if status == "approved" else "    readiness_summary: attention-needed",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        queue_dir = root / "approval_queue" / queue_status
        queue_dir.mkdir(parents=True, exist_ok=True)
        (queue_dir / f"APR-{run_id}.yaml").write_text("approval_request:\n  id: placeholder\n", encoding="utf-8")

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
                        "",
                        "Approval Queue:",
                        "- pending_total: 0",
                        "- latest_run_has_pending: unavailable",
                        "- stale_pending_count: 0",
                        "- stale_pending_run_ids: none",
                        "- stale_pending_path: none",
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
            _write_minimal_work_item(root, work_item_id="WI-010", goal_id="GOAL-010")

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
            _write_minimal_work_item(root, work_item_id="WI-010", goal_id="GOAL-010")
            _write_minimal_work_item(root, work_item_id="WI-011", goal_id="GOAL-011")

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
            _write_minimal_work_item(root, work_item_id="WI-010", goal_id="GOAL-010")
            _write_minimal_work_item(root, work_item_id="WI-011", goal_id="GOAL-011")
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


class BuildApprovalCliReadinessTest(unittest.TestCase):
    def _prepare_root(self, root) -> None:
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[1]
        (root / "config").mkdir(parents=True, exist_ok=True)
        (root / "approval_queue" / "pending").mkdir(parents=True, exist_ok=True)
        (root / "config" / "gates.yaml").write_text(
            (repo_root / "config" / "gates.yaml").read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    def _write_work_item(self, root, *, work_item_id: str, goal_id: str, related_lines: list[str] | None = None) -> None:
        (root / "docs" / "work-items").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "work-items" / f"{work_item_id}.md").write_text(
            "\n".join(
                [
                    f"# {work_item_id}: build approval readiness",
                    "",
                    "## Work Item ID",
                    work_item_id,
                    "",
                    "## Goal ID",
                    goal_id,
                    "",
                    "## Title",
                    "build approval readiness",
                    "",
                    "## Status",
                    "draft",
                    "",
                    "## Description",
                    "Source work item for approval output tests.",
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

    def _write_clarification(self, root, *, goal_id: str, clarification_id: str, status: str) -> None:
        (root / "clarifications" / goal_id).mkdir(parents=True, exist_ok=True)
        (root / "clarifications" / goal_id / f"{clarification_id}.md").write_text(
            "\n".join(
                [
                    f"# {clarification_id}",
                    "",
                    "## Clarification ID",
                    clarification_id,
                    "",
                    "## Goal ID",
                    goal_id,
                    "",
                    "## Status",
                    status,
                    "",
                ]
            ),
            encoding="utf-8",
        )

    def _bootstrap(self, root, run_id: str) -> None:
        self.assertEqual(
            main(
                [
                    "bootstrap-run",
                    "--root",
                    str(root),
                    "--run-id",
                    run_id,
                    "--pr-id",
                    "PR-READINESS",
                    "--work-item-id",
                    "WI-READINESS",
                    "--work-item-title",
                    "build approval readiness",
                ]
            ),
            0,
        )

    def _record_ready_artifacts(self, root, run_id: str) -> None:
        self.assertEqual(
            main(
                [
                    "record-verification",
                    "--root",
                    str(root),
                    "--run-id",
                    run_id,
                    "--lint",
                    "pass",
                    "--tests",
                    "pass",
                    "--type-check",
                    "pass",
                    "--build",
                    "pass",
                    "--summary",
                    "all green",
                ]
            ),
            0,
        )
        self.assertEqual(main(["record-review", "--root", str(root), "--run-id", run_id, "--status", "pass", "--summary", "review ok"]), 0)
        self.assertEqual(main(["record-qa", "--root", str(root), "--run-id", run_id, "--status", "pass", "--summary", "qa ok"]), 0)
        self.assertEqual(
            main(["record-docs-sync", "--root", str(root), "--run-id", run_id, "--status", "complete", "--summary", "docs ok"]),
            0,
        )

    def test_build_approval_output_includes_readiness_summary_and_count(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prepare_root(root)
            self._bootstrap(root, "RUN-CLI-READY")
            self._write_work_item(
                root,
                work_item_id="WI-READINESS",
                goal_id="GOAL-READINESS",
                related_lines=["- CLAR-001 (open)", "- CLAR-002 (resolved)"],
            )
            self._write_clarification(root, goal_id="GOAL-READINESS", clarification_id="CLAR-001", status="resolved")
            self._write_clarification(root, goal_id="GOAL-READINESS", clarification_id="CLAR-002", status="resolved")
            self._record_ready_artifacts(root, "RUN-CLI-READY")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["build-approval", "--root", str(root), "--run-id", "RUN-CLI-READY"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Build Approval:", output)
            self.assertIn("- readiness_summary: ready", output)
            self.assertIn("- linked_clarifications: 2", output)

    def test_build_approval_output_marks_unavailable_readiness_without_failing(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._prepare_root(root)
            self._bootstrap(root, "RUN-CLI-UNAVAILABLE")
            self._record_ready_artifacts(root, "RUN-CLI-UNAVAILABLE")

            stdout = StringIO()
            with redirect_stdout(stdout):
                exit_code = main(["build-approval", "--root", str(root), "--run-id", "RUN-CLI-UNAVAILABLE"])

            self.assertEqual(exit_code, 0)
            output = stdout.getvalue()
            self.assertIn("Build Approval:", output)
            self.assertIn("- readiness: unavailable", output)
