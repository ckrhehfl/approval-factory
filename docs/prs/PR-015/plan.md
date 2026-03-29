# PR-015 Plan

## input refs

- AGENTS.md (v1, repo local)
- README.md (current)
- docs/ops/runbook.md (current)
- docs/ops/how-we-work.md (current)
- docs/work-items/WI-015-demo-cleanup-matching.md (current)
- docs/prs/PR-014/plan.md (current)
- orchestrator/pipeline.py (current)
- tests/test_cli.py (current)

## scope

- `factory cleanup-rehearsal --include-demo`가 `RUN-DEMO-*`뿐 아니라 `RUN-*-DEMO*` demo run naming variant도 cleanup 하도록 보강한다.
- 관련 approval queue item도 `APR-RUN-DEMO-*`와 `APR-RUN-*-DEMO*`를 pending, approved, rejected, exceptions 경로에서 함께 cleanup 하도록 보강한다.
- goal, clarification, work-item, active/archive PR demo cleanup의 기존 경로 기반 보호 규칙은 유지하고 필요 이상으로 확장하지 않는다.
- demo cleanup apply 이후 `factory status`에 stale demo latest run 또는 demo-only open clarification이 남지 않도록 테스트를 추가한다.
- README와 ops 문서에 demo naming variants도 cleanup 대상이라는 계약을 반영한다.
- breaking change, ergonomics 변경, docs/prs history cleanup, commit/push는 포함하지 않는다.

## output summary

- PR-014 cleanup baseline의 demo naming variant 누락 보강
- suffix demo run과 queue item cleanup을 최소 수정으로 반영
- stale status 출력 회귀와 보호 규칙을 테스트 및 문서로 고정
- 다음 ergonomics PR 전에 baseline normalization 기준점 정리

## risks

- run/queue 매칭이 너무 넓어지면 실제 이력을 지울 수 있으므로 `RUN` 및 `APR-RUN` 경로 패턴만 확장해야 한다.
- status 회귀 테스트가 없으면 이후 cleanup 변경에서 stale demo latest run이 다시 노출될 수 있다.
- 문서 계약과 코드 매칭이 어긋나면 approval-first 운영 기준이 흔들릴 수 있다.

## next required gate

- review
