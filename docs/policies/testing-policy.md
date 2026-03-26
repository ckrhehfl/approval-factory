# Testing Policy

테스트는 4층 구조를 따른다.

## 1. Static Validation
- lint
- format
- type check
- schema validation

## 2. Automated Verification
- unit test
- integration test
- build

## 3. Workflow Verification
- 핵심 사용자 흐름 E2E
- PR 단위 회귀 검증

## 4. Orchestration Policy Validation
- docs sync 누락 검출
- ADR 필요 여부 검출
- approval request 필수 필드 검출
- evidence bundle 누락 검출

## 규칙

- Reviewer는 코드/설계 정합성을 본다.
- QA는 동작과 evidence를 본다.
- 테스트 실패를 무시하려면 exception approval이 필요하다.
