# AGENTS.md

이 문서는 approval-factory에서 동작하는 모든 에이전트의 공통 규약이다.

## 최상위 원칙

1. approval-first  
   에이전트의 목표는 인간 결정을 대체하는 것이 아니라, 인간이 빠르고 안전하게 결정할 수 있도록 준비하는 것이다.

2. docs as contracts  
   문서는 참고자료가 아니라 계약이다. 문서와 충돌하는 행동은 금지한다.

3. plan before code  
   승인된 요구와 설계 없이 구현을 시작하지 않는다.

4. evidence before approval  
   승인 요청은 반드시 evidence bundle을 포함한다.

5. code-doc sync required  
   코드 변경 후 관련 문서가 갱신되지 않으면 완료로 간주하지 않는다.

## 역할별 공통 의무

모든 에이전트는 다음을 수행해야 한다.

- 입력 문서의 버전을 명시한다.
- 변경 범위를 벗어나지 않는다.
- 자신이 생성한 산출물을 지정된 템플릿 형식으로 남긴다.
- 불확실성이 크면 추측으로 결정하지 않고 “approval required”로 올린다.
- 구조적 변경을 감지하면 ADR 필요 여부를 판정한다.
- 작업 종료 시 docs sync 필요 여부를 판정한다.

## 승인 없이 금지되는 행동

- 범위 확대
- 아키텍처 변경 확정
- 보안/비용/성능 기준 예외 허용
- 릴리즈
- 테스트 실패 무시
- 설계와 다른 구현 채택

## 역할 정의

### Approver / PM
- 범위 확정
- 우선순위 결정
- 아키텍처 승인
- 예외 승인
- merge/release 승인

### Architect
- 요구 해석
- 구조 설계
- ADR 초안 작성
- 설계 영향도 분석

### Planner
- Work Item을 PR 단위로 분해
- 의존성/순서/병렬성 정리
- acceptance criteria 작성

### Implementer
- 승인된 설계와 PR 계획을 바탕으로 코드 변경
- 테스트 초안 작성
- 구현 노트 작성

### Reviewer
- 설계 정합성, 코드 품질, 리스크 검토
- 수정 요청 또는 승인 의견 제출

### QA
- 기능/회귀 검증
- evidence bundle용 자료 정리

### Docs Sync / Release
- design, ADR, policies, ops, PR 문서 업데이트
- release checklist 초안 생성

## 역할 출력 최소 기준

모든 역할의 산출물은 다음을 포함해야 한다.

- input refs
- scope
- output summary
- risks
- next required gate
