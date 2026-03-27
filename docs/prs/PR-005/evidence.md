# PR-005 Evidence

## input refs

- orchestrator/cli.py (current)
- orchestrator/pipeline.py (current)
- config/gates.yaml (current)
- tests/test_pipeline_approval_loop.py (current)
- tests/test_cli.py (current)
- docs/ops/runbook.md (current)
- docs/ops/demo-script.md (current)
- README.md (current)

## scope

- 문서 진술이 코드/테스트로 검증 가능한 사실인지 기록한다.

## output summary

- `factory` 지원 명령은 `bootstrap-run`, `record-review`, `record-qa`, `record-docs-sync`, `record-verification`, `gate-check`, `build-approval`이다.
- `gate-check`는 `gate-status.yaml` 판정만 갱신한다. `evidence_bundle_complete`는 기존 `evidence-bundle.yaml` 상태를 사용한다.
- `build-approval`는 `build_evidence_bundle` 호출 후 `evaluate_gates`를 재실행하고 `approval-request.yaml`/`evidence-bundle.yaml`을 최신화한다.
- queue 자동 적재는 `docs_sync in {complete, not-needed}` 그리고 `merge_approval in {ready, exception_required}`일 때 `approval_queue/pending/APR-<run-id>.yaml`로 수행된다.
- `pending` 이후 승인/반려/예외 확정의 파일 이동은 현재 MVP에서 수동 운영이다.

## risks

- 운영자가 `gate-check` 결과만 보고 최종 승인 준비 완료로 오판할 수 있다.
- pending 큐 처리 표준이 약하면 팀별 수동 운영 편차가 커질 수 있다.

## next required gate

- decision
