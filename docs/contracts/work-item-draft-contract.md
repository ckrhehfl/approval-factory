# Work Item Draft Contract

Work Item Draft는 Goal artifact와 official clarification artifacts를 바탕으로 operator가 수동 work item 생성 전에 참고하는 repo-local Markdown artifact다.

## 저장 경로

- `work_item_drafts/<goal-id>.md`

## 생성 명령

- `factory draft-work-items --root <repo> --goal-id <goal-id>`

## 승격 명령

- `factory promote-work-item-draft --root <repo> --goal-id <goal-id> --draft-index <n> --work-item-id <id>`

## 입력

- `goals/<goal-id>.md`
- official clarification artifacts `clarifications/<goal-id>/*.md`

## 필수 섹션

- Goal ID
- Goal Title
- Source Goal
- Source Clarifications
- Draft Status
- Draft Method
- Operator Notes
- Candidate Work Items
- Promotion Guidance

## 규칙

- draft generation은 deterministic rule-based only다.
- source of truth는 official clarification artifacts다.
- `clarification_drafts/`는 입력으로 읽지 않는다.
- LLM integration은 없다.
- artifact는 repo-local로만 생성한다.
- goal artifact가 없으면 안전하게 실패한다.
- 같은 `goal-id` draft artifact가 이미 있으면 안전하게 실패한다.
- official clarification artifact가 없어도 zero-candidate draft artifact는 생성한다.
- draft는 `docs/work-items/` official artifact를 만들거나 갱신하지 않는다.
- draft는 readiness, approval, queue, selector, active PR, lifecycle semantics를 바꾸지 않는다.
- draft output은 operator-facing markdown이며 Candidate Work Items 아래 초안 항목을 제공할 수 있다.
- operator는 draft를 검토한 뒤 필요한 경우에만 `factory promote-work-item-draft` 또는 별도 `factory create-work-item`으로 official work item artifact를 수동 생성한다.
- operator는 draft candidate 하나만 index로 선택해 official work item artifact 하나로 승격할 수 있다.
- 승격된 official work item은 draft candidate의 `title`을 official `Title`, `summary`를 official `Description`으로 보존한다.
- draft candidate에 `source_clarification_id`가 있으면 같은 goal 아래 linked clarification context를 official work item에 함께 남긴다.
- 승격은 기존 `create-work-item` 경로를 재사용하며 새 official artifact shape를 도입하지 않는다.
- draft file은 승격 중에도 변경되지 않는다.
- draft artifact가 없거나 draft index가 없거나 target work item id가 이미 있으면 `promote-work-item-draft`는 안전하게 실패한다.
