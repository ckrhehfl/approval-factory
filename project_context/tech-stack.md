# Tech Stack

## 문서 목적
이 문서는 approval-factory MVP를 구현할 때 사용할 **최소 기술 스택과 구현 제약**을 정의한다.

## 구현 원칙
- 문서 우선
- CLI 우선
- 파일 기반 상태 관리 우선
- 단일 레포 우선
- Python 우선

## 권장 기술 선택
### 언어
- Python 3.11+

이유:
- 문서/파일 처리, CLI, 테스트, YAML/JSON 다루기에 적합하다.
- MVP 속도와 유지보수 균형이 좋다.

### 패키지 관리
- uv 또는 pip + venv 중 하나

원칙:
- 팀이 가장 단순하게 유지할 수 있는 방식 선택
- 초기에는 복잡한 monorepo 툴체인 도입 금지

### CLI
- Typer 또는 argparse

권장:
- Typer
이유:
- 명령 구조가 명확하고 MVP용 CLI 작성 속도가 빠르다.

### 데이터 저장
- 파일 기반 저장
- YAML / JSON / Markdown

이유:
- approval queue, run artifacts, evidence bundle을 사람이 직접 열어볼 수 있어야 한다.
- DB는 플랫폼 단계로 미룬다.

### 테스트
- pytest

### 정적 검증
- ruff
- mypy 또는 pyright 중 하나

### 포맷팅
- ruff format 또는 black 중 하나

### 문서 포맷
- Markdown
- YAML 템플릿

## 권장 개발 환경
- 기준 환경: WSL 기반 개발 환경 권장
- Windows는 편집/탐색 용도로 가능하나, Codex CLI 작업 기준은 WSL을 우선 고려

## 초기 디렉터리 책임
- orchestrator/: 실행 엔진과 CLI
- agents/: 역할별 실행 규칙 또는 스킬
- docs/: SSOT 문서
- project_context/: 프로젝트별 입력 문서
- runs/: 실행 결과물
- approval_queue/: 승인 요청 상태 저장

## 이번 MVP에서 피할 기술
- 데이터베이스
- 메시지 큐
- 마이크로서비스
- 웹 프런트엔드
- 복잡한 인증/권한 시스템
- 분산 워커

## 외부 연동 방침
초기 MVP에서는 외부 연동을 최소화한다.
- GitHub 연동은 선택 사항
- PR 리뷰 자동화는 후순위
- 먼저 로컬/수동 오케스트레이션이 끝까지 도는지 검증한다.
