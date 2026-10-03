"""디저트39.

공식 도메인은 **dessert39.com** 이다((주)에스엠씨인터내셔널). 루트(`/`)는 18KB
짜리 리다이렉트 셸이고 본체는 `/main.php` 다. robots.txt 는
`Disallow: /bbs/ · /adm/ · /html/pages/backup/` 세 줄뿐이라 우리가 읽는
`/html/pages/menu_*.php` 는 걸리지 않는다.

메뉴 면이 내비게이션에는 다섯 개로 걸려 있는데 **실제로 사는 건 세 개**다.
    /html/pages/menu_beverage.php     음료   820KB · 404건
    /html/pages/menu_dessert.php      디저트 421KB · 196건
    /html/pages/menu_md_product.php   MD    146KB ·  61건
    /html/pages/menu_doughnut.php     ⚠️ 죽었다. 응답이 main.php 와 **바이트까지
    /html/pages/menu_xmas.php            동일**(156,836B)하다. 상품 0건.
세 면이 전부 SSR 이라 요청 **3회**로 661행을 받는다. 브라우저도 API 도 필요 없다.

구조는 `<div class="cont-wrap"><h2>섹션명</h2> … <div class="product-container">
<div class="product">` 다. 상품 하나에 이름(`.tit`)·규격(`.engtit`)·가격·
설명(`.detail`)·사진이 다 들어 있다.

⚠️ **같은 상품이 여러 섹션에 실린다.** 661행 중 **136행이 중복**이라 make_key
로 접으면 **450건**이다(우베라떼가 SEASON & NEW 와 COFFEE 에 같이 있는 식,
그리고 `꿀고구마라떼` 450ml/650ml 처럼 규격만 다른 쌍). 섹션을 페이지 순서대로
돌면서 **먼저 나온 것을 남긴다** — 신메뉴 섹션이 맨 앞이라 거기 판정이 이긴다.

신제품 신호(2026-10-03 전수 실측):
  - **배지 마크업이 없다.** 카드가 `<div class="product ">` 로 뒤에 빈 자리가
    있어 조건부 클래스처럼 보이지만 **404건 전부 빈 문자열**이다. 버거운버거의
    `hidden` 빈 템플릿처럼 세면 전건이 신상이 되는 자리다.
  - 날짜는 **사진 파일명 앞의 10자리 epoch** 에서 얻는다.
    `/data/product/1780359689_7448_<base64>_<base64>.png`
      · 661행 중 407행에 붙는다. 나머지 254행은 epoch 없이 base64 로만 된 옛
        파일명이라 **비운다**(지어내지 않는다).
      · 면마다 사정이 다르다 — 음료는 404건 중 389건에 붙는데 디저트는 196건
        중 14건, MD 는 61건 중 4건뿐이다.
  - ⚠️ **2025-06-20 에 141건, 2025-06-19 에 83건**이 몰려 있다. 224건짜리
    사이트 구축 일괄이다. 16개월 전이라 60일 창에 들어올 일은 없지만, 탐앤탐스
    2025-05-14/15·컴포즈커피 2026-06-16 과 같은 성격이라 **버린다**(BULK_DAYS).
    나머지는 2026-09-16 2건, 2026-08-13 16건, 2026-07-27 5건, 2026-06-02 4건,
    2026-04-13 12건 … 식으로 출시 묶음 단위로 흩어진다.
  - 이건 사진 업로드 시각이지 브랜드가 공표한 출시일이 아니다.
    `released_at` 이 아니라 `uploaded_at` 에 넣는다.
  - 섹션 이름을 신호로 쓰는 건 **음료의 `SEASON & NEW MENU` 하나뿐**이다.
      · 44건 / 661행 = 6.7%. 블루샥 4.3%·탐앤탐스 17.6% 와 같은 자릿수다.
      · 44건 **전건에 날짜가 있다.**
      · 다만 **쌓이는 섹션**이다 — 2025-06-19 짜리 `저당 바닐라라떼`,
        2025-08-27 `슈팅 망고 팝` 이 아직 들어 있고 가장 최근이 2026-06-02 다.
        그래서 `is_new` 는 **이 섹션 + 날짜가 있을 때만** True 로 둔다. 날짜가
        있으면 rules.is_fresh 가 60일로 다시 거르니 옛 시즌메뉴는 자동으로 빠진다.
  - 🔴 **디저트 면의 `NEW & BEST MENU`(44건)는 쓰지 않는다.** 이름부터 NEW 와
    BEST 를 한 칸에 섞어 놓은 섹션이고, 44건 중 날짜가 붙는 게 6건뿐이라
    날짜로 거를 수도 없다. 설빙에서 `span.flag` 에 시그니처 배지와 NEW 배지가
    섞여 있는 걸 존재만 보고 세어 2013년 인절미설빙이 신상이 된 것과 같은
    함정이다. 이 면 상품도 수집은 하되 `is_new` 는 비운다.
  - 나머지는 `is_new` 를 **False 가 아니라 None** 으로 둔다. 브랜드가 '신제품
    아님' 이라고 말한 적이 없고, False 를 찍으면 rules 가 released_at 만 보게
    돼서 uploaded_at 경로가 통째로 막힌다.

MD 면(61건)은 `MD Food` 섹션 1건(`스페셜티 블랜딩(1kg)` — 원두다)만 빼고
전부 굿즈라 `nonfood=True` 로 찍는다. 이름만 보는 base.is_nonfood 로는
`토네이도 쉐이커`·`크롬실버컵`·`데코픽 3종`·`러브베어 캔들`·`티아라`·
`키치베어 DIY 키트`·`폼타월`·`패딩 홀더` 같은 게 줄줄 새서(61건 중 25건이
안 걸린다) 섹션을 믿는다 — 탐앤탐스 MD 탭과 같은 처리다.

사진 주소가 `https://dessert39.com:443/…` 로 포트가 붙어 나온다. 그대로 둬도
열리지만 보기 나빠서 `:443` 만 떼고 쓴다. http 가 아니라 https 라
base.derive() 가 지우지 않는다.

상품별 상세 페이지는 없다(`자세히보기` 가 같은 페이지 안 모달이다).
`url` 은 비우고 SITES 폴백에 맡긴다.
"""
import datetime
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "디저트39"
SITE = "https://dessert39.com"
PAGES = (
    ("menu_beverage", "음료"),
    ("menu_dessert", "디저트"),
    ("menu_md_product", "MD"),
)
MD_PAGE = "menu_md_product"
MD_FOOD_SECTION = "MD Food"       # MD 면에서 유일하게 먹는 것(원두)
NEW_SECTION = "SEASON & NEW MENU"  # 음료 면의 신메뉴 섹션. 디저트 면 것은 안 쓴다
DELAY = 2.0
MIN_ITEMS = 300                   # 현재 450건

# 사진 파일명 앞의 10자리 epoch. `/data/product/1780359689_7448_….png`
_TS = re.compile(r"/data/product/(\d{10})_")

# 사이트 구축 일괄. 출시일이 아니다(docstring 참고).
BULK_DAYS = {"2025-06-19", "2025-06-20"}


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _image(src: str) -> str:
    """`https://dessert39.com:443/…` 의 군더더기 포트만 뗀다."""
    return (src or "").replace("https://dessert39.com:443/", SITE + "/")


def _day(src: str) -> str:
    m = _TS.search(src or "")
    if not m:
        return ""
    day = datetime.datetime.fromtimestamp(int(m.group(1))).strftime("%Y-%m-%d")
    return "" if day in BULK_DAYS else day


def _section_title(cw) -> str:
    """섹션 제목. 가격 주의문구·부연설명이 h2 안에 섞여 있어 떼고 쓴다."""
    h = cw.css_first("h2")
    if h is None:
        return ""
    for junk in h.css(".store_pay, .sub-txt"):
        junk.decompose()
    return _clean(h.text())


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        for n, (page, page_name) in enumerate(PAGES):
            if n:
                time.sleep(DELAY)
            r = base.retry(lambda page=page: c.get(f"{SITE}/html/pages/{page}.php"))
            r.raise_for_status()
            doc = HTMLParser(r.text)
            for cw in doc.css(".cont-wrap"):
                section = _section_title(cw)
                for pr in cw.css(".product"):
                    tit = pr.css_first(".tit")
                    name = _clean(tit.text()) if tit else ""
                    if not name:
                        continue
                    img = pr.css_first("img")
                    src = _image(img.attributes.get("src", "") if img else "")
                    day = _day(src)
                    eng = pr.css_first(".engtit")
                    det = pr.css_first(".detail")
                    it = Item(
                        brand=BRAND,
                        name=name,
                        desc=_clean(det.text()) if det else "",
                        image=src,
                        # 규격(650ml 빅벤티 등)은 상품명이 아니라 컵 크기다. 라벨로 둔다.
                        labels=[_clean(eng.text())] if eng and _clean(eng.text()) else [],
                        category=f"{page_name}/{section}" if section else page_name,
                        uploaded_at=day,
                        # 섹션만으로는 못 믿는다. 날짜가 같이 있을 때만 신제품으로 본다.
                        is_new=True if (section == NEW_SECTION and day) else None,
                        nonfood=(page == MD_PAGE and section != MD_FOOD_SECTION),
                    )
                    # 같은 상품이 여러 섹션에 실린다. 먼저 나온 쪽(신메뉴 섹션이
                    # 맨 앞이다)을 남긴다.
                    if it.key in seen:
                        continue
                    seen.add(it.key)
                    items.append(it)

    if len(items) < MIN_ITEMS:
        raise RuntimeError(f"디저트39 {len(items)}건 — 메뉴 면 구조가 바뀌었을 수 있다")
    # 날짜가 통째로 사라지면 사진 파일명 규칙이 바뀐 것이다. 조용히 넘기지 않는다.
    if not any(it.uploaded_at for it in items):
        raise RuntimeError("디저트39 날짜가 0건 — 사진 파일명의 epoch 규칙이 바뀌었다")
    return items
