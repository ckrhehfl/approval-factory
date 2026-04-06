# PR-076 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- User task for PR-076 docs-only proposal PR using live repo state as source of truth
- `factory status --root .`
- `inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline -n 10`
- [docs/prs/README.md](/docs/prs/README.md)
- [docs/contracts/status-contract.md](/docs/contracts/status-contract.md)
- [docs/ops/runbook.md](/docs/ops/runbook.md)
- [docs/prs/PR-074/plan.md](/docs/prs/PR-074/plan.md)
- [docs/prs/PR-074/proposal.md](/docs/prs/PR-074/proposal.md)
- [docs/prs/PR-075/plan.md](/docs/prs/PR-075/plan.md)
- [docs/prs/PR-075/proposal.md](/docs/prs/PR-075/proposal.md)
- [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml)
- [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml)
- [approval_queue/pending/APR-RUN-20260327T055614Z.yaml](/approval_queue/pending/APR-RUN-20260327T055614Z.yaml)
- [approval_queue/pending/APR-RUN-20260327T063724Z.yaml](/approval_queue/pending/APR-RUN-20260327T063724Z.yaml)

## scope
- PR-076 is docs-only and proposal-only.
- Topic: dry-run behavior proposal for the manual approval queue hygiene command.
- No implementation.
- No runtime, code, test, parser, apply-path, or CLI behavior change.
- No expansion of `stale` or `latest` into cleanup semantics or selector semantics.
- Explicit target, dry-run-first, and separate apply remain required.
- This PR must leave [docs/prs/PR-076/plan.md](/docs/prs/PR-076/plan.md) in place before merge.

## output summary
- Add [docs/prs/PR-076/plan.md](/docs/prs/PR-076/plan.md) as the PR-local contract and snapshot note.
- Add [docs/prs/PR-076/proposal.md](/docs/prs/PR-076/proposal.md) as the dry-run behavior proposal.
- Pin the minimum dry-run output, safe-fail cases, and apply boundary without approving any mutation implementation.

## current repo snapshot
- Current branch is `pr/076-approval-queue-hygiene-dry-run`.
- Active PR: `none`.
- Latest run: `RUN-20260327T063724Z`.
- Approval queue pending total: `2`.
- `factory status --root .` reports `stale_pending_count: 1` and `stale_pending_run_ids: RUN-20260327T055614Z`.
- `inspect-approval-queue --root .` reports relation counts latest `1`, stale `1`, no-latest-run `0`, unparseable `0`.
- Pending item `APR-RUN-20260327T055614Z.yaml` maps to [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml), which records `pr_id: PR-003` and `state: approval_pending`.
- Pending item `APR-RUN-20260327T063724Z.yaml` maps to [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml), which records `pr_id: PR-004` and `state: approval_pending`.
- The repo therefore currently shows two visible pending approval artifacts across different run and PR histories, so dry-run must stay preview-only and exact-target only.

## contract to pin in this PR
- Dry-run exists only to preview one exact target before any mutation.
- Dry-run may show resolved identity, canonical queue artifact path, related run or PR context if present, proposed mutation category, and proceed or refuse reason.
- Dry-run must not mutate queue artifacts, run artifacts, or approval decision artifacts.
- Dry-run success does not approve apply.
- Apply remains a separate explicit step.
- Refusal must be explicit for target missing, ambiguous target, already terminal, heuristic selector attempt, and invalid selector combination.

## follow-up boundary
- PR-076 does not approve parser implementation.
- PR-076 does not approve dry-run implementation.
- PR-076 does not approve apply implementation.
- PR-076 does not approve docs/help/test updates beyond this PR-local proposal note.
- Any later implementation must be split into parser, dry-run implementation, apply implementation, and docs/help/tests.

## ADR and docs sync assessment
- ADR required: no.
- Reason: this PR narrows proposal wording for dry-run behavior only and does not approve an architecture change.
- Docs sync required: yes.
- Reason: this PR adds the required PR-local plan and proposal docs for PR-076 and does not broaden contract docs in this slice.

## risks
- If dry-run output is not constrained to preview fields, later implementation may smuggle mutation or selector semantics into a supposedly safe step.
- If refusal cases stay underspecified, operators may treat `stale` or `latest` visibility as a valid heuristic target.
- If dry-run success is mistaken for apply approval, a destructive path could become normalized without a second explicit decision.

## next required gate
- Reviewer: confirm the PR stays docs-only and proposal-only, with no implied runtime or mutation approval.
- Approver / PM: decide whether the dry-run contract is strict enough to authorize a later implementation split.
- Docs Sync / Release: confirm docs sync is satisfied by the PR-local plan and proposal docs only.
