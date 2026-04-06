# PR-103 Plan

## Input Refs
- AGENTS.md working-copy version observed on 2026-04-06
- User task for proposal-only PR-103 trace / logging / debug surface boundary
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline --decorate -10`
- `test -f AGENTS.md && echo present || echo missing`
- [README.md](/mnt/c/dev/approval-factory/README.md)
- [orchestrator/cli.py](/mnt/c/dev/approval-factory/orchestrator/cli.py)
- [orchestrator/pipeline.py](/mnt/c/dev/approval-factory/orchestrator/pipeline.py)
- [tests/test_cli.py](/mnt/c/dev/approval-factory/tests/test_cli.py)
- [docs/prs/PR-089/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-089/plan.md)
- [docs/prs/PR-096/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-096/plan.md)

## Scope
- Proposal-only boundary definition for future trace / logging / debug surfaces in approval-factory.
- Define how trace/debug visibility can exist without changing approval, inspect, queue, readiness, or decision semantics.
- Do not implement runtime features.
- Do not modify existing commands.
- Do not change current semantics.

## Output Summary
- Freeze a safe boundary between operator-visible inspect surfaces and deeper system-level trace/debug surfaces.
- Define candidate surfaces such as `trace-run`, `trace-approval`, and `debug-context` as read-only and non-decision.
- Lock wording, labeling, and separation rules so future implementation cannot turn trace/debug output into approval guidance.

## Risks
- If trace output looks like judgment, operators may treat lineage/debug artifacts as a decision signal.
- If inspect and debug layers are mixed, operator-visible state can be confused with low-level lineage or internal context.
- If degraded or partial trace output is phrased too strongly, it can imply correctness, completeness, or approval readiness that the system does not actually guarantee.

## Next Required Gate
- Reviewer: confirm the proposal remains boundary-definition only and does not authorize runtime behavior drift.
- Approver / PM: approve whether a later implementation may add the proposed trace/debug surfaces under the guardrails below.
- Implementer: defer all command, help, test, and runtime changes to a later implementation PR after this boundary is approved.

## Title
- Safe Boundary Proposal for Trace / Logging / Debug Surfaces

## Problem
- approval-factory already exposes several read-only visibility surfaces such as `status`, `inspect-*`, `inspect-approval-queue`, and `trace-lineage`, but the visibility model is fragmented across operator inspection, lineage tracing, queue inspection, and structured error output.
- The repo currently lacks a clearly named structured trace/debug surface for deeper system-level diagnostics, so future additions risk landing in the wrong place or borrowing semantics from inspect surfaces.
- Without an explicit boundary, trace/debug output can be overread as readiness, approval, queue action, or correctness evidence instead of low-level context.

## Current observed baseline
- `python -m factory status --root .` reports no active PR, latest run `RUN-20260327T063724Z` in `approval_pending`, and approval queue summary facts including two pending items and one stale pending relation.
- `python -m factory inspect-approval-queue --root .` exposes per-item queue visibility with `latest_relation`, matching run linkage, and degraded-readiness context presence without changing queue semantics.
- README already defines `inspect-*` surfaces and `trace-lineage` as read-only visibility only, and recent proposal history already protects inspect-style surfaces from drifting into control-plane or decision semantics.
- Recent error UX structure in the repo uses explicit labels such as `[Problem]`, `[Constraint]`, `[Expected location]`, and `[Next step (manual)]`, while tests explicitly reject traceback leakage for assist-only operator flows.

## Goal
- Introduce a future trace/debug surface without affecting decision boundaries.
- Preserve the existing rule that approval, readiness, queue eligibility, target selection, and human decisions remain outside trace/debug output.
- Make it unambiguous that trace/debug exists for lineage and internal context visibility, not for decision support.

## Proposed surfaces
- `trace-run`
  - Read-only run-scoped lineage and event trace for one exact run anchor.
- `trace-approval`
  - Read-only approval-artifact and approval-lifecycle trace for one exact run or exact approval anchor.
- `debug-context`
  - Read-only low-level context dump for human debugging of system state, degraded linkage, or parser/shape mismatches.

## Strict boundaries
- trace is read-only.
- trace is NOT decision input.
- trace does NOT affect approval.
- trace does NOT imply correctness.
- trace/debug output must not mutate artifacts, trigger commands, repair state, or recalculate approval/readiness meaning.
- trace/debug output must not choose a target, prefer a path, or rank outcomes.

## Relationship with inspect
- `inspect` = operator-visible state.
- `trace` = system-level lineage/debug.
- `inspect` should remain the surface for concise operator-facing artifact visibility that is safe to read during normal workflow.
- `trace` should remain a deeper diagnostic surface for linked lineage, internal context, and degraded-path explanation.
- `trace` must not become an expanded `inspect` surface, and `inspect` must not become a thin wrapper around raw debug output.

## Risk
- The main risk is semantic drift where trace output starts to look like approval reasoning, gating logic, or queue hygiene advice.
- A second risk is layer collapse: if inspect and trace are mixed, users may no longer know whether a field is operator-visible state or low-level debug context.
- A third risk is false confidence: trace often reflects raw or partial lineage, so presenting it without explicit caution can make incomplete data look authoritative.

## Non-goals
- No automatic diagnosis.
- No recommendations.
- No decision hints.
- No approval advice.
- No readiness advice.
- No queue action advice.
- No selector expansion from exact anchors to inferred or latest-derived targets unless separately approved.
- No replacement of existing `inspect-*`, `status`, or `trace-lineage` semantics in this proposal.

## Guardrails
- Wording rules:
  - Use neutral labels such as `trace-only`, `debug-only`, `lineage`, `raw context`, `degraded linkage`, and `human decision required`.
  - Do not use phrases such as `ready`, `correct`, `recommended`, `should approve`, `should resolve`, `selected target`, or `best next step`.
- Output labeling:
  - Every future trace surface must be explicitly labeled `trace-only`.
  - Every future debug surface must be explicitly labeled `debug-only`.
  - Labels must appear in help text and runtime output so the surface cannot be mistaken for inspect or approval state.
- Separation from inspect:
  - Do not add trace/debug fields into existing `inspect-*` output by default.
  - Do not surface debug context inside `status`.
  - Do not reuse inspect headings for trace/debug blocks if that would imply operator-state equivalence.

## Future implementation slice
- The smallest safe future slice is one exact-anchor, read-only trace surface that reuses existing lineage inputs and emits clearly labeled `trace-only` output without touching current commands.
- The safest first increment is likely a dedicated trace command for one exact run that exposes linked lineage detail already derivable from official artifacts, with degraded notes only and no next-step recommendation.
- Any later slice should preserve the current contract that `inspect` remains operator-visible state while trace/debug remains separate and explicitly non-decision.

## Examples
- Good trace output:
  - `Label: trace-only`
  - `Run linkage found from PR-004 to RUN-20260327T063724Z`
  - `Approval request artifact present`
  - `Degraded linkage: readiness context absent`
  - `Human decision required`
- Bad trace output:
  - `This run is ready for approval`
  - `Recommended decision: approve`
  - `Best next step: resolve the stale queue item`
  - `The approval packet is correct`
  - `Use this run as the selected target`

## Why this boundary fits current repo behavior
- README already separates read-only inspect surfaces from lifecycle and approval semantics, and `trace-lineage` is already bounded as read-only lineage visibility only.
- Approval queue visibility is already documented as operator visibility only, not selector or cleanup authority.
- Recent assist-only error UX shows a repo pattern for structured, clearly labeled, non-traceback output; future trace/debug surfaces should follow the same clarity standard without becoming advisory.
- This proposal therefore extends the repo's existing separation model rather than introducing a new control concept.

## Validation notes
- Baseline evidence for this proposal shows current queue visibility and lineage-related surfaces already exist, but they are fragmented across multiple commands and structured error outputs.
- The safe next step is to define a separate trace/debug layer rather than widening `inspect` or reinterpreting approval queue visibility.
- This PR intentionally adds only [docs/prs/PR-103/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-103/plan.md).
