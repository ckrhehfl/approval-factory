# Proposal: PR Loop Policy Authority Source Contract

## input refs
- AGENTS.md working-copy instructions provided for `/mnt/c/dev/approval-factory` on 2026-04-11 KST.
- User task for PR-121 proposal-only policy authority source contract.
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
- `docs/proposals/pr-loop-state-runtime-gate.md`
- `docs/proposals/README.md`
- `docs/prs/PR-119/plan.md`
- `docs/prs/PR-120/plan.md`

## scope
- Proposal-only PR-121 contract for PR Loop policy authority source, policy snapshots, stale invalidation, and exception / override boundaries.
- Fixes what current surfaces are not allowed to become policy authority before any policy loader or policy snapshot reader exists.
- Treats repo code, tests, git history, and runtime artifacts as source of truth. Official runtime artifacts and official repo docs may support review, but `docs/prs` and continuity handoff material remain reference only.
- Does not implement runtime code, CLI behavior, policy loader, policy snapshot reader, state core, live artifacts, phase machine, gate core, merge authority, apply mode, queue/status/readiness semantics, fixture promotion, or official pack updates.

## current landed facts
- Baseline command evidence on 2026-04-11 KST reported no active PR. `factory status` reported latest run `RUN-20260327T063724Z`, state `approval_pending`, pending approval status, `pending_total: 2`, `latest_run_has_pending: True`, and one stale pending approval for `RUN-20260327T055614Z`.
- `inspect-approval-queue` reported two pending approvals: stale `APR-RUN-20260327T055614Z.yaml` for `PR-003` and latest `APR-RUN-20260327T063724Z.yaml` for `PR-004`.
- Git baseline was branch `pr/121-pr-loop-policy-authority-source-proposal` at `26b83e6 Merge pull request #116 from ckrhehfl/pr/120-pr-loop-state-runtime-gate-proposal`, with `AGENTS.md` present.
- The checked repo has no top-level live `artifacts` directory. Therefore no live `artifacts/pr_loop/<PR-ID>` runtime state, policy snapshot, gate evidence, merge evidence, or approved PR Loop policy artifact currently exists there.
- The landed PR Loop slice remains fixture-backed and read-only:
  - PR-113 added inert fixture examples under `tests/fixtures/pr_loop/...`.
  - PR-114 added fixture-backed `factory pr-loop inspect`.
  - PR-115 added fixture-backed `factory pr-loop gate-check`.
  - PR-116 added fixture-backed review packet draft rendering.
  - PR-117 added fixture-backed `factory pr-loop merge --dry-run`.
- `factory pr-loop inspect --root . --pr-id PR-113` reported `source: local_non_runtime_fixture`, `runtime_authority: none`, and `mutation: none`. Its stored fixture facts include `policy_source_status: unresolved_future_contract` and `policy_source_authority: none`.
- `factory pr-loop gate-check --root . --pr-id PR-113` reported `gate_status: fail`, `runtime_authority: none`, `merge_authority: none`, `decision_authority: none`, and `mutation: none`.
- `factory pr-loop render-review --root . --pr-id PR-113` reported review drafting input only, with `runtime_authority: none`, `merge_authority: none`, `approval_authority: none`, `mutation: none`, and `fixture_scope: local inert fixture only`.
- `factory pr-loop merge --root . --pr-id PR-113 --dry-run` reported a read-only summary only, with `runtime_authority: none`, `merge_authority: none`, `approval_authority: none`, and `mutation: none`.
- PR-119 fixed a proposal-only live runtime authority contract. It did not create live artifacts, state authority, policy authority, merge authority, apply mode, or a policy loader.
- PR-120 fixed a proposal-only state runtime gate. It did not create live artifacts, state authority, policy authority, merge authority, apply mode, or a policy snapshot reader.
- Current PR Loop code does not implement live artifact load/save, state authority, phase-machine authority, approved policy authority, policy loading, policy snapshot reading, queue input, status input, approval authority, merge apply, or official pack automation.
- Current approved policy authority for PR Loop is `none`.

## non-goals and rejected options
- Do not treat the fixture lane as policy authority. Fixture files, fixture manifest fields, fixture policy snapshots, fixture gate summaries, and fixture rendered text are inert local test data only.
- Do not treat `runs/latest`, `approval_queue`, or `docs/prs` as policy source of truth.
- Do not treat inspect, readiness, status, trace, debug, rendered review text, review packet drafts, gate-check output, or dry-run summaries as policy decision input.
- Do not infer policy from latest run, latest queue item, stale queue item, current branch, current PR docs, continuity notes, generated summaries, or LLM-written review text.
- Do not implement a policy loader, policy snapshot reader, policy cache, policy migration, policy override command, state core/init behavior, merge authority, or apply semantics in this PR.
- Do not decide state authority, merge authority, dry-run/apply authority, phase-machine behavior, or live `artifacts/pr_loop` creation in this PR.
- Do not update official packs in this PR.
- Do not allow future runtime code to load policy from any candidate path until a separate approved contract fixes the path, schema, versioning, approval owner, and invalidation behavior.

## proposed policy source-of-truth candidates
- Candidate A: repo-local policy contract under a dedicated policy directory such as `docs/policies/pr-loop/`. This keeps policy review near repo code and docs, but it still needs a separate approval rule because proposal docs alone are not runtime authority.
- Candidate B: ADR-linked policy contract under the repo's architecture decision surface, if Architect decides policy authority is structural enough to require an ADR. This improves architecture traceability but may be heavier than needed for operational policy changes.
- Candidate C: a future runtime policy artifact under an approved `artifacts/pr_loop` namespace. This could preserve exact runtime inputs but is not available today because live PR Loop artifacts and state authority do not exist.
- Candidate D: a checked-in machine-readable policy file, paired with human-readable policy documentation. This may be appropriate for deterministic gates, but the file path, schema version, reviewer/approver requirements, and docs sync rule must be approved before implementation.
- Rejected as candidates for policy source of truth: `runs/latest`, `approval_queue`, `docs/prs`, `tests/fixtures/pr_loop`, continuity packs, inspect/readiness/status/trace/debug command text, rendered review packets, and `merge --dry-run` summaries.
- PR-121 does not choose among the viable candidates. It only fixes that there is currently no approved policy authority and that runtime code must fail closed until a later approved contract selects one.

## policy snapshot, versioning, and stale invalidation constraints
- A future policy snapshot must be derived from an approved policy source-of-truth, not from transient command output, generated prose, fixtures, queue files, run status, or PR history docs.
- A future policy snapshot must record at least a policy schema version, policy source path or id, source commit or content digest, snapshot id, snapshot creation time, approving role or approval reference, and the PR id or scope it applies to if scoped policy is allowed.
- A future policy loader must reject missing schema versions, unknown future schema versions, ambiguous policy sources, multiple conflicting policy sources, unapproved policy sources, and stale snapshots.
- A future policy snapshot reader must fail closed if the policy source commit/digest changes, the target PR head changes when policy is PR-scoped, required review/check/docs-sync rules change, exception records change, or the snapshot lacks the approved source refs.
- A future state or gate implementation may reference a policy snapshot id only after the policy source contract and state contract define how snapshot ids are stored, invalidated, and refreshed.
- A future implementation must not silently regenerate, migrate, or backfill policy snapshots from fixtures, docs/prs plans, approval queue entries, or rendered review text.
- Policy snapshot invalidation must be deterministic and test-covered before policy-backed gate or merge authority can exist.

## exception, override, and approval boundary
- A future exception or override must be explicit human approval evidence. It must not be inferred from pending queue items, stale queue items, status/readiness output, fixture fields, rendered review packets, dry-run summaries, trace/debug output, or LLM text.
- Exception policy must define the approving role, allowed exception types, required justification, expiration or scope, source refs, and stale invalidation behavior before implementation.
- Exceptions must be narrower than the policy rule they override and must identify the exact policy rule, PR id, target head or artifact digest, and time/scope boundary.
- Exceptions must not override missing human approval evidence, missing required check evidence, docs sync requirements, security/cost/performance constraints, or failed tests unless the approved policy explicitly allows that exception type and records the approving authority.
- A future policy override path must be separate from read-only inspect/status/debug surfaces and separate from merge apply. Override approval does not imply merge authority.
- Any exception that changes architecture, security, cost, performance, release, test-failure handling, implementation scope, or docs sync expectations is `approval required` and may require Architect review or ADR before runtime code acts on it.

## prerequisite gates before any implementation
- Architect gate: decide whether policy authority and exception semantics require a formal ADR before policy loader, policy snapshot reader, policy-backed gate, state transition, phase machine, or merge apply implementation.
- Approver / PM gate: approve which policy source-of-truth candidate is authoritative, who may approve it, and what exception/override evidence is acceptable.
- Policy contract gate: approve policy file path or artifact id, schema/versioning, machine-readable vs human-readable split, docs sync requirements, snapshot fields, stale invalidation rules, and migration constraints.
- Boundary gate: prove the design does not treat `runs/latest`, `approval_queue`, `docs/prs`, fixtures, inspect/readiness/status/trace/debug output, rendered review text, gate-check output, or dry-run summaries as policy decision input.
- State gate: separately approve state authority and policy snapshot references before any state core or init behavior records policy facts. PR-121 does not authorize state authority.
- Merge gate: separately approve merge authority and dry-run/apply separation before any merge request or merge apply implementation. PR-121 does not authorize merge authority or apply semantics.
- QA gate: provide tests for fail-closed missing policy authority, no fixture promotion, no implicit source fallback, no read-only command mutation, no transient text as policy input, stale snapshot invalidation, and exception refusal without approved evidence.
- Docs sync gate: update policy docs, proposal docs, ADR if required, PR docs, and operator docs together whenever implementation changes a policy authority boundary.

## output summary
- PR-121 fixes a proposal-only policy authority source contract before any PR Loop policy loader or policy snapshot reader exists.
- The proposal states that approved PR Loop policy authority is currently `none`.
- The proposal rejects the fixture lane, `runs/latest`, `approval_queue`, `docs/prs`, inspect/readiness/status/trace/debug output, rendered review text, gate-check output, and dry-run summaries as policy source of truth or policy decision input.
- The proposal leaves state authority, merge authority, phase-machine behavior, and apply semantics out of scope.
- The proposal requires separate approval for policy source selection, schema/versioning, snapshot invalidation, exception/override handling, and implementation tests before runtime code may read policy.

## risks
- If a future implementation loads policy before the source contract is approved, PR Loop could turn reference docs or visibility output into unreviewed decision authority.
- If fixture policy snapshots are promoted, tests could be mistaken for runtime policy evidence.
- If exception handling is implicit, overrides could bypass approval-first boundaries or survive after target head, policy, review, check, or docs-sync facts change.
- If policy snapshot invalidation is underspecified, stale rules could drive gate or merge decisions.
- If policy authority is coupled to state or merge implementation, scope could expand from proposal-only policy boundaries into unapproved runtime behavior.

## next required gate
- Reviewer: confirm this PR is proposal-only and does not alter runtime code, fixtures, CLI semantics, queue/status/readiness behavior, live artifacts, official packs, policy loader behavior, state authority, merge authority, or apply semantics.
- Architect: decide ADR need before policy authority, exception semantics, policy snapshot reader, policy-backed gate, state transition, phase machine, or merge apply implementation.
- Approver / PM: approve or reject the policy source-of-truth candidate and exception boundary before implementation begins.
