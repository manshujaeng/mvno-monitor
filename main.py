import requests

r = requests.get(
    "https://www.mvnohub.kr/rest/product/search",
    params={
        "minPrice": 0,
        "maxPrice": 30000,
        "dataRanges[0].min": 31,
        "saleMonthRanges[0].min": 24,
        "page": 0,
        "size": 12,
        "sortBy": "product.updatedAt",
        "sortDirection": "DESC",
    },
)

print(r.status_code)
print(r.json())
