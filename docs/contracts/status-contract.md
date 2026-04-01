# Status Contract

`factory status`는 현재 repo-local 운영 상태를 읽기 전용으로 요약하는 최소 상태 조회 명령이다.

## 조회 경로

- `prs/active/*.md`
- `runs/latest/*/run.yaml`
- `approval_queue/approved/`
- `approval_queue/pending/`
- `runs/latest/<run-id>/artifacts/approval-decision.yaml`
- `clarifications/*/*.md`

## 출력 섹션

- Active PR
- Work Item Readiness
- Latest Run
- Approval
- Open Clarifications

## 규칙

- 이 명령은 어떤 artifact도 생성, 수정, 이동하지 않는다.
- active PR가 없으면 `Work Item Readiness` 섹션은 생략할 수 있다.
- active PR가 있으면 status는 해당 PR의 `Work Item ID`를 기준으로 source work item readiness context를 함께 보여줄 수 있다.
- readiness summary 규칙은 `factory work-item-readiness`와 동일하게 `no-linked-clarifications|ready|attention-needed` 이다.
- linked clarification count는 현재 clarification artifact를 다시 읽은 결과를 기준으로 표시할 수 있다.
- readiness는 visibility only다. status 출력은 create-pr-plan, activate-pr, start-execution, gate, approval semantics를 바꾸지 않는다.
- readiness artifact를 읽는 중 문제가 생기면 status 전체를 실패시키지 않고 readiness 섹션만 제한적으로 `unavailable`로 표시할 수 있다.
- latest pending approval이 현재 approval target이다.
- 더 오래된 pending approval은 stale artifact로 계속 보일 수 있다.
- stale pending artifact는 자동 삭제, 자동 resolve, 자동 숨김 대상이 아니다.
- status 출력은 operator visibility다. queue lifecycle, selector logic, readiness semantics를 바꾸지 않는다.
- status에 보이는 path나 요약은 selector semantics가 아니다.
- active PR, latest run, approval이 없으면 각 섹션에서 `none`으로 보여준다.
