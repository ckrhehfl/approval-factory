# PR-085 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-05
- User task for PR-085 proposal-only `queue_hygiene` read-only visibility
- `git status -sb`
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- [docs/prs/README.md](/mnt/c/dev/approval-factory/docs/prs/README.md)
- [docs/prs/PR-084/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-084/plan.md)
- [docs/prs/PR-084/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-084/proposal.md)
- [orchestrator/cli.py](/mnt/c/dev/approval-factory/orchestrator/cli.py)
- [orchestrator/pipeline.py](/mnt/c/dev/approval-factory/orchestrator/pipeline.py)
- [tests/test_cli.py](/mnt/c/dev/approval-factory/tests/test_cli.py)

## scope
- PR-085 is proposal-only and docs-only.
- Decide whether `queue_hygiene` read-only visibility belongs in `factory status`, `inspect-approval-queue`, both, or neither for now.
- Keep any proposed visibility read-only operator visibility only.
- Keep `queue_hygiene` explicitly separate from cleanup, auto-resolve, approval decision, readiness/gate, selector, stale/latest relation, and Relation Summary semantics.
- Do not change runtime behavior, CLI output, tests, or queue artifacts in this PR.

## output summary
- Add this PR-local plan as the scope and validation contract for the visibility proposal.
- Add [docs/prs/PR-085/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-085/proposal.md) to define the recommended visibility surface, wording, and implementation split.
- Keep the proposal narrow: `inspect-approval-queue` item-local visibility only, no `factory status` exposure for now.

## current repo snapshot
- Branch is `pr/085-queue-hygiene-read-only-visibility-proposal`.
- `git status -sb` was clean before this PR-local docs work.
- `python -m factory status --root .` currently shows only queue summary facts: `pending_total`, `latest_run_has_pending`, `stale_pending_count`, `stale_pending_run_ids`, and `stale_pending_path`.
- `python -m factory inspect-approval-queue --root .` currently shows item-local facts for each pending approval and a separate Relation Summary section.
- Runtime writes `queue_hygiene` only inside the exact target queue artifact and only on apply, with fields `status`, `applied_at`, `selector_family`, `requested_run_id`, and `requested_approval_id`.
- Current CLI wording already says `queue_hygiene` mutation is exact-target-only and that stale/latest plus Relation Summary remain read-only operator visibility, not hygiene selectors.

## contract
- Proposed visibility, if any, must stay read-only and descriptive only.
- The proposal must not add any count, aggregate, or summary interpretation for `queue_hygiene`.
- The proposal must state that `queue_hygiene` is not cleanup state, resolve state, approval decision state, readiness/gate state, selector state, stale/latest relation state, or Relation Summary state.
- The proposal must define exact recommended wording that keeps operators from reading the field as `already cleaned up`, `safe to delete`, `safe to resolve`, `approval-ready`, `gate satisfied`, or `latest/stale selector` state.
- The proposal must split later implementation from this PR and keep any `factory status` exposure out of scope unless separately proposed.

## validation
- Proposal validation must confirm no runtime code paths changed.
- Proposal validation must confirm the proposal explicitly says `queue_hygiene` visibility is read-only only.
- Proposal validation must confirm the proposal explicitly says `queue_hygiene` is not cleanup, resolve, gate, selector, stale/latest, or Relation Summary state.
- Proposal validation must confirm the proposal names a separate implementation follow-up rather than doing it now.
- Closeout validation must report `git status --short`, `git --no-pager diff --stat`, and `git --no-pager diff --name-only`.

## risks
- If `factory status` receives a summary signal now, operators may overread it as queue-level decision or cleanup state.
- If item-local wording is weak, `queue_hygiene` can still be misread as `safe to resolve` or `already handled`.
- If implementation follow-up is not separated, this PR could drift from proposal-only into output-contract changes.

## next required gate
- Reviewer: confirm the PR is docs-only and that the proposal keeps `queue_hygiene` visibility descriptive only.
- Approver / PM: decide whether the proposed `inspect-approval-queue` item-local surface should proceed as a later implementation PR.
- Docs Sync / Release: confirm no broader docs sync is required because this PR changes only PR-local proposal docs.
