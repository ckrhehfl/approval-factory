# PR-082 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-05
- User task for PR-082 Stage 3 apply support
- `git status -sb`
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- [orchestrator/cli.py](/orchestrator/cli.py)
- [orchestrator/pipeline.py](/orchestrator/pipeline.py)
- [tests/test_cli.py](/tests/test_cli.py)
- [docs/prs/PR-080/plan.md](/docs/prs/PR-080/plan.md)
- [docs/prs/PR-081/plan.md](/docs/prs/PR-081/plan.md)
- [docs/prs/PR-077/proposal.md](/docs/prs/PR-077/proposal.md)

## scope
- Add Stage 3 `--apply` support for `factory hygiene-approval-queue`.
- Reuse the PR-080 selector parser and the PR-081 exact pending target resolution.
- Require exactly one selector family and exactly one mode: `--dry-run` or `--apply`.
- Keep dry-run-first wording explicit in help, UX, and tests.
- Limit apply mutation to the single resolved pending queue artifact only.
- Do not add cleanup semantics, auto-resolve semantics, or broad queue mutation.

## output summary
- Upgrade the CLI surface from Stage 2 dry-run only to Stage 3 dry-run/apply with required mutual exclusivity.
- Reuse the same exact target identity for both dry-run and apply paths.
- Implement apply as a safe target-local metadata mutation on the single resolved queue artifact only.
- Preserve refusal behavior for missing or conflicting selectors or modes, malformed selectors, heuristic selectors, missing targets, and ambiguous targets.
- Add focused tests for help discoverability, dry-run/apply acceptance, refusal coverage, and exact-target-only mutation.

## risks
- Because PR-077 never approved cleanup or resolve semantics, apply must remain narrower than queue removal or lifecycle mutation.
- Retry-suffixed duplicate pending artifacts remain an ambiguity case and must continue to refuse instead of guessing.
- Dry-run-first is enforced by help/tests/message contract, but the command still cannot prove a prior dry-run invocation occurred in a separate process.

## next required gate
- Reviewer: confirm PR-080 selector parsing and PR-081 exact target resolution are reused without selector or queue-scan expansion.
- QA: verify dry-run/apply acceptance and refusal cases on a temp root and confirm only the exact target artifact changes on apply.
- Docs Sync / Release: confirm this PR-local plan is sufficient because broader queue/operator semantics remain unchanged.
