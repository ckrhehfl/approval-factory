# PR-078 Proposal

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- `factory status --root .`
- `inspect-approval-queue --root .`
- [docs/contracts/status-contract.md](/mnt/c/dev/approval-factory/docs/contracts/status-contract.md)
- [docs/adr/ADR-003-file-based-approval-queue.md](/mnt/c/dev/approval-factory/docs/adr/ADR-003-file-based-approval-queue.md)
- [docs/prs/PR-074/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-074/proposal.md)
- [docs/prs/PR-075/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-075/proposal.md)
- [docs/prs/PR-076/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-076/proposal.md)
- [docs/prs/PR-077/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-077/proposal.md)
- [runs/latest/RUN-20260327T055614Z/run.yaml](/mnt/c/dev/approval-factory/runs/latest/RUN-20260327T055614Z/run.yaml)
- [runs/latest/RUN-20260327T063724Z/run.yaml](/mnt/c/dev/approval-factory/runs/latest/RUN-20260327T063724Z/run.yaml)
- [approval_queue/pending/APR-RUN-20260327T055614Z.yaml](/mnt/c/dev/approval-factory/approval_queue/pending/APR-RUN-20260327T055614Z.yaml)
- [approval_queue/pending/APR-RUN-20260327T063724Z.yaml](/mnt/c/dev/approval-factory/approval_queue/pending/APR-RUN-20260327T063724Z.yaml)

## scope
- Proposal-only parser and selector validation note for the manual approval queue hygiene command.
- No implementation.
- No runtime, code, test, or CLI behavior change.
- No parser implementation.
- No dry-run implementation.
- No apply implementation.
- No expansion of `stale` or `latest` into cleanup shorthand or selector semantics.

## output summary
- Fix the allowed selector families and their exclusivity rule.
- Fix parser refusal rules for missing, conflicting, malformed, and heuristic selector inputs.
- Fix the canonical identity resolution rule and the safe-fail cases any later implementation must preserve.

## observed repo facts
- `factory status --root .` reports latest run `RUN-20260327T063724Z`, pending total `2`, and one stale pending item.
- `inspect-approval-queue --root .` reports relation counts latest `1`, stale `1`, no-latest-run `0`, and unparseable `0`.
- Pending item `APR-RUN-20260327T055614Z.yaml` maps to [runs/latest/RUN-20260327T055614Z/run.yaml](/mnt/c/dev/approval-factory/runs/latest/RUN-20260327T055614Z/run.yaml), which records `pr_id: PR-003` and `state: approval_pending`.
- Pending item `APR-RUN-20260327T063724Z.yaml` maps to [runs/latest/RUN-20260327T063724Z/run.yaml](/mnt/c/dev/approval-factory/runs/latest/RUN-20260327T063724Z/run.yaml), which records `pr_id: PR-004` and `state: approval_pending`.
- The repo therefore currently contains two visible queue artifacts that both look real enough to require exact selector parsing and one-canonical-artifact resolution.
- Existing repo contracts already say that status paths, relation labels, and inspection summaries are visibility only and not selector semantics.

## selector families
- Allowed selector family 1: `--run-id <RUN-...>`.
- Allowed selector family 2: `--approval-id <APR-RUN-...>`.
- This proposal keeps both selector families because both identities already exist as real repo-local artifacts and each can name the same pending queue artifact from a different entry point.
- This proposal does not allow free-form positional selectors or heuristic selector aliases.
- The governing rule is exactly one selector family per invocation:
  - `--run-id` only is allowed.
  - `--approval-id` only is allowed.
  - both together are refused.
  - neither is refused.

## parser validation rules
- `neither provided`
  - Refuse when neither `--run-id` nor `--approval-id` is provided.
- `both provided`
  - Refuse when both `--run-id` and `--approval-id` are provided, even if they appear consistent.
- `malformed run-id`
  - Refuse when `--run-id` does not match the exact `RUN-...` identity shape expected by repo artifacts.
- `malformed approval-id`
  - Refuse when `--approval-id` does not match the exact `APR-RUN-...` identity shape expected by repo artifacts.
- `heuristic words`
  - Refuse inputs that attempt selector meaning through words such as `latest`, `stale`, `current`, `previous`, `all-stale`, or similar heuristic phrases.
- `no selector expansion`
  - Refuse any attempt to reinterpret `stale` or `latest` as cleanup scope, selector shorthand, or relation-derived convenience syntax.

## canonical identity resolution rule
- An accepted selector must resolve to exactly one canonical queue artifact.
- Canonical queue artifact means one repo-local approval queue artifact identity, not a relation label, summary line, or inferred class of items.
- `--run-id` resolution must map that exact run id to at most one canonical pending approval artifact for that run.
- `--approval-id` resolution must map that exact approval id to that exact canonical queue artifact.
- If resolution cannot prove one canonical queue artifact identity, the command must refuse rather than guess.
- If later dry-run or apply surfaces additional context such as run path or PR id, that context remains supporting evidence only and must not replace canonical queue artifact identity.

## safe-fail cases
- `missing`
  - Refuse when the exact selector does not resolve to any canonical queue artifact.
- `ambiguous`
  - Refuse when resolution yields more than one possible queue artifact or cannot prove a single canonical identity.
- `invalid selector combination`
  - Refuse when selector families are combined in one invocation or mixed with any future shorthand selector surface.
- `heuristic selector attempt`
  - Refuse when the operator tries to select through `latest`, `stale`, `current`, `previous`, `all-stale`, relation summary, status output, or inspect output.
- `identity mismatch precursor`
  - Refuse when the supplied selector parses syntactically but evidence around the resolved artifact suggests the command cannot safely prove one canonical target identity for later dry-run or apply reuse.

## non-goals
- This PR is not implementation approval.
- This PR does not approve parser implementation.
- This PR does not approve mutation approval.
- This PR does not approve dry-run or apply behavior changes.
- This PR does not approve cleanup semantics for `stale` or selector semantics for `latest`.
- This PR does not change `factory status`, `inspect-approval-queue`, runtime behavior, or approval lifecycle semantics.

## rationale
- The live repo state shows two visible pending approvals across different run histories, so selector parsing must reject anything short of one exact id family.
- Allowing both selector families is reasonable because `run-id` and `approval-id` are both first-class repo identities, but allowing both in one invocation would weaken operator intent and parser clarity.
- Malformed and heuristic input refusal must be part of the proposal contract because parser ambiguity would otherwise leak into dry-run or apply behavior later.
- Canonical identity resolution must be fixed now so later implementation cannot drift from exact selector parsing into relation-derived selection.

## follow-up implementation split
- `parser implementation`
  - Implement `--run-id` and `--approval-id` parsing, enforce the exactly-one-selector rule, validate identity shapes, and refuse heuristic words.
- `dry-run implementation`
  - Implement read-only canonical identity resolution preview and refusal messaging while preserving the same parser contract.
- `apply implementation`
  - Implement a separately approved exact-target mutation path that reuses the same canonical identity contract.
- `docs/help/tests`
  - Document selector examples, refusal wording, and regressions so shorthand selector drift does not reappear.

## risks
- Readers may overread this proposal as approval for parser code, but this PR only fixes validation rules and boundaries in docs.
- If exact identity shapes are not implemented consistently later, `run-id` and `approval-id` paths could diverge and point at different interpretations of the same queue state.
- If heuristic words are tolerated later even as warnings, operators may still treat visibility output as executable selector syntax.

## next required gate
- Reviewer: accept or reject the parser and selector validation contract as docs-only guardrails.
- Approver / PM: decide whether a later parser implementation PR may proceed under the exactly-one-selector and one-canonical-artifact rule.
- QA: if implementation is ever approved later, require evidence that malformed, conflicting, missing, ambiguous, and heuristic selectors all safe-fail without mutation.
