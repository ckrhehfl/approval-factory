# WI-015: demo cleanup matching normalization

## input refs

- AGENTS.md (v1, repo local)
- README.md (current)
- docs/ops/runbook.md (current)
- docs/ops/how-we-work.md (current)
- docs/work-items/WI-014-rehearsal-cleanup-baseline.md (current)
- docs/prs/PR-014/plan.md (current)
- orchestrator/pipeline.py (current)
- tests/test_cli.py (current)

## scope

- PR-014에서 도입한 `factory cleanup-rehearsal --include-demo`의 demo 매칭을 suffix/infix naming variant까지 보강한다.
- `runs/latest/RUN-DEMO-*`와 함께 `runs/latest/RUN-*-DEMO*`도 cleanup 대상에 포함한다.
- `APR-RUN-DEMO-*`와 함께 `APR-RUN-*-DEMO*` queue item도 pending, approved, rejected, exceptions 경로에서 cleanup 대상에 포함한다.
- docs/prs 이력 문서, README, docs/contracts, docs/adr, 코드, 테스트는 cleanup 대상이 아님을 유지한다.
- `factory status`가 stale demo latest run 또는 demo-only open clarification을 남기지 않도록 회귀 테스트를 추가한다.
- ergonomics 변경, 출력 포맷 변경, breaking change, 전체 reset은 범위에 넣지 않는다.

## output summary

- baseline normalization 완결을 위해 demo naming variant cleanup 누락 보강
- 경로 및 파일명 규칙 기반의 보수적 매칭 유지
- suffix demo run/queue cleanup과 status 정합성을 테스트로 고정
- 다음 ergonomics PR 전에 운영 baseline을 깨끗하게 맞추는 작은 보강 PR 준비

## risks

- `DEMO` 문자열이 우연히 포함된 실제 이력을 과하게 지우지 않도록 run/queue는 명시적 naming pattern으로 제한해야 한다.
- cleanup 매칭 확대 후에도 docs/prs history와 non-demo 실제 이력이 보존되는지 테스트로 유지해야 한다.
- latest run 선정은 timestamp 기반이므로 stale demo run 제거 뒤 status가 의도한 non-demo run으로 정상 복귀해야 한다.

## next required gate

- review
