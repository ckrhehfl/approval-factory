# Factory Runbook

## 정상 운영 순서

0. 현재 상태 확인이 필요하면 `factory status`로 active PR, latest run, approval 상태, open clarification을 한 번에 본다.
1. Work Item 생성
2. Goal intake 필요 시 `factory create-goal`로 `goals/<goal-id>.md` 생성
3. Goal 기준 clarification 필요 시 `factory create-clarification`로 `clarifications/<goal-id>/<clarification-id>.md` 생성
4. `factory create-work-item`로 `docs/work-items/<work-item-id>.md` 생성
5. `factory create-pr-plan`로 PR plan 후보 생성
6. active PR가 없으면 `prs/active/<pr-id>.md`, 이미 있으면 `prs/archive/<pr-id>.md`에 저장
7. 필요 시 `factory activate-pr`로 기존 active PR을 `prs/archive/`로 옮기고 의도한 PR을 active로 전환
8. `factory start-execution`로 active PR plan에서 `runs/latest/<run-id>/` 시작
9. Scope 승인
10. 설계 초안 생성
11. Architecture 승인 필요 여부 판정
12. PR별 구현
13. Verification 기록(lint/tests/type_check/build)
14. Review
15. QA
16. Docs Sync 완료
17. `gate-check`로 gate 판정 확인
18. `build-approval`로 Evidence Bundle + Approval Request 생성
19. `resolve-approval`로 승인자 결정 기록 및 queue 정리
20. Merge

## goal intake 최소 계약

- Goal artifact는 `goals/<goal-id>.md`에 저장한다.
- 생성 명령은 `factory create-goal --root <repo> --goal-id <id> --title <title> --problem <text> --outcome <text> [--constraints <text>]` 이다.
- 생성되는 문서는 사람 검토용 Markdown이며 다음 섹션을 항상 포함한다:
  - Goal ID
  - Title
  - Status
  - Problem
  - Desired Outcome
  - Non-Goals
  - Constraints
  - Risks
  - Open Questions
  - Approval-Required Decisions
  - Success Criteria
- 동일 `goal-id`가 이미 존재하면 명령은 실패한다.
- 현재 PR 범위에서 goal artifact는 intake 저장 계약만 제공한다.
- 질문 자동 생성, goal 해소, Work Item 자동 분해, LLM 연결은 아직 없다.

## clarification queue 최소 계약

- clarification artifact는 `clarifications/<goal-id>/<clarification-id>.md`에 저장한다.
- 생성 명령은 `factory create-clarification --root <repo> --goal-id <goal-id> --clarification-id <id> --title <title> --category <scope|design|dependency|constraint|approval-required> --question <text> [--escalation]` 이다.
- clarification은 Goal intake 다음 단계의 최소 질문 관리 계층이다.
- 생성되는 문서는 사람 검토용 Markdown이며 다음 섹션을 항상 포함한다:
  - Clarification ID
  - Goal ID
  - Title
  - Status
  - Category
  - Question
  - Suggested Resolution
  - Escalation Required
  - Resolution Notes
  - Next Action
- 기본 `Status`는 `open`이다.
- 동일 `goal-id` 아래 동일 `clarification-id`가 이미 존재하면 명령은 실패한다.
- 이번 PR 범위에서 clarification queue는 artifact 생성과 수동 관리까지만 제공한다.
- 질문 자동 생성, 질문 자동 해결, goal-to-WI 자동 분해, resolver/planner 구현, LLM 연결은 아직 없다.

## work item 최소 계약

- Work Item artifact는 `docs/work-items/<work-item-id>.md`에 저장한다.
- 생성 명령은 `factory create-work-item --root <repo> --work-item-id <id> --title <title> --goal-id <goal-id> --description <text> [--acceptance-criteria <text>]` 이다.
- Work Item은 Goal/clarification을 실제 PR 실행 단위로 연결하는 최소 수동 계층이다.
- 생성되는 문서는 사람 검토용 Markdown이며 다음 섹션을 항상 포함한다:
  - Work Item ID
  - Goal ID
  - Title
  - Status
  - Description
  - Scope
  - Out of Scope
  - Acceptance Criteria
  - Dependencies
  - Risks
  - Notes
- 기본 `Status`는 `draft`다.
- `--acceptance-criteria`를 생략하면 `Acceptance Criteria`는 `TBD`로 채운다.
- 동일 `work-item-id`가 이미 존재하면 명령은 실패한다.
- 이번 PR 범위에서 Work Item은 artifact 생성과 수동 관리까지만 제공한다.
- Goal to Work Item 자동 분해, clarification 강한 연결, planner 자동화, LLM 연결은 아직 없다.

## active pr plan 최소 계약

- active PR plan artifact는 `prs/active/<pr-id>.md`에 저장한다.
- archived PR plan artifact는 `prs/archive/<pr-id>.md`에 저장한다.
- 생성 명령은 `factory create-pr-plan --root <repo> --pr-id <id> --work-item-id <work-item-id> --title <title> --summary <text>` 이다.
- active PR plan은 one-PR-at-a-time 원칙을 명시하는 최소 수동 계층이다.
- 생성되는 문서는 사람 검토용 Markdown이며 다음 섹션을 항상 포함한다:
  - PR ID
  - Work Item ID
  - Title
  - Status
  - Summary
  - Scope
  - Out of Scope
  - Implementation Notes
  - Risks
  - Open Questions
- 기본 `Status`는 `planned`다.
- `prs/active/`에는 항상 0 또는 1개의 PR plan만 존재해야 한다.
- 동일 `pr-id`가 `prs/active/` 또는 `prs/archive/`에 이미 존재하면 명령은 실패한다.
- active PR plan이 없으면 `create-pr-plan`은 새 plan을 active에 만든다.
- 다른 active PR plan이 이미 존재하면 `create-pr-plan`은 새 plan 후보를 archive에 만든다.
- active PR 전환은 `factory activate-pr --root <repo> --pr-id <id>`로 수행한다.
- `activate-pr`는 기존 active PR을 `prs/archive/`로 이동시키고, 지정한 PR plan을 active로 이동시켜 `prs/active/`에 정확히 하나의 PR만 남긴다.
- 이번 PR 범위에서 close/merge lifecycle 전체, history 관리, multi-PR 관리, planner automation, LLM 연결은 구현하지 않는다.

## start-execution 최소 계약

- run 시작 명령은 `factory start-execution --root <repo> --run-id <run-id>` 이다.
- `prs/active/` 아래 active PR plan이 정확히 하나 있어야 한다.
- active PR plan의 `Work Item ID`는 `docs/work-items/` 아래 실제 work item artifact 하나와 연결되어야 한다.
- 사용자가 active PR를 바꾸려면 먼저 `activate-pr`로 `prs/active/`를 명시적으로 전환해야 한다.
- 명령은 active PR plan에서 `PR ID`, `Work Item ID`, `Title` 섹션을 읽는다.
- 내부적으로 기존 `bootstrap-run` 흐름을 재사용해 `runs/latest/<run-id>/`와 기본 artifact를 생성한다.
- 생성된 run에는 최소 `run_id`, `pr_id`, `work_item_id`, `pr_plan_path`, `work_item_path`가 식별 가능하게 남아야 한다.
- run 시작 시 `run.yaml.state`는 `in_progress`로 갱신된다.
- active PR plan이 0개이거나 2개 이상이거나, work item 연결이 불가하면 명령은 안전하게 실패한다.
- 이번 PR 범위에서 `start-execution`은 run bootstrap entrypoint만 제공하며 review/qa/docs-sync/verification 자동 실행은 하지 않는다.

## gate-check와 build-approval의 역할 차이

- `gate-check`는 `gate-status.yaml` 판정만 갱신한다.
- `build-approval`는 evidence를 재생성하고 gate를 다시 계산한 뒤 `approval-request.yaml`를 만든다.
- `build-approval`는 `record-review`, `record-qa`, `record-docs-sync`, `record-verification`이 실제로 실행되어 각 artifact에 `recorded_at`이 남은 뒤에만 진행된다.
- 최종 승인 요청 판단은 `build-approval` 이후 산출물을 기준으로 한다.

## run state 최소 규칙

- `draft`: bootstrap만 된 상태
- `in_progress`: execution이 시작됐고 verification/review/qa/docs-sync 기록이 진행 중인 상태
- `approval_pending`: approval package가 생성되어 승인 대기 중인 상태
- `approved`: 승인자가 approve를 기록한 상태
- `rejected`: 승인자가 reject를 기록한 상태

## status 최소 계약

- 상태 조회 명령은 `factory status --root <repo>` 이다.
- 이 명령은 읽기 전용이며 어떤 artifact도 생성, 수정, 이동하지 않는다.
- active PR 정보는 `prs/active/*.md`에서 읽는다.
- latest run 정보는 `runs/latest/*/run.yaml` 중 가장 최근 갱신된 run에서 읽는다.
- approval 상태는 latest run 기준으로 `approval_queue/approved/`, `approval_queue/pending/`, `approval-decision.yaml`를 읽어 `approved`, `pending`, `none` 중 하나로 보여준다.
- open clarification은 `clarifications/*/*.md` 중 `Status=open` 인 항목의 `Clarification ID`를 나열한다.
- active PR, latest run, approval이 없으면 각 섹션에서 `none`으로 보여준다.
- 출력 형식은 단순 텍스트이며 JSON 출력은 제공하지 않는다.

## 실패 시 복구

### 설계 불명확
Architect/Planner 단계로 되돌린다.

### 테스트 실패
Implementer로 되돌린다.  
예외 허용이 필요하면 exception approval로 올린다.

### verification artifact 누락
`verification-report.yaml`을 먼저 생성/갱신한 뒤 gate-check 및 build-approval을 다시 실행한다.

### review/qa/docs-sync 미기록 상태에서 build-approval 실행
누락된 `record-*` 명령을 먼저 실행한다. placeholder artifact만 있는 상태는 prerequisite 충족으로 보지 않는다.

### 문서 누락
Docs Sync 단계로 되돌린다.

### approval request 또는 pending queue 누락
`build-approval`를 다시 실행해 `approval-request.yaml`와 `approval_queue/pending/APR-<run-id>.yaml`를 복구한 뒤 `resolve-approval`를 재시도한다.

### 승인 반려
해당 반려 사유를 기준으로 Planner 또는 Architect 단계로 되돌린다.

## 재실행/재시도 운영 규칙

### canonical artifact 규칙
- `runs/latest/<run-id>/artifacts/*.yaml`는 canonical 파일이며 재실행 시 **overwrite** 된다.
- `bootstrap-run`을 동일 `run-id`로 다시 실행하면 기존 artifact를 초기화하지 않고 **누락 파일만 생성**한다.
- `start-execution`은 active PR plan을 읽은 뒤 `bootstrap-run` 기반으로 동일 규칙을 따른다.

### approval queue 규칙
- 기본 queue 파일명은 `approval_queue/pending/APR-<run-id>.yaml` 이다.
- 동일 내용으로 `build-approval`를 재실행하면 queue 파일을 중복 생성하지 않는다.
- 같은 파일명이 이미 존재하고 내용이 다르면 `APR-<run-id>--r2.yaml`, `--r3` 순으로 append한다.

### pending 이후 승인자 운영 (현재 MVP)
- 승인자는 `approval_queue/pending/*.yaml`와 `runs/latest/<run-id>/artifacts/{evidence-bundle,approval-request}.yaml`를 함께 검토한다.
- 승인자 결정은 `factory resolve-approval --decision {approve|reject|exception}`으로 기록한다.
- resolve 시 `runs/latest/<run-id>/artifacts/approval-decision.yaml`이 생성/갱신된다.
- resolve 시 queue 파일은 `pending`에서 `approved|rejected|exceptions`로 이동한다.
- `resolve-approval`는 populated `approval-request.yaml`와 pending queue item이 모두 없으면 실패한다.
- 이미 같은 결정으로 처리된 run을 다시 resolve해도 idempotent하게 동작한다.

### gate/build 재실행 추적
- `run.yaml`의 `run.operations`에 `gate_check`, `build_approval` 실행 횟수(`count`)와 마지막 실행 정보(`last_at`, `last_details`)를 남긴다.
- 운영자는 재실행 이력이 많을 때 `last_details`의 gate/decision 값이 최신 산출물과 일치하는지 확인한다.

## 운영자 원칙

- 한 번에 하나의 PR만 승인하지 말고 Work Item 전체 맥락도 본다.
- `prs/active/`에 active PR이 하나를 초과하지 않는지 먼저 확인한다.
- active PR를 바꿔야 하면 수동 파일 편집 대신 `activate-pr`를 사용한다.
- `start-execution` 전에도 `prs/active/` 단일성 유지와 plan 섹션 계약을 확인한다.
- `start-execution` 전에는 active PR의 `Work Item ID`가 실제 `docs/work-items/` artifact와 연결되는지도 확인한다.
- evidence 없는 속도는 금지한다.
- 설계와 구현이 엇갈리면 구현보다 문서와 ADR을 먼저 본다.
