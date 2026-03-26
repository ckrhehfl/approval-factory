# PR-002 Scope

## 제목
핵심 도메인 모델과 파일 기반 저장 스켈레톤 구현

## 목적
문서로 정의된 핵심 모델을 코드 스켈레톤으로 구현하고, runs / approval_queue / work item 관련 파일 저장 구조를 시작한다.

## 포함 범위
- 핵심 도메인 모델 스켈레톤 구현
- 기본 파일 입출력 스켈레톤
- runs / approval_queue 경로 초기화 로직
- 최소 테스트

## 비포함 범위
- 완전한 CLI
- GitHub 연동
- 자동 리뷰 호출

## Acceptance Criteria
- WorkItem, PRPlan, ApprovalRequest, EvidenceBundle, RunRecord 구조가 코드에 존재한다.
- 파일 저장 경로 초기화가 가능하다.
- 최소 단위 테스트가 있다.
