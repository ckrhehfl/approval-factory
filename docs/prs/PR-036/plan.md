# PR-036 Plan

## input refs
- AGENTS.md v2026-04-02
- README.md
- docs/ops/runbook.md
- docs/ops/how-we-work.md
- docs/contracts/work-item-draft-contract.md
- docs/work-items/WI-036-draft-work-items.md

## scope
- `factory draft-work-items` 명령 추가
- goal markdown + official clarification markdown 기반 deterministic work item draft artifact 생성
- `work_item_drafts/<goal-id>.md` repo-local output 고정
- goal missing, duplicate draft safe failure 처리
- official clarification zero-candidate case 지원
- `clarification_drafts/` non-input 보장
- `docs/work-items/` 비생성 보장
- tests/docs/contracts 동기화

## output summary
- operator가 official clarification artifact를 source of truth로 삼아 work item candidate draft를 생성할 수 있다.
- draft는 local aid이고 official work item artifact는 계속 수동으로만 생성된다.
- 기존 readiness, approval, queue, selector, active PR, lifecycle semantics는 그대로 유지된다.

## risks
- draft wording이 official work item 생성처럼 읽히면 artifact-only 범위가 흐려질 수 있다.
- clarification draft를 잘못 입력으로 읽으면 source-of-truth 계약이 깨질 수 있다.

## next required gate
- Reviewer: artifact-only 범위와 no-semantics-change 확인
- QA: safe failure, zero-candidate, non-input enforcement 확인
- Docs Sync: README/runbook/how-we-work/contract wording 일치 확인
