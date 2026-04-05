# AGENTS.md

이 문서는 approval-factory에서 동작하는 모든 에이전트의 공통 규약이다.

## Core Repo Principles

1. approval-first  
   에이전트의 목표는 인간 결정을 대체하는 것이 아니라, 인간이 빠르고 안전하게 결정할 수 있도록 준비하는 것이다.

2. source-of-truth first  
   repo 코드, 테스트, git history, runtime artifacts를 우선 근거로 삼는다.

3. plan before code  
   승인된 요구와 설계 없이 구현을 시작하지 않는다.

4. evidence before approval  
   승인 요청은 반드시 evidence bundle을 포함한다.

5. code-doc sync required  
   코드 변경 후 관련 문서가 갱신되지 않으면 완료로 간주하지 않는다.

## Source of Truth / Docs Scope

- source of truth 우선순위는 repo 코드, 테스트, git history, runtime artifacts이다.
- 공식 runtime artifacts와 공식 repo docs는 그 다음 근거로 사용한다.
- docs/prs와 외부 handoff pack은 참고자료이며, 1차 근거를 덮어쓰지 못한다.
- 문서는 운영 계약으로 다루되, source-of-truth 우선순위와 충돌하게 해석하지 않는다.

## 역할별 공통 의무

모든 에이전트는 다음을 수행해야 한다.

- 입력 근거의 버전 또는 기준 범위를 명시한다.
- 변경 범위를 벗어나지 않는다.
- 자신이 생성한 산출물을 지정된 템플릿 형식으로 남긴다.
- 불확실성이 크면 추측으로 결정하지 않고 “approval required”로 올린다.
- 구조적 변경을 감지하면 ADR 필요 여부를 판정한다.
- 작업 종료 시 docs sync 필요 여부를 판정한다.

## Change Safety

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

## Review Guidelines

- 리뷰는 findings-first로 작성한다. 요약보다 material issue, risk, missing evidence를 먼저 기록한다.
- Codex는 기본 안전망으로 GitHub review를 자동 수행한다.
- review-required PR만 deep review를 수행한다. review-optional PR은 핵심 리스크만 확인하고, review-skip은 자동 검토 또는 최소 확인으로 마무리한다.
- review-required: 아키텍처 영향, 승인 규칙 변경, 보안/비용/성능 민감 변경, 테스트 전략 변화, 문서-구현 불일치 가능성이 큰 변경
- review-optional: 국소적 문서 수정, 저위험 리팩터, 명확한 범위의 비동작 변경
- review-skip: 형식 정리, 오탈자, 기계적 갱신처럼 의미 변화가 없는 변경
- no material issues found: 승인 또는 통과 의견을 남기되, 확인한 evidence 범위를 명시한다.
- minor issue: 작성자 수정 요청 없이도 되는 경미한 보완 사항으로 남긴다.
- structural issue: 설계, 범위, 승인 조건, 검증 근거가 흔들리는 경우로 분류하고 approval required 또는 변경 요청으로 올린다.

## Evidence Collection Rule

- 사용자 붙여넣기 터미널 출력은 auxiliary evidence일 뿐이며, 검증이나 리뷰의 1차 근거로 단독 사용하지 않는다.
- validation 또는 review가 baseline, diff, test 결과에 의존하면 Codex가 해당 명령을 직접 실행해 primary evidence를 수집한다.
- working-tree review는 미커밋 변경의 working-tree diff와 현재 실행 결과를 기준으로 삼는다.
- committed-range review는 지정된 commit range 또는 base/head diff와 해당 범위의 실행 결과를 기준으로 삼는다.

## 역할 출력 최소 기준

모든 역할의 산출물은 다음을 포함해야 한다.

- input refs
- scope
- output summary
- risks
- next required gate
