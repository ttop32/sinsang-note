"""미스터피자.

메뉴가 gnuboard5 게시판(/bbs/board.php?bo_table=menu)의 갤러리 목록이다.
쿠키·세션 없이 열리고 UTF-8, 브라우저 불필요. 분류(sca)당 한 장씩만 받으면 된다.
분류 목록은 첫 응답의 분류 링크에서 뽑아 쓴다(사이트가 늘려도 따라간다).

⚠️ 신제품 신호가 하나도 없는 브랜드다. 2026-09-30 실측으로 확인한 내용:
  - 분류는 클래식/프리미엄/씬크러스트/1인용 피자·피자샌드·파스타&라이스·샐러드&사이드·
    음료·특가세트 3종, 11개뿐이고 '신메뉴' 분류는 없다.
  - 목록 카드에는 이름·썸네일·분류만 있다. NEW 배지도, 등록일도 없다.
  - 상세(wr_id)까지 열어봐도 설명·가격·엣지 안내뿐이고 날짜가 어디에도 안 찍힌다.
    게시판이라 wr_id 가 커질수록 나중 글이긴 하지만, 그건 날짜가 아니라 순번이고
    분류마다 다시 매겨져서 출시일로 쓸 수 없다. 추측으로 채우지 않는다.
  - 공지/이벤트 게시판에도 신메뉴 출시 글은 없다(할인·쿠폰 안내뿐).
그래서 is_new 는 None(모름), released_at 은 빈 값으로 둔다. 이 브랜드의 신제품 판정은
전적으로 collect 단계의 어제 대비 diff 에 맡긴다.

'특가세트-*' 분류 3개는 이름 그대로 행사 묶음이라 promo 로 찍는다.
상품 페이지는 카드가 이미 달고 있는 절대주소(board.php?bo_table=menu&wr_id=N&sca=...)
를 그대로 쓴다. 추가 요청은 없다.
설명은 상세에만 있는데 상품당 1회씩 더 두드려야 해서 받지 않고 빈 값으로 둔다.
가격도 상세에만 있고 Item 에 자리가 없다.
"""
import re
import time
from urllib.parse import parse_qs, urlparse

from selectolax.parser import HTMLParser

from . import base

from .base import Item

BRAND = "미스터피자"
URL = "https://www.mrpizza.co.kr/bbs/board.php"
MAX_CATEGORIES = 30   # 폭주 방지. 현재 11개.
DELAY = 0.5           # 요청 간격(초)
PROMO_PREFIX = "특가세트"


# 상품 사진은 업로드 경로에, 배지는 스킨 경로에 있다. 배지 파일명을 열거하면
# 반드시 빠뜨린다 — new·best 만 적어놨다가 hot.png 를 놓쳐서 '핫치킨 퀘사디아'
# 자리에 HOT 아이콘이 떴다(3건). 파일명이 아니라 경로로 가른다.
_PHOTO = re.compile(r"/data/file/", re.I)


def _categories(html: str) -> list[str]:
    """분류 탭의 sca 값. 상품 링크(wr_id 가 붙은 것)는 빼고 분류 링크만 고른다."""
    out = []
    for a in HTMLParser(html).css("a[href*='bo_table=menu']"):
        q = parse_qs(urlparse(a.attributes.get("href", "")).query)
        sca = (q.get("sca") or [""])[0]
        if sca and "wr_id" not in q and sca not in out:
            out.append(sca)
    return out[:MAX_CATEGORIES]


def _cards(html: str, category: str) -> list[Item]:
    items = []
    for li in HTMLParser(html).css("#sh_gall_ul > li"):
        tit = li.css_first("a.bo_tit")
        if tit is None:
            continue
        name = " ".join(tit.text().split())
        if not name:
            continue
        # .gall_img 에 img 가 둘 이상이다. 배지(/skin/…)가 앞에 와서 css_first
        # 로 집으면 음식 사진 자리에 아이콘이 뜬다. 업로드 경로만 고른다.
        srcs = [i.attributes.get("src", "") for i in li.css(".gall_img img")]
        photo = next((u for u in srcs if _PHOTO.search(u)), "")
        is_new = any("new.png" in u.lower() for u in srcs) or None
        items.append(Item(
            brand=BRAND,
            name=name,
            image=photo,
            category=category,
            is_new=is_new,
            url=tit.attributes.get("href", ""),
            promo=category.startswith(PROMO_PREFIX),
        ))
    return items


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        first = base.retry(lambda: c.get(URL, params={"bo_table": "menu"}))
        first.raise_for_status()

        for category in _categories(first.text):
            time.sleep(DELAY)
            r = base.retry(lambda: c.get(URL, params={"bo_table": "menu",
                                                      "sca": category}))
            r.raise_for_status()
            for it in _cards(r.text, category):
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)
    return items
