# PR-084 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-05
- User task for PR-084 proposal-only semantics freeze for `queue_hygiene` metadata
- `git status -sb`
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- [README.md](/mnt/c/dev/approval-factory/README.md)
- [docs/prs/README.md](/mnt/c/dev/approval-factory/docs/prs/README.md)
- [docs/prs/PR-080/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-080/plan.md)
- [docs/prs/PR-081/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-081/plan.md)
- [docs/prs/PR-082/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-082/plan.md)
- [docs/prs/PR-083/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-083/plan.md)
- [orchestrator/cli.py](/mnt/c/dev/approval-factory/orchestrator/cli.py)
- [orchestrator/pipeline.py](/mnt/c/dev/approval-factory/orchestrator/pipeline.py)
- [tests/test_cli.py](/mnt/c/dev/approval-factory/tests/test_cli.py)

## scope
- PR-084 is docs-only and proposal-only.
- Freeze the current meaning of `queue_hygiene` metadata written by `factory hygiene-approval-queue --apply`.
- Clarify what `queue_hygiene` means now and what it does not mean now.
- Keep `queue_hygiene` explicitly separate from cleanup, auto-resolve, approval decision, readiness/gate, and selector semantics.
- Do not change runtime behavior, CLI output, tests, queue artifacts, or implementation code.

## output summary
- Add this PR-local plan as the scope and validation contract for the proposal-only slice.
- Add [docs/prs/PR-084/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-084/proposal.md) to freeze the current operator meaning of `queue_hygiene`.
- Record the follow-up split so any later visibility work stays read-only and any semantic expansion requires separate approval.

## current repo snapshot
- Branch is `pr/084-queue-hygiene-metadata-semantics`.
- `git status -sb` shows only unrelated untracked PR-083 docs before this PR-local doc work.
- `python -m factory status --root .` reports latest run `RUN-20260327T063724Z`, pending total `2`, and one stale pending item.
- `python -m factory inspect-approval-queue --root .` reports Relation Summary counts `latest: 1`, `stale: 1`, `no_latest_run: 0`, `unparseable: 0`.
- Current runtime writes `queue_hygiene` only inside the exact target queue artifact and only on apply.
- Current CLI wording already says mutation is "queue_hygiene metadata updated on the exact target queue artifact only".

## contract
- `queue_hygiene` currently means an operator-audit marker attached to one exact pending queue artifact that was explicitly targeted by `hygiene-approval-queue --apply`.
- `queue_hygiene` does not currently mean cleanup completed, approval resolved, approval decided, queue eligibility changed, readiness/gate changed, stale/latest changed, or selector state stored.
- `queue_hygiene` does not affect `factory status` approval queue counts, `inspect-approval-queue` relation labels, Relation Summary, stale/latest visibility, or `resolve-approval` behavior.
- If surfaced later in `status` or `inspect`, it must be read-only visibility only unless a separately approved PR expands semantics.

## validation
- Proposal validation must confirm no runtime code paths changed.
- Proposal validation must confirm the proposal explicitly states that `queue_hygiene` is not cleanup, not auto-resolve, not approval decision semantics, not readiness/gate semantics, and not selector semantics.
- Proposal validation must confirm the proposal explains the relation to `factory status`, `inspect-approval-queue`, Relation Summary, and stale/latest visibility.
- Closeout validation must report `git status --short`, `git --no-pager diff --stat`, and `git --no-pager diff --name-only`.

## risks
- Without an explicit semantics freeze, readers may overread `queue_hygiene` as a cleanup completion flag or a resolve signal.
- If selector and visibility concepts are not separated now, later UX work could accidentally treat stale/latest output or Relation Summary as executable hygiene state.
- If read-only visibility follow-up is not split from semantics expansion, status/inspect output could imply runtime meaning that current code does not enforce.

## next required gate
- Reviewer: confirm the PR is docs-only and freezes meaning without approving new runtime semantics.
- Approver / PM: decide whether later read-only visibility for `queue_hygiene` should be authorized as a separate PR.
- Docs Sync / Release: confirm PR-local docs are sufficient because no runtime/document contract outside this PR is being changed.
