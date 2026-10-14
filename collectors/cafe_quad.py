"""쿼드커피(QUAD COFFEE) — 청주 기반 커피 프랜차이즈. **(CAFE, "커피")**

등록 담당자에게: `(CAFE, "커피")` · SITES `https://www.quadcoffee.co.kr/board/notice`

공정위 `커피` 289곳(가맹점 5+) 중 **94위(가맹점 33개)**. `notes/CANDIDATES-CAFE5.md` §6
"다음 후보 5순위". 2026-10-14 실측.

## 경로 — `NEWS > 공지사항` 의 `[신메뉴]` 말머리 글

```
GET https://www.quadcoffee.co.kr/board/notice                      목록 (글 5개, 1쪽)
GET https://www.quadcoffee.co.kr/board/notice?viewMode=view&idx=N   글 본문
```
목록은 `href="/board/notice?viewMode=view&…&idx=N"` 앵커 + `작성일YY.MM.DD`. 지금은 글이 5개뿐이고
**5개 전부 `[신메뉴]`** 다(2026-04-01 ~ 2026-07-21). 말머리가 없는 글은 읽지 않는다.

⚠️ `MENU > 신메뉴`(`/product/list?ca_id=01`)는 **캠페인 묶음 카드**(`🍉썸머스낵클럽⚡`·
`마시는 컵빙수🍨`)라 상품 단위가 아니다(CAFE5 §3). 쓰지 않는다.

## 상품명 — 본문의 **"이모지 + 이름" 한 줄**

본문은 `<br>` 로 끊긴 인스타그램 캡션이다. 상품은 이렇게 한 줄씩 온다:
```
🥑🍌 아보카도바나나스무디          ← 상품
🍓🍌 딸기바나나스무디              ← 상품
🍉⚡쿼드 스낵클럽 개장⚡🌭         ← 이름 뒤에 이모지가 또 온다 → 캠페인 문구. 버린다
🥭🫐🍓🥑🍌                        ← 글자가 없다. 버린다
건강해도 맛있을 수 있잖아요🌿      ← 이모지로 시작하지 않는다. 버린다
```
⚠️ **놓치는 꼴이 하나 있다** — 상품이 하나뿐인 글은 이름을 문장 속에 쓴다(`[신메뉴] … SNS 열풍 버터떡`,
2026-04-01: "중독성 강한 풍미가득 버터떡"). 문장에서 이름을 떼는 규칙은 오탐이 커서 **안 잡는다.**
5글 중 1글(버터떡 1건)이 이렇게 빠진다 — 신상이 아닌 게 끼는 쪽이 아니라 빠지는 쪽이다.
수집 실측: 5글 → 복귀 글 1 제외 → **11건**(웰니스 스무디 4 · 썸머스낵클럽 4 · 리치젤리블라썸 3).

규칙: **줄이 이모지로 시작하고, 이모지를 뗀 나머지가 한글·영문·숫자로만 된 20자 이하**이고
`!`·`?`·`~` 같은 문장부호가 없을 것. 해시태그 줄은 `#` 이라 걸리지 않는다.

## 🔴 '[신메뉴]' 인데 신메뉴가 아닌 글 — **복귀 메뉴**

`[신메뉴] 내 손안의 폭염대피소⛱️ 마시는 컵빙수🍨`(2026-05-07)의 본문이
"작년에 핫했던 컵빙수 무사히 **COME BACK!**" 이다 — 작년 메뉴의 재판매다. 말머리만 믿으면
작년 컵빙수가 올해 신상이 된다(함정 ②의 계절 바구니와 같은 성질). 본문에 `COME BACK`·`컴백`·
`재출시`·`재판매`·`돌아왔/온`·`다시 찾아`·`작년`·`올해도`·`앵콜` 이 있으면 **그 글을 통째로 버린다**
(검수: `MENU > 신메뉴` 카드 9장 중 4장이 2025년 계절 캠페인이라 올겨울 복귀 글이 나올 가능성이 높다).
같은 상품이 여러 글에 나오면 **가장 이른 글 날짜**를 남긴다 — '모음' 글이 옛 상품을 새 날짜로 올리는 걸 막는다.

## 날짜 — 글 작성일(`작성일26.07.21`)

브랜드가 신메뉴를 알리는 글을 올린 날이고 본문도 "7/21 공식 출시" 라고 같은 날을 말한다.
글 하나에 한 날짜라 일괄 입력이 아니므로 `released_at` 으로 쓴다. `is_new` 는 주지 않는다 —
날짜가 판정한다(배지 100% 칸에 날짜가 있으니 60일 창이 걸러 준다).

## 오늘(2026-10-14) 화면 — 0건이 정상

가장 최근 글이 2026-07-21(85일 전)이다. 다음 `[신메뉴]` 글이 올라오면 그날 잡힌다.
"""
import re
import time
from datetime import date

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "쿼드커피"
SITE = "https://www.quadcoffee.co.kr"
LIST = SITE + "/board/notice"
VIEW = LIST + "?viewMode=view&idx={}"
DELAY = 1.5
MAX_POSTS = 10          # [신메뉴] 글을 최근 몇 개까지 열지. 실측 5개 전부

_ROW = re.compile(r'href="/board/notice\?viewMode=view[^"]*?idx=(\d+)"')
_TITLE_DATE = re.compile(r"작성일\s*(\d{2})\.(\d{2})\.(\d{2})")
_VIEW_DATE = re.compile(r"(20\d\d)\.(\d{2})\.(\d{2})\s+\d{2}:\d{2}")
# 복귀 글 표지. "돌아온"·"올해도"·"앵콜" 처럼 흔한 말까지 넣는다(검수 재현: "올해도 돌아온 컵빙수" 를
# 놓치면 작년 맛이 올해 신상이 된다). "여름이 돌아왔다! 신메뉴 …" 같은 글도 통째로 빠지는데,
# 그건 신상이 **빠지는** 쪽이라 감수한다.
_COMEBACK = re.compile(r"COME\s*BACK|컴백|재출시|재판매|돌아[왔온오]|다시\s*찾아|작년|올해도|앵[콜코]", re.I)
# 이모지(기호·픽토그램·변형 선택자·ZWJ). 한글·영문·숫자는 안 걸린다.
_EMO = r"[☀-➿\U0001F000-\U0001FAFF️‍⬀-⯿〰〽]"
# 이름 꼴: 한글·영문·숫자로 시작, 괄호·슬래시·& 까지 허용(메뉴판 푸드 32개 중 8개가 `(…)` 꼴), 30자 이하.
_PRODUCT_LINE = re.compile(rf"^(?:{_EMO})+\s*([0-9A-Za-z가-힣][0-9A-Za-z가-힣 ()/&·]{{0,29}})$")
# 이모지로 시작해도 상품이 아닌 줄(검수 실측 미끼: `📍전국 쿼드커피 매장`·`🎁 증정 이벤트`·`📢 공지`·
# `✨ NEW`·`❄️ 겨울 한정`·`🌿 웰빙 라이프`·`💛 Thank you`·`🎉많관부`).
_BAD_WORDS = ("신메뉴", "클럽", "개장", "시즌", "모음", "출시", "이벤트", "증정", "매장", "공지",
              "한정", "쿼드", "NEW", "New", "new", "라이프", "Thank", "많관부", "오픈", "할인")
ZERO_RECENT = 3          # 최근 [신메뉴] 글 몇 개를 보고
ZERO_MAX = 2             # 그중 상품 0건 글이 이만큼이면 본문 꼴이 바뀐 것으로 본다


def _lines(html: str) -> list:
    """`div.memoWrap` 본문 → `<br>` 로 끊은 줄 목록."""
    t = HTMLParser(html)
    box = t.css_first("div.memoWrap")
    if box is None:
        return []
    raw = box.html or ""
    raw = re.sub(r"<br\s*/?>", "\n", raw, flags=re.I)
    raw = re.sub(r"</(?:p|div)>", "\n", raw, flags=re.I)
    txt = HTMLParser(f"<div>{raw}</div>").text()
    lines = [" ".join(l.replace("\xa0", " ").split()) for l in txt.split("\n")]
    return [l for l in lines if l]


def _names(lines: list) -> list:
    out = []
    for l in lines:
        m = _PRODUCT_LINE.match(l)
        if not m:
            continue
        name = m.group(1).strip()
        if len(name) < 2 or any(w in name for w in _BAD_WORDS):
            continue
        out.append(name)
    return out


def fetch() -> list[Item]:
    found: dict = {}        # key → Item. 같은 상품이 여러 글에 나오면 **가장 이른 글 날짜**를 남긴다
    posts = 0
    zero_recent = 0         # 최근 글 중 상품을 하나도 못 뽑은 글 수
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST))
        r.raise_for_status()
        t = HTMLParser(r.text)
        rows = []
        for a in t.css("a"):
            m = _ROW.search(f'href="{a.attributes.get("href") or ""}"')
            if not m:
                continue
            title = " ".join(a.text().split())
            if title.startswith("[신메뉴]") and m.group(1) not in [x[0] for x in rows]:
                rows.append((m.group(1), title))
        if not rows:
            raise RuntimeError(
                f"{BRAND}: 공지사항에서 `[신메뉴]` 글을 하나도 못 찾았다 — 2026-10-14 실측은 "
                f"5개였다. 목록 앵커(viewMode=view&idx=) 모양이 바뀌었는지 확인하라")

        for idx, title in rows[:MAX_POSTS]:
            time.sleep(DELAY)
            v = base.retry(lambda idx=idx: c.get(VIEW.format(idx)))
            v.raise_for_status()
            dm = _VIEW_DATE.search(v.text)
            if not dm:
                raise RuntimeError(f"{BRAND}: 글 {idx} {title!r} 에서 작성일을 못 읽었다")
            when = "-".join(dm.groups())
            if not "2020-01-01" <= when <= date.today().isoformat():
                raise RuntimeError(f"{BRAND}: 글 {idx} 작성일 {when} 이 이상하다")
            if '<div class="memoWrap' not in v.text:
                raise RuntimeError(f"{BRAND}: 글 {idx} 에 본문 상자(div.memoWrap)가 없다")
            lines = _lines(v.text)
            posts += 1
            if any(_COMEBACK.search(l) for l in lines):
                continue           # 작년 메뉴 복귀 글(모듈 주석)
            names = _names(lines)
            if not names and posts <= ZERO_RECENT:
                zero_recent += 1   # 이미지만 있는 글·문장 속 이름(버터떡) — 조용히 빠지는 자리
            for name in names:
                it = Item(brand=BRAND, name=name, released_at=when,
                          url=VIEW.format(idx))
                # 글을 최신순으로 읽으므로 나중에 본 것이 더 이르다. '모음' 글이 옛 상품을
                # 다시 묶어 올리면 최신 날짜가 붙어 신상이 되므로 이른 쪽을 남긴다.
                found[it.key] = it

    items = list(found.values())
    if zero_recent >= ZERO_MAX:
        raise RuntimeError(
            f"{BRAND}: 최근 [신메뉴] 글 {ZERO_RECENT}개 중 {zero_recent}개에서 상품을 못 뽑았다 — "
            f"2026-10-14 실측은 5글 중 1글(버터떡, 문장 속 이름)뿐이었다. 본문 꼴이 바뀌었는지 보라")

    # 글은 있는데 상품이 하나도 안 나오면 본문 꼴이 바뀐 것이다(이모지 줄 → 다른 꼴).
    if posts and not items:
        raise RuntimeError(
            f"{BRAND}: [신메뉴] 글 {posts}개에서 상품을 하나도 못 뽑았다 — 2026-10-14 "
            f"실측은 5글에서 상품이 나왔다. '이모지 + 이름' 줄 꼴이 바뀌었는지 확인하라")
    return items
