"""달리는커피(DALCU). (주)달리는커피코리아 — 배달커피 원조를 자처하는 브랜드다.

도메인부터가 함정이었다. 이름을 그대로 로마자로 옮긴 `dallinuncoffee.com`·
`dallineuncoffee.com`·`dalrineuncoffee.com`·`runningcoffee.co.kr` 등 14개가
전부 NXDOMAIN 이다. 실제 주소는 **dalcu.co.kr** 다 — '달리는커피'를 줄인
DALCU 이고, 회사 메일도 dalcukorea@dalcu.co.kr 다.

그누보드(Gnuboard5) 사이트다. 사람이 보는 면은 스킨을 입힌
`/bbs/content.php?co_id=menu` 한 장인데, 그 밑에 **게시판 원본이 그대로
열려 있다.** 그게 이 어댑터의 핵심이다.

    /bbs/content.php?co_id=menu            메뉴판 한 장(235카드, 사진 있음, 날짜 없음)
    /bbs/board.php?bo_table=food_table     푸드 113건 (샐러드·샌드위치·라이스보올·디저트)
    /bbs/board.php?bo_table=coffe_table    음료 102건 (coffe·non coffee·juice·
                                           smoothie ＆ frappe·ade ＆ tea)
    /bbs/board.php?bo_table=md_table       MD 18건 (텀블러 12·굿즈 6)
    /bbs/board.php?bo_table=<t>&wr_id=<n>  상품 상세

게시판 목록은 **분류와 날짜**를 주고 메뉴판은 **사진**을 준다. 둘을 상품명으로
잇는다 — 2026-10-03 실측에서 양쪽 고유 이름이 **229개로 정확히 같고 차집합이
양쪽 다 0** 이다(게시판 233행 중 4건은 같은 이름의 중복). robots.txt 는
`User-agent:* / Allow: /` 다.

## 신상 신호 — 배지가 **상품명 안에** 있다

이 브랜드는 배지 태그를 안 쓴다. 대신 담당자가 제목 앞에 `NEW)` 를 손으로
붙인다(`NEW)훈제오리현미박스`, `NEW) 공주밤 리코타 샐러드` — 괄호 뒤 띄어쓰기도
제각각이다). 235카드 중 **49건(20.8%)** 이다.

🔴 **이 배지만 믿으면 안 된다.** 20.8% 는 이디야(2017년 상품에 NEW)·버거킹
(31%) 과 같은 냄새가 나는 비율이고, 실제로 **늙어 있다** — 게시판 날짜를 붙여
보니 `NEW) 데리마요 우둔살&당근 현미부리또` 등 5건이 **2026-04-13**(173일 전),
`NEW) 딸바보코치니유자 샐러드` 계열 딸기 6종이 2026-02-26 이다. 반년 전
봄시즌 메뉴에 아직 NEW 가 붙어 있다.

그래서 **날짜를 같이 싣는다.** rules.is_fresh 는 is_new=True 라도 날짜가 있으면
날짜를 따르므로(`stamped >= cutoff`), 늙은 NEW 는 자동으로 걸러진다. 날짜가
없었다면 49건이 통째로 올라갔을 자리다.

NEW 묶음이 뉴스 게시판(`border_table`)의 출시 공지와도 맞는다 — '현미식단 5종
출시'(09-28) ↔ 현미박스 5건(09-28), '2026 가을시즌 공주밤 5종 출시'(09-07) ↔
공주밤 7건(09-07), '2026 여름시즌 화이트펄라떼 출시'(07-13) ↔ 화이트펄 3건
(07-13). 날짜가 맞물려서 게시판 날짜가 **등록일이 아니라 출시일**에 가깝다는
걸 확인했다. 그래도 아래 이유로 released_at 이 아니라 uploaded_at 에 넣는다.

## 날짜 — 연도가 안 적혀 있다. 그래서 역산하고 **검증한다**

그누보드 목록의 날짜 칸(`td_datetime`)은 `09-28` 처럼 **연도를 뺀 MM-DD** 다.
상세(`#bo_v_info`)에는 `작성일26-09-28 12:36` 로 연도가 있지만 그걸 받으려면
229요청이다.

목록이 **보드마다 날짜 내림차순으로 완전히 정렬**돼 있다(전건 확인). 그래서
맨 위부터 내려가며 MM-DD 가 **거꾸로 커지는 지점**마다 연도를 하나씩 깎으면
된다(`01-26` 다음이 `12-01` 이면 거기서 해가 바뀐 것이다). 추측으로 두지 않고
**보드별 맨 윗글의 상세를 한 번씩 받아 연도를 대조한다**(3요청). 어긋나면
RuntimeError 로 세운다 — 조용히 1년 틀린 날짜를 흘리는 것보다 낫다.

⚠️ **일괄 재등록이 있다.** 2025-09-23 에 48건, 2025-09-24 에 76건으로 233건 중
124건(53%)이 이틀에 몰려 있다. 사이트를 새로 만들면서 메뉴를 통째로 옮긴
자국이다. 그래서 날짜를 **released_at 이 아니라 uploaded_at 에 넣는다** —
rules.untrust_bulk_dates 가 uploaded_at 만 보고 이상치를 털기 때문이다
(이 브랜드의 날짜당 중앙값이 3건이라 20건 이상 & 30건 이상이 걸린다).
롯데웰푸드와 같은 처리다.

## 이름에서 `NEW)` 를 뗀다

떼지 않으면 base.display_name 의 제조사 접두 규칙이 `NEW)` 를 물어서 화면에
`NEW 훈제오리현미박스` 가 찍힌다 — 카드가 이미 NEW 배지를 그리므로 'NEW NEW'
가 된다. 게다가 담당자가 나중에 접두를 떼면 make_key 가 바뀌어 이력이 끊긴다.
떼는 쪽이 키도 안정적이다. 뗀 사실은 is_new=True 로 남는다.

MD(텀블러·굿즈 18건)는 nonfood 로 표시한다.
"""
import re
import time
from datetime import date

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "달리는커피"
SITE = "https://dalcu.co.kr"
MENU_URL = f"{SITE}/bbs/content.php"
BOARD_URL = f"{SITE}/bbs/board.php"
DELAY = 2.0
MAX_PAGES = 15       # 보드당 폭주 방지. 현재 최대 8페이지(113건 ÷ 15).

# 게시판 → 굿즈인가. md_table 은 텀블러 12 · 굿즈 6 으로 전건 비식품이다.
BOARDS = {"food_table": False, "coffe_table": False, "md_table": True}

# 담당자가 상품명 앞에 손으로 붙이는 신제품 표시. 괄호 뒤 띄어쓰기가 제각각이다.
_NEW_PREFIX = re.compile(r"^NEW\s*\)\s*", re.I)
# 목록의 날짜 칸. 오늘 쓴 글은 `14:22` 로 시각만 나온다.
_MMDD = re.compile(r"^(\d{2})-(\d{2})$")
_HHMM = re.compile(r"^\d{2}:\d{2}$")
# 상세의 작성일. 마크업이 `<strong class="if_date"><span class="sound_only">작성일
# </span>26-09-28 12:36</strong>` 라 **원문에는 '작성일' 과 숫자 사이에 태그가 낀다.**
# 정규식을 HTML 에 바로 대면 안 걸린다 — .if_date 의 텍스트를 뽑아서 본다.
_WRITTEN = re.compile(r"(\d{2})-(\d{2})-(\d{2})")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _abs(src: str) -> str:
    if not src:
        return ""
    return src if src.startswith("http") else SITE + src


def _menu_images(c) -> dict:
    """메뉴판 한 장에서 {상품명: 사진주소}. 게시판에는 사진이 없다."""
    r = base.retry(lambda: c.get(MENU_URL, params={"co_id": "menu"}))
    r.raise_for_status()
    out = {}
    for card in HTMLParser(r.text).css(".menu_border_s"):
        node = card.css_first(".menu_border_s_text_div")
        img = card.css_first("img")
        name = _clean(node.text()) if node else ""
        if name and name not in out:
            out[name] = _abs(img.attributes.get("src", "") if img else "")
    if len(out) < 100:
        raise RuntimeError(f"달리는커피 메뉴판 {len(out)}건 — 카드 구조가 바뀌었다")
    return out


def _rows(c, table: str) -> list:
    """게시판 목록 전체를 (분류, 제목, MM-DD, wr_id) 로. 날짜 내림차순 그대로 둔다."""
    out, seen = [], set()
    for page in range(1, MAX_PAGES + 1):
        if page > 1 or out:
            time.sleep(DELAY)
        r = base.retry(lambda: c.get(BOARD_URL, params={"bo_table": table, "page": page}))
        r.raise_for_status()
        trs = HTMLParser(r.text).css("table tbody tr")
        got = 0
        for tr in trs:
            a = tr.css_first(".bo_tit a")
            if not a:
                continue
            m = re.search(r"wr_id=(\d+)", a.attributes.get("href", ""))
            wr_id = int(m.group(1)) if m else 0
            if not wr_id or wr_id in seen:
                continue
            seen.add(wr_id)
            cat = tr.css_first("a.bo_cate_link")
            dt = tr.css_first(".td_datetime")
            out.append((_clean(cat.text()) if cat else "",
                        _clean(a.text()),
                        _clean(dt.text()) if dt else "",
                        wr_id))
            got += 1
        if not got:
            break
    return out


def _anchor_year(c, table: str, wr_id: int) -> int:
    """맨 윗글 상세에서 실제 연도. 아래 _with_years 의 역산을 검증하는 닻이다."""
    time.sleep(DELAY)
    r = base.retry(lambda: c.get(BOARD_URL, params={"bo_table": table, "wr_id": wr_id}))
    r.raise_for_status()
    node = HTMLParser(r.text).css_first(".if_date")
    m = _WRITTEN.search(_clean(node.text()) if node else "")
    if not m:
        raise RuntimeError(f"달리는커피 {table}#{wr_id} 상세에서 작성일을 못 읽었다 "
                           "— 게시판 스킨이 바뀌었을 수 있다")
    return 2000 + int(m.group(1))


def _with_years(dates: list, today: date) -> list:
    """MM-DD 목록(날짜 내림차순)에 연도를 붙인다. 거꾸로 커지면 해가 바뀐 것이다."""
    out, prev, year = [], None, today.year
    for raw in dates:
        m = _MMDD.match(raw)
        if _HHMM.match(raw):                      # 오늘 올린 글
            out.append(today.isoformat())
            prev = (today.month, today.day)
            continue
        if not m:
            out.append("")
            continue
        md = (int(m.group(1)), int(m.group(2)))
        if prev is None:
            if md > (today.month, today.day):     # 맨 윗글이 '미래'면 작년이다
                year -= 1
        elif md > prev:
            year -= 1
        prev = md
        out.append(f"{year:04d}-{md[0]:02d}-{md[1]:02d}")
    return out


def fetch() -> list[Item]:
    today = date.today()
    items: list[Item] = []
    seen = set()

    with base.client() as c:
        images = _menu_images(c)

        for table, goods in BOARDS.items():
            rows = _rows(c, table)
            if not rows:
                raise RuntimeError(f"달리는커피 {table} 0건 — 게시판 주소가 바뀌었다")

            days = _with_years([r[2] for r in rows], today)

            # 역산을 상세 한 건으로 검증한다. 틀린 연도를 조용히 흘리지 않는다.
            want = _anchor_year(c, table, rows[0][3])
            if days[0] and int(days[0][:4]) != want:
                raise RuntimeError(
                    f"달리는커피 {table} 연도 역산이 어긋났다 "
                    f"(역산 {days[0][:4]} / 상세 {want}) — 목록 정렬이 바뀌었을 수 있다")

            for (cat, raw_name, _, wr_id), day in zip(rows, days):
                is_new = bool(_NEW_PREFIX.match(raw_name))
                name = _NEW_PREFIX.sub("", raw_name).strip()
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    image=images.get(raw_name, ""),
                    category=cat.replace("＆", "&"),
                    # 일괄 재등록(2025-09-23·24 에 124건)이 섞여 있어 released_at 이
                    # 아니라 uploaded_at 에 둔다. rules.untrust_bulk_dates 가 이쪽만 턴다.
                    uploaded_at=day,
                    is_new=True if is_new else None,
                    nonfood=goods,
                    url=f"{BOARD_URL}?bo_table={table}&wr_id={wr_id}",
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)

    if len(items) < 150:
        raise RuntimeError(f"달리는커피 {len(items)}건 — 게시판 구조가 바뀌었을 수 있다")
    return items
