# PR-010 Plan

## input refs

- AGENTS.md (v1, repo local)
- README.md (current)
- docs/contracts/pr-contract.md (current)
- docs/ops/runbook.md (current)
- docs/ops/demo-script.md (current)
- docs/ops/how-we-work.md (current)
- orchestrator/cli.py (current)
- orchestrator/pipeline.py (current)
- tests/test_cli.py (current)

## scope

- repo-local, file-based single active PR plan minimum을 추가한다.
- `factory create-pr-plan` CLI 명령으로 `prs/active/<pr-id>.md` artifact를 생성한다.
- `prs/active/`에 active PR이 이미 있으면 생성 실패시키고, duplicate `pr-id`도 안전 실패 처리한다.
- active PR plan 최소 섹션 계약과 기본 `planned` 상태를 정의한다.
- archive 이동, PR lifecycle, multi-PR 관리, planner automation, LLM 연동은 이번 PR 범위에 넣지 않는다.

## output summary

- single active PR plan용 Markdown artifact 생성 기능 추가
- one-PR-at-a-time 규칙을 `prs/active/` 단일 파일 계약으로 강제
- README 및 ops/contracts 문서에 Goal -> Clarification -> Work Item -> PR Plan 흐름 반영
- PR-010/WI-010 문서 초안 추가

## risks

- active PR plan 도입만으로 PR lifecycle이나 archive 기능이 이미 있는 것으로 오해될 수 있다.
- 현재 계약은 `prs/active/` 단일성만 보장하므로 완료 후 정리 절차는 후속 PR에서 명시해야 한다.

## next required gate

- review
