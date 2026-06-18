import json
import os
import requests
from bs4 import BeautifulSoup
import re

url = (
    "https://www.moyoplan.com/plans"
    "?filters.data.includeUnlimited=true"
    "&filters.data.ranges.0.max=0&filters.data.ranges.0.min=30"
    #"&filters.discounts.excludeLifetimeDiscount=false"
    #"&filters.discounts.includeNoDiscount=false"
    "&filters.discounts.ranges.0.max=9999&filters.discounts.ranges.0.min=24"
    #"&filters.lowestFee.maxUnbounded=false"
    "&filters.lowestFee.ranges.0.max=30000&filters.lowestFee.ranges.0.min=0"
    "&page.page=0"
    "&page.size=100"
    #"&sort=RECOMMEND"
)

KNOWN_FILE = "known_moyo.json"

BOT_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def send_telegram(message):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=30
    )

def clean_plan_text(text):
    # 맨 앞 별점 제거 (예: 4.5 /음성기본 100GB+5Mbps_24개월/ 월 100GB + 5Mbps/ 통화 무제한/ 문자 무제한/ LG U+망/ LTE/ 월 25,600원 24개월 이후 47,080원/ 2,269명이 선택)
    text = re.sub(r'^\d+\.\d+\s+', '', text)          # 문자열 시작(^) 숫자.숫자 뒤에 공백 1개 이상(\s+)
    #text = re.sub(r'^\s*\d+\.\d+\s*', '', text)      # 문자열 시작  앞 공백 0개 이상  숫자.숫자  뒤 공백 0개 이상

    # 맨 뒤 "000명이 선택" 제거
    text = re.sub(r'\s+\d[\d,]*명이 선택$', '', text)  # 공백  숫자...명이 선택  문자열 끝($)
    #text = re.sub(r'\s*\d[\d,]*명이 선택', '', text)  # 어디에 있든 숫자명이 선택

    return text.strip()
    

def format_plan(text):
    # 줄바꿈
    text = text.replace(" 월 ", "\n월 ")
    text = text.replace(" 통화 ", "\n통화 ")
    text = text.replace(" 문자 ", "\n문자 ")
    text = text.replace(" LG U+망 ", "\nLG U+망 ")
    text = text.replace(" KT망 ", "\nKT망 ")
    text = text.replace(" SKT망 ", "\nSKT망 ")
    text = text.replace(" LTE ", "\nLTE ")
    text = text.replace(" 5G ", "\n5G ")
    #text = text.replace("개월 이후", "\n개월 이후")

    return text


def get_plans():
    response = requests.get(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            )
        },
        timeout=60
    )

    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    plans = {}

    for a in soup.select('a[href^="/plans/"]'):
        href = a.get("href")
        if not href:
            continue

        # /plans/12345 만 허용
        parts = href.split("/")

        if len(parts) != 3:
            continue

        if not parts[2].isdigit():
            continue

        text = a.get_text(" ", strip=True)

        #print(len(text))
        #print(text)

        if len(text) < 20:  # 설명이 짧은건 상품설명이 아니라고 보고 버림?
            continue

        plans[href] = clean_plan_text(text)  # 앞에 별점과 뒤에 000명이 선택 제거

    return plans


def load_previous():

    if not os.path.exists(KNOWN_FILE):
        return {}

    with open(KNOWN_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_current(data):
    with open(KNOWN_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def main():
    current = get_plans()
    previous = load_previous()
    print(f"현재 요금제 수: {len(current)}")

    # 신규
    for plan_id, text in current.items():
        if plan_id not in previous:
            message = ("[모요]\n\n🆕 신규 요금제\n\n"
                f"{format_plan(text)}\n\n"
                f"https://www.moyoplan.com{plan_id}"
            )
            print(message)
            #send_telegram(format_plan(message))

    # 변경
    for plan_id, text in current.items():
        if plan_id not in previous:
            continue

        if text != previous[plan_id]:
            message = ("[모요]\n\n🔄 요금제 정보 변경\n\n"
                f"{format_plan(text)}\n\n"
                f"https://www.moyoplan.com{plan_id}"
            )
            print(message)
            #send_telegram(format_plan(message))

    save_current(current)


if __name__ == "__main__":
    main()
