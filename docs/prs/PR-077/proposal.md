# PR-077 Proposal

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- `factory status --root .`
- `inspect-approval-queue --root .`
- [docs/contracts/status-contract.md](/docs/contracts/status-contract.md)
- [docs/ops/runbook.md](/docs/ops/runbook.md)
- [docs/prs/PR-074/proposal.md](/docs/prs/PR-074/proposal.md)
- [docs/prs/PR-075/proposal.md](/docs/prs/PR-075/proposal.md)
- [docs/prs/PR-076/proposal.md](/docs/prs/PR-076/proposal.md)
- [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml)
- [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml)
- [approval_queue/pending/APR-RUN-20260327T055614Z.yaml](/approval_queue/pending/APR-RUN-20260327T055614Z.yaml)
- [approval_queue/pending/APR-RUN-20260327T063724Z.yaml](/approval_queue/pending/APR-RUN-20260327T063724Z.yaml)

## scope
- Proposal-only apply behavior note for the manual approval queue hygiene command.
- No implementation.
- No runtime, code, test, parser, dry-run-path, apply-path, or CLI behavior change.
- No mutation semantic approval beyond boundary-setting for a future exact-target apply step.
- No expansion of `stale` or `latest` into cleanup shorthand or selector semantics.

## output summary
- Define apply as a separate explicit mutation attempt for exactly one exact target only.
- Fix apply preconditions, target-identity reuse expectation, mutation boundary, refusal behavior, and minimum audit expectations.
- Preserve the earlier contracts that dry-run stays first, `stale`/`latest` stay visibility-only, and apply implementation remains separately unapproved.

## observed repo facts
- `factory status --root .` reports latest run `RUN-20260327T063724Z`, pending total `2`, and one stale pending item.
- `inspect-approval-queue --root .` reports relation counts latest `1`, stale `1`, no-latest-run `0`, and unparseable `0`.
- Pending item `APR-RUN-20260327T055614Z.yaml` maps to [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml), which records `pr_id: PR-003` and `state: approval_pending`.
- Pending item `APR-RUN-20260327T063724Z.yaml` maps to [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml), which records `pr_id: PR-004` and `state: approval_pending`.
- The repo therefore currently contains two visible pending approval artifacts that remain real enough to require exact-target-only mutation boundaries and safe-fail refusal for any heuristic apply attempt.

## apply purpose
- Apply exists only to attempt mutation for one exact target after a separate explicit apply decision.
- Apply is not target discovery, not queue cleanup shorthand, not a selector convenience, and not a replacement for dry-run.
- Apply must remain a second step after dry-run-first operator review, even if the final mutation kind is not yet approved.
- Apply may attempt mutation only for the canonical queue artifact that corresponds to the one explicit target the operator named.

## apply preconditions
- Exact target is required.
- Heuristic selectors are forbidden.
- Dry-run-first remains the governing principle.
- When a prior dry-run resolved the target identity, apply should reuse that same target identity rather than reinterpreting latest queue state through broader matching.
- If implementation cannot prove it is acting on the same target identity that dry-run confirmed, apply must refuse rather than widen or guess.

## mutation boundary apply may touch
- The only candidate mutation surface is the resolved target's queue artifact within the manual approval queue.
- This proposal does not approve the final mutation kind, but it does constrain scope to target-local queue artifact handling such as state transition, relocation, archival, or equivalent target-local queue mutation if later approved.
- Apply must not mutate non-target queue artifacts.
- Apply must not mutate unrelated run artifacts, including non-target `runs/latest/<run-id>/` content.
- Apply must not rewrite approval decision semantics, approval policy semantics, readiness semantics, or status/inspection semantics.

## apply must never change
- Unrelated queue artifacts.
- Unrelated runs.
- Approval decision semantics in general.
- The meaning of `latest`, `stale`, relation summary, status output, or inspect output.
- The explicit-target, dry-run-first, and separate-apply principles already established in the proposal chain.

## refusal and safe-fail cases
- `target missing`
  - If the exact target cannot be resolved to one canonical queue artifact at apply time, apply must refuse without mutation.
- `ambiguous target`
  - If resolution yields more than one possible artifact or cannot prove one canonical identity, apply must refuse without mutation.
- `already terminal`
  - If the resolved target is already approved, rejected, exceptioned, archived, or otherwise outside the pending mutation surface, apply must refuse without mutation.
- `heuristic apply without dry-run`
  - If the operator tries to jump directly to apply using `latest`, `stale`, relation summary, or similar heuristic wording without an exact target and dry-run-first review, apply must refuse.
- `mismatched target identity`
  - If apply cannot prove that the target it is about to mutate is the same identity that dry-run confirmed, apply must refuse without mutation.

## audit and evidence minimums
- Before apply, the operator should confirm the exact target id, canonical queue artifact identity, related run or PR context if present, and the refusal-free dry-run result for that same target.
- Before apply, the operator should confirm that the request is not derived only from `latest`, `stale`, pending counts, relation summary, or other visibility labels.
- If a future apply path is approved, it should leave at least enough evidence to show requested target identity, resolved canonical artifact identity, attempted mutation category, and success or refusal outcome.
- This PR does not approve a final evidence schema or storage location; it only fixes the minimum evidence shape that later implementation must preserve.

## non-goals
- This PR is not implementation approval.
- This PR does not approve parser implementation.
- This PR does not approve dry-run implementation.
- This PR does not approve apply implementation.
- This PR does not approve a final mutation type.
- This PR does not approve cleanup semantics for `stale` or selector semantics for `latest`.
- This PR does not change `factory status`, `inspect-approval-queue`, approval lifecycle behavior, or queue contracts.

## rationale
- The live repo state still shows two visible pending approvals across different run histories, so apply cannot safely infer targets from queue visibility.
- The earlier proposal chain already fixed explicit target and dry-run-first as safeguards; apply remains safe only if it preserves those safeguards instead of bypassing them.
- Even without approving a final mutation type yet, the repo needs a narrow statement of what apply may touch and what it must never touch.

## follow-up implementation split
- `parser`
  - Define and validate the exact target form and reject heuristic selectors.
- `dry-run implementation`
  - Implement read-only target resolution, identity reporting, and refusal messaging that apply can later depend on.
- `apply implementation`
  - Implement the separately approved mutation path only for the same exact target identity and within the approved queue-artifact mutation surface.
- `docs/help/tests`
  - Document examples, refusal wording, and regressions so explicit target, dry-run-first, separate apply, and non-target protection do not drift.

## risks
- If apply is framed as cleanup rather than exact-target mutation, later work may smuggle in broad stale/latest semantics that current contracts reject.
- If same-target identity reuse is not explicit, apply may be implemented as a fresh heuristic search and mutate the wrong artifact after dry-run.
- If audit minimums stay vague, operators may treat apply as an untraceable direct action rather than an evidence-backed second step.

## next required gate
- Reviewer: accept or reject the apply contract as docs-only guardrails.
- Approver / PM: decide whether a later implementation split may proceed under this exact-target, dry-run-first, same-identity-reuse boundary.
- QA: if implementation is ever approved later, require evidence that apply mutates only the target-local queue artifact surface and safe-fails on identity mismatch or heuristic requests.
