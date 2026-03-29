# PR-021 Plan

## Input Refs
- AGENTS.md vcurrent
- README.md
- docs/ops/runbook.md
- docs/ops/how-we-work.md
- docs/contracts/pr-contract.md
- docs/contracts/work-item-contract.md
- docs/work-items/WI-021-pr-plan-readiness-visibility.md
- docs/work-items/WI-020-work-item-readiness-visibility.md

## Scope
- `create-pr-plan`에서 source work item readiness visibility를 PR plan artifact로 승격
- PR-020 readiness 규칙/helper 재사용으로 summary 일관성 유지
- create-pr-plan 성공 출력에 readiness summary와 linked clarification count 추가
- tests/docs sync 반영

## Output Summary
- PR plan artifact가 source work item readiness context를 함께 기록해 operator auditability를 높인다.
- readiness는 gating이 아니라 planning visibility 강화다.
- active/archive, activate-pr, start-execution, gate, approval semantics는 유지한다.

## Risks
- `attention-needed`가 blocking처럼 읽히지 않도록 wording과 docs를 명확히 유지해야 한다.
- missing linked clarification artifact 처리와 readiness helper 규칙이 어긋나면 operator 신뢰도가 떨어진다.

## Next Required Gate
- Reviewer: helper 재사용과 visibility-only scope 확인
- QA: markdown/output regression, full test pass 확인
- Docs Sync: README/runbook/how-we-work/contract 반영 확인
