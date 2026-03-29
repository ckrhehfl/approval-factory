# Approval Request Contract

Approval Request는 인간이 판단해야 할 정보를 구조화한 문서다.

## 필수 항목

- 어떤 gate인지
- 무엇을 바꿨는지
- 왜 필요한지
- 어떤 검증을 통과했는지
- 어떤 리스크가 남았는지
- 어떤 문서가 바뀌었는지
- 추천 결정
- 가능하면 source PR/work item readiness context visibility

## 규칙

- raw log만 붙이고 요약이 없으면 무효
- evidence bundle 링크가 없으면 무효
- 예외가 있으면 명시적으로 표기해야 한다
- `build-approval`가 readiness context를 읽을 수 있으면 `readiness_context`에 `readiness_summary`, `linked_clarification_count`, 가능하면 linked clarification status 요약, `readiness_source`를 함께 남길 수 있다.
- readiness summary 규칙은 `no-linked-clarifications|ready|attention-needed`만 사용한다.
- readiness는 informational only다. approval request에 포함돼도 merge/exception gate 계산, queue 적재, resolve-approval semantics를 바꾸지 않는다.
- readiness를 읽지 못해도 approval request 핵심 필드는 유지되어야 하며, 이 경우 `readiness_context.status=unavailable`로 제한적으로 표현할 수 있다.
