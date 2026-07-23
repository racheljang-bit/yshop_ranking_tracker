"""
Yahoo Shopping K-cosmetics 카테고리랭킹 수집기 (파서 전용)

원리:
  - Yahoo mc-module API를 Python에서 직접 호출하면 봇 탐지로 차단됨.
  - 대신 브라우저 콘솔(F12 -> Console)에서 실제 세션으로 mc-module을
    fetch해서 결과를 ranking_data.json으로 다운로드한 뒤,
    이 스크립트는 그 파일을 읽어서 htmlTag만 파싱함.
  - 카테고리 매칭: 응답 배열 안에서 몇 번째 인덱스가 어느 카테고리인지는
    캠페인 쪽 구조가 자주 바뀌어서(FreeHTML 스페이서 유무 등) 신뢰할 수 없었음.
    대신 "실제 상품이 들어있는 모듈이 등장하는 순서"만 세서, 앞 2개(픽업스토어
    위젯)를 건너뛰고 그다음 9개를 탭 순서(화장수→...→립)대로 배정함.

사용법:
  1. 브라우저에서 mc-module 요청을 콘솔의 "Copy as fetch" + 다운로드
     스니펫으로 ranking_data.json 다운로드
  2. 그 파일을 이 스크립트와 같은 폴더에 두기
  3. python ranking_collector.py 실행
"""

from bs4 import BeautifulSoup
import json
import csv

# 프로모션 페이지 탭 순서 그대로.
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

# 카테고리 탭이 시작되기 전, 상품이 들어있는 픽업스토어류 위젯 개수
# (이전 확인 기준 2개: mall_item_tag=kcos_pickupstore, kcos_pickup)
SKIP_ITEM_MODULES = 2

def parse_items_from_html(html_fragment: str) -> list:
    """htmlTag(상품 리스트 HTML 조각)에서 상품 정보 추출"""
    soup = BeautifulSoup(html_fragment, "html.parser")
    products = []

    for item in soup.select("li.elItem"):
        name_tag = item.select_one(".elNameName")
        link_tag = item.select_one("a.elItemLink[href]")
        price_tag = item.select_one(".elDiscountedPriceNumber")
        origin_price_tag = item.select_one(".elOriginPrice")
        store_tag = item.select_one(".elStoreName")

        if not name_tag or not link_tag:
            continue

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
    print(f"[디버그] 응답 모듈 개수: {len(modules)}")

    all_rows = []
    item_module_count = 0  # 상품이 들어있는 모듈이 몇 번째인지 세는 카운터

    for idx, module in enumerate(modules):
        html_fragment = module.get("htmlTag", "")
        if not html_fragment:
            continue

        products = parse_items_from_html(html_fragment)
        if not products:
            continue  # FreeHTML 등 상품 없는 모듈은 건너뜀

        category_position = item_module_count - SKIP_ITEM_MODULES
        item_module_count += 1

        if category_position < 0:
            category = None  # 픽업스토어류 위젯
        elif category_position < len(CATEGORY_NAMES):
            category = CATEGORY_NAMES[category_position]
        else:
            category = None  # 예상 밖의 추가 모듈 (9개 넘어감)

        print(f"[디버그] idx={idx} → {item_module_count}번째 상품모듈, category={category}, 상품 수={len(products)}")

        for rank, product in enumerate(products, start=1):
            all_rows.append({
                "category": category,
                "rank": rank,
                **product,
            })

    return all_rows


if __name__ == "__main__":
    rows = collect_ranking()
    print(f"총 {len(rows)}개 상품 수집됨")

    if rows:
        with open("ranking_result.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        print("ranking_result.csv로 저장 완료")
    else:
        print("수집된 상품이 없어요 — ranking_data.json 파일이 최신인지, CSS 셀렉터가 실제 구조랑 맞는지 확인해보세요.")