# PR Documents

## canonical role

`docs/prs/`는 PR별 문서 이력과 감사 추적을 남기는 canonical history surface다.
이 경로는 active execution input이나 runtime source of truth가 아니다.
active/archive PR plan의 공식 artifact는 `prs/active/`와 `prs/archive/`에 있다.

## current repo observation

현재 저장소의 `docs/prs/`는 단일 형식이 아니다.
초기 일부 PR은 `scope.md`, `plan.md`, `review.md`, `qa.md`, `docs-sync.md`, `evidence.md`, `decision.md`를 모두 가지지만, 많은 이후 PR은 `plan.md`만 남아 있다.
git history에는 PR-040~049 merge commit이 존재하지만 현재 `docs/prs/PR-040`부터 `docs/prs/PR-049`까지의 per-PR history docs는 저장소에 없다.

## contract

- `docs/prs/`의 canonical role은 historical record와 audit trail 유지다.
- 이 경로의 문서 유무만으로 runtime behavior, readiness, approval, queue, activation, execution semantics를 추론하지 않는다.
- 새로운 PR history docs를 추가할 때는 해당 PR에 대해 확인 가능한 근거만 기록한다.
- PR별 history docs의 권장 shape는 다음 7개 문서다.
  - `scope.md`
  - `plan.md`
  - `review.md`
  - `qa.md`
  - `docs-sync.md`
  - `evidence.md`
  - `decision.md`
- 다만 기존 저장소에는 mixed legacy formats가 존재하므로, 과거 PR 전체가 동일 shape를 가진다고 가정하지 않는다.
- PR-040~049에 대한 retro docs policy는 `README/architecture alignment only`다.
- 위 정책은 `docs/prs`와 architecture wording을 실제 repo/history에 맞게 정렬하는 데만 적용하며, 근거 없는 per-PR retro docs 작성은 포함하지 않는다.

## non-goals

- PR-040~049에 대해 근거 없는 `scope.md`/`plan.md`/`review.md` 등 retro history docs를 새로 작성하지 않는다.
- `docs/prs/` 설명을 근거로 runtime code, readiness semantics, approval semantics, queue semantics를 변경하지 않는다.
