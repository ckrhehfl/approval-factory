# Domain Model

## WorkItem
요구 단위다.

주요 필드:
- id
- title
- problem
- goal
- non_goals
- acceptance_criteria
- constraints
- risks
- approver
- status

## PRPlan
PR 단위 실행 계획이다.

주요 필드:
- pr_id
- scope
- input_refs
- files_to_change
- acceptance_criteria
- test_plan
- docs_sync_impact
- risks

## ApprovalRequest
인간 승인을 요청하는 패키지다.

주요 필드:
- id
- work_item_id
- pr_id
- gate_type
- decision_required
- summary
- checks
- risks
- exceptions
- changed_docs
- evidence_bundle

## EvidenceBundle
승인 판단에 필요한 검증 자료다.

주요 필드:
- checks
- review_findings
- qa_findings
- sample_outputs
- docs_sync
- residual_risks

## ADRReference
구조적 의사결정 연결 정보다.

주요 필드:
- adr_id
- status
- title
- affected_docs

## GateDecision
승인자의 결정 기록이다.

주요 필드:
- gate_type
- decision
- rationale
- exceptions_accepted
- approved_by
- approved_at
