# PR-091 Plan

## Input Refs
- Repo branch: `pr/091-orchestration-wording-hardening`
- Prior boundary note: `docs/prs/PR-089/plan.md`
- Implemented surface note: `docs/prs/PR-090/plan.md`
- Source of truth reviewed from repo code/tests: `orchestrator/cli.py`, `tests/test_cli.py`, `README.md`

## Scope
- Wording/docs/tests hardening only for the already-implemented dedicated `inspect-orchestration` surface.
- Keep the anchor exact to `--work-item-id <WI-...>` only.
- Do not change command behavior, parser shape, entrypoints, official-artifact-only scope, next-step assist scope, or lifecycle/readiness/approval/queue semantics.

## Output Summary
- Harden `inspect-orchestration` help wording so it reads as exact-anchor read-only visibility only.
- Harden README contract wording so the surface is less likely to be misread as recommendation, gating, target selection, or approval/readiness/queue action advice.
- Add focused tests that lock safe wording and reject unsafe wording drift in both help and runtime output.

## Risks
- Residual risk remains future wording drift outside the current focused help/runtime assertions.
- The surface can still be overread by a hurried operator if later edits weaken `read-only`, `official artifact summary only`, or `human decision required`.

## Next Required Gate
- Reviewer: confirm the change stays wording/docs/tests hardening only and preserves the PR-090 runtime boundary with no semantic expansion.
