# WI-001: 최소 실행 파이프라인 구현

## 상태
Draft

## 문제 정의
현재 approval-factory 레포에는 SSOT 문서와 계약/정책/템플릿이 존재하지만, 실제로 Work Item → PR Plan → Implementation → Review → QA → Docs Sync → Approval Package 흐름을 굴릴 최소 실행 파이프라인은 아직 구현되지 않았다.

## 목표
이 Work Item의 목표는 approval-factory MVP를 위한 **최소 실행 파이프라인**을 구현하는 것이다.

## 포함 범위
- Work Item 산출물 저장 구조 정리
- PR 계획 문서 구조 사용 시작
- Approval Request 생성 흐름 정의 또는 구현
- Evidence Bundle 생성 흐름 정의 또는 구현
- 실행 결과를 runs/에 저장하는 최소 구조 정의 또는 구현
- docs sync 판정 포인트를 흐름에 포함

## 비포함 범위
- 웹 UI
- 중앙 대시보드
- 멀티 프로젝트 관리
- 배포 자동화
- 병렬 에이전트 스케줄링

## 기대 결과
- 승인자가 하나의 PR에 대해 무엇을 승인하는지 명확히 볼 수 있다.
- 작은 PR 단위로 실행 흐름을 반복할 수 있다.
- 문서 기반 계약이 실제 실행 흐름과 연결된다.

## 성공 기준
다음 중 최소 하나의 예제 PR 흐름이 끝까지 돌아가면 성공이다.
1. PR 계획 문서 생성
2. 구현 산출물 또는 스켈레톤 생성
3. 리뷰 결과 작성
4. QA 결과 작성
5. docs sync 판정 작성
6. approval package 작성

## 리스크
- 범위가 쉽게 커질 수 있다.
- 구현보다 운영 구조가 먼저라서 답답하게 느껴질 수 있다.
- 문서와 실제 코드 구조가 일치하지 않을 수 있다.

## 승인자 질문
- 이 Work Item 범위로 MVP 첫 루프를 시작해도 되는가?
