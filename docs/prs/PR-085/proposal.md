# PR-085 Proposal

## input refs
- AGENTS.md working-copy version observed on 2026-04-05
- `git status -sb`
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- [docs/prs/PR-084/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-084/plan.md)
- [docs/prs/PR-084/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-084/proposal.md)
- [orchestrator/cli.py](/mnt/c/dev/approval-factory/orchestrator/cli.py)
- [orchestrator/pipeline.py](/mnt/c/dev/approval-factory/orchestrator/pipeline.py)
- [tests/test_cli.py](/mnt/c/dev/approval-factory/tests/test_cli.py)

## scope
- Proposal-only decision for `queue_hygiene` read-only visibility.
- No implementation.
- No runtime, CLI output, test, queue artifact, or approval lifecycle change.
- No semantics expansion beyond the PR-084 exact-target operator-audit marker contract.

## output summary
- Recommend surfacing `queue_hygiene` in `inspect-approval-queue` only, not in `factory status` for now.
- Recommend item-local visibility only and reject summary/count visibility.
- Fix the wording so operators read `queue_hygiene` as exact-target operator-audit metadata only.
- Keep stale/latest relation and Relation Summary explicitly separate from any `queue_hygiene` display.
- Split later implementation from this proposal and keep any broader surface expansion out of scope.

## observed repo facts
- `factory status --root .` is a queue-summary surface today and does not show per-item artifact metadata.
- `python -m factory inspect-approval-queue --root .` is already the per-item inspection surface for pending approval artifacts.
- `queue_hygiene` is written only when `factory hygiene-approval-queue --apply` updates one exact target queue artifact.
- The stored `queue_hygiene` fields are `status`, `applied_at`, `selector_family`, `requested_run_id`, and `requested_approval_id`.
- Current CLI wording already says cleanup is not implemented, auto-resolve is not implemented, selector scope is exact target only, and stale/latest plus Relation Summary remain read-only operator visibility.

## 0) 바꾸려는 의미
- 이번 PR이 바꾸려는 것은 `queue_hygiene`의 runtime 의미가 아니라 read-only visibility placement proposal이다.
- 질문 1에 대한 답: `queue_hygiene`는 `factory status`에 surfacing하지 않는다. `factory status`는 queue-level summary surface로 유지한다.
- 질문 2에 대한 답: `queue_hygiene`는 `inspect-approval-queue`에 surfacing하는 것이 맞다.
- 질문 3에 대한 답: surfacing한다면 per-item only다. summary only도 아니고 both도 아니다.
- `queue_hygiene`는 exact target queue artifact 하나에 붙는 operator-audit marker이므로, item-local inspection surface에서만 읽히는 것이 현재 의미와 맞다.

## 1) 왜 필요한지
- PR-084는 `queue_hygiene`를 exact-target operator-audit marker로 고정했고, read-only visibility 여부는 follow-up A로 분리했다.
- 현재 repo에는 `factory status`라는 summary surface와 `inspect-approval-queue`라는 item-local inspection surface가 이미 분리돼 있다.
- `queue_hygiene`를 summary surface에 올리면 queue-level meaning처럼 읽힐 위험이 크다.
- 반대로 `inspect-approval-queue`의 item-local 위치는 "이 pending artifact에 audit metadata가 붙어 있다"는 사실을 가장 좁고 정확하게 보여준다.
- 운영자에게는 exact-target apply 흔적을 볼 수 있는 read-only visibility가 유용하지만, 그 visibility는 decision signal이나 cleanup shorthand로 오해되면 안 된다.

## 2) 최소 계약
- `queue_hygiene` visibility는 read-only operator visibility only다.
- `queue_hygiene` visibility는 cleanup semantics가 아니다. `already cleaned up`, `safe to delete`, `safe to hide`, `safe to move`를 뜻하지 않는다.
- `queue_hygiene` visibility는 auto-resolve semantics가 아니다. `safe to resolve`, `already resolved`, `decision already applied`를 뜻하지 않는다.
- `queue_hygiene` visibility는 approval decision semantics가 아니다. approve/reject/request_changes/exception 상태를 뜻하지 않는다.
- `queue_hygiene` visibility는 readiness/gate semantics가 아니다. `approval-ready`, `gate satisfied`, `merge-ready`를 뜻하지 않는다.
- `queue_hygiene` visibility는 selector semantics가 아니다. `latest/stale selector`, `stored selector`, `follow-up selector`를 뜻하지 않는다.
- `queue_hygiene` visibility는 stale/latest relation semantics가 아니다. `latest_relation`을 보정하거나 대체하지 않는다.
- `queue_hygiene` visibility는 Relation Summary semantics가 아니다. count를 만들거나 Relation Summary에 포함되지 않는다.
- 질문 4에 대한 답: 보여줄 필드는 item-local `queue_hygiene_audit` block 아래의 `status`, `applied_at`, `selector_family`, `requested_run_id`, `requested_approval_id`다.
- 권장 display shape는 pending item 안의 별도 block 하나뿐이다. 예시는 `queue_hygiene_audit: present` 다음에 위 다섯 필드를 나열하는 형태가 적합하다.
- 권장 wording은 block label과 note 모두 audit 중심이어야 한다. 예: `queue_hygiene_audit`와 `operator_note: exact-target operator-audit marker only; not cleanup, resolve, approval decision, readiness/gate, selector, latest/stale relation, or Relation Summary state`.
- `factory status`에는 어떤 `queue_hygiene` summary, count, latest marker, stale marker, or boolean도 추가하지 않는다.

## 3) 금지 범위
- 질문 5에 대한 답: wording은 `cleanup`, `resolve`, `ready`, `gate`, `selector`, `latest`, `stale`, `summary`처럼 행동 유도를 암시하는 단독 라벨을 쓰지 않는다.
- `queue_hygiene`를 `queue_hygiene_status` 하나만 노출해서 queue state처럼 읽히게 하지 않는다.
- `factory status`에 `queue_hygiene` 관련 count, summary, boolean, latest-only indicator를 추가하지 않는다.
- `inspect-approval-queue`의 Relation Summary section에 `queue_hygiene` 집계를 추가하지 않는다.
- `latest_relation`과 `queue_hygiene`를 결합한 composite wording을 만들지 않는다.
- `queue_hygiene`를 cleanup completion, auto-resolve candidate, stale cleanup candidate, or selector memory로 해석하지 않는다.
- 이 PR에서 runtime behavior, CLI output, tests, queue artifacts, approval artifacts는 바꾸지 않는다.

## 4) 검증 기준
- Proposal validation:
- runtime code path 변경이 없어야 한다.
- proposal text가 `queue_hygiene` visibility is read-only only를 명시해야 한다.
- proposal text가 `queue_hygiene`는 cleanup/resolve/gate/selector state가 아니라고 명시해야 한다.
- proposal text가 stale/latest relation 및 Relation Summary와의 관계를 명시해야 한다.
- proposal text가 `factory status` 비노출, `inspect-approval-queue` item-local only, no summary counts 결정을 명시해야 한다.
- proposal text가 별도 implementation follow-up을 명시해야 한다.
- closeout validation:
- `git status --short`, `git --no-pager diff --stat`, `git --no-pager diff --name-only`를 기록한다.
- docs-only change면 docs-only라고 명시한다.

## 5) 후속 구현 분할안
- Follow-up B1: `inspect-approval-queue` item-local read-only visibility implementation
- pending item에만 `queue_hygiene_audit` block을 추가하고, metadata가 있을 때만 exact stored fields를 보여준다.
- Follow-up B1은 output wiring, docs/help alignment, focused tests만 포함한다. queue mutation semantics나 summary semantics는 포함하지 않는다.
- Follow-up B2: post-implementation wording verification
- `queue_hygiene` wording이 `already cleaned up`, `safe to resolve`, `approval-ready`, `latest/stale selector`로 읽히지 않는지 QA evidence를 분리한다.
- Follow-up C: any `factory status` exposure or any summary/count exposure proposal, only if ever needed
- status surface 추가는 이번 결정에 포함되지 않는다. 필요하면 별도 proposal PR에서 justification부터 다시 다룬다.
- Follow-up D: semantics expansion proposal only if ever needed
- cleanup, auto-resolve, approval decision, gate interaction, selector memory, stale/latest interaction 확장은 현재 범위 밖이다.

## risks
- item-local note가 빠지면 운영자가 stored metadata를 queue state로 오해할 수 있다.
- `factory status`에 같은 정보를 섞으면 relation summary나 stale count와 결합해서 decision signal처럼 읽힐 수 있다.
- implementation follow-up에서 필드 이름을 줄이거나 재해석하면 PR-084 semantics freeze를 훼손할 수 있다.

## next required gate
- Reviewer: confirm the proposal stays narrow and does not smuggle in status summary semantics.
- Approver / PM: decide whether the later `inspect-approval-queue` item-local read-only implementation should proceed.
- QA: when implementation follow-up exists, require evidence that display remains descriptive only and relation counts remain unchanged.
