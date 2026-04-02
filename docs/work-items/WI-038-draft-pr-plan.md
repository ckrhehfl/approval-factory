# WI-038: Draft PR Plan

## Work Item ID
WI-038

## Goal ID
GOAL-038

## Title
Draft PR plan

## Status
draft

## Description
official work item artifact를 source of truth로 삼아 operator가 검토할 수 있는 PR plan draft markdown을 deterministic rule-based 방식으로 생성해야 한다. 이번 범위는 artifact-only drafting step만 도입하며 readiness, approval, queue, selector, active PR, lifecycle semantics는 바꾸지 않는다.

## Scope
- `factory draft-pr-plan` CLI 명령 추가
- `docs/work-items/<work-item-id>.md`를 읽어 `pr_plan_drafts/<work-item-id>.md` 생성
- deterministic rule-based PR plan draft rendering helper 추가
- work item missing 및 duplicate draft safe failure 처리
- `work_item_drafts/` non-input 보장
- `prs/active/`, `prs/archive/` 비생성 보장
- README, ops, contract, PR plan 문서 동기화

## Out of Scope
- official PR plan auto-creation
- readiness semantics 변경
- approval semantics 변경
- queue semantics 변경
- selector behavior 변경
- active PR semantics 변경
- lifecycle semantics 변경
- LLM integration

## Acceptance Criteria
- `factory draft-pr-plan --root <repo> --work-item-id <work-item-id>` 실행 시 `pr_plan_drafts/<work-item-id>.md`가 생성된다.
- draft output은 deterministic rule-based operator-facing markdown이다.
- draft generation은 official work item artifact를 source of truth로 사용한다.
- command는 `work_item_drafts/`를 입력으로 읽지 않는다.
- official work item artifact가 없으면 안전하게 실패한다.
- 같은 work-item-id draft artifact가 이미 있으면 안전하게 실패한다.
- command는 `prs/active/` 또는 `prs/archive/` 아래 아무것도 생성하지 않는다.
- 기존 readiness, approval, queue, selector, active PR, lifecycle semantics는 그대로 유지된다.
- 관련 CLI 테스트가 통과한다.

## Dependencies
- Work item artifact contract
- existing CLI safe-failure pattern

## Risks
- operator가 draft artifact를 official PR plan으로 오해할 수 있다.
- work item draft를 입력으로 잘못 섞으면 source-of-truth 규칙이 약해질 수 있다.

## Notes
- 이번 PR은 minimum artifact-only drafting step만 다룬다.
- official PR plan 생성은 계속 `factory create-pr-plan`으로만 수행한다.
