# PR Contract

PR은 실행 가능한 최소 승인 단위이며, 현재 MVP에서는 repo-local active PR plan Markdown artifact로 관리한다.

## active pr artifact

- 경로: `prs/active/<pr-id>.md`
- 생성 명령: `factory create-pr-plan --root <repo> --pr-id <id> --work-item-id <work-item-id> --title <title> --summary <text>`
- one-PR-at-a-time 원칙에 따라 `prs/active/`에는 항상 0 또는 1개의 PR plan만 존재해야 한다.

## 필수 항목

- PR ID
- Work Item ID
- Title
- Status
- Summary
- Scope
- Out of Scope
- Implementation Notes
- Risks
- Open Questions

## 규칙

- 기본 `Status`는 `planned`다.
- 동일 `pr-id`가 이미 존재하면 생성은 실패한다.
- 다른 active PR이 이미 존재해도 생성은 실패한다.
- archive 이동, merge/close lifecycle, multi-PR 관리, planner automation은 현재 범위가 아니다.
