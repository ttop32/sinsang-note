"""배스킨라빈스.

/menu/fom.php('이달의 맛') 한 장이 SSR 로 다 나온다. 요청 1회면 끝이고 브라우저 불필요.
전체 메뉴(/menu/list.php)는 받지 않는다. 이 브랜드는 상시 맛이 수백 가지인데
신제품 신호가 없어서 긁어봐야 카탈로그만 불어난다. 게다가 robots.txt 가 없는
브랜드(404, HTML 404 페이지를 돌려준다)라 요청을 최소로 두는 게 맞다.

페이지에 상품이 두 군데 있다.
  - '이달의 맛' 본문 1건 — 영문명·설명·큰 이미지가 다 있다.
  - '이달의 신제품' 슬라이더 N건 — 이름과 썸네일만 있다.
둘이 같은 상품일 때가 많아(2026-09 실측: 둘 다 '도쿄바나나 크렘브륄레') key 로 겹치면
정보가 많은 본문 쪽을 남긴다. 월 1~2건이라 양은 적지만 오보 위험이 거의 없다.

신제품 신호:
  - is_new  '이달의 맛/이달의 신제품' 이니 전건 True.
  - released_at  페이지 머리글이 '9월 이달의 맛' 이라 월만 준다. 연도는 없어서
    실행 시점 연도를 붙이고 그 달의 1일로 둔다. 연말·연초에 브랜드가 페이지를
    늦게 갈면 미래 날짜가 나오므로, 이번 달보다 앞서면 작년으로 내린다.
    '며칠에 나왔는지'가 아니라 '몇 월 것인지'라는 점은 감안해야 한다.
가격은 상품 상세(/menu/view.php?seq=…)에 있지만 Item 에 자리가 없어 받지 않는다.
"""
import re
import time
from datetime import date
from urllib.parse import urljoin

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "배스킨라빈스"
ROOT = "https://www.baskinrobbins.co.kr"
URL = ROOT + "/menu/fom.php"
DELAY = 2.5   # robots.txt 가 없는 브랜드다. 허용도 금지도 아니니 간격을 길게 잡는다.


def _text(node, sel) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _image(node, sel) -> str:
    n = node.css_first(sel)
    src = n.attributes.get("src", "").strip() if n else ""
    return urljoin(ROOT, src) if src else ""


def _released_at(html: str, today: date) -> str:
    """머리글의 '9월' + 실행 연도 → 그 달 1일."""
    m = re.search(r"(\d{1,2})\s*월", _text(HTMLParser(html), ".page-header__number"))
    if not m:
        return ""
    month = int(m.group(1))
    if not 1 <= month <= 12:
        return ""
    year = today.year - 1 if month > today.month else today.year
    return f"{year:04d}-{month:02d}-01"


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(URL))
        r.raise_for_status()
        time.sleep(DELAY)
        page = HTMLParser(r.text)
        released = _released_at(r.text, date.today())

        fom = page.css_first(".menu-fom__container")
        if fom:
            name = _text(fom, "h3.menu-fom__title")
            if name:
                items.append(Item(
                    brand=BRAND,
                    name=name,
                    name_en=_text(fom, ".menu-fom__title--en"),
                    desc=_text(fom, ".menu-fom__text"),
                    image=_image(fom, ".menu-fom__image"),
                    category="이달의 맛",
                    released_at=released,
                    is_new=True,
                ))
                seen.add(items[0].key)

        for slide in page.css(".menu-fom-new .swiper-slide"):
            name = _text(slide, ".menu-fom-new__name")
            if not name:
                continue
            it = Item(
                brand=BRAND,
                name=name,
                image=_image(slide, ".menu-fom-new__image"),
                category="이달의 신제품",
                released_at=released,
                is_new=True,
            )
            if it.key in seen:
                continue          # 본문의 '이달의 맛'과 같은 상품이다
            seen.add(it.key)
            items.append(it)
    return items
