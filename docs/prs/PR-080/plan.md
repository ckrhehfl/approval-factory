# PR-080 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-05
- User task for PR-080 parser-only support
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- [orchestrator/cli.py](/orchestrator/cli.py)
- [orchestrator/pipeline.py](/orchestrator/pipeline.py)
- [tests/test_cli.py](/tests/test_cli.py)
- [docs/prs/PR-075/proposal.md](/docs/prs/PR-075/proposal.md)

## scope
- Add Stage 1 parser-only CLI surface for `factory hygiene-approval-queue`.
- Accept exactly one explicit selector family: `--run-id <RUN-...>` or `--approval-id <APR-RUN-...>`.
- Reject missing selectors, dual selectors, malformed selector values, and heuristic or pseudo selector values.
- Keep queue inspection semantics, stale/latest visibility wording, and relation summary behavior read-only.

## output summary
- Add parser-only command registration and help discoverability for `hygiene-approval-queue`.
- Add exact selector validation helpers and parser-only acceptance output that reports the canonical `run_id` and `approval_id`.
- Add focused CLI tests for acceptance, refusal, help discoverability, and no-mutation behavior on a temp root.
- Keep dry-run, apply, cleanup, and queue mutation semantics unimplemented.

## contract
- The command is parser-only in this PR.
- The command does not mutate approval queue artifacts, run artifacts, or decision artifacts.
- The command does not implement `--dry-run`.
- The command does not implement `--apply`.
- The command does not implement cleanup or resolution semantics.
- `latest`, `stale`, and relation summary remain operator visibility only and are not accepted as selector shorthand.

## validation
- Add tests for:
- help discoverability
- exact `--run-id` acceptance
- exact `--approval-id` acceptance
- refusal when neither selector is provided
- refusal when both selectors are provided
- refusal for malformed run id
- refusal for malformed approval id
- refusal for heuristic or pseudo run id
- refusal for heuristic or pseudo approval id
- no-mutation check on a temp root
- Run one-shot execution validation on a temp root for accepted, refused, and no-mutation cases.
- Run full closeout validation with `git status --short`, `git diff --stat`, `git diff --name-only`, and `PYTHONPATH=. pytest -q`.

## risks
- Future work could accidentally treat parser acceptance as approval for dry-run or apply behavior unless the parser-only boundary stays explicit.
- Selector validation could drift if later changes silently broaden acceptable token shapes or allow heuristic shorthands.

## next required gate
- Reviewer: confirm the new command remains parser-only and does not introduce queue mutation semantics.
- QA: verify accepted exact selectors succeed, heuristic selectors fail, and temp-root contents remain unchanged.
- Docs Sync / Release: confirm this PR-local plan is sufficient because broader operator semantics remain unchanged.
