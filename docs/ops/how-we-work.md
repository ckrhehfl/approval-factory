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

## 운영 흐름 (Goal -> clarification -> WI -> PR -> run -> approval)

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

4. PR 단위 계획
- `docs/prs/PR-###/plan.md` 중심으로 one-PR-at-a-time 실행 계획을 고정한다.

5. Run 부트스트랩
- `factory bootstrap-run`으로 `runs/latest/<run-id>/` 및 기본 artifact를 만든다.

6. 역할별 결과 기록
- Implementer/Reviewer/QA/Docs Sync/Verification 결과를 해당 record 명령으로 artifact에 반영한다.

7. 게이트 판정
- `factory gate-check`로 `gate-status.yaml`을 갱신한다.
 - 이 단계는 gate 판정 확인용이며, 최종 승인 요청 산출물 최신화 단계는 아니다.

8. 승인 패키지 생성
- `factory build-approval`로 `evidence-bundle.yaml`, `approval-request.yaml`를 최신 상태로 만든다.
- 조건이 맞으면 `approval_queue/pending/`에 approval 요청 파일이 적재된다.

9. 승인자 결정
- 승인자는 queue 파일과 evidence를 보고 `approve/reject/exception`을 결정한다.
- `factory resolve-approval`로 승인 결정을 `approval-decision.yaml`에 기록한다.
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
- 승인 없는 범위 확대, 구조 변경 확정, 테스트 실패 무시는 금지다.
