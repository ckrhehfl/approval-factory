# PR-039 Plan

## input refs
- AGENTS.md v2026-04-02
- README.md
- docs/ops/runbook.md
- docs/ops/how-we-work.md
- docs/contracts/pr-plan-draft-contract.md
- docs/work-items/WI-039-promote-pr-plan-draft.md

## scope
- `factory promote-pr-plan-draft` 명령 추가
- PR plan draft markdown에서 deterministic source seed 파싱
- 기존 `create-pr-plan` 경로 재사용으로 official PR plan artifact 단일 생성
- linked work item id 및 draft summary/scope/validation intent 가능한 범위 보존
- draft file non-destructive 보장
- draft missing, duplicate PR id, readiness conflict 등 safe failure 처리
- tests/docs 동기화

## output summary
- operator가 PR plan draft를 검토한 뒤 필요한 경우에만 official PR plan 하나로 수동 승격할 수 있다.
- promoted PR plan은 기존 `create-pr-plan` 규칙을 그대로 따르며 active/archive semantics를 유지한다.
- 기존 readiness, approval, queue, selector, lifecycle semantics는 그대로 유지된다.

## risks
- 수동 promotion step이 auto-planning이나 auto-activation처럼 읽히지 않도록 wording을 엄격히 유지해야 한다.
- `create-pr-plan` 재사용이 깨지면 official PR artifact shape와 active/archive 규칙이 분기될 수 있다.

## next required gate
- Reviewer: no semantics change와 `create-pr-plan` path reuse 확인
- QA: safe failure, draft file non-destructive, active/archive semantics 유지 확인
- Docs Sync: README/runbook/how-we-work/contract wording 일치 확인
