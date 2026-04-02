# approval-factory

승인자(Approver)가 evidence 기반으로 안전하게 결정할 수 있도록, PR 단위 실행 기록을 repo-local 파일로 남기는 approval-first 오케스트레이션 MVP다.

## 현재 MVP 범위

포함:
- repo-local, file-based Goal intake minimum (`goals/*.md`)
- repo-local, file-based clarification draft minimum (`clarification_drafts/*.md`)
- repo-local, file-based clarification queue minimum (`clarifications/*/*.md`)
- repo-local, file-based work item draft minimum (`work_item_drafts/*.md`)
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
- `inspect-approval-queue`
- `inspect-approval`
- `inspect-goal`
- `inspect-clarification`
- `inspect-work-item`
- `inspect-pr-plan`
- `inspect-run`
- `trace-lineage`
- `cleanup-rehearsal`
- `start-execution`
- `create-goal`
- `draft-clarifications`
- `draft-work-items`
- `promote-clarification-draft`
- `promote-work-item-draft`
- `create-clarification`
- `resolve-clarification`
- `create-work-item`
- `work-item-readiness`
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
2. 필요 시 `draft-clarifications`로 `clarification_drafts/<goal-id>.md`에 deterministic draft-only artifact 생성
3. 필요한 항목만 `promote-clarification-draft` 또는 `create-clarification`로 Goal 기준 official clarification queue artifact로 수동 생성
4. 필요 시 `resolve-clarification`로 clarification artifact를 `resolved|deferred|escalated` 중 하나로 공식 종결
5. 필요 시 `draft-work-items`로 `work_item_drafts/<goal-id>.md`에 official clarification 기반 deterministic draft-only artifact를 생성한다.
6. 필요 시 `promote-work-item-draft`로 `work_item_drafts/<goal-id>.md`의 단일 후보를 `docs/work-items/<work-item-id>.md` official artifact로 수동 승격한다.
7. 또는 `create-work-item`으로 Goal을 실행 가능한 Work Item Markdown artifact로 직접 연결한다. 필요하면 관련 clarification id를 함께 남긴다.
8. 필요하면 `work-item-readiness`로 linked clarification 기준 최소 readiness visibility를 읽기 전용으로 확인한다.
9. `create-pr-plan`으로 Work Item 기준 PR plan 후보를 생성한다. active PR이 없으면 `prs/active/`에, 이미 있으면 `prs/archive/`에 만든다. 이때 source work item readiness context도 함께 기록한다.
10. 필요 시 `activate-pr`로 기존 active PR을 `prs/archive/`로 이동하고 의도한 PR plan 후보를 active로 전환
11. `start-execution`으로 `prs/active/`의 단일 active PR plan에서 run을 시작
12. `record-verification`으로 lint/tests/type-check/build 상태 기록
13. `record-review` 기록
14. `record-qa` 기록
15. `record-docs-sync` 기록
16. `gate-check`로 merge/exception gate 판정
17. `build-approval`로 evidence/approval-request 생성 및 조건 충족 시 queue 적재
18. `resolve-approval`로 승인자 결정을 기록하고 queue를 pending에서 최종 queue로 이동

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
  - 가능하면 source work item readiness context도 approval artifact에 함께 기록한다.
  - 조건 충족 시 `approval_queue/pending/APR-<run-id>.yaml`를 생성/갱신한다.

approval artifact readiness visibility:
- `build-approval`는 source PR/work item readiness context를 읽을 수 있으면 `evidence-bundle.yaml`과 `approval-request.yaml`에 함께 남긴다.
- readiness summary 규칙은 기존과 동일하게 `no-linked-clarifications`, `ready`, `attention-needed`만 사용한다.
- readiness는 visibility only다. gate 계산, queue 적재, merge/exception approval 의미, `resolve-approval` semantics를 바꾸지 않는다.
- readiness source artifact를 읽지 못해도 기존 prerequisite 규칙은 그대로 유지하고, readiness 섹션만 제한적으로 `unavailable`로 기록할 수 있다.

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
- latest run은 `runs/latest/*/run.yaml` 중 `updated_at` 우선, 없으면 `created_at` 기준으로 가장 최근 run 1개를 고른다.
- timestamp가 같으면 `run_id`가 더 큰 항목을 고른다.
- active PR가 있으면 status는 linked clarification 기준 source work item readiness context를 함께 읽기 전용으로 보여줄 수 있다.
- readiness summary 규칙은 `work-item-readiness`와 동일하다: linked clarification 없음=`no-linked-clarifications`, 모두 resolved=`ready`, 하나라도 open/deferred/escalated 포함=`attention-needed`
- readiness artifact를 읽는 데 실패해도 status 전체를 막지 않고 readiness 섹션만 제한적으로 `unavailable`로 보여준다.

출력 항목:
- Active PR: `pr_id`, `work_item_id`, 가능하면 active PR artifact path
- Work Item Readiness: active PR 기준 `summary`, `linked_clarifications`, 또는 제한적 unavailable reason
- Latest Run: `run_id`, `state`, 가능하면 run path
- Approval: `status` (`pending`, `approved`, `none`), 가능하면 관련 queue 또는 artifact path
- Approval Queue: visibility only summary from `approval_queue/pending/APR-*.yaml`
  - `pending_total`
  - `latest_run_has_pending` (`True|False`, latest run이 없으면 `unavailable`)
  - `stale_pending_count`
  - `stale_pending_run_ids` 및 `stale_pending_path`
- Open Clarifications: 열려 있는 clarification count와 `clarification_id`
- `resolve-clarification`로 `resolved`, `deferred`, `escalated` 된 항목은 open clarification 목록에서 제외된다.

approval queue visibility 규칙:
- `Approval:` semantics는 그대로 유지하고, 새 `Approval Queue:` 섹션은 filesystem inspection 결과만 추가로 보여준다.
- latest run selector, readiness semantics, queue placement, `build-approval`, `resolve-approval` 동작은 바꾸지 않는다.
- latest run과 일치하지 않는 pending queue item은 stale/non-latest visibility artifact로만 보고하며 자동 정리/숨김/해결하지 않는다.
- latest run이 없으면 새 gate 의미를 만들지 않고 queue visibility만 안전하게 출력한다.

`inspect-approval-queue` 최소 계약:
- `factory inspect-approval-queue`는 `approval_queue/pending/APR-*.yaml`를 item 단위로 읽기 전용 inspection 출력한다.
- latest run 선택 규칙은 `factory status`와 동일하다.
- 항목별로 queue item path, 가능한 경우 parsed `run_id`, latest relation(`latest|stale|no-latest-run|unparseable`), matching run path/state, readiness context presence, degraded note를 보여준다.
- stale/non-latest queue entry는 inspection output only이며 자동 blocker, cleanup, resolve 대상으로 승격하지 않는다.
- matching run이나 source artifact가 없거나 읽기 제한이 있어도 semantics를 바꾸지 않고 degraded note로만 보여준다.

`inspect-run` 최소 계약:
- `factory inspect-run`은 latest run 또는 지정된 run의 execution run 전체를 읽기 전용 inspection 출력한다.
- 선택은 `--latest` 또는 `--run-id <id>`로 하며 latest run 선택 규칙은 `factory status`와 동일하다.
- 출력은 operator-facing visibility only이며 queue eligibility, approval decision, gate 계산, approval lifecycle transition에 영향을 주지 않는다.
- 최소 출력 항목: `run_id`, run path/existence/state, safely derivable latest relation 및 active PR relation, run-related operator artifact presence summary(`review`, `qa`, `docs-sync`, `verification`, `gate-check`, `approval-request`, `evidence-bundle`), degraded note.
- 일부 artifact가 없거나 부분적으로 unreadable이어도 queue mutation, cleanup, auto-hide, auto-resolve 없이 degraded note로만 보여준다.

`inspect-work-item` 최소 계약:
- `factory inspect-work-item`은 `docs/work-items/<work-item-id>.md` work item artifact를 읽기 전용으로 inspection 출력한다.
- 선택은 `--work-item-id <id>`만 지원한다.
- 출력은 operator-facing visibility only다. readiness gating, clarification resolution, planning selection, execution selection, approval decision에 영향을 주지 않는다.
- 최소 출력 항목: `work_item_id`, work item path/existence, title/summary if present, `goal_id` if present, linked clarification identifiers if present, readiness visibility summary/context if readable, metadata timestamp if present, degraded note.
- artifact가 없거나 부분적으로 unreadable이어도 work item mutation, clarification mutation, cleanup, auto-hide, auto-resolve, lifecycle/state transition semantics를 바꾸지 않고 degraded note로만 보여준다.

`inspect-clarification` 최소 계약:
- `factory inspect-clarification`은 clarification artifact 자체를 읽기 전용으로 inspection 출력한다.
- 선택은 `--clarification-id <id>`만 지원한다.
- 출력은 operator-facing visibility only다. clarification resolution, readiness gating, planning selection, execution selection, queue eligibility, approval decision에 영향을 주지 않는다.
- 최소 출력 항목: `clarification_id`, clarification path/existence, title/question/summary if present, `status` if present, linked `goal_id` if present, linked `work_item_id` 목록 if present, metadata timestamp if present, degraded note.
- artifact가 없거나 부분적으로 unreadable이어도 clarification mutation, auto-resolve, cleanup, auto-hide, readiness-to-gate 연결, work item mutation, lifecycle/state transition semantics를 바꾸지 않고 degraded note로만 보여준다.

`inspect-goal` 최소 계약:
- `factory inspect-goal`은 `goals/<goal-id>.md` goal artifact 자체를 읽기 전용으로 inspection 출력한다.
- 선택은 `--goal-id <id>`만 지원한다.
- 출력은 operator-facing visibility only다. clarification resolution, readiness gating, planning selection, execution selection, queue eligibility, approval decision에 영향을 주지 않는다.
- 최소 출력 항목: `goal_id`, goal path/existence, title/summary if present, `status` if present, linked clarification ids if derivable, linked work item ids if derivable, metadata timestamp if present, degraded note.
- artifact가 없거나 부분적으로 unreadable이어도 goal mutation, clarification mutation, work item mutation, auto-resolve, cleanup, auto-hide, readiness-to-gate 연결, planning selection, execution selection, lifecycle/state transition semantics를 바꾸지 않고 degraded note로만 보여준다.

`draft-work-items` 최소 계약:
- 입력: `--root`, `--goal-id`
- 입력 소스: `goals/<goal-id>.md`, official clarification artifacts `clarifications/<goal-id>/*.md`
- 출력 경로: `work_item_drafts/<goal-id>.md`
- draft generation은 deterministic rule-based only다.
- source of truth는 official clarification artifacts이며 `clarification_drafts/`는 입력으로 읽지 않는다.
- official clarification이 없어도 zero-candidate draft artifact는 생성한다.
- 같은 `goal-id` draft artifact가 이미 있거나 goal artifact가 없으면 안전하게 실패한다.
- command는 `docs/work-items/` 아래 official work item artifact를 만들거나 갱신하지 않는다.
- draft는 readiness, approval, queue, selector, active PR, lifecycle semantics를 바꾸지 않는다.

`promote-work-item-draft` 최소 계약:
- 입력: `--root`, `--goal-id`, `--draft-index <n>`, `--work-item-id <id>`
- 전제: `work_item_drafts/<goal-id>.md`가 존재하고 지정한 draft index가 정확히 하나 존재해야 한다.
- 동작: draft의 `title`, `summary`, `source_clarification_id`를 읽어 `docs/work-items/<work-item-id>.md` official artifact 하나를 생성한다.
- 재사용: official artifact 형상은 새로 정의하지 않고 기존 `create-work-item` 경로를 그대로 재사용한다.
- 보존: draft candidate의 `title`은 official `Title`, `summary`는 official `Description`으로 그대로 보존한다.
- linkage: `source_clarification_id`가 있으면 같은 goal 아래 linked clarification context를 official work item에 함께 남긴다.
- 범위: draft file은 삭제하거나 다시 쓰지 않으며 auto-promotion, bulk promotion, readiness, approval, queue, selector, active PR, lifecycle semantics를 바꾸지 않는다.
- 실패: draft artifact가 없거나, draft index가 없거나, target work item id가 이미 존재하면 안전하게 실패한다.

`inspect-pr-plan` 최소 계약:
- `factory inspect-pr-plan`은 PR plan artifact를 읽기 전용으로 inspection 출력한다.
- 선택은 `--active` 또는 `--pr-id <id>`로 하며 `--active`는 기존 active PR semantics를 그대로 재사용한다.
- 출력은 operator-facing visibility only다. active PR switching, planning mutation, readiness gating, execution selection, approval decision에 영향을 주지 않는다.
- 최소 출력 항목: `pr_id`, plan path/existence, active relation, source goal/work item identifiers if present, linked clarification identifiers if present, readiness visibility summary/context if present, created_at 또는 유사 metadata if present, degraded note.
- artifact가 없거나 부분적으로 unreadable이어도 planning lifecycle, queue, resolve, cleanup, auto-hide, auto-resolve semantics를 바꾸지 않고 degraded note로만 보여준다.

`inspect-approval` 최소 계약:
- `factory inspect-approval`는 latest run 또는 지정된 run의 approval package artifact를 읽기 전용으로 inspection 출력한다.
- 선택은 `--latest` 또는 `--run-id <id>`로 하며 latest run 선택 규칙은 `factory status`와 동일하다.
- 출력은 operator-facing visibility only이며 queue eligibility, approval decision, gate 계산, resolve semantics에 영향을 주지 않는다.
- 최소 출력 항목: `run_id`, run artifact path/state, approval request path/existence/status, evidence bundle path/existence, readiness_context summary, degraded note.
- approval request 또는 evidence bundle이 없거나 부분적으로 깨졌어도 자동 복구/cleanup/resolve 없이 degraded note로만 보여준다.

`trace-lineage` 최소 계약:
- `factory trace-lineage`는 지정한 run 기준으로 repo-local orchestration chain의 linked artifact lineage를 읽기 전용으로 추적 출력한다.
- 선택은 `--latest-run` 또는 `--run-id <id>`로 하며 latest run 선택 규칙은 `factory status`와 동일하다.
- 출력은 operator-facing visibility only다. readiness gating, active selection, execution selection, queue eligibility, approval decision, planning/work item mutation, run-state transition semantics에 영향을 주지 않는다.
- 최소 출력 항목:
  - Run: `run_id`, `run_path`, `run_state`
  - Approval: approval request path/status, queue path/status if present
  - PR Plan: `pr_id` if derivable, `plan_path`, `active_relation` if safely derivable
  - Work Item: `work_item_id` if derivable, work item path, readiness visibility if present
  - Goal: `goal_id` if derivable, goal path if safely derivable
  - Clarifications: linked clarification ids if derivable
  - Degraded Notes: missing or partial linkage explanation only
- missing artifact나 old-format artifact가 있어도 실패 대신 degraded note로 제한적으로 설명하며, semantic inference나 lifecycle 변경은 하지 않는다.

operator 해석 규칙:
- `create-pr-plan` 결과가 `archive`면 버그가 아니라 이미 다른 active PR가 있다는 뜻이다.
- `activate-pr`는 semantics를 바꾸지 않고 active/archive 위치만 명시적으로 전환한다.
- `start-execution` guardrail 실패는 lifecycle 버그가 아니라 현재 repo-local 상태를 먼저 정리하라는 안내다.
- `inspect-work-item`은 operator-facing visibility only다. readiness gating, clarification resolution, planning selection, execution selection, approval decision을 바꾸지 않는다.

`work-item-readiness` 최소 계약:
- 입력: `--root`, `--work-item-id`
- 조회 경로: `docs/work-items/<work-item-id>.md`와 linked clarification의 `clarifications/<goal-id>/<clarification-id>.md`
- 출력: `Work Item ID`, `Goal ID`, linked clarification count, clarification별 현재 status, overall readiness summary
- summary 규칙: linked clarification이 없으면 `no-linked-clarifications`, 모두 `resolved`면 `ready`, 하나라도 `open|deferred|escalated`가 있으면 `attention-needed`
- visibility only: 이 summary는 operator 판단 보조용이며 `create-work-item`, `create-pr-plan`, `start-execution`, approval/gate semantics를 바꾸지 않는다.
- 실패: work item 또는 linked clarification artifact를 읽을 수 없으면 경로와 함께 명확히 실패한다.

예시:

```bash
factory status --root .
# active PR가 있으면 source work item readiness summary도 함께 보여줄 수 있다.

factory work-item-readiness --root . --work-item-id WI-020
# linked clarification이 모두 resolved면 ready, 하나라도 open/deferred/escalated면 attention-needed를 읽기 전용으로 보여준다.

factory create-pr-plan --root . --pr-id PR-017 --work-item-id WI-017 --title "operator UX" --summary "clarify active PR flow"
# active PR가 이미 있으면 archive 생성과 함께 다음 activate-pr 예시를 출력한다.
# 성공 출력에는 source work item readiness summary와 linked clarification count도 짧게 포함된다.

factory activate-pr --root . --pr-id PR-017
# 기존 active가 archive로 이동됐는지와 새 active path를 함께 보여준다.

factory start-execution --root . --run-id RUN-017
# active PR가 없거나 여러 개이거나 work item 연결이 깨졌으면, 왜 실패했는지와 다음 명령 예시를 함께 보여준다.
```

## rehearsal cleanup

- `factory cleanup-rehearsal`는 repo-local 운영 baseline 정리를 위한 최소 cleanup 명령이다.
- 기본 동작은 dry-run이며 파일 시스템을 변경하지 않고 제거 대상 경로만 요약 출력한다.
- 실제 삭제는 `--apply`가 있을 때만 수행한다.
- 기본 대상은 공식 rehearsal prefix인 `RH` artifact만이다.
- `--include-demo`를 주면 legacy scratch/demo 흔적인 `DEMO` artifact도 함께 정리한다.
- demo cleanup은 prefix형 `RUN-DEMO-*`뿐 아니라 suffix/infix형 `RUN-*-DEMO*` 및 `APR-RUN-*-DEMO*` naming variant도 포함한다.
- partial cleanup만 허용하며 전체 reset은 제공하지 않는다.
- `docs/prs/` 아래 이력 문서는 cleanup 대상이 아니다.
- `README.md`, `docs/contracts/*`, `docs/adr/*`, 코드, 테스트는 cleanup 대상이 아니다.
- non-rehearsal 실제 이력은 기본적으로 보존한다.

기본 rehearsal 대상:
- `runs/latest/RUN-RH-*`
- `approval_queue/{pending,approved,rejected,exceptions}/APR-RUN-RH-*`
- `goals/GOAL-RH-*`
- `clarifications/GOAL-RH-*`
- `docs/work-items/WI-RH-*`
- `prs/active/PR-RH-*`
- `prs/archive/PR-RH-*`

`--include-demo` 추가 대상:
- `runs/latest/RUN-DEMO-*`
- `runs/latest/RUN-*-DEMO*`
- `approval_queue/{pending,approved,rejected,exceptions}/APR-RUN-DEMO-*`
- `approval_queue/{pending,approved,rejected,exceptions}/APR-RUN-*-DEMO*.yaml`
- `goals/*DEMO*`
- `clarifications/*DEMO*`
- `docs/work-items/*DEMO*`
- `prs/active/*DEMO*`
- `prs/archive/*DEMO*`

예시:

```bash
factory cleanup-rehearsal --root .
factory cleanup-rehearsal --root . --apply
factory cleanup-rehearsal --root . --apply --include-demo
```

## 주요 경로

- 오케스트레이터: `orchestrator/`
- Goal artifact: `goals/<goal-id>.md`
- Clarification artifact: `clarifications/<goal-id>/<clarification-id>.md`
- Clarification draft artifact: `clarification_drafts/<goal-id>.md`
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
- source work item readiness context를 read-only로 읽어 PR plan markdown에 함께 남긴다.
- PR plan에는 최소 `Work Item Readiness`, `Linked Clarifications` 섹션이 포함되며 linked clarification이 없으면 `- none`으로 기록한다.
- readiness summary 규칙은 `work-item-readiness`와 동일하다: linked clarification 없음=`no-linked-clarifications`, 모두 resolved=`ready`, 하나라도 open/deferred/escalated 포함=`attention-needed`
- readiness는 visibility only다. `attention-needed`여도 PR plan 생성은 허용되며 activation/start-execution/gate/approval semantics를 바꾸지 않는다.
- linked clarification artifact가 누락된 work item이면 `work-item-readiness`와 같은 안전한 실패 규칙을 따른다.
- 성공 출력은 기존 CLI tone을 유지하면서 readiness summary와 linked clarification count를 짧게 함께 보여준다.

`draft-clarifications` 최소 계약:
- 입력: `goals/<goal-id>.md`
- 출력: `clarification_drafts/<goal-id>.md`
- 명령: `factory draft-clarifications --root <repo> --goal-id <goal-id>`
- 방식: deterministic rule-based markdown generation only
- 실패: goal artifact가 없거나 같은 goal-id draft artifact가 이미 있으면 안전하게 실패한다.
- 의미론: official clarification queue artifact는 만들지 않고, readiness/approval/queue/selector/lifecycle semantics도 바꾸지 않는다.
- 승격: operator가 필요하다고 판단한 항목만 `factory promote-clarification-draft` 또는 `factory create-clarification`으로 수동 생성한다.

`promote-clarification-draft` 최소 계약:
- 입력: `--root`, `--goal-id`, `--draft-index <n>`, `--clarification-id <id>`
- 전제: `clarification_drafts/<goal-id>.md`가 존재하고 지정한 draft index가 정확히 하나 존재해야 한다.
- 동작: draft의 question/category/title/escalation을 읽어 `clarifications/<goal-id>/<clarification-id>.md`를 정확히 하나 생성한다.
- 보존: official artifact는 draft의 question, category, rationale(`source_rule`)를 보존하고 draft file path와 draft index provenance를 함께 기록한다.
- 범위: draft file은 삭제하거나 다시 쓰지 않으며, readiness/approval/queue/selector/lifecycle semantics를 바꾸지 않는다.
- 실패: draft artifact가 없거나, draft index가 없거나, target clarification id가 이미 존재하면 안전하게 실패한다.

`promote-work-item-draft` 최소 계약:
- 입력: `--root`, `--goal-id`, `--draft-index <n>`, `--work-item-id <id>`
- 전제: `work_item_drafts/<goal-id>.md`가 존재하고 지정한 draft index가 정확히 하나 존재해야 한다.
- 동작: draft의 title/summary를 읽어 `docs/work-items/<work-item-id>.md` 하나를 생성한다.
- 보존: source clarification id가 있으면 official work item의 linked clarification context도 함께 보존한다.
- 재사용: official artifact는 새 shape를 만들지 않고 기존 `create-work-item` 경로로 생성한다.
- 범위: draft file은 삭제하거나 다시 쓰지 않으며 auto-promotion, bulk promotion, readiness/approval/queue/selector/active PR/lifecycle semantics를 바꾸지 않는다.
- 실패: draft artifact가 없거나, draft index가 없거나, target work item id가 이미 존재하면 안전하게 실패한다.

`resolve-clarification` 최소 계약:
- 입력: `--root`, `--goal-id`, `--clarification-id`, `--decision <resolved|deferred|escalated>`, `--resolution-notes`, `--next-action`, 선택적 `--suggested-resolution`
- 전제: `clarifications/<goal-id>/<clarification-id>.md`가 존재하고 `Status=open` 이어야 한다.
- 동작: 기존 clarification Markdown 형식을 유지한 채 `Status`, `Resolution Notes`, `Next Action`, `Escalation Required`를 갱신한다.
- 규칙: `decision=escalated`면 `Escalation Required=yes`, 나머지는 `no`로 기록한다.
- 범위: clarification artifact 상태만 갱신하며 goal/work-item/pr/run/approval 상태는 자동 변경하지 않는다.
- 실패: artifact가 없거나 이미 open이 아니면, 경로와 다음 action을 함께 보여주며 안전하게 실패한다.

`create-work-item` 최소 계약:
- 입력: `--root`, `--work-item-id`, `--title`, `--goal-id`, `--description`, 선택적 `--acceptance-criteria`, 반복 가능한 `--clarification-id <id>`
- 기존 계약: `--clarification-id`를 생략하면 기존 work item 생성 동작을 그대로 유지한다.
- linkage 규칙: 지정한 clarification은 모두 `clarifications/<goal-id>/<clarification-id>.md` 아래에서 찾는다.
- validation: clarification이 없으면 실패하고, 같은 `clarification-id`가 다른 goal 아래만 있으면 goal mismatch를 설명하며 실패한다.
- artifact: Work Item 문서에 `Related Clarifications` 섹션을 추가하고 `- <clarification-id> (<status>)` 형식으로 기록한다.
- no-linkage 표기: clarification을 지정하지 않으면 `Related Clarifications`는 `- none`으로 기록한다.
- 범위 제한: unresolved clarification을 자동 차단하지 않으며, planner/resolver/recommendation automation은 추가하지 않는다.

`work-item-readiness` 최소 계약:
- 입력: `--root`, `--work-item-id`
- 전제: `docs/work-items/<work-item-id>.md`가 존재해야 한다.
- 동작: work item의 `Goal ID`, `Related Clarifications`를 읽고 linked clarification artifact의 현재 `Status`를 다시 조회해 짧은 readiness summary를 출력한다.
- summary 규칙: linked clarification 없음=`no-linked-clarifications`, 모두 resolved=`ready`, 하나라도 open/deferred/escalated 포함=`attention-needed`
- 범위 제한: visibility-only 명령이며 work item/pr/run/approval semantics, 허용/차단, 자동 resolution은 바꾸지 않는다.
- 실패: work item 또는 linked clarification artifact가 없으면 안전하게 실패한다.

`start-execution` 최소 계약:
- 입력: `--root`, `--run-id`
- 전제: `prs/active/` 아래 active PR plan이 정확히 하나여야 한다.
- 전제: active PR plan의 `Work Item ID`가 `docs/work-items/` 아래 실제 work item artifact와 정확히 연결되어야 한다.
- 동작: active PR plan에서 `pr_id`, `work_item_id`, `title`을 읽고 기존 `bootstrap-run` 흐름 위에 run을 시작한다.
- 기록: `runs/latest/<run-id>/run.yaml`과 `artifacts/{pr-plan,work-item}.yaml`에 최소 `run_id`, `pr_id`, `work_item_id`, `pr_plan_path`, `work_item_path`가 식별 가능하게 남고 `run.yaml.state=in_progress`로 갱신된다.
- 실패: active PR plan이 0개이거나 2개 이상이거나, work item 연결이 불가하면 안전하게 실패한다.

run-scoped 명령의 `--latest` 최소 계약:
- 대상 명령: `record-review`, `record-qa`, `record-docs-sync`, `record-verification`, `gate-check`, `build-approval`, `resolve-approval`, `inspect-approval`, `inspect-run`
- 입력: 각 명령은 기존 `--run-id <id>`를 그대로 지원하고, 같은 위치에서 `--latest`를 대안으로 지원한다.
- 배타성: `--run-id`와 `--latest`를 함께 주면 명확히 실패한다.
- 기본 계약: 둘 다 없으면 기존처럼 run selector가 필요하므로 실패한다.
- 선택 규칙: `--latest`는 `factory status`와 동일하게 `runs/latest/*/run.yaml`에서 latest run 1개를 고른다.
- 실패: latest run이 없으면 `inspect-approval`, `inspect-run`은 degraded visibility output을 반환하고, 나머지 명령은 `start-execution` 또는 명시적 `--run-id`가 필요하다고 안내하며 실패한다.
- 주의: `--latest`는 run-id 입력을 줄이는 convenience 계층일 뿐이며, artifact prerequisite 계약을 우회하지 않는다.

`build-approval` 최소 계약:
- 전제: `verification-report.yaml`, `review-report.yaml`, `qa-report.yaml`, `docs-sync-report.yaml`가 모두 존재하고 실제 record 명령으로 기록돼 있어야 한다.
- 실패: prerequisite artifact가 없거나 아직 placeholder 상태면 누락된 record 명령을 명확히 보여주며 실패한다.
- 상태: 승인 패키지를 만들면 `run.yaml.state=approval_pending`으로 갱신된다.
- 출력 artifact인 `evidence-bundle.yaml`, `approval-request.yaml`는 가능하면 source work item readiness context를 visibility-only로 포함한다.
- 최소 readiness context는 `readiness_summary`, `linked_clarification_count`, 가능하면 linked clarification status 요약, `readiness_source`(`work_item_id`, `pr_id`)다.
- readiness를 읽지 못해도 `build-approval` 전체 prerequisite/queue semantics는 바뀌지 않으며 readiness만 제한적으로 `unavailable` 처리할 수 있다.

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
factory draft-clarifications --root . --goal-id GOAL-LOCAL
factory promote-clarification-draft --root . --goal-id GOAL-LOCAL --draft-index 1 --clarification-id CLAR-001
factory create-clarification --root . --goal-id GOAL-LOCAL --clarification-id CLAR-001 --title "scope boundary" --category scope --question "What must stay out of scope for this goal?"
factory resolve-clarification --root . --goal-id GOAL-LOCAL --clarification-id CLAR-001 --decision resolved --resolution-notes "Scope boundary confirmed by operator review" --next-action "Proceed to work item drafting"
factory draft-work-items --root . --goal-id GOAL-LOCAL
factory promote-work-item-draft --root . --goal-id GOAL-LOCAL --draft-index 1 --work-item-id WI-LOCAL
factory create-work-item --root . --work-item-id WI-LOCAL-MANUAL --title "local work item" --goal-id GOAL-LOCAL --description "Create a minimal work item artifact" --clarification-id CLAR-001 --acceptance-criteria $'- docs/work-items/WI-LOCAL-MANUAL.md exists\n- Duplicate IDs fail safely'
factory create-pr-plan --root . --pr-id PR-LOCAL --work-item-id WI-LOCAL --title "local PR plan" --summary "Track the single active PR plan as a repo-local Markdown artifact"
factory activate-pr --root . --pr-id PR-LOCAL
factory start-execution --root . --run-id RUN-LOCAL
factory record-review --root . --latest --status pass --summary "review ok"
factory record-qa --root . --latest --status pass --summary "qa ok"
factory record-docs-sync --root . --latest --status complete --summary "docs aligned"
factory record-verification --root . --latest --lint pass --tests pass --type-check pass --build pass --summary "all checks green"
factory gate-check --root . --latest
factory build-approval --root . --latest
factory resolve-approval --root . --latest --decision approve --actor approver.local --note "all gates satisfied"
```

`--latest` 대신 언제든 기존 `--run-id RUN-LOCAL` 방식을 그대로 사용할 수 있다.

## 다음 단계 후보 (MVP 이후)

1. Goal clarification loop
2. clarification resolution loop
3. Goal to Work Item linkage hardening
4. WI auto-generation

`bootstrap-run`은 제거되지 않았다. 현재는 `activate-pr`로 active PR를 명시적으로 전환한 뒤 `start-execution`이 그 active PR plan을 읽어 실행을 시작하는 공식 entrypoint이고, `bootstrap-run`은 그 아래의 run bootstrap 기반 명령으로 유지된다.
