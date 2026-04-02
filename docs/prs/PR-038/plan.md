# PR-038 Plan

## input refs
- AGENTS.md v2026-04-02
- README.md
- docs/ops/runbook.md
- docs/ops/how-we-work.md
- docs/contracts/pr-plan-draft-contract.md
- docs/work-items/WI-038-draft-pr-plan.md

## scope
- `factory draft-pr-plan` 명령 추가
- official work item markdown 기반 deterministic PR plan draft artifact 생성
- `pr_plan_drafts/<work-item-id>.md` repo-local output 고정
- work item missing, duplicate draft safe failure 처리
- `work_item_drafts/` non-input 보장
- `prs/active/`, `prs/archive/` 비생성 보장
- tests/docs/contracts 동기화

## output summary
- operator가 official work item artifact를 source of truth로 삼아 PR plan draft를 생성할 수 있다.
- draft는 local aid이고 official PR plan artifact는 계속 수동으로만 생성된다.
- 기존 readiness, approval, queue, selector, active PR, lifecycle semantics는 그대로 유지된다.

## risks
- draft wording이 official PR plan 생성처럼 읽히면 artifact-only 범위가 흐려질 수 있다.
- work item draft를 잘못 입력으로 읽으면 source-of-truth 계약이 깨질 수 있다.

## next required gate
- Reviewer: artifact-only 범위와 no-semantics-change 확인
- QA: safe failure, non-input enforcement, no active/archive mutation 확인
- Docs Sync: README/runbook/how-we-work/contract wording 일치 확인
