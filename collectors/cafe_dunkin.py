"""던킨.

Inertia.js 사이트라 HTML 최상단 엘리먼트의 data-page 속성에 페이지 props 가 JSON 으로
통째로 들어있다. 클래스 이름을 훑는 것보다 이쪽이 훨씬 덜 깨져서 JSON 만 읽는다.
쿠키·토큰 없이 열리고 브라우저 불필요. 2026-09-30 실측.

신제품 신호는 카테고리 하나다. **DONUT(cat=1) 밑에만 '신제품'(sub=1) 서브카테고리가 있다.**
나머지 대분류 넷(FOOD·COFFEE·BEVERAGE·SNACK & MORE)에는 신제품 칸이 아예 없어서,
도넛이 아닌 신제품은 브랜드가 알려주지 않는다. 그래서 전체 메뉴판을 받아서
'신제품' 칸에 든 것만 is_new=True 로 올리고, 나머지는 None 으로 둔 채
collect 의 어제 대비 diff 에 맡긴다. 신제품 탭만 받으면 커피·음료 신제품은 영영 못 잡는다.

**출시일이 없다.** 상품 레코드에 날짜 필드가 하나도 없고(id/TITLE/E_TITLE/카테고리/
이미지/색상/TOP_YN/SEASON_MENU_DIV/SORTNUM 이 전부), /menu/<id> 상세 페이지는 404 다.
그래서 released_at 은 전부 빈 값이고 desc 도 받을 데가 없다. 가격 정보도 없다.

받는 구조에서 조심할 것 세 가지:
  - 한 페이지 12건이고 page 파라미터로 넘긴다. 다만 **다음 페이지가 없으면 서버가
    1페이지를 그대로 되돌려준다**(cat=1&sub=1&page=2 가 같은 5건). 0건 종료만 믿으면
    같은 걸 무한히 다시 받는다. 메가처럼 '전부 기존 id' 조건도 같이 둔다.
  - COFFEE(cat=6)는 SUBCATEGORY_DIV_YN=1 이라 products 대신 productCats 키로 오고,
    sub 을 줘도 그 대분류 전체를 돌려준다. 그래서 dd_product_cat2_id 로 한 번 더 거른다.
  - 카테고리 트리는 props.categories[0]["data"] 에 있다. 리스트 한 겹이 더 있다.

행사 표시는 메뉴에 없다. 프로모션은 별도 /event 영역이라 받지 않는다. promo 는 전부 False 다.
"""
import json
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "던킨"
URL = "https://www.dunkindonuts.co.kr/menu"
IMG_ROOT = "https://www.dunkindonuts.co.kr"
NEW_CAT = "신제품"      # DONUT 밑의 신제품 서브카테고리 이름
PAGE_SIZE = 12          # 한 페이지 12건. 이보다 적게 오면 다음 페이지가 없다.
MAX_PAGES = 12          # 폭주 방지. 현재 최대 2페이지.
DELAY = 1.0             # 요청 간격(초)


def _props(c, **params) -> dict:
    r = base.retry(lambda: c.get(URL, params=params))
    r.raise_for_status()
    time.sleep(DELAY)
    node = HTMLParser(r.text).css_first("[data-page]")
    if not node:
        raise RuntimeError(f"data-page 가 없다: {params}")
    return json.loads(node.attributes["data-page"])["props"]


def _rows(props: dict) -> list:
    """대분류에 따라 products 로 오기도 하고 productCats 로 오기도 한다."""
    box = props.get("products") or props.get("productCats") or {}
    return box.get("data") or []


def fetch() -> list[Item]:
    items: list[Item] = []
    seen, keys = set(), set()
    with base.client() as c:
        tree = _props(c)["categories"][0]["data"]
        pairs = [(c1["id"], c2["id"], c2["PRODUCT_CAT2_NM"])
                 for c1 in tree for c2 in c1.get("PRODUCT_CAT2") or []]

        for cat, sub, sub_name in pairs:
            for page in range(1, MAX_PAGES + 1):
                raw = _rows(_props(c, cat=cat, sub=sub, page=page))
                rows = [r for r in raw if r.get("dd_product_cat2_id") == sub]
                # 다음 페이지가 없으면 서버가 1페이지를 되돌려준다. 전부 기존이면 종료.
                if not rows or all(r["id"] in seen for r in rows):
                    break
                for r in rows:
                    if r["id"] in seen:
                        continue
                    seen.add(r["id"])
                    name = " ".join((r.get("TITLE") or "").split())
                    if not name:
                        continue
                    img = r.get("MAIN_IMG_FILE") or ""
                    it = Item(
                        brand=BRAND,
                        name=name,
                        name_en=" ".join((r.get("E_TITLE") or "").split()),
                        image=IMG_ROOT + img if img.startswith("/") else img,
                        category=r.get("PRODUCT_CAT1_NM") or "",
                        # 브랜드가 '신제품' 칸에 넣은 것만 True. 나머지는 모름(None).
                        is_new=True if sub_name == NEW_CAT else None,
                    )
                    # 같은 상품이 여러 칸에 걸쳐 있을 수 있다. 계약대로 key 로 지운다.
                    if it.key in keys:
                        continue
                    keys.add(it.key)
                    items.append(it)
                # 꽉 차지 않은 페이지면 다음 장이 없다. 확인 사살용 요청을 아낀다.
                # 거른 뒤가 아니라 거르기 전 개수로 본다(COFFEE 는 남의 것도 섞여 온다).
                if len(raw) < PAGE_SIZE:
                    break
    return items
