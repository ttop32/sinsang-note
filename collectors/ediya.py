"""이디야커피.

음료(drink.html)·베이커리(bakery.html) 두 페이지가 각각 1페이지분을 서버렌더로 담고,
그 아래는 '더보기' 버튼이 ajax_brand.php 를 때린다. 쿠키·세션 없이 그대로 응답한다.
브라우저 불필요. 더보기는 8건씩, 소진되면 본문 "none" 을 돌려줘서 종료 판정이 쉽다.

목록은 최신순이 아니다. 카테고리(커피/음료/쉐이크/빙수) 블록 순서라
중간에 자르면 상품군이 통째로 빠진다. 반드시 끝까지 돌 것. 음료는 전체가 50페이지쯤 되는데
신상만 보는 용도라 앞쪽만 긁는다.
가격 정보는 페이지 어디에도 없다(용량·영양성분·알레르기만 있음).

신제품 신호는 각 목록 페이지 맨 위의 신제품 슬라이더(ul.pro_n) 하나뿐이다.
브랜드가 new_icon 배지를 직접 달아둔 목록이라 여기 걸린 건 is_new=True 로 본다.
같은 페이지의 나머지 상품은 브랜드가 신제품 목록에서 뺀 것이므로 is_new=False.
슬라이더를 못 읽으면(마크업 변경 등) 전량 None 으로 떨어뜨린다. 슬라이더가 비었을 때
전부 False 로 단정하면 '신제품 0건'과 '모름'을 구분할 수 없게 된다.

출시일은 어디에도 없다. 이미지 파일명의 epoch 는 업로드 시각이라 uploaded_at 에만 두고
released_at 은 비워둔다. 상세(.pro_detail)에도 영양성분·알레르기뿐이다.
"""
import re
import time
from datetime import datetime
from urllib.parse import quote

import httpx
from selectolax.parser import HTMLParser

from . import base
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


def _product_url(path: str, name: str) -> str:
    """이 상품 한 건만 남는 목록 주소.

    상품 상세 페이지가 없는 브랜드다. 상세는 목록 안에 display:none 으로 이미 박혀
    있고 show_nutri('1300') 이 그걸 펼칠 뿐이라 고유 주소가 없다(사이트맵에도
    drink.html 한 줄뿐). 대신 skeyword 가 서버측 필터라 전체 상품명을 넣으면
    그 상품만 남은 목록이 GET 으로 열린다(2026-09-30 실측: 전체명 1건, 부분명 4건).
    상세 페이지는 아니지만 사용자가 찾던 상품 앞에 떨어진다.
    """
    return f"{BASE}{path}?chked_val=&skeyword={quote(name)}#blockcate"


def _new_ids(tree) -> set:
    """상단 신제품 슬라이더(ul.pro_n)에 걸린 메뉴 id. is_new 의 근거."""
    ids = set()
    for a in tree.css("ul.pro_n li a"):
        m = re.search(r"show_slide_detail\('(\d+)'\)", a.attributes.get("onclick") or "")
        if m:
            ids.add(m.group(1))
    return ids


def _parse(li, path: str, category: str, new_ids: set) -> Item | None:
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

    # 슬라이더를 못 읽었거나 상품의 메뉴 id 를 못 뽑았으면 대조할 근거가 없다 → 모름.
    is_new = menu_id in new_ids if (new_ids and menu_id) else None

    return Item(
        brand=BRAND,
        name=name,
        name_en=_text(li, ".detail_con h2 span"),
        desc=_text(li, ".detail_txt"),
        image=img,
        category=category,
        uploaded_at=_uploaded_at(img),
        is_new=is_new,
        url=_product_url(path, name),
    )


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
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
                for it in (_parse(li, path, category, new_ids) for li in lis):
                    if it is None:
                        continue
                    if it.key not in seen:
                        seen.add(it.key)
                        items.append(it)
            time.sleep(DELAY)
    return items
