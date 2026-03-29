# PR-017 Plan

## Input Refs
- AGENTS.md vcurrent
- README.md
- docs/ops/runbook.md
- docs/ops/how-we-work.md
- docs/contracts/pr-contract.md
- docs/work-items/WI-017-active-pr-operator-ux.md

## Scope
- operator UX simplification only
- no lifecycle semantics change
- no auto activate/create/repair
- no commit/push/release work

## Output Summary
- `factory status`에 path 중심 상태 요약 보강
- `create-pr-plan` 생성 위치와 next action summary 보강
- `activate-pr` 전환 결과 summary 보강
- `start-execution` guardrail을 operator action 중심으로 보강
- 관련 회귀 테스트 및 운영 문서 보강

## Plan
1. existing flow와 테스트 문자열 계약 확인
2. shared read-only status metadata와 CLI formatter 추가
3. guardrail 메시지를 repo 상태와 next command 기준으로 보강
4. 회귀 테스트를 핵심 문구 기준으로 고정
5. README/runbook/how-we-work에 해석 예시 추가

## Risks
- UX 보강이 semantics change처럼 오해될 수 있다.
- status path 노출이 stale artifact 선택처럼 보이지 않도록 latest/active 기준을 유지해야 한다.

## Next Required Gate
- Reviewer approval for semantics preservation
- QA verification on full test suite
