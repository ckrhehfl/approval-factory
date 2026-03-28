# WI-008: Clarification Queue

## Status
In Review (PR-008)

## 문제 정의

현재 repo-local approval-factory MVP는 Goal intake 이후에 누락 정보, 질문, 승인 필요 사항을 구조화해 추적하는 최소 clarification 계층이 없다. 이 때문에 Goal이 생성된 뒤 사람은 질문을 비정형적으로 남기게 되고, 어떤 질문이 중요한지 또는 승인자 escalation이 필요한지 일관되게 관리하기 어렵다.

## 목표

repo-local, file-based 방식의 최소 clarification queue contract를 도입해 Goal 기준 질문 artifact를 Markdown으로 생성하고 관리한다.

## 포함 범위

- `factory create-clarification` CLI 추가
- `clarifications/<goal-id>/<clarification-id>.md` Markdown artifact 생성
- clarification artifact 기본 섹션 계약 정의
- category 검증과 duplicate `clarification-id` 안전 실패 처리
- README 및 ops 문서에 clarification queue가 Goal intake 다음 단계의 최소 질문 관리 계층임을 반영

## 비포함 범위

- 질문 자동 생성
- 질문 자동 해결
- clarification resolver/planner 구현
- Goal to Work Item 자동 분해
- LLM 연동

## 성공 기준

1. `factory create-clarification` 실행 시 `clarifications/<goal-id>/<clarification-id>.md`가 생성된다.
2. clarification artifact에 Clarification ID, Goal ID, Title, Status, Category, Question, Suggested Resolution, Escalation Required, Resolution Notes, Next Action 섹션이 포함된다.
3. 기본 `Status`는 `open`이며 `category`는 `scope|design|dependency|constraint|approval-required`만 허용된다.
4. 동일 `goal-id` 아래 동일 `clarification-id`로 재생성하면 안전하게 실패한다.
5. README 및 ops 문서가 clarification queue를 Goal intake 다음 단계의 최소 질문 관리 계층으로 정확히 설명한다.
6. 기존 approval factory run/approval 흐름은 깨지지 않고 `pytest -q`가 통과한다.

## 리스크

- clarification queue만 추가된 상태에서 사용자가 자동 triage나 auto-resolution을 기대할 수 있다.
- Markdown contract 기반이므로 후속 PR에서 resolver가 붙을 때 상태 전이와 goal linkage strictness를 더 명확히 해야 할 수 있다.

## 승인자 질문

- PR-008 범위를 clarification artifact 생성과 최소 queue 계약으로 승인하고, resolver/planner와 자동화는 다음 PR로 분리해도 되는가?
