# PR-106 Proposal

## input refs
- AGENTS.md working-copy version observed on 2026-04-06
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline --decorate -10`
- `test -f AGENTS.md && echo present || echo missing`
- `git --no-pager diff --stat`
- `git --no-pager diff --name-only`
- `README.md`
- `orchestrator/pipeline.py`
- `orchestrator/cli.py`
- `tests/test_cli.py`
- `docs/work-items/WI-004-run-queue-hardening.md`
- `docs/prs/PR-085/proposal.md`
- `docs/prs/PR-103/plan.md`

## scope
- Proposal-only boundary definition for future run queue hardening work in the factory core self-update lane.
- Focus only on WI-004 latest-vs-stale queue visibility and hygiene boundary.
- No implementation, no runtime semantics change, and no expansion into product-lane behavior.

## output summary
- Freeze the semantics-sensitive boundary that later implementation work must preserve.
- State what hardening directions are allowed versus forbidden.
- Define acceptance criteria for a later implementation PR without approving any runtime change here.

## problem statement grounded in actual repo/runtime state
- On 2026-04-06, `python -m factory status --root .` reported `Active PR: none`, latest run `RUN-20260327T063724Z`, approval status `pending`, queue `pending_total: 2`, `latest_run_has_pending: True`, and `stale_pending_count: 1` for `RUN-20260327T055614Z`.
- On the same baseline, `python -m factory inspect-approval-queue --root .` reported two pending items: the stale item `approval_queue/pending/APR-RUN-20260327T055614Z.yaml` linked to run `RUN-20260327T055614Z`, `matching_pr_id: PR-003`, `matching_run_state: approval_pending`; and the latest item `approval_queue/pending/APR-RUN-20260327T063724Z.yaml` linked to run `RUN-20260327T063724Z`, `matching_pr_id: PR-004`, `matching_run_state: approval_pending`.
- The repo therefore currently contains visible stale pending coexistence. That coexistence is real operator-visible state, but by itself it does not prove error, does not select a target, and does not authorize cleanup.
- Current source files reinforce that split. `orchestrator/pipeline.py` implements `get_factory_status()` as a summary view over `approval_queue` visibility and `inspect_approval_queue()` as item-level read-only inspection with `latest_relation` and matching run linkage. `orchestrator/cli.py` renders those surfaces separately. `README.md` documents both as visibility-only. `tests/test_cli.py` already locks wording that queue-hygiene visibility must not be overread as cleanup, resolve, approval, readiness/gate, selector, or Relation Summary state.

## why this is semantics-sensitive
- `latest`, `stale`, readiness context presence, queue hygiene notes, and possible next-step text all look operationally meaningful. If they drift from visibility into action or judgment, the factory stops being approval-first and starts making implied decisions.
- `factory status` is especially sensitive because it is a summary surface. If summary fields begin to act like decision signals, operators may treat a visibility snapshot as a correctness or approval surface.
- `inspect-approval-queue` is also sensitive because it presents item-level relations. If `latest_relation=stale` starts to imply cleanup, hiding, refusal, or selector priority, runtime meaning changes even if the filesystem did not.
- `trace` and `debug` are separate sensitivity points. Recent repo direction, including the trace/debug boundary in `docs/prs/PR-103/plan.md`, keeps deeper diagnostics out of inspect surfaces so operator visibility does not become low-level judgment.

## exact boundaries to preserve
- Readiness remains visibility-only. Presence or absence of readiness context must not become queue eligibility, approval readiness, or a decision input.
- `factory status` remains a summary visibility surface, not a decision surface.
- `inspect-approval-queue` remains read-only operator visibility over pending approval items.
- `latest` versus `stale` remains a reported relation only. It is not selector semantics, cleanup semantics, correctness semantics, or approval semantics.
- Stale pending coexistence is an operator-visible condition, not by itself a cleanup command or correctness signal.
- Trace/debug stays separate from inspect. No run queue hardening work should smuggle trace/debug fields into `factory status` or `inspect-approval-queue`.
- Next-step assist remains assist only, not a decision signal and not target-selection authority.
- Queue hygiene visibility, if discussed or preserved, remains exact-target audit visibility only and must stay separate from latest/stale relation semantics.
- Factory core self-update lane remains separate from product lane. This proposal concerns factory runtime/operator boundary only.

## allowed hardening directions
- Tighten docs and implementation boundaries so current visibility surfaces remain descriptive-only and cannot be mistaken for selectors or commands.
- Improve degraded-note handling, item-local inspection clarity, or evidence wording as long as the runtime meaning stays read-only and non-decision.
- Add focused validation for the current boundary in a later implementation PR, including evidence that `factory status` and `inspect-approval-queue` remain separate surfaces.
- Harden exact-target hygiene handling only where it preserves the existing rule that visibility facts do not widen apply/cleanup scope.
- Clarify operator-facing wording around stale pending coexistence so it is read as visible coexistence, not as automatic remediation.

## explicitly forbidden directions
- Do not turn readiness into gate, approval, cleanup, or queue-selection semantics.
- Do not make `factory status` a decision surface, recommendation surface, or control surface.
- Do not make `inspect-approval-queue` mutate artifacts, hide entries, resolve approvals, or rank targets.
- Do not introduce cleanup-by-visibility semantics.
- Do not introduce heuristic selectors such as `latest`, `stale`, or relation-summary-derived targeting.
- Do not reinterpret stale pending coexistence as proof of incorrectness, orphaned state, or automatic cleanup eligibility.
- Do not mix trace/debug data into inspect/status output in a way that changes operator meaning.
- Do not mix factory core self-update lane concerns with product-lane behavior, user-facing feature requirements, or product-runtime semantics.
- Do not change CLI help text, templates, tests, runtime code, or orchestration behavior in this proposal PR.

## acceptance criteria for a later implementation PR
- The implementation PR must preserve the current baseline facts when pointed at the current repo state: no active PR, latest run `RUN-20260327T063724Z`, latest pending mapped to `PR-004`, stale pending mapped to `PR-003`, and visible coexistence of both pending items.
- The implementation PR must show that `factory status` still behaves as a summary visibility surface only and does not emit decision-shaped fields or selector guidance.
- The implementation PR must show that `inspect-approval-queue` remains read-only and that `latest_relation` still means visibility-only.
- The implementation PR must show that stale pending coexistence is still described as operator-visible coexistence, not cleanup or correctness signaling.
- The implementation PR must not add selector semantics based on `latest`, `stale`, readiness, queue hygiene metadata, or next-step assist.
- The implementation PR must keep trace/debug surfaces separate from inspect/status surfaces.
- The implementation PR must stay in the factory core self-update lane and keep product-lane behavior out of scope.
- The implementation PR must include direct evidence from repo commands and tests, not only prior PR prose.

## risks
- If wording around stale coexistence is loose, later work may treat visibility as authorization.
- If status/inspect/trace boundaries are not preserved, operators may infer decisions from the wrong surface.
- If later hardening uses heuristic targeting, the change would silently alter runtime semantics instead of merely hardening them.

## next required gate
- Reviewer: confirm no part of this proposal smuggles in cleanup, selector, or decision semantics.
- Approver / PM: approve or reject the preserved boundary before any implementation PR is authorized.
- Implementer: if approved later, keep the follow-up strictly evidence-backed and proposal-compliant.
