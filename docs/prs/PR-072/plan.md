# PR-072 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- User task for PR-072 small read-only/operator-assist CLI assist change
- `factory status --root .`
- `PYTHONPATH=. python -m factory inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline -n 5`
- [pyproject.toml](/pyproject.toml)
- [orchestrator/cli.py](/orchestrator/cli.py)
- [tests/test_cli.py](/tests/test_cli.py)

## scope
- PR-072 only reduces the UX/runtime entrypoint mismatch for approval queue inspection.
- Add a direct `inspect-approval-queue` console entrypoint as a thin shim over the existing CLI subcommand.
- Reuse the current `inspect-approval-queue` implementation and renderer without output format changes.
- Queue mutation, approval mutation, readiness gating, stale/latest interpretation, and cleanup semantics remain unchanged.
- Leave this plan note at [docs/prs/PR-072/plan.md](/docs/prs/PR-072/plan.md).

## output summary
- Register `inspect-approval-queue` as a direct console script in packaging metadata.
- Add a thin CLI shim that forwards direct-command argv to the existing `factory inspect-approval-queue` path.
- Add focused test coverage that the direct entrypoint and existing subcommand emit identical output for the same repo state.

## current repo snapshot
- `factory status --root .` succeeds and reports latest run `RUN-20260327T063724Z` with pending approvals visible.
- `PYTHONPATH=. python -m factory inspect-approval-queue --root .` succeeds and shows one stale pending item plus one latest pending item.
- The repo source of truth therefore shows an entrypoint mismatch, not an inspect implementation failure.

## risks
- Reimplementing inspect behavior in a second path would risk output drift, so the direct command must remain a pure forwarder.
- Any help, parsing, or rendering rewrite would widen scope beyond the operator-assist contract.
- Packaging-only changes can be missed at review time unless the forwarding path is covered by a focused runtime test.

## next required gate
- Reviewer: confirm the new direct command is a thin shim only and that no approval queue semantics changed.
- QA: confirm direct entrypoint and existing subcommand output remain identical for the same fixture.
- Docs Sync / Release: confirm docs sync is satisfied by this PR-local plan note plus code/test updates only.
