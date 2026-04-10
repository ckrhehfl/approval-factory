# PR-115 Plan

## title
- PR Loop Fixture-Backed Deterministic Gate Evaluation

## input refs
- AGENTS.md working-copy instructions provided for `/mnt/c/dev/approval-factory` on 2026-04-10
- User task for `PR-SLOT-4: fixture-backed deterministic gate evaluation`
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline --decorate -10`
- `test -f AGENTS.md && echo present || echo missing`
- [orchestrator/pr_loop/inspect.py](/orchestrator/pr_loop/inspect.py)
- [orchestrator/cli.py](/orchestrator/cli.py)
- [tests/fixtures/pr_loop/schema/pr-loop-artifact-manifest.yaml](/tests/fixtures/pr_loop/schema/pr-loop-artifact-manifest.yaml)
- [tests/fixtures/pr_loop/examples/artifacts/pr_loop/PR-113/state.yaml](/tests/fixtures/pr_loop/examples/artifacts/pr_loop/PR-113/state.yaml)
- [tests/fixtures/pr_loop/README.md](/tests/fixtures/pr_loop/README.md)
- [docs/prs/PR-114/plan.md](/docs/prs/PR-114/plan.md)

## scope
- Add `factory pr-loop gate-check --pr-id PR-<number>` as a fixture-backed read-only deterministic condition summary.
- Require an explicit exact numeric PR id and reject implicit or non-canonical selectors such as `latest`, `current`, `PR-1A`, or `PR-1-FOO`.
- Read only local non-runtime fixtures under `tests/fixtures/pr_loop/examples/artifacts/pr_loop/PR-<number>`.
- Evaluate condition facts from the fixture manifest, `state.yaml`, and local review/check observation fixtures.
- Render neutral `gate_status`, condition counts, and failed-condition facts without merge, approval, queue, or runtime authority.

## non-goals
- No merge dry-run or merge apply path.
- No PR publish text generation.
- No LLM rendering.
- No top-level live `artifacts/pr_loop/...` state.
- No approval queue, run state, status, readiness, inspect, trace, or debug semantic change.
- No implicit latest/current/current-branch/latest-run selector fallback.
- No authoritative ready-to-merge or approval semantics.

## output summary
- Add `orchestrator/pr_loop/gate_check.py` for fixture-backed deterministic condition evaluation.
- Add nested CLI support for `factory pr-loop gate-check --root . --pr-id PR-<number>`.
- Add focused tests for present fixture evaluation, absent fixture handling, incomplete fixture handling, invalid selector refusal, and output guardrails against runtime/merge authority wording.
- Update fixture README wording to include the new read-only condition-summary surface.

## ADR decision
- ADR required now: no.
- Reason: this PR adds a local non-runtime fixture reader and deterministic read-only summary only. It does not introduce runtime state, approved policy authority, gate evidence authority, merge authority, queue/status semantics, or automation authority.
- Approval required before ADR-free runtime authority: yes. Any future PR that introduces live `artifacts/pr_loop/PR-<number>/...` state, merge dry-run/apply behavior, runtime policy authority, or authoritative gate evidence must re-evaluate ADR need before implementation.

## risks
- If `gate-check` wording is too strong, operators may mistake fixture facts for merge or approval authority.
- If unknown fixture review/check states are treated as pass, the summary could overstate fixture evidence.
- If selectors drift from exact PR ids, the command could inspect the wrong fixture.
- If the command reads top-level runtime artifacts, it would violate the fixture-only scope.

## next required gate
- Reviewer: confirm the diff is limited to fixture-backed read-only condition evaluation and does not change hot path semantics.
- QA: confirm absent/incomplete fixtures are graceful and no runtime artifacts are created or mutated.
- Docs Sync / Release: confirm README, help text, tests, and this PR note state the same fixture-only, non-authoritative contract.
