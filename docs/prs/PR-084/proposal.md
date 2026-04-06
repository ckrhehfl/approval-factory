# PR-084 Proposal

## input refs
- AGENTS.md working-copy version observed on 2026-04-05
- `git status -sb`
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- [README.md](/README.md)
- [docs/prs/PR-080/plan.md](/docs/prs/PR-080/plan.md)
- [docs/prs/PR-081/plan.md](/docs/prs/PR-081/plan.md)
- [docs/prs/PR-082/plan.md](/docs/prs/PR-082/plan.md)
- [docs/prs/PR-083/plan.md](/docs/prs/PR-083/plan.md)
- [orchestrator/cli.py](/orchestrator/cli.py)
- [orchestrator/pipeline.py](/orchestrator/pipeline.py)
- [tests/test_cli.py](/tests/test_cli.py)

## scope
- Proposal-only note that freezes the current semantics of `queue_hygiene` metadata.
- No implementation.
- No runtime, CLI, test, queue artifact, or approval lifecycle change.
- No change to stale/latest visibility, Relation Summary, queue eligibility, or resolve semantics.

## output summary
- Fix the current meaning of `queue_hygiene` as a narrow operator-audit marker on one exact queue artifact.
- Fix the non-meaning boundary so it cannot be read as cleanup, resolve, gate, decision, or selector state.
- Fix the operator interpretation boundary for `factory status`, `inspect-approval-queue`, Relation Summary, and stale/latest visibility.
- Split any later visibility or semantic expansion into separate follow-up PRs.

## observed repo facts
- `factory hygiene-approval-queue --apply` currently writes `queue_hygiene` only on the single resolved target queue artifact.
- The written fields are `status`, `applied_at`, `selector_family`, `requested_run_id`, and `requested_approval_id`.
- Current CLI apply summary says the mutation is `queue_hygiene metadata updated on the exact target queue artifact only`.
- Current CLI dry-run/apply summaries also say cleanup is not implemented, auto-resolve is not implemented, selector scope is exact target only, and stale/latest plus Relation Summary remain read-only operator visibility.
- `factory status --root .` and `inspect-approval-queue --root .` currently report queue visibility from pending artifacts and latest-run relation only; they do not read `queue_hygiene` as approval state or selector state.
- Current tests lock exact-target-only metadata write behavior and also lock that non-target queue artifacts stay untouched.

## 0) 바꾸려는 의미
- `queue_hygiene`의 현재 의미는 exact target queue artifact 하나에 남는 operator-audit marker다.
- 이 metadata는 "운영자가 어떤 exact selector로 어떤 pending approval artifact에 hygiene apply를 수행했다"는 사실만 기록한다.
- 현재 의미는 queue artifact 내부의 부가적 audit trace에 한정된다.
- 질문 1에 대한 답: 예. 현재는 one exact queue artifact에 남는 operator-audit marker로만 봐야 한다.

## 1) 왜 필요한지
- PR-080부터 PR-083까지 parser, dry-run, apply, docs/help/tests는 구현되었지만 `queue_hygiene`의 해석 범위 자체는 별도 제안으로 고정되지 않았다.
- 이름만 보면 cleanup 완료, resolve 신호, gate 상태, selector 상태로 과대해석될 위험이 있다.
- 현재 repo 상태는 stale/latest visibility와 real pending artifacts를 동시에 보여주므로 visibility와 mutation audit를 분리해서 읽어야 한다.
- 이 PR은 추가 구현 전에 의미 drift를 막기 위한 semantics freeze가 필요하다.

## 2) 최소 계약
- `queue_hygiene`는 approval queue eligibility에 영향을 주지 않는다.
- `queue_hygiene`는 `resolve-approval` 동작에 영향을 주지 않는다.
- `queue_hygiene`는 approval decision semantics를 나타내지 않는다.
- `queue_hygiene`는 readiness or gate semantics를 나타내지 않는다.
- `queue_hygiene`는 selector semantics를 나타내지 않는다. 나중 invocation을 위한 stored selector state가 아니다.
- `queue_hygiene`는 stale/latest relation semantics를 바꾸지 않는다.
- `queue_hygiene`는 Relation Summary count나 `factory status`의 `pending_total`, `stale_pending_count`, `latest_run_has_pending` 해석을 바꾸지 않는다.
- `queue_hygiene`는 현재 cleanup semantics가 아니다. pending artifact 제거, 숨김, 이동, lifecycle transition을 뜻하지 않는다.
- `queue_hygiene`는 현재 auto-resolve semantics가 아니다. approval request를 approved/rejected/exceptions로 종결시키지 않는다.
- 질문 2에 대한 답: 아니오. approval queue eligibility에 영향이 없다.
- 질문 3에 대한 답: 아니오. `resolve-approval` behavior에 영향이 없다.
- 질문 4에 대한 답: 아니오. stale/latest relation semantics에 영향이 없다.
- 질문 5에 대한 답: 나중에 `status`나 `inspect`에 보이게 할 수는 있지만, 별도 PR로 read-only visibility only 범위에서만 다뤄야 한다.

## 3) 금지 범위
- `queue_hygiene`를 cleanup completed, safe to delete, safe to hide, safe to move로 해석하지 않는다.
- `queue_hygiene`를 resolved, approved, rejected, exceptioned, request-changed signal로 해석하지 않는다.
- `queue_hygiene`를 merge gate, readiness gate, approval gate, execution gate 신호로 해석하지 않는다.
- `queue_hygiene`를 stale/latest selector, Relation Summary selector, implicit follow-up selector로 해석하지 않는다.
- `queue_hygiene`를 exact target 외의 queue artifact들에 대한 broad queue state로 일반화하지 않는다.
- 이 PR에서 runtime, CLI, tests, queue artifacts, approval artifacts, status/inspect output을 변경하지 않는다.

## 4) 검증 기준
- Proposal validation:
- `orchestrator/` 아래 runtime code path 변경이 없어야 한다.
- proposal text 안에 `not cleanup`, `not auto-resolve`, `not approval decision semantics`, `not readiness/gate semantics`, `not selector semantics` 경계가 명시돼야 한다.
- proposal text 안에 `factory status`, `inspect-approval-queue`, Relation Summary, stale/latest visibility와의 관계가 명시돼야 한다.
- closeout validation:
- `git status --short`, `git --no-pager diff --stat`, `git --no-pager diff --name-only`로 docs-only change 여부를 확인한다.
- docs-only면 docs-only라고 명시한다.

## 5) 후속 구현 분할안
- Follow-up A: read-only visibility proposal
- `queue_hygiene`를 `inspect-approval-queue` 또는 `factory status`에 보여줄지 검토하되, 출력은 read-only visibility only로 제한한다.
- Follow-up B: read-only visibility implementation
- 별도 승인 후 status/inspect 출력에 audit marker를 노출하더라도 pending counts, relation semantics, selector semantics는 유지한다.
- Follow-up C: semantics expansion proposal, only if ever needed
- cleanup, resolve interaction, queue lifecycle, selector memory, gate interaction 같은 의미 확장은 현재 PR 범위 밖이며 각각 별도 제안 PR로 분리한다.
- 질문 6에 대한 답: 있다면 follow-up은 read-only visibility와 any semantic expansion을 분리해야 하고, semantic expansion은 cleanup/resolve/gate/selector별로 다시 분할해야 한다.

## risks
- 문서가 약하면 운영자가 `queue_hygiene`를 cleanup 또는 resolve shorthand로 읽을 수 있다.
- visibility surface에 노출되더라도 read-only boundary가 약하면 selector/gate 의미가 새어 들어갈 수 있다.
- exact target-local audit라는 현재 의미를 고정하지 않으면 후속 PR이 broad queue semantics를 암묵적으로 추가할 수 있다.

## next required gate
- Reviewer: confirm this PR freezes meaning only and does not approve any new behavior.
- Approver / PM: decide whether a later read-only visibility proposal should proceed.
- QA: if later visibility work is approved, require evidence that output remains descriptive only and does not affect queue or approval behavior.
