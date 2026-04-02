# WI-036: Draft Work Items

## Work Item ID
WI-036

## Goal ID
GOAL-036

## Title
Draft work items

## Status
draft

## Description
official clarification artifact를 source of truth로 삼아 operator가 검토할 수 있는 work item draft markdown을 deterministic rule-based 방식으로 생성해야 한다. 이번 범위는 artifact-only drafting step만 도입하며 official work item 생성, readiness, approval, queue, selector, active PR, lifecycle semantics는 바꾸지 않는다.

## Scope
- `factory draft-work-items` CLI 명령 추가
- `goals/<goal-id>.md`와 `clarifications/<goal-id>/*.md`를 읽어 `work_item_drafts/<goal-id>.md` 생성
- deterministic rule-based work item candidate rendering helper 추가
- goal missing 및 duplicate draft safe failure 처리
- official clarification이 없어도 zero-candidate draft artifact 생성
- `clarification_drafts/` non-input 보장
- README, ops, contract, PR plan 문서 동기화

## Out of Scope
- `docs/work-items/` official artifact auto-creation
- readiness semantics 변경
- approval semantics 변경
- queue lifecycle 변경
- selector behavior 변경
- active PR semantics 변경
- LLM integration

## Acceptance Criteria
- `factory draft-work-items --root <repo> --goal-id <goal-id>` 실행 시 `work_item_drafts/<goal-id>.md`가 생성된다.
- draft output은 deterministic rule-based operator-facing markdown이다.
- draft generation은 official clarification artifacts를 source of truth로 사용한다.
- command는 `clarification_drafts/`를 입력으로 읽지 않는다.
- goal artifact가 없으면 안전하게 실패한다.
- 같은 goal-id draft artifact가 이미 있으면 안전하게 실패한다.
- official clarification이 없어도 zero-candidate draft artifact는 생성된다.
- command는 `docs/work-items/` 아래 아무것도 생성하지 않는다.
- 기존 readiness, approval, queue, selector, active PR, lifecycle semantics는 그대로 유지된다.
- 관련 CLI 테스트가 통과한다.

## Dependencies
- Goal intake artifact contract
- clarification queue contract
- existing CLI safe-failure pattern

## Risks
- operator가 work item draft를 official work item 생성으로 오해할 수 있다.
- non-official input을 섞으면 source-of-truth 규칙이 약해질 수 있다.

## Notes
- 이번 PR은 minimum artifact-only drafting step만 다룬다.
- official work item 생성은 계속 `factory create-work-item`으로만 수행한다.
