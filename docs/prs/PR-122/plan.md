# PR-122 Plan

## title
- PR Loop Merge Authority / Dry-Run Apply Contract Proposal

## input refs
- User task for PR-122 proposal-only merge authority boundary / dry-run-apply contract.
- `git status -sb`
- `git diff --check`
- `git --no-pager diff --stat`
- `git --no-pager diff -- docs/proposals/README.md docs/proposals/pr-loop-merge-authority-dry-run-apply-contract.md docs/prs/PR-122/plan.md`
- `python -m pytest tests/test_pr_loop_*.py`
- `python -m pytest -q`

## scope
- Proposal-only docs update for the PR Loop merge authority / dry-run apply contract.
- Evidence cleanup only for attached-review-backed statements in the proposal and this plan.
- No runtime change, semantics change, or authority-surface expansion.

## output summary
- Narrow PR-122 documentation to proposal-only evidence cleanup.
- Keep `input refs` and proposal wording aligned to current attached review inputs only.
- Preserve proposal-only boundary wording without introducing runtime facts or runtime changes.

## risks
- If document refs exceed the attached review input range, the same structural issue will remain.
- If proposal wording drifts into current runtime claims, the review could again read unsupported facts as current evidence.
- If dry-run or visibility surfaces are described as current authority instead of rejected authority surfaces, the boundary could become ambiguous.

## next required gate
- Reviewer: confirm this PR is limited to proposal-only docs updates and same-PR evidence cleanup.
- Reviewer: confirm the proposal and plan use only the allowed current review inputs and do not assert new runtime facts.
- Approver / PM: decide whether the cleaned proposal boundary is acceptable for merge.
