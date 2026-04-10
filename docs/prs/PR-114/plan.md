# PR-114 Plan

## title
- PR Loop Fixture-Backed Read-Only Inspect

## input refs
- AGENTS.md working-copy instructions provided for `/mnt/c/dev/approval-factory` on 2026-04-10
- User task for PR-SLOT-3 fixture-backed read-only inspect
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline --decorate -10`
- `test -f AGENTS.md && echo present || echo missing`
- `docs/proposals/pr-loop-runner.md`
- `tests/fixtures/pr_loop/schema/pr-loop-artifact-manifest.yaml`
- `tests/fixtures/pr_loop/examples/artifacts/pr_loop/PR-113/state.yaml`
- `tests/fixtures/pr_loop/README.md`
- `orchestrator/cli.py`

## scope
- Add `factory pr-loop inspect --pr-id PR-<number>` as a read-only inspect entry.
- Require an explicit exact numeric PR id and reject implicit or non-canonical selectors such as `latest`, `current`, `PR-1A`, or `PR-1-FOO`.
- Read only local non-runtime fixtures under `tests/fixtures/pr_loop/examples/artifacts/pr_loop/PR-<number>`.
- Render operator-visible facts, absence, incomplete-file status, and fixture paths only.
- Keep merge readiness, gate evaluation, approval queue semantics, status semantics, run state, and live runtime artifact paths out of scope.

## non-goals
- No gate evaluation.
- No merge dry-run, merge apply, or merge request flow.
- No LLM review packet rendering.
- No top-level `artifacts/pr_loop/...` live runtime state.
- No approval queue, run state, inspect/status, readiness, trace, or debug semantic change.
- No implicit latest/current branch/latest run selector fallback.

## output summary
- Add a minimal `orchestrator/pr_loop/` inspect module for exact numeric PR id validation and fixture summary loading.
- Add a nested CLI path for `factory pr-loop inspect --pr-id PR-<number>`.
- Add focused tests for existing fixture summary, absent fixture handling, incomplete fixture handling, and implicit/non-canonical selector refusal.
- Update fixture README wording now that the fixtures can be read by the new local non-runtime inspect surface.

## ADR decision
- ADR required now: no.
- Reason: this PR adds a fixture-backed read-only visibility command only. It does not create runtime state, phase-machine authority, approved policy authority, gate evidence authority, merge authority, or queue/status semantic changes.
- Approval required before ADR-free runtime authority: yes. Any future PR that introduces runtime authority, deterministic gate semantics, merge request/execution behavior, or live `artifacts/pr_loop/PR-<number>/...` state must re-evaluate ADR need before implementation.

## risks
- If fixture output begins to expose decision-shaped gate wording, operators may mistake inert fixture fields for merge or approval state.
- If the command falls back to latest/current selectors or accepts non-canonical ids, it may inspect the wrong target.
- If fixture roots move to top-level `artifacts/`, local examples may be confused with live runtime state.

## next required gate
- Reviewer: confirm the diff is limited to read-only fixture inspect code, tests, and docs sync.
- QA: confirm absent and incomplete fixture cases are graceful and read-only.
- Approver / PM: decide whether a later PR-SLOT-4 gate-evaluation implementation may proceed after this read-only surface lands.
