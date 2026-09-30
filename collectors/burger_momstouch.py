"""맘스터치.

www.momstouch.co.kr 루트는 인트로 스플래시라 본문이 없다. 실제 사이트는 /home.php 이고
메뉴는 /menu/new.php?s_sect1=<탭> 이 서버렌더로 카드를 그대로 내려준다. 브라우저 불필요.
UTF-8, 쿠키·세션 없이 열린다. 상세(view.php)는 목록에 없는 정보가 없어서 보지 않는다.

신제품 신호(2026-09-30 실측):
  - s_sect1=new 가 '신메뉴' 전용 탭이다. 이게 1순위 소스다.
  - 다만 이 탭이 NEW 를 전부 담지는 않는다. 버거 탭의 '내슈빌핫치킨버거' 는
    NEW 배지가 있는데 new 탭에는 없었다. 그래서 카테고리 탭도 같이 훑고
    카드의 <i class="new">NEW</i> 배지가 붙은 것만 거둔다 → is_new=True.
  - 배지가 없는 카드는 브랜드가 신제품이 아니라고 말한 셈이지만, 우리 용건이
    신제품이라 애초에 담지 않는다(CU 어댑터와 같은 방침).

가격은 상세 페이지에 <!-- p class="price" --> 로 주석 처리돼 있어 어디에도 안 나온다.
출시일을 말해주는 자리도 없다. 이미지 파일명의 epoch 는 released_at 이 아니라
uploaded_at 으로 넣는다(파일 업로드 시각이지 브랜드가 말하는 출시일이 아니다).
행사/할인 표시는 메뉴쪽에 없고 /promotion/list.php 가 따로 있어 promo 는 못 채운다.
"""
import re
import time
from datetime import datetime

import httpx
from selectolax.parser import HTMLParser

from . import base
from .base import UA, Item

BRAND = "맘스터치"
BASE = "https://www.momstouch.co.kr"
LIST_URL = BASE + "/menu/new.php"
NEW_TAB = "new"          # 신메뉴 전용 탭. 여기서 나머지 탭 목록도 같이 읽는다.
MAX_PAGES = 10           # 폭주 방지. 현재 카테고리당 최대 3페이지.
DELAY = 0.4              # 요청 간격(초)


def _text(node, sel):
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _uploaded_at(img_url: str) -> str:
    """이미지 경로(/upload_file/product_info/1789594226-QSQCK.png)의 앞 숫자가 epoch(초)다."""
    m = re.search(r"/(\d{10})-[A-Z]+\.", img_url)
    if not m:
        return ""
    return datetime.fromtimestamp(int(m.group(1))).strftime("%Y-%m-%d")


def _tabs(tree) -> list:
    """nav.nav-tabs 에서 대분류 탭의 s_sect1 값만 뽑는다.

    카테고리 탭을 열면 그 아래 소분류(s_sect2)까지 같이 나오는데, 소분류는
    대분류의 부분집합이라 중복 요청만 는다. s_sect2 가 붙은 링크는 버린다.
    """
    out = []
    for a in tree.css("nav.nav-tabs a"):
        href = a.attributes.get("href", "") or ""
        if "s_sect2=" in href:
            continue
        m = re.search(r"s_sect1=([A-Za-z0-9]+)", href)
        if m and m.group(1) not in out:
            out.append(m.group(1))
    return out


def _last_page(tree) -> int:
    """페이지네이션 링크에 적힌 pageNo 중 최대값. 링크가 없으면 1페이지뿐이다."""
    nums = [int(m.group(1)) for a in tree.css(".menu-pagination a")
            for m in [re.search(r"pageNo=(\d+)", a.attributes.get("href", "") or "")] if m]
    return max(nums, default=1)


def _cards(tree, category: str) -> list:
    """NEW 배지가 붙은 카드만 Item 으로. 배지 없는 건 우리 용건이 아니다."""
    items = []
    for li in tree.css(".menu-list > ul > li"):
        badge = li.css_first("i.new")
        if not badge:
            continue
        name = _text(li, "h3")
        if not name:
            continue
        style = ""
        fig = li.css_first("figure span")
        if fig:
            style = fig.attributes.get("style", "") or ""
        m = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
        img = (BASE + m.group(1)) if m and m.group(1).startswith("/") else (m.group(1) if m else "")
        # a 바로 아래 p 가 둘. class="sub-text" 는 홍보 문구, 클래스 없는 쪽이 설명이다.
        desc = ""
        for p in li.css("a > p"):
            if not (p.attributes.get("class") or ""):
                desc = " ".join(p.text().split())
                break
        items.append(Item(
            brand=BRAND,
            name=name,
            desc=desc,
            image=img,
            labels=[badge.text(strip=True).upper()],
            category=category,
            uploaded_at=_uploaded_at(img),
            is_new=True,
        ))
    return items


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()

    def take(new_items):
        for it in new_items:
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)

    with base.client(headers={"Referer": BASE + "/home.php"}) as c:
        def page(sect: str, no: int):
            r = base.retry(lambda: c.get(LIST_URL, params={"s_sect1": sect, "pageNo": no}))
            r.raise_for_status()
            return HTMLParser(r.text)

        first = page(NEW_TAB, 1)
        names = {t: t for t in _tabs(first)}      # 탭 코드는 nav 에서 실측해 따라간다
        take(_cards(first, "신메뉴"))

        for sect in names:
            if sect == NEW_TAB:
                continue
            time.sleep(DELAY)
            tree = page(sect, 1)
            label = _text(tree, "nav.nav-tabs li.current a") or sect
            take(_cards(tree, label))
            for no in range(2, min(_last_page(tree), MAX_PAGES) + 1):
                time.sleep(DELAY)
                take(_cards(page(sect, no), label))
    return items
