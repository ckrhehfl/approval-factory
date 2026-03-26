# ADR-002 PR-Sized Execution

- Status: Accepted
- Date: 2026-03-26

## Context

대규모 자율 작업은 승인과 검증이 어렵고 실패 시 복구 비용이 크다.

## Decision

모든 실행 단위를 PR-sized change로 제한한다.

## Consequences

- 승인 단위가 작아진다.
- 병렬 작업 계획이 쉬워진다.
- evidence가 더 명확해진다.
