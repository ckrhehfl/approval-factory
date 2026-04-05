# PR-090 Plan

## Title
- Dedicated Inspect-Orchestration Read-Only Surface

## Scope
- Forward-minimum PR history note for the already-implemented PR-090 boundary.
- Docs-only follow-up that records the implemented behavior without changing runtime code, tests, README, or semantics.
- Scope is limited to the dedicated `inspect-orchestration` read-only surface anchored by exact `--work-item-id`.

## What was implemented
- Added a dedicated `factory inspect-orchestration` inspect-style surface separate from `factory status`.
- Kept the initial anchor exact: `--work-item-id <WI-...>` only.
- Summarized official artifacts linked to that exact work item only.
- Rendered anchor summary, linked official artifact summary, ambiguity or incomplete-state note, and possible next manual step.
- Surfaced ambiguity explicitly rather than collapsing it into a chosen path.
- Retained `human decision required` wording for ambiguous or incomplete cases.
- Emitted `possible next manual step` only in narrow single-path cases where official artifacts show exactly one obvious manual follow-up.
- Added focused CLI coverage for exact-anchor success, no linked downstream artifact, ambiguity preservation, no status expansion, and wording-boundary preservation.

## What was intentionally not implemented
- No `factory status` expansion.
- No widened anchors such as run id, approval id, latest item, inferred target, or selector-derived target.
- No unofficial fallback from docs/prs history notes when official artifacts are missing or unclear.
- No recommendation language that implies approval advice, readiness advice, or queue action advice.
- No lifecycle transition, readiness change, approval change, queue mutation, or operator action execution.
- No automation, gating, auto-selection, target selection, or hidden heuristics.

## Read-Only Guardrails Preserved
- `inspect-orchestration` remains read-only operator visibility only.
- The surface remains official artifact summary only.
- Ambiguous cases remain ambiguous and are surfaced explicitly.
- Human decision points remain human decision required.
- Possible next-step assist remains limited to one possible next manual step only when the path is single and obvious.
- Lifecycle, readiness, approval, and queue semantics remain unchanged.
- Existing `status`, `inspect-work-item`, and other inspect surfaces remain unchanged.

## Validation Summary
- Focused contract-safe validation passed for the new inspect-orchestration help and runtime cases.
- Existing inspect/status boundary validation passed with no `factory status` output drift.
- Full `pytest -q tests/test_cli.py` passed after the implementation.
- This follow-up itself is docs-only and records the already-validated implementation boundary.

## Risks / Follow-Up Note
- The main residual risk is later wording drift that could make the surface sound like recommendation, gating, or target-selection behavior.
- A later follow-up may harden wording further, but any expansion beyond exact work-item anchoring or read-only operator visibility requires separate approval.
