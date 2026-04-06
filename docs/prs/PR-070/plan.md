# PR-070 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- User task for PR-070 docs-only stale pending / approval queue hygiene proposal
- `factory status --root .`
- `factory inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline -n 5`
- [docs/prs/PR-067/plan.md](/docs/prs/PR-067/plan.md)
- [docs/prs/PR-068/plan.md](/docs/prs/PR-068/plan.md)
- [docs/prs/PR-069/plan.md](/docs/prs/PR-069/plan.md)
- [docs/prs/README.md](/docs/prs/README.md)
- [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml)
- [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml)

## scope
- PR-070 is docs-only.
- PR-070 records a proposal-only clarification for stale pending and approval queue hygiene.
- Runtime, code, tests, CLI semantics, approval semantics, and queue behavior remain unchanged.
- This PR must leave [docs/prs/PR-070/plan.md](/docs/prs/PR-070/plan.md) in place before merge.

## output summary
- Add [docs/prs/PR-070/plan.md](/docs/prs/PR-070/plan.md) as the PR-local contract and snapshot note.
- Add [docs/prs/PR-070/proposal.md](/docs/prs/PR-070/proposal.md) as the proposal-only clarification note.
- Record the current repo-observed approval queue state without proposing mutation behavior.

## current repo snapshot
- Active PR: none.
- Latest run: `RUN-20260327T063724Z`.
- Pending total: `2`.
- Relation summary: latest `1`, stale `1`, no_latest_run `0`, unparseable `0`.
- Stale pending item `RUN-20260327T055614Z` has a matching run at [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml) and that run state is `approval_pending`.
- Latest pending item `RUN-20260327T063724Z` has a matching run at [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml) and that run state is `approval_pending`.
- The stale item belongs to `PR-003`.
- The latest item belongs to `PR-004`.
- These are different PR/run pairs and both remain visible in the pending approval queue snapshot.

## contract
- `stale` is a non-latest visibility label relative to the latest run.
- `stale` is not obsolete, rejected, superseded-for-deletion, safe-to-delete, or auto-resolvable.
- `docs/prs` remains a history and audit-trail surface, not a runtime mutation surface.
- No auto cleanup.
- No auto resolve.
- No queue mutation.
- No readiness gating.
- No merge behavior change.

## follow-up boundary
- If follow-up operator hygiene work is proposed later, it must be a separate explicit manual hygiene command proposal.
- PR-070 does not propose or accept mutation behavior itself.

## risks
- Operators may misread `stale` as cleanup semantics if the visibility-only meaning is not stated explicitly.
- The coexistence of one latest and one stale pending approval can be overread as duplicate-safe deletion when the current repo state does not support that interpretation.
- Future discussion can drift into mutation design unless this PR keeps proposal scope narrow.

## next required gate
- Reviewer: confirm the note stays proposal-only and preserves unchanged runtime, CLI, and approval semantics.
- QA: confirm the recorded snapshot still matches live repo inspection at review time.
- Docs Sync / Release: confirm docs sync is satisfied by the PR-local plan and proposal notes only, with no broader contract update merged implicitly.
