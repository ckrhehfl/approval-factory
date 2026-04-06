# PR-083 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-05
- User task for PR-083 Stage 4 docs/help/tests follow-up
- `git status -sb`
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- [orchestrator/cli.py](/orchestrator/cli.py)
- [tests/test_cli.py](/tests/test_cli.py)
- [README.md](/README.md)
- [docs/design/architecture.md](/docs/design/architecture.md)
- [docs/prs/PR-082/plan.md](/docs/prs/PR-082/plan.md)

## scope
- Tighten user-facing help, read-only guidance, and focused tests for the already-implemented `factory hygiene-approval-queue` Stage 1/2/3 behavior.
- Keep selector semantics exact-target only: `--run-id` or `--approval-id`.
- Keep mode semantics exact and mutually exclusive: `--dry-run` or `--apply`.
- Document dry-run-first operator guidance and exact-target-only mutation scope.
- Do not change runtime semantics, selector resolution, dry-run/apply behavior, cleanup semantics, or auto-resolve semantics.

## output summary
- Clarify the CLI help and command summaries so operators see exact selector family, exact mode family, dry-run-first guidance, and non-goals in one place.
- Add README and architecture notes that stale/latest and Relation Summary remain read-only visibility and are not hygiene selectors.
- Add focused tests that lock the help/output contract to the PR-082 runtime behavior without expanding the command surface.
- Add this PR-local note as the minimum history-doc artifact for PR-083.

## risks
- Help/output wording must not imply a broader cleanup or queue-management workflow than the current implementation actually supports.
- Tests should document refusal/acceptance boundaries without overspecifying incidental formatting outside the contract lines.
- Because docs are contracts here, wording drift could accidentally suggest stale/latest selectors or implicit cleanup if phrased loosely.

## next required gate
- Reviewer: confirm the change is docs/help/tests-only in spirit and that no runtime selector or apply semantics changed.
- QA: run the required one-shot execution validation and full pytest closeout, including exact-target-only mutation confirmation.
- Docs Sync / Release: confirm README, architecture, and PR-local note stay aligned with the existing Stage 3 implementation.
