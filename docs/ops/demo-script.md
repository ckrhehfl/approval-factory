# Demo Script

이 데모는 반자동 repo-local MVP의 최소 승인 루프를 재실행 가능하게 보여준다.

## 0) 변수 설정

```bash
RUN_ID="RUN-DEMO-001"
WI_ID="WI-005"
PR_ID="PR-005"
```

## 1) bootstrap-run

```bash
factory bootstrap-run \
  --root . \
  --run-id "$RUN_ID" \
  --work-item-id "$WI_ID" \
  --work-item-title "mvp finish docs and ops" \
  --pr-id "$PR_ID"
```

## 2) record-review

```bash
factory record-review \
  --root . \
  --run-id "$RUN_ID" \
  --status pass \
  --summary "review passed for MVP demo"
```

## 3) record-qa

```bash
factory record-qa \
  --root . \
  --run-id "$RUN_ID" \
  --status pass \
  --summary "qa passed for MVP demo"
```

## 4) record-docs-sync

```bash
factory record-docs-sync \
  --root . \
  --run-id "$RUN_ID" \
  --status complete \
  --summary "docs are aligned"
```

## 5) record-verification

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

## 6) gate-check

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

## 7) build-approval

```bash
factory build-approval --root . --run-id "$RUN_ID"
```

확인:

```bash
sed -n '1,220p' "runs/latest/$RUN_ID/artifacts/approval-request.yaml"
sed -n '1,220p' "runs/latest/$RUN_ID/artifacts/evidence-bundle.yaml"
```

## 8) approval_queue 확인

```bash
find approval_queue/pending -maxdepth 1 -type f -name "APR-$RUN_ID*.yaml" | sort
```

## 9) resolve-approval

```bash
factory resolve-approval \
  --root . \
  --run-id "$RUN_ID" \
  --decision approve \
  --actor "approver.local" \
  --note "all merge prerequisites satisfied"
```

확인:

```bash
sed -n '1,220p' "runs/latest/$RUN_ID/artifacts/approval-decision.yaml"
find approval_queue/approved -maxdepth 1 -type f -name "APR-$RUN_ID*.yaml" | sort
find approval_queue/pending -maxdepth 1 -type f -name "APR-$RUN_ID*.yaml" | sort
```

## 참고: queue 적재 조건

- docs-sync 상태가 `complete` 또는 `not-needed`
- merge gate가 `ready` 또는 `exception_required`

## 참고: pending 이후 운영 (현재 MVP)

- 승인자는 `approval_queue/pending/APR-<run-id>.yaml`와 run artifact를 보고 결정을 내린다.
- 결정 반영은 `factory resolve-approval`로 수행한다.
