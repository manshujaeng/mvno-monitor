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

print(len(html))
print(html[:1000])
