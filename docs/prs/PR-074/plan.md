# PR-074 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- User task for PR-074 docs-only proposal PR using live repo state as source of truth
- `factory status --root .`
- `inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline -n 10`
- [docs/prs/README.md](/docs/prs/README.md)
- [docs/contracts/status-contract.md](/docs/contracts/status-contract.md)
- [docs/ops/runbook.md](/docs/ops/runbook.md)
- [docs/prs/PR-070/plan.md](/docs/prs/PR-070/plan.md)
- [docs/prs/PR-070/proposal.md](/docs/prs/PR-070/proposal.md)
- [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml)
- [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml)
- [approval_queue/pending/APR-RUN-20260327T055614Z.yaml](/approval_queue/pending/APR-RUN-20260327T055614Z.yaml)
- [approval_queue/pending/APR-RUN-20260327T063724Z.yaml](/approval_queue/pending/APR-RUN-20260327T063724Z.yaml)

## scope
- PR-074 is docs-only and proposal-only.
- Topic: explicit manual approval queue hygiene command proposal.
- No implementation, runtime, code, test, CLI, queue mutation, or approval behavior change.
- No expansion of `stale` or `latest` into cleanup semantics.
- This PR must leave [docs/prs/PR-074/plan.md](/docs/prs/PR-074/plan.md) in place before merge.

## output summary
- Add [docs/prs/PR-074/plan.md](/docs/prs/PR-074/plan.md) as the PR-local contract and snapshot note.
- Add [docs/prs/PR-074/proposal.md](/docs/prs/PR-074/proposal.md) as the proposal note for an explicit manual hygiene command.
- Record why any future hygiene work must begin as a manual, explicit, dry-run-first proposal instead of an implementation PR.

## current repo snapshot
- Active PR: `none`.
- Latest run: `RUN-20260327T063724Z`.
- Approval queue pending total: `2`.
- Relation summary: latest `1`, stale `1`, no_latest_run `0`, unparseable `0`.
- Stale pending item `RUN-20260327T055614Z` still has a matching run at [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml) and that run state is `approval_pending`.
- Latest pending item `RUN-20260327T063724Z` has a matching run at [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml) and that run state is `approval_pending`.
- The stale item belongs to `PR-003`.
- The latest item belongs to `PR-004`.
- The repo therefore currently shows simultaneous visible pending approvals for different PR/run histories without any cleanup behavior.

## contract
- `stale` remains a non-latest visibility label only.
- `stale` is not cleanup, deletion safety, auto resolve, or readiness gating semantics.
- A future hygiene command, if ever implemented, must require an explicit target and must not infer the target from `status`, `inspect`, `latest`, or relation summary output alone.
- A future hygiene command must default to dry-run and require an additional explicit apply step before any mutation.
- No auto cleanup.
- No auto resolve.
- No readiness gating.
- No Relation Summary-triggered action.
- No merge behavior change.

## follow-up boundary
- PR-074 does not approve implementation.
- If any follow-up proceeds, it must be split into small PRs with separate approval for command shape, guardrails, docs, and tests.
- Any later implementation PR must preserve the existing visibility-only meaning of `stale`.

## risks
- If the proposal skips the manual-first boundary, later work may smuggle queue mutation semantics into visibility surfaces.
- If explicit target wording is weak, operators may overread `latest` or `stale` as an implicit selector.
- If dry-run-first is not fixed now, later CLI design could normalize direct mutation on ambiguous queue state.

## next required gate
- Reviewer: confirm the PR stays docs-only and proposal-only, with no implied behavior approval.
- Approver / PM: decide whether an explicit manual hygiene command should advance beyond proposal.
- Docs Sync / Release: confirm docs sync is satisfied by the PR-local plan and proposal notes only.
