# PR-050 Plan

## input refs
- AGENTS.md v2026-04-03
- `git log --oneline --decorate --graph --max-count=20` output observed on 2026-04-03
- [docs/prs/README.md](/docs/prs/README.md)
- [docs/prs/PR-039/plan.md](/docs/prs/PR-039/plan.md)
- `rg --files docs/prs docs/work-items` output observed on 2026-04-03
- `find docs/prs -maxdepth 2 -type f | sort` output observed on 2026-04-03

## scope
- Add a docs-only proposal for PR/documentation history-contract drift around PR-040~049.
- Record only repo/log-backed observations and explicitly separate them from interpretation.
- Recommend a docs-only follow-up path first.
- Do not change runtime behavior, readiness, gate, approval, queue, or selector semantics.

## output summary
- This PR adds an operator-facing proposal that frames the current issue as documentation/history-contract drift first.
- The proposal avoids claiming missing runtime behavior from missing PR docs alone.
- The proposal narrows the next step to clarifying doc roles and deciding whether retro docs are required.

## observed facts from repo/log output
- `git log --oneline --decorate --graph --max-count=20` shows merge commits for PR-040 through PR-049 in git history.
- The same log shows `main` and `HEAD` at commit `efd7076`, a merge commit titled `Merge pull request #45 from ckrhehfl/pr/049-build-approval-next-step-ux`.
- The log includes merge commits down through `7a61956`, titled `Merge pull request #36 from ckrhehfl/pr/040-pr-plan-draft-next-step-ux`.
- `rg --files docs/prs docs/work-items` and `find docs/prs -maxdepth 2 -type f | sort` show `docs/prs` currently stops at `docs/prs/PR-039/plan.md`.
- The same file listings show `docs/work-items` currently stops at `docs/work-items/WI-039-promote-pr-plan-draft.md`.
- [docs/prs/README.md](/docs/prs/README.md) states that each PR has seven documents: `scope.md`, `plan.md`, `review.md`, `qa.md`, `docs-sync.md`, `evidence.md`, and `decision.md`.
- The actual `docs/prs` tree has mixed historical formats.
- Early entries such as [docs/prs/PR-001/plan.md](/docs/prs/PR-001/plan.md) sit alongside full 7-document PR directories such as `PR-001`, `PR-002`, `PR-003`, `PR-004`, `PR-005`, and `PR-006`.
- Many later entries, including [docs/prs/PR-039/plan.md](/docs/prs/PR-039/plan.md), exist as `plan.md`-only directories.
- No `docs/prs/PR-040` through `docs/prs/PR-049` files appear in the current repo tree listing.

## interpretations
- The repo currently shows a mismatch between documented `docs/prs` structure and actual stored PR-history artifacts.
- Based on repo state alone, this mismatch is best treated first as documentation/history-contract drift.
- Repo state does not, by itself, prove an immediate runtime feature absence for PR-040~049.
- Any stronger claim about why PR-040~049 docs are missing, or what process was intended at the time, would require evidence not present in the observed repo/log output above.

## candidate follow-up options
- Option A: docs-only clarification PR that defines the canonical role of `docs/prs`, defines the canonical role of `docs/work-items`, and aligns README/architecture/process docs without creating retro PR-040~049 records.
- Option B: docs-only clarification PR plus explicit policy for whether PR-040~049 require retro docs placeholders, concise retro plans, or no per-PR backfill.
- Option C: docs-only clarification PR first, followed by a separate approval step that decides whether retro docs should be added for PR-040~049 after the contract is clarified.

## recommended minimal next PR scope
- Keep the next PR docs-only.
- Clarify the canonical role of `docs/prs`.
- Clarify the canonical role of `docs/work-items`.
- Clarify whether PR-040~049 require retro docs, README/architecture alignment only, or both.
- Limit the first follow-up to contract and history-alignment wording; do not change runtime behavior or infer missing historical facts as if they were certain.

## risks
- If the follow-up mixes documentation repair with runtime work, operators may read a history-contract cleanup as a semantics change.
- If retro docs are created before the contract is clarified, the repo may gain fabricated or misleading history.
- If README/process docs are updated without explicitly addressing the mixed historical formats already present, the drift may remain ambiguous.

## next required gate
- Approver / PM: confirm that PR-050 stays docs-only and treats this as documentation/history-contract drift first.
- Architect: decide whether canonical source-of-truth wording for `docs/prs` and `docs/work-items` needs ADR-level treatment.
- Docs Sync / Release: prepare the minimal docs-only follow-up scope and avoid retroactive factual claims not supported by repo/log evidence.
