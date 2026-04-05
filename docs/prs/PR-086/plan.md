# PR-086 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-05
- User task for PR-086 implementation
- `git status -sb`
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- [docs/prs/PR-085/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-085/plan.md)
- [docs/prs/PR-085/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-085/proposal.md)
- [orchestrator/cli.py](/mnt/c/dev/approval-factory/orchestrator/cli.py)
- [orchestrator/pipeline.py](/mnt/c/dev/approval-factory/orchestrator/pipeline.py)
- [tests/test_cli.py](/mnt/c/dev/approval-factory/tests/test_cli.py)

## scope
- Implement PR-085 exactly as read-only queue hygiene visibility in `factory inspect-approval-queue` only.
- Keep the change item-local only and render a `queue_hygiene_audit` block only when that pending artifact stores queue hygiene metadata.
- Render only the exact stored audit fields: `status`, `applied_at`, `selector_family`, `requested_run_id`, `requested_approval_id`.
- Add explicit wording that the display is read-only operator visibility only and not cleanup, resolve, approval decision, readiness/gate, selector, latest/stale relation, or Relation Summary state.
- Do not change `factory status`, queue mutation behavior, apply semantics, selector semantics, or queue artifact schema.

## output summary
- Wire `queue_hygiene` metadata from queue item payloads into `inspect_approval_queue()` as read-only item-local audit data.
- Render that data in `_render_approval_queue_inspection()` only when present and keep Relation Summary unchanged.
- Add focused CLI tests for presence, absence, item-locality, wording, and `factory status` non-exposure.
- Keep docs sync limited to this PR-local implementation plan.

## contract
- `inspect-approval-queue` remains the only visibility surface for this metadata.
- `factory status` remains unchanged and must not gain `queue_hygiene` visibility, booleans, summaries, or counts.
- Relation Summary remains unchanged and must not gain `queue_hygiene` counts or interpretation.
- `queue_hygiene_audit` remains descriptive only and must not imply cleanup, resolve, approval readiness, gate satisfaction, selector memory, or stale/latest state.
- The rendered audit block must use exact stored field names and values only.

## validation
- Execution validation one-shot:
- create a temp root with at least two pending approvals
- add `queue_hygiene` metadata to exactly one target artifact
- confirm `python -m factory inspect-approval-queue --root "$tmp"` shows `queue_hygiene_audit` on only that item with exact stored fields
- confirm Relation Summary output is unchanged
- confirm `python -m factory status --root "$tmp"` does not surface queue hygiene visibility
- Closeout validation:
- run `git status --short`
- run `git --no-pager diff --stat`
- run `git --no-pager diff --name-only`
- run `PYTHONPATH=. pytest -q`

## risks
- If wording is weak, operators may overread the audit block as decision or cleanup state.
- If the block appears outside the target item, the output would imply queue-level semantics.
- If `factory status` changes, PR-085 scope would be violated.

## next required gate
- Reviewer: confirm the implementation stays inside PR-085 boundaries and keeps wording descriptive only.
- QA: confirm the one-shot execution validation and full pytest run pass.
- Docs Sync / Release: confirm no broader docs sync is required beyond this PR-local plan.
