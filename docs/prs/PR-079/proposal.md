# PR-079 Proposal

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- `factory status --root .`
- `inspect-approval-queue --root .`
- [docs/contracts/status-contract.md](/docs/contracts/status-contract.md)
- [docs/adr/ADR-003-file-based-approval-queue.md](/docs/adr/ADR-003-file-based-approval-queue.md)
- [docs/prs/PR-074/proposal.md](/docs/prs/PR-074/proposal.md)
- [docs/prs/PR-075/proposal.md](/docs/prs/PR-075/proposal.md)
- [docs/prs/PR-076/proposal.md](/docs/prs/PR-076/proposal.md)
- [docs/prs/PR-077/proposal.md](/docs/prs/PR-077/proposal.md)
- [docs/prs/PR-078/proposal.md](/docs/prs/PR-078/proposal.md)
- [docs/prs/PR-073/delta.md](/docs/prs/PR-073/delta.md)
- [docs/prs/PR-073/start-prompt.md](/docs/prs/PR-073/start-prompt.md)
- [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml)
- [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml)
- [approval_queue/pending/APR-RUN-20260327T055614Z.yaml](/approval_queue/pending/APR-RUN-20260327T055614Z.yaml)
- [approval_queue/pending/APR-RUN-20260327T063724Z.yaml](/approval_queue/pending/APR-RUN-20260327T063724Z.yaml)

## scope
- Proposal-only note for approval queue hygiene implementation split and rollout boundary.
- No implementation.
- No runtime, code, test, parser, dry-run, apply-path, or CLI behavior change.
- No expansion of `stale` or `latest` into cleanup shorthand or selector semantics.
- No approval of mutation semantics.

## output summary
- Summarize the confirmed proposal chain from PR-074 through PR-078.
- Fix the implementation split order the repo must follow if implementation is later approved.
- Fix rollout boundaries so parser, dry-run, and apply cannot be overread or merged together.
- Reconfirm the forbidden scope and record the follow-up boundary for the external downloadable 3-pack refresh after PR-079.

## observed repo facts
- `factory status --root .` reports latest run `RUN-20260327T063724Z`, pending total `2`, and one stale pending item.
- `inspect-approval-queue --root .` reports relation counts latest `1`, stale `1`, no-latest-run `0`, and unparseable `0`.
- Pending item `APR-RUN-20260327T055614Z.yaml` maps to [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml), which records `pr_id: PR-003` and `state: approval_pending`.
- Pending item `APR-RUN-20260327T063724Z.yaml` maps to [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml), which records `pr_id: PR-004` and `state: approval_pending`.
- The repo therefore still shows two visible pending approval artifacts across different run histories, so any future implementation must preserve exact-target-only handling and must not infer mutation from visibility labels.

## proposal chain summary
- PR-074 fixed the manual-first and explicit-target boundary.
  - Queue hygiene starts as a manual operator action only.
  - `stale` remains visibility-only and is not cleanup or deletion safety.
- PR-075 fixed the command-shape boundary.
  - Exact selector families stay limited to `--run-id` and `--approval-id`.
  - Dry-run-first and separate apply are command-shape requirements, not optional UX refinements.
- PR-076 fixed the dry-run boundary.
  - Dry-run previews one exact target only.
  - Dry-run stays non-mutating and must safe-fail on heuristic or ambiguous targeting.
- PR-077 fixed the apply boundary.
  - Apply is a separate explicit mutation attempt for one exact target only.
  - Apply must not widen from dry-run-confirmed identity into heuristic search.
- PR-078 fixed parser and selector validation.
  - Exactly one selector family is allowed per invocation.
  - Missing, conflicting, malformed, ambiguous, and heuristic selectors must all safe-fail.

## implementation split order
- Stage 1: parser implementation
  - Implement `--run-id` and `--approval-id` parsing only.
  - Enforce exactly-one-selector, identity-shape validation, and heuristic selector refusal.
  - Do not implement dry-run output semantics beyond what is needed to prove parser refusal or acceptance shape.
  - Do not implement mutation.
- Stage 2: dry-run implementation
  - Implement read-only canonical target resolution and preview output for one exact target.
  - Preserve zero mutation across queue artifacts, run artifacts, and approval decision artifacts.
  - Reuse the parser contract from Stage 1 without widening selector semantics.
- Stage 3: apply implementation
  - Implement the separately approved exact-target mutation path only after parser and dry-run behavior are already fixed and accepted.
  - Reuse the same canonical target identity that prior stages established.
  - Keep the mutation surface target-local and queue-artifact-local only.
- Stage 4: docs/help/tests
  - Update operator docs, help text, refusal wording, and regression tests only after implementation behavior exists to document and verify.
  - Keep docs/help/tests aligned with explicit target, dry-run-first, separate apply, and heuristic-refusal rules.

## rollout boundary
- Parser implementation must be accepted before dry-run implementation begins.
- Dry-run implementation must be accepted before apply implementation begins.
- Apply implementation must be accepted before docs/help/tests finalize user-facing examples and regression guarantees.
- Parser-only rollout does not permit mutation.
  - Even if parser accepts exact ids and rejects heuristic selectors, queue mutation remains forbidden until dry-run and apply stages are separately approved and implemented.
- Dry-run rollout does not permit apply.
  - Even if dry-run resolves one canonical target and previews a refusal-free path, apply remains a separate explicit approval and separate implementation stage.
- No later stage may weaken an earlier stage's guardrails.
  - Exact target remains mandatory.
  - Dry-run-first remains mandatory.
  - Separate apply remains mandatory.
  - Visibility labels remain non-executable.

## forbidden scope reconfirmed
- No auto cleanup.
- No auto resolve.
- No `stale` shorthand selector.
- No `latest` shorthand selector.
- No `all-stale`, `current`, `previous`, or similar selector aliases.
- No Relation Summary-triggered action.
- No Relation Summary-derived selector semantics.
- No parser, dry-run, or apply behavior in this PR.

## follow-up after PR-079
- External downloadable 3-pack refresh proceeds only after PR-079 is complete.
- That external pack should include:
  - master changed/unchanged re-evaluation
  - refreshed delta
  - refreshed start prompt
- PR-079 does not create or refresh the external pack itself.
- If the external pack is refreshed later, distribution packaging may change, but repo-internal behavior contracts must stay aligned with the PR-074 through PR-079 proposal chain.

## non-goals
- This PR is not implementation approval.
- This PR does not approve parser implementation.
- This PR does not approve dry-run implementation.
- This PR does not approve apply implementation.
- This PR does not approve docs/help/tests implementation.
- This PR does not change `factory status`, `inspect-approval-queue`, approval lifecycle behavior, or queue contracts.

## rationale
- The proposal chain already fixed the core guardrails. What remained open was sequencing and gate discipline between those guardrails and any later implementation work.
- The live repo state still shows multiple visible pending approvals, so parser, dry-run, and apply cannot safely be collapsed into one implementation step without weakening exact-target guarantees.
- Keeping docs/help/tests last prevents user-facing examples or regression claims from outrunning the actual approved implementation boundary.

## risks
- If implementation starts with dry-run or apply before parser validation is fixed in code, target identity rules may drift between stages.
- If parser rollout is mistaken for implementation approval in general, mutation could be introduced before dry-run-first and separate-apply boundaries are operational.
- If the forbidden scope is not repeated here, later work may reintroduce stale/latest shorthand or Relation Summary-triggered cleanup through convenience arguments.

## next required gate
- Reviewer: accept or reject the implementation split and rollout boundary as docs-only guardrails.
- Approver / PM: decide whether later implementation PRs must follow the Stage 1 through Stage 4 sequence without skipping gates.
- QA: if implementation is ever approved later, require evidence per stage that mutation stays forbidden until the apply stage and that heuristic selectors remain refused throughout.
