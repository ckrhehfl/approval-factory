# WI-011: Approval-Driven Execution Flow

## Work Item ID
WI-011

## Goal ID
GOAL-011

## Title
Approval-Driven Execution Flow

## Status
draft

## Description
active PR plan과 실제 run bootstrap 사이의 공식 연결이 필요하다. PR-011 보강 범위에서는 repo-local, file-based 방식으로 `prs/active/`의 단일 active PR plan을 읽어 run을 시작하는 최소 execution flow를 유지하면서, active PR가 이미 있어도 새 PR plan 후보를 `prs/archive/`에 만들고 `activate-pr`로 명시적으로 전환할 수 있는 minimum flow를 추가한다.

## Scope
- `factory start-execution` CLI 명령 추가
- `factory activate-pr` CLI 명령 추가
- active PR 유무에 따른 `create-pr-plan` active/archive 후보 생성 규칙 추가
- active PR plan 단일성 검사
- 기존 active PR archive 이동과 지정 PR active 전환
- active PR plan에서 `pr_id`, `work_item_id`, `title` 읽기
- 기존 `bootstrap-run` 재사용 기반으로 `runs/latest/<run-id>/` 생성
- run metadata와 artifact에 `pr_plan_path` 연결 정보 기록
- README 및 ops 문서 업데이트
- CLI 테스트 추가 및 `pytest -q` 통과

## Out of Scope
- review 자동 실행
- qa 자동 실행
- docs-sync 자동 실행
- verification 자동 실행
- PR lifecycle 전체
- history 관리
- planner automation
- approval auto-resolution
- multi-run orchestration

## Acceptance Criteria
- active PR가 없으면 `factory create-pr-plan --root <repo> --pr-id <id> ...` 는 `prs/active/<pr-id>.md`를 생성한다.
- active PR가 이미 있으면 `factory create-pr-plan --root <repo> --pr-id <id> ...` 는 `prs/archive/<pr-id>.md`를 생성한다.
- `factory activate-pr --root <repo> --pr-id <id>` 실행 시 기존 active PR는 `prs/archive/`로 이동하고 지정한 PR는 `prs/active/`로 이동한다.
- `activate-pr` 실행 뒤 `prs/active/` 아래에는 정확히 하나의 active PR plan만 남는다.
- `factory start-execution --root <repo> --run-id <id>` 실행 시 active PR plan이 정확히 하나면 `runs/latest/<run-id>/`가 생성된다.
- 생성된 run 쪽에서 최소 `run_id`, `pr_id`, `work_item_id`, `pr_plan_path`를 식별할 수 있다.
- active PR plan이 없으면 명령이 안전하게 실패한다.
- active PR plan이 여러 개면 명령이 안전하게 실패한다.
- `activate-pr` 후 `start-execution`은 새 active PR 기준으로 실행된다.
- 기존 `bootstrap-run` 명령은 제거되지 않고 계속 동작한다.
- `pytest -q`가 통과한다.

## Dependencies
- WI-010 active PR planning
- existing `bootstrap-run` artifact contract
- CLI parser error handling pattern

## Risks
- 사용자가 `start-execution`만으로 review/qa/approval가 자동 진행된다고 오해할 수 있다.
- 사용자가 `activate-pr`를 PR close/merge/history lifecycle로 오해할 수 있다.
- active PR plan 문서 형식이 계약과 다르면 시작 실패가 발생한다.

## Notes
- 이번 PR은 candidate PR plan 생성 규칙과 active PR switching minimum, active PR plan에서 run bootstrap으로 진입하는 최소 연결만 다룬다.
- 사람 승인과 역할별 수동 기록 흐름은 그대로 유지한다.
