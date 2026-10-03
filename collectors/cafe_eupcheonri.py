"""읍천리382 — 한 장짜리 랜딩의 '신메뉴' 섹션 하나만 담는다.

(주)원팀. 도메인이 두 개인데 **역할이 다르다.**

    eupcheonri382.co.kr          본사(주)원팀 사이트. 아임웹, 숫자 경로(/62·/66·…).
                                 기업개요·연혁·조직도·공지뿐이고 **상품이 없다.**
                                 sitemap.xml 의 47개 경로를 전부 봤고 메뉴 면이 없다.
    읍천리382.com                 브랜드 사이트. 여기에만 메뉴가 있다.
    (xn--382-v18me95c8ph.com)

본사 사이트의 내비에 걸린 브랜드 링크가 후자다. 그래서 이 어댑터가 보는 건
브랜드 쪽 하나다. (`dakdonggari.com` 도 같은 회사 링크지만 '닭동가리'라는
**다른 브랜드**라 건드리지 않는다. 브랜드 사이트의 이미지 경로가 `/img/dakdonggari/`
인 건 테마를 돌려 쓴 흔적일 뿐이다.)

## 브랜드 사이트의 모양 — 그누보드5 + 한 장짜리 랜딩

`<a href>` 로 걸린 하위 페이지는 `bbs/faq.php`·`bbs/qalist.php`·
`bbs/board.php?bo_table=location`(매장 찾기 167건)뿐이다. **상품 게시판이 없다.**
메뉴는 랜딩 HTML(516KB) 안에 섹션으로 박혀 있고, 섹션 중 상품이 들어 있는 건
`section#s4` **하나**다.

    <section class="s4" id="s4">
      <h1>읍천리382 <span>가을맞이 신메뉴</span></h1>
      <div class="owl-carousel …">
        <div class="item">
          <img src="…/img/dakdonggari/s4_img1_260928.webp">
          <div class="name">경산 대추의 깊은<br><b>풍미를 담아낸</b>
            <p>경산 대추차</p></div>

`div.name > p` 가 상품명, `div.name` 전체에서 그 이름을 뺀 앞부분이 설명이다.
나머지 섹션은 상품이 아니다 — s6=방송/리뷰 사진 21장, s3-n=인테리어 사진 10장,
s2·s3=브랜드 소개, s14·s10=창업 안내, s20=커피차 케이터링, s19=주문 사진.
`div.item` 을 사이트 전역에서 긁으면 이 사진들이 전부 '상품'이 된다.
**반드시 `section#s4` 안에서만** 긁는다.

## 신상 판정 — 배지가 아니라 섹션 자체다

여기엔 NEW 배지도, 전체 메뉴판도 없다. 브랜드가 랜딩에 **'신메뉴' 라고 제목을
붙여 따로 떼어 둔 묶음**이 전부고, 그래서 담는 8건이 전건 `is_new=True` 다.
'전건 NEW 면 가짜' 규칙과 어긋나 보이지만 성격이 다르다 — 배지가 전 상품에
붙은 게 아니라 **상품이 그 8건밖에 공개돼 있지 않다**(왓더버거의 '출시 글만
담는다'와 같은 자리다). 대신 섹션 제목이 '신메뉴' 가 아니게 되면 담지 않는다
(`_NEW_WORD` 가드) — 브랜드가 s4 를 다른 용도로 바꿔 쓰면 조용히 상시 메뉴를
퍼오게 되기 때문이다.

## 날짜 — 이미지 파일명의 YYMMDD

8건 전부 `s4_imgN_260928.webp` 다. `260928` = 2026-09-28, '가을맞이' 와 맞는다.
**이 사이트는 파일명·쿼리에 YYMMDD 를 적는 버릇이 있다**는 걸 다른 자리에서
확인했다 — `s8_content.png?ver=230707`, `s25_250417_02.png` 가 각각 2023-07-07·
2025-04-17 이고, 소스에 `<!-- 25-07-03 주미수정 -->` 같은 주석까지 같은 표기다.
Last-Modified 는 쓰지 않는다(컴포즈커피·블루샥 선례 — 배포할 때 전건이 갱신된다).

8건이 **한 날짜로 몰려 있지만 일괄 재업로드가 아니다** — 가을 신메뉴 8종을
같은 날 올린 것이고, 그게 맞는 날짜다. 일괄 재업로드가 문제인 건 '서로 다른
시기의 상품이 한 날짜를 뒤집어쓸 때' 다. 여기선 담는 게 한 묶음뿐이다.
그래도 파일명 날짜가 미래거나 말이 안 되면 **지어내지 말고 비운다**(`_day()`).

`released_at` 이 아니라 `uploaded_at` 에 넣는다. 브랜드가 "며칠에 출시한다"고
말한 게 아니라 우리가 파일명에서 읽어낸 업로드일이기 때문이다.

상품 상세 페이지가 없다(카드에 `<a>` 가 없다). `Item.url` 은 비우고 SITES 폴백에
맡긴다. 요청은 **1회**다.

robots.txt: 200/0바이트(빈 파일)라 금지 규칙이 없다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "읍천리382"
# 퓨니코드다. 읍천리382.com. httpx 가 그대로 때릴 수 있게 변환형을 박아둔다.
ROOT = "https://www.xn--382-v18me95c8ph.com"
MENU_SECTION = "section#s4"
_NEW_WORD = "신메뉴"            # 섹션 제목에 이게 없으면 담지 않는다
MAX_ITEMS = 30                  # 폭주 방지. 현재 8건이다.
DELAY = 2.0

# 파일명 꼬리의 YYMMDD. `s4_img1_260928.webp`
_FILE_DAY = re.compile(r"_(\d{2})(\d{2})(\d{2})\.[a-z]{3,4}(?:\?|$)")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _day(src: str) -> str:
    """이미지 파일명의 YYMMDD → YYYY-MM-DD. 말이 안 되면 빈 문자열."""
    m = _FILE_DAY.search(src or "")
    if not m:
        return ""
    yy, mm, dd = m.groups()
    if not ("01" <= mm <= "12" and "01" <= dd <= "31"):
        return ""
    return f"20{yy}-{mm}-{dd}"


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(ROOT + "/"))
        r.raise_for_status()
        time.sleep(DELAY)

    doc = HTMLParser(r.text)
    sec = doc.css_first(MENU_SECTION)
    if sec is None:
        raise RuntimeError(f"읍천리382 {MENU_SECTION} 이 없다 — 랜딩 구성이 바뀌었다")

    head = sec.css_first("h1")
    title = _clean(head.text()) if head is not None else ""
    if _NEW_WORD not in title:
        raise RuntimeError(f"읍천리382 {MENU_SECTION} 제목이 '{title}' 다 — "
                           "'신메뉴' 묶음이 아니면 상시 메뉴라 담지 않는다")

    cards = sec.css("div.item")
    if not cards:
        raise RuntimeError(f"읍천리382 {MENU_SECTION} 안에 상품 카드가 없다")
    if len(cards) > MAX_ITEMS:
        raise RuntimeError(f"읍천리382 {len(cards)}건 — 신메뉴 묶음 치고 너무 많다. "
                           "s4 가 전체 메뉴 캐러셀로 바뀌었을 수 있다")

    items: list[Item] = []
    seen = set()
    for card in cards:
        box = card.css_first("div.name")
        label = card.css_first("div.name p")
        if box is None or label is None:
            continue
        name = _clean(label.text())
        whole = _clean(box.text())
        # div.name 텍스트는 '설명 + 상품명' 이 이어 붙은 모양이다. 꼬리를 뗀다.
        desc = whole[:len(whole) - len(name)].strip() if whole.endswith(name) else ""
        img = card.css_first("img")
        src = img.attributes.get("src", "") if img is not None else ""
        if not name or name in seen:
            continue
        seen.add(name)
        items.append(Item(
            brand=BRAND,
            name=name,
            desc=desc,
            image=src,
            category=title,
            uploaded_at=_day(src),
            is_new=True,        # '신메뉴' 섹션만 담는다(docstring)
        ))

    if not items:
        raise RuntimeError("읍천리382 0건 — div.name 구조가 바뀌었다")
    return items
