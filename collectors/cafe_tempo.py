"""템포커피(tempo coffee) — NEWS 게시판의 신메뉴 글. 0건인 날이 정상이다.

등록 담당자에게: `(CAFE, "커피")` ·
SITES `http://tempocoffee.co.kr/web/cop/bbsWeb/selectBoardList.do?bbsId=BBSMSTR_000000000191`   (⚠️ http — https 는 연결 거부)

공정위 `커피` 가맹점 5+ 중 **가맹점 6개**(프차몰 실측). 운영 (주)템포컴퍼니. `notes/CANDIDATES-CAFE6.md` 긴 꼬리에서 찾았다.
2026-10-14 실측. 루트는 136B JS 리다이렉트 껍데기고 본체는 `/web/main/mainPage.do`(eGovFrame).

## 경로 — `EVENT&NEWS > NEWS` 목록 한 장

```
GET http://tempocoffee.co.kr/web/cop/bbsWeb/selectBoardList.do?bbsId=BBSMSTR_000000000191
    ul.list_news > li → strong.tit(제목) · p(본문 요약) · div.date(YYYY-MM-DD)     글 6개
```
1쪽 6글(전체 15글, 2022-11 ~ 2026-05 — 2쪽은 `pageIndex` POST) 중 신메뉴 글 2개(둘 다 2026-05-14).
나머지는 매장 오픈·가맹 안내다. 최신순이라 새 글은 1쪽에 온다(하루 최대 3글 실측).
EVENT 게시판(`…000190`)에도 같은 날 「여름 신메뉴 출시 소식 입니다.」가 있지만 **제목에 상품명이 없다** — 안 쓴다.
메뉴(`/web/content.do?proFn=9200000`)엔 `<div class="new">NEW</div>` 가 6개(애플시나몬라떼·마론라떼·애플시나몬티 ×2탭)
있지만 **손으로 짠 고정 HTML이고 날짜가 없다**(이미지 Last-Modified 도 전부 2026-03-27 배포 시각). 안 쓴다.

## 상품명 — 제목 괄호 안

```
여름신메뉴 (진미숫가루라떼, 겐마이현미 녹차)출시                 → 진미숫가루라떼 · 겐마이현미 녹차
여름 신메뉴 소식입니다.(블루베리 셔벗 에이드, 블루베리 셔벗 라떼)   → 블루베리 셔벗 에이드 · 블루베리 셔벗 라떼
```
제목에 `신메뉴` 가 있을 때 바깥 괄호 안을 `,`·`/` 로 쪼갠다. 겹친 괄호(`(iced only)`)는 지우고, `이벤트·오픈·시즌·날짜·iced/hot`
조각은 버린다(검수 재현 7꼴). 🔴 **창 안 신메뉴 글인데 이름이 0개면 raise** — 괄호 없는 제목(EVENT 46 꼴)이 NEWS 에 오면
1년 치가 조용히 빠지기 때문이다.
본문 요약의 `1. 진 미숫가루 라떼국내산 …` 은 이름과 설명 사이에 구분자가 없어 못 쓴다. 날짜 → `released_at`.

## 🔴 0건이 정상이다 → `ALLOW_EMPTY = True`

신메뉴 글이 **해에 한 번 남짓**(지금 2026-05-14 두 글뿐)이다. 홍짜장·킹스타피자와 같은 게시판형, `DAYS = 540`.
오늘은 4건 수집·화면 0건. 고장이면 예외(목록 0행·날짜 못 읽음)가 난다.
"""
import re
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "템포커피"
ALLOW_EMPTY = True
LIST = "http://tempocoffee.co.kr/web/cop/bbsWeb/selectBoardList.do?bbsId=BBSMSTR_000000000191"
DAYS = 540
MIN_ROWS = 3            # 실측 6글

_DATE = re.compile(r"^(20\d\d)-(\d{2})-(\d{2})$")
_BUNDLE = re.compile(r"\d+\s*종|세트|시리즈")
# 괄호 안이 상품명이 아닌 조각(검수 재현: `(오픈 이벤트)`·`(10월 1일)`·`(~11/30)`·`(가을 시즌)`·`(iced only)`).
_NOT_NAME = re.compile(r"이벤트|행사|기념|오픈|시즌|출시|iced|hot|only|~|\d+\s*[월/]|1\+1|2\+1", re.I)
_INNER = re.compile(r"\s*\([^()]*\)")


def _names(title: str) -> list:
    if "신메뉴" not in title:
        return []
    i, j = title.find("("), title.rfind(")")
    if i < 0 or j <= i:
        return []
    inner = _INNER.sub("", title[i + 1:j])          # 겹친 괄호 `(… (iced only), …)` 의 안쪽을 지운다
    out = []
    for p in re.split(r"\s*[,，、/]\s*", inner):
        p = " ".join(p.split())
        if len(p) >= 2 and not _BUNDLE.search(p) and not _NOT_NAME.search(p):
            out.append(p)
    return out


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST))
        r.raise_for_status()
    rows = []
    for li in HTMLParser(r.text).css("ul.list_news li"):
        t = li.css_first("strong.tit")
        d = li.css_first("div.date")
        title = " ".join(t.text().split()) if t else ""
        when = " ".join(d.text().split()) if d else ""
        if not title or not _DATE.match(when):
            raise RuntimeError(f"{BRAND}: NEWS 행에서 제목·날짜를 못 읽었다 — {title!r} {when!r}")
        rows.append((when, title))
    if len(rows) < MIN_ROWS:
        raise RuntimeError(f"{BRAND}: NEWS 목록 {len(rows)}행 — 실측 6행이었다. 'ul.list_news li' 가 바뀌었는지 보라")
    cutoff = (date.today() - timedelta(days=DAYS)).isoformat()
    found: dict = {}
    for when, title in rows:            # 최신순 → 같은 이름은 이른 날짜로 덮인다
        names = _names(title)
        # 신메뉴 글인데 이름을 못 뽑으면 1년 치가 통째로 빠진다(이 브랜드 신메뉴 제목 3개 중 1개가
        # 괄호 없는 꼴 — EVENT 46). 창 안 글이면 조용히 넘기지 않는다.
        if "신메뉴" in title and not names and when >= cutoff:
            raise RuntimeError(f"{BRAND}: 신메뉴 글 {title!r}({when}) 에서 상품명을 못 뽑았다 — "
                               f"제목 괄호 꼴이 바뀌었는지 보고 규칙을 고쳐라")
        for name in names:
            it = Item(brand=BRAND, name=name, released_at=when, url=LIST)
            found[it.key] = it
    return [it for it in found.values() if it.released_at >= cutoff]
