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
7. Orchestrator가 evidence bundle 생성
8. Approver가 승인/반려
9. Docs Sync가 문서 최종 정리
10. Merge

## 4. 확장 경계

MVP에서 다음은 명확히 분리해야 한다.

- 역할 인터페이스
- 템플릿 인터페이스
- 상태 저장 인터페이스
- 승인 인터페이스
- evidence 인터페이스

이 경계가 유지되면 이후 중앙 control plane으로 승격 가능하다.

## 5. 레포 우선 구조

현재는 repo-local 구조를 사용한다.
이는 다음 이유에서다.

- 구현이 빠르다.
- 상태가 Git에 남는다.
- 사람이 읽기 쉽다.
- UI 없는 MVP에 적합하다.

추후 플랫폼화 시에는 approval queue와 run state를 별도 서비스로 이동한다.
