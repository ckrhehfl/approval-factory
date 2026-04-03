# PR-069 Start Prompt

Read master and the latest delta as context only, not as runtime source of truth.

Start with `factory status --root .`.

Verify:
- active PR
- latest run
- approval queue state
- stale pending / old pending confusion
- current branch and working tree

Keep the loop:
- branch → Codex 작업 → 검증 → 로그 첨부 → 판정 → (머지 또는 같은 PR 수정)

Treat semantics-adjacent work as proposal first.
Separate one-shot validation from closeout validation.
After merge, delete the local branch.
New PRs should leave at least `docs/prs/PR-###/plan.md` before merge.
