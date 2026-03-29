# Evidence Bundle Contract

Evidence Bundle은 승인자를 위해 검증 자료를 요약한 패키지다.

## 필수 포함

- lint 결과
- tests 결과
- type_check 결과
- build 결과
- review 핵심 발견사항
- qa 핵심 발견사항
- docs sync 판정
- 잔여 리스크
- 가능하면 source PR/work item readiness context visibility

## 규칙

- “통과함”만 적지 말고 근거를 남긴다.
- 실패가 있으면 영향과 완화 계획을 함께 적는다.
- 승인자는 이 문서만으로 1차 판단이 가능해야 한다.
- `build-approval`가 readiness context를 읽을 수 있으면 `readiness_context`에 `readiness_summary`, `linked_clarification_count`, 가능하면 linked clarification status 요약, `readiness_source`를 함께 남길 수 있다.
- readiness summary 규칙은 `no-linked-clarifications|ready|attention-needed`만 사용한다.
- readiness는 visibility only다. evidence bundle에 포함돼도 gate 계산, queue 적재, approval 가능/불가 semantics를 바꾸지 않는다.
- source work item readiness를 읽지 못하면 evidence bundle 전체를 무효화하지 않고 `readiness_context.status=unavailable`과 제한적 reason만 남길 수 있다.
