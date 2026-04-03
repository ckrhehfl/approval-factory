# PR-060 Plan

## input refs
- AGENTS.md v2026-04-03
- [docs/prs/README.md](/mnt/c/dev/approval-factory/docs/prs/README.md)
- [docs/design/architecture.md](/mnt/c/dev/approval-factory/docs/design/architecture.md)
- [docs/ops/how-we-work.md](/mnt/c/dev/approval-factory/docs/ops/how-we-work.md)
- User request for PR-060 observed on 2026-04-03

## scope
- Document a forward-only minimum rule for new PR history notes.
- Keep `docs/prs` positioned as history/audit trail surface, not runtime source of truth.
- Preserve the existing PR-040~049 retro docs policy.
- Add the minimum operator workflow wording where operators can see it.
- Do not backfill PR-053~059 in this PR.
- Do not change runtime code or execution semantics.

## output summary
- `docs/prs/README.md` now states that new PRs must leave at least `docs/prs/PR-###/plan.md` before merge.
- `docs/design/architecture.md` now distinguishes recommended 7-file history shape from the forward minimum `plan.md` requirement.
- `docs/ops/how-we-work.md` now tells operators to leave the minimum `docs/prs/PR-###/plan.md` history note before merge.
- PR-040~049 retro docs policy remains unchanged.
- PR-060 does not include PR-053~059 backfill.

## risks
- Legacy PR directories will remain mixed-shape, so readers can still over-assume historical completeness if they skip the contract wording.
- PR-053~059 remain without history notes until a separate explicitly approved backfill PR is created.

## next required gate
- Reviewer: confirm the wording is forward-only, docs-only, and does not imply runtime semantic changes.
- Docs Sync / Release: confirm no additional docs are required for this minimum-rule PR.
