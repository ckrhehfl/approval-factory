# PR-009 Plan

## input refs

- AGENTS.md (v1, repo local)
- README.md (current)
- docs/contracts/work-item-contract.md (current)
- docs/ops/runbook.md (current)
- docs/ops/demo-script.md (current)
- docs/ops/how-we-work.md (current)
- orchestrator/cli.py (current)
- orchestrator/pipeline.py (current)
- tests/test_cli.py (current)

## scope

- repo-local, file-based Work Item artifact minimum을 추가한다.
- `factory create-work-item` CLI 명령으로 `docs/work-items/<work-item-id>.md` artifact를 생성한다.
- Work Item artifact의 최소 섹션 계약, 기본 `draft` 상태, duplicate `work-item-id` 안전 실패 규칙을 정의한다.
- Goal to Work Item 자동 분해, clarification 강한 연결, planner 자동화, LLM 연동은 이번 PR 범위에 넣지 않는다.

## output summary

- Work Item용 Markdown artifact 생성 기능 추가
- duplicate `work-item-id` 안전 실패 처리와 optional multiline acceptance criteria 지원 추가
- Goal -> Clarification -> Work Item 흐름을 README 및 ops 문서에 반영
- PR-009/WI-009 문서 초안 추가

## risks

- Work Item artifact가 추가되면서 자동 분해나 planning automation이 이미 있는 것으로 오해될 수 있다.
- clarification linkage를 강제하지 않는 현재 계약은 후속 PR에서 dependency/routing 정책을 더 명확히 해야 할 수 있다.

## next required gate

- review
