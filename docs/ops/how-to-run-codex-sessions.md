# How to Run Codex Sessions for approval-factory MVP

## 핵심 원칙
- 레포는 하나다.
- 세션은 역할별로 나눈다.
- 처음에는 한 번에 하나의 PR만 진행한다.
- 설계 승인 전 구현 금지.

## 세션 구조
1. Context Drafter
2. Architect
3. Planner
4. Implementer
5. Reviewer
6. QA
7. Docs Sync

## 실제 순서
### Step 1. Context Drafter
목표:
- project_context/*.md를 채운다.

### Step 2. Architect
목표:
- docs/design/*와 필요 ADR을 보강한다.

### Step 3. Planner
목표:
- WI-001을 작은 PR들로 나눈다.

### Step 4. Implementer
목표:
- 승인된 PR 하나만 구현한다.

### Step 5. Reviewer
목표:
- 결함, 설계 위반, 테스트 공백, docs sync 필요 여부를 찾는다.

### Step 6. QA
목표:
- acceptance criteria와 evidence를 검증한다.

### Step 7. Docs Sync
목표:
- 문서 갱신이 필요한지 판정하고 반영한다.

## 처음에는 한번에 실행하지 않는 이유
처음부터 여러 역할을 자동으로 한 번에 연결하면,
문제 발생 시 어디서 잘못됐는지 추적하기 어렵다.
MVP의 첫 목적은 자동화 수준이 아니라 **승인 가능한 운영 루프를 안정적으로 만드는 것**이다.

## 언제 자동화를 늘리나
아래가 안정화된 뒤에 늘린다.
- Context 문서가 잘 채워짐
- 설계 PR 품질이 안정적임
- PR 분해 품질이 안정적임
- 리뷰와 QA 결과가 반복적으로 유용함

그 다음에 scripts/ 또는 orchestrator/를 통해 반자동화한다.
