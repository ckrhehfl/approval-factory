# PR-075 Proposal

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- `factory status --root .`
- `inspect-approval-queue --root .`
- [README.md](/README.md)
- [docs/contracts/status-contract.md](/docs/contracts/status-contract.md)
- [docs/ops/runbook.md](/docs/ops/runbook.md)
- [docs/prs/PR-070/proposal.md](/docs/prs/PR-070/proposal.md)
- [docs/prs/PR-074/proposal.md](/docs/prs/PR-074/proposal.md)
- [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml)
- [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml)
- [approval_queue/pending/APR-RUN-20260327T055614Z.yaml](/approval_queue/pending/APR-RUN-20260327T055614Z.yaml)
- [approval_queue/pending/APR-RUN-20260327T063724Z.yaml](/approval_queue/pending/APR-RUN-20260327T063724Z.yaml)

## scope
- Proposal-only command-shape note for a manual approval queue hygiene command.
- No implementation.
- No runtime, code, test, or CLI behavior change.
- No mutation semantic approval.
- No expansion of `stale` or `latest` into cleanup shorthand or selector semantics.

## output summary
- Propose a provisional command surface for explicit manual queue hygiene.
- Fix the target contract so mutation can never be derived from `latest`, `stale`, or summary visibility alone.
- Fix dry-run-first and separate-apply rules before any implementation is considered.

## observed repo facts
- `factory status --root .` reports latest run `RUN-20260327T063724Z`, pending total `2`, and one stale pending item.
- `inspect-approval-queue --root .` reports relation counts latest `1`, stale `1`, no-latest-run `0`, and unparseable `0`.
- Pending item `APR-RUN-20260327T055614Z.yaml` maps to [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml), which records `pr_id: PR-003` and `state: approval_pending`.
- Pending item `APR-RUN-20260327T063724Z.yaml` maps to [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml), which records `pr_id: PR-004` and `state: approval_pending`.
- The repo therefore currently contains two visible queue candidates that look valid enough to require an operator-specified target.
- Existing repo contracts already say that status and inspection output are visibility only and do not define selector semantics.

## proposed command surface
- Provisional command name: `factory hygiene-approval-queue`.
- The command remains manual and operator-invoked only.
- The command must require exactly one explicit target selector family:
  - `--run-id <RUN-...>`
  - `--approval-id <APR-RUN-...>`
- The command must reject calls that provide both `--run-id` and `--approval-id`.
- The command must reject calls that provide neither.
- If `--run-id` is used, the command resolves only the canonical pending approval artifact path for that exact run id.
- If `--approval-id` is used, the command resolves only that exact approval queue artifact id.
- If both target families are ever kept in implementation, both must resolve to exactly one queue item and the command must surface which canonical approval artifact it matched.
- The command may optionally support a read-only preview form such as:

```bash
factory hygiene-approval-queue --root . --run-id RUN-20260327T055614Z
factory hygiene-approval-queue --root . --approval-id APR-RUN-20260327T055614Z
factory hygiene-approval-queue --root . --run-id RUN-20260327T055614Z --apply
```

## required explicit target
- `latest`, `stale`, relation summary counts, status output, and inspection output must never be accepted as shorthand selectors.
- Requests such as "clean the stale one", "apply to latest", or "pick the non-latest approval" must be refused until the operator provides an exact `run-id` or exact `approval-id`.
- The command must not infer targets from `latest_relation`, `pending_total`, matching PR id, matching run state, or path summaries.
- The command must not introduce `--latest`, `--stale`, `--all-stale`, `--current`, `--previous`, or similar convenience selectors in this proposal.

## dry-run and apply separation
- Default behavior must be dry-run.
- Dry-run must not mutate queue artifacts, run artifacts, or approval decision artifacts.
- Dry-run output should be limited to the resolved target, the proposed mutation category, and the exact reason the command would proceed or refuse.
- Mutation must require a separate explicit apply action such as `--apply`.
- `--apply` must reuse the same explicit target rules and must not enable broader selection behavior.
- Dry-run and apply must stay within one resolved target only. No bulk apply is accepted by this proposal.

## refusal and safe-fail cases
- `target missing`
  - If the exact `run-id` or `approval-id` cannot be resolved to a queue artifact, the command must fail without mutation.
- `ambiguous target`
  - If resolution yields multiple possible artifacts or a mismatch between requested selector family and canonical artifact identity, the command must fail without mutation.
- `already terminal`
  - If the target artifact is already approved, rejected, exceptioned, archived, or otherwise outside the intended pending mutation surface, the command must fail without mutation.
- `latest-only heuristic request`
  - If the operator attempts to rely on latest/stale wording instead of an exact target id, the command must fail and require an explicit target.
- `relation-summary-derived request`
  - If the only basis is inspection or status output, the command must fail and require an explicit target.
- `invalid selector combination`
  - If the operator provides both `--run-id` and `--approval-id`, or combines target flags with any future shorthand selector, the command must fail without mutation.

## non-goals
- This PR is not implementation approval.
- This PR does not approve mutation semantics such as delete, move, resolve, or archive behavior.
- This PR does not approve a final command name.
- This PR does not approve selector expansion for `latest` or `stale`.
- This PR does not change `factory status`, `inspect-approval-queue`, approval lifecycle, or queue contracts.

## rationale
- The live repo state shows two visible pending approvals across different run histories, so implicit target selection is not safe.
- `stale` remains a visibility label only because the stale item still maps to a real run in `approval_pending`.
- A hygiene command is potentially destructive, so dry-run first and separate apply must be fixed at the command shape level.
- Accepting exact `run-id` and exact `approval-id` together is reasonable only if the exclusivity and single-resolution rule are explicit.

## follow-up implementation split
- `command parser`
  - Add and validate `--run-id` versus `--approval-id`, enforce exactly-one-target, and reject shorthand selectors.
- `dry-run behavior`
  - Implement read-only resolution, preview output, and refusal messaging for missing, ambiguous, heuristic, and terminal cases.
- `apply behavior`
  - Implement the approved mutation only after dry-run behavior is separately accepted, preserving the same target resolution contract.
- `docs/help/tests`
  - Document examples, refusal wording, and regression tests so `latest`/`stale` never become shorthand selectors by drift.

## risks
- Readers may overread this proposal as approval for a specific mutation even though the proposal only fixes command shape.
- Supporting both `run-id` and `approval-id` could drift into inconsistent resolution unless the single-target rule is preserved.
- If refusal cases are weakened later, operators may treat status or inspection output as actionable selectors.

## next required gate
- Reviewer: accept or reject the command-shape proposal as docs-only guardrails.
- Approver / PM: decide whether a later implementation design may proceed under this explicit-target and dry-run-first contract.
- QA: if implementation is ever approved later, require evidence that heuristic selectors are refused and dry-run/apply remain separate.
