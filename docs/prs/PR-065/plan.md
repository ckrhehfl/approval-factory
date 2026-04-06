# PR-065 Plan

## input refs
- AGENTS.md v2026-04-03
- [pyproject.toml](/pyproject.toml)
- [orchestrator/cli.py](/orchestrator/cli.py)
- [tests/test_cli.py](/tests/test_cli.py)
- User request for PR-065 observed on 2026-04-03

## scope
- Close the UX gap where `python -m factory` previously failed because no importable `factory` module entrypoint existed.
- Add only a minimal shim package so `python -m factory` delegates to the existing CLI `main()` implementation.
- Keep runtime semantics, help wording, approval/run/queue/readiness behavior, artifact layout, and stale pending handling unchanged.
- Add only focused subprocess tests for `python -m factory --help` and `python -m factory status --help`, plus an environment-conditional check that the existing `factory` console command still exposes `status --help` when installed.
- Limit documentation to this PR-local plan note.

## output summary
- Add [factory/__main__.py](/factory/__main__.py) as a thin module entrypoint that forwards argv to `orchestrator.cli.main`.
- Add [factory/__init__.py](/factory/__init__.py) and update [pyproject.toml](/pyproject.toml) package discovery so the shim is importable and packageable.
- Extend [tests/test_cli.py](/tests/test_cli.py) with subprocess-based invocation checks for `python -m factory --help` and `python -m factory status --help`.
- Record the unchanged runtime surface and minimal-shim scope in this plan artifact.

## risks
- Even a small shim can accidentally diverge from the console entrypoint if it starts owning CLI logic instead of delegating directly.
- Subprocess checks cover invocation success, but reviewers still need to confirm no unintended wording or semantic drift occurred in existing help output.

## next required gate
- Reviewer: confirm the new module entrypoint only delegates to the existing CLI `main()` and does not introduce new runtime behavior.
- QA: run the focused CLI subprocess tests and verify `python -m factory --help` plus `python -m factory status --help` succeed.
- Docs Sync / Release: confirm docs sync is satisfied by this PR-local plan because product semantics and broader operator docs remain unchanged.
