# Factory Runbook

## 정상 운영 순서

0. 현재 상태 확인이 필요하면 `factory status`로 active PR, latest run, approval 상태, open clarification을 한 번에 본다.
1. Work Item 생성
2. Goal intake 필요 시 `factory create-goal`로 `goals/<goal-id>.md` 생성
3. Goal 기준 clarification 필요 시 `factory create-clarification`로 `clarifications/<goal-id>/<clarification-id>.md` 생성
4. clarification을 공식 종결해야 하면 `factory resolve-clarification`로 `resolved|deferred|escalated` 중 하나를 기록
5. `factory create-work-item`로 `docs/work-items/<work-item-id>.md` 생성
6. `factory create-pr-plan`로 PR plan 후보 생성
7. active PR가 없으면 `prs/active/<pr-id>.md`, 이미 있으면 `prs/archive/<pr-id>.md`에 저장
8. 필요 시 `factory activate-pr`로 기존 active PR을 `prs/archive/`로 옮기고 의도한 PR을 active로 전환
9. `factory start-execution`로 active PR plan에서 `runs/latest/<run-id>/` 시작
10. Scope 승인
11. 설계 초안 생성
12. Architecture 승인 필요 여부 판정
13. PR별 구현
14. Verification 기록(lint/tests/type_check/build)
15. Review
16. QA
17. Docs Sync 완료
18. `gate-check`로 gate 판정 확인
19. `build-approval`로 Evidence Bundle + Approval Request 생성
20. `resolve-approval`로 승인자 결정 기록 및 queue 정리
21. Merge

run convenience:
- `start-execution` 직후 이어지는 run-scoped 명령은 `--run-id <id>` 대신 `--latest`를 사용할 수 있다.
- `--latest`는 `factory status`와 같은 latest-run 규칙을 사용하므로 operator가 방금 확인한 latest run과 같은 대상을 잡는다.
- 명시성이 더 중요하거나 과거 run을 다시 다뤄야 할 때는 기존 `--run-id <id>`를 계속 사용한다.

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
- 종결 명령은 `factory resolve-clarification --root <repo> --goal-id <goal-id> --clarification-id <id> --decision <resolved|deferred|escalated> --resolution-notes <text> --next-action <text> [--suggested-resolution <text>]` 이다.
- clarification은 Goal intake 다음 단계의 최소 질문 관리 계층이다.
- clarification queue는 생성만 가능하면 운영이 막히므로, 이번 단계는 사람이 artifact를 명시적으로 닫는 최소 수동 계약까지 포함한다.
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
- `resolve-clarification`은 기존 문서 형식을 유지한 채 `Status`, `Resolution Notes`, `Next Action`, `Escalation Required`를 갱신한다.
- `decision=escalated`면 `Escalation Required=yes`, `resolved|deferred`면 `no`로 기록한다.
- `Status`가 `open`이 아닌 clarification은 다시 `resolve-clarification`할 수 없다.
- clarification 종결은 artifact 상태 업데이트까지만 수행하며 goal/work-item/pr/run/approval queue 상태를 자동 변경하지 않는다.
- 동일 `goal-id` 아래 동일 `clarification-id`가 이미 존재하면 명령은 실패한다.
- status는 계속 open clarification만 보여주며, `resolved|deferred|escalated` 된 항목은 open clarification 목록에서 제거된다.
- 이번 PR 범위에서 clarification queue는 artifact 생성과 수동 종결까지만 제공한다.
- 질문 자동 생성, 질문 자동 해결, goal-to-WI 자동 분해, resolver/planner 구현, LLM 연결은 아직 없다.

## work item 최소 계약

- Work Item artifact는 `docs/work-items/<work-item-id>.md`에 저장한다.
- 생성 명령은 `factory create-work-item --root <repo> --work-item-id <id> --title <title> --goal-id <goal-id> --description <text> [--acceptance-criteria <text>] [--clarification-id <id> ...]` 이다.
- Work Item은 Goal/clarification을 실제 PR 실행 단위로 연결하는 최소 수동 계층이다.
- 생성되는 문서는 사람 검토용 Markdown이며 다음 섹션을 항상 포함한다:
  - Work Item ID
  - Goal ID
  - Title
  - Status
  - Description
  - Related Clarifications
  - Scope
  - Out of Scope
  - Acceptance Criteria
  - Dependencies
  - Risks
  - Notes
- 기본 `Status`는 `draft`다.
- `--acceptance-criteria`를 생략하면 `Acceptance Criteria`는 `TBD`로 채운다.
- `--clarification-id`는 반복 가능하며, 모두 같은 `goal-id` 아래 clarification artifact여야 한다.
- linked clarification은 Work Item 문서에 `- <clarification-id> (<status>)`로 기록한다.
- clarification을 지정하지 않으면 `Related Clarifications`는 `- none`으로 기록한다.
- clarification이 없거나 다른 goal 아래만 있으면 명령은 기대 경로와 다음 action을 함께 보여주며 실패한다.
- 동일 `work-item-id`가 이미 존재하면 명령은 실패한다.
- 이번 PR 범위에서 Work Item은 artifact 생성과 수동 관리까지만 제공한다.
- unresolved clarification을 자동 차단하지 않으며 사람이 status를 보고 판단한다.
- Goal to Work Item 자동 분해, clarification 자동 추천/해결, planner 자동화, LLM 연결은 아직 없다.

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
- CLI 출력은 생성 위치가 active인지 archive인지와 artifact path를 함께 보여준다.
- archive 생성이면 이유가 "이미 active PR 존재"로 명시되고, 다음에 실행할 `factory activate-pr --root . --pr-id <id>` 예시가 같이 나온다.
- active PR 전환은 `factory activate-pr --root <repo> --pr-id <id>`로 수행한다.
- `activate-pr`는 기존 active PR을 `prs/archive/`로 이동시키고, 지정한 PR plan을 active로 이동시켜 `prs/active/`에 정확히 하나의 PR만 남긴다.
- `activate-pr` 성공 출력은 archive로 이동된 이전 active와 새 active path를 함께 요약한다.
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
- guardrail 실패 시 CLI는 왜 실패했는지와 다음에 확인할 repo-local 상태, 다음 명령 예시를 함께 출력해야 한다.
- 이번 PR 범위에서 `start-execution`은 run bootstrap entrypoint만 제공하며 review/qa/docs-sync/verification 자동 실행은 하지 않는다.

## gate-check와 build-approval의 역할 차이

- `gate-check`는 `gate-status.yaml` 판정만 갱신한다.
- `build-approval`는 evidence를 재생성하고 gate를 다시 계산한 뒤 `approval-request.yaml`를 만든다.
- `build-approval`는 `record-review`, `record-qa`, `record-docs-sync`, `record-verification`이 실제로 실행되어 각 artifact에 `recorded_at`이 남은 뒤에만 진행된다.
- 최종 승인 요청 판단은 `build-approval` 이후 산출물을 기준으로 한다.

## run selector 최소 계약

- 대상 명령은 `record-review`, `record-qa`, `record-docs-sync`, `record-verification`, `gate-check`, `build-approval`, `resolve-approval` 이다.
- 각 명령은 `--run-id <id>` 또는 `--latest` 중 하나를 사용한다.
- `--run-id`와 `--latest`를 함께 주면 실패한다.
- 둘 다 없으면 명령은 실패한다.
- `--latest`는 `runs/latest/*/run.yaml` 중 `updated_at` 우선, 없으면 `created_at` 기준으로 가장 최근 run 하나를 고른다.
- timestamp가 같으면 `run_id`가 더 큰 run을 고른다.
- latest run이 없으면 먼저 `factory start-execution --root <repo> --run-id <run-id>`로 run을 만들거나 `--run-id <id>`를 명시한다.

예시:

```bash
factory status --root .
factory record-review --root . --latest --status pass --summary "review ok"
factory gate-check --root . --latest
factory build-approval --root . --latest
factory resolve-approval --root . --latest --decision approve --actor approver.local --note "all gates satisfied"
```

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
- status는 가능하면 active PR path, latest run path, approval queue/artifact path도 함께 보여준다.
- open clarification은 `clarifications/*/*.md` 중 `Status=open` 인 항목의 `Clarification ID`를 count와 함께 읽기 쉽게 보여준다.
- `resolve-clarification`로 종결된 항목은 status에서 더 이상 open clarification으로 보이지 않는다.
- active PR, latest run, approval이 없으면 각 섹션에서 `none`으로 보여준다.
- 출력 형식은 단순 텍스트이며 JSON 출력은 제공하지 않는다.

operator 해석 팁:
- `factory status`에서 active PR path와 latest run path를 같이 보면 "내가 어떤 PR/run을 보고 있는지"를 즉시 확인할 수 있다.
- approval이 `pending` 또는 `approved`면 표시된 path를 기준으로 queue/artifact를 바로 열어 본다.
- `start-execution` guardrail 메시지는 bug report가 아니라 현재 active PR 흐름을 먼저 정리하라는 운영 안내로 해석한다.

## cleanup-rehearsal 최소 계약

- 운영 baseline 정리 명령은 `factory cleanup-rehearsal --root <repo> [--apply] [--include-demo]` 이다.
- 기본 동작은 dry-run이며, 제거 대상 경로를 요약 출력하지만 파일 시스템은 변경하지 않는다.
- 실제 삭제는 `--apply`가 있을 때만 수행한다.
- 기본 cleanup 범위는 공식 rehearsal prefix인 `RH` artifact만이다.
- `--include-demo`를 추가하면 legacy scratch/demo 흔적인 `DEMO` artifact도 함께 cleanup 한다.
- demo cleanup은 prefix형 `RUN-DEMO-*`뿐 아니라 suffix/infix형 `RUN-*-DEMO*` 및 `APR-RUN-*-DEMO*` naming variant도 포함한다.
- cleanup은 partial normalization만 허용한다. docs/contracts/history 전체 reset은 제공하지 않는다.
- `docs/prs/` 아래 이력 문서는 cleanup 대상이 아니다.
- `README.md`, `docs/contracts/*`, `docs/adr/*`, 코드, 테스트는 cleanup 대상이 아니다.
- apply 시 matched target만 제거하고, 비대상 파일은 그대로 유지한다.
- rehearsal/demo active PR 또는 open clarification만 남아 있던 fixture에서도 cleanup 후 `factory status`에 stale 항목이 남지 않아야 한다.

기본 rehearsal 대상:
- `runs/latest/RUN-RH-*`
- `approval_queue/pending/APR-RUN-RH-*.yaml`
- `approval_queue/approved/APR-RUN-RH-*.yaml`
- `approval_queue/rejected/APR-RUN-RH-*.yaml`
- `approval_queue/exceptions/APR-RUN-RH-*.yaml`
- `goals/GOAL-RH-*.md`
- `clarifications/GOAL-RH-*`
- `docs/work-items/WI-RH-*.md`
- `prs/active/PR-RH-*.md`
- `prs/archive/PR-RH-*.md`

`--include-demo` 추가 대상:
- `runs/latest/RUN-DEMO-*`
- `runs/latest/RUN-*-DEMO*`
- `approval_queue/pending/APR-RUN-DEMO-*.yaml`
- `approval_queue/pending/APR-RUN-*-DEMO*.yaml`
- `approval_queue/approved/APR-RUN-DEMO-*.yaml`
- `approval_queue/approved/APR-RUN-*-DEMO*.yaml`
- `approval_queue/rejected/APR-RUN-DEMO-*.yaml`
- `approval_queue/rejected/APR-RUN-*-DEMO*.yaml`
- `approval_queue/exceptions/APR-RUN-DEMO-*.yaml`
- `approval_queue/exceptions/APR-RUN-*-DEMO*.yaml`
- `goals/*DEMO*.md`
- `clarifications/*DEMO*`
- `docs/work-items/*DEMO*.md`
- `prs/active/*DEMO*.md`
- `prs/archive/*DEMO*.md`

운영 예시:

```bash
factory cleanup-rehearsal --root .
factory cleanup-rehearsal --root . --apply
factory cleanup-rehearsal --root . --apply --include-demo
```

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
`--latest`로 실행했다면 에러에 표시된 run-id를 그대로 따라 해당 run에 필요한 `record-*` 명령을 다시 실행한다.

### 문서 누락
Docs Sync 단계로 되돌린다.

### approval request 또는 pending queue 누락
`build-approval`를 다시 실행해 `approval-request.yaml`와 `approval_queue/pending/APR-<run-id>.yaml`를 복구한 뒤 `resolve-approval`를 재시도한다.
`--latest`를 사용했다면 먼저 `factory status`로 latest run이 의도한 run인지 확인한다.

### rehearsal/demo 흔적이 운영 상태를 오염시키는 경우
먼저 `factory cleanup-rehearsal --root <repo>`로 dry-run 결과를 확인한다.  
정리 대상이 맞으면 `--apply`를 붙여 rehearsal baseline만 정리하고, legacy demo까지 제거해야 할 때만 `--include-demo`를 추가한다.

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
