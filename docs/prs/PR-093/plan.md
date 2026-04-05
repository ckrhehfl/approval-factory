# PR-093 Plan

## Input Refs
- AGENTS.md working-copy version observed on 2026-04-06
- User task for `pr/093-orchestration-next-step-suppression-fix`
- [docs/prs/PR-092/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-092/plan.md)
- [orchestrator/pipeline.py](/mnt/c/dev/approval-factory/orchestrator/pipeline.py)
- [tests/test_cli.py](/mnt/c/dev/approval-factory/tests/test_cli.py)
- Current branch runtime and focused CLI tests reviewed in repo source-of-truth

## Scope
- Narrow corrective runtime fix for `inspect-orchestration` next-step suppression only.
- Focused regression coverage for degraded, incomplete, ambiguous, and safe single-path cases.
- Preserve exact anchor, output shape, wording boundary, and existing `factory status` semantics.
- Do not widen anchors, next-step assist logic, readiness semantics, approval semantics, queue semantics, or selector behavior.

## Output Summary
- Implement the PR-092-approved corrective suppression boundary in runtime code.
- Suppress `possible next manual step` whenever ambiguity/incomplete applies, or degraded state applies to the exact anchor or linked official artifacts for that exact anchor.
- Treat malformed or unreadable PR plan and run artifacts encountered during exact-anchor linkage discovery as blocking whenever they prevent proving whether they belong to that exact anchor.
- Preserve safe next-step output only for exact-anchor, readable-enough, single-obvious-path cases with no remaining degraded/incomplete/ambiguity condition.
- Add regression coverage that locks the corrective boundary without changing the inspect surface contract.

## Risks
- The current linked-artifact scan still treats some unreadable downstream artifacts as degraded notes rather than a separate incomplete classification; this PR preserves that existing semantics split rather than widening it.
- Future edits could still drift wording or widen hint behavior unless the focused CLI coverage remains intact.

## Next Required Gate
- Reviewer: confirm the patch stays limited to next-step suppression and regression locking.
- QA: run the corrective one-shot validation and closeout validation for the touched CLI cases.
- Docs Sync / Release: no broader docs sync expected beyond this PR history note unless wording is later changed elsewhere.

## Title
- Corrective Suppression Boundary for Inspect-Orchestration Next-Step Assist

## Corrective Boundary Implemented
- This PR implements the corrective suppression boundary approved by PR-092.
- `inspect-orchestration` remains a dedicated inspect-style read-only operator hint surface.
- Exact anchor remains `--work-item-id <WI-...>` only.
- Official artifact summary only remains unchanged.
- `possible next manual step` is suppressed whenever ambiguity/incomplete remains present, or degraded state remains on the exact anchor or its linked official artifacts.
- Unreadable or malformed PR plan / run artifacts discovered while proving exact-anchor linkage are treated as blocking when they could conceal linked ambiguity, linked degradation, or linked incompleteness for that exact anchor.
- Unrelated repo-wide scan degradation may remain visible, but it does not suppress a safe exact-anchor next step by itself.
- Safe next-step output is allowed only when the exact anchor resolves safely, linked official artifacts are readable enough, no degraded/incomplete/ambiguity condition remains, and the path is single and obvious.

## Non-goals / Preserved Non-Behaviors
- No `factory status` expansion.
- No anchor widening.
- No broader next-step assist logic.
- No readiness, approval, queue, or selector semantics changes.
- No recommendation, gating, or target-selection behavior.

## Validation Split
- Corrective one-shot validation:
  `pytest -q tests/test_cli.py -k "inspect_orchestration and (degraded or incomplete or ambiguous or success_path or does_not_expand_status_semantics)"`
- Closeout validation:
  `pytest -q tests/test_cli.py -k inspect_orchestration`
