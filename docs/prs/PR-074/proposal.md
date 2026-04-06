# PR-074 Proposal

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- `factory status --root .`
- `inspect-approval-queue --root .`
- [docs/contracts/status-contract.md](/docs/contracts/status-contract.md)
- [docs/ops/runbook.md](/docs/ops/runbook.md)
- [docs/prs/PR-070/proposal.md](/docs/prs/PR-070/proposal.md)
- [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml)
- [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml)
- [approval_queue/pending/APR-RUN-20260327T055614Z.yaml](/approval_queue/pending/APR-RUN-20260327T055614Z.yaml)
- [approval_queue/pending/APR-RUN-20260327T063724Z.yaml](/approval_queue/pending/APR-RUN-20260327T063724Z.yaml)

## scope
- Proposal-only note for an explicit manual approval queue hygiene command.
- No implementation.
- No runtime, code, test, CLI, queue, or approval semantic change.
- No expansion of stale/latest relation labels into cleanup semantics.

## output summary
- Explain why the next step must be a manual and explicit proposal boundary first.
- Preserve the existing contract that `stale` is only non-latest visibility.
- Define the minimum guardrails any later manual command would need before implementation is considered.

## observed repo facts
- `factory status --root .` reports latest run `RUN-20260327T063724Z`, pending total `2`, and one stale pending item.
- `inspect-approval-queue --root .` reports relation counts `latest: 1`, `stale: 1`, `no_latest_run: 0`, and `unparseable: 0`.
- Pending item `APR-RUN-20260327T055614Z.yaml` maps to [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml), which records `pr_id: PR-003` and `state: approval_pending`.
- Pending item `APR-RUN-20260327T063724Z.yaml` maps to [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml), which records `pr_id: PR-004` and `state: approval_pending`.
- The repo therefore still contains two real pending approval artifacts, not one valid target plus one safe-to-clean artifact.
- Existing contracts already state that older pending approvals may remain visible as stale artifacts and are not auto-delete, auto-resolve, or auto-hide targets.

## proposal
- Start with a manual and explicit proposal because the live repo state still contains simultaneous valid-looking pending approval artifacts across different PR/run histories.
- Preserve the current meaning that `stale` is only "non-latest relative to the latest run" and nothing more.
- If a manual hygiene command is ever proposed for implementation, its target must be explicitly named by the operator, such as a concrete run id or approval request id.
- A future command must not derive mutation targets from `latest`, `stale`, relation counts, status output, or Relation Summary blocks.
- A future command must be dry-run first by default and require a separate explicit apply path for mutation.
- A future command must stay manual. No auto cleanup, auto resolve, readiness gating, or Relation Summary-triggered action is accepted by this proposal.
- If implementation is later approved, it should be split into small PRs so command surface, guardrails, docs, and tests can be reviewed independently.

## non-goals
- No implementation PR in this slice.
- No new CLI command in this slice.
- No change to `factory status` or `inspect-approval-queue`.
- No semantic change to `approval_pending`.
- No stale/latest cleanup interpretation.
- No queue lifecycle change.

## rationale
- Manual-first is required because current visibility signals are informative but not safe selectors.
- `stale` must remain visibility-only because the stale artifact still points to a real run in `approval_pending`.
- Explicit target is required because the repo can show multiple pending approvals across distinct PR contexts at once.
- Dry-run first is required because queue hygiene is inherently destructive if it ever mutates artifacts.
- Small follow-up PRs are required because this topic crosses operator UX, guardrails, docs contracts, and test coverage.

## risks
- Readers may overread this proposal as approval to implement mutation if the proposal-only boundary is ignored.
- An implicit-target command would make stale/latest visibility look like selector semantics, which current contracts reject.
- Skipping dry-run first would create avoidable operator risk around queue artifact mutation.

## next required gate
- Reviewer: accept or reject the guardrails as proposal text only.
- Approver / PM: decide whether to authorize a later implementation design, split into small PRs.
- QA: if implementation is ever approved later, require explicit evidence for dry-run behavior and explicit-target protection.
