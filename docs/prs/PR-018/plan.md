# PR-018 Plan

## Input Refs
- AGENTS.md vcurrent
- README.md
- docs/ops/runbook.md
- docs/ops/how-we-work.md
- docs/work-items/WI-008-clarification-queue.md
- docs/work-items/WI-018-clarification-resolution-minimum.md

## Scope
- clarification queue 최소 resolution 계약 추가
- `factory resolve-clarification` CLI와 artifact field update만 구현
- `factory status`의 open clarification read-only 규칙 유지
- commit/push/release, auto resolution, auto WI decomposition, approval queue 자동 연동 제외

## Output Summary
- `resolved|deferred|escalated`로 clarification artifact를 공식 종결하는 최소 수동 명령 추가
- 없는 clarification, 이미 닫힌 clarification 재처리 시 안전 실패
- 성공/실패/status 회귀 테스트와 운영 문서 보강

## Plan
1. clarification markdown contract와 status 판독 규칙을 shared helper 기준으로 정리
2. `resolve-clarification` parser와 pipeline update 로직 추가
3. status가 open clarification만 유지하는 회귀 테스트 추가
4. README/runbook/how-we-work에 decision 의미와 범위 제한 반영
5. 전체 테스트로 기존 create-clarification 흐름과 비파괴성 확인

## Risks
- 종결 명령이 lifecycle automation처럼 읽히면 현재 approval-first 운영 계약을 흐릴 수 있다.
- 같은 artifact를 재구성할 때 기존 section ordering이나 기본값 형식이 깨지면 문서 계약이 손상될 수 있다.

## Next Required Gate
- Reviewer approval for semantics preservation
- QA verification on full test suite
