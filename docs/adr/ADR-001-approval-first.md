# ADR-001 Approval-First

- Status: Accepted
- Date: 2026-03-26

## Context

이 시스템의 사용자는 구현자가 아니라 승인자/PM/오케스트레이터에 가깝다.  
따라서 완전 자율 코딩보다 승인 가능한 산출물과 게이트 설계가 더 중요하다.

## Decision

승인자 중심 흐름을 최상위 원칙으로 채택한다.  
모든 역할은 evidence를 준비하며, 중요한 결정은 인간이 수행한다.

## Consequences

- 승인 패키지와 evidence bundle이 핵심 artifact가 된다.
- 자동화보다 gate 설계 품질이 중요하다.
