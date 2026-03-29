# WI-020: work item readiness visibility

## Input Refs
- AGENTS.md vcurrent
- README.md work item and status sections
- docs/ops/runbook.md work item contract
- docs/ops/how-we-work.md Goal -> clarification -> WI flow
- docs/contracts/work-item-contract.md
- docs/work-items/WI-019-work-item-clarification-linkage.md

## Scope
- `factory work-item-readiness` read-only CLI 추가
- work item linked clarification의 현재 status 조회와 readiness summary 출력
- 테스트와 운영 문서 최소 보강

## Problem
work item에 clarification linkage는 남길 수 있지만, operator가 특정 work item을 보고 linked clarification 기준으로 지금 바로 진행 가능한지 빠르게 판단하기 어렵다. 자동 gating 전에 사람이 읽을 수 있는 최소 visibility 계층이 먼저 필요하다.

## Output Summary
- `docs/work-items/<work-item-id>.md`를 읽는 read-only readiness visibility 명령 추가
- linked clarification 없음=`no-linked-clarifications`, 모두 resolved=`ready`, open/deferred/escalated 존재=`attention-needed` 규칙 고정
- create-work-item, create-pr-plan, start-execution, approval semantics는 변경하지 않음

## Risks
- readiness summary가 blocking/gating semantics로 오해되면 현재 approval-first 운영 계약이 흔들릴 수 있다.
- work item `Related Clarifications` 파싱이 문서 계약과 어긋나면 visibility 명령이 불안정해질 수 있다.

## Next Required Gate
- Implementer: CLI/helper/tests/docs sync
- Reviewer: visibility-only 범위 유지와 no-breaking-change 확인
- QA: readiness rule regression과 전체 테스트 통과 확인
