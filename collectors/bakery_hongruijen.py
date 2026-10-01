"""홍루이젠.

고도몰(GODOMALL) 이다. 목록이 쿠키·세션 없이 그대로 오고 브라우저는 필요 없다.
2026-09-30 실측.

  GET /goods/goods_list.php?cateCd=001   전체 (43종)
  GET /goods/goods_list.php?cateCd=002   신제품 (5종)

**신제품 판정은 002 분류로만 한다.** 목록 HTML 에 NEW·신상 문자열이 0회이고
.item_icon_box 는 43건 전부 비어 있다. 배지가 아예 없다. 대신 브랜드가 신제품을
분류로 따로 빼 놨고 PC 내비게이션에는 이 분류가 빠져 있다(모바일 내비에만 '신제품'
이름으로 나온다). 002 의 5건은 전부 001 안에도 있으므로 002 를 먼저 받아
번호 집합을 만들고 001 을 훑으면서 표시한다.

날짜는 어디에도 없다. 목록에도 상세에도 등록일이 안 찍히고, 공지 게시판은 마지막
글이 2022-01 이라 죽었다. 그래서 released_at·uploaded_at 둘 다 비운다.
정렬 옵션에 '등록일순' 이 있지만 순서만 바뀔 뿐 날짜를 주지는 않는다.

**요청 간격이 10초다.** robots.txt 의 Crawl-delay: 10 은 엄밀히는 Googlebot·bingbot
같은 지정 UA 그룹에 붙어 있고 우리가 걸리는 `User-agent: *` 그룹에는 없다. 그래도
같은 사이트가 밝힌 유일한 간격 요구라 그대로 지킨다. 전체 4요청이라 40초쯤 걸린다.

robots.txt: 200 text/plain 766B, 본문 첫 글자 'U'. `*` 그룹은 /admin/ /config/
/data/ /module/ /tmp/ 만 막고 Allow: / 가 그 뒤에 온다. /goods/ 는 제한 밖이다.
⚠️ 다만 고도몰이 기본으로 넣는 별도 그룹이 ClaudeBot·GPTBot 등 AI 수집 봇을
Disallow: / 로 막는다. 브랜드가 아니라 솔루션 제공사가 넣은 기본값이고 우리 UA 는
그 목록에 없어서 규칙상 허용이지만, 성격상 회색이라 여기 적어 둔다.

이용약관 문서는 사이트에서 찾지 못했다. 가격은 .item_money_box 가 비어 있어 없다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "홍루이젠"
LIST = "https://www.hongruizhen.com/goods/goods_list.php"
VIEW = "https://www.hongruizhen.com/goods/goods_view.php?goodsNo={no}"
ALL, NEW = "001", "002"
MAX_PAGES = 5    # 폭주 방지. 현재 1페이지에 전체가 다 온다.
DELAY = 10.0     # robots.txt 의 Crawl-delay

_NO = re.compile(r"goodsNo=(\d+)")


def _text(node, sel):
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _page(c, cate: str, page: int):
    params = {"cateCd": cate} | ({"page": page} if page > 1 else {})
    r = base.retry(lambda: c.get(LIST, params=params))
    r.raise_for_status()
    return HTMLParser(r.text)


def _goods_no(card) -> str:
    a = card.css_first("a[href*=goods_view]")
    m = _NO.search(a.attributes.get("href", "")) if a else None
    return m.group(1) if m else ""


def _cards(c, cate: str) -> dict:
    """번호 → 카드. 범위를 넘긴 page 는 새 번호를 안 주므로 그때 끊는다."""
    out = {}
    for page in range(1, MAX_PAGES + 1):
        doc = _page(c, cate, page)
        # 신제품 신호가 002 분류 하나뿐이라, 거기서 0건이 나와도 43건은 그대로 나오고
        # is_new 만 전부 False 가 된다. collect.py 의 0건 가드도 FLOOR 도 안 걸리는
        # 조용한 신호 손실이다. 그래서 '목록 페이지이긴 한가'를 먼저 확인한다.
        # 실측 2026-10-01: 없는 cateCd(00299)는 200 에 408바이트짜리
        # `alert('잘못된 접근입니다.')` 페이지를 주고 .goods_list 가 없다. 반면
        # 분류는 살아 있는데 상품만 0건인 경우는 브랜드의 정상 상태라 통과시킨다.
        if page == 1 and not doc.css_first(".goods_list"):
            raise ValueError(
                f"홍루이젠 cateCd={cate} 가 상품목록 페이지가 아니다(.goods_list 없음). "
                f"없는 분류코드는 200 에 alert 페이지를 준다 — "
                f"분류코드나 목록 셀렉터가 바뀌었는지 확인하라")
        cards = doc.css(".item_cont")
        fresh = {no: card for card in cards if (no := _goods_no(card)) and no not in out}
        if not fresh:
            break
        out |= fresh
        time.sleep(DELAY)
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        new_nos = set(_cards(c, NEW))
        for no, card in _cards(c, ALL).items():
            name = _text(card, ".item_name")
            it = Item(brand=BRAND, name=name)
            if not name or it.key in seen:
                continue
            seen.add(it.key)

            photo = card.css_first(".item_photo_box")
            img = card.css_first("img")
            it.desc = _text(card, ".item_name_explain")
            it.image = ((photo.attributes.get("data-image-list", "") if photo else "")
                        or (img.attributes.get("src", "") if img else ""))
            it.is_new = no in new_nos
            it.url = VIEW.format(no=no)
            items.append(it)
    return items
