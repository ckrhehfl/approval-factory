from __future__ import annotations

from tempfile import TemporaryDirectory
import unittest

from orchestrator.pipeline import PipelineState, bootstrap_run
from orchestrator.yaml_io import read_yaml


class PipelineBootstrapTest(unittest.TestCase):
    def test_pipeline_state_includes_docs_sync(self) -> None:
        self.assertEqual(PipelineState.docs_sync.value, "docs_sync")

    def test_gate_status_contains_docs_sync_state(self) -> None:
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_root = bootstrap_run(
                root_dir=root,
                run_id="RUN-002",
                work_item_id="WI-002",
                pr_id="PR-002",
                work_item_title="pipeline docs sync",
            )

            payload = read_yaml(run_root / "artifacts" / "gate-status.yaml")
            self.assertIn("docs_sync", payload["gate_status"]["states"])
            self.assertEqual(payload["gate_status"]["gates"]["merge_approval"], "pending")
