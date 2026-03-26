# Acceptance Rules

## 문서 목적
이 문서는 PR 완료, approval 요청, merge 승인에 필요한 최소 완료 기준을 정의한다.

## PR 완료 기준
다음이 충족되어야 PR이 "검토 가능" 상태가 된다.
- scope.md와 plan.md가 존재한다.
- 구현 범위가 PR 계획과 일치한다.
- 관련 테스트가 존재하거나 테스트 불가 사유가 명시된다.
- 구현 메모가 남는다.
- 관련 문서 영향도 검토가 수행된다.

## Review 완료 기준
- 설계 위반 여부가 검토된다.
- must fix / should fix / acceptable risk가 정리된다.
- docs sync 필요 여부가 표시된다.

## QA 완료 기준
- acceptance criteria 충족 여부가 표시된다.
- evidence summary가 있다.
- residual risk가 있다.
- 수동 확인이 필요한 항목이 정리된다.

## Merge 전 필수 조건
- 필요한 테스트가 통과한다.
- approval package가 생성된다.
- docs sync가 완료되거나 불필요 판정이 남는다.
- 승인자의 approve가 기록된다.

## Approval Package 필수 항목
- 변경 요약
- 변경 이유
- 통과/실패 테스트 요약
- changed files
- changed docs
- residual risk
- 승인 요청 질문

## 수동 승인 포인트
- Work Item 시작 승인
- 설계 승인
- PR 계획 승인
- merge 승인
- release 승인
