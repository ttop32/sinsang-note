"""텐퍼센트커피(TENPERCENT COFFEE).

도메인이 둘인데 **용도가 다르다**(2026-10-03 실측).
  tenpercentcoffee.co.kr   창업 상담 랜딩이다. 12.8KB 한 장짜리고 링크가
                           `../css/style.css` 와 favicon 둘뿐이다. 메뉴가 없다.
                           robots.txt 는 404.
  tenpercentcoffee.com     **본 사이트**. 그누보드(gnuboard) SSR.
                           robots.txt 가 `User-agent: Yeti / Allow:/` 두 줄이다
                           — `*` 그룹이 없으니 우리에게 거는 규칙도 없다.
호스트 이름이 비슷해서 앞엣것만 보고 '메뉴 없음' 으로 접으면 안 된다.

메뉴는 게시판 6개다. 탭 목록은 페이지 안 `.sub_tab_top` 에 있다.
  bo_table=new     신메뉴      52건
  bo_table=sub22   시그니처     6건
  bo_table=sub23   커피        12건
  bo_table=sub26   말차         6건
  bo_table=sub24   텐업        39건
  bo_table=sub25   디저트/MD   25건

⚠️ **`new`(신메뉴) 게시판은 상품 목록이 아니다.** 글 한 건이 상품 한 건이 아니라
**캠페인 포스터 한 장**이고, 제목이 상품명이 아니라 `26.09 가을음료`·
`26.08 아보카도 3종`·`26.07 컵빙수 3종` 같은 묶음 이름이다. 본문도 포스터
이미지 한 장뿐이라 상품명을 못 뽑는다. 그래서 **상품으로 넣지 않는다**
(왓더버거에서 '신메뉴' 로 거르니 1+1 행사 글이 들어온 것과 같은 자리다).
대신 **날짜 교차검증에만 쓴다** — 아래 참고.

상품은 나머지 5개 게시판 **88건**이다. 목록이 이름·사진·글 주소를 다 준다.
목록 자체에는 날짜가 없다(이 스킨이 `.gall_info` 를 CSS 로 숨기는 게 아니라
아예 출력하지 않는다). 그래서 글마다 상세를 열어 `작성일` 을 읽는다.
RSS(`/bbs/rss.php`)는 "RSS 보기가 금지되어 있습니다" 로 막혀 있다.

신제품 신호(2026-10-03 전수 실측):
  - **배지가 없다.** 상품 카드는 `<a class="big">` + `title` + 글 링크가 전부다.
  - **이미지 파일명의 타임스탬프는 쓰지 마라.** `_<10자리 epoch>_` 가 박혀 있어
    탐앤탐스처럼 쓰고 싶어지는데 **사진 교체 시각**이지 출시일이 아니다.
    반례가 또렷하다 — `커피` 게시판 12건 중 7건(아메리카노 옆의 카페라떼·
    바닐라빈라떼·돌체라떼·밀크카라멜라떼·카페모카·콜드브루라떼·돌체콜드브루라떼)이
    **2026-08-06 15:4x 에 몰려** 있다. 상설 커피 메뉴를 그날 다시 찍어 올린 것이다.
    88건 중 67건이 2026-05-18 한 날이기도 하다.
  - 쓸 수 있는 건 상세의 **`작성일`(wr_datetime)** 이다. 2021~2026 으로 흩어진다.
    88건 분포:
        2026-01-05  61건   ← 일괄. 메뉴 대개편 때 게시판을 통째로 다시 만든 날
        2026-05-18  15건   ← 일괄. 글을 게시판 사이로 옮긴 날
                            (본문에 "…2026-05-18 …에서 이동 됨" 이 남아 있다)
        2026-09-21   3건 / 2026-09-07 2건 / 2026-08-07 2건
        2026-07-13   1건 / 2026-06-15 1건
        2024-03-14·2023-06-19·2021-11-02 각 1건
    앞의 두 날(76건, 86%)은 **일괄이라 버린다**(BULK_DAYS). 탐앤탐스
    2025-05-14/15 의 56건, 컴포즈커피 Last-Modified 2026-06-16 의 149건과
    같은 함정이다.
  - **흩어진 날짜가 진짜인지 교차검증했다.** `new` 게시판(캠페인 포스터)의
    등록일과 상품 게시판의 `작성일` 이 **분 단위로 맞물린다** —
        2026-06-15 13:57·13:58 `26.06 과채 3종`·`26.06 수박 2종`
                   ↔ 16:08 땅콩빵
        2026-08-07 13:18 `26.07 워터음료(피치/멜론)` ↔ 13:20 톡 깨먹는 케이크·
                                                      고메버터 소금빵
        2026-09-07 11:23 `26.09 가을음료` ↔ 11:44 시그니처라떼 · 11:49 하트파이/하트쿠키
    운영자가 캠페인 글과 상품 글을 같은 작업 세션에 올린다. 일괄 두 날을 뺀
    나머지는 실제 등록(≈출시) 시점이 맞다.
  - 그래도 이건 **게시판 등록일**이지 브랜드가 공표한 출시일이 아니다.
    `released_at` 이 아니라 `uploaded_at` 에 넣는다. 지어내지 않는다.
  - `is_new` 는 **비운다(None).** 상품마다 '신제품' 이라고 말해 주는 표시가
    어디에도 없다. 날짜가 있는 12건은 날짜로, 나머지는 diff 로 판정된다.

디저트/MD 게시판은 먹는 것과 굿즈가 **섞여 있다**(25건 중 굿즈 8건).
탐앤탐스처럼 탭 통째로 nonfood 를 찍을 수 없어서 이름으로 가른다.
base.is_nonfood 가 `텀블러`·`머그`·`우산` 은 잡지만 **`보틀`·`잔 세트` 는
일부러 빼 둔 말**이라(보틀캔디·빅보틀팝 때문) 여기서 좁게 보탠다. 실측으로
이 브랜드 88건에 오탐 0 이다 — 걸리는 건 아이스 텀블러·텐퍼센트 텀블러·
시그니처 텀블러·슬림핸들보틀·에스프레소 잔 세트·뉴 라떼잔 세트·핸들 글라스머그·
장우산 **8건뿐**이고 음료·디저트는 하나도 안 걸린다.

요청 수는 목록 9회 + 상세 88회 ≈ 97회다. 상세를 안 받으면 날짜가 통째로
사라지므로 받는다. MAX_DETAILS 로 막아 둔다.
"""
import re
import time


from . import base
from .base import Item

BRAND = "텐퍼센트커피"
SITE = "https://tenpercentcoffee.com"
BOARD_URL = f"{SITE}/bbs/board.php"
TAB_PAGE = f"{BOARD_URL}?bo_table=new"    # 탭 목록을 긁어올 출발점
NEW_BOARD = "new"                          # 캠페인 포스터 게시판. 상품이 아니다
MAX_PAGES = 8                              # 폭주 방지. 현재 가장 큰 sub24 가 3페이지.
MAX_DETAILS = 150                          # 폭주 방지. 현재 88건.
DELAY = 2.0

# 글을 통째로 다시 만든 날. 출시일이 아니다(docstring 참고).
BULK_DAYS = {"2026-01-05", "2026-05-18"}

# 디저트/MD 게시판의 굿즈. base.NONFOOD_WORDS 에 없는 말만 보탠다.
MD_WORDS = ("보틀", "잔 세트")

# 탭 `<li><a href="/bbs/board.php?bo_table=sub22">시그니처</a></li>`
_TAB = re.compile(r'<a\s+href="[^"]*bo_table=(\w+)"[^>]*>\s*([^<]+?)\s*</a>')

# 갤러리 카드. 사진 앵커(class="big") → 이름(title) → 글 번호(onclick) 순으로 나온다.
# ⚠️ onclick 의 주소에는 보고 있던 `&page=N` 이 묻어 있다. 번호만 뽑아 다시 짠다.
_CARD = re.compile(
    r'<a href="(?P<img>[^"]+)" class="big">.*?title="(?P<name>[^"]*)".*?'
    r'wr_id=(?P<id>\d+)', re.S)

# 상세의 작성일. `26-09-07 11:23` 두 자리 연도다.
_WROTE = re.compile(r"작성일</span><strong>\s*(\d{2})-(\d{2})-(\d{2})")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _tabs(html: str) -> list:
    """(bo_table, 탭이름) 목록. 캠페인 게시판(new)은 뺀다."""
    out, seen = [], set()
    for code, name in _TAB.findall(html):
        name = _clean(name)
        if code == NEW_BOARD or code in seen or not name:
            continue
        seen.add(code)
        out.append((code, name))
    return out


def _wrote(html: str) -> str:
    """상세의 작성일을 YYYY-MM-DD 로. 없거나 일괄 등록일이면 빈 문자열."""
    m = _WROTE.search(html)
    if not m:
        return ""
    day = f"20{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return "" if day in BULK_DAYS else day


def _nonfood(name: str) -> bool:
    return any(w in name for w in MD_WORDS)


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(TAB_PAGE))
        r.raise_for_status()
        tabs = _tabs(r.text)
        if not tabs:
            raise RuntimeError("텐퍼센트커피 메뉴 탭을 못 찾았다 — 게시판 구성이 바뀌었다")

        pending = []                                   # (Item, bo_table, wr_id)
        for code, cat in tabs:
            ids = set()
            for page in range(1, MAX_PAGES + 1):
                time.sleep(DELAY)
                rr = base.retry(lambda code=code, page=page: c.get(
                    BOARD_URL, params={"bo_table": code, "page": page}))
                rr.raise_for_status()
                fresh = 0
                for m in _CARD.finditer(rr.text):
                    wid = m.group("id")
                    if wid in ids:
                        continue
                    ids.add(wid)
                    fresh += 1
                    name = _clean(m.group("name"))
                    if not name:
                        continue
                    it = Item(
                        brand=BRAND,
                        name=name,
                        image=m.group("img"),
                        category=cat,
                        # is_new 를 안 채운다(None). 상품별 신제품 표시가 없다.
                        nonfood=_nonfood(name),
                        url=f"{BOARD_URL}?bo_table={code}&wr_id={wid}",
                    )
                    if it.key in seen:
                        continue
                    seen.add(it.key)
                    items.append(it)
                    pending.append((it, code, wid))
                # 범위를 넘긴 page 를 서버가 마지막 페이지로 되돌려주는 경우를 막는다
                if not fresh:
                    break

        if len(items) < 60:
            raise RuntimeError(f"텐퍼센트커피 {len(items)}건 — 게시판 목록 구조가 바뀌었다")

        # 날짜는 상세에만 있다. 목록을 다 모은 뒤 한 번만 돈다.
        read = 0
        for it, code, wid in pending[:MAX_DETAILS]:
            time.sleep(DELAY)
            d = base.retry(lambda code=code, wid=wid: c.get(
                BOARD_URL, params={"bo_table": code, "wr_id": wid}))
            if d.status_code != 200:
                continue
            if _WROTE.search(d.text):
                read += 1
            # 게시판 등록일이지 브랜드가 공표한 출시일이 아니다. uploaded_at 에 넣는다.
            it.uploaded_at = _wrote(d.text)

    # 일괄 두 날을 버려서 날짜가 붙는 건 12건 안팎이다. 그래서 '날짜 0건' 은
    # 실패로 보지 않는다. 다만 **작성일 표시를 한 건도 못 읽으면** 그건 우리 쪽
    # 고장이다(상세 레이아웃이 바뀐 것).
    if pending and read == 0:
        raise RuntimeError("텐퍼센트커피 상세에서 작성일을 한 건도 못 읽었다 "
                           "— 게시판 스킨이 바뀌었을 수 있다")
    return items
