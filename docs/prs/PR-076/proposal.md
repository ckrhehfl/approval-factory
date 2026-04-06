# PR-076 Proposal

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- `factory status --root .`
- `inspect-approval-queue --root .`
- [docs/contracts/status-contract.md](/docs/contracts/status-contract.md)
- [docs/ops/runbook.md](/docs/ops/runbook.md)
- [docs/prs/PR-074/proposal.md](/docs/prs/PR-074/proposal.md)
- [docs/prs/PR-075/proposal.md](/docs/prs/PR-075/proposal.md)
- [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml)
- [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml)
- [approval_queue/pending/APR-RUN-20260327T055614Z.yaml](/approval_queue/pending/APR-RUN-20260327T055614Z.yaml)
- [approval_queue/pending/APR-RUN-20260327T063724Z.yaml](/approval_queue/pending/APR-RUN-20260327T063724Z.yaml)

## scope
- Proposal-only dry-run behavior note for the manual approval queue hygiene command.
- No implementation.
- No runtime, code, test, parser, apply-path, or CLI behavior change.
- No mutation semantic approval.
- No expansion of `stale` or `latest` into cleanup shorthand or selector semantics.

## output summary
- Define the purpose of dry-run as preview and guardrail for one exact target before any mutation.
- Fix the minimum dry-run output contract and refusal behavior.
- Preserve the boundary that apply remains separate and explicitly approved per invocation.

## observed repo facts
- `factory status --root .` reports latest run `RUN-20260327T063724Z`, pending total `2`, and one stale pending item.
- `inspect-approval-queue --root .` reports relation counts latest `1`, stale `1`, no-latest-run `0`, and unparseable `0`.
- Pending item `APR-RUN-20260327T055614Z.yaml` maps to [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml), which records `pr_id: PR-003` and `state: approval_pending`.
- Pending item `APR-RUN-20260327T063724Z.yaml` maps to [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml), which records `pr_id: PR-004` and `state: approval_pending`.
- The repo therefore currently contains two visible pending approval artifacts that remain real enough to require an exact target and a non-mutating preview step.

## dry-run purpose
- Dry-run exists to preview exactly one explicitly requested target before any mutation is even considered.
- Dry-run is a guardrail, not an approval, not an apply shortcut, and not a selector convenience.
- When the operator supplies an exact target, dry-run may resolve identity and explain what category of mutation would be considered later, but it must stop before changing artifacts.

## minimum dry-run output contract
- Dry-run must report the resolved target identity.
- Dry-run must report the canonical queue artifact path.
- Dry-run must report related run context and PR context if present.
- Dry-run may report the proposed mutation category.
- Dry-run must not perform the mutation.
- Dry-run must report an explicit proceed reason or explicit refuse reason.

## artifacts dry-run must never change
- Queue artifacts.
- Run artifacts.
- Approval decision artifacts.

## refusal and safe-fail cases
- `target missing`
  - If the exact target cannot be resolved to the canonical queue artifact, dry-run must refuse without mutation.
- `ambiguous target`
  - If resolution yields more than one possible artifact or cannot prove one canonical identity, dry-run must refuse without mutation.
- `already terminal`
  - If the resolved target is already terminal or otherwise outside the pending mutation surface, dry-run must refuse without mutation.
- `heuristic selector attempt`
  - If the request tries to use `latest`, `stale`, relation summary, or similar heuristic wording instead of an exact target, dry-run must refuse.
- `invalid selector combination`
  - If the request combines incompatible selector forms, dry-run must refuse without mutation.

## boundary with apply
- Dry-run success does not mean apply is approved.
- Apply must remain a separate explicit step.
- Apply must reuse the same exact target identity that dry-run resolved, rather than widening selection at mutation time.
- This proposal does not approve apply semantics, parser semantics, or mutation details.

## non-goals
- This PR is not implementation approval.
- This PR does not approve parser implementation.
- This PR does not approve dry-run implementation.
- This PR does not approve apply implementation.
- This PR does not approve cleanup semantics for `stale` or selector semantics for `latest`.
- This PR does not change `factory status`, `inspect-approval-queue`, or approval lifecycle behavior.

## rationale
- The live repo state still shows two visible pending approvals across different run histories, so preview must stay exact-target and non-mutating.
- Dry-run is useful only if it helps the operator inspect the real target identity before mutation; it becomes unsafe if it starts inferring selectors or mutating side artifacts.
- Separating dry-run from apply preserves the existing explicit-target and dry-run-first principles already established in the proposal chain.

## follow-up implementation split
- `parser`
  - Define and validate the exact target forms without introducing heuristic selectors.
- `dry-run implementation`
  - Implement target resolution, preview output, and refusal messaging with zero artifact mutation.
- `apply implementation`
  - Implement the separately approved mutation path while preserving the same exact target contract.
- `docs/help/tests`
  - Document examples, refusal wording, and regressions so preview-only dry-run and separate apply do not drift.

## risks
- If dry-run output grows beyond preview and refusal information, later work may accidentally normalize side effects in a supposedly safe mode.
- If operators read dry-run success as permission to mutate, apply could become a hidden second step without explicit approval.
- If heuristic selector refusal is weakened, stale/latest visibility could drift into unsupported target semantics.

## next required gate
- Reviewer: accept or reject the dry-run contract as docs-only guardrails.
- Approver / PM: decide whether a later implementation split may proceed under this preview-only and separate-apply boundary.
- QA: if implementation is ever approved later, require evidence that dry-run changes no artifacts and that refusal cases remain explicit.
