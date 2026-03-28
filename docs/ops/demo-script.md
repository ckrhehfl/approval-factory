# Demo Script

이 데모는 반자동 repo-local MVP의 최소 승인 루프를 재실행 가능하게 보여준다.

## 0) 변수 설정

```bash
GOAL_ID="GOAL-007-DEMO"
CLAR_ID="CLAR-001"
WI_ID="WI-010-DEMO"
RUN_ID="RUN-DEMO-001"
PR_ID="PR-005"
```

## 1) create-goal

```bash
factory create-goal \
  --root . \
  --goal-id "$GOAL_ID" \
  --title "goal intake demo" \
  --problem "A human needs a formal repo-local way to register a project goal." \
  --outcome "A readable goal artifact exists under goals/." \
  --constraints "repo-local\nfile-based"
```

확인:

```bash
sed -n '1,220p' "goals/$GOAL_ID.md"
```

주의:
- 현재 Goal intake는 artifact 생성만 다룬다.
- 자동 질문 생성, goal 해결, WI 자동 분해는 아직 없다.

## 2) create-clarification

```bash
factory create-clarification \
  --root . \
  --goal-id "$GOAL_ID" \
  --clarification-id "$CLAR_ID" \
  --title "scope boundary for demo" \
  --category scope \
  --question "What is explicitly out of scope before planning starts?" \
  --escalation
```

확인:

```bash
sed -n '1,220p' "clarifications/$GOAL_ID/$CLAR_ID.md"
```

주의:
- clarification queue는 Goal intake 다음의 최소 질문 관리 계층이다.
- 자동 질문 생성, 자동 해결, resolver/planner 구현은 아직 없다.

## 3) create-work-item

```bash
factory create-work-item \
  --root . \
  --work-item-id "$WI_ID" \
  --title "goal to work item demo" \
  --goal-id "$GOAL_ID" \
  --description "Create the minimum repo-local Work Item contract that links Goal intake to a PR-sized execution unit." \
  --acceptance-criteria $'- docs/work-items/'"$WI_ID"'.md exists\n- Duplicate work-item IDs fail safely\n- No auto decomposition is performed'
```

확인:

```bash
sed -n '1,220p' "docs/work-items/$WI_ID.md"
```

주의:
- Work Item은 Goal/clarification을 실제 PR 실행 단위로 연결하는 수동 Markdown artifact다.
- 자동 decomposition, clarification 강한 연결, planner 자동화는 아직 없다.

## 4) create-pr-plan

```bash
factory create-pr-plan \
  --root . \
  --pr-id "$PR_ID" \
  --work-item-id "$WI_ID" \
  --title "single active PR demo" \
  --summary "Create the minimum repo-local active PR plan artifact for the current Work Item."
```

확인:

```bash
sed -n '1,220p' "prs/active/$PR_ID.md"
```

주의:
- `prs/active/`는 항상 0 또는 1개의 PR plan만 가진다.
- active PR가 없으면 `create-pr-plan`은 active에 만들고, 이미 있으면 archive 후보를 만든다.
- archive 이동, PR close/merge lifecycle, multi-PR 관리, planner automation은 아직 없다.

## 5) activate-pr

active PR를 archive에서 다시 선택해야 할 때는 먼저 아래처럼 전환한다.

```bash
factory activate-pr \
  --root . \
  --pr-id "$PR_ID"
```

주의:
- `activate-pr`는 PR-011 execution flow 보강용 최소 전환 단계다.
- 기존 active PR이 있으면 `prs/archive/`로 이동하고, 지정한 PR plan이 active가 된다.

## 6) start-execution

```bash
factory start-execution \
  --root . \
  --run-id "$RUN_ID"
```

확인:

```bash
sed -n '1,220p' "runs/latest/$RUN_ID/run.yaml"
sed -n '1,220p' "runs/latest/$RUN_ID/artifacts/pr-plan.yaml"
```

주의:
- `start-execution`은 `prs/active/`의 단일 active PR plan을 읽어 run을 시작하는 공식 entrypoint다.
- active PR plan의 `Work Item ID`가 `docs/work-items/` 아래 실제 artifact와 연결되지 않으면 시작 전에 실패한다.
- active PR를 명시적으로 바꾼 뒤 실행해야 하면 `activate-pr`를 먼저 사용한다.
- review/qa/docs-sync/verification 자동 실행은 하지 않는다.
- `bootstrap-run`은 내부 기반 명령으로 유지되지만, active PR plan에서 실행을 시작할 때는 `start-execution`을 사용한다.

## 7) record-review

```bash
factory record-review \
  --root . \
  --run-id "$RUN_ID" \
  --status pass \
  --summary "review passed for MVP demo"
```

## 8) record-qa

```bash
factory record-qa \
  --root . \
  --run-id "$RUN_ID" \
  --status pass \
  --summary "qa passed for MVP demo"
```

## 9) record-docs-sync

```bash
factory record-docs-sync \
  --root . \
  --run-id "$RUN_ID" \
  --status complete \
  --summary "docs are aligned"
```

## 10) record-verification

```bash
factory record-verification \
  --root . \
  --run-id "$RUN_ID" \
  --lint pass \
  --tests pass \
  --type-check pass \
  --build pass \
  --summary "all checks green"
```

## 11) gate-check

```bash
factory gate-check --root . --run-id "$RUN_ID"
```

확인:

```bash
sed -n '1,200p' "runs/latest/$RUN_ID/artifacts/gate-status.yaml"
```

주의:
- `gate-check`는 gate 판정만 갱신한다.
- 최종 승인 요청 판단은 다음 단계 `build-approval` 산출물 기준으로 한다.

## 11) build-approval

```bash
factory build-approval --root . --run-id "$RUN_ID"
```

확인:

```bash
sed -n '1,220p' "runs/latest/$RUN_ID/artifacts/approval-request.yaml"
sed -n '1,220p' "runs/latest/$RUN_ID/artifacts/evidence-bundle.yaml"
```

주의:
- `build-approval`는 `record-review`, `record-qa`, `record-docs-sync`, `record-verification`이 모두 실제로 기록된 뒤에만 동작한다.
- placeholder artifact만 있는 상태에서 실행하면 누락된 record 명령을 알려주며 실패한다.

## 12) approval_queue 확인

```bash
find approval_queue/pending -maxdepth 1 -type f -name "APR-$RUN_ID*.yaml" | sort
```

## 13) resolve-approval

```bash
factory resolve-approval \
  --root . \
  --run-id "$RUN_ID" \
  --decision approve \
  --actor "approver.local" \
  --note "all merge prerequisites satisfied"
```

주의:
- `resolve-approval`는 `build-approval`로 채워진 `approval-request.yaml`와 `approval_queue/pending/APR-$RUN_ID.yaml`가 둘 다 있어야 한다.
- pending queue item이 없으면 승인 결정은 기록되지 않는다.

확인:

```bash
sed -n '1,220p' "runs/latest/$RUN_ID/artifacts/approval-decision.yaml"
find approval_queue/approved -maxdepth 1 -type f -name "APR-$RUN_ID*.yaml" | sort
find approval_queue/pending -maxdepth 1 -type f -name "APR-$RUN_ID*.yaml" | sort
```

## 참고: queue 적재 조건

- docs-sync 상태가 `complete` 또는 `not-needed`
- merge gate가 `ready` 또는 `exception_required`

## 참고: run state

- `draft`: bootstrap만 된 상태
- `in_progress`: execution 진행 중
- `approval_pending`: 승인 패키지 생성 후 승인 대기
- `approved`: 승인 완료

## 참고: pending 이후 운영 (현재 MVP)

- 승인자는 `approval_queue/pending/APR-<run-id>.yaml`와 run artifact를 보고 결정을 내린다.
- 결정 반영은 `factory resolve-approval`로 수행한다.
