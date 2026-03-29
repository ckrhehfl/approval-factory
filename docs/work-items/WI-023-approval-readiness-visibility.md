# WI-023: approval readiness visibility minimum

## input refs
- AGENTS.md v2026-03-30
- docs/work-items/WI-020-work-item-readiness-visibility.md
- docs/work-items/WI-021-pr-plan-readiness-visibility.md
- docs/work-items/WI-022-status-readiness-visibility.md

## scope
- `build-approval`가 approval artifact 생성 시 source PR/work item readiness context를 visibility-only로 함께 기록
- `evidence-bundle.yaml`, `approval-request.yaml`에 readiness context 최소 필드 추가
- 기존 gate/approval/queue semantics는 유지

## output summary
- approver/operator가 approval artifact를 열 때 evidence와 함께 source readiness summary를 같이 볼 수 있다.
- readiness summary 규칙은 기존 `no-linked-clarifications|ready|attention-needed`만 재사용한다.
- readiness source artifact를 읽지 못하면 approval package 전체 대신 readiness context만 제한적으로 unavailable 처리한다.

## risks
- readiness가 blocking signal처럼 오해되면 scope가 커질 수 있으므로 wording을 visibility-only로 고정해야 한다.
- 기존 prerequisite, queue 적재, resolve 흐름과 엮이면 breaking change가 되므로 계산식 재사용 범위를 제한해야 한다.

## next required gate
- Reviewer: readiness visibility가 gate/queue semantics에 연결되지 않았는지 검토
- QA: readiness variants와 unavailable handling, 기존 approval loop 회귀 확인
