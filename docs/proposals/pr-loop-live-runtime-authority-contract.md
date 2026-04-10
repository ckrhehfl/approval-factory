# Proposal: PR Loop Live Runtime Authority Contract

## input refs
- AGENTS.md working-copy instructions provided for `/mnt/c/dev/approval-factory` on 2026-04-11 KST.
- User task for PR-119 proposal-only authority-boundary / ADR-equivalent refresh.
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
- `docs/proposals/README.md`
- `docs/prs/PR-113/plan.md`
- `docs/prs/PR-114/plan.md`
- `docs/prs/PR-115/plan.md`
- `docs/prs/PR-116/plan.md`
- `docs/prs/PR-117/plan.md`

## scope
- Proposal-only PR-119 contract for PR Loop live runtime authority boundaries.
- Defines how future live `artifacts/pr_loop/<PR-ID>` authority must be separated from the current fixture-backed read-only lane, `runs/latest`, `approval_queue`, and `docs/prs`.
- Documents policy authority, state authority, merge authority, dry-run/apply separation, open questions, and prerequisite gates before any implementation.
- Does not implement runtime code, CLI behavior, state core, gate core, merge apply, queue/status/readiness meaning changes, fixture promotion, or official pack updates.

## current landed facts
- Baseline command evidence on 2026-04-11 reported no active PR, latest run `RUN-20260327T063724Z`, state `approval_pending`, pending approval status, `pending_total: 2`, `latest_run_has_pending: True`, and one stale pending approval for `RUN-20260327T055614Z`.
- `inspect-approval-queue` reported two pending approvals: stale `APR-RUN-20260327T055614Z.yaml` for `PR-003` and latest `APR-RUN-20260327T063724Z.yaml` for `PR-004`.
- Git baseline was branch `pr/119-pr-loop-live-runtime-authority-proposal` at `9990784 Merge pull request #114 from ckrhehfl/pr/118-pr-loop-authority-boundary-refresh`, with `AGENTS.md` present.
- The landed PR Loop slice is fixture-backed and read-only:
  - PR-113 added inert fixture examples under `tests/fixtures/pr_loop/...`.
  - PR-114 added fixture-backed `factory pr-loop inspect`.
  - PR-115 added fixture-backed `factory pr-loop gate-check`.
  - PR-116 added fixture-backed review packet draft rendering.
  - PR-117 added fixture-backed `factory pr-loop merge --dry-run`.
- Current PR Loop fixture commands report `source: local_non_runtime_fixture`, `runtime_authority: none`, and `mutation: none`.
- `gate-check` reports no `merge_authority` or `decision_authority`; its output explicitly says it is not merge authority, approval authority, or runtime gate evidence.
- `render-review` emits review drafting input only and reports no runtime, merge, approval, or mutation authority.
- `merge --dry-run` emits a read-only summary only and reports no runtime, gate evidence, approval, merge, or mutation authority.
- The checked repo has no top-level live `artifacts` directory and no live `artifacts/pr_loop/<PR-ID>` runtime state.
- Current PR Loop code does not implement live artifact load/save, state authority, phase-machine authority, policy authority, merge apply, queue input, status input, approval authority, or official pack automation.
- `docs/prs` and continuity docs are audit/reference material, not runtime source of truth.

## rejected options or non-goals
- Do not promote `tests/fixtures/pr_loop/...` into live runtime state.
- Do not treat `runs/latest`, `approval_queue`, `docs/prs`, fixture output, inspect output, readiness/status output, trace output, or debug output as PR Loop decision input.
- Do not make `docs/prs` a policy source of truth.
- Do not add implicit selectors such as latest PR, latest run, current branch, or current queue item.
- Do not add merge apply, git mutation, queue mutation, status mutation, approval mutation, runtime artifact mutation, or official pack mutation in this PR.
- Do not treat LLM-rendered text or review packet drafts as gate evidence or merge authority.
- Do not let a dry-run command share the same authority surface as an apply command.
- Do not change CLI semantics, approval queue semantics, readiness/status meaning, run state semantics, or fixture lane behavior.

## proposed authority model
- Live runtime state: future PR Loop runtime state may use `artifacts/pr_loop/<PR-ID>/` only after a separate implementation gate explicitly creates the state core. PR-119 does not create that path and does not authorize fixture promotion into that path.
- State authority owner: the future PR Loop State Runtime Core is the only proposed owner that may create or mutate `artifacts/pr_loop/<PR-ID>/state.yaml` and related live PR Loop artifacts. Until that core exists, state authority owner is `none`.
- Runtime-state boundary: `artifacts/pr_loop/<PR-ID>` must be a PR Loop-specific runtime namespace. It must not replace or backfill `runs/latest`, `approval_queue`, `docs/prs`, fixture examples, or current hot path run/approval semantics.
- `runs/latest` boundary: `runs/latest` remains the existing run artifact surface for factory runs. PR Loop must not infer merge eligibility or target PR selection from the latest run unless a future approved contract makes that explicit.
- `approval_queue` boundary: `approval_queue` remains approval visibility/workflow state for existing runs. PR Loop must not treat pending or stale queue items as merge approval, gate evidence, target selection, or cleanup authority.
- `docs/prs` boundary: `docs/prs` remains PR history/audit documentation. It may be cited as reference evidence but must not be read as live runtime state or approved policy authority.
- Fixture lane boundary: `tests/fixtures/pr_loop/...` remains local inert test data for read-only summaries. It must not be read by live runtime commands except as tests explicitly exercising fixture behavior.
- Policy source of truth: PR Loop policy authority must come from a separate versioned, human-approved policy artifact defined before implementation. This proposal rejects `docs/prs`, fixtures, queue files, status/readiness output, trace/debug output, and LLM-rendered text as policy authority. The exact policy file path remains an implementation prerequisite; runtime code must not load policy until that path and versioning contract are approved.
- Gate authority: merge gate authority must be deterministic and policy-backed. Current fixture `gate-check` output is not live gate evidence.
- Merge authority: merge apply authority must require explicit human approval evidence, required check evidence, docs sync evidence where applicable, deterministic gate evidence, and a separate apply contract. Current `merge --dry-run` output is not merge authority.
- Dry-run/apply separation: dry-run may summarize what would block or pass, with no mutation. Apply must be a distinct future authority surface with explicit naming, tests, evidence capture, failure handling, and approval gate. A dry-run result must never imply apply permission.
- Inspect/readiness/status/trace/debug boundary: these surfaces are read-only visibility. They may help humans inspect state, but they are not PR Loop decision inputs unless a future approved policy contract explicitly promotes a specific artifact, not transient command text, into evidence.

## open questions
- Should the approved policy artifact live under a new `docs/policies/pr-loop/` area, under an ADR-linked contract, or in another repo-local policy location?
- Which role is allowed to initialize a live `artifacts/pr_loop/<PR-ID>` state directory: Implementer, QA, Approver/PM, or a future runner command after human approval?
- What is the exact schema and versioning rule for `state.yaml`, policy snapshots, observations, gate evidence, and merge evidence?
- How should live PR Loop state reference `runs/latest` and `approval_queue` without importing their visibility state as decision authority?
- What migration or compatibility rule is needed if future runtime state must coexist with landed fixture examples that mirror the proposed path shape?
- What exact human approval evidence is sufficient for merge apply, and how are stale approvals or superseded checks invalidated?
- Is a formal ADR required before the first state core implementation PR, or is an approved prerequisite proposal sufficient?

## prerequisite gates before any implementation
- Architect gate: decide ADR requirement before any live `artifacts/pr_loop/<PR-ID>` state, phase machine, policy authority, deterministic gate authority, or merge authority implementation.
- Approver / PM gate: approve whether live `artifacts/pr_loop/<PR-ID>` should exist at all and which role or command may create it.
- Policy gate: approve the policy source-of-truth path, schema/versioning, exception handling, and evidence requirements before runtime code reads policy.
- State gate: approve the state schema, owner, lifecycle, locking/concurrency expectations, and relationship to `runs/latest`, `approval_queue`, `docs/prs`, and fixtures before state core code writes artifacts.
- Merge gate: approve dry-run/apply separation, required evidence bundle, failure handling, and explicit mutation boundary before merge request or merge apply code exists.
- QA gate: provide tests proving no fixture promotion, no queue/status/readiness meaning change, no implicit selector fallback, and no mutation from read-only surfaces.
- Docs sync gate: update proposal, policy, ADR, and PR docs together whenever implementation changes an authority boundary.

## output summary
- PR-119 fixes a proposal-only live runtime authority contract for PR Loop before implementation.
- The contract keeps current landed behavior as a fixture-backed read-only lane with no runtime, policy, gate, approval, or merge authority.
- The contract proposes future `artifacts/pr_loop/<PR-ID>` as a separate PR Loop runtime namespace only after explicit prerequisite approval.
- The contract requires a separate approved policy source, deterministic gate evidence, and strict dry-run/apply separation before merge authority can exist.

## risks
- If future implementation reads visibility surfaces as decision inputs, PR Loop could bypass approval-first boundaries.
- If fixture examples are promoted into live artifacts, tests could be mistaken for runtime evidence.
- If policy location remains unresolved during implementation, runtime code may accidentally treat docs, queues, status, or rendered text as authority.
- If dry-run and apply are not kept separate, a summary command could become a mutation path without approved evidence.
- If ADR need is skipped, state authority and merge authority may be introduced as incidental code structure instead of reviewed architecture.

## next required gate
- Reviewer: confirm this PR is proposal-only and does not alter runtime code, fixtures, CLI behavior, queue/status/readiness semantics, or official packs.
- Architect: decide ADR requirement for live runtime state, policy authority, phase machine, gate authority, and merge apply.
- Approver / PM: approve or reject the prerequisite authority model before any implementation PR begins.
