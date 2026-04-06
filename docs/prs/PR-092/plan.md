# PR-092 Plan

## Input Refs
- AGENTS.md working-copy version observed on 2026-04-05
- User task for `pr/092-orchestration-degraded-boundary-proposal`
- [docs/prs/PR-089/plan.md](/docs/prs/PR-089/plan.md)
- [docs/prs/PR-090/plan.md](/docs/prs/PR-090/plan.md)
- [docs/prs/PR-091/plan.md](/docs/prs/PR-091/plan.md)
- Repo source-of-truth reviewed from `orchestrator/cli.py`, `tests/test_cli.py`, and current branch state

## Scope
- Proposal-only corrective PR for the already-introduced `inspect-orchestration` semantics gap.
- Freeze the minimum corrective contract only.
- No runtime implementation in this PR.
- No changes to commands, parser, help, README, tests, pack files, or runtime semantics in this PR beyond documenting the corrective boundary for later implementation.

## Output Summary
- Record that this PR is a corrective proposal, not a new feature proposal.
- Freeze that `inspect-orchestration` remains a dedicated inspect-style read-only surface with exact anchor only and official artifact summary only unchanged.
- Freeze that degraded or incomplete conditions suppress next-step assist the same way ambiguity already should.
- Split follow-up so implementation and tests happen later in PR-093 only.

## Risks
- Until PR-093 implements this correction, current runtime behavior can still emit `possible next manual step` in degraded or incomplete conditions.
- Future edits could widen the corrective issue into broader next-step, anchor, or status semantics unless this proposal remains narrow.

## Next Required Gate
- Reviewer: confirm this stays proposal-only and freezes only the corrective boundary.
- Approver / PM: approve the corrective minimum contract and PR-093 follow-up split.
- Implementer: defer all runtime and test changes to PR-093.

## Title
- Corrective Proposal for Degraded / Incomplete Next-Step Boundary in Inspect-Orchestration

## Problem / background
- PR-090 established `inspect-orchestration` as a dedicated inspect-style read-only surface with exact anchor only and official artifact summary only.
- That approved boundary allowed limited operator-hint text as `possible next manual step` only when the path is single and obvious.
- Repo review on the current branch shows a semantics gap: current next-step gating is tied to not-ambiguity and anchor presence, which can still permit next-step output while the state remains degraded or incomplete.
- That outcome overstates certainty and breaks the approved operator-hint / ambiguity boundary.

## Observed semantics gap
- The current boundary is too narrow if it suppresses next-step assist only for ambiguity while allowing it for degraded or incomplete states.
- Exact anchor existence by itself is not enough to justify `possible next manual step`.
- Linked official artifacts can still be unreadable, partial, stale, or otherwise degraded even when an exact anchor resolves.
- In those cases the surface must stay read-only operator visibility only and keep `human decision required` explicit instead of implying a safe single-path hint.

## Corrective meaning
- This PR is corrective only. It does not propose a new surface, new anchor, new assist behavior, or broader semantics.
- `inspect-orchestration` remains a dedicated inspect-style read-only surface.
- Exact anchor remains `--work-item-id <WI-...>` only.
- Official artifact summary only remains unchanged.
- The corrective meaning is that degraded and incomplete conditions belong on the same suppression side of the boundary as ambiguity for next-step assist.

## Minimum contract
- This is a corrective PR, not a new feature proposal.
- `inspect-orchestration` remains a dedicated inspect-style read-only surface.
- `read-only operator visibility only` remains the governing meaning.
- `exact anchor only` remains `--work-item-id <WI-...>`.
- `official artifact summary only` remains unchanged.
- `human decision required` remains explicit whenever ambiguity, incomplete state, or degraded state prevents a safe hint.
- `degraded/incomplete state suppresses next-step assist`.
- `possible next manual step` appears only when the exact anchor and linked official artifacts remain non-degraded and single-path.
- This PR does not approve any broader next-step logic, anchor widening, status expansion, or semantics expansion.
- Master prompt, delta prompt, and start prompt updates remain out of scope until this corrective issue is fixed in a later implementation PR.

## Non-goals / forbidden scope
- No runtime behavior change in PR-092.
- No command, parser, help, README, or test changes in PR-092.
- No pack refresh in PR-092.
- No broadened next-step logic beyond the corrective minimum contract.
- No anchor widening beyond exact `--work-item-id <WI-...>`.
- No status expansion, readiness expansion, lifecycle expansion, approval expansion, or queue semantics expansion.
- No recommendation wording such as `recommended action`, `approved path`, `ready to proceed`, `next PR to run`, or `should resolve now`.
- No master prompt, delta prompt, or start prompt updates in this PR.

## Suppression rule for next-step assist
- `possible next manual step` must be suppressed whenever any ambiguity note is present.
- `possible next manual step` must be suppressed whenever any incomplete state note is present.
- `possible next manual step` must be suppressed whenever any degraded note is present.
- Next-step assist is allowed only when the exact anchor resolves without degraded anchor-state.
- Next-step assist is allowed only when linked official artifacts are readable enough to avoid degraded or incomplete ambiguity.
- Next-step assist is allowed only when the path is single and obvious.
- If any of those conditions fail, the safe output remains read-only visibility plus explicit `human decision required`.

## Safe wording / unsafe wording

### Safe wording
- `read-only operator visibility only`
- `exact anchor only`
- `official artifact summary only`
- `human decision required`
- `degraded/incomplete state suppresses next-step assist`
- `possible next manual step appears only when the exact anchor and linked official artifacts remain non-degraded and single-path`
- `linked official artifacts are not readable enough to support a safe hint`

### Unsafe wording
- `ready to proceed`
- `recommended action`
- `approved path`
- `next PR to run`
- `should resolve now`

## Validation criteria
- Proposal text must state that this is a corrective PR, not a new feature proposal.
- Proposal text must preserve `inspect-orchestration` as a dedicated inspect-style read-only surface.
- Proposal text must preserve `exact anchor only` as `--work-item-id <WI-...>`.
- Proposal text must preserve `official artifact summary only` unchanged.
- Proposal text must require suppression of `possible next manual step` when any ambiguity note, incomplete state note, or degraded note is present.
- Proposal text must allow next-step assist only when the exact anchor resolves without degraded anchor-state, linked official artifacts are readable enough to avoid degraded or incomplete ambiguity, and the path is single and obvious.
- Proposal text must preserve explicit `human decision required` whenever ambiguity, incomplete, or degraded conditions prevent a safe hint.
- Proposal text must explicitly forbid broader next-step logic, anchor widening, status expansion, semantics expansion, and prompt updates in this PR.
- Closeout validation for PR-092 is docs-only: `git status --short`, `git --no-pager diff --stat`, and `git --no-pager diff --name-only` should show only this proposal document.

## Follow-up split
- PR-092 = corrective proposal only
- PR-093 = corrective implementation + tests
- Pack refresh happens only after PR-093 merge and validation
