# PR-034 Plan

## input refs
- AGENTS.md v2026-04-02
- README.md
- docs/ops/runbook.md
- docs/ops/how-we-work.md
- docs/work-items/WI-034-goal-clarification-draft.md

## scope
- `factory draft-clarifications` 명령 추가
- goal markdown 기반 deterministic rule-based clarification draft artifact 생성
- `clarification_drafts/<goal-id>.md` repo-local output 고정
- goal missing, duplicate draft safe failure 처리
- official clarification queue, readiness, approval, selector, lifecycle semantics 무변경 유지
- tests/docs/contracts 동기화

## output summary
- operator가 Goal artifact만으로 clarification 초안을 한 번에 생성할 수 있다.
- draft는 local aid이고 official queue artifact는 계속 수동으로만 생성된다.
- 기존 clarification queue와 approval lifecycle semantics는 그대로 유지된다.

## risks
- draft wording이 official queue 후보처럼 보여 auto-promotion 기대를 만들 수 있다.
- rule-based heuristic이 부족하면 초안 품질보다 semantics 보호가 더 중요하므로 wording을 보수적으로 유지해야 한다.

## next required gate
- Reviewer: artifact-only 범위와 no-semantics-change 확인
- QA: safe failure, no queue side effect, deterministic output 확인
- Docs Sync: README/runbook/how-we-work/contract wording 일치 확인
