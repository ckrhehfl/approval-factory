# 승인자 중심 멀티 에이전트 개발 오케스트레이션 MVP 설계

## 1. 시스템 정의

이 시스템은 승인자/PM이 구현 세부에 직접 들어가지 않고도, AI 에이전트들이 설계·계획·구현·리뷰·QA·문서 동기화를 수행하도록 오케스트레이션하는 개발 공장이다.

핵심 단위는 대화가 아니라 다음 상태 전이 체인이다.

`Work Item -> Design -> PR Plan -> Implementation -> Review -> QA -> Evidence -> Approval -> Docs Sync -> Merge`

인간은 중요한 승인 지점에서만 개입한다.

- 범위 확정
- 아키텍처 변경 승인
- 예외 승인
- 최종 merge 승인
- release 승인

## 2. 왜 공장 MVP인가

이 시스템은 아직 중앙 플랫폼이 아니다.  
대신 다음 요소가 이미 정의된다.

- 역할 분리
- 문서 계약
- 승인 게이트
- evidence 포맷
- 상태 전이
- 실행 기록

즉, “버리는 자동화”가 아니라 나중에 플랫폼으로 올릴 수 있는 생산라인의 최소 단위다.

## 3. 핵심 목표

### 최종 플랫폼 목표
- multi-project
- multi-repo
- approval queue UI
- agent registry
- observability
- 정책 엔진
- release automation

### MVP 목표
- 단일 저장소 기준
- PR 단위 실행
- 승인자 중심 흐름
- 문서 기반 계약
- evidence 기반 승인
- 문서 동기화 강제

## 4. 설계 원칙

- approval-first
- docs as contracts
- plan before code
- PR-sized execution
- evidence before approval
- code-doc sync required
- platform-ready boundaries

## 5. 이번 MVP 범위

포함:
- Work Item 등록
- 설계 초안
- ADR 초안
- PR 분해
- 구현/리뷰/QA
- Evidence bundle 생성
- Approval request 생성
- 문서 동기화 체크

제외:
- 대시보드
- 멀티 프로젝트 중앙 제어
- 복잡한 권한 시스템
- 에이전트 마켓플레이스
- 배포 자동화

## 6. 성공 기준

- 승인자가 코드 전체를 읽지 않고도 판단할 수 있다.
- 모든 변경이 PR 단위로 잘려 있다.
- 코드 변경 시 문서 영향이 함께 추적된다.
- approval 없이 merge되지 않는다.
