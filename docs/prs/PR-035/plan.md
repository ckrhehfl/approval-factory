# PR-035 Plan

## input refs
- AGENTS.md v2026-04-02
- README.md
- docs/ops/runbook.md
- docs/ops/how-we-work.md
- docs/contracts/clarification-draft-contract.md
- docs/work-items/WI-035-promote-clarification-draft.md

## scope
- `factory promote-clarification-draft` 명령 추가
- draft markdown에서 index 기준 단일 항목 파싱
- official clarification artifact 단일 생성과 provenance 기록
- draft file non-destructive 보장
- draft missing, index missing, duplicate clarification id safe failure 처리
- tests/docs 동기화

## output summary
- operator가 draft에서 필요한 항목 하나만 명시적으로 official clarification으로 승격할 수 있다.
- promoted clarification은 draft의 question, category, rationale과 provenance를 함께 남긴다.
- 기존 readiness, approval, queue lifecycle, selector, auto-promotion semantics는 그대로 유지된다.

## risks
- 수동 promotion step이 queue lifecycle 변경처럼 읽히지 않도록 wording을 엄격히 유지해야 한다.
- clarification rewrite 경로가 provenance section을 잃으면 문서 계약과 audit trail이 깨질 수 있다.

## next required gate
- Reviewer: no semantics change와 provenance preservation 확인
- QA: safe failure, draft file non-destructive, resolve path preservation 확인
- Docs Sync: README/runbook/how-we-work/contract wording 일치 확인
