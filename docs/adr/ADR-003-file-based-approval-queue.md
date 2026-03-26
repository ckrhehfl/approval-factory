# ADR-003 File-Based Approval Queue for MVP

- Status: Accepted
- Date: 2026-03-26

## Context

MVP 단계에서 중앙 DB나 전용 UI를 먼저 만들면 추상화 비용이 과도하다.

## Decision

승인 큐와 실행 상태는 repo-local 파일 구조와 PR artifact로 관리한다.

## Consequences

- 초기 구현이 단순하다.
- Git으로 이력 추적이 가능하다.
- 추후 서비스형 approval queue로 이전할 수 있다.
