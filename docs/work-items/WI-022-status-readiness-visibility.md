# WI-022: status readiness visibility minimum

## Input Refs
- AGENTS.md vcurrent
- README.md current
- docs/ops/runbook.md current
- docs/ops/how-we-work.md current
- docs/contracts/status-contract.md current
- docs/contracts/work-item-contract.md current
- docs/work-items/WI-020-work-item-readiness-visibility.md
- docs/work-items/WI-021-pr-plan-readiness-visibility.md

## Scope
- `factory status`에 active PR 기준 work item readiness summary를 read-only로 노출
- PR-020 readiness helper와 summary 규칙 재사용
- readiness read 실패 시 status 전체 대신 readiness 섹션만 제한적으로 degraded 표시
- 최소 테스트와 계약/운영 문서 동기화

## Problem
현재 operator는 `factory status`로 active PR, latest run, approval, open clarification을 볼 수 있지만, active PR의 source work item readiness는 별도 `factory work-item-readiness`나 PR plan artifact를 다시 열어 봐야 한다. 다음 최소 계층으로 status 한 번만으로 현재 repo-local readiness context를 파악할 수 있어야 한다.

## Output Summary
- `factory status`가 active PR가 있을 때 source work item readiness summary와 linked clarification count를 함께 보여준다.
- readiness summary 규칙은 계속 `no-linked-clarifications|ready|attention-needed`만 사용한다.
- readiness는 visibility only이며 gating, approval, activation, execution semantics를 바꾸지 않는다.

## Risks
- readiness가 status에 붙으면서 blocking signal처럼 오해될 수 있으므로 read-only wording을 유지해야 한다.
- readiness artifact 누락 시 status 전체를 실패시키면 operator visibility가 오히려 나빠지므로 degraded 표시 범위를 readiness 섹션으로 제한해야 한다.

## Next Required Gate
- Implementer: status rendering/helper/tests/docs sync 반영
- Reviewer: visibility-only 범위와 no-breaking-change 확인
- QA: readiness summary/error handling 회귀와 전체 테스트 통과 확인
