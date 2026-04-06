# PR-070 Proposal

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- `factory status --root .`
- `factory inspect-approval-queue --root .`
- [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml)
- [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml)
- [approval_queue/pending/APR-RUN-20260327T055614Z.yaml](/approval_queue/pending/APR-RUN-20260327T055614Z.yaml)
- [approval_queue/pending/APR-RUN-20260327T063724Z.yaml](/approval_queue/pending/APR-RUN-20260327T063724Z.yaml)

## scope
- Proposal-only clarification for stale pending visibility and approval queue hygiene.
- No code, runtime, test, CLI, or queue artifact change.
- No mutation design acceptance.

## output summary
- Clarify how `stale` should be read in the current system.
- Preserve the contract that `docs/prs` is history and audit trail, not cleanup control.
- Keep any future hygiene automation or mutation discussion out of this PR.

## observed repo facts
- `factory status --root .` reports active PR `none`, latest run `RUN-20260327T063724Z`, and `pending_total: 2`.
- `factory inspect-approval-queue --root .` reports relation counts `latest: 1`, `stale: 1`, `no_latest_run: 0`, and `unparseable: 0`.
- Pending item `APR-RUN-20260327T055614Z.yaml` parses to run `RUN-20260327T055614Z`, relation `stale`, matching run present, matching run state `approval_pending`.
- Pending item `APR-RUN-20260327T063724Z.yaml` parses to run `RUN-20260327T063724Z`, relation `latest`, matching run present, matching run state `approval_pending`.
- [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml) records `pr_id: PR-003`.
- [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml) records `pr_id: PR-004`.
- The queue therefore contains two distinct pending approvals for two different PR/run histories.

## proposal
- Conclude that `stale` is a non-latest visibility label only.
- State explicitly that `stale` is not a cleanup semantic.
- State explicitly that `stale` must not be interpreted as obsolete or safe to delete.
- Preserve the current read-only meaning of queue inspection output.
- Preserve `docs/prs` as a history and audit-trail surface rather than a runtime control plane.

## non-goals
- No auto cleanup proposal.
- No auto resolve proposal.
- No queue mutation proposal.
- No readiness gating proposal.
- No semantic change to `approval_pending`.

## deferred follow-up
- If hygiene assistance is pursued later, treat it as a separate proposal for an explicit manual hygiene command.
- Any such later step should be evaluated independently from PR-070 and should not be inferred from the existence of a `stale` label.

## risks
- Without an explicit note, reviewers may infer deletion safety from a visibility label.
- Because both queue items still map to real runs in `approval_pending`, a cleanup interpretation would exceed the current contract.
- Mixing proposal text with mutation language would blur audit-trail docs and runtime semantics.

## next required gate
- Reviewer: accept or reject the wording as a docs-only clarification, not as behavior change approval.
- Approver / PM: decide whether any separate manual hygiene proposal should be opened later.
