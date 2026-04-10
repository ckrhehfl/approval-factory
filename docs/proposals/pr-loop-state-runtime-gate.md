# Proposal: PR Loop State Runtime Gate

## input refs
- AGENTS.md working-copy instructions provided for `/mnt/c/dev/approval-factory` on 2026-04-11 KST.
- User task for PR-120 proposal-only state runtime gate / ADR-equivalent boundary.
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline --decorate -10`
- `test -f AGENTS.md && echo present || echo missing`
- `python -m factory pr-loop inspect --root . --pr-id PR-113`
- `python -m factory pr-loop gate-check --root . --pr-id PR-113`
- `python -m factory pr-loop render-review --root . --pr-id PR-113`
- `python -m factory pr-loop merge --root . --pr-id PR-113 --dry-run`
- `test -d artifacts && find artifacts -maxdepth 3 -type f | sort | head -50 || echo artifacts_dir_absent`
- `docs/proposals/pr-loop-runner.md`
- `docs/proposals/pr-loop-live-runtime-authority-contract.md`
- `docs/proposals/README.md`
- `docs/prs/PR-113/plan.md`
- `docs/prs/PR-114/plan.md`
- `docs/prs/PR-115/plan.md`
- `docs/prs/PR-116/plan.md`
- `docs/prs/PR-117/plan.md`
- `docs/prs/PR-119/plan.md`

## scope
- Proposal-only PR-120 state runtime gate for PR Loop.
- Narrows the PR-119 live runtime authority proposal to the state authority boundary, initializer authority, versioning, invalidation, migration constraints, and prerequisite gates before implementation.
- Treats repo code, tests, git history, and runtime artifacts as source of truth. `docs/prs` and continuity notes remain reference material only.
- Does not implement runtime code, CLI behavior, state core, initializer commands, live artifacts, policy authority, merge authority, dry-run/apply behavior, queue/status/readiness semantics, fixture promotion, or official pack changes.

## current landed facts
- Baseline command evidence on 2026-04-11 KST reported no active PR. `factory status` reported latest run `RUN-20260327T063724Z`, state `approval_pending`, pending approval status, `pending_total: 2`, `latest_run_has_pending: True`, and one stale pending approval for `RUN-20260327T055614Z`.
- `inspect-approval-queue` reported two pending approvals: stale `APR-RUN-20260327T055614Z.yaml` for `PR-003` and latest `APR-RUN-20260327T063724Z.yaml` for `PR-004`.
- Git baseline was branch `pr/120-pr-loop-state-runtime-gate-proposal` at `a79f8f6 Merge pull request #115 from ckrhehfl/pr/119-pr-loop-live-runtime-authority-proposal`, with `AGENTS.md` present.
- The landed PR Loop slice is still the PR-113 through PR-117 fixture-backed read-only lane:
  - PR-113 added inert fixture examples under `tests/fixtures/pr_loop/...`.
  - PR-114 added fixture-backed `factory pr-loop inspect`.
  - PR-115 added fixture-backed `factory pr-loop gate-check`.
  - PR-116 added fixture-backed review packet draft rendering.
  - PR-117 added fixture-backed `factory pr-loop merge --dry-run`.
- `factory pr-loop inspect --root . --pr-id PR-113` reported `source: local_non_runtime_fixture`, `runtime_authority: none`, and `mutation: none`.
- `factory pr-loop gate-check --root . --pr-id PR-113` reported `gate_status: fail`, `runtime_authority: none`, `merge_authority: none`, `decision_authority: none`, and `mutation: none`.
- `factory pr-loop render-review --root . --pr-id PR-113` reported review drafting input only, with `runtime_authority: none`, `merge_authority: none`, `approval_authority: none`, `mutation: none`, and `fixture_scope: local inert fixture only`.
- `factory pr-loop merge --root . --pr-id PR-113 --dry-run` reported a read-only summary only, with `runtime_authority: none`, `merge_authority: none`, `approval_authority: none`, and `mutation: none`.
- The checked repo has no top-level live `artifacts` directory. Therefore no live `artifacts/pr_loop/<PR-ID>/state.yaml` currently exists as runtime state.
- PR-119 fixed a proposal-only live runtime authority contract. It did not create live artifacts, state authority, policy authority, merge authority, apply mode, or an initializer command.
- Current PR Loop code does not implement live artifact load/save, state authority, phase-machine authority, policy authority, queue input, status input, approval authority, merge apply, or official pack automation.
- `artifacts/pr_loop/<PR-ID>/state.yaml` is not current runtime state. Any `state.yaml` under `tests/fixtures/pr_loop/examples/artifacts/pr_loop/<PR-ID>/` is fixture data only.

## non-goals and rejected options
- Do not promote `tests/fixtures/pr_loop/...` into live runtime state.
- Do not treat the fixture lane as live PR Loop runtime state, state evidence, gate evidence, merge evidence, approval evidence, or policy authority.
- Do not treat `runs/latest`, `approval_queue`, or `docs/prs` as a PR Loop state authority source.
- Do not treat inspect, readiness, status, trace, debug, rendered review packets, or dry-run summaries as state transition decision input.
- Do not infer a target PR, state phase, initializer authority, approval status, check status, or merge eligibility from latest run, latest queue item, current branch, stale queue item, or rendered text.
- Do not implement any `init`-style command in this PR. Future `factory pr-loop init`, `initialize`, `state create`, or equivalent commands are prohibited until a separate approved state authority contract defines whether they may exist and who may invoke them.
- Do not implement state core, phase machine, live artifact writes, state migration, queue mutation, status mutation, approval mutation, policy loading, merge request, merge apply, or official pack mutation.
- Do not decide dry-run authority, policy authority, or merge authority in this PR. They remain out of scope except where their absence constrains state implementation.

## proposed live state namespace
- Future live PR Loop state may use `artifacts/pr_loop/<PR-ID>/state.yaml` only after a later implementation PR passes the prerequisite gates in this proposal.
- `artifacts/pr_loop/<PR-ID>/` is proposed as a PR Loop-specific runtime namespace, not an alias for `runs/latest`, `approval_queue`, `docs/prs`, fixture examples, or continuity handoff material.
- Until that later implementation exists, the state runtime authority for `artifacts/pr_loop/<PR-ID>/state.yaml` is `none`.
- The state namespace must be explicitly rooted by canonical PR id. No implicit selectors such as `latest`, `current`, current branch, latest run, or latest queue item may initialize or load live state.
- If future live state references `runs/latest` or `approval_queue`, the reference must be a typed observation or evidence pointer with invalidation rules. It must not import those visibility/workflow surfaces as state authority.
- If future live state references `docs/prs`, the reference must be audit context only. It must not import PR history docs as live state, policy authority, or transition authority.

## state owner and initializer authority
- Proposed future state owner: PR Loop State Runtime Core, after explicit approval. Until that core exists, there is no owner authorized to create or mutate live PR Loop state.
- Proposed future initializer authority: unresolved. It must be decided by Architect and Approver / PM before implementation.
- A future initializer must require an explicit canonical `PR-<number>` target and a human-approved state authority contract.
- A future initializer must write only inside the approved PR Loop state namespace and must not mutate `runs/latest`, `approval_queue`, `docs/prs`, fixtures, official packs, git branches, or PR metadata.
- A future initializer must record schema version, source refs, creation time, creator role or command identity, and initial invalidation assumptions in the state artifact or adjacent approved metadata.
- A future initializer must fail closed when a live state directory already exists, when the PR id is non-canonical, when policy authority is unresolved but required, or when source refs are stale or ambiguous.
- No current command, including `inspect`, `gate-check`, `render-review`, `merge --dry-run`, `factory status`, or `inspect-approval-queue`, is an initializer.

## versioning, invalidation, and migration constraints
- `state.yaml` must include an explicit schema version before any live implementation can write it.
- State transition code must reject unknown future schema versions and fail closed on missing required version fields.
- State transition code must record enough source refs to detect stale observations. Candidate refs include target PR id, repo, branch, base, observed commit head, policy snapshot id, review observation id, check observation id, and docs sync observation id if those concepts are approved later.
- Invalidation rules must be approved before implementation. At minimum, a changed target head, changed approved policy snapshot, changed required review/check observation, or changed merge base must invalidate any derived gate state.
- Migration must be explicit. A future implementation must not silently rewrite old `state.yaml` files, fixture examples, queue files, run files, PR docs, or official packs.
- Fixture compatibility must be explicit. The existence of `tests/fixtures/pr_loop/examples/artifacts/pr_loop/<PR-ID>/state.yaml` must never cause a live migration or live artifact creation.
- If a migration command is ever introduced, it must be separate from read-only inspect/status/debug surfaces and must require its own approval, tests, evidence bundle, and rollback/failure handling.
- Until these constraints are approved in an implementation PR, all live state creation, mutation, migration, and invalidation behavior remains unimplemented.

## prerequisite gates before any implementation
- Architect gate: decide whether a formal ADR is required before live state runtime, phase-machine behavior, state transitions, invalidation, or migration implementation.
- Approver / PM gate: approve whether `artifacts/pr_loop/<PR-ID>/state.yaml` may exist as live runtime state and who may initialize it.
- State contract gate: approve the state schema, versioning, lifecycle, owner, initializer, transition model, stale-state invalidation rules, and migration constraints.
- Boundary gate: prove the design does not treat `runs/latest`, `approval_queue`, `docs/prs`, fixtures, inspect/readiness/status/trace/debug output, rendered text, or dry-run summaries as state transition decision input.
- Policy gate: approve policy source-of-truth and policy snapshot semantics before state transitions depend on policy facts. This PR does not choose policy authority.
- Merge gate: separately approve merge authority and dry-run/apply separation before any merge request or merge apply implementation. This PR does not choose merge authority.
- QA gate: provide tests for no fixture promotion, no implicit selector fallback, no read-only command mutation, no queue/status/readiness semantic change, fail-closed version handling, stale-state invalidation, and migration refusal unless explicitly approved.
- Docs sync gate: update proposal, ADR if required, policy docs if approved, PR docs, and operator docs together whenever implementation changes the state authority boundary.

## output summary
- PR-120 fixes a proposal-only state runtime gate before any PR Loop live state implementation.
- The proposal states that `artifacts/pr_loop/<PR-ID>/state.yaml` is not current runtime state and that the current fixture lane is not live state.
- The proposal rejects `runs/latest`, `approval_queue`, `docs/prs`, inspect/readiness/status/trace/debug output, rendered text, and dry-run summaries as state transition decision input.
- The proposal requires separate approval for state owner, initializer authority, schema versioning, invalidation, migration, policy authority, dry-run/apply authority, and merge authority before implementation.

## risks
- If `state.yaml` wording is treated as current behavior, future code may create live state without approved owner or initializer authority.
- If fixture state is promoted accidentally, local tests could become mistaken for live runtime evidence.
- If visibility surfaces become state transition inputs, read-only commands could drift into unapproved control-plane behavior.
- If versioning and invalidation are postponed during implementation, stale review/check/policy facts could survive into later gate or merge decisions.
- If migration is implicit, future state core could rewrite artifacts outside the approved namespace or mutate official/reference materials.

## next required gate
- Reviewer: confirm this PR is proposal-only and does not alter runtime code, fixtures, CLI semantics, queue/status/readiness behavior, live artifacts, or official packs.
- Architect: decide ADR requirement before any state runtime, initializer, phase-machine, invalidation, or migration implementation.
- Approver / PM: approve or reject the state authority and initializer boundary before implementation begins.
