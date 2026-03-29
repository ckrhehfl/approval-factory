# PR-019 Plan

## Input Refs
- AGENTS.md vcurrent
- README.md
- docs/ops/runbook.md
- docs/ops/how-we-work.md
- docs/contracts/work-item-contract.md
- docs/work-items/WI-018-clarification-resolution-minimum.md
- docs/work-items/WI-019-work-item-clarification-linkage.md

## Scope
- `create-work-item` 입력에 반복 가능한 `--clarification-id` 추가
- work item artifact에 clarification linkage와 status 가시성 추가
- 같은 goal linkage validation과 안전 실패 메시지 추가
- 테스트 및 운영 문서 보강
- commit/push/release, goal/work-item/pr/run/approval semantics 확장, 자동 planning/resolution 제외

## Output Summary
- work item이 관련 clarification 목록을 최소 계약으로 공식 기록
- clarification이 없거나 다른 goal 아래 있으면 짧고 설명적인 에러로 실패
- 기존 no-linkage 경로와 수동 운영 흐름은 그대로 유지

## Plan
1. `create-work-item` parser와 pipeline에 optional clarification linkage 입력/검증 추가
2. work item markdown 섹션에 related clarification 목록과 status 렌더링 추가
3. no-linkage, single/multi linkage, missing/cross-goal failure 회귀 테스트 추가
4. README/runbook/how-we-work/work-item contract에 사용법과 범위 제한 반영
5. 전체 테스트로 breaking change가 없는지 확인

## Risks
- unresolved clarification status를 보여주는 것과 생성 허용 여부를 혼동하면 운영자가 자동 gate로 오해할 수 있다.
- duplicate 입력 처리 방식이 기존 CLI 기대와 어긋나면 operator 경험이 흔들릴 수 있으므로 dedupe를 조용히 적용하되 artifact에는 한 번만 기록한다.

## Next Required Gate
- Reviewer approval for linkage-hardening-only semantics
- QA verification on full test suite
