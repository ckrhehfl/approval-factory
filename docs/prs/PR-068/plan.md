# PR-068 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- User task for PR-068 read-only visibility assist
- `python -m factory inspect-approval-queue --root .`
- [orchestrator/pipeline.py](/mnt/c/dev/approval-factory/orchestrator/pipeline.py)
- [orchestrator/cli.py](/mnt/c/dev/approval-factory/orchestrator/cli.py)
- [tests/test_cli.py](/mnt/c/dev/approval-factory/tests/test_cli.py)

## scope
- PR-068 is a small read-only visibility assist.
- It improves `inspect-approval-queue` readability only.
- It adds a compact relation summary before the pending item list.
- Relation summary is operator assist, not decision automation.

## output summary
- Add a compact relation summary block for latest, stale, no-latest-run, and unparseable pending relations.
- Keep existing per-item fields, item ordering, status output semantics, and selection logic unchanged.
- Add focused CLI tests for empty, single-latest, and mixed latest-plus-stale output cases.

## contract
- Semantics remain unchanged.
- No auto cleanup.
- No auto resolve.
- No readiness gating.
- No approval or queue semantic change.
- No runtime mutation behavior change.
- No approval queue artifact handling change.

## validation
- Run focused `tests/test_cli.py` coverage for `inspect-approval-queue`.
- Verify empty queue still renders safely.
- Verify one latest pending item reports the expected relation summary counts.
- Verify mixed latest and stale pending items report the expected relation summary counts.
- Keep validation output-focused and narrow to this visibility-only change.
