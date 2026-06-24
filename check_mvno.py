import json
import os
import requests
import time

URL = "https://www.mvnohub.kr/rest/product/search"

STATE_FILE = "known_mvno.json"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
tele_msg = ""


def send_telegram(message: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(message)
        return

    chunks = []

    while len(message) > 4000:
        split_pos = message.rfind("\n", 0, MAX_MESSAGE_LENGTH)

        if split_pos == -1:
            split_pos = MAX_MESSAGE_LENGTH

        chunks.append(message[:split_pos])
        message = message[split_pos:].lstrip()

    if message:
        chunks.append(message)

    # 전송
    for chunk in chunks:
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": chunk,
                },
                timeout=60,
            )

            # Rate Limit
            if response.status_code == 429:
                retry_after = response.json().get(
                    "parameters", {}
                ).get("retry_after", 5)

                print(
                    f"Telegram 429 발생, {retry_after}초 후 재시도"
                )

                time.sleep(retry_after)

                requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                    json={
                        "chat_id": TELEGRAM_CHAT_ID,
                        "text": chunk,
                    },
                    timeout=60,
                )

            elif response.status_code != 200:
                print(
                    f"Telegram 오류: {response.status_code}"
                )
                print(response.text)

        except Exception as e:
            print(f"Telegram 전송 실패: {e}")

        time.sleep(1)


def get_products():

    page = 0
    products = {}

    while True:

        params = {
            "minPrice": 0,
            "maxPrice": 30000,
            "dataRanges[0].min": 31,
            #"saleMonthRanges[0].min": 24, # 24개월 이상만 추출됨, 다 출해서 걸러냄
            "page": page,
            "size": 100,
            "sortBy": "product.updatedAt",
            "sortDirection": "DESC",
        }

        print("MVNOHub 요청 시작...")
        for attempt in range(3):  # 스케줄 실행 시 타임아웃 에러가 너무 자주 발생, 3회 시도
            try:
                response = requests.get(
                    URL,
                    params=params,
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/137.0.0.0 Safari/537.36"
                        ),
                        "Referer": "https://www.mvnohub.kr/product/products.do",
                    },
                    timeout=30,
                )
                response.raise_for_status()
                print(f"MVNOHub 응답 수신: {response.status_code}")
                break
                
            except Exception as e:
                print(f"{attempt+1}회 실패: {e}")
        
                if attempt < 2:
                    time.sleep(30)
                else:
                    send_telegram(f"MVNOHub 요청 실패: {type(e).__name__} \n{e}")
                    return {}
        
        content = response.json()["pageResult"]["content"]

        if not content: break

        for p in content:
            if str(p["contractDiscountPeriod"]) not in ("24", "0"): continue  # 24개월 평생요금(0월)만 추출
            product_id = str(p["productId"])
            products[product_id] = {
                "productId": p["productId"],
                "partnerName": p["partnerName"],
                "productName": p["productName"],
                "networkOperator": p["networkOperator"],
                "networkProtocol": p["networkProtocol"],
                "monthlyPaymentFee": p["monthlyPaymentFee"],
                "data": p["data"],
                "dataAfter": p["dataAfter"],
                "contractDiscountPeriod": p["contractDiscountPeriod"],
                "contractDiscountAmount": p["contractDiscountAmount"],
            }   

        if len(content) < 100: break  # 한페이지에 요금제 갯수가 100개 이하면 다음페이지 볼 필요 없으니 break

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
    if str(p["contractDiscountPeriod"]) == "0":
        after_fee_text = " (평생)"
    else:
        after_fee = (p["monthlyPaymentFee"]+p["contractDiscountAmount"])
        after_fee_text = (f"\n할인기간 : {p['contractDiscountPeriod']}개월 후 {after_fee:,}원")

    if p["dataAfter"] == "0Mbps":
        after_data = ""
    else:
        after_data = (f"+{p['dataAfter']}")
        
    return (
        f"사업자 : {p['partnerName']}\n"
        f"상품명 : {p['productName']}\n"
        f"망 : {p['networkOperator']} {p['networkProtocol']}\n"
        f"데이터 : {p['data']}GB{after_data}\n"
        f"요금 : {p['monthlyPaymentFee']:,}원{after_fee_text}\n\n"
    )


def check_changes(previous, current):
    global tele_msg
    for product_id, product in current.items():

        # 신규 상품
        if product_id not in previous:
            #print("[알뜰폰허브] 🆕 신규 요금제 발견\n\n" + format_product(product))
            tele_msg += "[알뜰폰허브]\n\n🆕 신규 요금제 발견\n\n" + format_product(product)
            continue

        # 변경 여부
        if product != previous[product_id]:
            tele_msg += "[알뜰폰허브]\n\n🔄 요금제 변경\n\n" + format_product(product)


def main():
    global tele_msg
    #send_telegram("GitHub Actions 테스트\n\n알뜰폰 모니터링이 정상 동작합니다.")
    current = get_products()
    if not current:  # 상품 조회 실패
        return
    print(f"현재 요금제 수: {len(current)}")
    previous = load_state()

    if previous:
        check_changes(previous, current)
        if tele_msg: 
            send_telegram(tele_msg) # 신규 및 변경 된 요금제 정보 모아서 한번만 전송
        else:
            send_telegram('[알뜰폰허브] 신규 및 변경 요금제 정보 없음') 
    else:
        print("최초 실행 - 상태파일 생성")

    save_state(current)


if __name__ == "__main__":
    main()
