# PR-094 Plan

## Input Refs
- AGENTS.md working-copy version observed on 2026-04-06
- User task for `pr/094-agents-review-guidelines`
- Repo source-of-truth reviewed from current branch working tree and PR docs layout

## Title
- Forward-Minimum PR History Note for AGENTS Review Guideline Hardening

## Scope
- Add the missing forward-minimum PR history note for PR-094 in docs only.
- Record the actual AGENTS.md wording changes already present on this branch.
- Do not change runtime code, tests, README, AGENTS semantics beyond describing the current documented contract, or pack files.

## What changed
- AGENTS.md now states a source-of-truth first priority where repo code, tests, git history, and runtime artifacts come before other references.
- AGENTS.md now states that official runtime artifacts and official repo docs are secondary, while `docs/prs` and external handoff packs are reference material only.
- Review guidance now requires findings-first review output, with material issues, risk, and missing evidence recorded before summary.
- Review triage is now risk-based through `review-required`, `review-optional`, and `review-skip`.
- Evidence collection now distinguishes auxiliary user-pasted terminal output from primary evidence collected by Codex through direct command execution.
- Review mode boundaries now explicitly distinguish working-tree review from committed-range review.

## What did not change
- No runtime semantics changed.
- No runtime code, tests, or README files changed for this follow-up note.
- No pack files changed.
- This note does not reinterpret `docs/prs` or handoff packs as primary source-of-truth inputs.

## Why this update was needed
- PR-094 branch state already contains the AGENTS.md review-guideline and evidence-rule wording, but the PR history note was missing.
- Adding this note preserves code-doc sync for the current branch and makes the branch history explicit without widening scope or restating unrelated timeline detail.

## Validation summary
- Verified the current branch working tree directly from repo source-of-truth.
- Confirmed AGENTS.md contains the source-of-truth ordering, findings-first review guidance, risk-based review triage, auxiliary-versus-primary evidence distinction, and explicit working-tree versus committed-range review split.
- Confirmed this follow-up changes only `docs/prs/PR-094/plan.md`.

## Risks / follow-up note
- Residual wording risk remains if later edits paraphrase these AGENTS.md rules too loosely and blur the distinction between reference material and primary evidence.
- Follow-up should stay limited to wording sync unless a later approved PR intentionally changes review or evidence policy.

## Next Required Gate
- Reviewer: confirm this note reflects the current AGENTS.md branch content without expanding behavior claims.
- Docs Sync / Release: confirm PR-094 history is now present and remains docs-only.
