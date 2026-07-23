"""
Yahoo Shopping K-cosmetics category ranking collector(parser only)

How it works:
-Calling the Yahoo mc-module ApI directly from python gets blocked flagged by bot detection, so that route's out.
-Instead, the request is capturedfrom the browser console(F12->console)
  using the real logged-in session, and the respinse gets downloaded as ranking_data.json.This script just read that file and parses out the HTML fields.
-Category matvhing took a few tries to get right. Asuuning "index N in the response = category N"
 didn't hold up, since the campaign module sturcture isn't cosistent (spacer modules come and go).
 What's acturally works: count the order that modules WITH real products show up in, 
 skip the first 2(those are pickup-store widgets, not real categories), then map the next 9 to the tab order (toner->~~~->lip)


How to run it:
1. In the browser, capture the mc-module request via "Copy as fetch"+the download snippet to get ranking_data.json.
2. Drop that file in the same folder as this script.
3. Run: python ranking_collector.py 

 """

from bs4 import BeautifulSoup
import json
import csv

# Same order as the tabs on the promo page
CATEGORY_NAMES = [
    "화장수",
    "미용액",
    "크림",
    "시트마스크",
    "클렌징",
    "자외선차단제",
    "베이스메이크",
    "아이메이크",
    "립",
]

# Number of item-containing "pickup store" widgets that show up before the REAL category tabs start 
# (confirmed as 2: mall_item_tag=kcos_pickupstore, kcos_pickup)
SKIP_ITEM_MODULES = 2

def parse_items_from_html(html_fragment: str) -> list:
    """Pulls product info out of htmlTag (the product list HTML fragment)"""
    soup = BeautifulSoup(html_fragment, "html.parser")
    products = []

    for item in soup.select("li.elItem"):
        name_tag = item.select_one(".elNameName")
        link_tag = item.select_one("a.elItemLink[href]")
        price_tag = item.select_one(".elDiscountedPriceNumber")
        origin_price_tag = item.select_one(".elOriginPrice")
        store_tag = item.select_one(".elStoreName")

        if not name_tag or not link_tag:
            continue #missing the essential, so skip it

        products.append({
            "name": name_tag.get_text(strip=True),
            "url": link_tag.get("href", ""),
            "price": price_tag.get_text(strip=True) if price_tag else None,
            "origin_price": origin_price_tag.get_text(strip=True) if origin_price_tag else None,
            "store": store_tag.get_text(strip=True) if store_tag else None,
        })

    return products


def collect_ranking(json_path: str = "ranking_data.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        modules = json.load(f)
    print(f"[debug]{len(modules)} modules in the response")

    all_rows = []
    item_module_count = 0  # tracks how many modules actually had products!

    for idx, module in enumerate(modules):
        html_fragment = module.get("htmlTag", "")
        if not html_fragment:
            continue

        products = parse_items_from_html(html_fragment)
        if not products:
            continue  # empty module (FreeHTML etc.), nothing to grab here

        category_position = item_module_count - SKIP_ITEM_MODULES
        item_module_count += 1

        if category_position < 0:
            category = None  #one of the pickup store widgets, not a real category
        elif category_position < len(CATEGORY_NAMES):
            category = CATEGORY_NAMES[category_position]
        else:
            category = None  # more modules than expected, just in case!

        print(f"[debug] idx={idx} → item module #{item_module_count}, category={category}, {len(products)} products")

        for rank, product in enumerate(products, start=1):
            all_rows.append({
                "category": category,
                "rank": rank,
                **product,
            })

    return all_rows


if __name__ == "__main__":
    rows = collect_ranking()
    print(f"Collected {len(rows)} products total")

    if rows:
        with open("ranking_result.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print("ranking_result.csv saved successfully")
    else:
        print("Didn't collect anything this time - double check the ranking_date.js on is fresh and that the CSS selectors still match the page.")