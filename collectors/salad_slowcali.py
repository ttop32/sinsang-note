"""슬로우캘리 — 소식 게시판에서 신제품과 출시일을 뽑는다.

(주)슬로우캘리. 도메인은 **`slowcali.co.kr`** 이다(`slowcalli` 아님 — l 한 개).
샐러드 분류가 샐러디 한 곳뿐이라 두 번째 브랜드로 붙인다.

## 메뉴 페이지가 아니라 소식 게시판을 쓰는 이유

메뉴 페이지(`/bbs/content.php?co_id=menu`)에 46건이 SSR 로 다 있고 gnuboard
확장필드 `data-wr_9` 가 상품별 플래그로 노출된다. 그런데 **값을 전수 세어 보면
`new` 가 0건이다.**

    ''(빈값) 36 · 'best' 5 · '비건' 3 · 'hot' 2       ← 'new' 는 0건

`best`/`hot`/`비건` 은 쓰는데 `new` 는 한 번도 안 쓴다. 메뉴 상단의
`New Line up` 캐러셀 9건도 테마에 손으로 박아 둔 정적 HTML(`/images/ccon2_02_p1.png`
고정 경로)이라 CMS 신호가 아니다. **메뉴 페이지에는 신상 구분이 없다.**
그래서 소식 게시판이 이 브랜드의 진짜 신호다 — 거기엔 날짜까지 있다.

## ⚠️ 목록의 날짜에는 연도가 없다. 상세를 열어야 한다

gnuboard 목록의 `td.td_datetime` 이 `09-07`·`12-05` 처럼 **월일뿐**이다.
상세를 열어야 `작성일26-09-07` 로 연도가 나온다. 2026-10-02 실측에서
목록 `12-05` 가 실제로는 **2025-12-05**(10개월 전)였다 — 목록만 보고
"지난달"로 읽으면 1년을 틀린다. 달콤왕가탕후루에서 15개월 틀렸던 그 함정이고,
여기서도 그대로 재현됐다. **그래서 담을 글마다 상세를 한 번씩 받는다.**
목록이 글번호순이라 날짜순 정렬도 믿을 수 없다.

## 역필터 — 소식 게시판은 상품 피드가 아니다

14건 전수를 눈으로 훑고 규칙을 맞췄다(2026-10-02). 제목 접두가
`[NEW]`·`[NOTICE]`·`[OPEN]` 셋인데 **접두로는 못 가른다** —
`[NOTICE] ZERO 칼로리 ZERO SUGAR 애사비에이드 출시!` 는 신제품이고
`[NEW] 슬로우캘리 앱 출시` 는 먹는 게 아니다.

그래서 **제목에 `출시` 가 있고 아래 제외어가 없는 글**만 담는다.

| 제목 | 판정 |
|---|---|
| `[NOTICE] 포케와 한식의 만남! 8/24(월) 육회포케 출시!` | 담는다 |
| `[NOTICE] ZERO 칼로리 ZERO SUGAR 애사비에이드 출시!` | 담는다 |
| `[NEW] 두 가지 고기를 한번에! 더블프로틴 보울 2종 출시` | 담는다 |
| `[NEW] 스프 신메뉴 3종 출시` | 담는다 |
| `[NEW] T.H.E SALAD 신메뉴 4종 출시` | 담는다 |
| `[NEW] 마이픽포케 출시` | 담는다 |
| `육회포케 출시 10일만에 1만개 판매 돌파!` | `돌파` — 이미 나온 상품의 성과 글 |
| `[NEW] 슬로우캘리 앱 출시` | `앱` — 먹는 게 아니다 |
| `[NOTICE] 신메뉴 출시 기념 앱 이벤트 안내` | `이벤트` — 행사지 상품이 아니다 |
| `[NOTICE] 슬로우캘리 앱 혜택 개편 안내` · `[NOTICE] 메뉴 가격 조정 안내` · `[NOTICE] 앱 리뉴얼` ×2 · `[OPEN] 홈페이지 리뉴얼` | `출시` 가 없어 애초에 안 걸린다 |

## 글 하나 = 상품 하나로 둔다. 쪼개지 않는다

`스프 신메뉴 3종`·`T.H.E SALAD 신메뉴 4종`·`더블프로틴 보울 2종` 처럼 묶음
단위 글이 있다. 쪼개려면 본문에서 개별 상품명을 뽑아야 하는데, 본문이
이미지 한두 장뿐이라 **쪼개는 순간 이름을 지어내게 된다.** 묶음 그대로 둔다
(`notes/CANDIDATES-BAKERY.md` 의 "시리즈 단위" 처리와 같다).

이름은 제목에서 꾸밈말을 턴다. 14건 전수로 맞춘 세 규칙이고, 그 밖의 손질은
안 한다 — 규칙을 늘릴수록 멀쩡한 상품명을 깎는다.
  ① `[NEW]` 같은 접두 대괄호를 뗀다
  ② `!` 로 끊어 **마지막 조각**만 남긴다 (`두 가지 고기를 한번에! 더블프로틴…`)
  ③ 앞의 날짜(`8/24(월) `)와 뒤의 `출시` 를 턴다

`released_at` 은 상세의 작성일이다. 브랜드가 그 날 출시를 알린 글이므로
출시일로 쓴다. ⚠️ **다만 예고 글은 '공지 올린 날'이 들어간다** —
`[NOTICE] 포케와 한식의 만남! 8/24(월) 육회포케 출시!` 는 제목이 출시일을
8/24 라고 말하는데 작성일이 **2026-08-20** 이라 나흘 앞선 값이 담긴다.
제목의 날짜를 파싱해 덮어쓸 수도 있지만, 그 표기가 `8/24(월)` 한 건뿐이라
규칙을 만들 근거가 못 된다. **며칠 이르게 잡히는 건 알고 두는 것이다.** `is_new` 는 전부 True — 브랜드가 '출시'라고 낸 글만 담기 때문이다
(샘표·오리온·아워홈 보도자료 어댑터와 같은 근거).

robots.txt: **200 / 22바이트 / `User-agent:* / Allow: /`**. `co_id=provision` 은
이름과 달리 개인정보처리방침이고 크롤러·복제 금지 조항이 없다. 이용약관 본문은
사이트에서 찾지 못했다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "슬로우캘리"
ROOT = "https://www.slowcali.co.kr"
LIST = ROOT + "/bbs/board.php"
BO_TABLE = "main_news"
DELAY = 2.5
MAX_POSTS = 30   # 폭주 방지. 현재 글이 14건이고 그중 담는 건 6건이다.

# 제목에 이게 있어야 상품 글이다.
_RELEASE = "출시"
# 있으면 상품 글이 아니다. 위 docstring 의 14건 전수 표가 근거다.
_NOT_PRODUCT = ("앱", "이벤트", "돌파", "혜택", "가격", "리뉴얼")

_TAG = re.compile(r"^\s*\[[^\]]*\]\s*")          # [NEW] · [NOTICE] · [OPEN]
_DATE_HEAD = re.compile(r"^\d{1,2}/\d{1,2}\([^)]*\)\s*")   # 8/24(월)
_TAIL = re.compile(r"\s*출시\s*[!！.]*\s*$")
_WRITTEN = re.compile(r"작성일\s*(\d{2})-(\d{2})-(\d{2})")


def _is_product(title: str) -> bool:
    return _RELEASE in title and not any(w in title for w in _NOT_PRODUCT)


def _pick(title: str) -> str:
    """제목에서 상품 이름. 못 뽑으면 빈 문자열(그 글은 버린다)."""
    t = _TAG.sub("", title)
    # 앞의 꾸밈 문구를 끊는다. 제목이 '…출시!' 로 끝나는 게 흔해서 마지막
    # 조각이 빈 문자열이 된다 — 그냥 [-1] 을 쓰면 이름이 통째로 사라진다.
    parts = [p for p in t.split("!") if p.strip()]
    t = parts[-1] if parts else t
    t = _DATE_HEAD.sub("", t.strip())
    return _TAIL.sub("", t).strip()


def _detail(c, href: str):
    """상세 1장. (released_at, image). 날짜가 여기에만 있다(위 docstring 참고)."""
    r = base.retry(lambda: c.get(href))
    r.raise_for_status()
    time.sleep(DELAY)

    doc = HTMLParser(r.text)
    body = " ".join((doc.body.text() if doc.body else "").split())
    m = _WRITTEN.search(body)
    released = f"20{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""
    # 본문 첨부만 고른다. 헤더·퀵메뉴 아이콘(/images/…)이 섞이면 안 된다.
    img = ""
    for n in doc.css("img"):
        src = n.attributes.get("src", "")
        if f"/data/file/{BO_TABLE}/" in src:
            img = src
            break
    return released, img


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST, params={"bo_table": BO_TABLE}))
        r.raise_for_status()
        time.sleep(DELAY)

        posts = []
        for tr in HTMLParser(r.text).css("table tr"):
            a = tr.css_first("td.td_subject a")
            if not a:
                continue
            title = " ".join(a.text().split())
            href = a.attributes.get("href", "")
            if title and href and _is_product(title):
                posts.append((title, href))

        for title, href in posts[:MAX_POSTS]:
            name = _pick(title)
            if not name:
                continue
            released, img = _detail(c, href)
            it = Item(
                brand=BRAND,
                name=name,
                desc=_TAG.sub("", title),
                image=img,
                released_at=released,
                is_new=True,     # 브랜드가 '출시'라고 낸 글만 담는다
                url=href,
            )
            if it.key in keys:
                continue
            keys.add(it.key)
            items.append(it)
    return items
