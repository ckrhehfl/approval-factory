from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from orchestrator.pr_loop.inspect import validate_pr_id
from orchestrator.pr_loop.phase_machine import initial_pr_loop_phase, validate_pr_loop_phase


@dataclass(frozen=True)
class PrLoopState:
    pr_id: str
    runner_id: str
    phase: str

    @classmethod
    def initialize(cls, *, pr_id: str) -> "PrLoopState":
        canonical_pr_id = validate_pr_id(pr_id)
        pr_number = canonical_pr_id.removeprefix("PR-")
        return cls(
            pr_id=canonical_pr_id,
            runner_id=f"PR-LOOP-RUNTIME-{pr_number}",
            phase=initial_pr_loop_phase(),
        )

    @classmethod
    def from_payload(cls, payload: object, *, pr_id: str) -> "PrLoopState":
        canonical_pr_id = validate_pr_id(pr_id)
        if not isinstance(payload, dict):
            raise ValueError("pr-loop state payload must be a mapping")

        target_pr = payload.get("target_pr")
        if target_pr != canonical_pr_id:
            raise ValueError("pr-loop state target_pr must match the canonical PR id anchored path")

        runner_id = payload.get("runner_id")
        if not isinstance(runner_id, str) or not runner_id:
            raise ValueError("pr-loop state runner_id must be a non-empty string")

        phase = validate_pr_loop_phase(payload.get("phase"))
        return cls(pr_id=canonical_pr_id, runner_id=runner_id, phase=phase)

    def as_payload(self) -> dict[str, object]:
        return {
            "target_pr": self.pr_id,
            "runner_id": self.runner_id,
            "phase": self.phase,
        }
