# Factory Runbook

## 정상 운영 순서

1. Work Item 생성
2. Goal intake 필요 시 `factory create-goal`로 `goals/<goal-id>.md` 생성
3. Scope 승인
4. 설계 초안 생성
5. Architecture 승인 필요 여부 판정
6. PR 분해
7. PR별 구현
8. Verification 기록(lint/tests/type_check/build)
9. Review
10. QA
11. Docs Sync 완료
12. `gate-check`로 gate 판정 확인
13. `build-approval`로 Evidence Bundle + Approval Request 생성
14. `resolve-approval`로 승인자 결정 기록 및 queue 정리
15. Merge

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
- evidence 없는 속도는 금지한다.
- 설계와 구현이 엇갈리면 구현보다 문서와 ADR을 먼저 본다.
