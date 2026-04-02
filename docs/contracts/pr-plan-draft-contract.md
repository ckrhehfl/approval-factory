# PR Plan Draft Contract

PR Plan Draft는 official Work Item artifact를 바탕으로 operator가 수동 PR plan 생성 전에 참고하는 repo-local Markdown artifact다.

## 저장 경로

- `pr_plan_drafts/<work-item-id>.md`

## 생성 명령

- `factory draft-pr-plan --root <repo> --work-item-id <work-item-id>`

## 입력

- official work item artifact `docs/work-items/<work-item-id>.md`

## 필수 섹션

- Work Item ID
- Goal ID
- Work Item Title
- Source Work Item
- Draft Status
- Draft Method
- Operator Notes
- Suggested PR Title
- Suggested PR Summary
- Source Description
- Linked Clarifications
- Scope Seed
- Out of Scope Seed
- Acceptance Seed
- Dependency Seed
- Risk Seed
- Note Seed
- Promotion Guidance

## 규칙

- draft generation은 deterministic rule-based only다.
- source of truth는 official work item artifact다.
- `work_item_drafts/`는 입력으로 읽지 않는다.
- LLM integration은 없다.
- artifact는 repo-local로만 생성한다.
- official work item artifact가 없으면 안전하게 실패한다.
- 같은 `work-item-id` draft artifact가 이미 있으면 안전하게 실패한다.
- draft는 `prs/active/` 또는 `prs/archive/` official artifact를 만들거나 갱신하지 않는다.
- draft는 readiness, approval, queue, selector, active PR, lifecycle semantics를 바꾸지 않는다.
- draft output은 operator-facing markdown이며 official work item artifact의 내용을 deterministic seed로 재배열한다.
- operator는 draft를 검토한 뒤 필요한 경우에만 `factory create-pr-plan`으로 official PR plan artifact를 수동 생성한다.
