# Proposal: PR Loop Merge Authority / Dry-Run Apply Contract

## input refs
- User task for PR-122 proposal-only merge authority boundary / dry-run-apply contract.
- `git status -sb`
- `git diff --check`
- `git --no-pager diff --stat`
- `git --no-pager diff -- docs/proposals/README.md docs/proposals/pr-loop-merge-authority-dry-run-apply-contract.md docs/prs/PR-122/plan.md`
- `python -m pytest tests/test_pr_loop_*.py`
- `python -m pytest -q`

## scope
- Proposal-only PR-122 contract for PR Loop merge authority and dry-run/apply separation.
- Documents the intended boundary that approved merge authority should remain `none` until a separate approved contract selects one, and keeps `merge --dry-run` on the non-apply side of that boundary.
- Defines candidate merge authority models, rejected authority surfaces, required evidence, stale invalidation, override boundary, and prerequisite gates before any future implementation is approved.
- Treats repo code, tests, git history, and runtime artifacts as source of truth. Official runtime artifacts and official repo docs may support review, but `docs/prs` and continuity handoff material remain reference only.
- Does not implement runtime code, CLI behavior, merge apply, request-merge, gate-authoritative command behavior, state core, policy loader, phase machine, live artifacts, queue/status/readiness semantics, fixture promotion, or official pack updates.

## current landed facts
- Current working tree shows exactly three changed docs paths on this branch: `docs/proposals/README.md`, `docs/proposals/pr-loop-merge-authority-dry-run-apply-contract.md`, and `docs/prs/PR-122/plan.md`.
- Current diff stat shows a one-line README addition plus one proposal document addition and one PR plan document addition.
- `git diff --check` passes for the current working tree.
- `python -m pytest tests/test_pr_loop_*.py` passes.
- `python -m pytest -q` passes.

## non-goals and rejected options
- Do not treat the fixture lane as merge authority. In this proposal, fixture files, fixture manifest fields, fixture state, fixture policy snapshots, fixture gate summaries, fixture rendered text, and fixture dry-run summaries are treated as non-authoritative local test data.
- Do not treat `runs/latest`, `approval_queue`, or `docs/prs` as merge decision authority.
- Do not treat inspect, readiness, status, trace, debug, rendered review text, review packet drafts, gate-check output, or dry-run summaries as merge decision input.
- Do not infer merge approval from latest run, latest queue item, stale queue item, current branch, current PR docs, continuity notes, generated summaries, LLM-written review text, or the absence of failed dry-run preconditions.
- Do not implement merge apply, request-merge, gate-authoritative command behavior, merge queue mutation, git branch mutation, PR mutation, approval queue mutation, runtime artifact mutation, or official pack mutation in this PR.
- Do not decide state authority, policy authority, phase-machine behavior, live `artifacts/pr_loop` creation, policy source selection, or state transition semantics in this PR. Those remain outside PR-122 scope.
- Do not create an apply mode behind the existing `merge --dry-run` surface.
- Do not let a dry-run summary share the same authority surface as a future apply command.
- Do not allow future runtime code to merge, request merge, or mark a gate authoritative until a separate approved contract defines the authority owner, command name, evidence schema, stale invalidation, override boundary, mutation behavior, and failure handling.

## proposed merge authority candidates
- Candidate A: human-approved merge evidence bundle under a future approved live PR Loop runtime namespace. This could preserve exact merge inputs and stale invalidation refs, but it depends on separately approved state authority, policy authority, and live artifact creation.
- Candidate B: external platform authority, such as an approved GitHub merge queue or protected-branch status, referenced by immutable observation ids. This could avoid repo-local merge mutation, but it still needs a contract for how observations are collected, invalidated, and mapped to a canonical PR id.
- Candidate C: manual Approver / PM merge approval recorded in an approved policy or decision artifact, paired with deterministic check/review/docs-sync evidence. This fits approval-first workflow, but it requires a strict schema so prose or stale queue entries cannot become implicit authority.
- Candidate D: a future gate-authoritative command that produces machine-readable merge evidence only after state and policy authority exist. The proposal rejects fixture-backed `gate-check` and `merge --dry-run` outputs as authority surfaces for that command.
- Rejected as candidates for merge decision authority: `runs/latest`, `approval_queue`, `docs/prs`, `tests/fixtures/pr_loop`, continuity packs, inspect/readiness/status/trace/debug command text, rendered review packets, `gate-check` output, and `merge --dry-run` summaries.
- PR-122 does not choose among the viable candidates. It records that approved merge authority should remain `none` until a later approved contract selects one, and that implementation requirements belong to that later contract.

## dry-run summary vs apply authority separation
- This proposal documents the intended boundary that approved merge authority should remain `none` until a separate approved contract selects one.
- This proposal keeps `merge --dry-run` on the non-apply side of the boundary. It is read-only summary only, not runtime state, gate evidence, approval authority, merge authority, or apply permission.
- A dry-run command may report candidate blockers, missing evidence, and hypothetical precondition status. It must not create live artifacts, mutate git, update PR metadata, update approval queues, update run state, write policy snapshots, write merge evidence, or enqueue merge work.
- A dry-run pass, if future inputs ever allow one, must still not imply apply permission. Apply authority requires a separate approved contract and a separate explicit command or mode with its own evidence bundle.
- A future merge apply or request-merge command must not reuse transient dry-run text as decision input. It must read approved evidence artifacts or approved external observations through a deterministic contract.
- A future apply surface must fail closed when evidence is missing, stale, ambiguous, generated from fixtures, generated from read-only visibility output, or scoped to a different PR id, head commit, policy version, or gate run.
- A future apply surface must record what it intended to mutate, what it actually mutated, source refs, failure state, and rollback or recovery guidance before it may be considered for implementation.

## required evidence, stale invalidation, and override boundary
- Future merge authority must require explicit human approval evidence, required review evidence, required check evidence, docs sync evidence where applicable, deterministic gate evidence, approved policy refs, target PR id, target head commit, base branch, merge base or equivalent platform ref, and command/source identity.
- Evidence must be derived from approved source-of-truth surfaces or approved external observations, not from fixtures, queue visibility, status/readiness text, trace/debug text, rendered review prose, gate-check text, dry-run summary text, or `docs/prs` audit plans.
- Future merge evidence must record schema version, source path or observation id, source commit or content digest where available, collection time, approving role or approval reference, target PR id, target head, and policy snapshot or policy version if policy authority later exists.
- Future merge authority must fail closed if the target head changes, merge base changes, required review/check status changes, docs sync evidence changes, policy source or snapshot changes, exception records change, state phase changes, or any required evidence lacks approved source refs.
- Future merge authority must reject stale approvals, stale queue items, stale rendered reviews, stale dry-run summaries, stale gate summaries, and any evidence collected for a different PR id, branch, base, head, policy version, or gate run.
- Overrides must be explicit human approval evidence with approving role, allowed override type, exact rule or evidence requirement being overridden, justification, expiration or scope, target PR id, target head, and stale invalidation behavior.
- Overrides must not be inferred from pending queue items, stale queue items, status/readiness output, fixture fields, rendered review packets, dry-run summaries, gate-check output, trace/debug output, or LLM text.
- Overrides must not bypass missing human approval evidence, missing required check evidence, docs sync requirements, security/cost/performance constraints, failed tests, or architecture exceptions unless a later approved policy explicitly allows that override type and records the approving authority.
- Override approval does not imply merge apply authority. Merge apply still requires the separate approved merge authority contract and current non-stale evidence bundle.

## prerequisite gates before any future implementation is approved
- Architect gate: decide whether merge authority, dry-run/apply separation, request-merge behavior, gate-authoritative command behavior, stale invalidation, and override semantics require a formal ADR before implementation.
- Approver / PM gate: approve which merge authority candidate is authoritative, who may approve merge evidence, which overrides are allowed, and what human approval evidence is sufficient.
- Policy gate: separately approve policy source-of-truth, policy versioning, exception policy, and policy snapshot semantics before merge authority depends on policy facts. PR-122 does not choose policy authority.
- State gate: separately approve live PR Loop state authority, phase-machine behavior, state schema, and state invalidation before merge authority depends on state facts. PR-122 does not choose state authority or phase-machine behavior.
- Evidence contract gate: approve merge evidence schema, required source refs, stale invalidation rules, external observation rules, and docs sync evidence requirements before any command can produce authoritative merge evidence.
- Boundary gate: prove the design does not treat `runs/latest`, `approval_queue`, `docs/prs`, fixtures, inspect/readiness/status/trace/debug output, rendered review text, gate-check output, or dry-run summaries as merge decision authority.
- Apply contract gate: approve future merge apply or request-merge command name, mutation scope, idempotency behavior, failure handling, audit artifact, rollback/recovery guidance, and tests before implementation.
- QA gate: provide tests for no fixture promotion, no read-only command mutation, no transient command text as merge input, no implicit selector fallback, no stale evidence acceptance, override refusal without approved evidence, and apply refusal without an approved merge authority bundle.
- Docs sync gate: update proposal docs, policy docs, ADR if required, PR docs, operator docs, and CLI help docs together whenever implementation changes a merge authority boundary.

## output summary
- PR-122 documents a proposal-only merge authority and dry-run/apply separation contract before any future PR Loop merge apply or request-merge implementation is approved.
- The proposal documents the boundary that approved merge authority should remain `none` until a separate approved contract selects one.
- The proposal keeps `merge --dry-run` on the non-apply side of the boundary and treats it as read-only summary only, not apply permission.
- The proposal keeps current landed facts limited to what the attached review outputs directly show.
- The proposal rejects the fixture lane, `runs/latest`, `approval_queue`, `docs/prs`, inspect/readiness/status/trace/debug output, rendered review text, gate-check output, and dry-run summaries as merge decision authority.
- The proposal leaves state authority, policy authority, phase-machine behavior, live artifacts, and apply implementation out of scope.
- The proposal requires separate approval for merge authority selection, evidence schema, stale invalidation, override semantics, and apply mutation behavior before runtime code may implement merge apply, request-merge, or gate-authoritative command behavior.

## risks
- If dry-run output is treated as apply permission, a read-only summary could become an unapproved mutation path.
- If visibility surfaces become merge decision inputs, PR Loop could bypass approval-first boundaries and act on stale or auxiliary evidence.
- If fixture-backed summaries are promoted, local test data could be mistaken for live merge evidence.
- If override semantics are implicit, exceptions could bypass required approval, check, docs sync, security, cost, performance, or architecture gates.
- If state authority, policy authority, phase-machine behavior, and merge authority are implemented together, scope could expand from proposal-only boundaries into unreviewed runtime behavior.

## next required gate
- Reviewer: confirm this PR is proposal-only and does not alter runtime code, fixtures, CLI semantics, queue/status/readiness behavior, live artifacts, official packs, policy loader behavior, state authority, phase-machine behavior, merge authority, request-merge behavior, gate-authoritative command behavior, or apply semantics.
- Architect: decide ADR need before merge authority, dry-run/apply separation, request-merge behavior, gate-authoritative command behavior, stale invalidation, override semantics, or merge apply implementation.
- Approver / PM: approve or reject the merge authority candidate, evidence contract, stale invalidation, and override boundary before implementation begins.
