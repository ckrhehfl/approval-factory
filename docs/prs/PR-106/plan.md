# PR-106 Plan

## title
- Safe Boundary Proposal for Run Queue Hardening

## input refs
- AGENTS.md working-copy version observed on 2026-04-06
- User task for PR-106 proposal-only queue hardening boundary
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline --decorate -10`
- `test -f AGENTS.md && echo present || echo missing`
- `git --no-pager diff --stat`
- `git --no-pager diff --name-only`
- `README.md`
- `orchestrator/pipeline.py`
- `orchestrator/cli.py`
- `tests/test_cli.py`
- `docs/work-items/WI-004-run-queue-hardening.md`
- `docs/prs/PR-077/plan.md`
- `docs/prs/PR-085/proposal.md`
- `docs/prs/PR-087/plan.md`
- `docs/prs/PR-088/plan.md`
- `docs/prs/PR-103/plan.md`

## scope
- Proposal-only, docs-only PR slice for WI-004 / latest-vs-stale queue visibility and hygiene boundary.
- Define the safe boundary for later run queue hardening work without changing runtime semantics.
- Ground the proposal in actual current repo state: no active PR, latest run `RUN-20260327T063724Z`, two pending approvals, latest pending mapped to `PR-004`, stale pending mapped to `PR-003`, and clean working tree before this docs change.
- Preserve the current split where `factory status` is a summary visibility surface, `inspect-approval-queue` is an item-level read-only inspection surface, and trace/debug remains separate.

## non-goals
- No runtime implementation.
- No changes to `factory status`, `inspect-approval-queue`, `trace-run`, queue hygiene commands, selectors, or approval lifecycle behavior.
- No changes to tests, templates, CLI help text, queue artifact schema, orchestration flow, or operator wording in code.
- No decision-surface expansion from readiness, latest/stale relation, stale coexistence, queue hygiene metadata, or next-step assist.
- No mixing of factory core self-update lane with product-lane behavior or requirements.

## output summary
- Add this PR-local plan to freeze the proposal scope and evidence base.
- Add `docs/prs/PR-106/proposal.md` to define the semantics-sensitive boundary for future run queue hardening work.
- Keep the allowed future direction narrow: visibility-preserving hardening around queue inspection and hygiene boundaries only.

## risks
- If stale pending coexistence is described imprecisely, later work may treat it as a cleanup command, correctness signal, or selector shortcut.
- If `factory status` grows decision-shaped meaning, queue visibility facts may be misread as approval guidance.
- If inspect and trace/debug are mixed, later hardening work may smuggle deeper diagnostics into operator decision surfaces.
- If a future implementation uses `latest` or `stale` as a selector family, it would change behavior rather than harden visibility.

## validation approach
- Re-run baseline evidence directly from the repo before writing:
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline --decorate -10`
- `test -f AGENTS.md && echo present || echo missing`
- `git --no-pager diff --stat`
- `git --no-pager diff --name-only`
- Read current source-of-truth files that define or render the relevant behavior:
- `README.md`
- `orchestrator/pipeline.py`
- `orchestrator/cli.py`
- `tests/test_cli.py`
- Validate closeout by confirming this PR adds docs only and does not modify runtime code, tests, templates, CLI text, or orchestration behavior.

## next required gate
- Reviewer: confirm the proposal is tightly limited to WI-004 queue visibility and hygiene boundary, with no implied runtime approval.
- Approver / PM: decide whether a later implementation PR may proceed under these exact preserved boundaries.
- Docs Sync / Release: confirm docs sync is satisfied by this PR-local plan and proposal only.
