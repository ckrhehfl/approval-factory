# PR-006 Plan

## input refs

- AGENTS.md
- README.md
- docs/ops/runbook.md
- docs/ops/demo-script.md
- docs/ops/how-we-work.md
- orchestrator/cli.py
- orchestrator/pipeline.py
- tests/test_pipeline_approval_loop.py
- approval_queue/*
- runs/latest/*

## scope

- `factory resolve-approval` CLI 명령을 추가한다.
- pending queue item을 승인자 결정에 맞는 최종 queue로 이동한다.
- `approval-decision.yaml` artifact를 생성/갱신한다.
- approve/reject/exception 및 idempotent 재실행 테스트를 추가한다.
- 운영 문서를 현재 동작에 맞게 동기화한다.

## output summary

- 신규 명령: `factory resolve-approval`
- 신규 artifact: `runs/latest/<run-id>/artifacts/approval-decision.yaml`
- queue lifecycle: `pending -> approved|rejected|exceptions`
- idempotent 재실행 및 이미 처리된 상태 검증 테스트 추가

## risks

- 이미 다른 queue에 처리된 run에 대해 상충 결정을 입력하면 운영 충돌이 발생한다.
- 과거 수동 운영 파일이 표준 파일명(`APR-<run-id>.yaml`)을 따르지 않으면 resolve가 실패할 수 있다.

## next required gate

- review
