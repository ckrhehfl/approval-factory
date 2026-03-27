# WI-005: MVP Finish (Repo-local docs and operations)

## Status
Draft

## 문제 정의

repo-local approval factory 구현은 완료 후보 상태이나, README와 운영 문서가 현재 CLI/게이트/queue 동작을 초보 승인자가 재실행 가능한 수준으로 설명하지 못한다.

## 목표

새 기능 추가 없이, 현재 구현 상태를 정확히 설명하는 운영 문서 세트를 완성한다.

## 포함 범위

- README를 현재 구현 기준으로 정합화
- `docs/ops/how-we-work.md` 작성
- `docs/ops/mvp-checklist.md` 작성
- `docs/ops/demo-script.md` 작성
- `docs/prs/PR-005/plan.md` 작성

## 비포함 범위

- Goal intake 자동화
- UI
- central control plane
- multi-project orchestration
- 새 gate 로직/새 CLI 명령 추가

## 성공 기준

1. 문서의 명령/경로/조건이 `orchestrator/cli.py`, `orchestrator/pipeline.py`, `config/gates.yaml`와 일치한다.
2. 데모 스크립트대로 실행하면 approval queue 적재까지 재현 가능하다.
3. 문서가 현재 MVP의 포함/비포함 범위를 명확히 구분한다.

## 리스크

- 구현 변경 없이 문서만 갱신하므로, 향후 코드 변경 시 문서 드리프트가 다시 발생할 수 있다.

## 승인자 질문

- 현재 상태를 repo-local MVP 종료 기준으로 인정하고 다음 단계(Goal intake/clarification/WI 자동화) 설계로 넘어가도 되는가?
