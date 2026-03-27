# PR-005 Scope

## input refs

- AGENTS.md (v1, repo local)
- docs/prs/README.md (current)
- docs/work-items/WI-005-mvp-finish.md (current)
- README.md (current)
- docs/ops/runbook.md (current)
- docs/ops/demo-script.md (current)
- docs/ops/how-we-work.md (current)
- orchestrator/cli.py (current)
- orchestrator/pipeline.py (current)
- config/gates.yaml (current)

## scope

- PR-005의 목적은 기능 추가가 아니라 문서 계약 정리와 운영 정합성 마감이다.
- `docs/prs/README.md` 계약(필수 7문서)을 PR-005 폴더에 충족시킨다.
- gate-check와 build-approval의 역할 차이, queue 운영, pending 이후 수동 운영 절차를 명시한다.

## output summary

- PR-005 필수 문서(`scope/review/qa/docs-sync/evidence/decision`)를 현재 상태 기준으로 작성한다.
- WI-005 상태/범위를 실제 저장소 기준으로 갱신한다.
- README 및 ops 문서를 코드 동작과 일치하도록 정정한다.

## risks

- queue의 `pending` 이후 자동 상태 전환 기능이 없는데 자동으로 오해될 수 있다.
- gate-check 단독 결과를 최종 승인 가능 상태로 오해할 수 있다.

## next required gate

- review
