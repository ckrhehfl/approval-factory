# Factory Runbook

## 정상 운영 순서

1. Work Item 생성
2. Scope 승인
3. 설계 초안 생성
4. Architecture 승인 필요 여부 판정
5. PR 분해
6. PR별 구현
7. Verification 기록(lint/tests/type_check/build)
8. Review
9. QA
10. Docs Sync 완료
11. Evidence Bundle 생성
12. Merge Approval 요청
13. Merge

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

### gate/build 재실행 추적
- `run.yaml`의 `run.operations`에 `gate_check`, `build_approval` 실행 횟수(`count`)와 마지막 실행 정보(`last_at`, `last_details`)를 남긴다.
- 운영자는 재실행 이력이 많을 때 `last_details`의 gate/decision 값이 최신 산출물과 일치하는지 확인한다.

## 운영자 원칙

- 한 번에 하나의 PR만 승인하지 말고 Work Item 전체 맥락도 본다.
- evidence 없는 속도는 금지한다.
- 설계와 구현이 엇갈리면 구현보다 문서와 ADR을 먼저 본다.
