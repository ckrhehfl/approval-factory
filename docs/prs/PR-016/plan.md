# PR-016 Plan

## input refs

- AGENTS.md (v1, repo local)
- README.md (current)
- docs/ops/runbook.md (current)
- docs/ops/how-we-work.md (current)
- docs/work-items/WI-016-latest-run-ergonomics.md (current)
- orchestrator/cli.py (current)
- orchestrator/pipeline.py (current)
- tests/test_cli.py (current)
- tests/test_pipeline_approval_loop.py (current)

## scope

- run-scoped CLI 명령에 `--latest`를 추가해 `--run-id <id>`의 대안 selector를 제공한다.
- 기존 `--run-id` 사용 방식과 artifact 계약은 유지하고, 둘을 동시에 쓰면 명확히 실패하게 한다.
- latest run 선택 기준은 `factory status`와 같은 repo-local 규칙으로 공통 helper에서 해석한다.
- latest run 없음, selector conflict, prerequisite artifact 부족 시 operator가 다음 액션을 바로 알 수 있게 오류 메시지를 보강한다.
- CLI 테스트와 approval loop 회귀를 유지하면서 latest selector 관련 테스트를 추가한다.
- README와 ops 문서에 `--latest` 사용법, 주의점, 예시를 반영한다.
- 구조 리팩터링, remote state, multi-run orchestration, commit/push는 포함하지 않는다.

## output summary

- baseline normalization 다음 단계로 latest-run convenience를 최소 변경으로 추가
- status와 run-scoped 명령 사이의 latest-run 해석 일관성 확보
- operator UX 단순화와 계약 보존을 동시에 충족하는 selector 정리
- 테스트와 문서로 convenience 계층의 안전한 사용 경로 고정

## risks

- CLI에서 latest-run 해석이 중복되면 이후 status와 drift가 생길 수 있으므로 shared helper가 필요하다.
- `--latest`가 암묵적 기본값처럼 보이면 잘못된 run에 기록할 수 있으므로 selector는 계속 명시적으로 요구해야 한다.
- prerequisite error가 모호하면 operator가 latest run 자체를 의심하게 되므로 다음 단계 안내가 중요하다.

## next required gate

- review
