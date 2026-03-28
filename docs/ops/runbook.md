# Factory Runbook

## 정상 운영 순서

1. Work Item 생성
2. Goal intake 필요 시 `factory create-goal`로 `goals/<goal-id>.md` 생성
3. Goal 기준 clarification 필요 시 `factory create-clarification`로 `clarifications/<goal-id>/<clarification-id>.md` 생성
4. `factory create-work-item`로 `docs/work-items/<work-item-id>.md` 생성
5. `factory create-pr-plan`로 `prs/active/<pr-id>.md` 생성
6. Scope 승인
7. 설계 초안 생성
8. Architecture 승인 필요 여부 판정
9. PR별 구현
10. Verification 기록(lint/tests/type_check/build)
11. Review
12. QA
13. Docs Sync 완료
14. `gate-check`로 gate 판정 확인
15. `build-approval`로 Evidence Bundle + Approval Request 생성
16. `resolve-approval`로 승인자 결정 기록 및 queue 정리
17. Merge

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
- 동일 `pr-id`가 이미 존재하면 명령은 실패한다.
- 다른 active PR plan이 이미 존재해도 명령은 실패한다.
- 이번 PR 범위에서 archive 이동, close/merge lifecycle, multi-PR 관리, planner automation, LLM 연결은 구현하지 않는다.

## gate-check와 build-approval의 역할 차이

- `gate-check`는 `gate-status.yaml` 판정만 갱신한다.
- `build-approval`는 evidence를 재생성하고 gate를 다시 계산한 뒤 `approval-request.yaml`를 만든다.
- 최종 승인 요청 판단은 `build-approval` 이후 산출물을 기준으로 한다.

## 실패 시 복구

### 설계 불명확
Architect/Planner 단계로 되돌린다.

### 테스트 실패
Implementer로 되돌린다.  
예외 허용이 필요하면 exception approval로 올린다.

### verification artifact 누락
`verification-report.yaml`을 먼저 생성/갱신한 뒤 gate-check 및 build-approval을 다시 실행한다.

### 문서 누락
Docs Sync 단계로 되돌린다.

### 승인 반려
해당 반려 사유를 기준으로 Planner 또는 Architect 단계로 되돌린다.

## 재실행/재시도 운영 규칙

### canonical artifact 규칙
- `runs/latest/<run-id>/artifacts/*.yaml`는 canonical 파일이며 재실행 시 **overwrite** 된다.
- `bootstrap-run`을 동일 `run-id`로 다시 실행하면 기존 artifact를 초기화하지 않고 **누락 파일만 생성**한다.

### approval queue 규칙
- 기본 queue 파일명은 `approval_queue/pending/APR-<run-id>.yaml` 이다.
- 동일 내용으로 `build-approval`를 재실행하면 queue 파일을 중복 생성하지 않는다.
- 같은 파일명이 이미 존재하고 내용이 다르면 `APR-<run-id>--r2.yaml`, `--r3` 순으로 append한다.

### pending 이후 승인자 운영 (현재 MVP)
- 승인자는 `approval_queue/pending/*.yaml`와 `runs/latest/<run-id>/artifacts/{evidence-bundle,approval-request}.yaml`를 함께 검토한다.
- 승인자 결정은 `factory resolve-approval --decision {approve|reject|exception}`으로 기록한다.
- resolve 시 `runs/latest/<run-id>/artifacts/approval-decision.yaml`이 생성/갱신된다.
- resolve 시 queue 파일은 `pending`에서 `approved|rejected|exceptions`로 이동한다.
- 이미 같은 결정으로 처리된 run을 다시 resolve해도 idempotent하게 동작한다.

### gate/build 재실행 추적
- `run.yaml`의 `run.operations`에 `gate_check`, `build_approval` 실행 횟수(`count`)와 마지막 실행 정보(`last_at`, `last_details`)를 남긴다.
- 운영자는 재실행 이력이 많을 때 `last_details`의 gate/decision 값이 최신 산출물과 일치하는지 확인한다.

## 운영자 원칙

- 한 번에 하나의 PR만 승인하지 말고 Work Item 전체 맥락도 본다.
- `prs/active/`에 active PR이 하나를 초과하지 않는지 먼저 확인한다.
- evidence 없는 속도는 금지한다.
- 설계와 구현이 엇갈리면 구현보다 문서와 ADR을 먼저 본다.
