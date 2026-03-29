# approval-factory

승인자(Approver)가 evidence 기반으로 안전하게 결정할 수 있도록, PR 단위 실행 기록을 repo-local 파일로 남기는 approval-first 오케스트레이션 MVP다.

## 현재 MVP 범위

포함:
- repo-local, file-based Goal intake minimum (`goals/*.md`)
- repo-local, file-based clarification queue minimum (`clarifications/*/*.md`)
- repo-local, file-based Work Item minimum (`docs/work-items/*.md`)
- repo-local, file-based single active PR plan minimum (`prs/active/*.md`)
- repo-local, file-based 운영 (`runs/latest`, `approval_queue/*`)
- approval-first 원칙 기반의 게이트 판정
- one-PR-at-a-time 운영 가정
- 잘못된 실행 순서를 막는 최소 guardrail과 run state 갱신
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
- `status`
- `start-execution`
- `create-goal`
- `create-clarification`
- `create-work-item`
- `create-pr-plan`
- `activate-pr`
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
3. `create-work-item`으로 Goal을 실행 가능한 Work Item Markdown artifact로 연결
4. `create-pr-plan`으로 Work Item 기준 PR plan 후보를 생성한다. active PR이 없으면 `prs/active/`에, 이미 있으면 `prs/archive/`에 만든다.
5. 필요 시 `activate-pr`로 기존 active PR을 `prs/archive/`로 이동하고 의도한 PR plan 후보를 active로 전환
6. `start-execution`으로 `prs/active/`의 단일 active PR plan에서 run을 시작
7. `record-verification`으로 lint/tests/type-check/build 상태 기록
8. `record-review` 기록
9. `record-qa` 기록
10. `record-docs-sync` 기록
11. `gate-check`로 merge/exception gate 판정
12. `build-approval`로 evidence/approval-request 생성 및 조건 충족 시 queue 적재
13. `resolve-approval`로 승인자 결정을 기록하고 queue를 pending에서 최종 queue로 이동

조건 요약:
- review/qa 실패 시 `merge_approval=blocked`
- verification 실패가 있으면 `merge_approval=exception_required`
- 모든 prerequisite 통과 시 `merge_approval=ready`
- queue 적재는 `docs_sync` 완료(`complete` 또는 `not-needed`)이고 merge gate가 `ready` 또는 `exception_required`일 때만 수행
- `build-approval`는 placeholder artifact만으로는 진행되지 않으며 `record-review`, `record-qa`, `record-docs-sync`, `record-verification`이 실제로 기록된 뒤에만 진행된다.
- `resolve-approval`는 `build-approval` 이후 생성된 approval request와 pending queue item이 모두 있어야만 진행된다.

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

## 상태 조회

- `factory status`는 현재 repo-local 상태를 읽기 전용으로 요약 출력한다.
- 이 명령은 파일을 변경하지 않는다.
- 조회 경로는 `prs/active/`, `runs/latest/`, `approval_queue/`, `clarifications/` 고정이다.

출력 항목:
- Active PR: `pr_id`, `work_item_id`
- Latest Run: `run_id`, `state`
- Approval: `status` (`pending`, `approved`, `none`)
- Open Clarifications: 열려 있는 clarification이 있으면 `clarification_id`

예시:

```bash
factory status --root .
```

## 주요 경로

- 오케스트레이터: `orchestrator/`
- Goal artifact: `goals/<goal-id>.md`
- Clarification artifact: `clarifications/<goal-id>/<clarification-id>.md`
- Work Item artifact: `docs/work-items/<work-item-id>.md`
- Active PR plan artifact: `prs/active/<pr-id>.md`
- Archived PR plan artifact: `prs/archive/<pr-id>.md`
- 게이트 설정: `config/gates.yaml`
- 운영 문서: `docs/ops/`
- PR 문서: `docs/prs/`
- Work Item 문서: `docs/work-items/`
- 실행 결과: `runs/latest/<run-id>/`

`activate-pr` 최소 계약:
- 입력: `--root`, `--pr-id`
- 전제: 지정한 `pr-id`의 PR plan artifact가 `prs/active/` 또는 `prs/archive/`에 존재해야 한다.
- 동작: 기존 active PR이 있으면 `prs/archive/`로 이동시키고, 지정한 PR plan을 `prs/active/`로 이동시킨다.
- 결과: `prs/active/` 아래에는 정확히 1개의 active PR만 남아야 한다.
- 범위: PR-011 execution flow 보강용 최소 전환만 제공하며, merge/close/history lifecycle 전체는 구현하지 않는다.

`create-pr-plan` 최소 계약:
- active PR이 없으면 `prs/active/<pr-id>.md`를 생성한다.
- active PR이 이미 있으면 새 PR plan 후보를 `prs/archive/<pr-id>.md`에 생성한다.
- duplicate `pr-id`는 `prs/active/`와 `prs/archive/`를 함께 검사해 막는다.

`start-execution` 최소 계약:
- 입력: `--root`, `--run-id`
- 전제: `prs/active/` 아래 active PR plan이 정확히 하나여야 한다.
- 전제: active PR plan의 `Work Item ID`가 `docs/work-items/` 아래 실제 work item artifact와 정확히 연결되어야 한다.
- 동작: active PR plan에서 `pr_id`, `work_item_id`, `title`을 읽고 기존 `bootstrap-run` 흐름 위에 run을 시작한다.
- 기록: `runs/latest/<run-id>/run.yaml`과 `artifacts/{pr-plan,work-item}.yaml`에 최소 `run_id`, `pr_id`, `work_item_id`, `pr_plan_path`, `work_item_path`가 식별 가능하게 남고 `run.yaml.state=in_progress`로 갱신된다.
- 실패: active PR plan이 0개이거나 2개 이상이거나, work item 연결이 불가하면 안전하게 실패한다.

`build-approval` 최소 계약:
- 전제: `verification-report.yaml`, `review-report.yaml`, `qa-report.yaml`, `docs-sync-report.yaml`가 모두 존재하고 실제 record 명령으로 기록돼 있어야 한다.
- 실패: prerequisite artifact가 없거나 아직 placeholder 상태면 누락된 record 명령을 명확히 보여주며 실패한다.
- 상태: 승인 패키지를 만들면 `run.yaml.state=approval_pending`으로 갱신된다.

`resolve-approval` 최소 계약:
- 전제: `approval-request.yaml`가 실제 `build-approval` 결과로 채워져 있어야 하고 `approval_queue/pending/APR-<run-id>.yaml`가 존재해야 한다.
- 실패: approval request artifact 또는 pending queue item이 없으면 누락 원인을 명확히 표시하고 실패한다.
- 상태: `approve`면 `approved`, `reject`면 `rejected`, `exception`은 `approval_pending` 상태를 유지한다.

`run.yaml.state` 최소 의미:
- `draft`: bootstrap만 된 상태
- `in_progress`: execution이 시작됐고 verification/review/qa/docs-sync 기록 중인 상태
- `approval_pending`: approval package가 만들어져 승인자 결정을 기다리는 상태
- `approved`: 승인자가 approve를 기록한 상태

## 빠른 시작

```bash
pip install -e ".[dev]"
factory create-goal --root . --goal-id GOAL-LOCAL --title "local intake" --problem "Need a formal goal artifact" --outcome "A readable goal file exists" --constraints "repo-local only"
factory create-clarification --root . --goal-id GOAL-LOCAL --clarification-id CLAR-001 --title "scope boundary" --category scope --question "What must stay out of scope for this goal?"
factory create-work-item --root . --work-item-id WI-LOCAL --title "local work item" --goal-id GOAL-LOCAL --description "Create a minimal work item artifact" --acceptance-criteria $'- docs/work-items/WI-LOCAL.md exists\n- Duplicate IDs fail safely'
factory create-pr-plan --root . --pr-id PR-LOCAL --work-item-id WI-LOCAL --title "local PR plan" --summary "Track the single active PR plan as a repo-local Markdown artifact"
factory activate-pr --root . --pr-id PR-LOCAL
factory start-execution --root . --run-id RUN-LOCAL
factory record-review --root . --run-id RUN-LOCAL --status pass --summary "review ok"
factory record-qa --root . --run-id RUN-LOCAL --status pass --summary "qa ok"
factory record-docs-sync --root . --run-id RUN-LOCAL --status complete --summary "docs aligned"
factory record-verification --root . --run-id RUN-LOCAL --lint pass --tests pass --type-check pass --build pass --summary "all checks green"
factory gate-check --root . --run-id RUN-LOCAL
factory build-approval --root . --run-id RUN-LOCAL
factory resolve-approval --root . --run-id RUN-LOCAL --decision approve --actor approver.local --note "all gates satisfied"
```

## 다음 단계 후보 (MVP 이후)

1. Goal clarification loop
2. clarification resolution loop
3. Goal to Work Item linkage hardening
4. WI auto-generation

`bootstrap-run`은 제거되지 않았다. 현재는 `activate-pr`로 active PR를 명시적으로 전환한 뒤 `start-execution`이 그 active PR plan을 읽어 실행을 시작하는 공식 entrypoint이고, `bootstrap-run`은 그 아래의 run bootstrap 기반 명령으로 유지된다.
