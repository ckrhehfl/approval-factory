# Work Item Contract

Work Item은 Goal/clarification을 PR 실행 계획으로 연결하는 repo-local Markdown artifact다.

## 저장 경로

- `docs/work-items/<work-item-id>.md`

## 생성 명령

- `factory create-work-item --root <repo> --work-item-id <id> --title <title> --goal-id <goal-id> --description <text> [--acceptance-criteria <text>] [--clarification-id <id> ...]`

## 필수 섹션

- Work Item ID
- Goal ID
- Title
- Status
- Description
- Related Clarifications
- Scope
- Out of Scope
- Acceptance Criteria
- Dependencies
- Risks
- Notes

## 규칙

- 기본 `Status`는 `draft`다.
- 동일 `work-item-id`가 이미 존재하면 생성 명령은 안전하게 실패한다.
- `--clarification-id`는 0개 이상 반복 가능하며, 생략하면 기존 동작을 유지한다.
- linked clarification은 모두 같은 `goal-id` 아래 `clarifications/<goal-id>/<clarification-id>.md`로 해석한다.
- clarification이 없거나 다른 goal 아래만 존재하면 생성 명령은 안전하게 실패한다.
- `Related Clarifications`는 `clarification_id (status)` 목록으로 기록하고, linkage가 없으면 `- none`으로 기록한다.
- artifact는 사람 검토와 수동 분해를 위한 계약이며 Goal to Work Item 자동 분해는 현재 범위에 없다.
- clarification 연결은 선택 사항이며, 이번 범위는 추적성 hardening만 추가한다. unresolved clarification 자동 차단, 자동 추천, 자동 해결은 하지 않는다.
