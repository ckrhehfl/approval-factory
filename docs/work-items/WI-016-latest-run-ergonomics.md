# WI-016: latest run ergonomics

## input refs

- AGENTS.md (v1, repo local)
- README.md (current)
- docs/ops/runbook.md (current)
- docs/ops/how-we-work.md (current)
- docs/work-items/WI-015-demo-cleanup-matching.md (current)
- orchestrator/cli.py (current)
- orchestrator/pipeline.py (current)
- tests/test_cli.py (current)
- tests/test_pipeline_approval_loop.py (current)

## scope

- run-scoped CLI 명령에 `--latest` selector를 추가해 operator가 latest run을 다시 복사 입력하지 않아도 되게 한다.
- 대상 명령은 `record-review`, `record-qa`, `record-docs-sync`, `record-verification`, `gate-check`, `build-approval`, `resolve-approval` 이다.
- 기존 `--run-id <id>` 계약은 유지하고, `--latest`를 대안 selector로만 추가한다.
- latest run 판정은 `factory status`가 읽는 repo-local 규칙과 동일해야 하며 중복 구현을 피한다.
- latest run 없음, `--run-id`와 `--latest` 동시 사용, prerequisite artifact 부족 같은 operator error path를 더 명확히 한다.
- approval-first, one-PR-at-a-time, repo-local, file-based 운영과 docs/prs history 보호 규칙은 유지한다.
- 구조 변경, breaking change, commit/push, docs/prs history cleanup, non-local resolver 도입은 범위에 넣지 않는다.

## output summary

- latest run convenience 계층 추가로 반복적인 run-id 재입력 감소
- status와 동일한 latest-run resolver로 선택 기준 일관성 확보
- run selector conflict 및 missing latest/prerequisite 오류 메시지 보강
- README와 ops 문서에 사용법과 주의점 동기화

## risks

- latest-run 기준이 status와 어긋나면 operator가 다른 run에 기록할 수 있으므로 공통 helper 재사용이 필요하다.
- convenience 추가가 기본 계약을 흐리면 안 되므로 `--run-id` 경로와 명시적 실패 규칙을 유지해야 한다.
- latest run은 선택만 단순화할 뿐 prerequisite를 완화하지 않으므로 문서와 에러 메시지가 이를 분명히 해야 한다.

## next required gate

- review
