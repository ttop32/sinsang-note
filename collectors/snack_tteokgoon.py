"""떡군이네떡볶이.

(주)신우푸드(377-86-02353, 인천 서구 북항로177번길 26) 운영. 공정위 `분식`
50개점(2024년 말). 떡볶이 하위 순위 23위.

도메인이 **한글도메인 하나뿐**이다 — `떡군이네떡볶이.com`
(punycode `xn--6e0b73ep0espx.com`). 수유리우동집과 같은 경우라 로마자를
추측하면 못 찾는다. 푸터 사업자등록번호로 (주)신우푸드와 대조했다.

robots.txt: **200 / 132바이트 / `User-agent: * / Allow:/`** (나머지는 다음
웹마스터도구 인증 주석). 전부 https, 완전 SSR, UTF-8.
이용약관은 푸터에 없다(개인정보처리방침·사이트맵만). **"약관을 확인하지 못했다"**
상태로 붙는다.

## 두 소스를 합친다 — 메뉴에서 상품, NEWS 에서 출시일

**① 메뉴 3장 — `/menu/menu_a.html`(떡볶이 4) · `menu_b`(튀김 4) · `menu_c`(사이드 4).**
합쳐서 **12건**이다. 카드가 `ul.con2_li1 > li` 이고 `.st2` 이름 · `.st3` 설명 ·
`.img1 img` 사진이다.

    <li><a href="#">
      <div class="img1"><img src="/pds/space/62_s?1762325871" alt="" /></div>
      <div class="st1"><a href="#">
        <p class="st2">New)소이크림떡볶이</p>
        <div class="st3">짭쪼름한 크림소스에 풍미를 더하다!!</div>

## ⭐ 배지가 없다. 신상 표시가 **상품명 안에** 들어 있다

`NEW` 배지 요소가 **0건**이다. 대신 이름 앞에 `New)` 가 붙어 있다 —
**12건 중 1건**(`New)소이크림떡볶이`). 전수가 아니고(퀴즈노스 66/66과 반대),
붙은 이름을 읽어 보면 간판 메뉴가 아니라 실제로 가장 최근 출시 상품이다
(아래 NEWS 2025-11-21 과 일치한다).

접두는 **이름에서 턴다.** 안 털면 브랜드가 나중에 접두를 떼는 순간
`make_key` 가 바뀌어 같은 상품이 '어제 없던 신규'로 한 번 더 올라온다.
`labels` 에 `NEW` 로 남겨 근거를 보존한다.

⚠️ 표기가 `New)` 하나로 고정돼 있다는 보장이 없다(`[New]`·`NEW)` 등). 그래서
정규식을 느슨하게 잡되, 이름 **맨 앞**에서만 턴다 — 가운데 `new` 가 든 상품명
(예: `뉴욕핫도그`)을 건드리지 않기 위해서다.

**② NEWS — `/notice/news.html` 에 연도까지 있는 날짜가 붙어 있다.**

    <p class="st2">&lt;신메뉴 출시&gt; 소이크림 떡볶이</p>
    <div class="st3">짭조름한 크림소스에 풍미를 더하다!!</div>
    <p class="st4 mt20 clfix">2025-11-21 <span>MORE &gt;</span></p>

2026-10-02 실측 전체 5건, 최신 **2025-11-21**(≈10개월). 게시판이 아주 활발하진
않지만 **연 1~2건씩 꾸준히 출시 글이 올라온다**(2025-11 · 2024-01 · 2023-10 ·
2022-11). 애플꼬마김밥과 같은 급이라 붙인다.

| 날짜 | 제목 | 메뉴와 매칭 |
|---|---|---|
| 2025-11-21 | `<신메뉴 출시> 소이크림 떡볶이` | ✅ `New)소이크림떡볶이` |
| 2024-01-10 | `BIG SIZE 바삭 타코야끼 3종 출시` | ❌ 3종 묶음 글이라 상품명이 아니다 |
| 2023-10-05 | `로제마라,간차마라 떡볶이 출시` | ❌ 두 상품을 합쳐 쓴 제목 |
| 2022-11-09 | `간차떡볶이 출시` | ✅ `간차떡볶이` |
| 2022-09-23 | `스트릿 댄스 걸스파이터 제작지원` | ❌ 제작지원 글(출시 아님) |

삼첩분식과 같은 방식이다 — **이름이 정확히 같을 때만 붙인다.** 느슨하게 맞추면
`BIG SIZE 바삭 타코야끼 3종` 이 `오리지널 바삭 타코야끼` 에 붙는다.
2026-10-02 실측으로 12건 중 **2건**이 날짜를 받는다. 못 붙은 건 **비운다.**

## 날짜를 이미지에서 줍지 않는 이유 — epoch 가 출시일이 아니다

이미지 주소가 `/pds/space/62_s?1762325871` 처럼 **유닉스 초 타임스탬프**를
쿼리로 달고 있다. 변환하면 깨지지 않는 값이 나와서(2025-11-05·2024-01-10·
2022-10-28) 토마토김밥의 초/밀리초 혼용(§5-9)과 달리 그대로 쓰고 싶어진다.
그런데 **소이크림떡볶이는 1762325871 = 2025-11-05 이고 NEWS 글은 2025-11-21**,
**간차떡볶이는 1704872089 = 2024-01-10 인데 NEWS 글은 2022-11-09** 이다.
간차의 값은 하필 `타코야끼 3종 출시`(2024-01-10)와 같은 날이다 — 그 날
사진을 한꺼번에 갈아끼운 자국이다. **업로드 시각이지 출시일이 아니다.**
`released_at` 은 물론 `uploaded_at` 에도 넣지 않는다(김가네 반례와 같은 종류).

상품별 주소는 **없다** — 카드의 `<a href="#">` 다. `url` 을 비워
`base.SITES` 폴백에 맡긴다. 가격은 사이트에 없다. 이미지는 전부 https 상대경로다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "떡군이네떡볶이"
ROOT = "https://xn--6e0b73ep0espx.com"   # 떡군이네떡볶이.com
NEWS = ROOT + "/notice/news.html"
DELAY = 2.5
MAX_POSTS = 50   # 폭주 방지. 현재 전체 5건이다.

# (분류, 경로)
PAGES = (
    ("떡볶이", "/menu/menu_a.html"),
    ("튀김",   "/menu/menu_b.html"),
    ("사이드", "/menu/menu_c.html"),
)

# 이름 맨 앞의 신상 표시. `New)` 가 현재 유일한 형태지만 표기가 바뀔 수 있어
# 느슨하게 잡는다. 맨 앞에서만 턴다(가운데 'new' 가 든 상품명 보호).
_NEWTAG = re.compile(r"^\s*[\[(<]?\s*new\s*[\])>]?\s*", re.I)
# 두 소스의 이름을 맞추는 키. 공백과 꾸밈말을 턴다.
_NOISE = re.compile(r"신메뉴|출시|[<>\[\]()]|\s+")
_DATE = re.compile(r"(20\d{2})-(\d{2})-(\d{2})")
# 출시 글이 아닌 것. 이름 일치가 1차 방어고 이건 두 번째 그물이다.
_EVENT = ("이벤트", "제작지원", "할인", "콜라보", "증정", "기념", "당첨", "오픈")


def _norm(name: str) -> str:
    return _NOISE.sub("", name or "")


def _released(c) -> dict:
    """NEWS 의 출시 글 → {정규화 이름: YYYY-MM-DD}. 날짜가 여기에만 있다."""
    r = base.retry(lambda: c.get(NEWS))
    r.raise_for_status()
    time.sleep(DELAY)

    out = {}
    for box in HTMLParser(r.text).css(".con3_li2 > div")[:MAX_POSTS]:
        tit = box.css_first(".st2")
        dat = box.css_first(".st4")
        if not (tit and dat):
            continue
        title = " ".join(tit.text().split())
        m = _DATE.search(" ".join(dat.text().split()))
        if not m or any(w in title for w in _EVENT):
            continue
        # 목록이 최신순이다. 같은 상품이 두 번 나오면 더 오래된(=처음) 날짜를
        # 쓰고 싶으므로 덮어쓴다.
        out[_norm(title)] = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        dates = _released(c)

        for category, path in PAGES:
            r = base.retry(lambda: c.get(ROOT + path))
            r.raise_for_status()
            time.sleep(DELAY)

            cards = HTMLParser(r.text).css("ul.con2_li1 > li")
            if not cards:
                # 조용히 넘기지 않는다. 한 분류가 통째로 비면 구조가 바뀐 것이다.
                raise ValueError(f"{BRAND}: {path} 에 상품 카드가 0건이다")

            for card in cards:
                tit = card.css_first(".st2")
                if not tit:
                    continue
                raw = " ".join(tit.text().split())
                name = _NEWTAG.sub("", raw).strip()
                if not name:
                    continue
                flagged = name != raw      # 'New)' 접두가 붙어 있었다
                img = card.css_first(".img1 img")
                src = img.attributes.get("src", "") if img else ""
                desc = card.css_first(".st3")
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=" ".join(desc.text().split()) if desc else "",
                    image=ROOT + src if src.startswith("/") else src,
                    labels=["NEW"] if flagged else [],
                    category=category,
                    # NEWS 에 출시 글이 있는 상품만 찬다. 없으면 비운다.
                    released_at=dates.get(_norm(name), ""),
                    # 접두가 붙은 것만 True. 없음은 '아니다'가 아니라 '모른다'다.
                    is_new=True if flagged else None,
                    # 상품별 주소가 없다(href="#").
                    url="",
                )
                if it.key in keys:
                    continue
                keys.add(it.key)
                items.append(it)

    # 이 브랜드의 상품별 신호는 이름 접두 하나뿐이다. 브랜드가 표기를 바꾸면
    # 건수는 12 그대로라 collect 의 0건·급감 가드에 안 걸린다. 로그에 남긴다.
    if items and not any(i.is_new for i in items):
        print(f"[{BRAND}] 이름 앞 'New)' 표시가 0건이다 — 접두를 뗀 건지 "
              f"표기가 바뀐 건지 확인해야 한다")
    return items
