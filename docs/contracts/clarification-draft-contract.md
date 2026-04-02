# Clarification Draft Contract

Clarification Draft는 Goal artifact를 바탕으로 operator가 수동 triage 전에 참고하는 repo-local Markdown artifact다.

## 저장 경로

- `clarification_drafts/<goal-id>.md`

## 생성 명령

- `factory draft-clarifications --root <repo> --goal-id <goal-id>`
- `factory promote-clarification-draft --root <repo> --goal-id <goal-id> --draft-index <n> --clarification-id <id>`

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
- operator는 draft item 하나를 `factory promote-clarification-draft`로 official clarification artifact 하나로 수동 승격할 수 있다.
- 승격 명령은 draft file을 삭제하거나 다시 쓰지 않는다.
- 승격 명령은 draft의 question, category, rationale(`source_rule`)를 official clarification에 보존한다.
- 승격 명령은 official clarification에 draft file path와 draft index provenance를 함께 기록한다.
- 승격 명령은 draft artifact missing, draft index missing, duplicate clarification id에서 안전하게 실패한다.
- draft를 거치지 않는 official clarification 생성은 계속 `factory create-clarification`로 수행할 수 있다.
