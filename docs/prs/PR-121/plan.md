# PR-121 Plan

## title
- PR Loop Policy Authority Source Contract Proposal

## input refs
- AGENTS.md working-copy instructions provided for `/mnt/c/dev/approval-factory` on 2026-04-11 KST.
- User task for PR-121 proposal-only policy authority source contract.
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
- [docs/proposals/pr-loop-state-runtime-gate.md](/docs/proposals/pr-loop-state-runtime-gate.md)
- [docs/proposals/README.md](/docs/proposals/README.md)
- [docs/prs/PR-119/plan.md](/docs/prs/PR-119/plan.md)
- [docs/prs/PR-120/plan.md](/docs/prs/PR-120/plan.md)

## scope
- Add a proposal-only PR Loop policy authority source contract under `docs/proposals`.
- Separate current landed facts, non-goals/rejected options, proposed policy source-of-truth candidates, policy snapshot/versioning/stale invalidation constraints, exception/override/approval boundary, and prerequisite gates before implementation.
- Link the new proposal from the proposal README.
- Add this minimal PR-121 plan.

## non-goals
- No orchestrator or PR Loop runtime code changes.
- No live `artifacts/pr_loop` creation.
- No fixture promotion from `tests/fixtures/pr_loop` into live runtime state or policy authority.
- No policy loader, policy snapshot reader, policy cache, state core/init implementation, merge authority, apply semantics, queue/status/readiness semantic change, or official pack update.
- No use of `runs/latest`, `approval_queue`, `docs/prs`, inspect/readiness/status/trace/debug output, rendered review text, gate-check output, or dry-run summary as policy decision input.

## output summary
- Add `docs/proposals/pr-loop-policy-authority-source-contract.md`.
- Update `docs/proposals/README.md` with the new proposal link.
- Add this minimal PR-121 plan.

## ADR decision
- ADR required now: no for this proposal-only documentation PR.
- Approval required before ADR-free runtime authority: yes. Before any policy loader, policy snapshot reader, policy-backed gate, exception/override runtime behavior, state transition, phase-machine behavior, merge authority, or apply implementation, Architect and Approver / PM must decide whether a formal ADR or separate prerequisite proposal is required.

## risks
- If proposal wording is treated as approved runtime policy, future code may load policy before a source-of-truth contract is selected.
- If fixture snapshots or visibility output are promoted, test/reference material could become unapproved policy decision input.
- If exception handling is left implicit, overrides could bypass approval-first boundaries or stale invalidation.

## next required gate
- Reviewer: confirm this PR is limited to proposal docs and does not change runtime code, fixtures, CLI semantics, queue/status/readiness behavior, live artifacts, official packs, policy loader behavior, state authority, merge authority, or apply semantics.
- Architect: decide ADR need before policy authority implementation.
- Approver / PM: approve or reject the policy source-of-truth and exception boundary before implementation begins.
