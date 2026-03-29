# WI-017: active PR operator UX clarification

## Input Refs
- AGENTS.md vcurrent
- README.md active PR / status / execution flow sections
- docs/ops/runbook.md active PR plan, status, start-execution contracts
- docs/ops/how-we-work.md execution flow summary
- docs/contracts/pr-contract.md
- docs/work-items/WI-011-approval-driven-execution.md
- docs/work-items/WI-012-execution-guardrails.md
- docs/work-items/WI-016-latest-run-ergonomics.md

## Scope
- `factory status` read-only output clarity for active PR, latest run, approval, clarifications
- `create-pr-plan`, `activate-pr`, `start-execution` operator-facing CLI summary hardening
- regression tests for the above
- operator docs examples only

## Problem
continuation pack 기준 다음 혼란이 반복된다.
- active PR가 남아 있어서 다른 실행이 시작된다.
- `create-pr-plan`과 `activate-pr` semantics가 섞여 보인다.
- `start-execution` guardrail 실패가 버그처럼 보인다.

## Output Summary
- semantics 변경 없이 active PR / archive / execution 흐름을 더 직접적으로 보여주는 CLI summary 추가
- status에 artifact path 중심 가시성 추가
- guardrail 실패 시 다음 action 예시 추가

## Risks
- 출력 문자열이 길어지면 기존 operator 습관을 해칠 수 있다.
- semantics처럼 읽히는 문구가 들어가면 contract drift가 생길 수 있다.

## Next Required Gate
- Implementer: CLI/tests/docs sync
- Reviewer: semantics non-change 확인
- QA: 문자열 회귀와 전체 테스트 통과 확인
