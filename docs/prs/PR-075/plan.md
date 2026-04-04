# PR-075 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- User task for PR-075 docs-only proposal PR using live repo state as source of truth
- `factory status --root .`
- `inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline -n 10`
- [README.md](/mnt/c/dev/approval-factory/README.md)
- [docs/contracts/status-contract.md](/mnt/c/dev/approval-factory/docs/contracts/status-contract.md)
- [docs/ops/runbook.md](/mnt/c/dev/approval-factory/docs/ops/runbook.md)
- [docs/prs/README.md](/mnt/c/dev/approval-factory/docs/prs/README.md)
- [docs/prs/PR-070/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-070/proposal.md)
- [docs/prs/PR-074/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-074/plan.md)
- [docs/prs/PR-074/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-074/proposal.md)
- [runs/latest/RUN-20260327T055614Z/run.yaml](/mnt/c/dev/approval-factory/runs/latest/RUN-20260327T055614Z/run.yaml)
- [runs/latest/RUN-20260327T063724Z/run.yaml](/mnt/c/dev/approval-factory/runs/latest/RUN-20260327T063724Z/run.yaml)
- [approval_queue/pending/APR-RUN-20260327T055614Z.yaml](/mnt/c/dev/approval-factory/approval_queue/pending/APR-RUN-20260327T055614Z.yaml)
- [approval_queue/pending/APR-RUN-20260327T063724Z.yaml](/mnt/c/dev/approval-factory/approval_queue/pending/APR-RUN-20260327T063724Z.yaml)

## scope
- PR-075 is docs-only and proposal-only.
- Topic: command-shape proposal for a manual approval queue hygiene command.
- No implementation.
- No runtime, code, test, CLI behavior, or approval behavior change.
- No expansion of `stale` or `latest` into cleanup semantics or selector semantics.
- This PR must leave [docs/prs/PR-075/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-075/plan.md) in place before merge.

## output summary
- Add [docs/prs/PR-075/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-075/plan.md) as the PR-local contract and repo snapshot note.
- Add [docs/prs/PR-075/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-075/proposal.md) as the command-shape proposal.
- Fix the proposal boundary so any later implementation must preserve explicit target selection, dry-run first, and separate apply.

## current repo snapshot
- Current branch is `pr/075-manual-approval-queue-command-shape`.
- Active PR: `none`.
- Latest run: `RUN-20260327T063724Z`.
- Approval queue pending total: `2`.
- `factory status --root .` reports `stale_pending_count: 1` and `stale_pending_run_ids: RUN-20260327T055614Z`.
- `inspect-approval-queue --root .` reports relation counts latest `1`, stale `1`, no-latest-run `0`, unparseable `0`.
- Pending item `APR-RUN-20260327T055614Z.yaml` maps to [runs/latest/RUN-20260327T055614Z/run.yaml](/mnt/c/dev/approval-factory/runs/latest/RUN-20260327T055614Z/run.yaml), which records `pr_id: PR-003` and `state: approval_pending`.
- Pending item `APR-RUN-20260327T063724Z.yaml` maps to [runs/latest/RUN-20260327T063724Z/run.yaml](/mnt/c/dev/approval-factory/runs/latest/RUN-20260327T063724Z/run.yaml), which records `pr_id: PR-004` and `state: approval_pending`.
- The repo therefore currently shows two visible pending approval artifacts across different run and PR histories.

## contract to pin in this PR
- The command name may remain provisional in this PR.
- The future command surface must define whether the explicit target is `run-id`, `approval-id`, or both.
- If both target forms are later accepted, the parse and validation rule must be explicit and must still resolve to exactly one queue artifact.
- `latest`, `stale`, relation counts, relation summary, and status output are visibility surfaces only and must not become mutation target selectors.
- The future command must be dry-run first by default.
- Any mutation path must be a separate explicit apply action such as `--apply`.
- Safe-fail behavior must be part of the proposal surface, not deferred to implementation guesswork.

## follow-up boundary
- PR-075 does not approve mutation semantics.
- PR-075 does not approve queue lifecycle changes.
- PR-075 does not approve a final command name.
- Any later implementation must be split so parser, dry-run behavior, apply behavior, and docs/help/tests can be reviewed independently.

## ADR and docs sync assessment
- ADR required: no.
- Reason: this PR fixes proposal wording and command-shape guardrails only, without approving an architecture change.
- Docs sync required: yes.
- Reason: this PR adds the required PR-local history docs for PR-075 and no broader contract file changes are needed in this slice.

## risks
- If target rules stay vague, later implementation may smuggle in implicit latest/stale selector behavior.
- If dry-run and apply are not separated at proposal time, a destructive command could be normalized as a one-step action.
- If refusal cases are not explicit, ambiguous queue states may be handled inconsistently across later PRs.

## next required gate
- Reviewer: confirm the PR stays docs-only and proposal-only, with no implied implementation approval.
- Approver / PM: decide whether the command-shape proposal is strict enough to authorize a later design/implementation split.
- Docs Sync / Release: confirm docs sync is satisfied by the PR-local plan and proposal docs only.
