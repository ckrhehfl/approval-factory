# Proposal: PR Loop Runner / Review-Gated Merge Runner

## input refs
- AGENTS.md working-copy instructions provided for `/mnt/c/dev/approval-factory` on 2026-04-10
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline --decorate -10`
- `test -f AGENTS.md && echo present || echo missing`
- `README.md`
- `docs/prs/README.md`

## scope
- Proposal-only start for a new in-repo subsystem named `PR Loop Runner / Review-Gated Merge Runner`.
- The subsystem proposal covers design boundaries, artifact shape, FSM phases, CLI draft, merge gate conditions, and a PR-SLOT-1 through PR-SLOT-6 roadmap.
- This PR does not implement runtime code, tests, queue mutation, approval semantics, hot path changes, pack automation, or external repo orchestration.

## output summary
- Define why this belongs in the current repo as a new subsystem instead of a separate repo.
- Define why a proposal PR must land before implementation PRs.
- Propose a four-layer architecture: Policy, Runtime State, LLM Rendering, Deterministic Gate.
- Sketch the future state/artifact/CLI/merge-gate contract without treating it as current behavior.
- Keep the proposal isolated from current factory hot path runtime semantics.

## current repo facts
- Baseline on 2026-04-10: `factory status` reported no active PR, latest run `RUN-20260327T063724Z`, state `approval_pending`, pending approval status, `pending_total: 2`, `latest_run_has_pending: True`, and `stale_pending_count: 1`.
- Baseline on 2026-04-10: `factory inspect-approval-queue` reported two pending items. `APR-RUN-20260327T055614Z.yaml` was stale and matched `PR-003`; `APR-RUN-20260327T063724Z.yaml` was latest and matched `PR-004`.
- Baseline git state was `pr/112-propose-pr-loop-runner-minimal-contract`; `AGENTS.md` was present; the latest commit was `23ee24e Merge pull request #107 from ckrhehfl/pr/111-review-packet-assist-corrective`.
- `docs/prs/README.md` states that `docs/prs/` is PR history/audit surface, not active execution input or runtime source of truth.
- This proposal is intentionally stored under `docs/proposals/` so the design proposal is not confused with PR history/audit docs.
- No current fact in this proposal claims that PR Loop Runner code, commands, state files, merge automation, or artifacts already exist.

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

## proposed four-layer structure
- Policy: human-approved rules for eligible PRs, required reviews, required checks, blocked states, exception handling, and explicit non-goals.
- Approved policy: future human-approved policy artifact for this subsystem. Its source location and authority boundary are TBD and must be defined in a later proposal or implementation prerequisite before runtime code reads it.
- Runtime State: deterministic repo-local state such as `state.yaml`, phase, observed PR metadata, review state, check state, and artifact paths.
- LLM Rendering: optional prompt/input/output rendering for summary, reviewer packet, or operator-facing text. This layer must not make merge decisions.
- Deterministic Gate: non-LLM evaluator that decides whether the runner may propose or execute a merge step based only on approved policy and runtime state.

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
- `factory pr-loop init --pr-id <PR-ID>`
- `factory pr-loop inspect --pr-id <PR-ID>`
- `factory pr-loop render-review-packet --pr-id <PR-ID>`
- `factory pr-loop gate-check --pr-id <PR-ID>`
- `factory pr-loop request-merge --pr-id <PR-ID>`
- `factory pr-loop abort --pr-id <PR-ID> --reason <TEXT>`

These commands are not implemented by this PR. Future implementation must keep inspect/status-style commands read-only unless the command name and approved contract explicitly allow mutation.

## proposed merge gate required conditions
- Target PR id and branch are explicit. No implicit latest PR selector.
- Required human review state is satisfied according to approved policy.
- Required CI/check state is satisfied according to approved policy.
- Docs sync handling is not yet a deterministic gate contract. A future policy layer must define when docs sync is required, when proposal-only PRs are not applicable, and what evidence is sufficient.
- No unresolved blocking reviewer finding is present.
- No failed test/check is ignored without explicit exception approval.
- No approval, queue, or hot path runtime semantic change is inferred from visibility-only status or inspect output.
- LLM-rendered text is not used as a decision input. It may only summarize source evidence for human review.
- Deterministic gate evidence is written before merge is proposed or executed.

## PR-SLOT roadmap
- PR-SLOT-1: land this proposal-only contract and review the subsystem boundary.
- PR-SLOT-2: add inert artifact schemas and fixture examples for `artifacts/pr_loop/<PR-ID>/...` under a non-runtime fixture location; this is not state runtime core and does not introduce runtime authority.
- PR-SLOT-3: add read-only inspect command over explicit PR id and local artifact fixtures.
- PR-SLOT-4: add deterministic gate evaluation against fixture-backed state, without merge execution.
- PR-SLOT-5: add optional LLM rendering for review packet text, explicitly excluded from gate decisions.
- PR-SLOT-6: add review-gated merge request or merge execution path only after human approval and evidence requirements are satisfied.

## hot path separation rules
- Do not change current approval queue placement, resolution, or hygiene semantics.
- Do not change current run state machine semantics under `runs/latest`.
- Do not change active/archive PR plan semantics.
- Do not treat `factory status`, `inspect-approval-queue`, readiness, trace, or debug output as merge decision input.
- Do not introduce review-skipping auto-merge.
- Do not automate official pack updates in this subsystem proposal.
- Do not orchestrate external repos from this proposal.

## risks
- If future implementation treats LLM rendering as a decision layer, the runner would violate approval-first operation.
- If future implementation uses implicit selectors such as latest PR, latest run, stale queue item, or current branch, it may merge or block the wrong target.
- If in-repo placement is misread as permission to share hot path state, the proposal could create accidental runtime coupling.
- If proposal wording drifts into current-fact language, reviewers may approve behavior that has not been implemented or validated.

## next required gate
- Reviewer: verify that this proposal does not alter runtime code, hot path semantics, approval semantics, queue mutation semantics, or current inspect/status meaning.
- Approver / PM: approve or reject the in-repo subsystem boundary and PR-SLOT roadmap before any implementation PR starts.
- Architect: decide whether a future ADR is required before PR-SLOT-2, because the proposal introduces a new subsystem boundary even though it does not implement one in this PR.
