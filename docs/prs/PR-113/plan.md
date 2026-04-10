# PR-113 Plan

## title
- PR Loop Runner Inert Artifact Fixture Examples

## input refs
- AGENTS.md working-copy instructions provided for `/mnt/c/dev/approval-factory` on 2026-04-10
- User task for PR-SLOT-2 inert fixture/examples follow-up
- `docs/proposals/pr-loop-runner.md` at `main` / `origin/main` commit `3e495e0`
- `git --no-pager log --oneline --decorate -12`
- `git status -sb`
- `tests/test_cli.py`
- `tests/test_pipeline_approval_loop.py`
- `orchestrator/yaml_io.py`
- `docs/proposals/README.md`

## scope
- Add inert fixture/example files for the proposed future `artifacts/pr_loop/<PR-ID>/...` layout.
- Keep all example artifacts under `tests/fixtures/pr_loop/` so they are not live runtime artifacts.
- Add a low-level test that verifies fixture manifest metadata, required files, and required fields/text only.
- Minimally clarify the proposal that PR-SLOT-2 is an inert schema/fixture follow-up and does not introduce runtime authority.

## non-goals
- No `orchestrator/pr_loop/` runtime package.
- No state runtime core, state load/save, phase machine, CLI command, merge gate, queue, approval, status, or run pipeline change.
- No top-level `artifacts/pr_loop/<PR-ID>/...` active state.
- No use of `docs/prs/` as runtime source of truth.

## output summary
- Add `tests/fixtures/pr_loop/schema/pr-loop-artifact-manifest.yaml`.
- Add `tests/fixtures/pr_loop/examples/artifacts/pr_loop/PR-113/...` fixture files for the proposed future layout.
- Add `tests/test_pr_loop_fixture_examples.py` for low-level fixture integrity checks.
- Add this PR note to record scope, risks, and ADR decision.

## ADR decision
- ADR required now: no.
- Reason: this PR adds inert fixtures and tests only; it does not establish runtime authority, approved policy source, merge authority, or architecture-changing code.
- Approval required before ADR-free runtime authority: yes. Any future PR that introduces runtime authority, `orchestrator/pr_loop/`, state load/save behavior, phase-machine behavior, CLI mutation/read behavior, or merge gate semantics must re-evaluate ADR need before implementation.

## risks
- If fixture paths are moved to top-level `artifacts/`, they may be mistaken for live runtime state.
- If tests begin interpreting fixture state as behavior, PR-SLOT-2 may accidentally become state runtime core.
- If proposal wording is read without the fixture boundary, later work may cite PR-SLOT-2 as runtime authority.

## next required gate
- Reviewer: confirm the diff is limited to inert fixtures, low-level fixture tests, and proposal/PR notes.
- Approver / PM: decide whether PR-SLOT-3 may proceed after this fixture-only PR lands.
- Docs Sync / Release: confirm proposal and PR notes are aligned with the fixture-only implementation.
