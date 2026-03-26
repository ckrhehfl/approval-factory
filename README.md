# approval-factory

승인자 중심 멀티 에이전트 개발 오케스트레이션 MVP용 레포 SSOT 문서 세트다.

이 레포의 기본 원칙은 다음과 같다.

1. 이 저장소 안의 **설계, 정책, 계약, ADR, 운영 기준**이 SSOT다.
2. 노션 문서는 이해를 돕는 how-to 용도이며, 충돌 시 이 레포 문서가 우선한다.
3. 모든 작업은 Work Item → 설계 → PR 계획 → 구현 → 리뷰 → QA → Evidence → 승인 → 문서 동기화 → Merge 흐름을 따른다.
4. 승인 없는 구조 변경, 범위 변경, 예외 허용, 릴리즈는 금지한다.
5. 코드 변경은 문서 영향도를 반드시 함께 판정한다.

## 이 레포에서 SSOT로 취급하는 폴더

- `docs/design/` : 시스템 설계와 구조
- `docs/adr/` : 구조적 의사결정 기록
- `docs/contracts/` : 역할/산출물/문서 계약
- `docs/policies/` : 승인/테스트/문서동기화 정책
- `docs/ops/` : 실제 운영 기준(runbook, checklist)
- `config/` : 역할, 게이트, 프로젝트 기본 설정
- `templates/` : 산출물 템플릿
- `AGENTS.md` : 에이전트 공통 운영 규약

## SSOT와 How-to를 분리하는 이유

SSOT는 “현재 시스템이 어떻게 동작해야 하는가”를 정의한다.  
How-to는 “사람이 이 시스템을 어떻게 활용할 것인가”를 설명한다.

둘을 섞으면 다음 문제가 생긴다.

- 설명 문서가 정책 문서처럼 오해된다.
- 실제 규칙 변경 없이 운영 팁만 바뀌어도 레포 SSOT가 흔들린다.
- 승인 기준과 가이드 문서의 버전 차이가 생긴다.

따라서 **정책/설계/계약은 레포**, **운영법/교육자료는 노션**으로 분리한다.

## 권장 시작 경로

- 로컬 경로: `c:\dev\approval-factory`
- 시작 순서:
  1. `docs/design/mvp-system-design.md`
  2. `docs/design/architecture.md`
  3. `AGENTS.md`
  4. `config/roles.yaml`
  5. `config/gates.yaml`
  6. 첫 Work Item 등록

## 최소 구현 우선순위

1. Work Item 생성
2. 설계 초안 생성
3. PR 분해
4. PR별 구현/리뷰/QA
5. Approval Package 생성
6. Docs Sync 체크
7. 승인 후 Merge

## 레포 구조

```text
approval-factory/
├─ AGENTS.md
├─ README.md
├─ config/
├─ templates/
└─ docs/
   ├─ design/
   ├─ adr/
   ├─ contracts/
   ├─ policies/
   ├─ ops/
   └─ prs/
```
