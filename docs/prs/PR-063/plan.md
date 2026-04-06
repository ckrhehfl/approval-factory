# PR-063 Plan

## input refs
- AGENTS.md v2026-04-03
- [docs/prs/PR-059/plan.md](/docs/prs/PR-059/plan.md)
- [docs/prs/PR-060/plan.md](/docs/prs/PR-060/plan.md)
- [orchestrator/cli.py](/orchestrator/cli.py)
- [tests/test_cli.py](/tests/test_cli.py)
- User request for PR-063 observed on 2026-04-03

## scope
- Add small operator-assist help discoverability for `status`, `inspect-approval-queue`, `inspect-pr-plan`, `inspect-work-item`, `inspect-clarification`, `inspect-goal`, and `trace-lineage`.
- Limit changes to `orchestrator/cli.py`, `tests/test_cli.py`, and this `docs/prs/PR-063/plan.md`.
- Keep runtime behavior and command semantics unchanged.
- Add only help-layer `description`, `epilog`, operator-hint next steps, examples, and focused help-output tests.
- Keep visibility/read-only commands framed as visibility continuity only, not as gates, selectors, decisions, or automatic orchestration.
- Avoid wording that presents readiness visibility as gating.

## output summary
- `orchestrator/cli.py` adds explicit descriptions and `Next step:` / `Example:` epilogs for the seven visibility-oriented commands in scope.
- The new help text keeps follow-ups operator-chosen and read-only oriented where required.
- `tests/test_cli.py` adds help-output assertions that each scoped command includes a description, `Next step:`, and `Example:`.
- PR-063 adds its own minimum history note at `docs/prs/PR-063/plan.md`.

## risks
- Help wording is easy to over-specify; if phrasing drifts toward activation or approval semantics, operators could misread visibility commands as control inputs.
- Focused help tests protect presence and key examples, but future wording edits could still reintroduce unwanted gating language unless reviewers check the phrasing intent.

## next required gate
- Reviewer: confirm the seven commands remain visibility-only in wording, readiness visibility is not described as gating, and no runtime semantics changed.
- QA: run focused CLI help tests to confirm each scoped command emits description, `Next step:`, and `Example:` text.
- Docs Sync / Release: confirm PR-063 requires no additional docs beyond this plan note because the change is limited to CLI help discoverability.
