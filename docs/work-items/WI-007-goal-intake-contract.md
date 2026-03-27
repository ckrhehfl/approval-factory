# WI-007: Goal Intake Contract

## Status
In Review (PR-007)

## 문제 정의

현재 repo-local approval-factory MVP는 review, qa, docs-sync, verification, evidence, approval request, approval decision까지의 뒤쪽 승인 공장 코어를 갖고 있다. 하지만 사람이 만들고 싶은 프로그램의 목표를 repo 안에 공식 계약 형태로 남기는 Goal intake artifact가 없다.

## 목표

repo-local, file-based 방식의 최소 Goal intake contract를 도입해 사람이 읽을 수 있는 Goal artifact를 안정적으로 생성하고 관리한다.

## 포함 범위

- `factory create-goal` CLI 추가
- `goals/<goal-id>.md` Markdown artifact 생성
- Goal artifact 기본 섹션 계약 정의
- duplicate `goal-id` 안전 실패 처리
- README 및 ops 문서에 Goal intake minimum 범위 반영

## 비포함 범위

- 질문 자동 생성
- Goal 해결 자동화
- Goal to Work Item 자동 분해
- planner/resolver 구현
- LLM 연동

## 성공 기준

1. `factory create-goal` 실행 시 `goals/<goal-id>.md`가 생성된다.
2. Goal artifact에 Goal ID, Title, Status, Problem, Desired Outcome, Non-Goals, Constraints, Risks, Open Questions, Approval-Required Decisions, Success Criteria 섹션이 포함된다.
3. 동일 `goal-id`로 재생성하면 안전하게 실패한다.
4. README 및 ops 문서가 Goal intake minimum 범위와 제외 범위를 정확히 설명한다.
5. 기존 approval factory run/approval 흐름은 깨지지 않는다.

## 리스크

- Goal artifact만 도입된 상태에서 사용자가 다음 단계 자동화를 기대할 수 있다.
- Markdown 중심 계약이므로 후속 PR에서 parser 도입 시 strict contract 논의가 다시 필요할 수 있다.

## 승인자 질문

- PR-007 범위를 Goal artifact 생성과 관리의 최소 계약으로 승인하고, planner/resolver는 다음 PR로 분리해도 되는가?
