# WI-034: Goal Clarification Draft

## Work Item ID
WI-034

## Goal ID
GOAL-034

## Title
Goal clarification draft

## Status
draft

## Description
Goal artifact만 읽어서 operator가 검토할 수 있는 clarification draft markdown을 deterministic rule-based 방식으로 생성해야 한다. 이번 범위는 artifact-only automation step만 도입하며 official clarification queue, readiness, approval, lifecycle semantics는 바꾸지 않는다.

## Scope
- `factory draft-clarifications` CLI 명령 추가
- `goals/<goal-id>.md`를 읽어 `clarification_drafts/<goal-id>.md` 생성
- deterministic rule-based draft rendering helper 추가
- goal missing 및 duplicate draft safe failure 처리
- README, ops, contract, PR plan 문서 동기화
- CLI 테스트 추가 및 기존 clarification queue semantics 회귀 방지

## Out of Scope
- official clarification queue artifact 자동 생성
- `clarifications/` auto-promotion
- readiness, approval, queue, selector, lifecycle semantics 변경
- LLM integration
- draft artifact inspection/resolve lifecycle 추가

## Acceptance Criteria
- `factory draft-clarifications --root <repo> --goal-id <goal-id>` 실행 시 `clarification_drafts/<goal-id>.md`가 생성된다.
- draft output은 deterministic rule-based operator-facing markdown이다.
- goal artifact가 없으면 안전하게 실패한다.
- 같은 goal-id draft artifact가 이미 있으면 안전하게 실패한다.
- command는 official clarification queue artifact를 생성하거나 갱신하지 않는다.
- 기존 readiness, approval, queue, selector, lifecycle semantics는 그대로 유지된다.
- 관련 CLI 테스트가 통과한다.

## Dependencies
- Goal intake artifact contract
- clarification queue contract
- existing CLI safe-failure pattern

## Risks
- operator가 draft artifact를 official clarification queue와 혼동할 수 있다.
- heuristic wording이 너무 공격적으로 읽히면 scope 변경 제안처럼 오해될 수 있다.

## Notes
- 이번 PR은 minimum artifact-only automation step만 다룬다.
- draft에서 official clarification으로의 승격은 사람의 수동 판단으로만 허용한다.
