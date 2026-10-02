"""하이오커피(HIO COFFEE).

hiocoffee.co.kr 로 들어가면 **hiocoffee.com 으로 302** 된다. 본체는 .com 이다.
루트(`/`)는 BRAND / FRANCHISE / HIO ORDER 세 칸짜리 스플래시라 본문이
67자뿐이다. 브랜드 사이트 본체는 `/main.html` 이고, 메뉴는 그 아래 두 장이다.
정적 HTML + jQuery 다. 브라우저 불필요.

  /sub/menu/list.html                    '신메뉴' 탭 (내비의 첫 칸)
  /sub/menu/list2.html?searchCate=<n>    '메뉴' 탭. n 은 내비 순서 그대로다
      2 커피 / 3 콜드 브루 / 4 논커피 / 5 프라페·블렌디드 / 6 에이드·티 /
      7 시그니처 / 8 1리터 보틀 / 9 디저트 / 10 아이스크림
  ⚠️ **searchCate=1 이 바로 그 '신메뉴'다.** list.html 과 같은 40건이 온다
     (상품의 data-cate 가 전부 '1'). 그래서 list.html 은 안 때리고
     카테고리 1~10 을 같은 코드로 돈다 — 요청이 하나 준다.

페이징은 '더보기' 버튼이 `?page=N&ajax=1` 로 같은 경로를 때려 `<li>` 조각을
덧붙이는 구조다. 페이지당 12건이고 1페이지 HTML 안에
`var totalCount = <전체>` 가 박혀 있어서 그걸 보고 멈춘다.
2026-10-02 실측 건수: 1=40, 2=20, 3=14, 4=16, 5=15, 6=18, 7=10, 8=40, 9=56,
10=8 → 합계 237, 요청 약 25회.

상품 데이터는 `a.menu-item-link` 의 data-* 에 들어 있다. 모달을 따로 받을
필요가 없다.
  data-title(국문) / data-subtitle(영문) / data-label1(설명) /
  data-sublabel1(알레르기) / data-size(HOTICE|ICE|빈값) / data-file(이미지
  파일명) / data-cate / data-nutrition(JSON)
이미지는 `https://hiocoffee.com/files/product/<data-file>` 이다(https 정상).

신제품 신호(2026-10-02 실측):
  - 브랜드가 **'신메뉴'를 별도 카테고리(cate=1)로 분리**해 두었고, 내비에서도
    '메뉴'와 나란히 첫 칸이다.
  - 교차검증: cate=1 의 40건을 나머지 9개 카테고리 197건과 이름으로 대조했더니
    **겹치는 게 하나도 없다.** 신메뉴는 승격되면 cate 를 옮기는 운영이라는
    뜻이고, '신메뉴 탭에 상시 메뉴가 같이 걸려 있는' 모양이 아니다.
    (탐앤탐스는 반대로 전용 목록과 isNew 가 완전히 겹쳤다. 어느 쪽이든
     두 집합을 실제로 대조해 봐야 안다.)
  - 비율은 40/237 = **16.9%** 다. 탐앤탐스(17.6%)·만월경(17.1%)과 같은 대역이고
    버거킹(31%)·퀴즈노스(100%)처럼 쏠려 있지 않다.
  - 그래서 cate=1 은 is_new=True, 나머지는 is_new=False 로 내보낸다.
    브랜드가 직접 갈라 놓은 묶음이라 '모름'이 아니다.
  - ⚠️ 40건은 적은 수가 아니다. 쌍화차·유자생강차(겨울)와 딸기·수박(여름)이
    같이 들어 있어서 **1년치가 쌓여 있는 탭**으로 보인다. 날짜가 없으니
    rules.is_fresh 의 STALE(90일, first_seen 기준) 가드에 맡긴다.

**날짜는 없다.** 실측한 후보와 기각 사유 —
  - 목록·상세 어디에도 날짜 텍스트가 0건이다.
  - data-file 은 md5 해시(`b5d87671c3c8cbc606e30c0c8dc84235.png`)라 시각이 없다.
  - 이미지 Last-Modified 는 쓰지 않는다. 컴포즈커피(2026-06-16 149건)·
    블루샥(배포 시각)에서 가짜로 판명된 것과 같은 함정이다.
  released_at·uploaded_at 둘 다 비운다.

굿즈 카테고리가 없다. 237건 전부 먹는 것이다.

상품 상세 주소가 없다 — `href="#"` 에 jQuery 가 모달을 띄울 뿐이다.
Item.url 을 비우고 SITES 폴백에 맡긴다.

8번 '1리터 보틀'은 같은 음료의 대용량 라인이라 이름이 2번 '커피'와 겹친다
(`카페라떼` ↔ `카페 라떼`). base.make_key 가 공백을 털기 때문에 한 건으로
접힌다. 일부러 두는 동작이다 — 화면에 같은 카드를 두 장 그리지 않는다.

robots.txt 는 **404**(Apache 기본 404)다. 403 이 아니므로 RFC 9309 상
'규칙 명시 없음'이다(매머드커피와 같은 처지). 규칙이 없는 만큼 간격은 2초를 쓴다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "하이오커피"
SITE = "https://hiocoffee.com"
LIST_URL = f"{SITE}/sub/menu/list2.html"
IMG_BASE = f"{SITE}/files/product/"
DELAY = 2.0

# 내비 순서 그대로다. 1 이 '신메뉴' 탭(= /sub/menu/list.html 과 같은 목록).
NEW_CATE = 1
CATEGORIES = {
    1: "신메뉴", 2: "커피", 3: "콜드 브루", 4: "논커피", 5: "프라페·블렌디드",
    6: "에이드·티", 7: "시그니처", 8: "1리터 보틀", 9: "디저트", 10: "아이스크림",
}
PAGE_ROW = 12        # 서버가 쓰는 페이지 크기. 1페이지 스크립트에 박혀 있다
MAX_PAGES = 12       # 폭주 방지. 현재 가장 큰 9번(56건)이 5페이지다
MIN_ITEMS = 120      # 이보다 적으면 마크업이 바뀐 것이다. 현재 237건

_TOTAL = re.compile(r"var\s+totalCount\s*=\s*(\d+)")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _labels(size: str) -> list:
    """제공 온도. data-size 가 'HOTICE' / 'ICE' / 빈값(디저트) 세 가지다."""
    s = (size or "").upper()
    if s == "HOTICE":
        return ["HOT", "ICE"]
    return [s] if s in ("HOT", "ICE") else []


def _cards(doc) -> list:
    return doc.css("a.menu-item-link")


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client(headers={"Referer": LIST_URL}) as c:
        for cate, label in CATEGORIES.items():
            total = None
            got = 0
            for page in range(1, MAX_PAGES + 1):
                if items or page > 1:
                    time.sleep(DELAY)
                params = {"searchCate": cate, "page": page}
                if page > 1:
                    params["ajax"] = 1      # 더보기는 조각만 돌려준다
                r = base.retry(lambda: c.get(LIST_URL, params=params))
                r.raise_for_status()
                doc = HTMLParser(r.text)
                cards = _cards(doc)
                if page == 1:
                    m = _TOTAL.search(r.text)
                    total = int(m.group(1)) if m else None
                    # 카테고리가 통째로 비면 조용한 부분수집이 된다. 드러낸다.
                    if not cards:
                        raise RuntimeError(
                            f"하이오커피 {label}: 상품 0건 — 셀렉터가 깨졌을 수 있다")
                if not cards:
                    break
                for x in cards:
                    a = x.attributes
                    name = _clean(a.get("data-title"))
                    if not name:
                        continue
                    it = Item(
                        brand=BRAND,
                        name=name,
                        name_en=_clean(a.get("data-subtitle")),
                        desc=_clean(a.get("data-label1")),
                        image=IMG_BASE + _clean(a.get("data-file")),
                        labels=_labels(a.get("data-size")),
                        category=label,
                        is_new=(cate == NEW_CATE),
                    )
                    got += 1
                    if it.key in seen:
                        continue
                    seen.add(it.key)
                    items.append(it)
                if len(cards) < PAGE_ROW or (total and got >= total):
                    break

    if len(items) < MIN_ITEMS:
        raise RuntimeError(f"하이오커피 {len(items)}건 — 메뉴 구조가 바뀌었을 수 있다")

    new = sum(1 for i in items if i.is_new)
    if not new:
        raise RuntimeError("하이오커피 신메뉴 0건 — 카테고리 번호가 바뀌었을 수 있다")
    # 신메뉴 탭이 전체의 절반을 넘으면 그건 '신메뉴'가 아니다(퀴즈노스 66/66).
    if new > len(items) // 2:
        raise RuntimeError(f"하이오커피 신메뉴 {new}/{len(items)}건 — 믿을 수 없다")
    return items
