import json
import os
import requests
from bs4 import BeautifulSoup
#import re

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

def get_plans():
    response = requests.get(
        URL,
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

        print(len(text))
        print(text)

        if len(text) < 20:
            continue

        plans[href] = text

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
                f"{text}\n\n"
                f"https://www.moyoplan.com{plan_id}"
            )

            print(message)
            #send_telegram(message)

    # 변경
    for plan_id, text in current.items():
        if plan_id not in previous:
            continue

        if text != previous[plan_id]:
            message = ("[모요]\n\n🔄 요금제 정보 변경\n\n"
                f"{text}\n\n"
                f"https://www.moyoplan.com{plan_id}"
            )

            print(message)
            #send_telegram(message)

    save_current(current)


if __name__ == "__main__":
    main()
