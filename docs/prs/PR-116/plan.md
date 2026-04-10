# PR-116 Plan

## title
- PR Loop Fixture Review Packet Rendering

## input refs
- AGENTS.md working-copy instructions provided for `/mnt/c/dev/approval-factory` on 2026-04-10
- User task for `PR-SLOT-5: optional LLM rendering for review packet text`
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline --decorate -10`
- `test -f AGENTS.md && echo present || echo missing`
- [orchestrator/pr_loop/inspect.py](/orchestrator/pr_loop/inspect.py)
- [orchestrator/pr_loop/gate_check.py](/orchestrator/pr_loop/gate_check.py)
- [orchestrator/cli.py](/orchestrator/cli.py)
- [tests/fixtures/pr_loop/README.md](/tests/fixtures/pr_loop/README.md)
- [docs/prs/PR-115/plan.md](/docs/prs/PR-115/plan.md)

## scope
- Add `factory pr-loop render-review --root . --pr-id PR-<number>` as a read-only markdown review packet draft surface.
- Require an explicit exact numeric PR id and reject implicit or non-canonical selectors such as `latest`, `current`, `PR-1A`, or `PR-1-FOO`.
- Read only local non-runtime fixture inspect and gate-check summaries under `tests/fixtures/pr_loop/examples/artifacts/pr_loop/PR-<number>`.
- Render findings-first review drafting input with fixture status, gate status, failed condition summary, scope reminder, non-authority reminder, and reviewer focus checklist.
- Handle absent or incomplete fixtures with graceful summary packets and no traceback.

## non-goals
- No review verdict automation.
- No approval clear, merge clear, merge dry-run, merge apply, or publish packet generation.
- No top-level live `artifacts/pr_loop/...` state.
- No queue, status, readiness, approval, inspect, gate-check, trace, or debug semantic change.
- No implicit latest/current/current-branch/latest-run selector fallback.
- No runtime artifact creation or mutation.

## output summary
- Add `orchestrator/pr_loop/render_review.py` for fixture-backed markdown packet drafting.
- Add nested CLI support for `factory pr-loop render-review --root . --pr-id PR-<number>`.
- Add focused tests for present fixture rendering, absent fixture handling, incomplete fixture handling, invalid selector refusal, help text, and output wording guardrails.
- Update fixture README wording to include the render-review drafting surface and authority boundary.

## ADR decision
- ADR required now: no.
- Reason: this PR adds a local non-runtime fixture renderer over existing read-only fixture summaries only. It does not introduce runtime state, policy authority, gate evidence authority, queue/status semantics, approval authority, review verdict authority, or merge authority.
- Approval required before ADR-free runtime authority: yes. Any future PR that introduces live `artifacts/pr_loop/PR-<number>/...` state, LLM runtime execution, approval state, merge state, or authoritative gate evidence must re-evaluate ADR need before implementation.

## risks
- If wording is too strong, operators may mistake fixture rendering for review, approval, or merge authority.
- If selectors drift from exact PR ids, the command could render the wrong fixture.
- If the command reads queue/status/latest state, it would violate the fixture-only scope.
- If docs/help/tests disagree, the command contract could become ambiguous.

## next required gate
- Reviewer: confirm the diff is limited to fixture-backed read-only review packet drafting and does not change hot path semantics.
- QA: confirm present, absent, incomplete, and invalid selector cases are graceful and no runtime artifacts are created or mutated.
- Docs Sync / Release: confirm README, help text, tests, and this PR note state the same fixture-only, non-authoritative contract.
