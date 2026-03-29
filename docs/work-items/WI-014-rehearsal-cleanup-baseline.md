# WI-014: rehearsal cleanup baseline normalization

## input refs

- AGENTS.md (v1, repo local)
- README.md (current)
- docs/ops/runbook.md (current)
- docs/ops/how-we-work.md (current)
- orchestrator/cli.py (current)
- orchestrator/pipeline.py (current)
- tests/test_cli.py (current)

## scope

- repo-local 운영 baseline 정리를 위한 `factory cleanup-rehearsal` 최소 명령을 추가한다.
- 기본 cleanup 범위는 공식 rehearsal prefix `RH` artifact만으로 제한한다.
- `--include-demo`가 있을 때만 legacy scratch/demo prefix `DEMO` artifact를 추가 cleanup 한다.
- dry-run 기본값, `--apply` 실제 삭제, 대상 path 수집 후 summary 출력 계약을 명시한다.
- `docs/prs/` 이력 문서와 non-rehearsal 실제 이력은 기본적으로 보존한다.
- `factory status`가 stale rehearsal/demo active PR 또는 open clarification을 남기지 않도록 검증한다.

## output summary

- 기능 확장 전에 rehearsal/demo 리허설 흔적만 부분 정리할 수 있는 repo-local cleanup baseline 추가
- 전체 reset 대신 partial cleanup만 허용하는 운영 계약과 보호 규칙 문서화
- RH는 공식 rehearsal prefix, DEMO는 legacy scratch artifact라는 의미를 CLI/문서/테스트에 반영
- 다음 기능 PR 전에 baseline normalization을 안전하게 수행할 수 있는 최소 guardrail 확보

## risks

- glob 범위가 넓으면 실제 이력을 지울 수 있으므로 prefix와 경로를 엄격히 제한해야 한다.
- dry-run/apply 동작이 섞이면 운영자가 예상하지 못한 삭제를 경험할 수 있으므로 기본값을 dry-run으로 유지해야 한다.
- status가 stale artifact를 캐시하지는 않지만, cleanup 범위가 불완전하면 stale active PR/open clarification이 남을 수 있다.

## next required gate

- review
