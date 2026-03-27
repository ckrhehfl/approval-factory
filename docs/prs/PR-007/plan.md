# PR-007 Plan

## input refs

- AGENTS.md (v1, repo local)
- README.md (current)
- docs/ops/runbook.md (current)
- docs/ops/demo-script.md (current)
- docs/ops/how-we-work.md (current)
- orchestrator/cli.py (current)
- orchestrator/pipeline.py (current)
- tests/test_cli.py (current)

## scope

- repo-local, file-based 최소 Goal intake contract를 추가한다.
- `factory create-goal` CLI 명령으로 `goals/<goal-id>.md` artifact를 생성한다.
- Goal artifact의 최소 섹션 계약과 duplicate `goal-id` 처리 규칙을 문서화한다.
- planner/resolver, auto-questions, goal-to-WI 분해, LLM 연동은 이번 PR 범위에 넣지 않는다.

## output summary

- Goal intake용 Markdown artifact 생성 기능 추가
- duplicate `goal-id` 안전 실패 처리 추가
- Goal intake minimum 범위를 README 및 ops 문서에 반영
- PR-007/WI-007 문서 초안 추가

## risks

- Goal artifact를 생성했다고 바로 Work Item/PR 분해가 자동화된 것으로 오해될 수 있다.
- Markdown contract가 너무 느슨하면 후속 PR에서 구조 해석이 어려워질 수 있다.

## next required gate

- review
