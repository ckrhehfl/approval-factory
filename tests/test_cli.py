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
