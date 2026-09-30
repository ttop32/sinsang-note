"""CU(씨유).

product.do 는 껍데기만 내려주고, 목록은 /product/productAjax.do 에 listForm 의
hidden 값을 그대로 POST 해서 받는다. 쿠키·세션 없이 열리고 브라우저도 불필요.
'더보기' 버튼도 같은 엔드포인트를 pageIndex 만 올려 다시 부르는 구조다.

신상품만 따로 모은 목록은 없다(상단 메뉴는 전체 상품 / CU 차별화 상품 / 행사상품 셋뿐).
대신 카테고리별로 최신등록순(searchCondition=setC)으로 훑으면서 NEW 태그가 붙은 것만
거두고, 태그가 끊기는 페이지에서 멈춘다. 설명문은 목록에 없어서 상세(view.do)를
상품당 한 번씩 더 본다.

NEW 배지는 진짜 최신등록 표시다. 2026-09-30 실측:
  - 최신등록순으로 끝까지 내려보면 NEW 가 특정 지점에서 뚝 끊긴다.
    음료는 40건 중 35건(1p) → 1건(2p) → 0건, 식품은 6페이지까지 붙다가 7p 6건 → 0건.
    전량에 붙는 게 아니라 앞쪽 일부에만 붙는다.
  - 상세 링크의 gdIdx 는 등록 일련번호라 페이지가 깊어질수록 단조 감소한다
    (식품 1p 중앙 28258 → 12p 중앙 26113). NEW 가 끊기는 지점의 gdIdx 는
    카테고리가 달라도 27200~27900 대로 몰려 있다. 즉 카테고리별 상위 N 개가 아니라
    '최근 등록분'이라는 전사 기준으로 붙는 배지다.
  - 앞서 '666건 전부 NEW 라 정보량이 0'이라고 본 건 NEW 인 것만 걸러 담고 나서
    그 결과를 다시 센 것이라, 배지가 무의미하다는 근거가 되지 못한다.
그래서 NEW 배지는 is_new=True 로 믿는다. 다만 배지가 붙는 기간은 알 수 없다.
날짜 필드가 없어 일수로 환산이 안 되고, 현재 NEW 가 걸린 gdIdx 폭이 950 가량이라
'오늘 나온 것'이 아니라 '최근 몇 주~몇 달'로 보는 게 맞다.

출시일·등록일은 목록에도 상세에도 없다. 상세 HTML 의 날짜처럼 보이는 문자열은
개발자가 script 태그에 남긴 주석(<!-- 2022-02-18 -->)이다. 그래서 released_at 은 비운다.
가격은 목록·상세 모두 들고 있지만(예: 5,500원) Item 에 담을 자리가 없어 버린다.
"""
import re
import time

import httpx
from selectolax.parser import HTMLParser

from . import base
from .base import UA, Item

BRAND = "CU"
LIST_URL = "https://cu.bgfretail.com/product/productAjax.do"
VIEW_URL = "https://cu.bgfretail.com/product/view.do"
REFERER = "https://cu.bgfretail.com/product/product.do?category=product&depth2=4"

# 전체상품 페이지의 3depth 탭. gomaincategory() 가 넘기는 코드값 그대로다.
CATEGORIES = {
    "10": "간편식사", "20": "즉석조리", "30": "과자류", "40": "아이스크림",
    "50": "식품", "60": "음료", "70": "생활용품",
}
MAX_PAGES = 20   # 폭주 방지. 현재 최대 9페이지(식품)에서 NEW 가 끊긴다.
DELAY = 0.15     # 요청 간격. 상세까지 합쳐 700회쯤 두드리므로 반드시 둔다.


def _text(node, sel):
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _gd_idx(card) -> str:
    """상세 링크가 a 태그로 없고 onclick="view(28352);" 로만 상품코드가 나온다."""
    for sel in (".prod_img", ".name"):
        n = card.css_first(sel)
        m = re.search(r"view\((\d+)\)", n.attributes.get("onclick", "") or "") if n else None
        if m:
            return m.group(1)
    return ""


def _labels(card) -> list:
    """1+1·2+1 배지는 span 글자로, NEW·BEST 태그는 img alt 로 붙어 있다."""
    out = []
    for sp in card.css(".badge span, .tag span"):
        t = " ".join(sp.text().split())
        if not t:
            img = sp.css_first("img")
            t = (img.attributes.get("alt", "") or "").strip() if img else ""
        t = t.upper()
        if t and t not in out:
            out.append(t)
    return out


def _promo(card) -> bool:
    """행사 상품. 마크업 주석 그대로 .badge > span.plus1 = 1+1, .plus2 = 2+1."""
    return card.css_first(".badge .plus1, .badge .plus2") is not None


def _form(cat: str, page: int) -> dict:
    """listForm 의 hidden 필드 그대로. setC=최신등록순, listType=1 은 이어붙이기."""
    return {"pageIndex": str(page), "searchMainCategory": cat, "searchSubCategory": "",
            "listType": "1", "searchCondition": "setC", "searchUseYn": "N",
            "gdIdx": "0", "codeParent": cat, "search1": "", "search2": "",
            "searchKeyword": ""}


def _fill_desc(client, items: list, gd_by_key: dict, known: dict) -> int:
    """설명문은 목록에 없으니 상세를 상품당 한 번씩 긁는다. 실패하면 빈 값으로 둔다.

    설명문은 사실상 바뀌지 않는데 상품이 600건대라 매일 전량을 다시 긁으면
    하루 700요청이 된다. 이미 받아둔 건 재사용하고 새로 나타난 것만 긁는다.
    """
    fetched = 0
    for it in items:
        cached = known.get(it.key, {}).get("desc")
        if cached:
            it.desc = cached
            continue
        gd = gd_by_key.get(it.key)
        if not gd:
            continue
        fetched += 1
        try:
            r = client.get(VIEW_URL, params={"category": "product", "gdIdx": gd})
            r.raise_for_status()
        except httpx.HTTPError:
            continue
        finally:
            time.sleep(DELAY)
        tree = HTMLParser(r.text)
        it.desc = " ".join(" ".join(n.text().split())
                           for n in tree.css(".prodExplain li")).strip()
    return fetched


def fetch(known: dict | None = None) -> list[Item]:
    items: list[Item] = []
    gd_by_key: dict = {}
    headers = {"User-Agent": UA, "X-Requested-With": "XMLHttpRequest", "Referer": REFERER}
    with base.client(headers=headers) as c:
        for code, cat_name in CATEGORIES.items():
            for page in range(1, MAX_PAGES + 1):
                r = c.post(LIST_URL, data=_form(code, page))
                r.raise_for_status()
                cards = HTMLParser(r.text).css("li.prod_list")

                fresh = 0
                for card in cards:
                    # 최신등록순이라 NEW 가 끊긴 뒤는 전부 구상품이다
                    if card.css_first(".tag .new") is None:
                        continue
                    fresh += 1
                    name = _text(card, ".name p")
                    if not name:
                        continue
                    img = card.css_first(".prod_img img")
                    src = (img.attributes.get("src", "") or "") if img else ""
                    it = Item(
                        brand=BRAND,
                        name=name,
                        image="https:" + src if src.startswith("//") else src,
                        labels=_labels(card),
                        category=cat_name,
                        is_new=True,          # NEW 배지 = 브랜드가 붙인 최근등록 표시
                        promo=_promo(card),   # 1+1·2+1 은 행사로 따로 뺀다
                    )
                    if it.key in gd_by_key:
                        continue
                    gd_by_key[it.key] = _gd_idx(card)
                    items.append(it)

                time.sleep(DELAY)
                # NEW 가 한 건도 없거나 더보기가 사라지면 이 카테고리는 끝
                if not cards or not fresh or "더보기" not in r.text:
                    break

        n = _fill_desc(c, items, gd_by_key, known or {})
        print(f"  CU 상세 요청 {n}건 (캐시 {len(items) - n}건)")
    return items
