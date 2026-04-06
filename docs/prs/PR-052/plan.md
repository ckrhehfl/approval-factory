# PR-052 Plan

## input refs
- AGENTS.md v2026-04-03
- [docs/prs/README.md](/docs/prs/README.md)
- [docs/design/architecture.md](/docs/design/architecture.md)
- [docs/prs/PR-051/plan.md](/docs/prs/PR-051/plan.md)
- `grep -RInE 'docs/prs|prs/active|prs/archive|docs/work-items|runtime source of truth|canonical role|audit trail|official PR plan artifact|official work item artifact|planning surface|history' docs/ops docs/policies docs/contracts docs/design AGENTS.md` observed on 2026-04-03

## scope
- Re-check the PR-051 wording contract against the requested candidate docs.
- Find only real wording conflicts before editing anything.
- Align any discovered `docs/prs` wording to history/audit trail semantics only.
- Align any discovered `docs/work-items` versus `prs/active|archive` canonical-role mixups only.

## output summary
- Searched the requested candidate paths first: `docs/ops/`, `docs/policies/`, `docs/contracts/`, `docs/design/`, `AGENTS.md`.
- Reconfirmed the current contract from `docs/prs/README.md` and `docs/design/architecture.md`.
- Did not find additional candidate files that describe `docs/prs/` as a runtime source of truth or that materially mix the canonical roles of `docs/work-items` and `prs/active|archive`.
- Left non-conflicting files unchanged to avoid unsupported broad rewrites.

## observed evidence
- `docs/design/architecture.md` already states that `docs/prs/` is not a runtime source of truth and that official PR plan artifacts live in `prs/active/` and `prs/archive/`.
- `docs/ops/runbook.md` and `docs/ops/how-we-work.md` mention `docs/prs/` only as preserved history during cleanup, not as runtime input.
- `docs/contracts/`, `docs/ops/`, and `docs/design/` search hits consistently describe `docs/work-items/<work-item-id>.md` as the official work item artifact and `prs/active/<pr-id>.md` or `prs/archive/<pr-id>.md` as official PR plan artifacts.
- No searched candidate file was found to require wording correction under this PR scope.

## non-goals
- Do not modify runtime code.
- Do not change readiness, gate, approval, queue, selector, or activation semantics.
- Do not create retro docs for PR-040 through PR-049.
- Do not rewrite candidate docs without direct `grep` evidence of a wording conflict.
- Do not reopen or redefine the README/architecture contract set in PR-051.

## risks
- Some wording outside the requested candidate paths may still use older terminology and would need a later alignment-only pass.
- Future readers may still overgeneralize from legacy `docs/prs/` shapes unless they also read the README/architecture contract.

## next required gate
- Reviewer: confirm the search evidence supports a no-op alignment decision outside this PR history note.
- Docs Sync / Release: decide whether a later wider docs-only pass is needed beyond the requested candidate paths.
