# PR-001 Scope

## 제목
실행 파이프라인 설계 및 상태 모델 구체화

## 목적
WI-001을 구현하기 전에, approval-factory MVP의 실제 실행 흐름과 핵심 도메인 모델을 문서 수준에서 구체화한다.

## 포함 범위
- docs/design/architecture.md 보강
- docs/design/domain-model.md 보강
- 필요 시 ADR 추가
- docs/work-items 및 docs/prs 사용 방식 명시

## 비포함 범위
- CLI 구현
- approval queue 코드 구현
- evidence bundle 생성 코드

## Acceptance Criteria
- WorkItem, PRPlan, ApprovalRequest, EvidenceBundle, RunRecord 모델이 문서에 반영된다.
- 실행 상태 전이가 문서에 반영된다.
- 중요한 구조 결정이 있으면 ADR이 추가된다.
- 이후 구현 PR로 나눌 수 있을 정도로 설계가 구체화된다.
