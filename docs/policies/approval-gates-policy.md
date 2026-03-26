# Approval Gates Policy

## 필수 인간 승인 게이트

1. Scope Approval  
새 Work Item 시작 또는 범위 변경 시

2. Architecture Approval  
구조 변경, 데이터 모델 변경, 의존성 추가, ADR 필요 시

3. Exception Approval  
보안/비용/성능 기준 예외 또는 실패한 테스트 허용 시

4. Merge Approval  
모든 필수 체크 후

5. Release Approval  
릴리즈 전

## Merge Approval 최소 조건

- lint pass
- test pass
- build pass
- review complete
- qa complete
- docs sync complete
- evidence bundle complete

## 승인 결정 종류

- approve
- reject
- request_changes
- approve_with_exception
