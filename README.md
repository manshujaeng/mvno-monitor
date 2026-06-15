# mvno-monitor
알뜰폰 요금제 알림

# 구성
GitHub Actions (매일 오전 9시)
        │
        ▼
알뜰폰 허브 API 조회
        │
        ▼
조건 필터링
(LGU+, 100GB+, 25,000원 이하 등)
        │
        ▼
기존 결과와 비교
        │
 ┌──────┴──────┐
 │ 신규 없음   │
 │ 종료        │
 └─────────────┘

 ┌──────┴──────┐
 │ 신규 발견   │
 ▼             │
텔레그램 알림
 │
 ▼
현재 결과 저장

# 구조
mvno-monitor/
 ├─ check_mvno.py
 ├─ known_products.json
 └─ requirements.txt
