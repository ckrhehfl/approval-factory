# PR-051 Plan

## input refs
- AGENTS.md v2026-04-03
- [docs/prs/PR-050/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-050/plan.md)
- [docs/prs/README.md](/mnt/c/dev/approval-factory/docs/prs/README.md)
- [docs/design/architecture.md](/mnt/c/dev/approval-factory/docs/design/architecture.md)
- [docs/contracts/work-item-contract.md](/mnt/c/dev/approval-factory/docs/contracts/work-item-contract.md)
- [docs/contracts/pr-contract.md](/mnt/c/dev/approval-factory/docs/contracts/pr-contract.md)
- `git log --oneline --decorate -n 40` output observed on 2026-04-03
- `find docs/prs -maxdepth 2 -type f | sort` output observed on 2026-04-03

## scope
- Apply the PR-050 recommended minimal next scope as a docs-only clarification.
- Define the canonical role of `docs/prs`.
- Define the canonical role of `docs/work-items`.
- Align `docs/prs/README.md` and `docs/design/architecture.md` to actual repo/history with minimal wording changes.
- Choose and justify one retro docs policy for PR-040~049.
- Do not change runtime code or execution semantics.

## output summary
- `docs/prs/README.md` now defines `docs/prs/` as canonical PR history/audit trail documentation, not runtime source of truth.
- `docs/design/architecture.md` now distinguishes `docs/work-items/`, `docs/prs/`, and `prs/active|archive` roles.
- PR-040~049 retro docs policy is explicitly set to `README/architecture alignment only`.

## observed facts
- `docs/contracts/work-item-contract.md` defines `docs/work-items/<work-item-id>.md` as the official work item artifact.
- `docs/contracts/pr-contract.md` defines `prs/active/<pr-id>.md` and `prs/archive/<pr-id>.md` as the official PR plan artifacts.
- `find docs/prs -maxdepth 2 -type f | sort` shows `docs/prs/` currently contains mixed historical shapes: some PR directories have seven docs, many later directories have only `plan.md`.
- The same file listing shows no `docs/prs/PR-040` through `docs/prs/PR-049` files in the current tree.
- `git log --oneline --decorate -n 40` shows merge commits corresponding to PR-040 through PR-049 in repository history.

## contract updates
- `docs/prs/` is the canonical documentation surface for PR history and audit trail.
- `docs/work-items/` is the canonical planning surface for official work item artifacts.
- Runtime PR source of truth remains `prs/active/` and `prs/archive/`.
- Recommended PR history-doc shape remains the seven-file set, but existing mixed legacy formats are explicitly acknowledged.
- PR-040~049 retro docs policy is `README/architecture alignment only`.

## rationale for retro docs policy
- Repository history proves that PR-040~049 existed as merged PRs.
- Current tree state does not provide evidence for what per-PR history docs were created, omitted, or intended at the time.
- Creating retro per-PR docs now would risk fabricated history, which is prohibited by this PR scope.
- The minimum safe repair is to align README and architecture wording with the observable repo/history state.

## non-goals
- Do not create fabricated `docs/prs/PR-040` through `docs/prs/PR-049` placeholder records.
- Do not change readiness semantics.
- Do not change approval, queue, activation, or execution semantics.
- Do not modify runtime code.

## risks
- Readers may still over-assume that the recommended seven-file PR doc shape is historically complete across all legacy PRs.
- Other process documents outside the requested scope may still contain older wording until a later docs sync pass addresses them.

## next required gate
- Reviewer: confirm README/architecture wording matches current contracts and does not imply runtime semantic changes.
- Docs Sync / Release: decide whether any additional non-targeted process docs need a later alignment-only pass.
