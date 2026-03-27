# approval-factory

승인자(Approver)가 evidence 기반으로 안전하게 결정할 수 있도록, PR 단위 실행 기록을 repo-local 파일로 남기는 approval-first 오케스트레이션 MVP다.

## 현재 MVP 범위

포함:
- repo-local, file-based 운영 (`runs/latest`, `approval_queue/*`)
- approval-first 원칙 기반의 게이트 판정
- one-PR-at-a-time 운영 가정
- PR 실행 산출물(artifact) 및 문서 흔적(`docs/prs`, `docs/work-items`) 생성/갱신

비포함:
- Goal intake 자동화
- UI
- central control plane
- multi-project orchestration

## 지원 CLI 명령

엔트리포인트: `factory`

- `bootstrap-run`
- `record-review`
- `record-qa`
- `record-docs-sync`
- `record-verification`
- `gate-check`
- `build-approval`

도움말:

```bash
factory --help
factory <command> --help
```

## 기본 실행 흐름

1. `bootstrap-run`으로 canonical run/artifact 스켈레톤 생성
2. `record-verification`으로 lint/tests/type-check/build 상태 기록
3. `record-review` 기록
4. `record-qa` 기록
5. `record-docs-sync` 기록
6. `gate-check`로 merge/exception gate 판정
7. `build-approval`로 evidence/approval-request 생성 및 조건 충족 시 queue 적재

조건 요약:
- review/qa 실패 시 `merge_approval=blocked`
- verification 실패가 있으면 `merge_approval=exception_required`
- 모든 prerequisite 통과 시 `merge_approval=ready`
- queue 적재는 `docs_sync` 완료(`complete` 또는 `not-needed`)이고 merge gate가 `ready` 또는 `exception_required`일 때만 수행

## approval queue 설명

- 대기 큐: `approval_queue/pending/`
- 승인 큐: `approval_queue/approved/`
- 반려 큐: `approval_queue/rejected/`
- 예외 큐: `approval_queue/exceptions/`

`build-approval`는 기본적으로 `approval_queue/pending/APR-<run-id>.yaml`를 사용한다.

재실행 규칙:
- 같은 내용으로 재실행하면 queue 파일을 중복 생성하지 않는다(idempotent).
- 같은 파일명이 이미 있고 내용이 다르면 `--r2`, `--r3` 접미사를 붙여 저장한다.

## 주요 경로

- 오케스트레이터: `orchestrator/`
- 게이트 설정: `config/gates.yaml`
- 운영 문서: `docs/ops/`
- PR 문서: `docs/prs/`
- Work Item 문서: `docs/work-items/`
- 실행 결과: `runs/latest/<run-id>/`

## 빠른 시작

```bash
pip install -e ".[dev]"
factory bootstrap-run --root . --run-id RUN-LOCAL --work-item-id WI-LOCAL --work-item-title "local bootstrap" --pr-id PR-LOCAL
factory record-verification --root . --run-id RUN-LOCAL --lint pass --tests pass --type-check pass --build pass --summary "all checks green"
factory record-review --root . --run-id RUN-LOCAL --status pass --summary "review ok"
factory record-qa --root . --run-id RUN-LOCAL --status pass --summary "qa ok"
factory record-docs-sync --root . --run-id RUN-LOCAL --status complete --summary "docs aligned"
factory gate-check --root . --run-id RUN-LOCAL
factory build-approval --root . --run-id RUN-LOCAL
```

## 다음 단계 후보 (MVP 이후)

1. Goal intake
2. clarification loop
3. WI auto-generation
