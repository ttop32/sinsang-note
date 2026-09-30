"""빽다방(더본코리아).

WordPress SSR 이라 상품·설명·영양정보가 한 페이지에 다 들어있다. 페이징도 없고
쿠키·세션도 필요 없다. 브라우저 불필요.

신제품 신호가 세 브랜드 중 제일 깔끔하다. /menu/menu_new/ 가 신메뉴 전용
카테고리다. 그 페이지에 있으면 브랜드가 신메뉴라고 말한 것이니 is_new=True,
나머지 카테고리에만 있으면 False 로 본다.

전체 카테고리를 다 받는 이유는 두 가지다.
  - 신메뉴 페이지만 받으면 수집 건수가 11↔5 처럼 출렁여서 collect 의 급감 가드
    (FLOOR)에 부분수집으로 오인당한다.
  - 같은 상품이 신메뉴와 커피에 동시에 올라와 있어서, 신메뉴를 먼저 읽고 키로
    중복을 걸러야 is_new=True 가 False 에 덮이지 않는다.

날짜는 브랜드가 주지 않는다. 이미지 경로가 /wp-content/uploads/2026/09/ 라 연·월까지는
알 수 있지만 '일'이 없다. 없는 날짜를 1일로 채우면 그건 우리가 지어낸 값이라
released_at·uploaded_at 둘 다 비워둔다. 신제품 판정은 is_new 가 받는다.

가격은 어느 경로에도 없다.

url 은 비운다. WordPress 지만 상품이 글(post)이 아니라서 permalink 가 없다
(2026-09-30 실측).
  - 카드 안에 <a> 가 0개다. id="post-N" 도 data-* 도 없다.
  - /wp-json/wp/v2/types 에 post·page·attachment 뿐이고 상품 커스텀 타입이 없다.
    상품은 카테고리 페이지 템플릿 안에 통째로 박혀 나온다.
  - 상세는 카드 안의 .hover 레이어다. 같은 페이지 요소라 주소가 없다.
카테고리 페이지(/menu/menu_coffee/ 등)로 딥링크할 수는 있지만 상품 페이지가
아니고, 우리가 화면에 올리는 건 is_new=True 인 신메뉴뿐이라 그 링크는 결국
base.SITES 폴백(/menu/menu_new/)과 같은 곳이다. 이득 없이 url 만 채우는 꼴이라 둔다.
"""
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "빽다방"
HOST = "https://paikdabang.com"
NEW_PATH = "/menu/menu_new/"
DELAY = 1.0          # 요청 간격(초)

# 신메뉴 탭을 맨 앞에 둔다. 중복 제거가 먼저 본 쪽을 남기므로 순서가 곧 우선순위다.
CATEGORIES = [
    (NEW_PATH, "신메뉴"),
    ("/menu/menu_coffee/", "커피"),
    ("/menu/menu_drink/", "음료"),
    ("/menu/menu_dessert/", "아이스크림/디저트"),
    ("/menu/menu_ccino/", "빽스치노"),
]


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _desc(card) -> str:
    """상세 레이어(.hover .txt)의 소개 문구.

    안쪽 <span> 은 '*고카페인 함유)…섭취에 주의' 주의문구 전용이라 걷어낸다.
    설명이 아니라 표시의무 문구고, 카드에 그대로 실으면 설명이 이것으로 덮인다.
    """
    node = card.css_first(".hover .txt")
    if not node:
        return ""
    for s in node.css("span"):
        s.decompose()
    return _clean(node.text())


def _cards(doc, path: str) -> list:
    """카테고리 페이지와 신메뉴 페이지의 마크업이 다르다.

    일반 카테고리는 .menu_list 격자, 신메뉴는 .new_menu_slider 슬라이더뿐이고
    격자가 아예 없다(신메뉴 그룹마다 슬라이더가 하나씩 더 생긴다).
    """
    if path == NEW_PATH:
        return doc.css(".new_menu_slider .swiper-slide")
    return doc.css(".menu_list > ul > li")


def _name(card, path: str) -> str:
    sel = ".best_tit" if path == NEW_PATH else ".menu_tit"
    n = card.css_first(sel)
    return _clean(n.text()) if n else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        for path, label in CATEGORIES:
            r = base.retry(lambda: c.get(HOST + path))
            r.raise_for_status()
            cards = _cards(HTMLParser(r.text), path)
            # 카테고리가 통째로 비면 조용한 부분수집이 된다. 예외로 올려 드러낸다.
            if not cards:
                raise RuntimeError(f"{label}({path}): 상품 0건 — 셀렉터가 깨졌을 수 있다")

            for card in cards:
                name = _name(card, path)
                if not name:
                    continue
                img = card.css_first(".thumb img") or card.css_first("img")
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=_desc(card),
                    image=img.attributes.get("src", "") if img else "",
                    category=label,
                    is_new=(path == NEW_PATH),
                )
                if it.key not in seen:        # 신메뉴가 카테고리에도 중복으로 올라와 있다
                    seen.add(it.key)
                    items.append(it)

            time.sleep(DELAY)
    return items
