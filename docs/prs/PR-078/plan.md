# PR-078 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- User task for PR-078 docs-only proposal PR using live repo state as source of truth
- `factory status --root .`
- `inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline -n 10`
- [docs/prs/README.md](/docs/prs/README.md)
- [docs/contracts/status-contract.md](/docs/contracts/status-contract.md)
- [docs/adr/ADR-003-file-based-approval-queue.md](/docs/adr/ADR-003-file-based-approval-queue.md)
- [docs/prs/PR-074/plan.md](/docs/prs/PR-074/plan.md)
- [docs/prs/PR-074/proposal.md](/docs/prs/PR-074/proposal.md)
- [docs/prs/PR-075/plan.md](/docs/prs/PR-075/plan.md)
- [docs/prs/PR-075/proposal.md](/docs/prs/PR-075/proposal.md)
- [docs/prs/PR-076/plan.md](/docs/prs/PR-076/plan.md)
- [docs/prs/PR-076/proposal.md](/docs/prs/PR-076/proposal.md)
- [docs/prs/PR-077/plan.md](/docs/prs/PR-077/plan.md)
- [docs/prs/PR-077/proposal.md](/docs/prs/PR-077/proposal.md)
- [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml)
- [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml)
- [approval_queue/pending/APR-RUN-20260327T055614Z.yaml](/approval_queue/pending/APR-RUN-20260327T055614Z.yaml)
- [approval_queue/pending/APR-RUN-20260327T063724Z.yaml](/approval_queue/pending/APR-RUN-20260327T063724Z.yaml)

## scope
- PR-078 is docs-only and proposal-only.
- Topic: parser and selector validation proposal for the manual approval queue hygiene command.
- No implementation.
- No runtime, code, test, or CLI behavior change.
- No parser implementation.
- No dry-run implementation.
- No apply implementation.
- No expansion of `stale` or `latest` into cleanup semantics or selector semantics.
- Explicit target, dry-run-first, and separate apply remain required.
- This PR must leave [docs/prs/PR-078/plan.md](/docs/prs/PR-078/plan.md) in place before merge.

## output summary
- Add [docs/prs/PR-078/plan.md](/docs/prs/PR-078/plan.md) as the PR-local contract and snapshot note.
- Add [docs/prs/PR-078/proposal.md](/docs/prs/PR-078/proposal.md) as the parser and selector validation proposal.
- Pin selector families, parser refusal rules, canonical identity resolution, safe-fail cases, and follow-up implementation split without approving any implementation work.

## current repo snapshot
- Current branch is `pr/078-approval-queue-parser-selector-validation`.
- Active PR: `none`.
- Latest run: `RUN-20260327T063724Z`.
- Approval queue pending total: `2`.
- `factory status --root .` reports `stale_pending_count: 1` and `stale_pending_run_ids: RUN-20260327T055614Z`.
- `inspect-approval-queue --root .` reports relation counts latest `1`, stale `1`, no-latest-run `0`, unparseable `0`.
- Pending item `APR-RUN-20260327T055614Z.yaml` maps to [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml), which records `pr_id: PR-003` and `state: approval_pending`.
- Pending item `APR-RUN-20260327T063724Z.yaml` maps to [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml), which records `pr_id: PR-004` and `state: approval_pending`.
- The repo therefore currently shows two visible pending approval artifacts across different run and PR histories, so selector parsing must refuse heuristic or multi-target interpretation.

## contract to pin in this PR
- Selector families remain limited to exact identifiers, not visibility labels.
- The proposal should allow both `--run-id` and `--approval-id` as selector families, but each invocation must satisfy an exactly-one-selector rule.
- Parser validation must refuse neither-selector, both-selectors, malformed selector values, and heuristic words such as `latest`, `stale`, `current`, `previous`, or `all-stale`.
- Any accepted selector must resolve to exactly one canonical queue artifact identity.
- Safe-fail behavior must cover missing, ambiguous, invalid selector combination, heuristic selector attempt, and identity mismatch precursor cases.
- This PR fixes proposal wording only. It does not approve parser behavior in code, dry-run output in code, or apply behavior in code.

## follow-up boundary
- PR-078 does not approve parser implementation.
- PR-078 does not approve dry-run implementation.
- PR-078 does not approve apply implementation.
- PR-078 does not approve docs/help/test updates beyond this PR-local proposal note.
- Any later implementation must be split into parser implementation, dry-run implementation, apply implementation, and docs/help/tests.

## ADR and docs sync assessment
- ADR required: no.
- Reason: this PR narrows parser and selector validation proposal wording only and does not approve an architecture change.
- Docs sync required: yes.
- Reason: this PR adds the required PR-local plan and proposal docs for PR-078 and does not broaden runtime contract docs in this slice.

## risks
- If selector families are left vague, later implementation may smuggle `latest` or `stale` into selector semantics.
- If canonical identity resolution is not fixed at proposal time, different selector forms may drift into conflicting target interpretations.
- If malformed and heuristic inputs are not explicitly refused, operators may treat visibility output as executable selector syntax.

## next required gate
- Reviewer: confirm the PR stays docs-only and proposal-only, with no implied parser or mutation implementation approval.
- Approver / PM: decide whether the parser and selector validation proposal is strict enough to authorize a later implementation split.
- Docs Sync / Release: confirm docs sync is satisfied by the PR-local plan and proposal docs only.
