# PR-058 Plan

## input refs
- AGENTS.md v2026-04-03
- [docs/prs/PR-060/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-060/plan.md)
- `git show --stat --name-only --format=fuller e323639` observed on 2026-04-03
- `git show --stat --name-only --format=fuller 641278a` observed on 2026-04-03
- User request for PR-062 docs-only backfill batch B observed on 2026-04-03

## scope
- Backfill a minimum `docs/prs/PR-058/plan.md` history note through the docs/history backlog only.
- Record PR-058 against commit `e323639` and merge `641278a`.
- Ground the note in the observed touched files: `orchestrator/cli.py` and `tests/test_cli.py`.
- Do not treat the missing `docs/prs/PR-058/` directory as evidence of a runtime gap.
- Do not change semantics, runtime code, tests, artifacts, or help wording in this backfill PR.

## output summary
- `docs/prs/PR-058/plan.md` is added as the minimum history artifact for PR-058.
- The note records PR-058 as `cli: improve inspect-approval help discoverability`.
- The note explicitly anchors PR-058 to the observed touched files `orchestrator/cli.py` and `tests/test_cli.py`.
- This backfill does not add or imply any new runtime behavior beyond the existing git history.

## risks
- A minimum backfill note cannot recreate the full contemporaneous planning context that was not preserved in `docs/prs/` at the time.
- Readers could still overread historical `docs/prs/` gaps as product/runtime gaps unless they follow the history-contract wording established in later docs.

## next required gate
- Reviewer: confirm the backfill stays history-only, keeps PR-058 distinct from PR-062, and does not imply semantics beyond commit `e323639` / merge `641278a`.
- Docs Sync / Release: confirm this minimum `plan.md` satisfies the approved docs/history backlog batch B scope with no further doc expansion in this PR.
