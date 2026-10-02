"""롯데리아 — 롯데GRS 통합몰(LOTTE EATZ)의 **브랜드 메뉴 면** 한 장만 받는다.

이 파일은 오랫동안 '수집 불가' 스텁이었다. 사유는 신호가 없어서가 아니라
`lotteeatz.com/robots.txt` 가 알려진 봇 티어 외 모든 UA 를 `Disallow: /` 로
막기 때문이었다. **운영자 승인으로 그 제약을 무시하고 수집한다.** UA 는
위장하지 않는다 — `base.UA` 그대로 신원을 밝히고 간다.

## 어디를 읽는가 — 주문 플로우가 아니라 `/brand/ria`

조사 단계에서는 주문 플로우(`/hsv/products/{divcd}/{storecd}`)를 봤다.
그쪽도 뚫린다. 페이지에 박힌 `let template = {...}` 에서 카테고리 배열을 꺼내
`POST /products/{divcd}/{storecd}/menu?orderType=HSV&reservationTime=HHMM` 에
`{"categories":[...]}` 로 던지면 560KB JSON 이 온다(2026-10-02 실측, 103행).
**그런데 그 길을 안 쓴다.** 이유가 셋이다.
  1. **매장 종속이다.** 사이트맵에 divcd=10(롯데리아) 매장이 1,235곳이고
     메뉴는 매장 템플릿마다 다르다. 어느 매장을 '대표'로 삼든 임의 선택이다.
  2. **주문 플로우에는 할인·품절·배달가가 섞인다**(`discountList`·`soldOutYn`).
     신상 목록에 들어오면 안 되는 값들이다.
  3. 요청이 2회(페이지 + POST)인데 `/brand/ria` 는 **1회**에 같은 정보를 준다.

`/brand/ria` 는 완전 SSR 이다(525KB). 브랜드 하나(롯데리아)만 담고, 매장
코드가 없고, 세트·할인·품절 표기가 아예 없다. 2026-10-02 실측 96카드 /
중복 제거 85종. ⚠️ 통합몰이라 `/brand/angel`(엔제리너스)·`/brand/kkd`
(크리스피크림)도 같은 모양으로 있는데 **여기서는 건드리지 않는다.**

## 신제품 신호 — 배지 '글자'다. `aria-label` 이 아니다

카드 배지는 이렇게 생겼다.

    <span class="mn-badge" aria-label="신메뉴" style="border: solid 1px #EF3D2E; …">
        NEW
    </span>

🔴 **`aria-label` 은 쓰면 안 된다.** 2026-10-02 실측에서 배지 12개의
`aria-label` 이 **전부 "신메뉴"** 였다 — `BEST` 6개와 `재주문1위` 2개에도
똑같이 붙어 있다. 롯데GRS 쪽 템플릿 실수다. 이걸 믿으면 2019년부터 파는
'리아 새우'(BEST)가 신제품이 된다. 그래서 **배지의 텍스트**로만 가른다.

배지 분포(96카드): `NEW` 4 · `BEST` 6 · `재주문1위` 2 · 없음 84.
NEW 4개는 중복 포함이고 실제 상품은 2종이다(리아 불고기 레드 / 더블 레드).
NEW 비율 4.2% — 버거킹 31%·이디야(2017년 상품)처럼 배지를 안 내리는 축이
아니다.

## 교차검증 — 이미지 경로의 업로드일과 완전히 일치한다

카드 썸네일이 `https://img.lotteeatz.com/upload/product/2026/08/27/…` 형태라
경로에 업로드 날짜가 들어 있다. 96장의 날짜 분포는 2019-12-20 ~ 2026-08-27 로
흩어지고(최다가 2024-11-20 의 10장) **일괄 재업로드 봉우리가 없다.**
그리고 **최신 날짜(2026-08-27)를 가진 카드 4장이 정확히 NEW 배지 4장이다.**
배지가 붙은 것 중 2026년 이전 날짜는 0건이다. 반대로 BEST 는 전부
2019~2024년이라 배지 글자로 가르는 게 맞다는 증거가 된다.

`released_at` 에는 넣지 않는다. 이건 출시일이 아니라 이미지 올린 날이다
(`notes/BRAND-CANDIDATES.md` §6-5). `uploaded_at` 까지가 정직하다.

배지 없는 카드는 `is_new=None` 으로 둔다. **False 가 아니다** — 이 템플릿에는
'여긴 신메뉴 아님' 을 명시하는 표시가 없다(프랭크버거 `icon_none` 과 다르다).
False 로 찍으면 `rules.is_fresh` 가 `released_at` 만 보게 돼서, 배지를 아직
안 단 신상(예: 주문 플로우에만 있는 '해피즈 트로피칼믹스' 2026-10-01)이
업로드일로도 못 올라온다.

## 담지 않는 것

가격(`.mn-card-price`)은 Item 에 자리가 없어 버린다. 상품 상세 주소도 없다 —
카드에 `<a>` 가 0개고 `onclick` 도 없다(본문 링크는 전부 `javascript:;`).
`url` 은 비우고 `base.SITES` 폴백에 맡긴다.

`/board/notice` 는 전부 개인정보처리방침 변경 안내고, `/event/main` 은
'이달의 쿠폰'·'리아런치 할인' 같은 행사뿐이라 둘 다 쓰지 않는다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "롯데리아"
ROOT = "https://www.lotteeatz.com"
MENU_URL = ROOT + "/brand/ria"
DELAY = 2.0          # 요청이 1회뿐이지만 다음 호출자를 위해 간격을 남긴다
MAX_CARDS = 500      # 폭주 방지. 현재 96장.

# 배지 '글자'가 이거여야 신제품이다. aria-label 은 전건 '신메뉴' 라 못 쓴다
# (위 docstring). 공백·대소문자만 털고 정확히 비교한다.
NEW_BADGE = "NEW"

# 중복 카드를 합칠 때 본으로 삼지 않는 카테고리. 같은 상품이 '추천메뉴' 와
# 실제 분류(버거·치킨…)에 두 번 실린다. 분류 쪽을 남겨야 카드에 쓸 말이 맞다.
_PROMO_CATEGORY = "추천메뉴"

# 썸네일 주소는 `…/20260827141828795_6.png/dims/resize/x214/optimize` 처럼
# 뒤에 리사이즈 지시가 붙는다. 날짜는 그 앞 경로에 있다.
_IMG_DATE = re.compile(r"/(\d{4})/(\d{2})/(\d{2})/")


def _text(node, sel: str) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _uploaded_at(src: str) -> str:
    """이미지 경로의 /YYYY/MM/DD/ 가 업로드 날짜다. 없으면 빈 문자열."""
    m = _IMG_DATE.search(src or "")
    return "-".join(m.groups()) if m else ""


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(MENU_URL))
        r.raise_for_status()
        time.sleep(DELAY)

    doc = HTMLParser(r.text)
    sections = doc.css(".mn-section")
    if not sections:
        raise RuntimeError(f"{MENU_URL}: .mn-section 이 0개다(마크업이 바뀌었다)")

    merged: dict[str, Item] = {}
    seen_cards = 0
    for sec in sections:
        category = _text(sec, ".mn-section-title")
        for card in sec.css(".mn-card"):
            seen_cards += 1
            if seen_cards > MAX_CARDS:
                raise RuntimeError(f"{BRAND}: 카드가 {MAX_CARDS}장을 넘었다")
            name = _text(card, ".mn-card-name")
            if not name:
                continue
            badge = _text(card, ".mn-badge")
            img = card.css_first("img.mn-card-img")
            src = img.attributes.get("src", "") if img else ""
            it = Item(
                brand=BRAND,
                name=name,
                image=src,
                labels=[badge] if badge else [],
                category=category,
                uploaded_at=_uploaded_at(src),
                is_new=True if badge.upper() == NEW_BADGE else None,
            )
            old = merged.get(it.key)
            # 같은 상품이 '추천메뉴' 와 실제 분류에 두 번 실린다. 분류 쪽을 남긴다.
            if old is None or old.category == _PROMO_CATEGORY:
                merged[it.key] = it

    if not merged:
        raise RuntimeError(f"{MENU_URL}: 카드에서 상품을 하나도 못 뽑았다")
    return list(merged.values())
