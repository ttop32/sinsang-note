"""메가MGC커피.

menu.php 가 쿠키·세션 없이 HTML 조각을 그대로 돌려준다. 브라우저 불필요.
카테고리 파라미터는 먹지 않아서(빈 응답) 전체 조회만 쓴다.
"""
import re
import httpx
from selectolax.parser import HTMLParser

from . import base
from .base import UA, Item

BRAND = "메가MGC커피"
URL = "https://www.mega-mgccoffee.com/menu/menu.php"
MAX_PAGES = 30  # 폭주 방지. 현재 4페이지.


def _text(node, sel):
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _uploaded_at(img_url: str) -> str:
    """이미지 파일명 앞의 업로드 타임스탬프(20260916234952)를 날짜로."""
    m = re.search(r"/(\d{4})(\d{2})(\d{2})\d{6}_", img_url)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            r = c.get(URL, params={"page": page, "menu_category1": "",
                                   "menu_category2": "", "category": ""})
            r.raise_for_status()
            cards = HTMLParser(r.text).css("ul#menu_list > li")
            if not cards:
                break

            parsed = []
            for card in cards:
                name = _text(card, ".cont_text_title b")
                if not name:
                    continue
                img_node = card.css_first(".cont_gallery_list_img img")
                img = img_node.attributes.get("src", "") if img_node else ""
                parsed.append(Item(
                    brand=BRAND,
                    name=name,
                    name_en=_text(card, ".cont_text_title + .cont_text_info .text1"),
                    desc=_text(card, ".cont_text_info .text2"),
                    image=img,
                    labels=[n.text().strip() for n in card.css(".cont_gallery_list_label")],
                    uploaded_at=_uploaded_at(img),
                ))

            # 범위를 넘긴 page는 서버가 1페이지를 되돌려주므로, 전부 기존 키면 종료
            if not parsed or all(it.key in seen for it in parsed):
                break

            for it in parsed:
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)
    return items
