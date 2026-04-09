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

## Related Assist Surface

- `factory suggest-next-pr`는 status와 같은 repo-local visibility inputs를 읽되, 별도의 assist-only surface로 `Short State Block`과 `Minimum Execution Packet`만 출력한다.
- active PR가 정확히 하나 있으면 새 PR 자동 제안 대신 assist-only continuation packet만 출력한다.
- `prs/active/`에 active PR plan이 여러 개 있으면 ambiguous active PR state를 명시적으로 surface하고 hard-stop한다.
- active PR가 없으면 repo와 현재 branch에서 관찰되는 numeric PR id 범위를 기준으로 다음 unused PR id/branch를 assist-only로 제안할 수 있다.
- 현재 branch는 continuity context only이며 suggested next PR identity와 같은 의미로 쓰지 않는다.
- single-active continuation packet은 `active_pr_id`, active PR context/path, `work_scope` 1~2개, `validation_command`, `closeout_log_format`만 포함한다.
- no-active packet은 기존처럼 `branch_name`, `work_scope` 1~2개, `validation_command`, `closeout_log_format`만 포함한다.
- 이 assist surface도 read-only다. full pack, branch 생성, run 생성, queue mutation, selector semantics, approval/review semantics를 만들지 않는다.
- ambiguous active PR state를 보여주더라도 auto-select, cleanup, recovery semantics는 만들지 않는다.
