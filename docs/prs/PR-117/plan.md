# PR-117 Plan

## title
- PR Loop Fixture Merge Dry-Run Summary

## input refs
- AGENTS.md working-copy instructions provided for `/mnt/c/dev/approval-factory` on 2026-04-10
- User task for `PR-SLOT-6a: fixture-backed merge dry-run summary`
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline --decorate -10`
- `test -f AGENTS.md && echo present || echo missing`
- [orchestrator/pr_loop/inspect.py](/orchestrator/pr_loop/inspect.py)
- [orchestrator/pr_loop/gate_check.py](/orchestrator/pr_loop/gate_check.py)
- [orchestrator/pr_loop/render_review.py](/orchestrator/pr_loop/render_review.py)
- [orchestrator/cli.py](/orchestrator/cli.py)
- [tests/fixtures/pr_loop/README.md](/tests/fixtures/pr_loop/README.md)
- [docs/prs/PR-116/plan.md](/docs/prs/PR-116/plan.md)

## scope
- Add `factory pr-loop merge --root . --pr-id PR-<number> --dry-run` as a read-only fixture-backed merge dry-run summary surface.
- Require an explicit exact numeric PR id and reject implicit or non-canonical selectors such as `latest`, `current`, `PR-1A`, or `PR-1-FOO`.
- Read only local non-runtime fixture inspect, gate-check, and review packet surfaces under `tests/fixtures/pr_loop/examples/artifacts/pr_loop/PR-<number>`.
- Render neutral operator-visible fields such as `merge_dry_run_status`, precondition counts, failed preconditions, authority boundaries, mutation boundary, and note.
- Handle absent or incomplete fixtures with graceful summaries and no traceback.

## non-goals
- No `--apply`.
- No git merge, checkout, branch deletion, push, PR mutation, queue mutation, or runtime artifact mutation.
- No top-level live `artifacts/pr_loop/...` state.
- No queue, status, readiness, approval, inspect, gate-check, render-review, trace, or debug semantic change.
- No implicit latest/current/current-branch/latest-run selector fallback.
- No runtime artifact creation or mutation.
- No merge authority, approval authority, review verdict, or live gate evidence.

## output summary
- Add `orchestrator/pr_loop/merge_dry_run.py` for fixture-backed read-only merge dry-run summaries.
- Add nested CLI support for `factory pr-loop merge --root . --pr-id PR-<number> --dry-run`.
- Add focused tests for present fixture dry-run summary, absent fixture handling, incomplete fixture handling, invalid selector refusal, help text, wording guardrails, and no runtime artifact mutation.
- Update fixture README wording to include the merge dry-run summary surface and authority boundary.

## ADR decision
- ADR required now: no.
- Reason: this PR adds a local non-runtime fixture summary over existing read-only fixture surfaces only. It does not introduce runtime state, policy authority, gate evidence authority, queue/status semantics, approval authority, merge authority, or git mutation.
- Approval required before ADR-free runtime authority: yes. Any future PR that introduces live `artifacts/pr_loop/PR-<number>/...` state, merge execution, approval state, or authoritative gate evidence must re-evaluate ADR need before implementation.

## risks
- If wording is too strong, operators may mistake fixture-backed dry-run output for merge authority.
- If selectors drift from exact PR ids, the command could summarize the wrong fixture.
- If the command reads queue/status/latest state, it would violate the fixture-only scope.
- If docs/help/tests disagree, the dry-run contract could become ambiguous.

## next required gate
- Reviewer: confirm the diff is limited to fixture-backed read-only merge dry-run summarization and does not change hot path semantics.
- QA: confirm present, absent, incomplete, and invalid selector cases are graceful and no runtime artifacts are created or mutated.
- Docs Sync / Release: confirm README, help text, tests, and this PR note state the same fixture-only, non-authoritative contract.
