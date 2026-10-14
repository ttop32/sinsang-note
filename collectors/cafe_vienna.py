"""비엔나커피하우스(Vienna Coffee House) — 오스트리아식 커피 프랜차이즈. **(CAFE, "커피")**

등록 담당자에게: `(CAFE, "커피")` · SITES `https://viennacoffeehouse.co.kr/notice`

공정위 `커피` 289곳(가맹점 5+) 중 110위 아래 구간(가맹점 17개). `notes/CANDIDATES-CAFE6.md` 긴 꼬리에서 찾았다.
공식 도메인은 프차몰 franchise-info 의 링크로 확인. 2026-10-14 실측.

## 경로 — `NEWS > 공지사항` 목록 3쪽. 글이 거의 다 **출시 안내**다

```
GET https://viennacoffeehouse.co.kr/notice?page=1..3     글 8개/쪽, 24개 (2024-09 ~ 2026-09)
```
카드 = `<article>` → `h3 a`(제목, `/notice/NNNN`) · 날짜 `YYYY년 MM월 DD일`. 상세는 안 연다 — **제목에 상품명이 있다**:
```
"비엔나 가을 디저트 (솔티카라멜 팝 아이스크림)" 출시 안내        → 괄호 안 한글 = 상품명
"비엔나 생과일 주스 (고창 수박 주스 & 토마토 주스)" 출시 안내     → `&` 로 쪼갠다
"핑크솔트카카오(Pink Salt Cacao)" 출시 안내                    → 괄호가 영문이면 바깥이 상품명
"비엔나의 여름 빙수 3종 (Summer in Vienna)" 출시 안내           → `N종` = 묶음. 버린다
"피스타치오 시즌 음료 (European Spring Cafe)" 출시 안내          → `시즌`·`시리즈`·`컬렉션` = 묶음. 버린다
"에스프레소 클라시코 (ESPRESSO CLASSICO)" 2종 출시 안내         → 따옴표 밖 `2종` 도 묶음. 버린다
'프란치스카너' 리뉴얼                                          → 제목에 `출시` 가 없으면 안 본다
```
배지·카탈로그 날짜는 없다. `/catalog`(75개)는 **상시 메뉴만** 있어 시즌 신메뉴가 아예 안 실린다 — 대조축으로도 못 쓴다.

## 🔴 해마다 돌아오는 메뉴 — 가장 이른 글 날짜를 남긴다

`고창 수박 주스` 가 **2025-07-17 과 2026-06-18 두 번** 출시 안내로 올라왔다(2024-09-05 클렌즈 주스 글에도 수박 주스).
최신 글 날짜를 쓰면 작년 수박 주스가 올해 신상이 된다. 그래서 3쪽을 다 읽고 **같은 이름은 가장 이른 날짜**를 쓴다.
2026-06-18 글에서 새로 남는 건 `토마토 주스` 뿐이다. 3쪽 밖(2024-09 이전)에 있던 걸 다시 내면 못 막는다 — 남는 구멍.

## 날짜 — 글 날짜 → `released_at`

브랜드가 출시를 알리는 글이고 본문이 "9월 16일부터 일부 매장에서 판매" 처럼 같은 주의 판매일을 말한다.
⚠️ **2025-07-17 에 글 7개가 같은 날짜**다(사이트 이전 때 옛 글을 한꺼번에 다시 올린 흔적 — 썸네일 파일명의
유닉스 시각도 전부 2025-07-17). 60일 창 밖이라 지금은 무해하지만, 다시 이전하면 옛 글이 한꺼번에 오늘 날짜를 단다.
그래서 **창 안에서 같은 날 글이 4개 이상**이면 터뜨린다(실측 최대: 창 안 1개, 평소 같은 날 2개 — 2026-05-14).

## 오늘(2026-10-14) 화면 — 1건

`솔티카라멜 팝 아이스크림`(2026-09-09). 수집은 4쪽(2023-06 까지) → 상품 15건 안팎.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "비엔나커피하우스"
SITE = "https://viennacoffeehouse.co.kr"
LIST = SITE + "/notice?page={}"
MAX_PAGES = 5
DELAY = 1.5
WINDOW = 60
SAME_DAY_MAX = 3        # 창 안 같은 날 글 상한(위 docstring)
MIN_POSTS = 15          # 실측 3쪽 24글
MIN_ITEMS = 6           # 실측 15건 안팎

_DATE = re.compile(r"(20\d\d)년\s*(\d{1,2})월\s*(\d{1,2})일")
_QUOTE = re.compile(r"[\"“”'‘’「]([^\"“”'‘’」]{2,60})[\"“”'‘’」]")
_BUNDLE = re.compile(r"\d+\s*종|시리즈|컬렉션|시즌|세트|set\b|트리오", re.I)
_PAREN = re.compile(r"^(.*?)\s*\(([^()]*)\)\s*$")
_HANGUL = re.compile(r"[가-힣]")


def _names(title: str) -> list:
    """제목 → 상품명 목록. 묶음·리뉴얼·따옴표 없는 제목은 [] (모듈 주석의 표)."""
    if "출시" not in title or "리뉴얼" in title:
        return []
    m = _QUOTE.search(title)
    if not m:
        return []
    inner = " ".join(m.group(1).split())
    outside = title[:m.start()] + title[m.end():]
    if _BUNDLE.search(outside):            # 따옴표 밖 `2종`
        return []
    pm = _PAREN.match(inner)
    if pm and _HANGUL.search(pm.group(2)):
        if _BUNDLE.search(pm.group(2)):
            return []
        parts = re.split(r"\s*[&,·]\s*", pm.group(2))
    else:
        head = pm.group(1) if pm else inner
        if _BUNDLE.search(inner):
            return []
        parts = re.split(r"\s*[&,·]\s*", head)
    out = []
    for p in parts:
        p = " ".join(p.split())
        if len(p) >= 2 and _HANGUL.search(p) and not _BUNDLE.search(p):
            out.append(p)
    return out


def fetch() -> list[Item]:
    posts = []                       # (날짜, 제목, URL) — 최신순
    with base.client() as c:
        for p in range(1, MAX_PAGES + 1):
            if p > 1:
                time.sleep(DELAY)
            r = base.retry(lambda p=p: c.get(LIST.format(p)))
            r.raise_for_status()
            arts = HTMLParser(r.text).css("article")
            if not arts:
                break
            for art in arts:
                a = art.css_first("h3 a")
                dm = _DATE.search(" ".join(art.text().split()))
                if a is None or dm is None:
                    raise RuntimeError(f"{BRAND}: {p}쪽 카드에서 제목·날짜를 못 읽었다 — 목록 꼴이 바뀌었다")
                y, mo, d = dm.groups()
                posts.append((f"{y}-{int(mo):02d}-{int(d):02d}",
                              " ".join(a.text().split()), a.attributes.get("href") or ""))

    if len(posts) < MIN_POSTS:
        raise RuntimeError(f"{BRAND}: 공지 {len(posts)}개 — 2026-10-14 실측은 3쪽 24개였다. "
                           f"페이지(`?page=`)나 `<article>` 카드 꼴이 바뀌었는지 보라")
    cutoff = (date.today() - timedelta(days=WINDOW)).isoformat()
    per_day: dict = {}
    for d, _, _ in posts:
        if d >= cutoff:
            per_day[d] = per_day.get(d, 0) + 1
    if per_day and max(per_day.values()) > SAME_DAY_MAX:
        raise RuntimeError(f"{BRAND}: 최근 {WINDOW}일 안 같은 날 글이 {per_day} — 사이트 이전으로 "
                           f"옛 글을 다시 올린 것인지 보라(2025-07-17 7글 선례)")

    found: dict = {}
    for d, title, url in posts:          # 최신순 → 나중에 본 게 더 이르다
        for name in _names(title):
            it = Item(brand=BRAND, name=name, released_at=d, url=url or SITE + "/notice")
            found[it.key] = it          # 같은 이름은 가장 이른 날짜로 덮인다
    items = list(found.values())
    if len(items) < MIN_ITEMS:
        raise RuntimeError(f"{BRAND}: 상품 {len(items)}건 — 실측은 15건 안팎이었다. 제목 꼴"
                           f"(`\"… (상품명)\" 출시 안내`)이 바뀌었는지 보라")
    return items
