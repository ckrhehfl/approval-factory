# How We Work (Repo-local MVP)

## 목적

이 문서는 approval-factory를 현재 구현 범위 안에서 어떻게 운영하는지 설명한다. 현재 시스템은 완전 자동화가 아니라 승인자 중심의 반자동 MVP다.

## 범위 선언

포함:
- repo-local
- file-based
- approval-first
- one-PR-at-a-time

비포함:
- Goal intake 자동화
- UI
- central control plane
- multi-project orchestration

## 운영 흐름 (WI -> PR -> run -> approval)

1. Work Item 정의
- `docs/work-items/WI-###-*.md`에 문제/범위/성공기준을 기록한다.

2. PR 단위 계획
- `docs/prs/PR-###/plan.md` 중심으로 one-PR-at-a-time 실행 계획을 고정한다.

3. Run 부트스트랩
- `factory bootstrap-run`으로 `runs/latest/<run-id>/` 및 기본 artifact를 만든다.

4. 역할별 결과 기록
- Implementer/Reviewer/QA/Docs Sync/Verification 결과를 해당 record 명령으로 artifact에 반영한다.

5. 게이트 판정
- `factory gate-check`로 `gate-status.yaml`을 갱신한다.

6. 승인 패키지 생성
- `factory build-approval`로 `evidence-bundle.yaml`, `approval-request.yaml`를 최신 상태로 만든다.
- 조건이 맞으면 `approval_queue/pending/`에 approval 요청 파일이 적재된다.

7. 승인자 결정
- 승인자는 queue 파일과 evidence를 보고 `approve/reject/request_changes/approve_with_exception`을 결정한다.

## 역할 설명 (현재 MVP 기준)

Implementer:
- 승인된 PR 계획 범위에서만 변경한다.
- 구현 결과와 verification 입력값을 준비한다.

Reviewer:
- 설계 정합성/리스크/결함 관점으로 `record-review`에 반영될 판단 근거를 제공한다.

QA:
- 기능/회귀 관점 검증 결과를 `record-qa`로 반영한다.

Docs Sync:
- 문서 동기화 필요 여부와 완료 상태를 `record-docs-sync`로 반영한다.

Verification:
- `lint/tests/type-check/build` 상태를 `record-verification`로 기록한다.

## 반자동 MVP라는 점

- 명령 실행과 판정 업데이트는 CLI로 반자동 처리한다.
- 최종 승인 결정은 반드시 인간 승인자가 수행한다.
- 승인 없는 범위 확대, 구조 변경 확정, 테스트 실패 무시는 금지다.
