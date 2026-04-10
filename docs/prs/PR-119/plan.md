# PR-119 Plan

## title
- PR Loop Live Runtime Authority Contract Proposal

## input refs
- AGENTS.md working-copy instructions provided for `/mnt/c/dev/approval-factory` on 2026-04-11 KST.
- User task for PR-119 proposal-only authority-boundary / ADR-equivalent refresh.
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
- [docs/proposals/README.md](/docs/proposals/README.md)

## scope
- Add a proposal-only live runtime authority contract for PR Loop.
- Separate current landed facts, rejected options/non-goals, proposed authority model, open questions, and prerequisite implementation gates.
- Keep `docs/proposals` as the proposal surface and link the new proposal from the proposal README.

## non-goals
- No orchestrator or PR Loop runtime code changes.
- No fixture promotion from `tests/fixtures/pr_loop` into live runtime state.
- No CLI semantic expansion.
- No state core, gate core, merge apply, queue/status/readiness semantic change, or official pack update.
- No use of inspect/readiness/status/trace/debug output as decision authority.

## output summary
- Add `docs/proposals/pr-loop-live-runtime-authority-contract.md`.
- Update `docs/proposals/README.md` with the new proposal link.
- Add this minimal PR-119 plan as PR audit context.

## ADR decision
- ADR required now: no for this proposal-only documentation PR.
- Approval required before ADR-free runtime authority: yes. Before any live `artifacts/pr_loop/<PR-ID>` state, policy authority, phase-machine behavior, deterministic gate evidence, merge request, or merge apply implementation, Architect and Approver / PM must decide whether a formal ADR or separate prerequisite proposal is required.

## risks
- If the proposal wording is too broad, readers may treat future live artifact paths as already authorized runtime state.
- If policy source-of-truth remains unresolved during implementation, code may accidentally rely on docs, queues, status, trace/debug, rendered text, or fixtures.
- If dry-run/apply separation is not explicit, a read-only merge summary may be mistaken for merge authority.

## next required gate
- Reviewer: confirm this PR is limited to proposal docs and does not change runtime code, fixtures, CLI semantics, approval queue/status/readiness meaning, or official packs.
- Architect: decide ADR need before implementation.
- Approver / PM: approve or reject the authority model before live runtime work begins.
