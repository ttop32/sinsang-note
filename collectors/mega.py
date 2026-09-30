"""메가MGC커피.

menu.php 가 쿠키·세션 없이 HTML 조각을 그대로 돌려준다. 브라우저 불필요.
카테고리 파라미터는 먹지 않아서(빈 응답) 전체 조회만 쓴다.

신제품 신호가 없는 브랜드다. 2026-09-30 실측으로 확인한 내용:
  - 카드의 .cont_gallery_list_label 은 ICE(63)/HOT(45) 뿐이다. NEW 배지는 없다.
  - /menu/ 의 카테고리는 음료·푸드·상품 셋뿐이고 '신메뉴' 목록은 없다.
    '가을시즌 신메뉴' 문구가 있지만 상품 목록이 아니라 배너 이미지 한 장이다.
  - 게시판(/bbs/)에 신메뉴 공지가 올라오긴 해도 상품 목록이 아니라 글이다.
    글 제목을 상품에 끼워맞추는 건 추측이라 하지 않는다.
그래서 is_new 는 None(모름)으로 둔다. 이 브랜드의 신제품 판정은 전적으로
collect 단계의 어제 대비 diff 에 맡긴다.
"""
import re
import httpx
from selectolax.parser import HTMLParser

from . import base
from .base import UA, Item

BRAND = "메가MGC커피"
URL = "https://www.mega-mgccoffee.com/menu/menu.php"
MAX_PAGES = 30  # 폭주 방지. 한 페이지 20건, 현재 11페이지.


def _text(node, sel):
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _uploaded_at(img_url: str) -> str:
    """이미지 파일명 앞의 업로드 타임스탬프(20260916234952)를 날짜로.

    released_at 에는 넣지 않는다. 브랜드가 말하는 출시일이 아니라 파일 업로드 시각이고,
    실제로 173건 중 81건이 2024-06 한 달에 몰려 있다(이미지 일괄 재업로드 흔적).
    그 81건을 그날 출시된 신제품으로 내보내면 그대로 오보다.
    """
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
