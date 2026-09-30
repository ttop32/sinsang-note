"""프랭크버거.

정적 HTML 두 장이면 끝난다. 브라우저 불필요.
  /html/menu_1.html   전체 메뉴. 버거 15건 + 사이드·음료 19건. 한글명·설명·이미지·배지가 다 있다.
  /index_brand.html   홈 슬라이더. 버거 15건의 영문명을 여기서만 얻는다.
menu_2.html 부터는 404 라 메뉴 페이지는 한 장뿐이다.

조사 단계에서 열려 있던 '전체 메뉴 페이지에도 NEW 배지가 있는가'는 있다로 확인했다.
다만 클래스 이름이 다르다. 홈은 <div class="new"><p>NEW</p></div> 하나로 NEW·BEST·대표를
다 찍어서 클래스만 세면 과대집계된다(실제 NEW 는 15건 중 3건이다).
menu_1.html 은 카드마다 아이콘 div 를 따로 둔다 — icon_new / icon_best / icon_sig / icon_none.
그래서 menu_1.html 을 기준으로 삼는다. 홈은 영문명 사전으로만 쓴다.
2026-09-30 실측 두 쪽의 NEW 3건이 정확히 같다(파닭파닭 치킨버거·깐쇼새우 비프버거·맥앤치즈 비프버거).

신제품 신호:
  - is_new=True   버거 카드의 icon_new.
  - is_new=False  버거 카드의 icon_none / icon_best / icon_sig. 이 페이지는 배지가
    없는 카드에도 icon_none 을 빈 채로 꼭 찍는다. 브랜드가 '여긴 NEW 아님'을
    명시한 것이므로 모름(None)이 아니라 False 로 본다.
  - is_new=None   사이드·음료. 슬라이드에 아이콘 div 자체가 없어 신호가 없다.
출시일·등록일은 어디에도 없다. 이미지 파일명도 menu1_img39.jpg 식 일련번호라 날짜가 없다.
영문명은 menu_1.html 에선 이미지(.menu_en img, alt 비어 있음)라 홈에서 가져온다.
가격은 두 쪽 다 없다.

robots.txt 는 User-agent: * / Allow:/ 로 전체 허용이다(2026-09-30 실측).
푸터에 사이트 이용약관 자체가 없다.
"""
import re
import time
from urllib.parse import urljoin

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "프랭크버거"
ROOT = "https://www.frankburger.co.kr"
MENU_URL = ROOT + "/html/menu_1.html"
BRAND_URL = ROOT + "/index_brand.html"
DELAY = 2.5   # robots.txt 에 Crawl-delay 는 없지만 요청이 2회뿐이라 넉넉히 둔다.


def _text(node, sel) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _norm(name: str) -> str:
    """두 쪽의 상품명 띄어쓰기가 어긋나서('100% 한우갈릭' vs '100% 한우 갈릭') 공백을 턴다."""
    return re.sub(r"\s+", "", name)


def _bg_image(node, sel, page_url: str) -> str:
    """이미지가 <img> 가 아니라 style 의 background-image 로 들어있다."""
    n = node.css_first(sel)
    m = re.search(r"url\(['\"]?(.*?)['\"]?\)", n.attributes.get("style", "") if n else "")
    return urljoin(page_url, m.group(1).strip()) if m else ""


def _is_new(card) -> bool | None:
    """카드의 아이콘 div 로 판정. 아이콘 div 가 아예 없으면 신호 없음(None)."""
    for d in card.css("div"):
        cls = (d.attributes.get("class") or "").split()
        if "icon_new" in cls:
            return True
        if any(c.startswith("icon_") for c in cls):
            return False          # icon_none / icon_best / icon_sig
    return None


def _name_en_map(html: str) -> dict:
    """홈 슬라이더에서 한글명 → 영문명."""
    out = {}
    for c in HTMLParser(html).css("#menu .menu_slide .menu-container"):
        ko, en = _text(c, ".text03"), _text(c, ".text04")
        if ko and en:
            out[_norm(ko)] = en
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(MENU_URL))
        r.raise_for_status()
        menu = HTMLParser(r.text)

        time.sleep(DELAY)
        b = base.retry(lambda: c.get(BRAND_URL))
        b.raise_for_status()
        name_en = _name_en_map(b.text)

        # (분류, 카드 셀렉터). 사이드·음료 슬라이드엔 아이콘 div 가 없어 is_new 가 None 이 된다.
        for category, sel in (("버거", ".set .set_cont"),
                              ("사이드·음료", ".menu_side .swiper-slide")):
            for card in menu.css(sel):
                name = _text(card, ".menu_ko")
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    name_en=name_en.get(_norm(name), ""),
                    desc=_text(card, ".stext"),
                    image=_bg_image(card, ".img_area", MENU_URL),
                    category=category,
                    is_new=_is_new(card),
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
    return items
