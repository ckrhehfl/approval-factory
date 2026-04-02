# WI-039: Promote PR Plan Draft

## Work Item ID
WI-039

## Goal ID
GOAL-039

## Title
Promote PR plan draft

## Status
draft

## Description
PR plan draft에서 operator가 검토한 단일 draft artifact를 official PR plan artifact로 수동 승격하는 최소 명령이 필요하다. 이번 범위는 draft file을 보존한 채 기존 `create-pr-plan` 경로를 재사용해 official artifact 하나만 생성하며, readiness, approval, queue, selector, active/archive, lifecycle semantics는 바꾸지 않는다.

## Scope
- `factory promote-pr-plan-draft` CLI 명령 추가
- `pr_plan_drafts/<work-item-id>.md` 단일 draft artifact 읽기
- `create-pr-plan` 경로 재사용으로 official PR plan artifact 하나 생성
- linked work item id 및 draft summary/scope/validation intent 가능한 범위 보존
- deterministic work item to PR id 대응(`WI-039 -> PR-039`) 적용
- draft file non-destructive 보장
- draft missing 및 `create-pr-plan` conflict safe failure 처리
- README, ops, contract, PR plan 문서 동기화

## Out of Scope
- PR plan draft auto-promotion
- auto-activation
- readiness semantics 변경
- approval semantics 변경
- queue semantics 변경
- selector behavior 변경
- active/archive semantics 변경
- lifecycle semantics 변경
- official PR artifact shape 신규 정의

## Acceptance Criteria
- `factory promote-pr-plan-draft --root <repo> --work-item-id <id>` 실행 시 official PR plan artifact 하나가 생성된다.
- 승격된 official PR plan은 linked work item id를 유지한다.
- 승격된 official PR plan은 draft의 summary/scope/validation intent를 가능한 범위에서 `Summary`/`Scope`/`Implementation Notes`에 보존한다.
- 승격은 기존 `create-pr-plan` 경로를 재사용하므로 official artifact shape와 active/archive 배치 규칙이 새로 갈라지지 않는다.
- draft file은 삭제되거나 수정되지 않는다.
- draft artifact가 없으면 안전하게 실패한다.
- target PR id 충돌, linked clarification missing 등 promotion이 기존 `create-pr-plan` 제약과 충돌하면 안전하게 실패한다.
- auto-activation, auto-promotion, readiness, approval, queue, selector, active/archive, lifecycle semantics는 그대로 유지된다.
- 관련 CLI 테스트가 통과한다.

## Dependencies
- PR plan draft contract
- PR artifact contract
- existing CLI safe-failure pattern

## Risks
- promotion 명령이 planning lifecycle 자동화처럼 읽히면 approval-first 운영 의미가 흐려질 수 있다.
- `create-pr-plan` 재사용이 깨지면 official PR artifact shape나 active/archive 규칙이 분기될 수 있다.

## Notes
- 이 명령은 수동 promotion step만 추가한다.
- draft를 거치지 않는 manual PR plan 생성 경로는 계속 `create-pr-plan`으로 유지한다.
