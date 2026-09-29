"""CU(씨유).

product.do 는 껍데기만 내려주고, 목록은 /product/productAjax.do 에 listForm 의
hidden 값을 그대로 POST 해서 받는다. 쿠키·세션 없이 열리고 브라우저도 불필요.
'더보기' 버튼도 같은 엔드포인트를 pageIndex 만 올려 다시 부르는 구조다.

신상품만 따로 모은 목록은 없다. 대신 카테고리별로 최신등록순(searchCondition=setC)
으로 훑으면서 NEW 태그가 붙은 것만 거두고, 태그가 끊기는 페이지에서 멈춘다.
설명문은 목록에 없어서 상세(view.do)를 상품당 한 번씩 더 본다.

가격은 목록·상세 모두 들고 있지만(예: 5,500원) Item 에 담을 자리가 없어 버린다.
등록일·출시일은 어디에도 없어서 uploaded_at 은 비운다.
"""
import re
import time

import httpx
from selectolax.parser import HTMLParser

from .base import Item

BRAND = "CU"
LIST_URL = "https://cu.bgfretail.com/product/productAjax.do"
VIEW_URL = "https://cu.bgfretail.com/product/view.do"
REFERER = "https://cu.bgfretail.com/product/product.do?category=product&depth2=4"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0 Safari/537.36")

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


def _form(cat: str, page: int) -> dict:
    """listForm 의 hidden 필드 그대로. setC=최신등록순, listType=1 은 이어붙이기."""
    return {"pageIndex": str(page), "searchMainCategory": cat, "searchSubCategory": "",
            "listType": "1", "searchCondition": "setC", "searchUseYn": "N",
            "gdIdx": "0", "codeParent": cat, "search1": "", "search2": "",
            "searchKeyword": ""}


def _fill_desc(client, items: list, gd_by_key: dict) -> None:
    """설명문은 목록에 없으니 상세를 상품당 한 번씩 긁는다. 실패하면 빈 값으로 둔다."""
    for it in items:
        gd = gd_by_key.get(it.key)
        if not gd:
            continue
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


def fetch() -> list[Item]:
    items: list[Item] = []
    gd_by_key: dict = {}
    headers = {"User-Agent": UA, "X-Requested-With": "XMLHttpRequest", "Referer": REFERER}
    with httpx.Client(headers=headers, timeout=20, follow_redirects=True) as c:
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
                    )
                    if it.key in gd_by_key:
                        continue
                    gd_by_key[it.key] = _gd_idx(card)
                    items.append(it)

                time.sleep(DELAY)
                # NEW 가 한 건도 없거나 더보기가 사라지면 이 카테고리는 끝
                if not cards or not fresh or "더보기" not in r.text:
                    break

        _fill_desc(c, items, gd_by_key)
    return items
