"""발도스커피(VALDOS COFFEE) — 커피 프랜차이즈. **(CAFE, "커피")**

등록 담당자에게: `(CAFE, "커피")` ·
SITES `http://valdos.co.kr/bbs/bbs/board.php?bo_table=m31`   (⚠️ http 만 — CAFE5 노트 실측)

공정위 `커피` 289곳(가맹점 5+) 중 **47위(가맹점 91개)**. 운영사 조이풀컴퍼니(주)(인천 부평).
`notes/CANDIDATES-CAFE5.md` §6 "다음 후보 1순위". 2026-10-14 실측.

## 경로 — `New & season` 갤러리 게시판(그누보드 5) 앞 2쪽

```
GET http://valdos.co.kr/bbs/bbs/board.php?bo_table=m31&page=1   글 8개 (2026-03 ~ 2026-09)
GET http://valdos.co.kr/bbs/bbs/board.php?bo_table=m31&page=2   글 8개 (2025-06 ~ 2025-12)
    (9쪽까지 있다. 60일 창에는 1쪽이면 충분하고, 2쪽은 가드용 분모다)
```
⚠️ 루트 `valdos.co.kr/` 는 1,981B meta refresh 껍데기고 본체는 `/bbs/` 다(CAFE5 §4-2).
메뉴 네비의 나머지 7칸(`m32` Coffee ~ `m38` Dessert)은 **배지·날짜 없는 전체 메뉴판**이라
읽지 않는다 — 긁으면 제1 규칙 위반이다.

글 하나 = `a.js-smartPhoto`. `data-id` = 글 제목, `href` = **원본 이미지**,
같은 카드의 `.gallery-list-title_s` = 본문(상품명을 `&` 로 이어 붙인 것).
```
제목 `2026 가을 신메뉴`   본문 `초당옥수수라떼&초당옥수수크림커피&리얼알밤빵`
제목 `바질토마토치아바타샌드위치`  본문 같음
```
→ **본문을 `&`·줄바꿈으로 쪼갠 것이 상품명이다**(엽떡 선례, 함정 ⑪). 제목은 묶음 이름이라 안 쓴다.

## 🔴 이름 — 본문이 비거나 연도로 시작하면 버린다

2쪽까지 16글 중 본문이 **빈 글이 3개**(`아사이소르베`·`제로슈가`·`디카페인`, 전부 2025-06~07)다.
제목만 남는데 그중 `제로슈가`·`디카페인` 은 **상품이 아니라 옵션 라인 공지**다(3쪽엔
`쉐이크`·`아이스크림` 같은 카테고리 공지도 있다). 하나를 특정할 근거가 없으니 **버린다.**
`2026 컵빙수` 처럼 **연도로 시작하는 이름**은 맛 이름을 안 준 묶음이라 버린다(`N종` 과 같은 취급).
그리고 **제목이 연도로 시작하는데 `신메뉴` 가 없는 글은 통째로 버린다** — 컵빙수는 2023~2026 매년
올라온 **복귀 시즌 상품**이라, 본문에 맛 이름을 나열하기 시작하면 작년 맛이 올해 신상이 된다.
(9쪽 전수: 1~2쪽은 `A&B` 꼴, 3~6쪽은 본문 빈 글이 대부분, 7~9쪽은 `TEA`·`에이드` 같은 카테고리 공지다.
7쪽 글이 2쪽 범위로 밀려오려면 새 글 32개가 쌓여야 한다.)
`신메뉴`·`시즌`·`part` 가 상품명에 섞이면 쪼개기가 깨진 것이므로 터뜨린다.

## 날짜 — 원본 이미지의 `Last-Modified`. **RSS 작성일과 초 단위로 맞는다**

목록에도 글 보기에도 날짜가 없다 — 글 보기의 작성일 칸이 `-0001-11-30 00:00`(MySQL
`0000-00-00`)이다. RSS(`/bbs/bbs/rss.php?bo_table=m31`)는 8글 중 **4글만** 날짜를 주고 나머지는
`0000-00-00T00:00:00`. 그래서 원본 이미지 `HEAD` 의 `Last-Modified` 를 쓴다. 날짜가 살아 있는
4글로 대조했다:
```
wr_id  RSS dc:date              이미지 Last-Modified
71     2026-09-16 10:06:19 KST  Wed, 16 Sep 2026 01:06:19 GMT   ← 초까지 같다
67     2026-04-17 11:28:28      Fri, 17 Apr 2026 02:28:28 GMT
66     2026-04-17 11:28:03      Fri, 17 Apr 2026 02:28:03 GMT
65     2026-04-01 14:24:43      Wed, 01 Apr 2026 05:24:43 GMT
```
날짜가 빈 글도 계절이 맞는다 — `2026 여름 신메뉴` 06-10 · `part2` 06-18 · `2026 봄` 03-11 ·
`2025 겨울` 11-04 · `2025 가을` 09-05. 그리고 **글 순서(최신→과거)대로 단조 감소**한다.

🔴 **다만 일괄 재업로드가 있다.** 2·3쪽에 `2025-06-11` 이 6글 몰려 있고(2쪽 2 + 3쪽 4) 그중
`2025 봄 신메뉴`(봄인데 6월)·`2025 컵빙수`·`팥브라우니` 가 섞인다 — 사진을 한꺼번에 다시 올린 것이다.
그래서 ① `uploaded_at` 에만 넣고(함정 ⑤) ② 숲속호두와 같은 **순서 보정**을 한다 — 목록 순서상
나보다 **새 글들의 가장 이른 날짜**보다 내 날짜가 늦으면 그 값으로 깎는다. 깎는 방향은 항상
'더 옛날'이다. ③ 상품 28건 중 최근 60일이 절반을 넘거나 ④ **창 안에서 같은 날 올라온 글이 3개 이상**이면 터뜨린다.
   ④가 필요한 이유(검수 재현): 맨 위 5글만 오늘 날짜로 다시 올리면 순서 보정은 맨 위를 깎을 기준이
   없고 ③도 11/28 이라 통과해, 우베 4종·청포도 등 옛 메뉴 7건이 오늘 신상이 됐다. 이 게시판엔
   2024-02-13 에 24글, 2024-02-05 에 18글을 한꺼번에 올린 이력이 있다(9쪽 67글 전수 실측).

`is_new` 는 주지 않는다(`None`). 게시판 전체가 '신메뉴 글'이지만 9쪽짜리 아카이브라 배지로
쓰면 하이오커피 사고(날짜 없는 1년치 바구니)와 같아진다 — **날짜가 유일한 판정 근거**다.
날짜를 못 읽은 글은 그대로 `None`·날짜 없음이 돼 화면에 오르지 않는다.

## 오늘(2026-10-14) 화면 — 수집 28건 중 4건

`초당옥수수라떼` · `초당옥수수크림커피` · `리얼알밤빵`(09-16) · `바질토마토치아바타샌드위치`(09-07).
가을 글이 가을에 올라온 것이라 계절 모순 없음. `리얼알밤빵`·`바질토마토치아바타샌드위치` 는
디저트·푸드지만 카페 브랜드 신메뉴라 유형은 그대로 `CAFE` 다.
"""
import re
import time
from datetime import date, timedelta, timezone
from email.utils import parsedate_to_datetime

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "발도스커피"
LIST = "http://valdos.co.kr/bbs/bbs/board.php?bo_table=m31"
PAGES = 2
DELAY = 1.5
HEAD_DELAY = 0.7

MIN_POSTS = 12          # 실측 2쪽 16글
MIN_ITEMS = 15          # 실측 28건
MAX_ITEMS = 120
DATED_MIN_RATIO = 0.8   # 실측 16/16 글
FRESH_MAX_RATIO = 0.5   # 실측 4/28
WINDOW = 60             # rules.WINDOW 와 같은 값. 가드 전용

_SPLIT = re.compile(r"\s*(?:&|＆|\n)\s*")
_YEAR_LEAD = re.compile(r"^\s*20\d\d\b")
_BAD = re.compile(r"신메뉴|시즌|\bpart\s*\d", re.I)
# 제목이 연도로 시작하는데 `신메뉴` 가 아닌 글 — `2026 컵빙수` 처럼 매년 돌아오는 시즌 상품 글이다
_SEASON_RETURN = re.compile(r"^\s*20\d\d\b(?!.*신메뉴)")
_KST = timezone(timedelta(hours=9))
SAME_DAY_MAX = 2        # 창 안에서 같은 날 올라온 글 수 상한. 실측 최대 2(09-16·09-07 각 1, 04-17 2)


def _names(body: str) -> list:
    """본문 `A&B&C` → ['A','B','C']. 연도로 시작하는 묶음 이름은 버린다(모듈 주석)."""
    out = []
    for n in _SPLIT.split(body or ""):
        n = " ".join(n.split())
        if not n or _YEAR_LEAD.match(n):
            continue
        out.append(n)
    return out


def _lm_date(c, url: str) -> str:
    """원본 이미지 HEAD 의 Last-Modified → KST 'YYYY-MM-DD'. 못 읽으면 ''."""
    try:
        h = base.retry(lambda: c.head(url))
    except Exception:
        return ""
    lm = h.headers.get("last-modified") if h.status_code == 200 else None
    if not lm:
        return ""
    try:
        return parsedate_to_datetime(lm).astimezone(_KST).date().isoformat()
    except (TypeError, ValueError):
        return ""


def fetch() -> list[Item]:
    posts = []                 # (제목, 본문, 원본 이미지, 날짜) — 목록 순서(최신→과거)
    with base.client() as c:
        for p in range(1, PAGES + 1):
            if p > 1:
                time.sleep(DELAY)
            url = f"{LIST}&page={p}"
            r = base.retry(lambda url=url: c.get(url))
            r.raise_for_status()
            for a in HTMLParser(r.text).css("a.js-smartPhoto"):
                title = " ".join((a.attributes.get("data-id") or "").split())
                href = a.attributes.get("href") or ""
                card = a.parent
                while card is not None and card.css_first(".gallery-list-title_s") is None:
                    card = card.parent
                sub = card.css_first(".gallery-list-title_s") if card is not None else None
                body = sub.text() if sub is not None else ""
                time.sleep(HEAD_DELAY)
                posts.append((title, body, href, _lm_date(c, href) if href else ""))

    if len(posts) < MIN_POSTS:
        raise RuntimeError(
            f"{BRAND}: {PAGES}쪽에서 글 {len(posts)}개 — 2026-10-14 실측은 16개였다. "
            f"'a.js-smartPhoto' 갤러리 스킨이 바뀌었는지 확인하라")
    dated_posts = sum(1 for p in posts if p[3])
    if dated_posts < len(posts) * DATED_MIN_RATIO:
        raise RuntimeError(
            f"{BRAND}: 글 {len(posts)}개 중 이미지 날짜를 {dated_posts}개만 읽었다 — "
            f"원본 이미지 HEAD 가 Last-Modified 를 안 주게 됐다. 실측 16/16")

    # 순서 보정 — 나보다 새 글들의 가장 이른 날짜로 깎는다(모듈 주석 §날짜).
    floor = ""
    items: list[Item] = []
    seen = set()
    for title, body, href, d in posts:
        raw = d
        if d and floor and floor < d:
            d = floor
        if raw and (not floor or raw < floor):
            floor = raw
        if _SEASON_RETURN.match(title):
            continue      # 매년 돌아오는 시즌 상품 글(컵빙수 2023~2026 매년). 모듈 주석 §이름
        for name in _names(body):
            if _BAD.search(name):
                raise RuntimeError(
                    f"{BRAND}: 상품명에 묶음 말이 섞였다 — {name!r} (글 제목 {title!r}). "
                    f"본문 쪼개기 규칙이 깨졌다")
            it = Item(brand=BRAND, name=name, image=href, uploaded_at=d,
                      url=LIST)
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)

    if not MIN_ITEMS <= len(items) <= MAX_ITEMS:
        raise RuntimeError(
            f"{BRAND}: 상품 {len(items)}건 — 2026-10-14 실측은 2쪽 16글 → 28건이었다"
            f"(기대 {MIN_ITEMS}~{MAX_ITEMS}). 본문이 비기 시작했는지 확인하라")
    cutoff = (date.today() - timedelta(days=WINDOW)).isoformat()
    fresh = sum(1 for i in items if i.uploaded_at and i.uploaded_at >= cutoff)
    # 최신 글 몇 개를 다시 올리면 순서 보정이 못 막는다(맨 위 글은 깎을 기준이 없다).
    # 창 안에서 같은 날 올라온 글이 많으면 재업로드로 보고 멈춘다.
    per_day: dict = {}
    for _, _, _, d in posts:
        if d and d >= cutoff:
            per_day[d] = per_day.get(d, 0) + 1
    if per_day and max(per_day.values()) > SAME_DAY_MAX:
        raise RuntimeError(
            f"{BRAND}: 최근 {WINDOW}일 안에 같은 날 올라온 글이 {per_day} — 실측 최대 "
            f"{SAME_DAY_MAX}개였다. 옛 글을 다시 올린 것인지 눈으로 보라(2024-02-13 24글 선례)")
    if fresh > len(items) * FRESH_MAX_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 {fresh}건이 최근 {WINDOW}일 — 실측 4/28. "
            f"이미지를 일괄 재업로드했는지 확인하라(2025-06-11 6글 선례)")
    return items
