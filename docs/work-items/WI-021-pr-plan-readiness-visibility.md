# WI-021: pr plan readiness visibility

## Input Refs
- AGENTS.md vcurrent
- README.md current
- docs/ops/runbook.md current
- docs/ops/how-we-work.md current
- docs/contracts/pr-contract.md current
- docs/contracts/work-item-contract.md current
- docs/work-items/WI-020-work-item-readiness-visibility.md

## Scope
- `factory create-pr-plan`가 source work item readiness context를 읽어 PR plan artifact에 기록하도록 보강
- PR plan markdown에 readiness summary와 linked clarification 목록 섹션 추가
- create-pr-plan 성공 출력, 테스트, 운영/계약 문서 최소 동기화

## Problem
`factory work-item-readiness`로는 linked clarification readiness를 읽기 전용으로 확인할 수 있지만, 실제 PR planning artifact 자체에는 그 맥락이 충분히 남지 않는다. 다음 자동화 이전 단계로 PR plan 문서가 source work item readiness context를 함께 들고 있어야 operator auditability가 좋아진다.

## Output Summary
- `create-pr-plan`이 PR-020 readiness helper를 재사용해 `no-linked-clarifications|ready|attention-needed` summary를 PR plan에 기록
- PR plan markdown에 `Work Item Readiness`, `Linked Clarifications` 섹션 추가
- readiness는 visibility only이며 `attention-needed`여도 PR plan 생성은 허용

## Risks
- readiness visibility가 blocking semantics처럼 보이면 approval-first 운영 계약이 흔들릴 수 있다.
- PR plan markdown 형식 변경이 기존 active/archive 흐름이나 operator reading order를 과도하게 흔들면 사용성이 떨어질 수 있다.

## Next Required Gate
- Implementer: helper 재사용, markdown/output/test/docs sync 반영
- Reviewer: visibility-only 범위와 no-breaking-change 확인
- QA: readiness summary regression과 active/archive semantics 유지 확인
