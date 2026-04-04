# PR-073 Start Prompt

Read master and the latest delta as context only, not as runtime source of truth.

Start with `factory status --root .`.
If approval queue context is relevant, run `inspect-approval-queue --root .`.

Do not misread `stale` or `latest` as cleanup semantics.
`matching_pr_id` visibility is now available.
Direct `inspect-approval-queue` entrypoint is now available.

Keep the loop:
- branch → Codex 작업 → 검증 → 로그 첨부 → 판정 → (머지 또는 같은 PR 수정)

Keep proposal-first for semantics-adjacent changes.
Separate one-shot validation from closeout validation.
After merge, delete the local branch.
Before merge, leave at least `docs/prs/PR-###/plan.md`.
