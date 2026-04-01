# PR-033 Plan

## input refs
- AGENTS.md v2026-04-02
- docs/contracts/status-contract.md
- docs/ops/runbook.md

## scope
- stale pending approval operator semantics 문서화
- latest pending을 current approval target으로 명시
- stale pending visibility 유지 규칙 명시
- readiness, selector, CLI behavior 무변경 계약 고정

## output summary
- `status` 계약에 latest pending, stale pending visibility, no auto cleanup semantics를 짧게 추가한다.
- runbook에 operator-facing approval 해석 규칙을 짧게 반영한다.
- queue lifecycle, selector logic, readiness semantics, CLI behavior는 그대로 유지한다고 명시한다.

## risks
- stale pending visibility가 queue cleanup 필요 신호인지 current target 변경 신호인지 혼동될 수 있다.
- status path 출력이 selector처럼 읽히면 잘못된 운영 판단으로 이어질 수 있다.

## next required gate
- Reviewer: pending/stale semantics가 docs-only이고 기존 approval behavior를 바꾸지 않는지 확인
- Docs Sync: status contract와 runbook wording 일치 확인
