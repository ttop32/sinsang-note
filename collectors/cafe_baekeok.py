"""백억커피 — 메뉴 페이지 맨 위의 '신메뉴' 슬라이드만 담는다.

(주)오가다. 2009년 한방차 '오가다' 로 시작해 2022년 커피로 전환한 곳이다.
**도메인이 이름과 안 맞는다** — `100ercoffee.com`·`baekeokcoffee.com`·
`100ercoffee.co.kr`·`baekuk.co.kr` 은 전부 NXDOMAIN 이고, 본사
`ogada.co.kr` 은 Accept 헤더를 무엇으로 바꿔도 **406 Not Acceptable** 이다.
살아 있는 공식 사이트는 `10billioncoffee.co.kr`('백억'=10 billion) 이다.

## 신메뉴 슬라이드 — 날짜까지 같이 준다

`/menu` 는 SSR 이고 맨 위에 이런 섹션이 있다.

    <section class="launch">
      <h3 class="launch-title">신메뉴</h3>
      <div class="menu-launch-slide"> <ul class="swiper-wrapper">
        <li class="swiper-slide">
          <button class="slide-btn" data-menu-idx="453">
            <picture><source srcset="…/uploads/menu_boards/20260910/b106….webp">
              <img class="figure-img" src="…/uploads/menu_boards/20260910/b106….png"
                   alt="버터 리치 크림 라떼"></picture>
            <div class="menu-content-box">
              <span class="box-title-ko">버터 리치 크림 라떼</span>
              <ul class="box-list"><li class="list-item">ICED</li></ul>

2026-10-03 실측으로 **13건**이다. 그리고 상품 이미지 경로에
`/uploads/menu_boards/YYYYMMDD/` 가 들어 있다. 13건의 분포가

    20260910  10건   20260806  1건   20260709  2건

로 **세 묶음**이라 '전부 한 날' 짜리 일괄 재업로드가 아니다. 가장 최근 묶음이
3주 전이고, 세 묶음이 각각 다른 라인업이다(밀크쉐이크·핫도그 / 선셋 코스모폴리탄 /
영암 멜론). 그래서 이 날짜를 `uploaded_at` 으로 쓴다.

`released_at` 이 아니라 `uploaded_at` 인 이유: 브랜드가 "며칠 출시"라고 말한 게
아니라 우리가 업로드 경로에서 읽은 날짜다.

⚠️ 이미지 태그가 **두 모양**이다. 대부분은 `<picture><source …><img>` 인데
영암 멜론 2건만 `<picture>` 없이 `<img src="/uploads/menu_boards/20260709/
menu-304.webp">` 다. 그래서 `picture img` 가 아니라 `img.figure-img` 로 집는다.
같은 `div.slide-feature` 안에 배경 `<img class="figure-bg">`(SVG 틀)이 하나 더
있으니 그건 클래스로 갈린다.

## 전체 메뉴판을 안 긁는 이유

같은 `/menu` 아래 `section.menu` 에 카테고리 11개(NEW·커피·디카페인·라떼·
주스&에이드·스무디·티·빙수·백억 시네마·백억 휴게소·디저트)가 있지만,
**SSR 로 내려오는 건 활성 카테고리(커피) 10건뿐**이고 나머지는 JS 가 받아 온다.
`?category=__new__`·`?category=dessert`·`?page=1` 을 다 넣어 봤지만 **응답이
한 글자도 안 바뀐다**(80KB 동일, 같은 10건). 쿼리로는 못 바꾼다.

그걸 뚫을 이유도 없다. 전체 메뉴판에는 **날짜도 NEW 배지도 없다** — 긁으면
상시 메뉴가 통째로 '신상' 이 된다. 브랜드가 이미 신메뉴를 따로 떼어
`section.launch` 에 올려 뒀고, 거기에만 날짜가 붙어 있다. 그 13건만 담는다.

`is_new=True` 는 '브랜드가 신메뉴 묶음에 올려둔 것' 이라는 뜻이다. 전건에
붙지만 배지를 센 게 아니라 **그 섹션에 있는 것만 담았기 때문**이다
(맘스터치 `/menu/new.php`·명랑핫도그 `/menu/new` 와 같은 자리).
섹션 제목이 '신메뉴' 가 아니게 되면 담지 않는다(`_NEW_WORD` 가드).

세트 메뉴('바닐라 밀크쉐이크 핫도그 세트' 등 3건)가 섞여 있는데 **어댑터가
빼지 않는다.** `Item.promo` 로 찍는 것도 아니다 — `collect.drop_sets()` 가
이름으로 거르는 게 정본이고, 어댑터마다 세트 기준을 따로 만들면 신메뉴 세트가
잘린다(Item docstring).

상품 상세 페이지가 없다(카드가 `<button data-menu-idx>` 로 영양정보 토스트를
띄운다). `Item.url` 은 비우고 SITES 폴백(/menu)에 맡긴다. 요청은 1회다.

robots.txt: 200/`User-agent: * / Allow: /` + sitemap 한 줄. 금지 경로가 없다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "백억커피"
ROOT = "https://10billioncoffee.co.kr"
MENU_URL = f"{ROOT}/menu"
LAUNCH_SECTION = "section.launch"
_NEW_WORD = "신메뉴"
MAX_ITEMS = 60          # 폭주 방지. 현재 13건이다.
DELAY = 2.0

# `/uploads/menu_boards/20260910/xxxx.png`
_UPLOAD_DAY = re.compile(r"/uploads/[a-z_]+/(\d{4})(\d{2})(\d{2})/")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _day(src: str) -> str:
    m = _UPLOAD_DAY.search(src or "")
    return "-".join(m.groups()) if m else ""


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(MENU_URL))
        r.raise_for_status()
        time.sleep(DELAY)

    doc = HTMLParser(r.text)
    sec = doc.css_first(LAUNCH_SECTION)
    if sec is None:
        raise RuntimeError(f"백억커피 {LAUNCH_SECTION} 이 없다 — /menu 구성이 바뀌었다")
    head = sec.css_first("h3.launch-title")
    title = _clean(head.text()) if head is not None else ""
    if _NEW_WORD not in title:
        raise RuntimeError(f"백억커피 신메뉴 섹션 제목이 '{title}' 다 — "
                           "'신메뉴' 묶음이 아니면 담지 않는다")

    slides = sec.css("div.menu-launch-slide li.swiper-slide")
    if not slides:
        raise RuntimeError("백억커피 신메뉴 슬라이드가 비었다 — 선택자가 깨졌다")
    if len(slides) > MAX_ITEMS:
        raise RuntimeError(f"백억커피 {len(slides)}건 — 신메뉴 묶음 치고 너무 많다. "
                           "launch 섹션이 전체 메뉴로 바뀌었을 수 있다")

    items: list[Item] = []
    seen = set()
    for li in slides:
        label = li.css_first("span.box-title-ko")
        name = _clean(label.text()) if label is not None else ""
        if not name or name in seen:
            continue
        seen.add(name)
        # ⚠️ figure-bg(배경 SVG)가 아니라 figure-img 다. <picture> 유무가 섞여 있다.
        img = li.css_first("img.figure-img")
        src = img.attributes.get("src", "") if img is not None else ""
        items.append(Item(
            brand=BRAND,
            name=name,
            image=ROOT + src if src.startswith("/") else src,
            labels=[_clean(x.text()) for x in li.css("li.list-item") if x.text().strip()],
            category=title,
            uploaded_at=_day(src),
            is_new=True,        # 브랜드가 '신메뉴' 로 떼어둔 묶음만 담는다
        ))

    if not items:
        raise RuntimeError("백억커피 0건 — box-title-ko 구조가 바뀌었다")
    items.sort(key=lambda i: i.uploaded_at, reverse=True)
    return items
