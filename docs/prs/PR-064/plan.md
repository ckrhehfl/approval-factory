# PR-064 Plan

## input refs
- AGENTS.md v2026-04-03
- [docs/prs/PR-063/plan.md](/docs/prs/PR-063/plan.md)
- [orchestrator/cli.py](/orchestrator/cli.py)
- [tests/test_cli.py](/tests/test_cli.py)
- User request for PR-064 observed on 2026-04-03

## scope
- Add small operator-assist help discoverability for `create-goal`, `create-clarification`, `resolve-clarification`, `create-work-item`, `work-item-readiness`, `cleanup-rehearsal`, and `bootstrap-run`.
- Limit changes to `orchestrator/cli.py`, `tests/test_cli.py`, and this [plan.md](/docs/prs/PR-064/plan.md).
- Preserve runtime behavior and command semantics.
- Add only help-layer `description`, `epilog`, `Next step:`, `Example:`, and focused help-output tests.
- Keep manual/create surfaces framed as operator-managed commands, not as automatic orchestration.
- Keep `work-item-readiness` explicitly visibility-only and avoid describing readiness as a gate.
- Keep `bootstrap-run` and `cleanup-rehearsal` framed as operator-managed repo-local flow support only.

## output summary
- [cli.py](/orchestrator/cli.py) adds descriptions and `Next step:` / `Example:` help epilogs for the seven scoped commands.
- The new help text keeps operator hints explicit without implying auto-execution or semantics changes.
- [test_cli.py](/tests/test_cli.py) adds the seven requested help-output tests covering description, `Next step:`, and `Example:`.
- PR-064 records its own scope and guardrails in this plan artifact.

## risks
- Help wording can accidentally imply orchestration or gating if the operator-hint language becomes too directive.
- Focused tests verify presence, but reviewers still need to check tone so visibility-only commands do not drift into control semantics.

## next required gate
- Reviewer: confirm the scoped commands remain operator-managed help only, `work-item-readiness` stays visibility-only, and no runtime semantics changed.
- QA: run focused CLI help tests for the seven scoped commands and confirm help output contains description, `Next step:`, and `Example:`.
- Docs Sync / Release: confirm no additional docs are required beyond this PR-local plan note because the change is limited to CLI help discoverability.
