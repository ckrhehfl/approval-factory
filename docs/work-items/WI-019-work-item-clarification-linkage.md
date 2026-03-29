# WI-019: work item clarification linkage

## Input Refs
- AGENTS.md vcurrent
- README.md create-work-item and status sections
- docs/ops/runbook.md work item contract
- docs/ops/how-we-work.md Goal -> clarification -> WI flow
- docs/contracts/work-item-contract.md
- docs/work-items/WI-018-clarification-resolution-minimum.md

## Scope
- `factory create-work-item`에 반복 가능한 `--clarification-id` 입력 추가
- 같은 goal 아래 clarification linkage validation과 안전 실패 추가
- work item markdown에 clarification linkage 섹션 추가
- 관련 테스트와 운영 문서 보강

## Problem
goal 생성, clarification 생성/종결, work item 생성은 각각 가능하지만 어떤 clarification이 특정 work item의 근거였는지 공식 linkage가 약하다. 다음 구조 확장 전에 work item이 goal과 clarification 맥락을 함께 들고 있어야 수동 운영 추적이 덜 흔들린다.

## Output Summary
- work item이 관련 clarification id와 현재 status를 함께 기록하는 최소 linkage 계층 추가
- 없는 clarification, 다른 goal clarification, inconsistent artifact goal-id에 대한 보수적 guardrail 추가
- 자동 planner/resolver/link recommendation 없이 사람 운영자가 추적 가능한 수동 흐름 유지

## Risks
- linkage를 gating이나 automatic decision처럼 읽히면 현재 approval-first 운영 계약이 흐려질 수 있다.
- markdown 섹션 추가가 기존 work item artifact style이나 downstream read path와 어긋나면 문서 계약 drift가 생길 수 있다.

## Next Required Gate
- Implementer: CLI/helper/tests/docs sync
- Reviewer: no breaking change and scope containment 확인
- QA: full test suite와 create-work-item regression 확인
