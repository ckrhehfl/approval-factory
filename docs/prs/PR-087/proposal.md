# PR-087 Proposal

## input refs
- AGENTS.md working-copy version observed on 2026-04-05
- `git status -sb`
- `python -m factory status --root .`
- `python -m factory inspect-approval-queue --root .`
- [docs/prs/PR-085/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-085/plan.md)
- [docs/prs/PR-085/proposal.md](/mnt/c/dev/approval-factory/docs/prs/PR-085/proposal.md)
- [docs/prs/PR-086/plan.md](/mnt/c/dev/approval-factory/docs/prs/PR-086/plan.md)

## scope
- Proposal-only clarification for wording verification and operator misread risk around `queue_hygiene_audit`.
- No implementation.
- No runtime, CLI output, test, queue artifact, or approval lifecycle change.
- No change to cleanup semantics, resolve semantics, approval decision semantics, readiness/gate semantics, selector semantics, stale/latest relation semantics, or Relation Summary semantics.

## output summary
- Define the exact misreadings that `queue_hygiene_audit` wording must prevent.
- Classify short wording patterns as safe or unsafe based on whether they imply action, decision state, or relation state.
- Judge the current warning wording as directionally correct but too dense for reliable operator safety.
- Recommend docs/help/tests-only verification evidence first; defer any output wording refinement to a separate follow-up if evidence shows persistent overread risk.
- Define what later evidence would count as operator-safe wording.

## observed repo facts
- `factory status --root .` currently reports queue summary facts and must not gain `queue_hygiene_audit` meaning in this proposal.
- `python -m factory inspect-approval-queue --root .` currently reports Relation Summary separately from per-item inspection facts.
- PR-085 fixed the intended placement boundary: `inspect-approval-queue` only, per-item only, no `factory status` exposure, no summary/count visibility.
- PR-086 already implemented item-local read-only rendering plus warning wording.
- The next risk is operator overreading of the wording, not missing runtime functionality.

## 0) 바꾸려는 의미
- 이번 PR이 바꾸려는 것은 `queue_hygiene_audit`의 runtime semantics가 아니라 wording verification standard다.
- `queue_hygiene_audit`는 계속해서 read-only operator visibility wording으로만 해석돼야 한다.
- 제안의 목적은 "무엇을 뜻하는가"를 늘리는 것이 아니라 "무엇으로 오해되면 안 되는가"를 더 선명하게 고정하는 것이다.
- 문구 검증의 대상은 per-item inspection 위치의 짧은 operator-facing wording뿐이다.

## 1) 왜 필요한지
- PR-085와 PR-086으로 placement와 read-only rendering은 정리됐지만, 운영자가 문구를 과잉 해석할 가능성은 별도로 남아 있다.
- `queue_hygiene_audit`라는 이름과 경고 문구가 길어지면, 운영자는 핵심 부정 경계보다 익숙한 action word만 집어 읽을 수 있다.
- 특히 pending item inspection 화면에서는 운영자가 빠르게 triage하므로, `cleaned`, `resolved`, `ready`, `selected`, `latest/stale` 같은 단어 조각만으로도 오독이 생길 수 있다.
- 따라서 이번 PR은 runtime gap이 아니라 operator reading risk를 줄이기 위한 verification contract가 필요하다.

## 2) 최소 계약
- `queue_hygiene_audit` wording은 다음 misreading을 반드시 막아야 한다.
- `cleaned`: 이 항목이 이미 정리됐거나 queue에서 제거해도 된다고 읽히면 안 된다.
- `resolved`: 이 항목이 이미 처리됐거나 지금 resolve해도 안전하다고 읽히면 안 된다.
- `approval decision`: approve/reject/request_changes/exception 판단이 이미 정리됐다고 읽히면 안 된다.
- `ready` or `satisfied`: readiness/gate condition이 충족됐다고 읽히면 안 된다.
- `selected`: selector가 저장돼 있거나 후속 동작의 선택 결과라고 읽히면 안 된다.
- `latest/stale`: latest_relation 또는 stale/latest 상태를 설명하거나 덮어쓴다고 읽히면 안 된다.
- `summary`: Relation Summary 또는 queue-level summary 의미로 일반화되면 안 된다.
- Safe wording pattern은 짧고 descriptive only여야 한다.
- Safe wording pattern은 `read-only`, `operator note`, `audit only`, `does not change queue state`처럼 action을 직접 부정하는 구조여야 한다.
- Safe wording pattern은 한 문장 또는 두 짧은 구문 안에서 "what it is"와 "what it is not"를 바로 붙여야 한다.
- Unsafe wording pattern은 action hint를 직접 포함하거나 state label처럼 보이는 구조다.
- Unsafe wording pattern 예시는 `cleaned`, `resolved`, `safe to resolve`, `ready`, `satisfied`, `selected`, `latest`, `stale`, `current state`, `handled`, `done`, `applied state`다.
- Unsafe wording pattern은 긴 부정 목록을 한 문장에 과도하게 압축해 operator가 중간만 읽어도 의미를 놓치게 만드는 형태도 포함한다.
- 현재 warning wording에 대한 판정은 "too dense"가 맞다.
- 현재 wording은 방향은 맞다. read-only, non-cleanup, non-resolve, non-decision 경계를 이미 지향한다.
- 하지만 한 번에 너무 많은 비의미 범주를 나열하면 operator가 핵심인 `read-only audit only`보다 뒤쪽 금지 목록을 흘려 읽을 가능성이 크다.
- 따라서 현재 wording은 "too weak"보다는 "too dense"로 본다.
- 질문 4에 대한 답: follow-up이 필요하다면 docs/help/tests-only verification이 먼저다.
- output wording refinement는 evidence가 누적될 때만 별도 PR로 다루고, semantics expansion과 분리한다.

## 3) 금지 범위
- 이번 PR에서 inspect output in code를 바꾸지 않는다.
- 이번 PR에서 warning text runtime string을 바꾸지 않는다.
- 이번 PR에서 tests를 추가하거나 수정하지 않는다.
- 이번 PR에서 `queue_hygiene_audit`를 cleanup semantics로 연결하지 않는다.
- 이번 PR에서 `queue_hygiene_audit`를 resolve semantics로 연결하지 않는다.
- 이번 PR에서 `queue_hygiene_audit`를 approval decision semantics로 연결하지 않는다.
- 이번 PR에서 `queue_hygiene_audit`를 readiness/gate semantics로 연결하지 않는다.
- 이번 PR에서 `queue_hygiene_audit`를 selector semantics로 연결하지 않는다.
- 이번 PR에서 `queue_hygiene_audit`를 stale/latest relation semantics나 Relation Summary semantics로 연결하지 않는다.
- 이번 PR에서 docs wording verification을 근거로 새로운 runtime surface나 summary/count semantics를 승인하지 않는다.

## 4) 검증 기준
- Proposal validation:
- runtime code path 변경이 없어야 한다.
- proposal text가 misreadings to prevent를 explicit list로 포함해야 한다.
- proposal text가 safe vs unsafe wording pattern을 구분해야 한다.
- proposal text가 current wording verdict를 `sufficient`, `too weak`, `too dense` 중 하나로 명시해야 한다.
- proposal text가 `queue_hygiene_audit`는 read-only only라고 명시해야 한다.
- proposal text가 wording tweak follow-up과 semantics expansion follow-up을 분리해야 한다.
- Later operator-safe wording evidence should require all of the following.
- evidence reviewers can point to a short candidate phrase and restate it as `read-only audit only` without inferring cleanup, resolve, decision, readiness, selector, latest/stale, or summary meaning.
- evidence includes at least one negative checklist that explicitly tests the unsafe phrases `cleaned`, `resolved`, `safe to resolve`, `ready`, `satisfied`, `selected`, `latest`, and `stale`.
- evidence keeps verification on docs/help/mock output or review checklist first before any code change.
- if a wording refinement PR is opened later, it must show that the refinement shortens or clarifies wording without broadening semantics.
- Closeout validation:
- record `git status --short`, `git --no-pager diff --stat`, and `git --no-pager diff --name-only`.
- if only docs changed, say so explicitly.

## 5) 후속 구현 분할안
- Follow-up A: docs/help/tests-only wording verification
- produce a compact operator-reading checklist, mock output excerpt, or reviewer rubric without changing runtime strings.
- Follow-up B: output wording refinement proposal, only if Follow-up A shows current wording remains too dense in review.
- keep the change limited to phrasing refinement on the existing item-local read-only surface.
- do not use Follow-up B to add summary semantics, action semantics, or new fields.
- Follow-up C: no change needed
- if Follow-up A shows operators consistently read the current wording as read-only audit only, stop here and keep runtime wording unchanged.
- Any future cleanup, resolve, decision, readiness/gate, selector, latest/stale, or Relation Summary discussion remains separate proposal work.

## risks
- If later reviewers compress the wording to a single state-like adjective, operator safety will regress even if the text is shorter.
- If later refinements mix anti-misread wording with stale/latest or Relation Summary wording, the item-local boundary from PR-085 will blur.
- If docs-only verification is skipped, a wording tweak could be approved on intuition rather than evidence.

## next required gate
- Reviewer: confirm the proposal is wording-verification-only and does not approve semantics expansion.
- Approver / PM: decide whether to run Follow-up A first or declare no change needed.
- QA: if any later refinement PR opens, require operator-safe wording evidence before accepting it.
