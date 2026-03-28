# PR Contract

PR은 실행 가능한 최소 승인 단위이며, 현재 MVP에서는 repo-local PR plan Markdown artifact로 관리한다.

## active pr artifact

- 경로: `prs/active/<pr-id>.md`
- 생성 명령: `factory create-pr-plan --root <repo> --pr-id <id> --work-item-id <work-item-id> --title <title> --summary <text>`
- 생성 규칙: active PR가 없을 때만 `create-pr-plan`이 여기에 생성한다.
- one-PR-at-a-time 원칙에 따라 `prs/active/`에는 항상 0 또는 1개의 PR plan만 존재해야 한다.

## archive pr artifact

- 경로: `prs/archive/<pr-id>.md`
- 후보 생성 규칙: active PR가 이미 있으면 `create-pr-plan`이 새 PR plan 후보를 여기에 생성한다.
- 전환 명령: `factory activate-pr --root <repo> --pr-id <id>`
- `activate-pr`는 현재 active PR plan을 archive로 이동시키고 지정한 PR plan을 active로 이동시키는 최소 file-based 전환만 제공한다.

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
- 동일 `pr-id`가 `prs/active/` 또는 `prs/archive/`에 이미 존재하면 생성은 실패한다.
- 다른 active PR이 이미 존재하면 새 PR plan 후보는 `prs/archive/`에 생성한다.
- `activate-pr` 실행 후 `prs/active/`에는 정확히 1개의 PR plan만 남아야 한다.
- merge/close lifecycle 전체, history 관리, multi-PR orchestration, planner automation은 현재 범위가 아니다.
