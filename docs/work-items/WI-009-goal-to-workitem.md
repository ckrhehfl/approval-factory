# WI-009: Goal to Work Item Decomposition

## Work Item ID
WI-009

## Goal ID
GOAL-009

## Title
Goal to Work Item Decomposition

## Status
draft

## Description
Goal intake와 clarification queue 다음 단계로, 사람이 검토 가능한 최소 Work Item artifact를 repo-local Markdown 형식으로 생성하고 관리할 수 있어야 한다. 이번 범위는 Goal/clarification을 실제 실행 단위와 연결하는 계약과 CLI만 도입하며 자동 decomposition은 포함하지 않는다.

## Scope
- `factory create-work-item` CLI 명령 추가
- `docs/work-items/<work-item-id>.md` Markdown artifact 생성
- Work Item 최소 섹션 계약 정의
- duplicate `work-item-id` 안전 실패 처리
- README 및 ops/PR 문서 동기화
- CLI 테스트 추가 및 `pytest -q` 통과

## Out of Scope
- Goal to Work Item 자동 분해
- clarification과의 강한 연결 강제
- planner/resolver 자동화
- LLM 연동

## Acceptance Criteria
- `factory create-work-item` 실행 시 `docs/work-items/<work-item-id>.md`가 생성된다.
- Work Item artifact에 Work Item ID, Goal ID, Title, Status, Description, Scope, Out of Scope, Acceptance Criteria, Dependencies, Risks, Notes 섹션이 포함된다.
- 기본 `Status`는 `draft`다.
- 동일 `work-item-id`로 다시 생성하면 안전하게 실패한다.
- 기존 approval-first run/approval 흐름은 깨지지 않고 `pytest -q`가 통과한다.

## Dependencies
- Goal intake artifact contract
- clarification queue contract
- existing CLI error handling pattern

## Risks
- 사용자가 Work Item 도입을 자동 decomposition으로 오해할 수 있다.
- Work Item 파일명이 기존 `WI-###-slug.md` 문서와 혼재되어 naming convention 정리가 후속 PR에서 필요할 수 있다.

## Notes
- 이번 PR은 one-PR-at-a-time 원칙에 따라 PR-009 범위만 다룬다.
- clarification linkage는 future PR에서 강화 여부를 결정한다.
