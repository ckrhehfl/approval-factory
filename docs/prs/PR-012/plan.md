# PR-012 Plan

## input refs

- AGENTS.md (v1, repo local)
- README.md (current)
- docs/ops/runbook.md (current)
- docs/ops/demo-script.md (current)
- docs/ops/how-we-work.md (current)
- docs/work-items/WI-011-approval-driven-execution.md (current)
- orchestrator/cli.py (current)
- orchestrator/pipeline.py (current)
- tests/test_cli.py (current)
- tests/test_pipeline_approval_loop.py (current)

## scope

- `start-execution`이 active PR plan의 `work_item_id`를 실제 `docs/work-items/` artifact와 연결 가능한지 검증한다.
- `build-approval` 전에 `review/qa/docs-sync/verification` artifact가 실제 record 명령으로 기록됐는지 검증한다.
- `resolve-approval` 전에 populated `approval-request.yaml`와 pending queue item 존재를 검증한다.
- `run.yaml.state`를 `draft -> in_progress -> approval_pending -> approved|rejected` 흐름으로 더 명확히 갱신한다.
- 기존 CLI 이름, artifact 이름, repo-local/file-based 흐름은 유지한다.
- planner automation, multi-agent orchestration, review/qa/docs-sync/verification 자동 실행, 대규모 state machine은 추가하지 않는다.

## output summary

- 잘못된 실행 순서를 더 일찍 차단하는 최소 execution guardrail 추가
- active PR, work item, approval artifact 사이의 연결성 강화
- 현재 run state 의미를 운영 문서와 테스트에 맞춰 명확화
- 실패 원인을 바로 알 수 있는 테스트 및 문서 보강

## risks

- placeholder artifact와 recorded artifact를 구분하면서 기존 재실행 패턴이 흔들리지 않도록 주의가 필요하다.
- work item 연결 검증이 너무 엄격하면 기존 수동 문서 운영과 충돌할 수 있으므로 unique match 규칙을 유지해야 한다.
- 상태 수를 줄이는 대신 의미를 더 분명히 해야 하므로 문서 동기화가 중요하다.

## next required gate

- review
