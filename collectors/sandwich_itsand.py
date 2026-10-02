"""잇샌드(itsand). 가맹점 23개. 가맹본부 (주)안다F&B(315-06-40037).

커피+샌드위치+샐러드+디저트를 같이 파는 카페형 브랜드다. 사이트는 그누보드(GNUBOARD)
이고 **메뉴가 게시판 한 개(`bo_table=menu`)로 돼 있다.** 2026-10-02 실측.

  GET /board/bbs/board.php?bo_table=menu&page=1..10    한 장 15건, 전부 148건
  GET /board/bbs/board.php?bo_table=menu&sca=<분류키>    분류별 추림

목록 카드가 이름·가격·사진·상세주소를 다 들고 있어 상세를 따로 받을 필요가 없다.
`li.element-item` 의 class 에 분류키가 그대로 박혀 있고(`mn_beverage` 등) 링크의
`wr_id` 가 그누보드 자동증가 번호다. 10요청에 148건.

**신제품 신호는 둘인데, 하나는 지금 비어 있다.**
  is_new  **`sca=mn_new`('신메뉴')가 브랜드가 따로 고른 독립 칸이다.** 화면 탭에도
          '신메뉴'로 나와 있다. **그런데 2026-10-02 현재 그 칸이 0건이다.**
          칸은 있는데 아무것도 안 담아 둔 상태다. 그래서 이 어댑터는 전건
          `is_new=False` 를 돌려준다 — 모름이 아니라 "브랜드가 신메뉴로 고른 게
          없다"가 맞다(에그드랍 category=NEW 와 같은 처분).
          ⚠️ 칸 자체가 사라지면 그건 다른 얘기라 RuntimeError 로 드러낸다.
  uploaded_at  **이미지 Last-Modified.** `wr_id` 순서와 맞물려 움직인다 —
          wr_id 153~148 이 2024-10-31, 79~76 이 2023-09-18, 3 이 2023-09-18 이다.
          2023-09 에 사이트를 열며 넣은 뭉치 위에 2024-10-31 한 뭉치가 얹혀 있다.
          **`released_at` 로 올리지 않는다** — 사진 올린 시각이지 출시일이 아니다.

⚠️ **이 브랜드는 2024-10-31 이후로 멈춰 있다.** 148건 중 가장 최근 사진이 그날이고,
'신메뉴' 칸도 비어 있다. 즉 **지금 이 어댑터가 화면에 올릴 신상은 0건이다.**
그래도 등록하는 건 (가) 신호가 가짜가 아니라 실재하고 (나) 다음에 뭔가 올라오면
그날 바로 잡히기 때문이다. 건수를 채우려고 전 메뉴를 신상으로 밀어 올리지 않는다.

⚠️ 카드마다 `<ul class="mn_icon">` 자리가 있는데 **148건 전부 비어 있다.**
퀴즈노스 `new_icon`(66건 전건에 붙어 가짜였다)과 반대 방향의 함정이다 — 거긴
전건에 붙어서 못 썼고 여긴 전건이 비어서 쓸 게 없다. 브랜드가 여기에 NEW 를
달기 시작하면 그게 훨씬 좋은 신호이니 그때 갈아타라.

요청 수: 목록 10 + 이미지 HEAD 상한 `MAX_HEADS`. 전건(148) HEAD 는 과하므로
**`wr_id` 가 큰(= 최근 등록) 쪽부터** 채우고 상한에 걸린 오래된 쪽은 비워 둔다
(하루엔소쿠 선례). 어차피 화면에 오를 일이 없는 구간이고, 날짜를 지어내느니
비우는 쪽이다. 개별 HEAD 실패도 그 상품만 비운다.

가격은 `권장소비자가격 : 8,500원` 으로 목록에 있지만 Item 에 자리가 없어 버린다.
`-` 나 빈 값인 것도 많다. 상세(`&wr_id=`)에는 목록에 없는 정보가 없어 받지 않는다
(실측: 설명·원재료·등록일 전부 없음. 페이지의 `2021.12.06` 은 개인정보처리방침
개정일이지 상품 날짜가 아니다 — 이걸 상품 등록일로 오인하지 마라).

robots.txt: 확인하지 못했다(이 어댑터는 받지 않는다). 이용약관도 푸터에 링크가
없고 개인정보처리방침만 있다. 금지 조항을 확인하지 못했다는 뜻이다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "잇샌드"
HOST = "https://itsand.co.kr"
LIST = HOST + "/board/bbs/board.php"
BO_TABLE = "menu"
NEW_SCA = "mn_new"       # 브랜드가 신메뉴를 담는 칸
MAX_PAGES = 12           # 폭주 방지. 현재 10장
MAX_HEADS = 50           # 이미지 HEAD 상한. 현재 148건이라 최근 50건만 날짜를 받는다
DELAY = 1.5              # 목록 요청 간격(초)
HEAD_DELAY = 0.8         # 이미지 HEAD 간격(초)

# li.element-item 의 분류 class → 화면 분류. 탭 라벨 그대로다.
CATEGORIES = {
    "mn_new":       "신메뉴",
    "mn_beverage":  "커피/음료/요거트",
    "mn_sandwich":  "샌드위치",
    "mn_salad":     "샐러드",
    "mn_lap":       "랩",
    "mn_riceballs": "현미주먹밥",
    "mn_dessert":   "디저트",
}

_WR_ID = re.compile(r"wr_id=(\d+)")
# Last-Modified: Thu, 31 Oct 2024 08:09:28 GMT
_MONTHS = {m: i for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}
_LM = re.compile(r"\w{3},\s*(\d{1,2})\s+(\w{3})\s+(\d{4})")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _uploaded_at(c, url: str) -> str:
    """이미지 Last-Modified 를 날짜로. 못 받으면 비운다 — 지어내지 않는다."""
    try:
        r = base.retry(lambda: c.head(url))
    except Exception:
        return ""
    m = _LM.search(r.headers.get("last-modified", ""))
    if not m or m.group(2) not in _MONTHS:
        return ""
    return f"{m.group(3)}-{_MONTHS[m.group(2)]:02d}-{int(m.group(1)):02d}"


def _cards(page: str) -> list:
    """목록 한 장에서 (wr_id, 이름, 분류키, 이미지경로, 상세주소)."""
    out = []
    for li in HTMLParser(page).css("li.element-item"):
        a = li.css_first("a[href]")
        tit = li.css_first(".tlt")
        img = li.css_first(".imgBox img")
        name = _clean(tit.text()) if tit else ""
        if not a or not name:
            continue
        href = a.attributes.get("href") or ""
        m = _WR_ID.search(href)
        cls = [x for x in (li.attributes.get("class") or "").split()
               if x.startswith("mn_")]
        out.append((int(m.group(1)) if m else -1, name,
                    cls[0] if cls else "",
                    (img.attributes.get("src") or "") if img else "",
                    href))
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    order: dict = {}
    seen = set()
    with base.client() as c:
        # 신메뉴 칸이 살아 있는지 먼저 본다. 이 어댑터의 is_new 가 거기 걸려 있다.
        r = base.retry(lambda: c.get(LIST, params={"bo_table": BO_TABLE,
                                                   "sca": NEW_SCA}))
        r.raise_for_status()
        if f"sca={NEW_SCA}" not in r.text:
            raise RuntimeError(
                f"잇샌드: '{NEW_SCA}'(신메뉴) 칸이 사라졌다 — 신상 신호 없음")
        new_names = {base.make_key(BRAND, n) for _, n, _, _, _ in _cards(r.text)}
        time.sleep(DELAY)

        for page in range(1, MAX_PAGES + 1):
            r = base.retry(lambda: c.get(LIST, params={"bo_table": BO_TABLE,
                                                       "page": page}))
            r.raise_for_status()
            cards = _cards(r.text)
            if page == 1 and not cards:
                raise RuntimeError("잇샌드: 1페이지 상품 0건 — 셀렉터가 깨졌다")
            if not cards:
                break

            fresh = 0
            for wr_id, name, cls, src, href in cards:
                it = Item(
                    brand=BRAND,
                    name=name,
                    image=HOST + src if src.startswith("/") else src,
                    category=CATEGORIES.get(cls, ""),
                    # 신메뉴 칸에 담긴 것만 True. 칸은 있고 비어 있으면 전건 False 다.
                    is_new=base.make_key(BRAND, name) in new_names,
                    url=href,
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                order[it.key] = wr_id
                items.append(it)
                fresh += 1

            time.sleep(DELAY)
            # 범위를 넘긴 page 는 같은 내용을 되돌려주므로 새 게 없으면 끝낸다.
            if not fresh:
                break

        if not items:
            raise RuntimeError("잇샌드: 상품 0건")

        # wr_id 가 큰(= 최근 등록) 쪽부터 날짜를 채운다. 상한에 걸리면 옛것이 빈다.
        for it in sorted(items, key=lambda x: -order[x.key])[:MAX_HEADS]:
            if not it.image:
                continue
            it.uploaded_at = _uploaded_at(c, it.image)
            time.sleep(HEAD_DELAY)

    return items
