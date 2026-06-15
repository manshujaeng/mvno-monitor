import json
import os
import requests

URL = "https://www.mvnohub.kr/rest/product/search"

STATE_FILE = "known_products.json"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(message)
        return

    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
        },
        timeout=30,
    )


def get_products():

    page = 0
    products = {}

    while True:

        params = {
            "minPrice": 0,
            "maxPrice": 30000,
            "dataRanges[0].min": 31,
            "saleMonthRanges[0].min": 24,
            "page": page,
            "size": 100,
            "sortBy": "product.updatedAt",
            "sortDirection": "DESC",
        }

        response = requests.get(
            URL,
            params=params,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.mvnohub.kr/product/products.do",
            },
            timeout=30,
        )

        response.raise_for_status()

        content = response.json()["pageResult"]["content"]

        if not content:
            break

        for p in content:

            product_id = str(p["productId"])

            products[product_id] = {
                "productId": p["productId"],
                "partnerName": p["partnerName"],
                "productName": p["productName"],
                "networkOperator": p["networkOperator"],
                "networkProtocol": p["networkProtocol"],
                "monthlyPaymentFee": p["monthlyPaymentFee"],
                "data": p["data"],
                "contractDiscountPeriod": p["contractDiscountPeriod"],
            }

        if len(content) < 100:
            break

        page += 1

    return products


def load_state():

    if not os.path.exists(STATE_FILE):
        return {}

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(data):

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )


def format_product(p):

    return (
        f"사업자 : {p['partnerName']}\n"
        f"상품명 : {p['productName']}\n"
        f"망 : {p['networkOperator']} {p['networkProtocol']}\n"
        f"데이터 : {p['data']}GB\n"
        f"요금 : {p['monthlyPaymentFee']:,}원\n"
        f"할인기간 : {p['contractDiscountPeriod']}개월"
    )


def check_changes(previous, current):

    # 신규 상품
    for product_id, product in current.items():

        if product_id not in previous:
            print("🆕 신규 요금제 발견\n\n" + format_product(product))
            #send_telegram("🆕 신규 요금제 발견\n\n" + format_product(product))

    # 변경 감지
    for product_id, product in current.items():

        if product_id not in previous:
            continue

        old = previous[product_id]

        # 가격 인하
        if product["monthlyPaymentFee"] < old["monthlyPaymentFee"]:

            #send_telegram(
            print(
                "⬇️ 가격 인하\n\n"
                f"{product['partnerName']}\n"
                f"{product['productName']}\n\n"
                f"{old['monthlyPaymentFee']:,}원 → "
                f"{product['monthlyPaymentFee']:,}원"
            )

        # 데이터 증가
        if product["data"] > old["data"]:

            #send_telegram(
            print(
                "📈 데이터 증가\n\n"
                f"{product['partnerName']}\n"
                f"{product['productName']}\n\n"
                f"{old['data']}GB → "
                f"{product['data']}GB"
            )

        # 할인기간 증가
        if (
            product["contractDiscountPeriod"]
            > old["contractDiscountPeriod"]
        ):

            #send_telegram(
            print(
                "🎁 할인기간 증가\n\n"
                f"{product['partnerName']}\n"
                f"{product['productName']}\n\n"
                f"{old['contractDiscountPeriod']}개월 → "
                f"{product['contractDiscountPeriod']}개월"
            )


def main():

    current = get_products()

    previous = load_state()

    if previous:
        check_changes(previous, current)
    else:
        print("최초 실행 - 상태파일 생성")

    save_state(current)


if __name__ == "__main__":
    main()
