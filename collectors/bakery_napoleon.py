"""나폴레옹과자점.

Next.js SSR 사이트지만 상품은 HTML 을 긁지 않고 백엔드 API 를 직접 부른다.
2026-09-30 실측.

  GET napoleonbakery.co.kr/api/products?jstr_mongoparam={...}

몽고 쿼리를 그대로 받는 API 다. 페이지 JS 청크(46049)의 pageconfig2mongoparam 에서
상품목록 화면이 만드는 파라미터를 그대로 옮겼다. 쿼리는 brand_key 와 '판매 가능한
변형이 하나라도 있을 것' 두 조건이고, 이 둘만 넣으면 사이트가 보여주는 354건과
정확히 일치한다(조건을 빼면 649건이 나온다 — 미노출 상품까지 딸려온다).

**페이지네이션 해결.** 조사 단계에서 못 풀었다고 기록된 부분이다. 상품 페이지에
?page=2 를 붙여도 응답의 page 가 계속 1인 게 맞다. 그 페이지는 getServerSideProps 가
쿼리스트링을 아예 안 읽고 limit 36 으로 고정 호출하기 때문이고, 페이지 넘김은
화면이 위 API 를 skip/limit 로 다시 부르는 방식이다. limit 400 한 번이면 354건이
통째로 온다(전체의 10%인 36건만 가져오던 상태에서 100%가 됐다).

**day8until_newarrival 의 의미도 확정했다. 출시일이 아니라 신상품 표시가 끝나는
날(YYYYMMDD, 포함)이다.** 같은 청크의 상품필터 코드가 근거다.

    "NEWARRIVAL"===i && (o.day8until_newarrival = {$gte: date2day8(new Date)})

즉 사이트의 '신상품' 필터는 이 값이 오늘 이상인 상품을 고른다. day8 은 이 플랫폼이
날짜를 담는 타입으로, dt2day8 이 year*10000+month*100+day 다. 그래서
  - released_at 에는 넣지 않는다. 출시일이 아니다.
  - uploaded_at 도 아니다. 업로드 시각이 아니라 배지 만료일이다.
  - is_new 는 '오늘까지 유효한가'로만 판정한다. 브랜드 규칙을 그대로 쓴다.
354건 중 20건에 값이 있는데 2026-09-30 기준 전부 만료다(최신 20260831). 같은 날짜로
8건이 몰린 덩어리도 있어 어차피 출시일로 쓸 물건이 아니었다. 값이 있었다가 만료된
상품과 애초에 값이 없는 상품 모두 '지금은 신상품이 아니다'가 브랜드의 판정이므로
is_new 는 False 로 둔다. 실제로 API 에 신상품 필터를 걸어보면 0건이 나온다.

tags 에 시즌한정·한정판·인기상품이 따로 있어서 labels 로 넘긴다. 신제품 신호는
아니라서 is_new 에는 쓰지 않는다.

_i18n 에 영문명이 들어있지만 origin 이 "CLAUDE" 인 기계번역이고 "DEVONLY" 같은
내부값도 섞여 있어 name_en 에 쓰지 않는다.

robots.txt: 200 text/plain 178B, 본문 첫 글자 'U'. /athena/ /orders/ /test /api/test
만 막는다. /api/products 는 제한 밖이다. 이용약관 문서는 사이트에서 찾지 못했다.
가격은 productVariants 에 있지만 Item 에 필드가 없어 담지 않는다.
"""
import json
import time
from datetime import date

from . import base
from .base import Item

BRAND = "나폴레옹과자점"
BRAND_KEY = "nIizUPQSY7ShRHcXPJlZZ"
API = "https://napoleonbakery.co.kr/api/products"
# 상품 상세. 사이트 링크는 뒤에 이름 슬러그가 더 붙지만 키만으로도 200 이 온다.
PRODUCT = "https://napoleonbakery.co.kr/hermes/product/{key}?brands=napoleon"
IMAGE = ("https://ik.imagekit.io/napoleonbakery/tr:w-800,h-800"
         "/binaryfile/processed/{sha}")

# 상품목록 화면이 쓰는 판매상태. 이게 빠지면 미노출 상품까지 딸려온다.
STATES = ["PAYPLEABLE", "KAKAOABLE", "OUTOFSEASON", "PRICEABLE"]
PAGE_SIZE = 400
MAX_PAGES = 10   # 폭주 방지. 현재 354건이라 1페이지로 끝난다.
DELAY = 2.0
# 배지로 쓰는 태그. 나머지 태그는 분류라서 category 로 간다.
LABEL_TAGS = ("시즌한정", "한정판", "인기상품")


def _today8() -> int:
    """오늘을 YYYYMMDD 정수로. 사이트의 date2day8 과 같은 표현."""
    t = date.today()
    return t.year * 10000 + t.month * 100 + t.day


def _param(skip: int) -> str:
    return json.dumps({
        "query": {
            "brand_key": BRAND_KEY,
            "productVariants": {"$elemMatch": {"_state": {"$in": STATES}}},
        },
        "projection": {"key": 1, "name": 1, "tags": 1, "description": 1,
                       "richimages": 1, "day8until_newarrival": 1, "rowindex": 1},
        "sort": [["rowindex", 1], ["key", 1]],
        "limit": PAGE_SIZE,
        "skip": skip,
    }, ensure_ascii=False)


def _category(tags: list) -> str:
    """배지 태그를 뺀 첫 태그. 태그는 넓은 것부터 오므로 앞이 대분류다."""
    rest = [t for t in tags if t not in LABEL_TAGS]
    return rest[0] if rest else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    today = _today8()
    with base.client() as c:
        for page in range(MAX_PAGES):
            r = base.retry(lambda: c.get(API, params={"jstr_mongoparam": _param(page * PAGE_SIZE)}))
            r.raise_for_status()
            body = r.json()["body"]
            rows = body.get("items", [])
            if not rows:
                break

            for x in rows:
                name = (x.get("name") or "").strip()
                if not name:
                    continue
                it = Item(brand=BRAND, name=name)
                if it.key in seen:
                    continue
                seen.add(it.key)

                tags = x.get("tags") or []
                imgs = x.get("richimages") or []
                sha = imgs[0].get("imagene", {}).get("sha", "") if imgs else ""
                until = x.get("day8until_newarrival")

                it.desc = (x.get("description") or {}).get("oneliner", "").strip()
                it.image = IMAGE.format(sha=sha) if sha else ""
                it.labels = [t for t in tags if t in LABEL_TAGS]
                it.category = _category(tags)
                it.is_new = bool(until) and until >= today
                it.url = PRODUCT.format(key=x["key"])
                items.append(it)

            if len(items) >= body.get("total", 0):
                break
            time.sleep(DELAY)
    return items
