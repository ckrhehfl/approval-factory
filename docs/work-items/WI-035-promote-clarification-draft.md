# WI-035: Promote Clarification Draft

## Work Item ID
WI-035

## Goal ID
GOAL-035

## Title
Promote clarification draft

## Status
draft

## Description
clarification draft에서 operator가 선택한 단일 항목을 official clarification artifact로 수동 승격하는 최소 명령이 필요하다. 이번 범위는 draft file을 보존한 채 provenance가 있는 clarification artifact 하나만 생성하며, readiness, approval, queue lifecycle, selector, auto-promotion semantics는 바꾸지 않는다.

## Scope
- `factory promote-clarification-draft` CLI 명령 추가
- `clarification_drafts/<goal-id>.md`에서 draft index 기준 단일 항목 선택
- `clarifications/<goal-id>/<clarification-id>.md` official artifact 하나 생성
- draft question/category/rationale 보존
- draft file path와 draft index provenance 기록
- draft missing, index missing, duplicate clarification id safe failure 처리
- README, ops, contract, PR plan 문서 동기화

## Out of Scope
- readiness semantics 변경
- approval semantics 변경
- queue lifecycle 변경
- selector behavior 변경
- auto-promotion behavior 추가
- draft file 삭제 또는 rewrite
- 다중 draft 일괄 승격

## Acceptance Criteria
- `factory promote-clarification-draft --root <repo> --goal-id <goal-id> --draft-index <n> --clarification-id <id>` 실행 시 official clarification artifact 하나가 생성된다.
- 승격된 official clarification은 draft의 question, category, rationale을 보존한다.
- 승격된 official clarification에는 draft file path와 draft index provenance가 기록된다.
- draft file은 삭제되거나 수정되지 않는다.
- draft artifact가 없으면 안전하게 실패한다.
- draft index가 없으면 안전하게 실패한다.
- target clarification id가 이미 있으면 안전하게 실패한다.
- readiness, approval, queue lifecycle, selector, auto-promotion semantics는 그대로 유지된다.
- 관련 CLI 테스트가 통과한다.

## Dependencies
- Clarification draft contract
- Clarification queue contract
- existing CLI safe-failure pattern

## Risks
- 승격 명령이 draft의 auto-promotion처럼 오해되면 approval-first 운영 의미가 흐려질 수 있다.
- promoted clarification이 provenance 없이 재작성되면 draft-origin auditability가 사라질 수 있다.

## Notes
- 이 명령은 수동 promotion step만 추가한다.
- draft를 거치지 않는 manual clarification 생성 경로는 계속 `create-clarification`으로 유지한다.
