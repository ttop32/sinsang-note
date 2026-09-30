"""커피빈.

/menu/list.asp 가 쿠키·세션 없이 상품을 서버렌더로 다 내려준다. 브라우저 불필요.
Content-Type 이 Charset=UTF-8 이고 실제로도 UTF-8 이다(오래된 ASP 지만 EUC-KR 아님).

카테고리 목록은 페이지 안의 전역 내비(a[href*="/menu/list.asp?category="])에서 읽는다.
어댑터에 14개를 박아두면 브랜드가 카테고리를 늘렸을 때 조용히 빠진다.
페이지당 9건 고정이고 범위를 넘긴 page 는 카드 0개를 준다(1페이지로 되돌리지 않는다).
2026-09-30 실측 14분류·166건·40요청.

신제품 신호는 '신음료'(category=32) 카테고리 하나뿐이다.
  - 신음료에 든 상품만 is_new=True.
  - 나머지는 None 으로 둔다. False 가 아니다. 카테고리 밖에 있다는 게
    신제품이 아니라는 뜻은 아니고(푸드·베이커리 신상은 들어갈 자리가 없다),
    브랜드가 "이건 신제품이 아니다"라고 말한 적도 없다.
  - 배지·출시일·등록일은 어디에도 없다. 그래서 released_at 은 전건 빈 값이고,
    신음료 밖 상품의 신제품 판정은 collect 단계의 어제 대비 diff 에 맡긴다.
신음료가 28건으로 꽤 많다. 브랜드가 시즌 라인업을 통째로 두는 카테고리라
'오늘 나온 것'보다는 '요즘 것'에 가깝다. 날짜가 없어서 collect.py 의 STALE 가지치기가
걸리지 않으니, 오래 걸려 있는 상품이 계속 NEW 로 보일 수 있다.

가격은 페이지에 없다(영양정보만 있다). 영양정보는 Item 에 자리가 없어 버린다.
"""
import re
import time
from urllib.parse import quote, urljoin

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "커피빈"
ROOT = "https://www.coffeebeankorea.com"
URL = ROOT + "/menu/list.asp"
NEW_CATEGORY = "32"   # '신음료'. 이 브랜드의 유일한 신제품 신호다.
DELAY = 1.0
MAX_PAGES = 15        # 폭주 방지. 현재 최대 4페이지.


def _text(node, sel) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _image(src: str) -> str:
    """이미지 경로에 한글과 대괄호가 들어있다(/data/menu/[홈페이지]…jpg). 인코딩해 둔다."""
    return urljoin(ROOT, quote(src, safe="/:")) if src else ""


def _categories(html: str) -> dict:
    """전역 내비에서 category 번호 → 이름. '신음료'를 먼저 훑도록 순서를 지킨다."""
    cats = {}
    for a in HTMLParser(html).css('a[href*="/menu/list.asp?category="]'):
        m = re.search(r"category=(\d+)", a.attributes.get("href", ""))
        if m:
            cats.setdefault(m.group(1), " ".join(a.text().split()))
    return cats


def _cards(html: str, category: str, is_new) -> list[Item]:
    out = []
    for li in HTMLParser(html).css("ul.menu_list > li"):
        name = _text(li, ".kor")
        if not name:
            continue
        img = li.css_first("figure.photo img")
        out.append(Item(
            brand=BRAND,
            name=name,
            name_en=_text(li, ".eng"),
            desc=_text(li, "dl.txt dd"),
            image=_image(img.attributes.get("src", "") if img else ""),
            category=category,
            is_new=is_new,
        ))
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        first = base.retry(lambda: c.get(URL, params={"category": NEW_CATEGORY}))
        first.raise_for_status()
        cats = _categories(first.text)

        # '신음료'를 먼저 처리한다. 다른 분류에 같은 상품이 겹쳐 있어도
        # is_new=True 쪽이 남도록.
        order = [NEW_CATEGORY] + [k for k in cats if k != NEW_CATEGORY]

        for cat in order:
            name = cats.get(cat, "")
            is_new = True if cat == NEW_CATEGORY else None
            for page in range(1, MAX_PAGES + 1):
                if cat == NEW_CATEGORY and page == 1:
                    html = first.text           # 위에서 이미 받았다
                else:
                    time.sleep(DELAY)
                    r = base.retry(lambda ct=cat, p=page:
                                   c.get(URL, params={"category": ct, "page": p}))
                    r.raise_for_status()
                    html = r.text

                parsed = _cards(html, name, is_new)
                if not parsed:
                    break
                for it in parsed:
                    if it.key not in seen:
                        seen.add(it.key)
                        items.append(it)
    return items
