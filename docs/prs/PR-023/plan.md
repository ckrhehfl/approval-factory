# PR-023 Plan

## input refs
- AGENTS.md v2026-03-30
- docs/work-items/WI-023-approval-readiness-visibility.md
- docs/work-items/WI-020-work-item-readiness-visibility.md
- docs/work-items/WI-021-pr-plan-readiness-visibility.md
- docs/work-items/WI-022-status-readiness-visibility.md

## scope
- `build-approval` visibility 보강
- approval artifact readiness context 확장
- readiness unavailable degraded handling 추가
- 관련 계약/운영 문서 동기화

## output summary
- `runs/latest/<run-id>/artifacts/evidence-bundle.yaml`와 `approval-request.yaml`에 readiness context를 visibility-only로 기록한다.
- summary 값은 기존 helper 규칙 그대로 `no-linked-clarifications|ready|attention-needed`만 사용한다.
- `build-approval` 성공 출력은 readiness summary와 linked clarification count를 짧게 보여준다.

## risks
- readiness가 approval gating처럼 해석되지 않도록 계약/문구를 명시해야 한다.
- source work item artifact가 부실한 bootstrap/rehearsal fixture에서는 unavailable handling이 operator-friendly 해야 한다.

## next required gate
- Reviewer: gate-check/build-approval/resolve-approval semantics 무변경 확인
- QA: readiness 3종, unavailable, queue semantics 회귀 테스트 확인
