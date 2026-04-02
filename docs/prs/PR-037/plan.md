# PR-037 Plan

## input refs
- AGENTS.md v2026-04-02
- README.md
- docs/ops/runbook.md
- docs/ops/how-we-work.md
- docs/contracts/work-item-draft-contract.md
- docs/work-items/WI-037-promote-work-item-draft.md

## scope
- `factory promote-work-item-draft` 명령 추가
- work item draft markdown에서 index 기준 단일 후보 파싱
- 기존 `create-work-item` 경로 재사용으로 official work item artifact 단일 생성
- draft candidate title/summary 및 source clarification linkage 보존
- draft file non-destructive 보장
- draft missing, index missing, duplicate work item id safe failure 처리
- tests/docs 동기화

## output summary
- operator가 work item draft에서 필요한 후보 하나만 명시적으로 official work item으로 승격할 수 있다.
- promoted work item은 draft candidate의 title/summary를 그대로 보존하고 source clarification linkage도 이어받는다.
- 기존 readiness, approval, queue, selector, active PR, lifecycle semantics는 그대로 유지된다.

## risks
- 수동 promotion step이 auto decomposition이나 lifecycle 변경처럼 읽히지 않도록 wording을 엄격히 유지해야 한다.
- `create-work-item` 재사용이 깨지면 official artifact shape가 분기될 수 있다.

## next required gate
- Reviewer: no semantics change와 `create-work-item` path reuse 확인
- QA: safe failure, draft file non-destructive, linked clarification preservation 확인
- Docs Sync: README/runbook/how-we-work/contract wording 일치 확인
