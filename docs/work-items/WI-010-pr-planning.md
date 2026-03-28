# WI-010: Single Active PR Planning

## Work Item ID
WI-010

## Goal ID
GOAL-010

## Title
Single Active PR Planning

## Status
draft

## Description
Goal intake, clarification queue, Work Item 다음 단계로 현재 진행 중인 단 하나의 PR plan을 repo-local Markdown artifact로 명시적으로 생성하고 관리할 수 있어야 한다. 이번 범위는 `prs/active/` 아래 단일 active PR 계약과 CLI만 도입하며 multi-PR 관리나 planner automation은 포함하지 않는다.

## Scope
- `factory create-pr-plan` CLI 명령 추가
- `prs/active/<pr-id>.md` Markdown artifact 생성
- active PR plan 최소 섹션 계약 정의
- single active PR rule 및 duplicate `pr-id` 안전 실패 처리
- README 및 ops/PR 문서 동기화
- CLI 테스트 추가 및 `pytest -q` 통과

## Out of Scope
- multi-PR 관리
- PR archive 이동
- PR close/merge lifecycle
- planner automation
- LLM 연동

## Acceptance Criteria
- `factory create-pr-plan` 실행 시 `prs/active/<pr-id>.md`가 생성된다.
- active PR plan artifact에 PR ID, Work Item ID, Title, Status, Summary, Scope, Out of Scope, Implementation Notes, Risks, Open Questions 섹션이 포함된다.
- 기본 `Status`는 `planned`다.
- `prs/active/`에 다른 active PR이 이미 있으면 생성이 안전하게 실패한다.
- 동일 `pr-id`로 다시 생성하면 안전하게 실패한다.
- 기존 approval-first run/approval 흐름은 깨지지 않고 `pytest -q`가 통과한다.

## Dependencies
- Goal intake artifact contract
- clarification queue contract
- Work Item artifact contract
- existing CLI error handling pattern

## Risks
- 사용자가 active PR plan 도입을 multi-PR 보드나 lifecycle 기능으로 오해할 수 있다.
- 완료 후 archive 전략이 없으므로 운영자는 후속 PR 전까지 수동 규율을 유지해야 한다.

## Notes
- 이번 PR은 one-PR-at-a-time 원칙에 따라 PR-010 범위만 다룬다.
- archive 이동과 lifecycle 정리는 future work로 남긴다.
