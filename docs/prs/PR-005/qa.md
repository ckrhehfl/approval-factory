# PR-005 QA

## input refs

- tests/test_cli.py (current)
- tests/test_pipeline_approval_loop.py (current)
- orchestrator/cli.py (current)
- orchestrator/pipeline.py (current)
- docs/ops/demo-script.md (current)

## scope

- 문서 정합성 변경이 테스트 기대 동작과 충돌하지 않는지 확인한다.
- gate-check/build-approval 설명이 테스트 시나리오와 일치하는지 확인한다.

## output summary

- `test_pipeline_approval_loop.py` 기준으로 queue 적재는 `pending` 디렉터리만 자동 처리됨을 확인했다.
- 동일 approval 재실행 시 idempotent, 충돌 시 `--rN` suffix 동작이 테스트로 확인된다.
- 문서는 위 동작을 과장 없이 반영하도록 수정했다.

## risks

- 수동 승인 처리(approved/rejected/exceptions 이동)는 테스트 범위 밖이며 운영 실수 가능성이 있다.

## next required gate

- docs-sync
