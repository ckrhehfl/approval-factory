# PR-022 Plan

## Input Refs
- AGENTS.md vcurrent
- README.md
- docs/ops/runbook.md
- docs/ops/how-we-work.md
- docs/contracts/status-contract.md
- docs/contracts/work-item-contract.md
- docs/work-items/WI-022-status-readiness-visibility.md
- docs/work-items/WI-020-work-item-readiness-visibility.md
- docs/work-items/WI-021-pr-plan-readiness-visibility.md

## Scope
- `factory status`에 active PR 기준 work item readiness visibility 추가
- PR-020 readiness helper/summary 규칙 재사용
- readiness read failure를 status 전체가 아니라 readiness 섹션에만 제한
- status/create-pr-plan/activate-pr/start-execution semantics 회귀 테스트 보강
- README/runbook/how-we-work/status contract 문서 동기화

## Output Summary
- operator가 `factory status` 한 번으로 active PR, latest run, approval 상태와 함께 source work item readiness context를 읽을 수 있다.
- readiness는 계속 visibility only이고 gating/approval 의미는 추가되지 않는다.
- artifact read 문제에도 status 나머지 섹션은 계속 보여 주므로 repo-local 운영 가시성이 유지된다.

## Risks
- `attention-needed` 또는 `unavailable`가 command blocking처럼 오해되지 않도록 wording과 contract를 명확히 유지해야 한다.
- status와 `work-item-readiness`의 규칙이 어긋나면 operator 신뢰도가 떨어지므로 helper 재사용이 중요하다.

## Next Required Gate
- Reviewer: status visibility-only 범위, helper 재사용, no-breaking-change 확인
- QA: active PR 유무, readiness summary variants, degraded handling, 전체 테스트 통과 확인
- Docs Sync: README/runbook/how-we-work/status contract 반영 확인
