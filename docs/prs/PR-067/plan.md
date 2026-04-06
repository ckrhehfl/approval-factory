# PR-067 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- `PYTHONPATH=. pytest -q`
- recent git log and current repo state observations
- [docs/prs/README.md](/docs/prs/README.md)
- User direction that `docs/prs` is history and audit trail, not runtime source of truth
- User direction that repo/log output must override docs packs and prior notes

## scope
- PR-067 is docs-only.
- PR-067 records a minimal proposal for stale pending and approval queue hygiene.
- No runtime behavior, code paths, test behavior, CLI behavior, or approval semantics are changed.

## output summary
- PR-067 adds only this plan note under [docs/prs/PR-067/plan.md](/docs/prs/PR-067/plan.md).
- The note narrows future discussion to operator hygiene, visibility, and manual workflow boundaries around stale pending approval queue entries.
- The note does not propose or accept any runtime or approval semantic change.

## observed facts from repo/log output
- Active PR: none.
- Latest run `RUN-20260327T063724Z` is `approval_pending`.
- `approval_queue pending_total` is `2`.
- Stale pending count is `1`.
- Stale pending run id is `RUN-20260327T055614Z`.
- `python -m factory inspect-approval-queue --root .` distinguishes stale versus latest by `latest_relation`.
- Reported queue relations are `RUN-20260327T055614Z => latest_relation: stale` and `RUN-20260327T063724Z => latest_relation: latest`.
- The matching stale run path exists at [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml) and its recorded state is `approval_pending`.
- The matching latest run path exists at [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml) and its recorded state is `approval_pending`.
- Tests currently pass: `196 passed`.

## interpretation
- Stale pending is currently a real visibility state, not an automatic cleanup semantic.
- The presence of stale and latest pending together creates operator hygiene ambiguity for queue review.
- This should not be interpreted as reject, error, invalid, or otherwise failed approval semantics.
- Readiness visibility must not be reinterpreted as gate semantics.

## candidate follow-up options
- A. docs-only contract clarification: tighten wording in operator-facing docs so stale pending is described as visibility and manual hygiene scope only, without implying automatic cleanup or approval-state mutation.
- B. read-only visibility assist: add non-mutating output that helps operators see stale versus latest pending items more directly while preserving current approval and queue behavior.
- C. explicit manual hygiene command proposal: if mutation is ever proposed, require dry-run first, an explicit run-id target, latest pending protection, and no automatic mutation by `status` or `inspect`.

## recommended minimal next PR scope
- The first follow-up should remain docs and contract clarification or a read-only visibility assist.
- Do not jump directly to mutation behavior.

## risks
- Users may overread stale pending as cleanup semantics when it is currently only a visibility condition.
- A point-in-time queue snapshot can change later and should not be treated as a permanent state guarantee.
- Mutation features here would be structurally risky without separate proposal acceptance.

## next required gate
- Reviewer: confirm this proposal-only note stays within operator hygiene and visibility framing and does not imply acceptance of a runtime or approval semantic change.
- QA: confirm the recorded facts still match the cited repo and log observations for a docs-only PR at review time.
- Docs Sync / Release: confirm docs sync is satisfied by this PR-local plan artifact and that no broader contract change is being merged through this note alone.
