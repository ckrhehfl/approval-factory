# PR-087 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-05
- User task for PR-087 proposal-only wording verification and operator misread risk
- `git status -sb`
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- [docs/prs/PR-085/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-085/plan.md)
- [docs/prs/PR-085/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-085/proposal.md)
- [docs/prs/PR-086/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-086/plan.md)

## scope
- PR-087 is proposal-only and docs-only.
- Clarify the wording verification standard for `queue_hygiene_audit` in `inspect-approval-queue`.
- Define the operator misreadings that the wording must prevent.
- Decide whether current warning wording is sufficient, too weak, or too dense.
- Keep the proposal explicitly separate from cleanup semantics, resolve semantics, approval decision semantics, readiness/gate semantics, selector semantics, stale/latest relation semantics, and Relation Summary semantics.
- Do not change runtime behavior, inspect output in code, tests, or queue artifacts in this PR.

## output summary
- Add this PR-local plan as the contract for a wording-verification-only proposal.
- Add [docs/prs/PR-087/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-087/proposal.md) to define safe vs unsafe wording patterns, required anti-misread coverage, and future evidence requirements.
- Keep any future output wording refinement separate from semantics expansion and separate from this proposal PR.

## current repo snapshot
- Branch is `pr/087-queue-hygiene-wording-verification-proposal`.
- `git status -sb` was clean before this PR-local docs work.
- `python -m factory status --root .` currently exposes queue summary facts and must remain unchanged in this PR.
- `python -m factory inspect-approval-queue --root .` currently exposes Relation Summary and per-item pending approval details.
- PR-085 decided placement boundaries: `inspect-approval-queue` only, per-item only, no `factory status` exposure, no summary/count visibility.
- PR-086 implemented read-only item-local rendering with warning wording, so the next risk is wording overread rather than missing runtime functionality.

## contract
- The proposal must list the exact operator misreadings that `queue_hygiene_audit` wording must prevent.
- The proposal must classify wording patterns as safe or unsafe and keep them narrowly tied to read-only operator visibility.
- The proposal must judge the current warning wording as sufficient, too weak, or too dense.
- The proposal must define what evidence would count as operator-safe wording in a later refinement or implementation PR.
- The proposal must state whether any next step should be docs/help/tests-only first, output wording refinement, or no change needed.
- The proposal must not approve runtime semantics expansion.

## validation
- Proposal validation must confirm no runtime code paths changed.
- Proposal validation must confirm the proposal explicitly lists misreadings to prevent.
- Proposal validation must confirm the proposal explicitly keeps `queue_hygiene_audit` read-only only.
- Proposal validation must confirm the proposal separates any later wording tweak from cleanup/resolve/decision/gate/selector/latest-summary semantics.
- Closeout validation must report `git status --short`, `git --no-pager diff --stat`, and `git --no-pager diff --name-only`.

## risks
- If wording is short but ambiguous, operators may overread it as decision-state guidance.
- If wording is exhaustive but too dense, operators may skim past the boundary and still infer cleanup or resolve meaning.
- If future refinement is not split from semantics expansion, a wording-only follow-up could accidentally approve broader behavior.

## next required gate
- Reviewer: confirm the proposal stays proposal-only and targets wording verification rather than behavior change.
- Approver / PM: decide whether a later follow-up should be docs/help/tests-only first, output wording refinement, or no change.
- QA: require operator-safe wording evidence before any later output wording change is accepted.
