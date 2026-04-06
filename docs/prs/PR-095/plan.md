# PR-095 Plan

## Input Refs
- AGENTS.md working-copy version observed on 2026-04-06
- User task for the docs-only corrective follow-up PR after merged PR-083
- `git status -sb`
- `git --no-pager log --oneline --decorate -15`
- repo grep verification for workstation-specific absolute paths under `docs/prs`
- Repo working tree under `docs/prs`

## Title
- Docs-Only Repo-Relative Path Hygiene Correction Under `docs/prs`

## Scope
- Correct workstation-specific absolute paths under `docs/prs` only.
- Replace workstation-specific absolute markdown link targets with repo-root-relative `/...` targets where the existing target is explicit.
- Add this PR-local plan note documenting the corrective scope and docs-only boundary.
- Do not change runtime code, tests, CLI behavior, wording intent, or any non-matching files outside `docs/prs`.
- Do not reinterpret or amend merged PR-083; record this as the next narrow corrective PR.

## Output Summary
- Verified the absolute-path issue is repeated across multiple `docs/prs` files, not isolated to `docs/prs/PR-083/plan.md`.
- Normalized matching markdown links in affected `docs/prs` files from workstation-specific absolute paths to repo-root-relative links.
- Kept the change set mechanical and limited to path hygiene only.
- Added `docs/prs/PR-095/plan.md` as the corrective follow-up note for this docs-only PR.

## Risks
- Historical PR docs remain numerous, so any future copy-forward from older notes could reintroduce workstation-specific paths if link hygiene is not preserved.
- This correction intentionally avoids non-explicit workstation-path rewrites; if such cases appear later, they should be reviewed separately rather than inferred.

## Next Required Gate
- Reviewer: confirm the diff is limited to repo-relative path hygiene under `docs/prs` plus this PR-local note.
- Docs Sync / Release: confirm no additional docs sync is required beyond recording this corrective follow-up in `docs/prs/PR-095/plan.md`.
