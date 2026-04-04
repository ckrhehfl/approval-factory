# PR-079 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- User task for PR-079 docs-only proposal PR using live repo state as source of truth
- `factory status --root .`
- `inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline -n 10`
- [docs/prs/README.md](/mnt/c/dev/approval-factory/docs/prs/README.md)
- [docs/contracts/status-contract.md](/mnt/c/dev/approval-factory/docs/contracts/status-contract.md)
- [docs/adr/ADR-003-file-based-approval-queue.md](/mnt/c/dev/approval-factory/docs/adr/ADR-003-file-based-approval-queue.md)
- [docs/prs/PR-074/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-074/plan.md)
- [docs/prs/PR-074/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-074/proposal.md)
- [docs/prs/PR-075/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-075/plan.md)
- [docs/prs/PR-075/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-075/proposal.md)
- [docs/prs/PR-076/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-076/plan.md)
- [docs/prs/PR-076/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-076/proposal.md)
- [docs/prs/PR-077/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-077/plan.md)
- [docs/prs/PR-077/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-077/proposal.md)
- [docs/prs/PR-078/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-078/plan.md)
- [docs/prs/PR-078/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-078/proposal.md)
- [docs/prs/PR-073/delta.md](/mnt/c/dev/approval-factory/docs/prs/PR-073/delta.md)
- [docs/prs/PR-073/start-prompt.md](/mnt/c/dev/approval-factory/docs/prs/PR-073/start-prompt.md)
- [runs/latest/RUN-20260327T055614Z/run.yaml](/mnt/c/dev/approval-factory/runs/latest/RUN-20260327T055614Z/run.yaml)
- [runs/latest/RUN-20260327T063724Z/run.yaml](/mnt/c/dev/approval-factory/runs/latest/RUN-20260327T063724Z/run.yaml)
- [approval_queue/pending/APR-RUN-20260327T055614Z.yaml](/mnt/c/dev/approval-factory/approval_queue/pending/APR-RUN-20260327T055614Z.yaml)
- [approval_queue/pending/APR-RUN-20260327T063724Z.yaml](/mnt/c/dev/approval-factory/approval_queue/pending/APR-RUN-20260327T063724Z.yaml)

## scope
- PR-079 is docs-only and proposal-only.
- Topic: approval queue hygiene implementation split and rollout boundary proposal.
- No implementation.
- No runtime, code, test, parser, dry-run, apply-path, or CLI behavior change.
- No expansion of `stale` or `latest` into cleanup semantics or selector semantics.
- Explicit target, dry-run-first, and separate apply remain required.
- This PR must leave [docs/prs/PR-079/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-079/plan.md) in place before merge.

## output summary
- Add [docs/prs/PR-079/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-079/plan.md) as the PR-local contract and snapshot note.
- Add [docs/prs/PR-079/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-079/proposal.md) as the implementation split and rollout boundary proposal.
- Summarize the confirmed proposal chain from PR-074 through PR-078 and pin the next-stage ordering and gate conditions without approving implementation.

## current repo snapshot
- Current branch is `pr/079-approval-queue-implementation-split-boundary`.
- Active PR: `none`.
- Latest run: `RUN-20260327T063724Z`.
- Approval queue pending total: `2`.
- `factory status --root .` reports `stale_pending_count: 1` and `stale_pending_run_ids: RUN-20260327T055614Z`.
- `inspect-approval-queue --root .` reports relation counts latest `1`, stale `1`, no-latest-run `0`, unparseable `0`.
- Pending item `APR-RUN-20260327T055614Z.yaml` maps to [runs/latest/RUN-20260327T055614Z/run.yaml](/mnt/c/dev/approval-factory/runs/latest/RUN-20260327T055614Z/run.yaml), which records `pr_id: PR-003` and `state: approval_pending`.
- Pending item `APR-RUN-20260327T063724Z.yaml` maps to [runs/latest/RUN-20260327T063724Z/run.yaml](/mnt/c/dev/approval-factory/runs/latest/RUN-20260327T063724Z/run.yaml), which records `pr_id: PR-004` and `state: approval_pending`.
- The repo therefore currently shows two visible pending approval artifacts across different run and PR histories, so implementation order and mutation boundaries must stay explicit.

## contract to pin in this PR
- PR-079 summarizes the settled proposal chain only. It does not reopen earlier decisions.
- The follow-up implementation order remains:
  - parser implementation
  - dry-run implementation
  - apply implementation
  - docs/help/tests
- Rollout boundary must prevent later stages from starting before earlier stage guardrails are accepted.
- Parser-only implementation must not introduce mutation.
- Dry-run implementation must remain non-mutating and must not imply apply approval.
- Apply implementation must remain separately approved after parser and dry-run behavior are already fixed.
- Auto cleanup, auto resolve, stale/latest shorthand selectors, and Relation Summary-triggered action remain out of scope.
- External downloadable 3-pack refresh is a follow-up after PR-079, not part of this PR.

## follow-up boundary
- PR-079 does not approve parser implementation.
- PR-079 does not approve dry-run implementation.
- PR-079 does not approve apply implementation.
- PR-079 does not approve docs/help/test updates beyond this PR-local proposal note.
- Any later implementation PR must preserve explicit target, dry-run-first, separate apply, and visibility-only stale/latest semantics.

## ADR and docs sync assessment
- ADR required: no.
- Reason: this PR orders already-proposed implementation slices and rollout gates, but does not approve an architecture change.
- Docs sync required: yes.
- Reason: this PR adds the required PR-local plan and proposal docs for PR-079 and does not broaden runtime contract docs in this slice.

## risks
- If implementation order is not pinned, later work may jump directly to mutation behavior before parser and dry-run guardrails are stable.
- If rollout boundaries are not explicit, parser or dry-run work may be overread as approval for apply semantics.
- If forbidden scope is not restated, stale/latest or relation-summary visibility may drift into cleanup or selector semantics later.

## next required gate
- Reviewer: confirm the PR stays docs-only and proposal-only, with no implied implementation or mutation approval.
- Approver / PM: decide whether the implementation split and rollout boundary proposal is strict enough to govern later PR sequencing.
- Docs Sync / Release: confirm docs sync is satisfied by the PR-local plan and proposal docs only.
