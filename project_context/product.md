# Product Context

## 문서 목적
이 문서는 approval-factory 프로젝트의 **제품 의도와 MVP 범위**를 정의한다.
Architect, Planner, Implementer, Reviewer, QA, Docs Sync 역할은 이 문서를 제품 의도의 1차 기준으로 사용한다.

## 한 줄 정의
approval-factory는 **승인자 중심 멀티 에이전트 개발 오케스트레이션 MVP**다.
AI 에이전트들이 설계, 계획, 구현, 리뷰, QA, 문서 동기화를 수행하고, 인간은 중요한 승인 지점에서만 판단한다.

## 왜 만드는가
현재 AI 코딩 도구는 코드 생성에는 강하지만, 승인자 중심 개발 운영에는 약하다.
이 프로젝트의 목적은 단순 코드 생성기가 아니라 다음을 만족하는 개발 공장을 만드는 것이다.

- 승인자 중심 운영
- 문서 기반 계약
- PR 단위 실행
- evidence 기반 승인
- 설계 변경 시 문서/ADR 동기화
- 플랫폼화 가능한 구조

## 목표 사용자
- 1차 사용자: 승인자 / PM / 오케스트레이터
- 2차 사용자: Architect, Planner, Implementer, Reviewer, QA 역할의 AI 에이전트
- 3차 사용자: 이후 이 공장을 이용해 실제 프로젝트를 운영하는 소규모 개발팀

## 이번 MVP에서 꼭 되는 것
1. Work Item을 등록할 수 있다.
2. Work Item을 작은 PR 계획으로 분해할 수 있다.
3. PR마다 구현, 리뷰, QA, 문서 동기화, 승인 패키지 생성 흐름을 갖는다.
4. 승인자는 evidence를 보고 approve / reject / request changes를 판단할 수 있다.
5. 코드 변경 시 관련 설계 문서, ADR, PR 문서의 갱신 여부가 판정된다.

## 이번 MVP에서 하지 않을 것
- 멀티 프로젝트 중앙 대시보드
- 멀티 레포 중앙 control plane
- 웹 UI
- 자동 배포 / 운영 자동화
- 조직 권한 관리
- 고급 정책 엔진
- 병렬 다중 에이전트 스케줄러

## 핵심 사용 시나리오
1. 승인자가 Work Item을 등록한다.
2. Architect가 설계 문서를 보강하고 ADR이 필요하면 작성한다.
3. Planner가 Work Item을 작은 PR로 분해한다.
4. Implementer가 PR 하나를 구현한다.
5. Reviewer가 결함과 설계 위반을 검토한다.
6. QA가 acceptance criteria와 evidence를 검증한다.
7. Docs Sync가 문서 갱신 여부를 판정하고 반영한다.
8. 시스템이 approval package를 만든다.
9. 승인자가 승인하면 merge한다.

## 성공 기준
다음이 가능하면 MVP 성공으로 본다.
- 승인자가 코드 전체를 읽지 않고도 PR 승인 여부를 판단할 수 있다.
- 모든 변경이 PR 단위와 evidence 단위로 정리된다.
- 문서/ADR/ops와 코드 사이의 동기화 누락이 드러난다.
- 이 구조를 기반으로 이후 플랫폼화가 가능하다.

## 승인자 관점의 운영 원칙
- 설계 승인 전 구현 금지
- PR은 작고 독립적이어야 함
- evidence 없는 승인 금지
- 범위 변경은 항상 승인 대상
- 문서 동기화 없는 완료 금지

## 승인자 확인 필요
아래 항목은 실제 운영하면서 더 구체화해도 된다.
- Merge 승인 기준의 정량화 수준
- QA evidence 최소 형식
- docs sync 자동 판정 규칙의 상세 범위
