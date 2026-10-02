"""카페봄봄(cafe BomBom). (주)카페봄봄, 대구.

도메인이 둘 걸린다. **cafebombom.com 은 남의 집이다** — Cloudflare 뒤에 있는
미국 식당 'Bombom Cafe' 고 메뉴 링크가 bombomcafe.com 으로 나간다. 국내
가맹본부는 **cafebombom.co.kr**(112.175.85.147, 그누보드5 + nero 테마)이다.
bombom.co.kr 은 NXDOMAIN.

대문(/)은 가맹상담 폼 한 장이라 메뉴가 없다. sitemap.xml 이 알려주는 실제
브랜드 사이트는 **/theme/nero/subpage/brand/** 아래다.

  menu_01.php  신제품          ← 신제품 신호가 여기 있다
  menu_02~10   커피/라떼/버블티/스무디/에이드/주스/티/사이드 메뉴/저당·디카페인

## 신제품 신호: '신제품' 탭에 실렸는가

2026-10-02 전수 실측(10개 탭 178행 / 중복 제거 165품목):

  - menu_01 '신제품' 13품목 = **165품목의 7.9%**. 설빙·퀴즈노스처럼 전건에
    붙는 배지가 아니다.
  - 13건 전부가 일반 탭에도 **한 번씩 더** 실려 있다(이천쌀라떼=라떼,
    서문시장땅콩빵=사이드 메뉴 …). 즉 신제품 탭은 별도 상품군이 아니라
    브랜드가 직접 고른 **큐레이션**이다. 그래서 신호로 쓸 수 있다.
  - 세 묶음으로 깔끔하게 갈린다 — 2026-09-21 7건(이천쌀 시리즈·땅콩),
    2026-07-08 3건(주스), 2026-06-02 3건(컵빙수 리뉴얼).

⚠️ **이미지 배지(.mark_wrap)는 신상 신호가 아니다.** 세 종류가 있는데
season.png 14회 / best.png 9회 / pro.png 20회고, season 은 신제품 탭 밖에도
8회 붙어 있다(라떼 3·스무디 2·사이드 3). '시즌' 과 '신제품' 은 다른 말이라
배지로 세면 신제품 탭에 없는 상시 시즌메뉴가 섞인다. **NEW 배지는 아예 없다.**

## 날짜

브랜드가 출시일을 주지 않는다. 쓸 수 있는 건 썸네일 파일명의 업로드 시각뿐이다.
  /data/menu/menu_**20260921**095237_6942.png → 2026-09-21
**uploaded_at 까지만 쓰고 released_at 에는 넣지 않는다.**

⚠️ **2025-07-16(46건)·2025-07-17(80건)은 버린다.** 둘을 합치면 178행 중
126행(71%)이고, 아메리카노·카페라떼 같은 상시 메뉴가 전부 여기 들어 있다.
사이트를 새로 만들면서 메뉴 사진을 통째로 올린 자국이다. 나머지 날짜는
하루 1~14건으로 고르다(2025-09-01 5 / 2025-10-10 3 / 2025-12-01 5 /
2026-06-02 6 / 2026-07-08 6 / 2026-09-21 14). 경계는 그 틈 한가운데인
20건에 둔다(_BULK_MIN) — 실측 분포가 14 ↔ 46 으로 끊겨 있다.

rules.untrust_bulk_dates 도 같은 일을 하지만 거기 맡기지 않는다. 그쪽은
브랜드 전체 분포의 중앙값 대비 10배를 보는데, 이 브랜드는 날짜 묶음이
13개뿐이라 중앙값이 5~6 으로 올라가 46건짜리가 안 걸린다(10배=50~60).

## 그 밖에

- 상세는 POST menu_detail_ajax.php {menu_id} → JSON 이다(menu_desc,
  menu_name_en, category_name, 영양정보). **신제품으로 판정한 것만** 받는다.
- 온도 표기는 목록의 `.c_h > span.hot/.cold` 로 온다.
- 탭 순서를 02~10 먼저 돌고 01(신제품)을 마지막에 돈다. 같은 상품이 두 번
  나오는데 category 에 '신제품' 보다 '라떼'·'사이드 메뉴' 가 남는 쪽이 낫다
  (엔제리너스는 반대로 먼저 만난 쪽을 남겨서 category 가 '❤️신제품❤️' 이 된다).
- robots.txt 는 `Disallow: /bbs/` 뿐이고 우리가 읽는 /theme/ 경로는 안 막는다.
"""
import collections
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "카페봄봄"
SITE = "https://cafebombom.co.kr"
PAGE_URL = f"{SITE}/theme/nero/subpage/brand/menu_%02d.php"
DETAIL_URL = f"{SITE}/theme/nero/subpage/brand/menu_detail_ajax.php"

# 신제품 탭은 맨 뒤에 둔다(위 docstring). 1 이 신제품, 2~10 이 일반 분류다.
PAGES = list(range(2, 11)) + [1]
NEW_PAGE = 1
DELAY = 2.0
MAX_DETAILS = 40     # 폭주 방지. 현재 신제품 13건.

# 하루에 이만큼 몰렸으면 출시일이 아니라 사이트 개편 자국이다(위 docstring).
_BULK_MIN = 20

_IMG_DATE = re.compile(r"/menu_(\d{4})(\d{2})(\d{2})\d{6}_")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _uploaded_at(img: str) -> str:
    """썸네일 파일명의 업로드 날짜(menu_20260921095237_6942.png)."""
    m = _IMG_DATE.search(img or "")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def _labels(li) -> list:
    out = []
    for sp in li.css(".c_h span"):
        cls = sp.attributes.get("class", "")
        if "hot" in cls and "HOT" not in out:
            out.append("HOT")
        elif "cold" in cls and "ICE" not in out:
            out.append("ICE")
    return out


def _detail(c, menu_id: str) -> tuple:
    """상세 JSON에서 (desc, name_en). 실패하면 조용히 빈 값으로 둔다."""
    r = base.retry(lambda: c.post(DETAIL_URL, data={"menu_id": menu_id}))
    r.raise_for_status()
    d = r.json()
    if not d.get("success"):
        return "", ""
    m = d.get("menu") or {}
    return _clean(m.get("menu_desc")), _clean(m.get("menu_name_en"))


def fetch() -> list[Item]:
    items: list[Item] = []
    by_id: dict = {}
    with base.client() as c:
        first = True
        for n in PAGES:
            if not first:
                time.sleep(DELAY)
            first = False
            r = base.retry(lambda: c.get(PAGE_URL % n))
            r.raise_for_status()
            doc = HTMLParser(r.text)
            h = doc.css_first(".product .stitle h2")
            cat = _clean(h.text()) if h else ""
            cards = doc.css(".product .wrap .item")
            # 한 탭이 통째로 비면 셀렉터가 깨진 것이다. 조용히 넘기지 않는다.
            if not cards:
                raise RuntimeError(f"카페봄봄 menu_{n:02d} 0건 — 셀렉터가 깨졌을 수 있다")
            for li in cards:
                a = li.css_first("a[data-menu-id]")
                mid = a.attributes.get("data-menu-id", "") if a else ""
                nm = li.css_first(".name_box h2")
                name = _clean(nm.text()) if nm else ""
                if not name:
                    continue
                old = by_id.get(mid)
                if old is not None:
                    # 신제품 탭을 마지막에 도니, 여기 걸리는 건 신제품 쪽이다.
                    if n == NEW_PAGE:
                        old.is_new = True
                    continue
                img = li.css_first(".pro_imgbox img")
                src = img.attributes.get("src", "") if img else ""
                en = li.css_first(".name_box h3")
                it = Item(
                    brand=BRAND,
                    name=name,
                    name_en=_clean(en.text()) if en else "",
                    image=src,
                    labels=_labels(li),
                    category=cat,
                    uploaded_at=_uploaded_at(src),
                    # 일반 탭에만 있는 상품은 '신제품 탭에 없음' 을 확인한 것이다.
                    is_new=(n == NEW_PAGE),
                )
                by_id[mid] = it
                items.append(it)

        if not items:
            raise RuntimeError("카페봄봄 0건 — 경로나 셀렉터가 바뀌었을 수 있다")

        # 사이트 개편 때 몰아 올린 날짜를 지운다(위 docstring).
        bulk = {d for d, n in collections.Counter(
            i.uploaded_at for i in items if i.uploaded_at).items() if n >= _BULK_MIN}
        for it in items:
            if it.uploaded_at in bulk:
                it.uploaded_at = ""

        ids = {id(v): k for k, v in by_id.items()}
        for it in [i for i in items if i.is_new][:MAX_DETAILS]:
            mid = ids.get(id(it), "")
            if not mid:
                continue
            time.sleep(DELAY)
            desc, en = _detail(c, mid)
            it.desc = desc
            it.name_en = it.name_en or en

    return items
