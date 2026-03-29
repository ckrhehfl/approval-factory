# PR-020 Plan

## Input Refs
- AGENTS.md vcurrent
- README.md
- docs/ops/runbook.md
- docs/ops/how-we-work.md
- docs/contracts/work-item-contract.md
- docs/work-items/WI-020-work-item-readiness-visibility.md
- docs/work-items/WI-019-work-item-clarification-linkage.md

## Scope
- `factory work-item-readiness` read-only visibility 명령 추가
- work item linked clarification의 현재 status를 읽는 helper 추가
- readiness summary 규칙 테스트 고정
- 관련 운영/계약 문서 동기화

## Output Summary
- operator가 특정 work item에 대해 clarification 관점 readiness를 짧게 확인할 수 있는 최소 CLI 제공
- linked clarification 없음=`no-linked-clarifications`, 모두 resolved=`ready`, open/deferred/escalated 존재=`attention-needed`
- 기존 create-work-item, create-pr-plan, start-execution, gate, approval semantics는 유지

## Risks
- visibility summary를 future gating처럼 오해하면 범위가 넓어질 수 있다.
- linked clarification artifact 누락 처리 정책이 느슨하면 operator가 잘못된 readiness를 볼 수 있다.

## Next Required Gate
- Reviewer: visibility-only scope와 UX 톤 확인
- QA: missing artifact failure 포함 회귀 확인
- Docs Sync: README/runbook/contract 반영 확인
