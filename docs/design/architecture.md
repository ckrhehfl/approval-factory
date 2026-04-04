# Architecture

## 1. 구성 요소

### 1) Orchestrator
역할 호출, 상태 전이, artifact 수집, gate 판정을 담당한다.

### 2) Agents
역할별 실행 단위다.
- Architect
- Planner
- Implementer
- Reviewer
- QA
- Docs Sync

### 3) Templates
산출물 형식을 고정한다.
- Work Item
- PR Plan
- Approval Request
- Evidence Bundle
- ADR

### 4) Config
역할, 게이트, 프로젝트 정책을 분리한다.

### 5) Docs
설계/정책/계약/운영 기준을 담는다.

## 2. 상태 모델

- draft
- planned
- in_progress
- review
- qa
- docs_sync
- approval_pending
- approved
- merged
- rejected

## 3. 데이터 흐름

1. PM이 Work Item 등록
2. Architect가 설계/ADR 초안 생성
3. Planner가 PR 분해
4. Implementer가 코드/테스트 작성
5. Reviewer가 리스크와 설계 정합성 검토
6. QA가 기능/회귀 검증
7. Docs Sync가 문서 최종 정리
8. Orchestrator가 evidence bundle 생성
9. Approver가 승인/반려
10. Merge

## 4. canonical naming

### docs roles

- `docs/work-items/`는 Goal/clarification을 official work item artifact로 고정하는 canonical planning surface다.
- `docs/prs/`는 PR별 history/audit trail을 남기는 canonical documentation surface다.
- active execution에 사용되는 official PR plan artifact는 `prs/active/`와 `prs/archive/`에 있다.
- 따라서 `docs/prs/`는 runtime source of truth가 아니며, history coverage 차이만으로 runtime semantics를 판정하지 않는다.
- 앞으로 새 PR은 merge 전 최소 `docs/prs/PR-###/plan.md`를 남긴다.

### canonical paths

사람용 문서 경로:

- `docs/work-items/WI-###-<slug>.md`
- `docs/prs/PR-###/scope.md` (recommended history-doc shape)
- `docs/prs/PR-###/plan.md` (recommended history-doc shape)
- `docs/prs/PR-###/review.md` (recommended history-doc shape)
- `docs/prs/PR-###/qa.md` (recommended history-doc shape)
- `docs/prs/PR-###/docs-sync.md` (recommended history-doc shape)
- `docs/prs/PR-###/evidence.md` (recommended history-doc shape)
- `docs/prs/PR-###/decision.md` (recommended history-doc shape)
- `prs/active/<pr-id>.md` (official active PR plan artifact)
- `prs/archive/<pr-id>.md` (official archived PR plan artifact)

approval queue hygiene visibility boundary:

- `factory status`와 `factory inspect-approval-queue`의 stale/latest 및 Relation Summary는 operator visibility only다.
- `factory hygiene-approval-queue`는 exact selector family(`--run-id` 또는 `--approval-id`)와 exact mode family(`--dry-run` 또는 `--apply`)만 사용한다.
- hygiene apply는 exact pending queue target artifact 하나에 대한 target-local mutation만 허용한다.
- 이 visibility는 cleanup selector, auto-resolve trigger, broad queue mutation semantics로 승격되지 않는다.

forward minimum:

- 7-file shape는 recommended history-doc shape다.
- 새 PR의 forward minimum history-doc requirement는 `docs/prs/PR-###/plan.md` 1개다.

기계용 artifact 경로:

- `runs/latest/<run_id>/run.yaml`
- `runs/latest/<run_id>/artifacts/work-item.yaml`
- `runs/latest/<run_id>/artifacts/pr-plan.yaml`
- `runs/latest/<run_id>/artifacts/review-report.yaml`
- `runs/latest/<run_id>/artifacts/qa-report.yaml`
- `runs/latest/<run_id>/artifacts/docs-sync-report.yaml`
- `runs/latest/<run_id>/artifacts/evidence-bundle.yaml`
- `runs/latest/<run_id>/artifacts/approval-request.yaml`
- `runs/latest/<run_id>/artifacts/gate-status.yaml`

### history alignment policy

- 현재 저장소의 `docs/prs/`는 mixed legacy formats를 가진다.
- git history에는 PR-040~049 merge commit이 존재하지만, 현재 저장소에는 해당 per-PR history docs가 없다.
- PR-040~049 retro docs policy는 `README/architecture alignment only`다.
- 즉, architecture와 README는 실제 repo/history에 맞게 정렬하되, 확인 가능한 근거 없이 PR-040~049용 retro history docs를 새로 만들지 않는다.
- PR-060은 PR-053~059 history-doc backfill을 같은 PR 안에서 처리하지 않는다.

## 5. 확장 경계

MVP에서 다음은 명확히 분리해야 한다.

- 역할 인터페이스
- 템플릿 인터페이스
- 상태 저장 인터페이스
- 승인 인터페이스
- evidence 인터페이스

이 경계가 유지되면 이후 중앙 control plane으로 승격 가능하다.

## 6. 레포 우선 구조

현재는 repo-local 구조를 사용한다.
이는 다음 이유에서다.

- 구현이 빠르다.
- 상태가 Git에 남는다.
- 사람이 읽기 쉽다.
- UI 없는 MVP에 적합하다.

추후 플랫폼화 시에는 approval queue와 run state를 별도 서비스로 이동한다.
