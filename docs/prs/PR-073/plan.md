# PR-073 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- User task for PR-073 handoff pack refresh using live repo state as source of truth
- `factory status --root .`
- `inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline -n 10`
- `pytest -q tests/test_cli.py -k 'approval_queue or inspect'`
- [docs/prs/PR-070/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-070/plan.md)
- [docs/prs/PR-070/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-070/proposal.md)
- [docs/prs/PR-071/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-071/plan.md)
- [docs/prs/PR-072/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-072/plan.md)
- [docs/prs/PR-069/delta.md](/mnt/c/dev/approval-factory/docs/prs/PR-069/delta.md)
- [docs/prs/PR-069/start-prompt.md](/mnt/c/dev/approval-factory/docs/prs/PR-069/start-prompt.md)
- [docs/prs/README.md](/mnt/c/dev/approval-factory/docs/prs/README.md)

## scope
- PR-073 is a docs-only handoff refresh for the verified PR-070 through PR-072 slice.
- Keep the 3-document handoff structure as PR-local `plan.md`, `delta.md`, and `start-prompt.md`.
- Conclude `master unchanged` first because PR-070 through PR-072 did not introduce a permanent contract or semantic change.
- Do not mutate runtime code, queue artifacts, approval state, or prior PR documents.

## output summary
- Add [docs/prs/PR-073/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-073/plan.md) as the PR-local contract and refresh record.
- Add [docs/prs/PR-073/delta.md](/mnt/c/dev/approval-factory/docs/prs/PR-073/delta.md) to capture the verified PR-070 through PR-072 changes, current repo snapshot, and external-pack boundary note.
- Add [docs/prs/PR-073/start-prompt.md](/mnt/c/dev/approval-factory/docs/prs/PR-073/start-prompt.md) as the short restart prompt for the next conversation.
- Leave master-pack style documents unchanged because the recent slice changed visibility and entrypoint UX only, not permanent semantics.

## non-goals
- No runtime change.
- No approval or queue mutation.
- No cleanup semantic change.
- No implicit external downloadable pack creation in this PR.

## validation
- Confirm only `docs/prs/PR-073/plan.md`, `docs/prs/PR-073/delta.md`, and `docs/prs/PR-073/start-prompt.md` are added.
- Confirm the refresh states `master unchanged` and keeps `semantics changed? -> none`.
- Confirm the delta reflects PR-070 proposal-only clarification, PR-071 `matching_pr_id` visibility, PR-072 direct entrypoint availability, and the current validation snapshot.
- Confirm the start prompt remains short and keeps first action plus prohibition rules explicit.

## risks
- Time-bound queue and validation snapshots will age after later runs, approvals, or test changes.
- Readers may still overread `stale` as cleanup semantics unless the visibility-only wording stays explicit.
- External downloadable handoff packaging can be confused with this repo-internal PR-local refresh unless the boundary note stays explicit.

## next required gate
- Reviewer: confirm the refresh stays within verifiable PR-070 through PR-072 facts and keeps master unchanged.
- QA: confirm the recorded repo snapshot and validation snapshot still match live command output at review time.
- Docs Sync / Release: confirm PR-local handoff docs are sufficient and that no master-pack update is required.
