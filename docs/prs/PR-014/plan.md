# PR-014 Plan

## input refs

- AGENTS.md (v1, repo local)
- README.md (current)
- docs/ops/runbook.md (current)
- docs/ops/how-we-work.md (current)
- docs/work-items/WI-014-rehearsal-cleanup-baseline.md (current)
- orchestrator/cli.py (current)
- orchestrator/pipeline.py (current)
- tests/test_cli.py (current)

## scope

- `factory cleanup-rehearsal` CLI를 추가해 rehearsal artifact cleanup을 dry-run 기본으로 제공한다.
- `--apply`가 있을 때만 실제 삭제하고, `--include-demo`가 있을 때만 legacy demo artifact cleanup을 포함한다.
- cleanup 범위는 repo-local 운영 경로의 `RH` 및 optional `DEMO` artifact로 제한하고 `docs/prs/` 이력 문서는 제외한다.
- `factory status`가 cleanup 이후 stale rehearsal/demo active PR 또는 open clarification을 보여주지 않도록 테스트로 고정한다.
- README 및 ops 문서에 partial cleanup 계약과 예시를 반영한다.
- breaking change, 전체 reset, non-rehearsal 실제 이력 삭제는 포함하지 않는다.

## output summary

- baseline normalization용 최소 cleanup 명령 추가
- rehearsal/demo 흔적만 선택적으로 제거하는 보호 규칙 문서화
- status stale 항목 정리와 demo 보존/삭제 분기 테스트 추가
- 다음 기능 PR 전 repo-local 운영 baseline을 안전하게 정리할 수 있는 최소 운영 정상화 반영

## risks

- cleanup 대상 glob이 실제 이력과 겹치지 않도록 prefix 규칙을 엄격히 유지해야 한다.
- docs/prs history와 코드/계약 문서를 건드리지 않는 보호 규칙이 문서와 테스트 양쪽에 반영돼야 한다.
- apply 이후 active PR/open clarification가 비는 시나리오에서 status 출력이 자연스럽게 `none`으로 정리돼야 한다.

## next required gate

- review
