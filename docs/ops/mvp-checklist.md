# MVP Checklist

## MVP 완료 조건

1. repo-local file-based 실행 루프가 재현 가능해야 한다.
2. one-PR-at-a-time 운영이 문서/구조/명령에서 일관돼야 한다.
3. approval-first 흐름이 gate + evidence + approval-request로 연결돼야 한다.
4. record/gate/build 재실행이 idempotent하게 동작해야 한다.
5. 코드-문서 동기화 판단 지점이 운영 절차에 포함돼야 한다.

## 현재 충족 상태

- [x] `factory` CLI로 bootstrap/record/gate/build 명령 실행 가능
- [x] canonical artifact 경로(`runs/latest/<run-id>/artifacts/*.yaml`) 고정
- [x] review/qa/docs-sync/verification 결과를 gate/evidence/approval에 반영
- [x] approval queue file 기반 적재 및 중복/충돌 처리(`APR-<run-id>.yaml`, `--r2`)
- [x] run operation 카운트로 재실행 이력 추적
- [x] 문서 기반 계약(AGENTS, contracts, ops, prs/work-items 경로) 유지

## 남은 비범위 (이번 MVP에서 하지 않음)

- Goal intake 자동화
- UI
- central control plane
- multi-project orchestration

## 완료 판정

현재 상태는 repo-local approval factory MVP의 완료 후보로 판정한다. 남은 작업은 기능 확장이 아니라 운영 정밀화와 다음 단계 설계다.
