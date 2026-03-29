# WI-018: clarification resolution minimum

## Input Refs
- AGENTS.md vcurrent
- README.md clarification queue and status sections
- docs/ops/runbook.md clarification queue and status contracts
- docs/ops/how-we-work.md clarification flow summary
- docs/work-items/WI-008-clarification-queue.md

## Scope
- `factory resolve-clarification` 최소 CLI 추가
- clarification artifact 수동 종결 계약 추가
- `factory status`의 open clarification 판독과 정합성 유지
- 관련 테스트와 운영 문서 보강

## Problem
clarification queue는 생성만 가능하면 운영자가 공식적으로 닫을 수 없어 queue가 쌓이기만 한다. 다음 구조 확장 전에 사람이 repo-local artifact를 명시적으로 `resolved`, `deferred`, `escalated`로 정리하는 최소 계약이 먼저 필요하다.

## Output Summary
- 기존 `create-clarification` 형식은 유지한 채 clarification artifact 상태 갱신 명령 추가
- open clarification만 status에 남는 read-only 규칙 유지
- 자동 resolution, 자동 WI 분해, approval queue 자동 연동 없이 최소 수동 종결 계층만 추가

## Risks
- resolution semantics를 과하게 넓히면 goal/work-item/run 상태까지 바뀌는 것으로 오해될 수 있다.
- markdown field 갱신이 기존 artifact 형식과 어긋나면 status/read tooling과 drift가 생길 수 있다.

## Next Required Gate
- Implementer: CLI/helper/tests/docs sync
- Reviewer: no breaking change and scope containment 확인
- QA: full test suite와 status regression 확인
