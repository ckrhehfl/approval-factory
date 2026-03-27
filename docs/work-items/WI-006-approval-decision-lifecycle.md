# WI-006: Approval Decision Lifecycle Hardening

## Status
In Progress (PR-006)

## 문제 정의

현재 MVP는 `build-approval` 단계까지는 안정적으로 동작하지만, pending 이후 승인자 결정(`approve/reject/exception`)을 일관되게 기록하고 queue를 정리하는 공식 CLI/artifact가 약하다.

## 목표

승인 요청이 `approval_queue/pending/`에 적재된 이후, 승인자가 명시적 결정을 남기고 queue를 정리할 수 있는 repo-local/file-based lifecycle을 추가한다.

## 포함 범위

- `factory resolve-approval` CLI 추가
- `approve|reject|exception` 결정별 queue 이동
- `approval-decision.yaml` 생성/갱신
- idempotent 재실행 안전성 확보
- README/ops/PR 문서 동기화

## 비포함 범위

- GitHub API/Slack/UI/central control plane 연동
- merge/release 자동화
- 기존 `build-approval` 범위 외 대규모 리팩토링

## 성공 기준

1. `factory resolve-approval --decision approve|reject|exception`이 정상 동작한다.
2. `approval_queue/pending/APR-<run-id>.yaml`가 결정별 target queue로 이동한다.
3. `runs/latest/<run-id>/artifacts/approval-decision.yaml`에 필수 필드가 기록된다.
4. 이미 처리된 run에 대한 재실행은 idempotent하게 동작한다.
5. `pytest -q`가 통과한다.

## 리스크

- 상충 결정 입력(예: 승인 후 반려 시도) 시 운영 혼선이 생길 수 있어 명확한 오류 처리 필요.
- 수동으로 조작된 queue 파일 구조가 표준에서 벗어나면 resolve 실패 가능.

## next required gate

- review
