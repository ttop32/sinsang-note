"""이디야커피.

음료(drink.html)·베이커리(bakery.html) 두 페이지가 각각 1페이지분을 서버렌더로 담고,
그 아래는 '더보기' 버튼이 ajax_brand.php 를 때린다. 쿠키·세션 없이 그대로 응답한다.
브라우저 불필요. 더보기는 8건씩, 소진되면 본문 "none" 을 돌려줘서 종료 판정이 쉽다.

목록은 최신순이 아니다. 카테고리(커피/음료/쉐이크/빙수) 블록 순서라
중간에 자르면 상품군이 통째로 빠진다. 반드시 끝까지 돌 것. 음료는 전체가 50페이지쯤 되는데
신상만 보는 용도라 앞쪽만 긁는다.
가격 정보는 페이지 어디에도 없다(용량·영양성분·알레르기만 있음).
"""
import re
import time
from datetime import datetime

import httpx
from selectolax.parser import HTMLParser

from .base import UA, Item

BRAND = "이디야커피"
BASE = "https://www.ediya.com"
MORE = BASE + "/inc/ajax_brand.php"
# product_cate: 목록 페이지 → (경로, 카테고리명)
MENUS = {7: ("/contents/drink.html", "음료"), 8: ("/contents/bakery.html", "베이커리")}
MAX_PAGES = 60   # 폭주 방지선. 실제 종료는 서버가 "none" 을 줄 때다.
DELAY = 0.4      # 연속 호출 간격(초)


def _text(node, sel):
    n = node.css_first(sel)
    return " ".join(n.text().replace("\xa0", " ").split()) if n else ""


def _uploaded_at(img_url: str) -> str:
    """이미지 파일명(IMG_1788999992703.png)이 밀리초 epoch 업로드 시각이다."""
    m = re.search(r"/IMG_(\d{13})\.", img_url)
    if not m:
        return ""
    try:
        d = datetime.fromtimestamp(int(m.group(1)) / 1000)
    except (ValueError, OSError, OverflowError):
        return ""
    # 파일명이 epoch 가 아닌 다른 13자리일 수도 있으니 상식적인 범위만 인정
    return d.date().isoformat() if 2010 <= d.year <= datetime.now().year + 1 else ""


def _new_ids(tree) -> set:
    """상단 신제품 슬라이더(ul.pro_n)에 걸린 메뉴 id. NEW 라벨 근거."""
    ids = set()
    for a in tree.css("ul.pro_n li a"):
        m = re.search(r"show_slide_detail\('(\d+)'\)", a.attributes.get("onclick") or "")
        if m:
            ids.add(m.group(1))
    return ids


def _parse(li, category: str, new_ids: set) -> Item | None:
    name = _text(li, ".menu_tt a span")
    if not name:
        return None

    img = ""
    for node in li.css("img"):
        src = node.attributes.get("src", "")
        if "/files/menu/" in src:      # 나머지는 창닫기 아이콘 같은 UI 이미지
            img = BASE + src if src.startswith("/") else src
            break

    detail = li.css_first(".pro_detail")
    menu_id = (detail.attributes.get("id", "") if detail else "").removeprefix("nutri_")

    return Item(
        brand=BRAND,
        name=name,
        name_en=_text(li, ".detail_con h2 span"),
        desc=_text(li, ".detail_txt"),
        image=img,
        labels=["NEW"] if menu_id and menu_id in new_ids else [],
        category=category,
        uploaded_at=_uploaded_at(img),
    )


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with httpx.Client(headers={"User-Agent": UA}, timeout=20, follow_redirects=True) as c:
        for cate, (path, category) in MENUS.items():
            r = c.get(BASE + path)
            r.raise_for_status()
            tree = HTMLParser(r.text)
            new_ids = _new_ids(tree)

            for page in range(1, MAX_PAGES + 1):
                if page == 1:
                    lis = tree.css("ul#menu_ul > li")      # 1페이지는 본문에 박혀 있다
                else:
                    time.sleep(DELAY)
                    r = c.post(MORE, params={"gubun": "menu_more", "product_cate": cate,
                                             "chked_val": "", "skeyword": "", "page": page})
                    r.raise_for_status()
                    if r.text.strip() == "none":           # 더 없음
                        break
                    lis = HTMLParser(f"<ul>{r.text}</ul>").css("ul > li")
                if not lis:
                    break

                # Item.key 가 괄호를 털어내서 (L)/(EX) 컵사이즈 변형이 한 건으로 합쳐진다.
                # 한 페이지가 통째로 중복일 수 있으니 중복이라고 페이지를 끊으면 안 된다.
                for it in (_parse(li, category, new_ids) for li in lis):
                    if it is None:
                        continue
                    if it.key not in seen:
                        seen.add(it.key)
                        items.append(it)
            time.sleep(DELAY)
    return items
