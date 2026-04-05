# PR-088 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-05
- User task for PR-088 docs/help/tests-only wording verification
- `git status -sb`
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- [README.md](/mnt/c/dev/approval-factory/README.md)
- [docs/design/architecture.md](/mnt/c/dev/approval-factory/docs/design/architecture.md)
- [docs/prs/PR-085/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-085/plan.md)
- [docs/prs/PR-085/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-085/proposal.md)
- [docs/prs/PR-086/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-086/plan.md)
- [docs/prs/PR-087/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-087/plan.md)
- [docs/prs/PR-087/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-087/proposal.md)
- [tests/test_cli.py](/mnt/c/dev/approval-factory/tests/test_cli.py)

## scope
- PR-088 is docs/help/tests-only verification for `queue_hygiene_audit` wording.
- Keep actual repo/code/tests/runtime behavior as source of truth.
- Verify current inspect wording as read-only operator-audit wording without changing runtime output strings.
- Verify operator-safe boundaries explicitly: not cleanup, not resolve, not approval decision, not readiness/gate, not selector, not latest/stale relation, not Relation Summary state.
- Do not change inspect output code, `factory status`, queue artifact schema, or runtime semantics.

## output summary
- Add this PR-local plan as the contract for wording-verification-only work.
- Refine repo docs so safe vs unsafe interpretation is stated directly against the current runtime surface.
- Add focused CLI tests that lock the current inspect wording as operator-audit evidence and guard against interpretation drift.
- Add a one-shot validation-style test shape that checks inspect item-local rendering and `factory status` non-exposure together.

## current repo snapshot
- Branch is `pr/088-queue-hygiene-wording-verification-docs-tests`.
- Actual repo behavior today still shows queue summary facts in `factory status` and Relation Summary plus per-item latest relation facts in `inspect-approval-queue`.
- Current `inspect-approval-queue` item-local output already renders `queue_hygiene_audit` only when the pending artifact stores queue hygiene metadata.
- Current wording already points in the right direction by saying `read-only operator visibility only` and `exact stored audit fields only`, then listing excluded meanings.
- The risk for this PR is interpretation drift in docs/help/tests, not missing runtime behavior.

## contract
- Verification must treat current wording as evidence only, not as approval to expand semantics.
- Tests must lock current wording as operator-audit oriented and keep it item-local.
- Tests must explicitly guard against drift toward cleanup, resolve, approval decision, readiness/gate, selector, latest/stale relation, and Relation Summary state.
- Tests must keep `factory status` free of `queue_hygiene_audit` or related field exposure.
- Docs must say that PR-088 does not change runtime wording yet and exists to make later refinement decisions easier.

## validation
- Execution validation one-shot:
- create a temp root with two pending approval artifacts
- add `queue_hygiene` metadata to exactly one target item
- run `python -m factory inspect-approval-queue --root "$tmp"`
- run `python -m factory status --root "$tmp"`
- confirm item-local visibility still appears only on the target item
- confirm `factory status` still has no `queue_hygiene` visibility
- confirm current wording is documented and tested as read-only audit only, not decision-state wording
- Closeout validation:
- run `git status --short`
- run `git --no-pager diff --stat`
- run `git --no-pager diff --name-only`
- run `PYTHONPATH=. pytest -q`

## risks
- If docs phrase the output as state instead of audit evidence, later reviewers may approve semantics expansion by accident.
- If tests only lock the full line but not the negative interpretations, unsafe wording shortcuts could slip in under later edits.
- If verification ignores actual repo behavior and assumes prior PR summaries, the docs contract would diverge from source of truth.

## next required gate
- Reviewer: confirm this PR remains docs/help/tests-only and does not modify runtime behavior.
- QA: confirm the one-shot validation and full pytest run pass with current wording unchanged.
- Docs Sync / Release: confirm no broader docs sync is required beyond the touched contracts and PR-local plan.
