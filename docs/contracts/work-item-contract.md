# Work Item Contract

Work Item은 Goal/clarification을 PR 실행 계획으로 연결하는 repo-local Markdown artifact다.

## 저장 경로

- `docs/work-items/<work-item-id>.md`

## 생성 명령

- `factory create-work-item --root <repo> --work-item-id <id> --title <title> --goal-id <goal-id> --description <text> [--acceptance-criteria <text>]`

## 필수 섹션

- Work Item ID
- Goal ID
- Title
- Status
- Description
- Scope
- Out of Scope
- Acceptance Criteria
- Dependencies
- Risks
- Notes

## 규칙

- 기본 `Status`는 `draft`다.
- 동일 `work-item-id`가 이미 존재하면 생성 명령은 안전하게 실패한다.
- artifact는 사람 검토와 수동 분해를 위한 계약이며 Goal to Work Item 자동 분해는 현재 범위에 없다.
- clarification 연결은 선택 사항이며 현재 PR 범위에서는 강제하지 않는다.
