# approval-factory

승인자(Approver)가 evidence 기반으로 안전하게 결정할 수 있도록, PR 단위 실행 기록을 repo-local 파일로 남기는 approval-first 오케스트레이션 MVP다.

## 현재 MVP 범위

포함:
- repo-local, file-based Goal intake minimum (`goals/*.md`)
- repo-local, file-based clarification queue minimum (`clarifications/*/*.md`)
- repo-local, file-based 운영 (`runs/latest`, `approval_queue/*`)
- approval-first 원칙 기반의 게이트 판정
- one-PR-at-a-time 운영 가정
- PR 실행 산출물(artifact) 및 문서 흔적(`docs/prs`, `docs/work-items`) 생성/갱신

비포함:
- Goal intake 질문 자동 생성
- clarification 질문 자동 생성
- clarification 질문 자동 해결
- Goal to Work Item 자동 분해
- LLM 연동
- UI
- central control plane
- multi-project orchestration

## 지원 CLI 명령

엔트리포인트: `factory`

- `bootstrap-run`
- `create-goal`
- `create-clarification`
- `record-review`
- `record-qa`
- `record-docs-sync`
- `record-verification`
- `gate-check`
- `build-approval`
- `resolve-approval`

도움말:

```bash
factory --help
factory <command> --help
```

## 기본 실행 흐름

1. `create-goal`로 repo-local Goal artifact 생성
2. `create-clarification`로 Goal 기준 clarification queue artifact 생성
3. 사람 승인 하에 Goal과 clarification을 Work Item/PR 계획으로 연결
4. `bootstrap-run`으로 canonical run/artifact 스켈레톤 생성
5. `record-verification`으로 lint/tests/type-check/build 상태 기록
6. `record-review` 기록
7. `record-qa` 기록
8. `record-docs-sync` 기록
9. `gate-check`로 merge/exception gate 판정
10. `build-approval`로 evidence/approval-request 생성 및 조건 충족 시 queue 적재
11. `resolve-approval`로 승인자 결정을 기록하고 queue를 pending에서 최종 queue로 이동

조건 요약:
- review/qa 실패 시 `merge_approval=blocked`
- verification 실패가 있으면 `merge_approval=exception_required`
- 모든 prerequisite 통과 시 `merge_approval=ready`
- queue 적재는 `docs_sync` 완료(`complete` 또는 `not-needed`)이고 merge gate가 `ready` 또는 `exception_required`일 때만 수행

## gate-check vs build-approval

- `gate-check`:
  - `gate-status.yaml`의 gate 판정만 갱신한다.
  - `evidence_bundle_complete` 판정은 기존 `evidence-bundle.yaml` 상태를 읽어 계산한다.
  - 따라서 `gate-check`만 실행한 결과는 최종 승인 요청 산출물 최신 상태를 보장하지 않는다.
- `build-approval`:
  - 내부에서 evidence bundle 재생성 후 gate를 다시 계산한다.
  - `evidence-bundle.yaml`과 `approval-request.yaml`을 최신 상태로 만든다.
  - 조건 충족 시 `approval_queue/pending/APR-<run-id>.yaml`를 생성/갱신한다.

## approval queue 설명

- 대기 큐: `approval_queue/pending/`
- 승인 큐: `approval_queue/approved/`
- 반려 큐: `approval_queue/rejected/`
- 예외 큐: `approval_queue/exceptions/`

`build-approval`는 기본적으로 `approval_queue/pending/APR-<run-id>.yaml`를 사용한다.

현재 MVP에서 자동 처리되는 범위:
- pending 큐 적재까지 (`build-approval` 실행 시)
- 승인자 결정 기록 및 queue 이동 (`resolve-approval` 실행 시)

현재 MVP에서 수동 운영인 범위:
- merge/release 실행

재실행 규칙:
- 같은 내용으로 재실행하면 queue 파일을 중복 생성하지 않는다(idempotent).
- 같은 파일명이 이미 있고 내용이 다르면 `--r2`, `--r3` 접미사를 붙여 저장한다.

## 주요 경로

- 오케스트레이터: `orchestrator/`
- Goal artifact: `goals/<goal-id>.md`
- Clarification artifact: `clarifications/<goal-id>/<clarification-id>.md`
- 게이트 설정: `config/gates.yaml`
- 운영 문서: `docs/ops/`
- PR 문서: `docs/prs/`
- Work Item 문서: `docs/work-items/`
- 실행 결과: `runs/latest/<run-id>/`

## 빠른 시작

```bash
pip install -e ".[dev]"
factory create-goal --root . --goal-id GOAL-LOCAL --title "local intake" --problem "Need a formal goal artifact" --outcome "A readable goal file exists" --constraints "repo-local only"
factory create-clarification --root . --goal-id GOAL-LOCAL --clarification-id CLAR-001 --title "scope boundary" --category scope --question "What must stay out of scope for this goal?"
factory bootstrap-run --root . --run-id RUN-LOCAL --work-item-id WI-LOCAL --work-item-title "local bootstrap" --pr-id PR-LOCAL
factory record-verification --root . --run-id RUN-LOCAL --lint pass --tests pass --type-check pass --build pass --summary "all checks green"
factory record-review --root . --run-id RUN-LOCAL --status pass --summary "review ok"
factory record-qa --root . --run-id RUN-LOCAL --status pass --summary "qa ok"
factory record-docs-sync --root . --run-id RUN-LOCAL --status complete --summary "docs aligned"
factory gate-check --root . --run-id RUN-LOCAL
factory build-approval --root . --run-id RUN-LOCAL
factory resolve-approval --root . --run-id RUN-LOCAL --decision approve --actor approver.local --note "all gates satisfied"
```

## 다음 단계 후보 (MVP 이후)

1. Goal clarification loop
2. clarification resolution loop
3. WI auto-generation
