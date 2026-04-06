# PR-096 Plan

## Input Refs
- AGENTS.md working-copy version observed on 2026-04-06
- User task for `pr/096-packet-automation-scope-proposal`
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline --decorate -10`
- `test -f AGENTS.md && echo present || echo missing`
- [README.md](/README.md)
- [docs/ops/how-we-work.md](/docs/ops/how-we-work.md)
- [docs/ops/runbook.md](/docs/ops/runbook.md)
- [docs/contracts/evidence-bundle-contract.md](/docs/contracts/evidence-bundle-contract.md)
- [docs/contracts/approval-request-contract.md](/docs/contracts/approval-request-contract.md)
- [docs/contracts/status-contract.md](/docs/contracts/status-contract.md)
- [docs/design/architecture.md](/docs/design/architecture.md)
- [docs/prs/PR-089/plan.md](/docs/prs/PR-089/plan.md)
- [docs/prs/PR-090/plan.md](/docs/prs/PR-090/plan.md)
- [docs/prs/PR-091/plan.md](/docs/prs/PR-091/plan.md)
- [docs/prs/PR-092/plan.md](/docs/prs/PR-092/plan.md)
- [docs/prs/PR-093/plan.md](/docs/prs/PR-093/plan.md)

## Scope
- Proposal-only boundary for the next smallest safe execution / approval packet automation assistance slice.
- Keep Manual Guided PR Mode intact.
- Keep factory core self-update lane separate from product-lane automation.
- Do not implement runtime automation in this PR.
- Do not change code, tests, CLI behavior, runtime contracts, or queue semantics in this PR.

## Output Summary
- Propose a draft-only approval packet prep artifact as the next smallest safe automation slice.
- Keep the slice strictly operator assistance, not decision automation.
- Keep canonical approval artifacts unchanged: `build-approval` remains the only path that creates `evidence-bundle.yaml`, `approval-request.yaml`, and pending queue items.
- Freeze non-goals and guardrails so later implementation cannot drift into selector expansion, approval automation, status/inspect expansion, or product-lane workflow logic.

## Risks
- If the later implementation drifts from draft-only assistance into canonical packet generation, operators could confuse preflight help with approval semantics.
- If the later implementation emits recommendation wording or auto-target behavior, it could weaken the read-only / human-decision boundary already hardened for inspect surfaces.
- If the slice is attached to `status`, `inspect-*`, `readiness`, or `next-step` semantics, the repo could reintroduce decision-surface ambiguity that current docs explicitly forbid.

## Next Required Gate
- Reviewer: confirm the proposal stays proposal-only and keeps the slice artifact-only, manual-guided, and non-decision.
- Approver / PM: approve whether a later implementation PR may introduce the proposed draft-only packet-prep surface.
- Implementer: defer all command, artifact, and test changes to a later implementation PR after this boundary is approved.

## Title
- Draft-Only Approval Packet Prep Assistance Proposal

## Why now
- The repo already automates canonical approval packet creation only at `build-approval` time, after review, QA, docs sync, and verification have been explicitly recorded.
- The repo also already distinguishes read-only visibility surfaces from control behavior, and recent PRs hardened that boundary for inspect-style surfaces and next-step wording.
- The next safe step is therefore not more decision logic. It is a narrow assistance layer that helps an operator prepare and review the approval packet inputs before `build-approval`, without changing what counts as ready, what gets queued, or what an approver decides.
- Proposal-first is required because this slice touches execution-to-approval handoff meaning inside factory core. Without a frozen contract first, a later implementation could be overread as packet generation, readiness signaling, or approval guidance.

## Current boundary
- Manual Guided PR Mode is still the governing model for factory core execution and approval flow.
- `build-approval` is the canonical runtime path that regenerates evidence, recalculates gate state, writes `evidence-bundle.yaml` and `approval-request.yaml`, and conditionally writes `approval_queue/pending/APR-<run-id>.yaml`.
- `inspect-approval`, `inspect-run`, `status`, `trace-lineage`, `readiness`, and `inspect-orchestration` are read-only operator visibility only. They are not decision surfaces, not selectors, and not approval automation.
- `docs/prs/` remains history/audit material, not runtime source of truth.
- Approval decisions, queue lifecycle changes, readiness meaning, and next-step semantics are already bounded and must stay unchanged.

## Proposed smallest safe slice
- Add a later implementation PR for one new draft-only operator assistance surface: deterministic approval packet prep drafting for one exact run.
- The draft must read only official repo/runtime artifacts for that exact run, such as `run.yaml`, role reports, current gate artifact if present, PR plan linkage, work item linkage, and any already-existing approval artifacts if present.
- The draft must produce a non-canonical prep artifact that summarizes packet inputs and obvious gaps for operator review before `build-approval`.
- The draft must not create, modify, overwrite, or repair canonical approval artifacts.
- The draft must not place anything in `approval_queue/`.
- The draft must not replace `build-approval`, `gate-check`, `record-*`, or approver review.
- Exact anchor must stay exact-anchor-only for one run. No latest-derived fallback, queue-derived target selection, stale/latest heuristic target choice, or selector expansion is approved by this proposal.
- The draft may include bounded operator hints, but only as non-decision manual prep guidance tied to exact observed artifact presence/absence. It must not express approval advice, readiness advice, merge advice, or queue action advice.

## Operator assistance vs decision automation
- Operator assistance allowed by this proposal:
- deterministic summary of exact-run packet inputs already present
- deterministic visibility of missing or placeholder prerequisites already present in official artifacts
- deterministic grouping of review, QA, docs sync, verification, gate, and approval-packet input references for manual review
- neutral manual-prep wording such as `operator review required` or `approval packet not yet built`
- Decision automation explicitly not allowed by this proposal:
- no approval recommendation
- no readiness or gate reinterpretation
- no queue eligibility decision
- no auto-selection of target run
- no auto-run of `record-*`, `gate-check`, `build-approval`, or `resolve-approval`
- no selector broadening from exact run to latest, stale, matching, inferred, or relation-summary-derived targets

## Explicit non-goals
- No runtime automation in this PR.
- No implementation of the draft surface in this PR.
- No changes to `factory status`, `inspect-approval`, `inspect-run`, `inspect-orchestration`, `trace-lineage`, `work-item-readiness`, or `inspect-approval-queue` semantics in this PR.
- No approval decision automation.
- No selector expansion.
- No packet auto-repair, auto-fill, auto-build, auto-queue, auto-resolve, auto-approve, or auto-reject behavior.
- No mixing of factory core self-update lane with product-lane execution or delivery workflow.
- No reinterpretation of readiness, status, inspect, approval queue, or next-step as control-plane signals.
- No change to canonical packet structure meaning unless a later implementation PR is separately approved and kept within this proposal boundary.

## Guardrails
- The later implementation must be draft-only and non-canonical.
- Canonical output remains the existing `build-approval` path only.
- Any draft output must be clearly labeled as operator prep assistance only.
- Any draft output must use official repo/runtime artifacts only and must not elevate `docs/prs` history notes or user-pasted logs over primary artifacts.
- Any missing or degraded source artifact must remain a visibility note, not a synthetic repair or inferred decision.
- If an exact-run anchor cannot be resolved safely, the surface must stop at explicit incompleteness and `operator decision required`.
- `status`, `inspect-*`, `readiness`, `approval queue`, and `next-step` semantics must remain unchanged by the later implementation.
- Any wording that sounds like `ready to approve`, `recommended decision`, `selected run`, `should queue now`, or `next PR to run` is out of bounds.

## Acceptance criteria for follow-up implementation
- A later implementation PR introduces only one draft-only approval packet prep surface for one exact run.
- The implementation reads only official repo/runtime artifacts for that exact run and does not depend on `docs/prs` history docs as packet truth.
- The implementation creates only non-canonical prep output and does not modify `evidence-bundle.yaml`, `approval-request.yaml`, pending queue items, or approval decisions.
- The implementation preserves Manual Guided PR Mode: operators still run `record-*`, `gate-check`, `build-approval`, and `resolve-approval` manually.
- The implementation preserves existing semantics for `status`, `inspect-approval`, `inspect-run`, `inspect-orchestration`, `trace-lineage`, `work-item-readiness`, `inspect-approval-queue`, readiness visibility, and next-step assist.
- The implementation does not introduce target inference beyond one exact run anchor.
- The implementation uses wording that is explicitly operator-assistance-only and non-decision.
- Tests, help, and docs added in the implementation PR must reject recommendation, gating, selector, queue-action, or approval-decision interpretations.
- Closeout for the implementation PR must include direct repo-run evidence that canonical approval artifacts and queue semantics remain unchanged unless `build-approval` or `resolve-approval` is explicitly invoked.

## What remains manual
- Choosing the target run to inspect or prepare.
- Deciding whether prerequisite evidence is sufficient.
- Running missing `record-*` commands.
- Running `gate-check`.
- Running `build-approval`.
- Reviewing canonical `evidence-bundle.yaml` and `approval-request.yaml`.
- Making the final approval decision and recording it with `resolve-approval`.

## Validation notes
- Baseline repo evidence for this proposal shows no active PR, latest run `RUN-20260327T063724Z` in `approval_pending`, and two pending approval queue items with one stale relation.
- That observed state reinforces the need to keep queue visibility and packet assistance separate: stale/latest visibility exists, but it must not become target selection or decision automation.
- This PR intentionally adds only [docs/prs/PR-096/plan.md](/docs/prs/PR-096/plan.md).
- Any later implementation PR must collect fresh primary evidence from repo commands directly rather than relying on this proposal note.
