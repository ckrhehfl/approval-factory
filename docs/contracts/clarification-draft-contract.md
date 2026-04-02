# Clarification Draft Contract

Clarification Draft는 Goal artifact를 바탕으로 operator가 수동 triage 전에 참고하는 repo-local Markdown artifact다.

## 저장 경로

- `clarification_drafts/<goal-id>.md`

## 생성 명령

- `factory draft-clarifications --root <repo> --goal-id <goal-id>`

## 입력

- `goals/<goal-id>.md`

## 필수 섹션

- Goal ID
- Goal Title
- Source Goal
- Draft Status
- Draft Method
- Operator Notes
- Suggested Clarifications
- Promotion Guidance

## 규칙

- draft generation은 deterministic rule-based only다.
- LLM integration은 없다.
- artifact는 repo-local로만 생성한다.
- goal artifact가 없으면 안전하게 실패한다.
- 같은 `goal-id` draft artifact가 이미 있으면 안전하게 실패한다.
- draft는 official clarification queue artifact를 만들거나 갱신하지 않는다.
- draft는 `clarifications/`로 auto-promotion하지 않는다.
- draft는 readiness, approval, queue, selector, lifecycle semantics를 바꾸지 않는다.
- draft output은 operator-facing markdown이며, Suggested Clarifications 아래 초안 항목을 제공할 수 있다.
- official clarification 생성은 계속 `factory create-clarification`로만 수행한다.
