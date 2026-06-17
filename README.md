# mvno-monitor
알뜰폰 요금제 알림(30기가 이상, 할인 24개월 이상, 3만원 이하 요금제)

# 구성
GitHub Actions (매일 오전 9시)  
        ▼  
알뜰폰 허브 API 조회  
        ▼  
조건 필터링(LGU+, 100GB+, 25,000원 이하 등)  
        ▼  
기존 결과와 비교  
 ┌──────┴──────┐  
 │ 신규 없음   │  
 │ 종료        │  
 └─────────────┘  
 ┌──────┴──────┐  
 │ 신규 발견   │  
 └─────────────┘  
         ▼  
텔레그램 알림  
        ▼  
현재 결과 저장(같은 로직으로 모요도 실행)  


# 구조
mvno-monitor/  
├─ check_mvno.py  
├─ check_moyo.py  
├─ requirements.txt  
├─ known_mvno.json  
├─ known_moyo.json  
└─ .github/  
   └─ workflows/  
      └─ mvno.yml  

# 스케줄 등록 실패 시
안내받은 모든 걸 확인해봐도 스케줄 실행이 안되서 토큰을 받아 구글 스크립트로 실행  
깃허브 우측 상단 프로필 클릭 ➡️ Settings로 이동합니다.  
왼쪽 최하단의 Developer Settings ➡️ Personal Access Tokens ➡️ Tokens (classic)을 클릭합니다.  
Generate new token (classic)을 선택합니다.  
Note에는 GAS-Trigger 같은 이름을 적고, 권한(Scopes)에서 workflow 항목에 체크합니다.  
아래 Generate token 누르면 나오는 긴 문자열(토큰)을 반드시 복사해서 따로 저장해 두세요. (이 창을 닫으면 다시는 볼 수 없습니다!)  



