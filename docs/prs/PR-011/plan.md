# PR-011 Plan

## input refs

- AGENTS.md (v1, repo local)
- README.md (current)
- docs/contracts/pr-contract.md (current)
- docs/ops/runbook.md (current)
- docs/ops/demo-script.md (current)
- docs/ops/how-we-work.md (current)
- docs/prs/PR-010/plan.md (current)
- docs/work-items/WI-010-pr-planning.md (current)
- orchestrator/cli.py (current)
- orchestrator/pipeline.py (current)
- tests/test_cli.py (current)

## scope

- `factory start-execution` CLI 명령을 추가한다.
- `factory activate-pr` CLI 명령을 추가한다.
- `factory create-pr-plan`은 active PR가 없으면 active에, 있으면 archive 후보로 생성하도록 보강한다.
- `prs/active/` 아래 정확히 하나의 active PR plan이 있을 때만 run bootstrap을 시작한다.
- active PR plan에서 `pr_id`, `work_item_id`, `title`을 읽어 기존 `bootstrap-run` 흐름에 연결한다.
- 기존 active PR를 `prs/archive/`로 이동시키고 지정한 PR를 active로 전환하는 최소 file-based switching을 추가한다.
- run metadata와 artifact에 최소 `run_id`, `pr_id`, `work_item_id`, `pr_plan_path`를 남긴다.
- active PR plan이 0개이거나 2개 이상이면 안전하게 실패시킨다.
- review/qa/docs-sync/verification 자동 실행, multi-run orchestration, planner automation은 이번 PR 범위에 넣지 않는다.

## output summary

- candidate PR plan 생성과 active PR switching minimum, run entrypoint를 함께 제공하는 PR-011 execution flow 보강
- 기존 `bootstrap-run` 재사용 기반의 file-based orchestration 연결
- switching 및 실행 기준 검증용 CLI 테스트 추가
- README 및 ops 문서에 active PR -> run 연결 흐름 반영

## risks

- 사용자가 `start-execution`을 전체 pipeline 자동 실행으로 오해할 수 있다.
- 사용자가 `activate-pr`를 lifecycle 전체로 오해할 수 있으므로 archive 이동만 제공한다는 계약을 문서에 유지해야 한다.
- active PR plan Markdown 섹션 계약이 깨지면 시작 단계에서 실패하므로 문서 계약 유지가 중요하다.

## next required gate

- review
