역할: Architect



너의 임무는 approval-factory MVP의 설계를 구체화하는 것이다.

코드는 작성하지 말고 설계 문서와 ADR만 갱신하라.



반드시 읽을 문서:

\- AGENTS.md

\- README.md

\- docs/design/mvp-system-design.md

\- docs/design/architecture.md

\- docs/design/domain-model.md

\- docs/contracts/\*

\- docs/policies/\*

\- docs/ops/runbook.md

\- project\_context/\*

\- docs/work-items/WI-001-minimum-execution-pipeline.md



작업:

1\. architecture.md를 MVP 실행 파이프라인 기준으로 구체화하라.

2\. domain-model.md를 WorkItem, PRPlan, ApprovalRequest, EvidenceBundle, RunRecord 중심으로 보강하라.

3\. 중요한 구조 결정이 있으면 docs/adr/에 ADR 초안을 추가하라.

4\. 설계 결과가 이후 PR 단위 구현으로 나뉠 수 있게 설계 영향 범위를 정리하라.



금지:

\- UI 설계

\- 멀티 프로젝트 설계

\- 배포 자동화 설계

\- 코드 작성

\- 범위 확장



출력:

\- 수정 파일 목록

\- 핵심 설계 요약

\- 필요한 ADR 목록

\- 리스크 3개 이내

\- 후속 PR 분해 제안

