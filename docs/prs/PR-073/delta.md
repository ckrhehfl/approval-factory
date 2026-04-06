# approval-factory delta pack (PR-070~072 handoff context)

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- User task for PR-073 handoff pack refresh using live repo state as source of truth
- `factory status --root .`
- `inspect-approval-queue --root .`
- `git --no-pager log --oneline -n 10`
- `pytest -q tests/test_cli.py -k 'approval_queue or inspect'`
- [docs/prs/PR-070/plan.md](/docs/prs/PR-070/plan.md)
- [docs/prs/PR-070/proposal.md](/docs/prs/PR-070/proposal.md)
- [docs/prs/PR-071/plan.md](/docs/prs/PR-071/plan.md)
- [docs/prs/PR-072/plan.md](/docs/prs/PR-072/plan.md)
- [docs/prs/README.md](/docs/prs/README.md)

## scope
- Summarize the verified handoff context for PR-070 through PR-072 only.
- Treat live repo commands and current merged code as source of truth; older handoff text is secondary until re-verified.
- Conclude `master unchanged` because this slice introduced no permanent semantic or contract change.

## master unchanged?
- Yes.
- PR-070 was proposal-only clarification.
- PR-071 added read-only `matching_pr_id` visibility.
- PR-072 added a direct `inspect-approval-queue` entrypoint as a thin forwarder.
- None of the three changed approval semantics, queue semantics, stale/latest meaning, cleanup behavior, or merge rules.

## PR-070
- PR-070 clarified that stale pending is visibility-only and proposal-only in this slice.
- `stale` remains a non-latest relation label relative to the latest run.
- Do not interpret `stale` or `latest` as cleanup, deletion safety, auto resolve, or queue mutation semantics.

## PR-071
- `inspect-approval-queue` now exposes `matching_pr_id` when a matching run exists and provides `pr_id`.
- This is operator visibility assist only.
- Missing, unreadable, or unparseable run context still degrades safely without mutation behavior.

## PR-072
- `inspect-approval-queue --root .` is now available as a direct console entrypoint.
- The direct command is a thin shim over the existing inspect subcommand path.
- Output semantics and rendering contract remain unchanged.

## semantics changed?
- None.

## current repo-state snapshot
- `factory status --root .`:
- Active PR: `none`
- Latest run: `RUN-20260327T063724Z`
- Approval status: `pending`
- Pending total: `2`
- `latest_run_has_pending`: `True`
- `stale_pending_count`: `1`
- stale pending run id: `RUN-20260327T055614Z`
- `inspect-approval-queue --root .`:
- `latest_run_id`: `RUN-20260327T063724Z`
- `latest_relation_count_latest`: `1`
- `latest_relation_count_stale`: `1`
- `latest_relation_count_no_latest_run`: `0`
- `latest_relation_count_unparseable`: `0`
- stale item `RUN-20260327T055614Z`: `matching_pr_id: PR-003`, `matching_run_state: approval_pending`
- latest item `RUN-20260327T063724Z`: `matching_pr_id: PR-004`, `matching_run_state: approval_pending`

## recent validation snapshot
- `pytest -q tests/test_cli.py -k 'approval_queue or inspect'`
- Result: `55 passed, 116 deselected`
- Validation confirms the inspect/read-only CLI slice currently passes, including queue inspection coverage and direct entrypoint coverage.

## external downloadable 3-pack boundary
- This PR refreshes only the repo-internal PR-local handoff docs under `docs/prs/PR-073/`.
- No separate external downloadable 3-pack artifact is created in this PR.
- If an external downloadable 3-pack is requested later, the verified content split is currently:
- master: unchanged
- delta: refresh required for PR-070 through PR-072 and current snapshot
- start prompt: refresh required for current first-step guidance
- If repo-internal and external packs diverge later, the difference should be distribution wrapper only, not runtime semantics.

## next conversation starting question
- After `factory status --root .`, what is the next approved work item once the current active PR, latest run, and pending approval context are re-verified?

## output summary
- PR-073 refreshes the handoff pack for the verified PR-070 through PR-072 slice.
- The refresh keeps master unchanged, records recent repo and validation snapshots, and updates the short start prompt for the next conversation.
- No permanent contract update is required in this slice.

## risks
- Snapshot values may age after new runs, approvals, or test edits.
- Readers may still conflate stale/latest visibility with cleanup semantics unless the explicit prohibition remains.
- External downloadable pack requests may be assumed completed unless the boundary note is read.

## next required gate
- Reviewer: confirm the delta stays within verifiable PR-070 through PR-072 facts and keeps semantics unchanged.
- QA: confirm the current snapshot still shows direct entrypoint availability and `matching_pr_id` visibility.
- Docs Sync / Release: confirm PR-local handoff docs are sufficient and that master remains unchanged.
