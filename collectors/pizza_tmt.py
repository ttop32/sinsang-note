"""티엠티피자(T.M.T PIZZA) — 새소식 게시판의 `[신메뉴]` 글. 0건인 날이 정상이다.

등록 담당자에게: `(FRANCHISE, "피자")` · SITES `https://tmtpizza.com/news`

공정위 `피자` 가맹점 5+ 중 **가맹점 15개**(프차몰 실측). 운영 (주)티엠티컴퍼니(울산). 2026-10-14 실측.
`notes/CANDIDATES-PIZZA4.md` 긴 꼬리 스크리닝에서 찾았다(도메인은 프차몰에 없어 `tmtpizza.com` 을 찍어 맞혔다).

## 경로 — 그누보드 `news` 게시판(짧은 주소 `/news`, 글 `/news/N`)

```
GET https://tmtpizza.com/news        목록 1쪽 9글(2026-01-09 ~ 2026-06-18) — 날짜 `YYYY.MM.DD` + 제목
GET https://tmtpizza.com/news/N      `[신메뉴]` 글만 연다(지금 3글: 13·11·9)
```
나머지 글은 직영점 개점·수상·유튜브·봉사·우수가맹점이다. 말머리 `[신메뉴]` 로만 고른다.
`/menu.php` 는 테마에 박힌 메뉴판(41개)이라 날짜가 없고, `badge_new` 는 **큰 칸 1개(트러플 머쉬룸)** 에만 붙는다 —
진열 강조지 목록이 아니라 안 쓴다(쓰면 1년 내내 트러플 머쉬룸 하나가 NEW 다).

## 상품명 — 글마다 꼴이 다르다. 세 단계로 본다

```
13  [신메뉴] 피자랑 찰떡궁합! 신메뉴 사이드 4종 출시      본문 `■ 투움바 스파게티 ₩7,000` × 4줄     → ① ■ 줄
11  [신메뉴] 입안 가득 퍼지는 풍미, 바질 크림 쉬림프 피자를 소개합니다.
                                                     본문 ‘바질 크림치즈 쉬림프 피자’           → ② 본문 ‘…’
 9  [신메뉴] 트러플 머쉬룸 피자 출시!                   본문이 이미지                          → ③ 제목 `X 출시`
```
① `■ 이름 ₩가격` 줄이 있으면 그것만 ② 없으면 본문의 ‘…’/'…' 인용(2~25자, `피자`·`스파게티` 같은 음식어가 들어간 것)
③ 그것도 없으면 제목에서 말머리를 떼고 `X 출시` 의 X(쉼표·느낌표가 없을 때만). 셋 다 실패하면 그 글은 건너뛴다
(빠지는 방향). ⚠️ 11번 글은 제목(`바질 크림 쉬림프`)과 본문(`바질 크림치즈 쉬림프`)이 다르다 — 본문을 따른다.

## 날짜 — 목록의 글 날짜 → `released_at`

## 🔴 0건이 정상이다 → `ALLOW_EMPTY = True`

`[신메뉴]` 글이 2026-01 · 05 · 06 세 번(반년에 1~2번)이다. 홍짜장·킹스타피자와 같은 게시판형이라 `DAYS`(540일)
밖 글은 내보내지 않는다. 오늘은 6건 수집·화면 0건(최근 06-02, 134일 전). 고장이면 예외가 난다
(목록 0행·날짜 못 읽음·`[신메뉴]` 글 0개).
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "티엠티피자"
ALLOW_EMPTY = True
SITE = "https://tmtpizza.com"
LIST = SITE + "/news"
DAYS = 540
DELAY = 1.5
MIN_ROWS = 4            # 실측 1쪽 9글
MIN_LAUNCH = 1          # 실측 [신메뉴] 3글

_ROW_HREF = re.compile(r"^https?://tmtpizza\.com/news/(\d+)$")
_DATE = re.compile(r"(20\d\d)\.(\d{2})\.(\d{2})")
_SQUARE = re.compile(r"^■\s*(.+?)\s*₩\s*[\d,]+")
_QUOTE = re.compile(r"[‘'“\"]([^’'”\"]{2,25})[’'”\"]")
_FOOD = re.compile(r"피자|스파게티|파스타|볶음밥|떡볶이|윙|감자|치즈|샐러드|소스|브레드|리조또")
_TITLE = re.compile(r"^\s*(?:\[신메뉴\]\s*)?(?:신메뉴\s*)?([^,!?~]+?)\s*출시\s*!*\s*$")
_BUNDLE = re.compile(r"\d+\s*종|세트|시리즈")


def _lines(html: str) -> list:
    box = HTMLParser(html).css_first("#bo_v_con")
    if box is None:
        return []
    raw = re.sub(r"<br\s*/?>|</p>|</div>|</li>", "\n", box.html or "", flags=re.I)
    return [" ".join(l.split()) for l in HTMLParser(f"<div>{raw}</div>").text().split("\n") if l.strip()]


def _names(title: str, lines: list) -> list:
    sq = [m.group(1) for l in lines if (m := _SQUARE.match(l))]
    if sq:
        return sq
    qs = []
    for l in lines:
        for q in _QUOTE.findall(l):
            q = " ".join(q.split())
            if _FOOD.search(q) and not _BUNDLE.search(q) and q not in qs:
                qs.append(q)
    if qs:
        return qs
    m = _TITLE.match(title)
    if m and not _BUNDLE.search(m.group(1)):
        return [m.group(1).strip()]
    return []


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST))
        r.raise_for_status()
        t = HTMLParser(r.text)
        rows = []
        for a in t.css("a"):
            href = a.attributes.get("href") or ""
            if not _ROW_HREF.match(href):
                continue
            title = " ".join(a.text().split())
            # 날짜는 같은 행(조상 li/tr) 텍스트에 있다
            node, d = a, None
            for _ in range(4):
                node = node.parent
                if node is None:
                    break
                d = _DATE.search(node.text())
                if d:
                    break
            if title and d and href not in [x[2] for x in rows]:
                rows.append(("-".join(d.groups()), title, href))
        if len(rows) < MIN_ROWS:
            raise RuntimeError(f"{BRAND}: 새소식 목록 {len(rows)}행 — 실측 9행이었다. "
                               f"글 주소(`/news/N`)나 날짜(`YYYY.MM.DD`) 꼴이 바뀌었는지 보라")
        launch = [x for x in rows if x[1].startswith("[신메뉴]")]
        if len(launch) < MIN_LAUNCH:
            raise RuntimeError(f"{BRAND}: `[신메뉴]` 말머리 글이 0개 — 실측 3개. 말머리가 바뀌었는지 보라: "
                               f"{[x[1] for x in rows[:5]]}")
        cutoff = (date.today() - timedelta(days=DAYS)).isoformat()
        found: dict = {}
        for d, title, url in launch:
            if d < cutoff:
                continue
            time.sleep(DELAY)
            v = base.retry(lambda url=url: c.get(url))
            v.raise_for_status()
            for name in _names(title, _lines(v.text)):
                it = Item(brand=BRAND, name=name, released_at=d, url=url)
                found[it.key] = it          # 최신순 → 같은 이름은 이른 날짜로 덮인다
    return list(found.values())
