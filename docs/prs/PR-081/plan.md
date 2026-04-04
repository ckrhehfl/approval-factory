# PR-081 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-05
- User task for PR-081 Stage 2 dry-run support
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- [orchestrator/cli.py](/mnt/c/dev/approval-factory/orchestrator/cli.py)
- [orchestrator/pipeline.py](/mnt/c/dev/approval-factory/orchestrator/pipeline.py)
- [tests/test_cli.py](/mnt/c/dev/approval-factory/tests/test_cli.py)
- [docs/prs/PR-080/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-080/plan.md)

## scope
- Add Stage 2 dry-run support for `factory hygiene-approval-queue`.
- Reuse the existing PR-080 exact selector parser without broadening selector semantics.
- Require explicit `--dry-run` and resolve exactly one pending queue artifact from `--run-id` or `--approval-id`.
- Keep stale/latest visibility and relation summaries read-only; do not add mutation, apply, or cleanup behavior.

## output summary
- Upgrade the CLI help and execution path from parser-only to dry-run preview only.
- Resolve a single exact pending queue target and print a target-local preview with no queue mutation.
- Refuse missing `--dry-run`, missing selector, dual selectors, malformed selectors, heuristic selectors, no-match cases, and ambiguous multiple matches.
- Add focused CLI tests for Stage 2 dry-run acceptance and no-mutation behavior.

## risks
- Retry-suffixed pending artifacts can create ambiguous selector resolution; this PR refuses those cases instead of guessing.
- Future apply or cleanup work must not reuse this dry-run path as implicit authorization for mutation.

## next required gate
- Reviewer: confirm selector validation is still delegated to the PR-080 parser and that no mutation path was introduced.
- QA: verify exact-target dry-run preview works for both selector families and that temp-root contents remain unchanged.
- Docs Sync / Release: confirm this PR-local note is sufficient because broader queue/operator semantics remain unchanged.
