"""킹스타피자 — 공지 게시판의 `신메뉴 … 출시` 글 제목과 등록일을 쓴다. 0건인 날이 정상이다.

등록 담당자에게: `(FRANCHISE, "피자")` · SITES `http://kingstarpizza.co.kr/html/brandstory/notice.php`  (⚠️ http)

공정위 `피자` 가맹점 5+ 중 **가맹점 26개**(프차몰 실측). 운영 (주)스타푸드코리아. 2026-10-14 실측.
`notes/CANDIDATES-PIZZA4.md` 긴 꼬리 스크리닝에서 찾았다(공식 도메인은 프차몰·검색에 없어 `kingstarpizza.co.kr`
을 한 번 찍어 맞혔다 — 루트는 meta refresh 로 `/html/index/` 에 넘긴다).

## 경로 — `BRAND STORY > 공지사항` 1쪽

```
GET http://kingstarpizza.co.kr/html/brandstory/notice.php        TOTAL 22, 1쪽 10행 + 상단 고정 1행
```
행 = `<tr>` → `strong.bbs-title`(제목) · 등록일 칸(`YYYY-MM-DD`). 상세 주소는 `?bbs_data=<base64>||&bgu=view`.
페이징은 `div.paging` 의 링크가 `bbs_data=base64("startPage=10&code=notice…")` 꼴이다(`?page=` 가 아니다 — 함정 ⑦).
**1쪽만 본다** — 최신순이고 1쪽이 2016-10 까지 내려가서 신메뉴 글 9개가 전부 1쪽에 있다.

메뉴 페이지(`/html/menu/menu01.php`, `menu_view` idx)는 배지·날짜가 없어 안 쓴다(긁으면 메뉴판 전체가 신상).

## 신호 — 제목이 곧 상품명이다

```
2026-04-20  신메뉴 소시지 포테이토 피자 출시!
2023-05-09  신메뉴 '치즈프라이피자' 출시!!
2022-08-25  신메뉴 블러디소보로 출시
2021-12-31  신메뉴 핫제육쉬림프피자&핫치킨쉬림프피자 출시!        → `&` 로 쪼갠다(엽떡 선례)
2020-06-11  신메뉴 트리플미트피자 출시!
2018-12-14  킹스타 겨울 신메뉴~아보카도바이트 피자 출시!
2018-05-09  킹스타 봄 신메뉴~ '와규소보로피자' 출시!
2017-08-01  킹스타피자 신메뉴 '바베큐 플레터 피자' 출시!
2017-01-20  킹스타피자 신메뉴 '풀드포크피자' 출시 !
(2021-07-21 알레르기 안내 · 2016-10-12 카카오톡 쿠폰 — `신메뉴` 가 없어 안 본다)
```
규칙: 제목에 `신메뉴` 와 `출시` 가 **둘 다** 있을 때만. 따옴표가 있으면 따옴표 안, 없으면 `신메뉴`(뒤 `~`) 와 `출시` 사이.
`N종`·`세트`·`시리즈` 가 남으면 묶음이라 버린다. 등록일은 글마다 하나라 `released_at` 이다.
🟡 블러디소보로처럼 이름에 `피자` 가 안 붙은 것도 있다 — 브랜드가 쓴 대로 둔다.

## 🔴 0건이 정상이다 → `ALLOW_EMPTY = True`

신메뉴 글이 **1~3년에 한 번**(2020·2021·2022·2023·2026)이다. 홍짜장·요아정과 같은 게시판형이라
`DAYS`(540일) 밖 글은 내보내지 않는다. 오늘은 2026-04-20 소시지 포테이토 피자 1건이 수집되고
화면(60일 창)에는 0건이다. 고장이면 0건이 아니라 예외가 난다(목록 행 0개·날짜 못 읽음·`신메뉴` 글 0개).

⚠️ 푸터에 `프로그램 신청 / 자원봉사, 후원 신청 / 기관방문 신청` 이 있다 — 복지관 템플릿을 고쳐 쓴 흔적이지
침해 흔적이 아니다(링크가 사이트 안 상대경로이고 내용 없음).
"""
import re
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "킹스타피자"

# 신제품 글 게시판이 유일한 소스라 **0건인 날이 정상**이다. collect 의 0건 가드를 끄되
# 로그에는 한 줄 찍힌다 — 사유는 collect.py 의 ALLOW_EMPTY 주석 참고.
ALLOW_EMPTY = True
SITE = "http://kingstarpizza.co.kr"
LIST = SITE + "/html/brandstory/notice.php"
DAYS = 540            # 홍짜장·짬뽕관과 맞췄다. 화면 노출은 rules.WINDOW(60일)가 따로 자른다
MIN_ROWS = 5          # 실측 1쪽 11행(고정 1 + 10)
MIN_LAUNCH = 3        # 실측 1쪽 신메뉴 글 9개

_DATE = re.compile(r"^(20\d\d)-(\d{2})-(\d{2})$")
_QUOTE = re.compile(r"['‘’\"“”]([^'‘’\"“”]{2,40})['‘’\"“”]")
_BETWEEN = re.compile(r"신메뉴\s*~?\s*(.+?)\s*출시")
_BUNDLE = re.compile(r"\d+\s*종|세트|시리즈")
_LEAD = re.compile(r"^(?:킹스타피자|킹스타)\s*")


def _names(title: str) -> list:
    if "신메뉴" not in title or "출시" not in title:
        return []
    m = _QUOTE.search(title)
    raw = m.group(1) if m else (_BETWEEN.search(title).group(1) if _BETWEEN.search(title) else "")
    out = []
    for p in re.split(r"\s*[&＆,]\s*", raw):
        p = _LEAD.sub("", " ".join(p.split())).strip(" ~!")
        if len(p) >= 2 and not _BUNDLE.search(p):
            out.append(p)
    return out


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST))
        r.raise_for_status()
    rows = []
    for tr in HTMLParser(r.text).css("table.board-basic-tbl tbody tr"):
        t = tr.css_first("strong.bbs-title")
        a = tr.css_first("td.bbs-subject a")
        tds = [" ".join(td.text().split()) for td in tr.css("td")]
        d = next((x for x in tds if _DATE.match(x)), "")
        if t is None or not d:
            continue
        href = (a.attributes.get("href") or "") if a else ""
        rows.append((d, " ".join(t.text().split()), SITE + href if href.startswith("/") else LIST))
    if len(rows) < MIN_ROWS:
        raise RuntimeError(f"{BRAND}: 공지 목록 {len(rows)}행 — 실측 11행이었다. "
                           f"'table.board-basic-tbl' 이나 등록일 칸이 바뀌었는지 보라")
    launch = [x for x in rows if _names(x[1])]
    if len(launch) < MIN_LAUNCH:
        raise RuntimeError(f"{BRAND}: 1쪽에서 `신메뉴 … 출시` 글을 {len(launch)}개만 찾았다 — 실측 9개. "
                           f"제목 꼴이 바뀌었는지 보라: {[x[1] for x in rows[:5]]}")

    cutoff = (date.today() - timedelta(days=DAYS)).isoformat()
    found: dict = {}
    for d, title, url in rows:                 # 최신순 → 같은 이름은 이른 날짜로 덮인다
        for name in _names(title):             # (재출시를 막으려고 창 밖 글까지 먼저 다 본다)
            it = Item(brand=BRAND, name=name, released_at=d, url=url)
            found[it.key] = it
    return [it for it in found.values() if it.released_at >= cutoff]
