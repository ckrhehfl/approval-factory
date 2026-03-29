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
- clarification queue minimum
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

## 운영 흐름 (Goal -> clarification -> WI -> active PR -> run -> approval)

1. Goal intake
- `factory create-goal`로 `goals/<goal-id>.md`를 생성한다.
- Goal은 사람이 읽고 수정 가능한 Markdown artifact다.
- 현재 단계는 intake 저장 계약만 제공하며, planner/resolver는 다음 PR 범위다.

2. Clarification queue
- `factory create-clarification`로 `clarifications/<goal-id>/<clarification-id>.md`를 생성한다.
- clarification은 Goal intake 다음 단계의 최소 질문 관리 계층이다.
- 현재 단계는 질문 artifact 생성과 수동 관리까지만 제공하며, auto-generation/resolution은 다음 PR 범위다.

3. Work Item 정의
- `factory create-work-item`로 `docs/work-items/<work-item-id>.md`를 생성한다.
- Work Item은 Goal/clarification을 PR 실행 단위로 연결하는 수동 Markdown artifact다.
- 기본 섹션은 Work Item ID, Goal ID, Title, Status, Description, Scope, Out of Scope, Acceptance Criteria, Dependencies, Risks, Notes다.
- 현재 단계는 artifact 생성과 수동 관리까지만 제공하며 auto decomposition과 clarification 강제 연결은 다음 PR 범위다.

4. Active PR 계획
- `factory create-pr-plan`로 PR plan 후보를 생성한다.
- active PR plan은 Work Item을 현재 실행 중인 단 하나의 PR로 연결하는 수동 Markdown artifact다.
- 기본 섹션은 PR ID, Work Item ID, Title, Status, Summary, Scope, Out of Scope, Implementation Notes, Risks, Open Questions다.
- `prs/active/`는 항상 0 또는 1개의 PR만 가져야 한다.
- active PR가 없으면 `create-pr-plan`은 `prs/active/<pr-id>.md`를 만든다.
- active PR가 이미 있으면 `create-pr-plan`은 `prs/archive/<pr-id>.md`에 후보를 만든다.
- active PR를 명시적으로 바꿔야 할 때는 `factory activate-pr`로 기존 active를 `prs/archive/`로 옮기고 대상 PR을 active로 전환한다.
- 이번 범위는 PR-011 execution flow 보강용 최소 전환만 포함하며, lifecycle 전체나 multi-PR orchestration은 포함하지 않는다.

5. Run 부트스트랩
- `factory start-execution`으로 `prs/active/`의 단일 active PR plan을 읽어 `runs/latest/<run-id>/` 및 기본 artifact를 만든다.
- active PR가 사용자의 의도와 다르면 먼저 `activate-pr`로 전환한 뒤 실행한다.
- active PR plan의 `Work Item ID`가 실제 `docs/work-items/` artifact와 연결되지 않으면 시작하지 않는다.
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

6. 역할별 결과 기록
- Implementer/Reviewer/QA/Docs Sync/Verification 결과를 해당 record 명령으로 artifact에 반영한다.

7. 게이트 판정
- `factory gate-check`로 `gate-status.yaml`을 갱신한다.
 - 이 단계는 gate 판정 확인용이며, 최종 승인 요청 산출물 최신화 단계는 아니다.

8. 승인 패키지 생성
- `factory build-approval`로 `evidence-bundle.yaml`, `approval-request.yaml`를 최신 상태로 만든다.
- 이 단계는 `record-review`, `record-qa`, `record-docs-sync`, `record-verification`이 모두 실제로 기록된 뒤에만 허용된다.
- 조건이 맞으면 `approval_queue/pending/`에 approval 요청 파일이 적재된다.
- approval package가 생성되면 run state는 `approval_pending`이 된다.

9. 승인자 결정
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
