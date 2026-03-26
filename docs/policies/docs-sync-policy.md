# Docs Sync Policy

코드 변경 후 문서 동기화는 선택이 아니라 필수 판정 단계다.

## 갱신 기준

### architecture.md
- 컴포넌트 추가/삭제
- 책임 이동
- 데이터 흐름 변경
- 외부 연동 변경

### ADR
- 중요한 기술 선택
- 구조적 패턴 채택/변경
- 기존 설계 결정 폐기

### domain-model.md
- 엔티티/상태/스키마 변경

### ops 문서
- 승인/실패복구/운영 절차 변경

### PR 문서
- 모든 PR은 자기 기록을 남긴다

## 필수 규칙

- docs sync가 필요 없더라도 그 근거를 남긴다
- docs sync complete 이전에는 merge 금지
