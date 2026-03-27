# PR-005 Plan

## input refs

- README.md
- AGENTS.md
- docs/ops/runbook.md
- docs/prs/README.md
- docs/work-items/*
- orchestrator/cli.py
- orchestrator/pipeline.py
- tests/*
- config/gates.yaml
- runs/latest artifacts
- approval_queue structure

## scope

- 현재 구현 상태를 기준으로 운영/가이드 문서를 정리한다.
- 새 기능, 새 gate 로직, 새 CLI 명령은 추가하지 않는다.

## output summary

- README를 현재 MVP 범위와 실제 CLI 흐름 기준으로 갱신
- ops 문서(`how-we-work`, `mvp-checklist`, `demo-script`) 추가
- WI-005 문서 생성

## risks

- 문서가 코드보다 앞서가면 운영 오해가 발생할 수 있다.
- run 샘플의 과거 이력(verification artifact 미존재 케이스)을 현재 기준으로 일반화하면 안 된다.

## next required gate

- review
