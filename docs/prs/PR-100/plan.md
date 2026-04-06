# PR-100 Plan

## Input Refs
- AGENTS.md working-copy version observed on 2026-04-06
- User task for proposal-only `PR-100` unified operator review flow
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline --decorate -10`
- `test -f AGENTS.md && echo present || echo missing`
- [README.md](/mnt/c/dev/approval-factory/README.md)
- [orchestrator/cli.py](/mnt/c/dev/approval-factory/orchestrator/cli.py)
- [orchestrator/pipeline.py](/mnt/c/dev/approval-factory/orchestrator/pipeline.py)
- [tests/test_cli.py](/mnt/c/dev/approval-factory/tests/test_cli.py)
- [tests/test_pipeline_approval_loop.py](/mnt/c/dev/approval-factory/tests/test_pipeline_approval_loop.py)
- [docs/prs/PR-096/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-096/plan.md)

## Scope
- Proposal only for a unified operator review flow that combines existing approval-draft surfaces.
- Define one future command shape without implementing it in this PR.
- Preserve current semantics for `draft-approval-packet`, `inspect-draft-approval`, and `build-approval`.
- Do not modify runtime code, tests, queue behavior, approval behavior, selector behavior, or CLI help in this PR.

## Output Summary
- Propose a single read-only operator review entrypoint for one exact run: `python -m factory review-approval --run-id <RUN-ID>`.
- Combine three existing assistance surfaces into one review flow: draft existence check, draft inspection output, and the current manual next-step hint toward `build-approval`.
- Freeze explicit assist-only labeling so operators cannot misread the surface as approval, queue control, or automation.
- Limit the future implementation slice to the smallest safe composition of existing behavior without semantic drift.

## Risks
- A combined surface could be misread as a decision engine if the output does not clearly distinguish inspect facts from operator action.
- A combined surface could accidentally widen semantics by silently drafting artifacts, inferring readiness, or suppressing existing inspect failures.
- A future implementation could drift into queue selection or approval guidance unless the proposal fixes the boundary around exact-run, read-only, and no-decision behavior.

## Next Required Gate
- Reviewer: confirm the proposal remains proposal-only and does not reinterpret current approval or inspect semantics.
- Approver / PM: approve whether a later implementation PR may add the unified review surface under the stated guardrails.
- Implementer: if approved later, keep the first implementation PR to composition only with no runtime mutation or semantic expansion.

## Title
- Unified Operator Review Flow for Approval Draft Inspection

## Problem
- The current operator flow is fragmented across separate commands.
- An operator must manually chain `draft-approval-packet`, `inspect-draft-approval`, and the next-step hint implied by `build-approval`.
- That fragmentation adds avoidable command switching even when the operator intent is a single review pass for one exact run.
- The repo already has assist-only pieces, but the review experience is not unified at one entrypoint.

## Goal
- Define a unified review flow for one exact run with no automation.
- Keep the operator in control of every decision and every mutating command.
- Present the existing assist surfaces in one deterministic review output so the operator can inspect the current approval-draft state before deciding whether to run `build-approval`.

## Proposed Command
`python -m factory review-approval --run-id <RUN-ID>`

- Exact selector only.
- No `--latest` fallback.
- No inferred target selection from queue, status, or relation summaries.

## Behavior Breakdown
### 1) Draft Existence Check
- Check whether `runs/draft/APPROVAL-DRAFT-<run-id>.yaml` exists for the exact run.
- If the draft is missing, report that state explicitly and stop before any inspect-style comparison.
- Do not auto-create the draft.
- Do not suppress the missing-draft condition behind a synthetic summary.

### 2) Inspect Output
- If the draft exists, surface the current `inspect-draft-approval` inspection result for the same exact run.
- Preserve the existing section model: `Draft Summary`, `Sanity Check`, `Diff Summary`, `Operator Note`.
- Preserve existing failure conditions when the draft, canonical run artifact, canonical approval artifact, or required fields are missing or malformed.
- Treat the unified command as a composition layer over the inspect surface, not a new interpretation layer.

### 3) Next-Step Hint
- After the inspection block, show the current manual next-step hint toward `python -m factory build-approval --root . --run-id <RUN-ID>`.
- Label the hint as suggestion-only and operator-triggered.
- Keep the hint informational only; it must not imply approval readiness, queue eligibility, or recommended decision.

## Boundaries
- Read-only.
- No mutation.
- No decision.
- No draft creation.
- No canonical artifact creation.
- No approval queue writes.
- No approval resolution.

## Non-goals
- No auto approval.
- No queue changes.
- No selector expansion.
- No implicit fallback to latest run.
- No readiness reinterpretation.
- No rewrite of `inspect-draft-approval` output semantics.
- No replacement of `build-approval` as the canonical approval artifact path.

## Guardrails
- The command must be presented as operator assistance only, never as a decision system.
- The output must explicitly state that approval decisions remain manual.
- The output must not claim that the run is approved, approvable, ready to merge, or ready to queue.
- Existing `inspect-draft-approval` semantics must be preserved verbatim in meaning, including its exact-run requirement and explicit failure behavior.
- Existing `build-approval` semantics must remain unchanged; the unified review flow may only restate its current manual next step.
- If the state is incomplete or ambiguous, the command must report that ambiguity rather than smoothing it into a recommendation.

## UX Design
- Exact output structure should be fixed and labeled.
- The top block should identify the surface and its assist-only boundary.
- The middle block should show draft presence status and, when possible, the unchanged inspect output.
- The bottom block should show the manual next-step hint only as an operator option.

Proposed output structure:

```text
Approval Review Assist:
- run_id: <RUN-ID>
- mode: assist-only
- mutation: none
- decision: operator required

Draft Check
- draft_exists: true|false
- draft_path: runs/draft/APPROVAL-DRAFT-<RUN-ID>.yaml|none
- note: review surface only; no draft was created

Inspect Output
Draft Summary
...

Sanity Check
...

Diff Summary
...

Operator Note
...

Next Step
- manual_hint: suggestion only
- command: python -m factory build-approval --root . --run-id <RUN-ID>
- assist_only: this command did not build approval artifacts or make a decision
```

- `Approval Review Assist` must be the primary framing label.
- `assist-only`, `mutation: none`, and `decision: operator required` must be visible near the top.
- When draft inspection cannot proceed, the output should still preserve the same assist-only framing and then stop with a clear failure.

## Failure Modes
- Missing draft:
  report exact missing draft path and stop; do not auto-create or infer draft content.
- Missing canonical artifact:
  preserve the current explicit inspect failure when `run.yaml` or `approval-request.yaml` is absent.
- Ambiguous state:
  if the unified surface cannot safely represent the current state without implying a decision, it must stop with a clear operator-required message rather than continue with a softened hint.

## Implementation Slice (Future PR)
- Add one new command that orchestrates existing read-only checks for one exact run.
- Reuse existing draft-path resolution and existing `inspect-draft-approval` logic rather than forking semantics.
- Reuse the current manual `build-approval` hint wording or equivalent wording with the same meaning.
- Keep the first implementation PR limited to CLI composition, focused tests, and docs/help updates for the new command only.
- Do not change `draft-approval-packet`, `inspect-draft-approval`, `build-approval`, queue logic, or approval artifacts in that first implementation slice.

## Validation Notes
- Baseline repo evidence on 2026-04-06 shows no active PR, latest run `RUN-20260327T063724Z`, and two pending approval queue items with one stale pending entry.
- That observed state reinforces the proposal boundary: queue visibility exists already, but the unified review surface must not turn that visibility into target selection or approval guidance.
- This PR intentionally adds only [docs/prs/PR-100/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-100/plan.md).
