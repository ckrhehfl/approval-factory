# PR-120 Plan

## title
- PR Loop State Runtime Gate Proposal

## input refs
- AGENTS.md working-copy instructions provided for `/mnt/c/dev/approval-factory` on 2026-04-11 KST.
- User task for PR-120 proposal-only state runtime gate / ADR-equivalent boundary.
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline --decorate -10`
- `test -f AGENTS.md && echo present || echo missing`
- `python -m factory pr-loop inspect --root . --pr-id PR-113`
- `python -m factory pr-loop gate-check --root . --pr-id PR-113`
- `python -m factory pr-loop render-review --root . --pr-id PR-113`
- `python -m factory pr-loop merge --root . --pr-id PR-113 --dry-run`
- `test -d artifacts && find artifacts -maxdepth 3 -type f | sort | head -50 || echo artifacts_dir_absent`
- [docs/proposals/pr-loop-runner.md](/docs/proposals/pr-loop-runner.md)
- [docs/proposals/pr-loop-live-runtime-authority-contract.md](/docs/proposals/pr-loop-live-runtime-authority-contract.md)
- [docs/proposals/README.md](/docs/proposals/README.md)
- [docs/prs/PR-119/plan.md](/docs/prs/PR-119/plan.md)

## scope
- Add a proposal-only PR Loop state runtime gate document under `docs/proposals`.
- Separate current landed facts, non-goals/rejected options, proposed live state namespace, state owner/initializer authority, versioning/invalidation/migration constraints, and prerequisite gates before implementation.
- Link the new proposal from the proposal README.
- Add this minimal PR-120 plan as PR audit context.

## non-goals
- No orchestrator or PR Loop runtime code changes.
- No live `artifacts/pr_loop` creation.
- No fixture promotion from `tests/fixtures/pr_loop` into live runtime state.
- No CLI semantic expansion and no `init`-style command implementation.
- No state core, phase machine, policy authority, merge authority, dry-run/apply authority, queue/status/readiness semantic change, or official pack update.
- No use of inspect/readiness/status/trace/debug output as state transition decision input.

## output summary
- Add `docs/proposals/pr-loop-state-runtime-gate.md`.
- Update `docs/proposals/README.md` with the new proposal link.
- Add this minimal PR-120 plan.

## ADR decision
- ADR required now: no for this proposal-only documentation PR.
- Approval required before ADR-free runtime authority: yes. Before any live `artifacts/pr_loop/<PR-ID>/state.yaml`, initializer, state transition, invalidation, migration, policy authority, dry-run/apply authority, or merge authority implementation, Architect and Approver / PM must decide whether a formal ADR or separate prerequisite proposal is required.

## risks
- If proposal wording is too broad, readers may treat `artifacts/pr_loop/<PR-ID>/state.yaml` as already-authorized runtime state.
- If initializer authority is left implicit, future `init`-style commands could create live state without approved ownership.
- If versioning, invalidation, and migration rules are deferred into code, stale observations or fixture data may be mistaken for live decision input.

## next required gate
- Reviewer: confirm this PR is limited to proposal docs and does not change runtime code, fixtures, CLI semantics, approval queue/status/readiness behavior, live artifacts, or official packs.
- Architect: decide ADR need before state runtime implementation.
- Approver / PM: approve or reject the state runtime gate before implementation begins.
