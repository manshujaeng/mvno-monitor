from bs4 import BeautifulSoup
import requests

url = (
    "https://www.moyoplan.com/plans"
    "?filters.data.includeUnlimited=true"
    "&filters.data.ranges.0.min=30"
    "&filters.discounts.ranges.0.min=24"
    "&filters.lowestFee.ranges.0.max=30000"
    "&page.page=0"
    "&page.size=100"
)

html = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
).text

#print(len(html))
#print(html[:1000])

#print("핀다" in html)
#print("모나" in html)
#print("아이즈" in html)
#print("100GB" in html)
#print("150GB" in html)

#idx = html.find("핀다")
#print(idx)
#print(html[idx-1000:idx+2000])

soup = BeautifulSoup(html, "html.parser")

for a in soup.find_all("a", href=True):

    href = a["href"]

    if href.startswith("/plans/"):

        print("ID:", href)

        text = a.get_text(" ", strip=True)

        print(text[:500])

        print("=" * 100)

        break
