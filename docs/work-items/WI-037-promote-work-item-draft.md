# WI-037: Promote Work Item Draft

## Work Item ID
WI-037

## Goal ID
GOAL-037

## Title
Promote work item draft

## Status
draft

## Description
work item draft에서 operator가 선택한 단일 후보를 official work item artifact로 수동 승격하는 최소 명령이 필요하다. 이번 범위는 draft file을 보존한 채 기존 `create-work-item` 경로를 재사용해 official artifact 하나만 생성하며, readiness, approval, queue, selector, active PR, lifecycle semantics는 바꾸지 않는다.

## Scope
- `factory promote-work-item-draft` CLI 명령 추가
- `work_item_drafts/<goal-id>.md`에서 draft index 기준 단일 후보 선택
- `docs/work-items/<work-item-id>.md` official artifact 하나 생성
- draft candidate의 title/summary를 official title/description으로 보존
- source clarification id가 있으면 linked clarification context 보존
- draft file non-destructive 보장
- draft missing, index missing, duplicate work item id safe failure 처리
- README, ops, contract, PR plan 문서 동기화

## Out of Scope
- work item draft auto-promotion
- 다중 draft 일괄 승격
- readiness semantics 변경
- approval semantics 변경
- queue semantics 변경
- selector behavior 변경
- active PR semantics 변경
- lifecycle semantics 변경
- official work item artifact shape 신규 정의

## Acceptance Criteria
- `factory promote-work-item-draft --root <repo> --goal-id <goal-id> --draft-index <n> --work-item-id <id>` 실행 시 official work item artifact 하나가 생성된다.
- 승격된 official work item은 draft candidate의 title/summary를 각각 official `Title`/`Description`으로 보존한다.
- draft candidate에 source clarification id가 있으면 승격된 official work item의 `Related Clarifications`에도 같은 context가 남는다.
- 승격은 기존 `create-work-item` 경로를 재사용하므로 official artifact shape가 새로 갈라지지 않는다.
- draft file은 삭제되거나 수정되지 않는다.
- draft artifact가 없으면 안전하게 실패한다.
- draft index가 없으면 안전하게 실패한다.
- target work item id가 이미 있으면 안전하게 실패한다.
- auto-promotion, bulk promotion, readiness, approval, queue, selector, active PR, lifecycle semantics는 그대로 유지된다.
- 관련 CLI 테스트가 통과한다.

## Dependencies
- Work item draft contract
- Work item artifact contract
- existing CLI safe-failure pattern

## Risks
- 승격 명령이 auto decomposition 또는 auto-promotion처럼 읽히면 approval-first 운영 의미가 흐려질 수 있다.
- create path를 재사용하지 않으면 official work item artifact shape가 이중화될 수 있다.

## Notes
- 이 명령은 수동 promotion step만 추가한다.
- draft를 거치지 않는 manual work item 생성 경로는 계속 `create-work-item`으로 유지한다.
