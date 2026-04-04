# PR-077 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- User task for PR-077 docs-only proposal PR using live repo state as source of truth
- `factory status --root .`
- `inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline -n 10`
- [docs/prs/README.md](/mnt/c/dev/approval-factory/docs/prs/README.md)
- [docs/contracts/status-contract.md](/mnt/c/dev/approval-factory/docs/contracts/status-contract.md)
- [docs/ops/runbook.md](/mnt/c/dev/approval-factory/docs/ops/runbook.md)
- [docs/prs/PR-074/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-074/plan.md)
- [docs/prs/PR-074/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-074/proposal.md)
- [docs/prs/PR-075/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-075/plan.md)
- [docs/prs/PR-075/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-075/proposal.md)
- [docs/prs/PR-076/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-076/plan.md)
- [docs/prs/PR-076/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-076/proposal.md)
- [runs/latest/RUN-20260327T055614Z/run.yaml](/mnt/c/dev/approval-factory/runs/latest/RUN-20260327T055614Z/run.yaml)
- [runs/latest/RUN-20260327T063724Z/run.yaml](/mnt/c/dev/approval-factory/runs/latest/RUN-20260327T063724Z/run.yaml)
- [approval_queue/pending/APR-RUN-20260327T055614Z.yaml](/mnt/c/dev/approval-factory/approval_queue/pending/APR-RUN-20260327T055614Z.yaml)
- [approval_queue/pending/APR-RUN-20260327T063724Z.yaml](/mnt/c/dev/approval-factory/approval_queue/pending/APR-RUN-20260327T063724Z.yaml)

## scope
- PR-077 is docs-only and proposal-only.
- Topic: apply behavior proposal for the manual approval queue hygiene command.
- No implementation.
- No runtime, code, test, parser, dry-run-path, apply-path, or CLI behavior change.
- No expansion of `stale` or `latest` into cleanup semantics or selector semantics.
- Explicit target, dry-run-first, and separate apply remain required.
- This PR must leave [docs/prs/PR-077/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-077/plan.md) in place before merge.

## output summary
- Add [docs/prs/PR-077/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-077/plan.md) as the PR-local contract and snapshot note.
- Add [docs/prs/PR-077/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-077/proposal.md) as the apply behavior proposal.
- Pin apply purpose, preconditions, mutation boundary, refusal cases, minimum audit expectations, and follow-up implementation split without approving any parser or mutation implementation.

## current repo snapshot
- Current branch is `pr/077-approval-queue-hygiene-apply`.
- Active PR: `none`.
- Latest run: `RUN-20260327T063724Z`.
- Approval queue pending total: `2`.
- `factory status --root .` reports `stale_pending_count: 1` and `stale_pending_run_ids: RUN-20260327T055614Z`.
- `inspect-approval-queue --root .` reports relation counts latest `1`, stale `1`, no-latest-run `0`, unparseable `0`.
- Pending item `APR-RUN-20260327T055614Z.yaml` maps to [runs/latest/RUN-20260327T055614Z/run.yaml](/mnt/c/dev/approval-factory/runs/latest/RUN-20260327T055614Z/run.yaml), which records `pr_id: PR-003` and `state: approval_pending`.
- Pending item `APR-RUN-20260327T063724Z.yaml` maps to [runs/latest/RUN-20260327T063724Z/run.yaml](/mnt/c/dev/approval-factory/runs/latest/RUN-20260327T063724Z/run.yaml), which records `pr_id: PR-004` and `state: approval_pending`.
- The repo therefore currently shows two visible pending approval artifacts across different run and PR histories, so apply must stay exact-target only and must not widen from visibility labels or summaries.

## contract to pin in this PR
- Apply exists only to attempt mutation for one exact target that was already explicitly chosen and previewed.
- Apply must require an exact target and must refuse heuristic selector requests.
- Apply must preserve dry-run-first and should reuse the same target identity that dry-run confirmed when that identity is available.
- Apply may only touch the queue artifact mutation surface of the resolved target and must not mutate unrelated queue artifacts, unrelated runs, or approval decision semantics.
- Apply must safe-fail for target missing, ambiguous target, already terminal, heuristic apply without dry-run, and mismatched target identity.
- This PR may describe minimum operator checks and evidence expectations for a future apply path, but it does not approve evidence schema or implementation.

## follow-up boundary
- PR-077 does not approve parser implementation.
- PR-077 does not approve dry-run implementation.
- PR-077 does not approve apply implementation.
- PR-077 does not approve docs/help/test updates beyond this PR-local proposal note.
- Any later implementation must be split into parser, dry-run implementation, apply implementation, and docs/help/tests.

## ADR and docs sync assessment
- ADR required: no.
- Reason: this PR narrows proposal wording for apply behavior only and does not approve an architecture change.
- Docs sync required: yes.
- Reason: this PR adds the required PR-local plan and proposal docs for PR-077 and does not broaden runtime contract docs in this slice.

## risks
- If apply purpose is not constrained to one explicit target, later work may smuggle in cleanup or selector semantics through the mutation path.
- If dry-run identity reuse is left vague, apply could drift into re-resolution against changed queue state and mutate the wrong artifact.
- If non-target boundaries are not explicit, queue hygiene work may accidentally rewrite unrelated queue artifacts, runs, or approval semantics.

## next required gate
- Reviewer: confirm the PR stays docs-only and proposal-only, with no implied runtime or mutation approval.
- Approver / PM: decide whether the apply contract is strict enough to authorize a later implementation split.
- Docs Sync / Release: confirm docs sync is satisfied by the PR-local plan and proposal docs only.
