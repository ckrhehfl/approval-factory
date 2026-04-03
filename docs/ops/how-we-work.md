# How We Work (Repo-local MVP)

## 목적

이 문서는 approval-factory를 현재 구현 범위 안에서 어떻게 운영하는지 설명한다. 현재 시스템은 완전 자동화가 아니라 승인자 중심의 반자동 MVP다.

## 범위 선언

포함:
- repo-local
- file-based
- approval-first
- one-PR-at-a-time
- Goal intake minimum
- clarification draft minimum
- clarification queue minimum
- work item draft minimum
- PR plan draft minimum
- Work Item artifact minimum
- active PR plan minimum

비포함:
- Goal intake 질문 자동화
- clarification 질문 자동화
- clarification 해결 자동화
- Goal 해결 자동화
- Goal to Work Item 자동 분해
- LLM 연동
- UI
- central control plane
- multi-project orchestration

## 운영 흐름 (Goal -> clarification -> WI draft -> WI -> active PR -> run -> approval)

1. Goal intake
- `factory create-goal`로 `goals/<goal-id>.md`를 생성한다.
- Goal은 사람이 읽고 수정 가능한 Markdown artifact다.
- 현재 단계는 intake 저장 계약만 제공하며, planner/resolver는 다음 PR 범위다.

2. Clarification draft
- `factory draft-clarifications`로 `clarification_drafts/<goal-id>.md`를 생성한다.
- draft는 `goals/<goal-id>.md`에서 deterministic rule-based prompt만 뽑아내는 operator-facing artifact다.
- draft는 official clarification queue artifact를 만들지 않고, readiness/gate/approval/queue/selector/lifecycle semantics도 바꾸지 않는다.
- draft에서 official clarification으로의 승격은 자동이 아니라 operator가 `factory promote-clarification-draft` 또는 `factory create-clarification`를 별도로 실행할 때만 일어난다.

3. Clarification queue
- `factory create-clarification`로 `clarifications/<goal-id>/<clarification-id>.md`를 생성한다.
- draft 항목을 그대로 official clarification으로 승격할 때는 `factory promote-clarification-draft --root <repo> --goal-id <goal-id> --draft-index <n> --clarification-id <id>`를 사용한다.
- clarification은 Goal intake 다음 단계의 최소 질문 관리 계층이다.
- promotion 명령은 draft file을 건드리지 않고 official artifact 하나만 만들며, draft의 question/category/rationale과 draft path/index provenance를 함께 남긴다.
- clarification queue는 생성만 가능하면 운영이 막히므로 `factory resolve-clarification`로 사람이 `resolved|deferred|escalated`를 명시적으로 기록할 수 있어야 한다.
- 이 명령은 기존 Markdown 형식을 유지한 채 `Status`, `Resolution Notes`, `Next Action`, `Escalation Required`를 갱신한다.
- `Status=open`인 artifact만 종결할 수 있고, 종결된 clarification은 `factory status`의 open clarification 목록에서 빠진다.
- 현재 단계는 draft artifact 생성, 질문 artifact 수동 생성/수동 승격, 최소 수동 종결까지만 제공하며, auto-promotion/auto-resolution은 다음 구조 확장 범위다.

4. Work Item draft
- `factory draft-work-items`로 `work_item_drafts/<goal-id>.md`를 생성한다.
- draft는 `goals/<goal-id>.md`와 official clarification artifacts `clarifications/<goal-id>/*.md`만 읽는 deterministic rule-based artifact다.
- source of truth는 official clarification artifacts이며 `clarification_drafts/`는 입력으로 읽지 않는다.
- official clarification이 없어도 zero-candidate draft artifact는 남긴다.
- draft는 `docs/work-items/` official artifact를 만들지 않고, readiness/gate/approval/queue/selector/active PR/lifecycle semantics도 바꾸지 않는다.
- draft에서 official work item으로의 승격은 자동이 아니라 operator가 `factory promote-work-item-draft` 또는 `factory create-work-item`를 별도로 실행할 때만 일어난다.

5. Work Item 정의
- `factory create-work-item`로 `docs/work-items/<work-item-id>.md`를 생성한다.
- draft 후보를 그대로 official work item으로 올릴 때는 `factory promote-work-item-draft --root <repo> --goal-id <goal-id> --draft-index <n> --work-item-id <id>`를 사용한다.
- Work Item은 Goal/clarification을 PR 실행 단위로 연결하는 수동 Markdown artifact다.
- promotion 명령은 draft file을 건드리지 않고 official artifact 하나만 만들며, draft candidate의 title/summary와 source clarification linkage를 그대로 넘긴다.
- promotion 명령은 새 artifact shape를 만들지 않고 기존 `create-work-item` 경로를 재사용한다.
- 필요하면 반복 가능한 `--clarification-id`로 같은 goal 아래 clarification linkage를 함께 기록할 수 있다.
- 기본 섹션은 Work Item ID, Goal ID, Title, Status, Description, Related Clarifications, Scope, Out of Scope, Acceptance Criteria, Dependencies, Risks, Notes다.
- `Related Clarifications`는 `clarification_id (status)`를 보여주며, 없으면 `- none`으로 남긴다.
- `factory work-item-readiness --root <repo> --work-item-id <id>`는 linked clarification의 현재 상태를 다시 읽어 `no-linked-clarifications|ready|attention-needed` 중 하나로 짧게 요약한다.
- clarification status는 가시성 목적이며 생성 허용 여부를 자동 판정하지 않는다.
- readiness summary도 visibility only이며 create-pr-plan, start-execution, gate, approval semantics를 바꾸지 않는다.
- 현재 단계는 artifact 생성과 수동 관리까지만 제공하며 auto decomposition, work item draft auto-promotion, bulk promotion, clarification auto-link recommendation, 강제 gating은 다음 PR 범위다.

6. PR plan draft
- `factory draft-pr-plan`으로 `pr_plan_drafts/<work-item-id>.md`를 생성한다.
- draft는 official work item artifact `docs/work-items/<work-item-id>.md`만 읽는 deterministic rule-based artifact다.
- source of truth는 official work item artifact이며 `work_item_drafts/`는 입력으로 읽지 않는다.
- draft는 `prs/active/`, `prs/archive/` official artifact를 만들지 않고, readiness/gate/approval/queue/selector/active PR/lifecycle semantics도 바꾸지 않는다.
- draft에서 official PR plan으로의 승격도 자동이 아니라 operator가 `factory promote-pr-plan-draft` 또는 `factory create-pr-plan`을 별도로 실행할 때만 일어난다.

7. Active PR 계획
- `factory create-pr-plan`로 PR plan 후보를 생성한다.
- draft seed를 최대한 재사용해 official PR plan 하나를 만들 때는 `factory promote-pr-plan-draft --root <repo> --work-item-id <id>`를 사용한다.
- active PR plan은 Work Item을 현재 실행 중인 단 하나의 PR로 연결하는 수동 Markdown artifact다.
- operator는 merge 전 해당 PR에 대한 최소 history note로 `docs/prs/PR-###/plan.md`를 남긴다. 이 문서는 history/audit trail surface이며 runtime source of truth는 아니다.
- 기본 섹션은 PR ID, Work Item ID, Title, Status, Summary, Work Item Readiness, Linked Clarifications, Scope, Out of Scope, Implementation Notes, Risks, Open Questions다.
- `prs/active/`는 항상 0 또는 1개의 PR만 가져야 한다.
- active PR가 없으면 `create-pr-plan`은 `prs/active/<pr-id>.md`를 만든다.
- active PR가 이미 있으면 `create-pr-plan`은 `prs/archive/<pr-id>.md`에 후보를 만든다.
- promotion 명령도 기존 `create-pr-plan` 경로를 재사용하므로 같은 active/archive 배치 규칙과 conflict checks를 그대로 따른다.
- promotion 명령의 target PR id는 work item id에서 deterministic 하게 파생되며 `WI-039 -> PR-039` 같은 대응을 사용한다.
- promotion 명령은 draft file을 건드리지 않고 linked work item id와 draft summary/scope/validation intent를 가능한 범위에서 official plan에 보존한다.
- `create-pr-plan`은 source work item readiness를 read-only로 다시 계산해 plan 문서에 함께 남긴다.
- readiness summary 규칙은 `work-item-readiness`와 동일하며 `no-linked-clarifications|ready|attention-needed` 중 하나다.
- 이 정보는 operator auditability를 위한 visibility layer이며 `attention-needed`여도 생성 자체를 자동 차단하지 않는다.
- CLI는 plan이 active에 생겼는지 archive에 생겼는지와 readiness summary, linked clarification count, 다음 action을 함께 보여주므로, archive 생성은 guardrail이지 버그가 아니다.
- active PR를 명시적으로 바꿔야 할 때는 `factory activate-pr`로 기존 active를 `prs/archive/`로 옮기고 대상 PR을 active로 전환한다.
- 이번 범위는 PR-011 execution flow 보강용 최소 전환만 포함하며, lifecycle 전체나 multi-PR orchestration은 포함하지 않는다.
- `factory status`는 active PR가 있을 때 source work item readiness summary를 같은 규칙으로 read-only 노출할 수 있다.
- 이 status readiness는 visibility only이며 start-execution, gate, approval semantics를 바꾸지 않는다.
- `docs/prs`의 7-file shape는 권장 history-doc shape일 뿐이며, forward minimum requirement는 `plan.md` 1개다.

8. Run 부트스트랩
- `factory start-execution`으로 `prs/active/`의 단일 active PR plan을 읽어 `runs/latest/<run-id>/` 및 기본 artifact를 만든다.
- active PR가 사용자의 의도와 다르면 먼저 `activate-pr`로 전환한 뒤 실행한다.
- active PR plan의 `Work Item ID`가 실제 `docs/work-items/` artifact와 연결되지 않으면 시작하지 않는다.
- guardrail 실패 시 CLI는 현재 repo 상태에서 먼저 해야 할 조치와 예시 명령을 짧게 보여준다.
- 이 명령은 내부적으로 기존 `bootstrap-run` 흐름을 재사용한다.
- 생성된 run에는 최소 `run_id`, `pr_id`, `work_item_id`, `pr_plan_path`, `work_item_path`가 남아 active PR plan과 연결된다.
- run state는 `in_progress`로 갱신된다.
- active PR plan이 없거나 여러 개이거나, work item 연결이 안 되면 안전하게 실패한다.

운영 baseline 정리:
- 기능 확장 전에 repo-local baseline normalization이 필요하면 `factory cleanup-rehearsal`를 먼저 사용한다.
- 기본값은 dry-run이며 공식 rehearsal prefix `RH` artifact만 보여준다.
- legacy scratch artifact까지 정리해야 할 때만 `--include-demo`를 사용한다.
- demo cleanup에는 `RUN-DEMO-*`뿐 아니라 `RUN-*-DEMO*`, `APR-RUN-*-DEMO*` 같은 naming variant도 포함된다.
- 이 명령은 전체 reset이 아니라 partial cleanup만 허용하며, `docs/prs/` 이력 문서는 유지한다.
- 실제 운영 이력과 non-rehearsal artifact는 기본적으로 보존한다.

9. 역할별 결과 기록
- Implementer/Reviewer/QA/Docs Sync/Verification 결과를 해당 record 명령으로 artifact에 반영한다.
- 같은 세션에서 방금 시작한 run에 계속 기록할 때는 `--run-id <id>` 대신 `--latest`를 사용할 수 있다.
- `--latest`는 `factory status`와 같은 latest-run 규칙을 사용하므로 operator가 상태 화면에서 본 latest run과 같은 대상을 고른다.
- 과거 run 재작업이나 명시성이 필요한 상황에서는 기존 `--run-id <id>`를 유지한다.

10. 게이트 판정
- `factory gate-check`로 `gate-status.yaml`을 갱신한다.
 - 이 단계는 gate 판정 확인용이며, 최종 승인 요청 산출물 최신화 단계는 아니다.

11. 승인 패키지 생성
- `factory build-approval`로 `evidence-bundle.yaml`, `approval-request.yaml`를 최신 상태로 만든다.
- 이 단계는 가능하면 source work item readiness context를 approval artifact에 함께 남겨 approver가 evidence와 readiness 맥락을 같이 볼 수 있게 한다.
- 이 단계는 `record-review`, `record-qa`, `record-docs-sync`, `record-verification`이 모두 실제로 기록된 뒤에만 허용된다.
- 조건이 맞으면 `approval_queue/pending/`에 approval 요청 파일이 적재된다.
- approval package가 생성되면 run state는 `approval_pending`이 된다.
- latest run에는 placeholder artifact가 남아 있어도 prerequisite를 충족한 것이 아니므로, 에러가 나면 안내된 `record-*` 명령을 먼저 수행한다.
- readiness는 informational only이며 queue 적재, gate 계산, resolve-approval semantics를 바꾸지 않는다.

12. 승인자 결정
- 승인자는 queue 파일과 evidence를 보고 `approve/reject/exception`을 결정한다.
- `factory resolve-approval`로 승인 결정을 `approval-decision.yaml`에 기록한다.
- 이 단계는 populated `approval-request.yaml`와 pending queue item이 모두 있을 때만 허용된다.
- resolve 시 queue 상태가 `pending`에서 `approved|rejected|exceptions`로 이동한다.

## 역할 설명 (현재 MVP 기준)

Implementer:
- 승인된 PR 계획 범위에서만 변경한다.
- 구현 결과와 verification 입력값을 준비한다.

Reviewer:
- 설계 정합성/리스크/결함 관점으로 `record-review`에 반영될 판단 근거를 제공한다.

QA:
- 기능/회귀 관점 검증 결과를 `record-qa`로 반영한다.

Docs Sync:
- 문서 동기화 필요 여부와 완료 상태를 `record-docs-sync`로 반영한다.

Verification:
- `lint/tests/type-check/build` 상태를 `record-verification`로 기록한다.

## 반자동 MVP라는 점

- 명령 실행과 판정 업데이트는 CLI로 반자동 처리한다.
- 최종 승인 결정은 반드시 인간 승인자가 수행한다.
- 승인자의 명시적 결정을 반영하는 기록/queue 이동은 `resolve-approval`로 수행한다.
- `start-execution`은 최소 orchestration entrypoint일 뿐이며 이후 단계 자동 호출은 하지 않는다.
- rehearsal/demo 흔적 정리는 `cleanup-rehearsal`로 제한적으로만 수행하며 docs/contracts/history 전체 초기화는 허용하지 않는다.
- 시스템은 잘못된 순서를 줄이기 위한 최소 guardrail만 제공하며, planner automation이나 역할 자동 실행은 계속 제공하지 않는다.
- 승인 없는 범위 확대, 구조 변경 확정, 테스트 실패 무시는 금지다.

## run state 최소 해석

- `draft`: run bootstrap만 생성된 상태
- `in_progress`: execution 진행 중이며 role artifact를 기록하는 상태
- `approval_pending`: approval package가 준비되어 승인 대기 중인 상태
- `approved`: approve 기록이 끝난 상태
