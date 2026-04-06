# PR-089 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-05
- User task for PR-089 proposal-only inspect-style surface boundary
- `git status --short`
- [docs/prs/PR-084/proposal.md](/docs/prs/PR-084/proposal.md)
- [docs/prs/PR-087/proposal.md](/docs/prs/PR-087/proposal.md)
- [docs/prs/PR-088/plan.md](/docs/prs/PR-088/plan.md)

## scope
- Proposal-only contract for a dedicated inspect-style orchestration summary / next-step assist surface.
- No implementation.
- No runtime behavior, command, CLI help/output semantics, lifecycle semantics, readiness semantics, approval semantics, queue semantics, or test change.
- No scope beyond the minimum contract needed to make PR-090 implementation-ready and read-only.

## output summary
- Freeze the meaning of orchestration summary / next-step assist as a read-only inspect-style operator surface only.
- Freeze the exact anchor, source-of-truth, ambiguity, and wording boundaries before any implementation work.
- Split later work into PR-090 for read-only implementation and PR-091 for wording/docs/tests hardening.

## Title
- Dedicated Inspect-Style Orchestration Summary / Next-Step Assist Proposal

## Problem / background
- The repo already distinguishes operator visibility from control behavior. This proposal is needed so an inspect-style summary surface does not get read as factory control, lifecycle state, or approval guidance.
- Without a narrow contract, phrases like orchestration summary or next-step assist can drift into queue expansion, target selection, readiness signaling, or implied human decision outcomes.
- This PR exists to lock the boundary before any read-only implementation work begins.

## Proposed meaning
- Orchestration summary / next-step assist is read-only operator visibility only.
- It is a dedicated inspect-style surface, not a factory status expansion and not a control plane.
- The surface may summarize official artifacts for one exact anchor and may, in narrow cases, show one possible next manual step.
- The surface does not decide, recommend, select, promote, activate, start, approve, resolve, or gate anything.
- Any human decision remains outside the surface and must remain human decision required.

## Minimum contract
- `orchestration summary / next-step assist` is not a control plane.
- It is a dedicated inspect-style surface only, not a `factory status` expansion.
- Initial anchor is exact anchor only: `--work-item-id <WI-...>`.
- The surface reads official artifacts only.
- The surface is read-only operator visibility only and operator hint only.
- Next-step assist may show only one possible next manual step when the path is single and obvious from official artifacts.
- The surface must not recommend or imply human decision outcomes.
- Ambiguous cases must remain ambiguous and be surfaced explicitly.
- The surface must not change lifecycle, readiness, approval, or queue semantics.
- The surface must not introduce auto-selection, auto-promotion, auto-activation, auto-start, auto-build-approval, auto-resolve, or any gating behavior.

## Non-goals / forbidden scope
- No runtime implementation in this PR.
- No new command in this PR.
- No CLI help or output wording change in this PR.
- No factory-wide status expansion.
- No multi-anchor entry such as run id, approval id, latest item, inferred target, or selector-derived target.
- No artifact synthesis from unofficial notes when official artifacts are missing.
- No recommendation text that sounds like approval advice, readiness advice, or queue action advice.
- No lifecycle transition, queue mutation, approval mutation, or operator action execution.
- No automatic target choice, follow-up automation, or hidden gating rule.

## Exact anchor rule
- The only initial anchor approved by this proposal is exact anchor only: `--work-item-id <WI-...>`.
- The surface must resolve from the exact provided work item id and must not infer a target from latest run, pending queue state, relation summary, or any other heuristic.
- If the exact work item id is missing, unresolved, or maps to ambiguous artifact state, the surface must stop at explicit ambiguity and must not fall back to another anchor.

## Official-artifact-only rule
- The surface may summarize official artifact summary only.
- Official inputs are limited to repo/runtime artifacts and official artifacts under `docs/work-items`, `prs/active`, `prs/archive`, `runs`, and `approvals`.
- The surface must not treat docs/prs history notes as primary evidence when an official artifact is absent or unclear.
- If official artifacts do not provide enough information for a summary or possible next manual step, the surface must say so and keep the result incomplete.

## Ambiguity handling rule
- Ambiguous cases must remain ambiguous and be surfaced explicitly.
- If multiple next manual paths exist, the surface must not pick one and must not present a preferred outcome.
- If official artifacts disagree, are stale, or are incomplete, the surface must report the ambiguity rather than normalize it away.
- In ambiguous cases, the safe outcome is `human decision required`.

## Wording guidance

### safe wording examples
- `read-only operator visibility only`
- `exact anchor only`
- `official artifact summary only`
- `possible next manual step`
- `human decision required`
- `official artifacts do not show a single obvious next manual step`
- `ambiguous state surfaced explicitly`

### unsafe wording examples
- `ready to proceed`
- `blocked until resolved`
- `selected target`
- `next PR to run`
- `should resolve now`
- `pending cleanup`
- `recommended action`
- `best next step`
- `approved path`

## Validation criteria
- Proposal text must state that the surface is read-only operator visibility only and not a control plane.
- Proposal text must state that the surface is dedicated inspect-style visibility only and not a `factory status` expansion.
- Proposal text must lock exact anchor only to `--work-item-id <WI-...>`.
- Proposal text must lock official artifact summary only and reject unofficial fallback behavior.
- Proposal text must state that only a possible next manual step may be shown, and only when the path is single and obvious.
- Proposal text must explicitly preserve ambiguity and require `human decision required` in ambiguous cases.
- Proposal text must explicitly forbid lifecycle, readiness, approval, queue, automation, and gating semantics drift.
- Closeout validation for this PR is docs-only: `git status --short`, `git --no-pager diff --stat`, and `git --no-pager diff --name-only` should show only this proposal document.

## Follow-up split
- PR-090 = read-only implementation
- PR-090 must implement only the approved inspect-style read-only surface for exact work-item anchoring and official artifact summary only.
- PR-091 = wording/docs/tests hardening
- PR-091 must harden wording, docs, and tests so the surface remains operator-hint-only and does not drift into decision or control semantics.

## risks
- If later implementation leaks beyond exact work-item anchoring, the surface will look like target selection or status expansion.
- If wording drifts toward recommendation language, operators may misread hint text as approval or readiness guidance.
- If unofficial notes are allowed to fill gaps, the surface can imply false certainty instead of explicit ambiguity.

## next required gate
- Reviewer: confirm the proposal stays proposal-only and locks the inspect-style read-only boundary without approving new behavior.
- Approver / PM: approve the narrow contract for PR-090 and PR-091 split.
- Docs Sync / Release: confirm no additional docs sync is required beyond this PR-local proposal contract.
