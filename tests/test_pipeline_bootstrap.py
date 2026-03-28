from __future__ import annotations

from tempfile import TemporaryDirectory
import unittest

from orchestrator.pipeline import PipelineState, bootstrap_run
from orchestrator.yaml_io import read_yaml


class PipelineBootstrapTest(unittest.TestCase):
    def test_pipeline_state_includes_approval_pending(self) -> None:
        self.assertEqual(PipelineState.approval_pending.value, "approval_pending")

    def test_gate_status_contains_refined_states(self) -> None:
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
            self.assertEqual(
                payload["gate_status"]["states"],
                ["draft", "in_progress", "approval_pending", "approved", "rejected"],
            )
            self.assertEqual(payload["gate_status"]["gates"]["merge_approval"], "pending")
