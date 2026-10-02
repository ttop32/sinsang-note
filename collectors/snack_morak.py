"""모락떡볶이(모락로제떡볶이).

(주)채움푸드(임채용, 인천 부평구 부평대로 283 우림라이온스밸리 A동 409호) 운영.
공정위 `분식` 76개점(2024년 말). 떡볶이 하위 순위 17위.
도메인은 **`moraktteok.com`** 이다(브랜드 로마자 `morak` + 떡).
간판은 '모락떡볶이'인데 사이트와 보도자료는 **'모락로제떡볶이'** 로 쓴다.
`BRAND` 는 공정위 등록명인 `모락떡볶이` 로 둔다.

## ⚠️ robots.txt 가 404 다. 간격을 길게 잡는다

`https://moraktteok.com/robots.txt` → **404 / 204바이트 아파치 기본 HTML**.
허용도 금지도 아니다. 죠스떡볶이와 같은 처분으로 `DELAY` 를 3초로 둔다.
이용약관도 없다 — 푸터에 개인정보처리방침 링크조차 없다. **"약관을 확인하지
못했다"** 상태로 붙는다. 삭제 요청이 오면 즉시 내린다.

## 사이트가 **창업 모집 한 장짜리**인데 메뉴 목록이 그 안에 있다

내비게이션이 없고 `/` 한 장(60KB)이 전부다. 그런데 `#sec10` 에 상품 슬라이드가
텍스트로 들어 있다 — 이미지 포스터가 아니다. **1요청**이면 끝난다.

    <section id="sec10"> … <div class="swiper swiper-menu"><ul class="swiper-wrapper">
      <li class="swiper-slide">
        <h6>화끈한 마라맛 신메뉴 마라떡볶이</h6>
        <h4>마라떡볶이</h4>
        <img src="https://moraktteok.com/data/file/menu/925ecf…png" alt="">

우리할매떡볶이(319개점)·감탄떡볶이(182개점)·걸작떡볶이치킨(79개점)은 같은
'창업 모집 사이트'인데 **메뉴 페이지 자체가 없거나 포스터 이미지**였다.
여기는 창업 사이트인데도 상품이 텍스트로 있다. **창업 사이트라고 먼저 접지 마라.**

## ⭐ 배지가 없다. 신상 표시가 **설명 문장 안에** 있다

`NEW`·`new` 요소가 **0건**이다. 전체 텍스트에서 `신메뉴` 가 나오는 자리는
**딱 한 군데**, `마라떡볶이` 의 설명 `화끈한 마라맛 신메뉴 마라떡볶이` 다.

**2026-10-02 실측 비율 — 슬라이드 6건 중 `신메뉴` 1건.**

| 슬라이드 | 설명 | 신메뉴 |
|---|---|---|
| 볼로냐 로제떡볶이 | 고급 생크림과 특제 소스로 만든 꾸덕한 로제떡볶이 | |
| 국물떡볶이 | 모락만의 특별 비법 조개육수로 만든 진한 떡볶이 | |
| 이태리투움바떡볶이 | 매콤한 맛을 더한 고급 투움바떡볶이 | |
| 베이컨까르보나라떡볶이 | 크리미한 소스로 만든 진한 베이컨 까르보나라 떡볶이 | |
| **마라떡볶이** | **화끈한 마라맛 신메뉴 마라떡볶이** | ✅ |
| 세트구성 | 모락로제떡볶이 직접 개발 떡볶이+닭강정세트 | (세트. `collect.drop_sets()` 가 이름으로 거른다) |

전수(6/6)가 아니라 1/6 이고, 붙은 이름이 간판 메뉴가 아니라 가장 나중에 붙은
맛이다(브랜드 설명은 로제가 간판이라고 말한다). 겐로쿠우동의 유일한 NEW 가
`카모난우동(일시중단)` 이었던 함정(§5-4)은 피했다.

⚠️ **이건 배지가 아니라 사람이 쓴 문장이다.** 브랜드가 문장을 안 고치면 영원히
신상으로 남는다. `rules.is_fresh` 의 STALE(first_seen 기준)이 걷어가는 데 맡긴다.
설빙 '인절미설빙'(2013년 간판에 배지가 계속 달려 있던 건)과 같은 처분이다.

## 날짜가 없다

게시판이 **아예 없다**(gnuboard 인데 공지·소식 메뉴가 노출돼 있지 않다).
이미지는 `/data/file/menu/<해시>_<해시>_<해시>.png` 라 날짜가 없다.
`released_at`·`uploaded_at` 둘 다 빈다.

상품별 주소도 없다(슬라이드 `<li>`). `url` 을 비워 `base.SITES` 폴백에 맡긴다.
가격은 사이트에 없다. 이미지는 전부 https 절대경로다.
"""
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "모락떡볶이"
URL = "https://moraktteok.com/"
DELAY = 3.0   # robots.txt 가 404 다. 허용도 금지도 아니니 간격을 길게 잡는다.

# 설명 문장 안의 신상 표시. 배지가 아니라 사람이 쓴 문장이다(위 docstring 참고).
NEW_WORDS = ("신메뉴", "신상", "NEW")


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(URL))
        r.raise_for_status()
        time.sleep(DELAY)

    slides = HTMLParser(r.text).css(".swiper-menu .swiper-slide")
    if not slides:
        # 조용히 빈 리스트를 돌려주지 않는다. 한 장짜리 사이트라 이게 깨지면
        # 수집할 게 아무것도 없다.
        raise ValueError(f"{BRAND}: .swiper-menu 슬라이드가 0건이다 "
                         f"(2026-10-02 실측 6건). 페이지 구조를 확인해라")

    for s in slides:
        h4 = s.css_first("h4")
        if not h4:
            continue
        name = " ".join(h4.text().split())
        if not name:
            continue
        h6 = s.css_first("h6")
        desc = " ".join(h6.text().split()) if h6 else ""
        img = s.css_first("img")
        flagged = any(w in desc for w in NEW_WORDS)
        it = Item(
            brand=BRAND,
            name=name,
            desc=desc,
            image=img.attributes.get("src", "") if img else "",
            labels=["신메뉴"] if flagged else [],
            # 분류 축이 없다(섹션 하나에 전부 들어 있다).
            category="",
            # 설명에 '신메뉴' 가 든 것만 True. 없음은 '아니다'가 아니라 '모른다'다.
            is_new=True if flagged else None,
            # 상품별 주소가 없다(슬라이드 <li>).
            url="",
        )
        if it.key in keys:
            continue
        keys.add(it.key)
        items.append(it)

    # 이 브랜드의 신호는 설명 문장 하나뿐이다. 문장이 바뀌면 건수는 6 그대로라
    # collect 의 0건·급감 가드에 안 걸리고 조용히 '신상 없는 브랜드' 가 된다.
    if items and not any(i.is_new for i in items):
        print(f"[{BRAND}] 설명에 '신메뉴' 가 든 상품이 0건이다 — 문구를 지운 건지 "
              f"슬라이드 구조가 바뀐 건지 확인해야 한다")
    return items
