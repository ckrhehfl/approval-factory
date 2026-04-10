# Proposal: PR Loop Runner / Review-Gated Merge Runner

## input refs
- AGENTS.md working-copy instructions provided for `/mnt/c/dev/approval-factory` on 2026-04-10
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline --decorate -10`
- `test -f AGENTS.md && echo present || echo missing`
- `python -m factory pr-loop inspect --root . --pr-id PR-113`
- `python -m factory pr-loop gate-check --root . --pr-id PR-113`
- `python -m factory pr-loop render-review --root . --pr-id PR-113`
- `python -m factory pr-loop merge --root . --pr-id PR-113 --dry-run`
- `README.md`
- `docs/prs/README.md`
- `tests/fixtures/pr_loop/README.md`
- `orchestrator/cli.py`
- `orchestrator/pr_loop/*`
- `tests/test_pr_loop_*.py`

## scope
- Proposal refresh for the in-repo subsystem named `PR Loop Runner / Review-Gated Merge Runner`, after PR-113 through PR-117 landed on `main`.
- The refresh aligns this proposal with the actual landed read-only fixture lane and sharpens the authority boundary before any live runtime, state authority, policy authority, or merge authority work is proposed.
- This PR does not implement runtime code, tests, queue mutation, CLI semantic expansion, approval semantics, state core, apply mode, hot path changes, official pack updates, or external repo orchestration.

## output summary
- Preserve why this belongs in the current repo as a new subsystem instead of a separate repo.
- Refresh current facts from PR-113 through PR-117 landed code, tests, git history, and fixture/runtime observations.
- Separate the landed local fixture lane from the unimplemented future live runtime lane.
- Clarify that the landed surface is read-only, fixture-backed, and explicitly non-authoritative.
- Document prerequisites before live `artifacts/pr_loop`, state authority, policy authority, merge authority, phase-machine behavior, or apply mode can begin.
- Keep the proposal isolated from current factory hot path runtime semantics.

## current repo facts
- Baseline on 2026-04-10: `factory status` reported no active PR, latest run `RUN-20260327T063724Z`, state `approval_pending`, pending approval status, `pending_total: 2`, `latest_run_has_pending: True`, and `stale_pending_count: 1`.
- Baseline on 2026-04-10: `factory inspect-approval-queue` reported two pending items. `APR-RUN-20260327T055614Z.yaml` was stale and matched `PR-003`; `APR-RUN-20260327T063724Z.yaml` was latest and matched `PR-004`.
- Baseline git state was `pr/118-pr-loop-authority-boundary-refresh`; `AGENTS.md` was present; HEAD was `ec2ce9f Merge pull request #113 from ckrhehfl/pr/117-pr-loop-merge-dry-run-readonly`, matching current `main`.
- Git history at HEAD shows PR-113 through PR-117 landed as the current PR Loop slice:
  - PR-113 added inert PR Loop fixture examples under `tests/fixtures/pr_loop/...`.
  - PR-114 added `factory pr-loop inspect --root . --pr-id PR-<number>`.
  - PR-115 added `factory pr-loop gate-check --root . --pr-id PR-<number>`.
  - PR-116 added `factory pr-loop render-review --root . --pr-id PR-<number>`.
  - PR-117 added `factory pr-loop merge --root . --pr-id PR-<number> --dry-run`.
- `docs/prs/README.md` states that `docs/prs/` is PR history/audit surface, not active execution input or runtime source of truth.
- This proposal is intentionally stored under `docs/proposals/` so the design proposal is not confused with PR history/audit docs.
- The current PR Loop implementation reads local non-runtime fixtures from `tests/fixtures/pr_loop/examples/artifacts/pr_loop/<PR-ID>` and the manifest at `tests/fixtures/pr_loop/schema/pr-loop-artifact-manifest.yaml`.
- `factory pr-loop inspect --root . --pr-id PR-113` reported `source: local_non_runtime_fixture`, `fixture_status: present`, `runtime_authority: none`, and `mutation: none`.
- `factory pr-loop gate-check --root . --pr-id PR-113` reported `gate_status: fail`, `runtime_authority: none`, `merge_authority: none`, `decision_authority: none`, `mutation: none`, and a read-only note that the evaluation is not merge authority, approval authority, or runtime gate evidence.
- `factory pr-loop render-review --root . --pr-id PR-113` rendered a review packet draft only and stated `runtime_authority: none`, `merge_authority: none`, `approval_authority: none`, `mutation: none`, and `fixture_scope: local inert fixture only`.
- `factory pr-loop merge --root . --pr-id PR-113 --dry-run` rendered a merge dry-run summary only and stated `runtime_authority: none`, `merge_authority: none`, `approval_authority: none`, and `mutation: none`.
- No live `artifacts/pr_loop` runtime state exists in the checked repo. The top-level `artifacts` directory was absent during this refresh.
- No current PR Loop code implements live artifact load/save, state authority, phase-machine authority, policy authority, merge apply, queue input, status input, approval authority, or official pack automation.

## why this is an in-repo subsystem, not a new repo
- The runner is about enforcing approval-factory's own approval-first PR execution discipline, so its policy boundary should live next to the repo-local contracts and evidence artifacts it will eventually inspect.
- Keeping it in this repo lets future implementation reuse existing source-of-truth ordering: repo code, tests, git history, runtime artifacts, then official repo docs.
- A separate repo would add orchestration and synchronization before the minimal contract is approved, increasing the risk of policy drift between runner behavior and approval-factory semantics.
- The new subsystem must remain isolated from the hot path. In-repo placement does not mean it may mutate current runtime semantics, approval queue semantics, or execution gates.

## why proposal first
- The runner would sit near merge decisions and PR review gates, so implementation before an approved contract would create implicit approval semantics.
- A proposal PR lets reviewer and approver roles evaluate the boundary before any runtime code can interpret reviews, status, or artifacts as merge authority.
- The proposal separates current facts from future design so later PRs cannot cite unimplemented behavior as already available.
- The proposal also creates an evidence target for later implementation PRs: they must prove conformance to this contract rather than introducing behavior opportunistically.
- This refresh is required because the proposal now has landed fixture-backed commands to account for. Future work must not cite PR-113 through PR-117 as evidence that live runtime state, policy authority, or merge apply already exists.

## proposed four-layer structure
- Policy: human-approved rules for eligible PRs, required reviews, required checks, blocked states, exception handling, and explicit non-goals.
- Approved policy: future human-approved policy artifact for this subsystem. Its source location and authority boundary are TBD and must be defined in a later proposal or implementation prerequisite before runtime code reads it.
- Runtime State: deterministic repo-local state such as `state.yaml`, phase, observed PR metadata, review state, check state, and artifact paths.
- LLM Rendering: optional prompt/input/output rendering for summary, reviewer packet, or operator-facing text. This layer must not make merge decisions.
- Deterministic Gate: non-LLM evaluator that decides whether the runner may propose or execute a merge step based only on approved policy and runtime state.

The landed PR-113 through PR-117 surface does not implement this four-layer structure as runtime authority. It only exercises local fixture examples and fixture-derived summaries with explicit `none` authority fields.

## proposed `state.yaml` shape

```yaml
runner_id: PR-LOOP-001
target_pr: PR-112
phase: gate_evaluation
policy_source: approved policy artifact for this subsystem (TBD; to be defined before implementation)
runtime_refs:
  repo: approval-factory
  branch: pr/112-propose-pr-loop-runner-minimal-contract
  base: main
observations:
  reviews:
    required: true
    state: pending
  checks:
    required: true
    state: unknown
gate:
  merge_allowed: false
  reason: proposal-only contract, no implementation authority
artifacts:
  root: artifacts/pr_loop/PR-112
```

This is a proposed future artifact shape, not current runtime state. `policy_source` is intentionally not a `docs/prs` path; `docs/prs` remains PR history/audit surface and is not proposed here as a future policy source of truth.

## proposed artifact layout

```text
artifacts/pr_loop/<PR-ID>/
  state.yaml
  policy-snapshot.md
  observations/
    pr-metadata.yaml
    reviews.yaml
    checks.yaml
    docs-sync.yaml
  rendering/
    review-packet.md
    operator-summary.md
  gates/
    merge-gate.yaml
    blocked-reasons.md
  evidence/
    commands.md
    diff-summary.md
```

The layout is scoped to future runner artifacts only. It must not replace `runs/latest`, `approval_queue`, `prs/active`, or `prs/archive`.

PR-SLOT-2 may add inert schemas and fixture examples for this layout under a non-runtime location such as `tests/fixtures/pr_loop/...`. Those fixtures must not be treated as live `artifacts/pr_loop/<PR-ID>/...` runtime state, approved policy, gate evidence, queue input, status input, or merge authority.

PR-113 landed this fixture lane. It remains non-runtime and non-authoritative.

## proposed FSM phases
- `initialized`
- `policy_loaded`
- `state_collected`
- `review_packet_rendered`
- `awaiting_review`
- `gate_evaluation`
- `blocked`
- `merge_ready`
- `merge_requested`
- `merged`
- `aborted`

The phase list is a proposal. It does not change current run state names or approval queue lifecycle.

## proposed CLI draft
Landed read-only fixture lane:
- `factory pr-loop inspect --root . --pr-id PR-<number>`
- `factory pr-loop gate-check --root . --pr-id PR-<number>`
- `factory pr-loop render-review --root . --pr-id PR-<number>`
- `factory pr-loop merge --root . --pr-id PR-<number> --dry-run`

These commands require an explicit canonical `PR-<number>` id and refuse non-canonical selectors such as `latest`, `current`, `PR-1A`, or `PR-1-FOO`. They read local non-runtime fixtures only. They do not read or write live `artifacts/pr_loop`, mutate queues, change status, approve reviews, create policy authority, create gate evidence, or perform merge apply.

Unimplemented future live/runtime candidates, all approval required before implementation:
- `factory pr-loop init --pr-id <PR-ID>` or any equivalent live artifact initializer.
- Any live `factory pr-loop inspect` mode that reads `artifacts/pr_loop/<PR-ID>`.
- Any live `factory pr-loop gate-check` mode that evaluates approved policy against runtime state.
- Any review packet renderer that reads live runtime state or emits official evidence.
- Any merge request or merge apply mode.
- Any abort, phase transition, state-store, or policy loading command.

Future implementation must keep inspect/status/trace/debug/readiness-style commands read-only unless the command name, approved design, and tests explicitly authorize mutation. PR-117 is not merge apply; it is a required-`--dry-run` fixture summary with no apply mode available.

## proposed merge gate required conditions
- Target PR id and branch are explicit. No implicit latest PR selector.
- Required human review state is satisfied according to approved policy.
- Required CI/check state is satisfied according to approved policy.
- Docs sync handling is not yet a deterministic gate contract. A future policy layer must define when docs sync is required, when proposal-only PRs are not applicable, and what evidence is sufficient.
- No unresolved blocking reviewer finding is present.
- No failed test/check is ignored without explicit exception approval.
- No approval, queue, or hot path runtime semantic change is inferred from visibility-only status or inspect output.
- `factory status`, `inspect-approval-queue`, `inspect-*`, readiness, status, trace, and debug outputs are not PR Loop decision inputs.
- LLM-rendered text is not used as a decision input. It may only summarize source evidence for human review.
- Deterministic gate evidence is written before merge is proposed or executed.
- The current fixture-backed `gate-check` and `merge --dry-run` outputs are not deterministic runtime gate evidence. They are only read-only summaries of inert fixtures.

## PR-SLOT roadmap
- PR-SLOT-1 landed as the original proposal-only contract.
- PR-SLOT-2 landed as inert fixture examples under `tests/fixtures/pr_loop/...`; this did not introduce state runtime core or runtime authority.
- PR-SLOT-3 landed as read-only fixture inspect over explicit PR id.
- PR-SLOT-4 landed as fixture-backed read-only gate-check summary; this did not introduce live deterministic gate evidence or merge authority.
- PR-SLOT-5 landed as fixture-backed review packet draft rendering; this did not introduce review verdict, approval authority, or LLM decision input.
- PR-SLOT-6 landed only as fixture-backed `merge --dry-run` summary; this did not introduce merge request, merge apply, or merge authority.

Next roadmap boundary:
- Before any State Runtime Core implementation, a separate proposal/ADR decision must define whether PR Loop should have live `artifacts/pr_loop/<PR-ID>` state at all, who may create it, how it relates to existing `runs/latest`, `approval_queue`, and `prs/*`, and what migration/backward-compatibility constraints apply.
- Before any policy-backed gate implementation, a separate approved policy-source contract must define the authoritative policy location, versioning, exception handling, and evidence requirements.
- Before any merge request or merge apply implementation, a separate approved merge-authority contract must define required human review evidence, CI/check evidence, docs sync evidence, failure handling, dry-run-to-apply separation, and explicit non-goals.
- The next implementation must not be assumed to be State Runtime Core by default. The next safe step may be another boundary proposal, ADR, tests-only contract, or documentation refresh if authority questions remain open.

## hot path separation rules
- Do not change current approval queue placement, resolution, or hygiene semantics.
- Do not change current run state machine semantics under `runs/latest`.
- Do not change active/archive PR plan semantics.
- Do not treat `factory status`, `inspect-approval-queue`, readiness, trace, or debug output as merge decision input.
- Do not treat PR Loop `inspect`, `gate-check`, `render-review`, or `merge --dry-run` fixture output as live runtime state, approved policy, review verdict, deterministic gate evidence, approval authority, or merge authority.
- Do not treat `tests/fixtures/pr_loop/...` as live `artifacts/pr_loop`.
- Do not introduce review-skipping auto-merge.
- Do not automate official pack updates in this subsystem proposal.
- Do not orchestrate external repos from this proposal.

## risks
- If future implementation treats LLM rendering as a decision layer, the runner would violate approval-first operation.
- If future implementation uses implicit selectors such as latest PR, latest run, stale queue item, or current branch, it may merge or block the wrong target.
- If in-repo placement is misread as permission to share hot path state, the proposal could create accidental runtime coupling.
- If the landed fixture lane is overread as live runtime authority, reviewers may approve State Runtime Core, policy-backed gates, or merge apply without a clear prerequisite decision.
- If PR-117 is described as merge apply instead of merge dry-run summary, it could create a false authorization path for mutation.
- If inspect/readiness/status/trace/debug output is treated as a decision input, visibility surfaces could drift into unapproved control-plane behavior.
- If proposal wording drifts into future-fact language, reviewers may approve behavior that has not been implemented or validated.

## next required gate
- Reviewer: verify that this proposal refresh does not alter runtime code, CLI semantics, hot path semantics, approval semantics, queue mutation semantics, fixture command behavior, or current inspect/status meaning.
- Approver / PM: approve or reject the refreshed authority boundary before any live runtime, state core, policy-backed gate, or merge apply implementation PR starts.
- Architect: decide whether an ADR is required before live `artifacts/pr_loop`, state authority, policy authority, merge authority, or phase-machine behavior is proposed. The landed fixture lane alone does not settle those architectural decisions.
