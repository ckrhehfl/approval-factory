# PR-008 Plan

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

- repo-local, file-based clarification queue minimum을 추가한다.
- `factory create-clarification` CLI 명령으로 `clarifications/<goal-id>/<clarification-id>.md` artifact를 생성한다.
- clarification artifact의 최소 섹션 계약과 category 검증, duplicate `clarification-id` 처리 규칙을 문서화한다.
- clarification resolver/planner 구현, 자동 질문 생성, 자동 해결, goal-to-WI 자동 분해, LLM 연동은 이번 PR 범위에 넣지 않는다.

## output summary

- clarification queue용 Markdown artifact 생성 기능 추가
- category 검증과 duplicate `clarification-id` 안전 실패 처리 추가
- Goal intake 다음 단계의 최소 질문 관리 계층을 README 및 ops 문서에 반영
- PR-008/WI-008 문서 초안 추가

## risks

- clarification queue 도입만으로 resolver나 escalation 자동화가 이미 있는 것으로 오해될 수 있다.
- Goal artifact 존재 여부를 강제하지 않는 현재 계약은 후속 PR에서 연결성 강화 논의가 필요할 수 있다.

## next required gate

- review
