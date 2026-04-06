# PR-071 Plan

## input refs
- AGENTS.md working-copy version observed on 2026-04-04
- User task for PR-071 small read-only/operator-assist change
- `factory status --root .`
- `PYTHONPATH=. python -m factory inspect-approval-queue --root .`
- `git status -sb`
- `git --no-pager log --oneline -n 5`
- [orchestrator/pipeline.py](/orchestrator/pipeline.py)
- [orchestrator/cli.py](/orchestrator/cli.py)
- [tests/test_cli.py](/tests/test_cli.py)
- [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml)
- [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml)

## scope
- PR-071 adds only `matching_pr_id` visibility to `inspect-approval-queue` pending item output.
- The change is read-only assist only and reads from existing matching run metadata.
- Queue mutation, approval mutation, readiness gating, cleanup semantics, and Relation Summary semantics remain unchanged.
- PR-071 leaves this plan note at [docs/prs/PR-071/plan.md](/docs/prs/PR-071/plan.md).

## output summary
- Extend approval queue inspection item payload/rendering with `matching_pr_id` when a matching run exists and exposes `pr_id`.
- Preserve the existing output shape and append only the new field.
- Keep non-destructive behavior when the run is missing, unreadable, or lacks a parseable `pr_id`.
- Add focused CLI coverage for the new field and unchanged fallback behavior.

## current repo snapshot
- `factory status --root .` reports latest run `RUN-20260327T063724Z`, pending total `2`, and one stale pending item.
- `PYTHONPATH=. python -m factory inspect-approval-queue --root .` reports stale `RUN-20260327T055614Z` and latest `RUN-20260327T063724Z`.
- [runs/latest/RUN-20260327T055614Z/run.yaml](/runs/latest/RUN-20260327T055614Z/run.yaml) records `pr_id: PR-003`.
- [runs/latest/RUN-20260327T063724Z/run.yaml](/runs/latest/RUN-20260327T063724Z/run.yaml) records `pr_id: PR-004`.
- This is operator visibility assist for the case where stale and latest can belong to different PRs.

## risks
- Operators could over-interpret stale/latest as mutation or cleanup semantics if the visibility-only contract is not kept explicit.
- A matching run may be absent or unreadable, so the new field must degrade to the existing non-destructive style.
- Reading anything beyond existing run metadata would widen scope and violate the minimum contract.

## next required gate
- Reviewer: confirm the change remains read-only/operator-assist only and keeps Relation Summary semantics unchanged.
- QA: confirm stale item resolves to `PR-003`, latest item resolves to `PR-004`, and existing `latest_relation`/`matching_run_state` output remains present.
- Docs Sync / Release: confirm docs sync is satisfied by this PR-local plan note plus the code/test change only.
