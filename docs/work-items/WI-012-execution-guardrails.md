# WI-012: Execution Guardrails / State Enforcement

## Status
Draft

## 문제 정의

현재 repo-local approval-factory는 end-to-end 실행 흐름을 수행할 수 있지만, placeholder artifact가 이미 생성되는 구조라서 사용자가 잘못된 순서로 `start-execution`, `build-approval`, `resolve-approval`를 호출해도 실수를 늦게 발견하기 쉽다.

## 목표

기존 file-based 흐름을 유지한 채, 승인자 중심 orchestration에 필요한 최소 guardrail과 run state refinement를 추가해 잘못된 순서를 더 명확히 차단한다.

## 포함 범위

- active PR plan과 실제 work item artifact 연결 검증
- `build-approval` prerequisite artifact 존재 및 recorded 상태 검증
- `resolve-approval` prerequisite artifact 및 pending queue 검증
- `run.yaml.state` 최소 상태 의미 정리와 자연스러운 갱신
- README / ops / PR plan 문서 동기화
- failure path 및 state transition 테스트 추가

## 비포함 범위

- 대규모 상태 머신 구현
- planner automation
- review/qa/docs-sync/verification 자동 실행
- PR lifecycle 전체 자동화
- multi-agent orchestration
- 기존 CLI breaking change

## 성공 기준

1. `factory start-execution --root <repo> --run-id <id>`는 active PR plan의 `Work Item ID`가 실제 `docs/work-items/` artifact와 연결되지 않으면 실패한다.
2. `factory build-approval --root <repo> --run-id <id>`는 `record-review`, `record-qa`, `record-docs-sync`, `record-verification` 중 하나라도 실제로 기록되지 않았으면 실패한다.
3. `factory resolve-approval --root <repo> --run-id <id> --decision ...`는 populated `approval-request.yaml`가 없거나 pending queue item이 없으면 실패한다.
4. `run.yaml.state`는 최소 `draft`, `in_progress`, `approval_pending`, `approved` 상태를 현재 호출 시점에 맞게 반영한다.
5. `pytest -q`가 통과한다.

## 리스크

- 기존 bootstrap placeholder artifact와 recorded artifact를 혼동하면 guardrail이 과하거나 약해질 수 있다.
- work item 연결 규칙이 애매하면 수동으로 유지하던 문서와 충돌할 수 있다.
- 상태 정의 변경 후 문서가 동기화되지 않으면 운영 혼선이 생길 수 있다.

## next required gate

- review
