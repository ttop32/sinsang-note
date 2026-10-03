"""홍짜장 — 공지사항 게시판의 등록일을 쓴다. 지금은 0건이고 그게 정상이다.

공정위 `중식` 업종 가맹점 수 **18위**(58개, 2024년 말). (주)한밭에프앤지.

**메뉴 페이지는 쓸 수 없다.** 사이트가 한 장짜리 랜딩(`/`)이고 그 안에 메뉴 28건이
`li.swiper-slide` 로 들어 있다. 2026-10-02 실측으로 28건 전부
  - 배지가 없다. 자리(`p.menu_tag`)는 있는데 **28건 모두 빈 문자열**이다.
  - 날짜가 없다. 상세도 없다 — 카드가 `href="#none"` 에 `data-idx` 로 여는
    JS 모달이라 상품별 주소 자체가 없다(김가네와 같은 구조).
  - HTML 전체에 `NEW`·`신메뉴`·`신상`·`출시` 라는 글자가 **0회** 나온다.
긁으면 짜장면·짬뽕·탕수육 같은 상시 메뉴 28건이 통째로 '신상'이 된다.

⚠️ **사진 업로드 날짜를 신상 신호로 쓰지 마라.** 소림마라와 같은 제작사 템플릿이라
   사진 경로에 날짜가 박혀 있다(`/upload/menu_01/2026_05_08/hero_….jpg`). 28건을
   세어 보면 2021-06-24 2건 / 2023-04-12 1건 / 2025-05-30 13건 / 2025-06-05 2건 /
   2026-05-08 7건 / 2026-07-06 1건(불닭냉면)이다. 2026-05-08 의 7건은 한 번에
   올라간 **사진 교체**지 상품 7종 출시가 아니다(돼지갈비후라이드·왕새우튀김·
   크림새우·멘보샤·간짜장·로제짬뽕·초계냉면 — 간짜장이 신상일 리 없다).
   소림마라는 **NEW 배지가 신호**였고 uploaded_at 은 그 배지가 3년 묵은 걸
   누르는 제동 장치였다. 여기엔 배지가 없으니 날짜만 남고, 날짜만으로는
   '사진을 새로 찍었다'와 '상품이 새로 나왔다'를 못 가른다. 그래서 안 쓴다.

남은 경로는 공지사항 게시판 하나다. 자체 CMS 의 `/board/index.php?board=<이름>` 이고
**등록일이 붙는다.** 2026-10-02 실측으로 게시판 네 개를 전부 받아 봤다:
  notice_01 (공지사항)  **1건** — "홍짜장 공식 인스타그램 개설 안내"(2026-09-01)
  event_01  (이벤트)    0건. 탭 3개(진행중/완료/전체)를 다 받아도 0건이다
  sns       (SNS)       0건. "게시물이 없습니다"
  menu_01   (메뉴)      0건. 메뉴는 게시판이 아니라 랜딩에 박혀 있다
  news_01·press_01·gallery_01 등은 "개발자에게 문의하십시오" = 없는 게시판이다
보도자료 게시판은 없다. 그래서 **공지사항만** 본다.

🔴 **이 어댑터는 지금 0건을 돌려준다. 그게 정상이고 의도다.**
   유일한 글이 인스타그램 개설 안내라서 상품이 아니다. 더본코리아 18개 브랜드와
   같은 칸이다(theborn.py docstring §2) — "보도자료가 없으니 0건"이지 고장이 아니다.
   고장이면 `fetch()` 가 예외를 던진다(1페이지가 비면 raise 한다).
   이 사이트는 2026년에 새로 열린 것으로 보인다(공지 1건이 2026-09-01, 인스타
   계정 이름이 `2026_hongjjajang_official`). 신메뉴 공지가 올라오면 그때 잡힌다.

상품명은 제목·본문을 **교차검증**해서만 뽑는다(탕화쿵푸·보배반점과 같은 규칙).
  ① 본문에서 ‘…’ 로 인용된 이름을 모으고
  ② 그중 **제목에도 글자 그대로 있는 것만** 채택한다.
⚠️ 브랜드명이 따옴표 안에 들어와 상품으로 둔갑하는 사고가 있었다(라홍방 선례).
   `_NOT_PRODUCT` 에 '홍짜장'을 넣지 **않는다** — '홍짜장(해물)'·'辛홍짜장' 처럼
   브랜드명이 그대로 상품명인 메뉴가 실재하기 때문이다. 대신 브랜드명과
   **정확히 같은** 후보만 따로 버린다(`_BRAND_ALONE`).

목록 제목은 잘리지 않는다(`board_list_desc` 쪽만 30자쯤에서 `..` 로 잘린다).
그래도 상세를 받는 건 교차검증에 본문이 필요해서다.

robots: `hongjjajang.com/robots.txt` → 200, text/plain. 본문이 두 줄뿐이다 —
        `User-agent: *` / `Allow:/`. 전면 허용이다.
약관: 푸터에 개인정보처리방침만 있고 **이용약관 페이지가 없다**. 수집·복제를
      금지하는 문구는 찾지 못했다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "홍짜장"
SITE = "https://hongjjajang.com"
LIST = SITE + "/board/index.php"
BOARD = "notice_01"   # 상품 신호가 있을 수 있는 유일한 게시판. 나머지는 전부 0건이다
MAX_PAGES = 3         # 2026-10-02 현재 1페이지뿐이다. 늘어날 자리를 남겨둔다
DAYS = 540           # 중식은 신메뉴가 연 1~4건이라 300일이면 브랜드 페이지가 빈다.
                     # 화면 노출은 rules.WINDOW(60일)가 따로 자르므로 넓혀도
                     # '오래된 게 신상으로 뜨는' 일은 없다(짬뽕관 어댑터와 맞췄다).
DELAY = 2.2

# 상품 글인가. 이 말이 없으면 상세를 받지 않는다.
_LAUNCH = re.compile(r"(출시|선봬|선보|론칭|신메뉴|신제품|한정 ?메뉴|새롭게)")

# 상품 글이 아닌데 위 동사를 쓰는 것들. 실측 1건("인스타그램 개설 안내")이
# '새롭게 개설했습니다'로 _LAUNCH 에 걸려서 '인스타그램'이 필요하다.
#
# 🔴 **'공지' 를 빼라는 지적을 반영했다.** 여긴 공지사항 게시판이라 글 제목이
#    `[공지] 신메뉴 … 출시` 꼴이 되기 쉽다. '공지' 를 _SKIP 에 두면 브랜드가
#    신메뉴를 올리는 날 **조용히 0건**이 된다. 대신 삼삼마라 어댑터처럼 머리말
#    `[공지]` 를 **떼고** 판정한다(아래 _names).
# 🔴 같은 이유로 '개설'·'개편'·'홈페이지' 도 뺐다 — "홈페이지 개편 기념 신메뉴"
#    같은 제목을 통째로 죽인다. '인스타그램' 하나로 실측 1건은 그대로 걸린다.
_SKIP = ("인스타그램", "오픈", "점 OPEN", "수상",
         "선정", "대상", "이벤트", "프로모션", "성료", "창업", "박람회", "채용",
         "정보공개서", "휴무", "안내말씀")

# 머리말. 판정 전에 뗀다(삼삼마라 어댑터와 같은 규칙).
_HEAD = re.compile(r"^\s*\[[^\]]{1,10}\]\s*")

_QUOTED = re.compile(r"[‘'`]([^’'`\n]{2,30})[’'`]")

# 따옴표 안이 상품이 아닌 것들.
_NOT_PRODUCT = ("브랜드", "프랜차이즈", "이벤트", "캠페인", "협약", "기념",
                "서비스", "인스타", "블로그", "채널", "대상", "축제")

# 지점명. `"점"` 을 _NOT_PRODUCT 에 넣으면 부분일치라 '점보마라탕'·'점보만두'
# 같은 실존 작명을 죽인다(라화쿵부가 실제로 '3KG 점보마라탕' 을 판다).
# 지점명은 항상 '…점' 으로 **끝나므로** 끝자리로만 본다.
_BRANCH = re.compile(r"점$")

# 브랜드명 자체가 상품으로 둔갑하는 걸 막는다(라홍방 선례). '홍짜장(해물)' 처럼
# 브랜드명을 품은 **진짜 상품**은 살려야 하므로 정확히 같을 때만 버린다.
_BRAND_ALONE = {"홍짜장", "홍짜장마라탕", "한밭에프앤지", "(주)한밭에프앤지"}


def _text(node) -> str:
    return " ".join(node.text().split()) if node else ""


def _date(s: str) -> str:
    m = re.search(r"(20\d{2})-(\d{1,2})-(\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    return f"{y:04d}-{mo:02d}-{d:02d}" if 1 <= mo <= 12 and 1 <= d <= 31 else ""


def _abs(src: str) -> str:
    """사이트 안 경로를 https 절대주소로. 밖이면 그대로 둔다."""
    if not src:
        return ""
    if src.startswith("//"):
        return "https:" + src
    return SITE + src if src.startswith("/") else src


def _rows(html: str) -> list:
    """목록 한 페이지 → [(등록일, 글번호, 제목, 요약, 썸네일)]."""
    out = []
    for li in HTMLParser(html).css("ul.board_list li"):
        a = li.css_first("a")
        if not a:
            continue
        idx = re.search(r"idx=(\d+)", a.attributes.get("href", ""))
        title = _text(li.css_first(".board_list_title"))
        when = _date(_text(li.css_first(".board_list_date")))
        desc = _text(li.css_first(".board_list_desc"))
        img = li.css_first(".board_list_thumb img")
        thumb = _abs(img.attributes.get("src", "")) if img else ""
        if idx and title and when:
            out.append((when, idx.group(1), title, desc, thumb))
    return out


def _names(title: str, body: str) -> list:
    """제목과 본문을 교차검증해 상품명을 뽑는다. 못 고르면 빈 목록."""
    # 머리말 `[공지]`·`[이벤트]` 는 떼고 본다. _SKIP 에 '공지' 를 두면 공지사항
    # 게시판의 신메뉴 글이 통째로 죽는다(_SKIP 주석 참고).
    t = _HEAD.sub("", " ".join(title.split()))
    if any(w in t for w in _SKIP) or not _LAUNCH.search(t):
        return []
    flat = t.replace(" ", "")
    out, seen = [], set()
    for m in _QUOTED.finditer(body):
        name = m.group(1).strip(" ,·∙")
        # 두 상품을 '·' 로 묶은 한 덩어리는 버린다. 본문이 각각을 따로 부르므로
        # 개별 상품은 이 반복에서 따로 잡힌다(보배반점에서 실제로 터진 오집이다).
        if len(name) < 2 or any(ch in name for ch in "·∙&?") or name in _BRAND_ALONE:
            continue
        if any(w in name for w in _NOT_PRODUCT) or _BRANCH.search(name):
            continue
        if name.replace(" ", "") not in flat or name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out


def _body_image(doc) -> str:
    """글 본문 이미지. 사이트 UI 이미지(/img/)는 뺀다."""
    for n in doc.css(".board_view_text img"):
        src = _abs(n.attributes.get("src", ""))
        if src.startswith("https://") and "/img/" not in src:
            return src
    return ""


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    cand, stop = [], False
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"board": BOARD, "page": page}))
            r.raise_for_status()
            rows = _rows(r.text)
            # 1페이지가 비면 마크업이 바뀐 것이다. 조용히 빈 목록을 돌려주지 않는다.
            if not rows:
                if page == 1:
                    raise RuntimeError(
                        f"{LIST}?board={BOARD} 1페이지에서 글을 못 찾았다. 마크업을 확인해라")
                break
            for when, idx, title, desc, thumb in rows:
                if when < floor:
                    stop = True
                    continue
                if any(w in title for w in _SKIP):
                    continue
                if not _LAUNCH.search(title + " " + desc):
                    continue
                cand.append((when, idx, thumb))
            if stop:
                break

        items: list[Item] = []
        seen = set()
        for when, idx, thumb in cand:
            time.sleep(DELAY)
            r = base.retry(lambda: c.get(
                LIST, params={"board": BOARD, "type": "view", "idx": idx}))
            r.raise_for_status()
            doc = HTMLParser(r.text)
            for s in doc.css("script,style"):
                s.decompose()
            title = _text(doc.css_first(".board_view_title"))
            body = _text(doc.css_first(".board_view_text"))
            if not title:
                continue
            img = _body_image(doc) or thumb
            url = f"{LIST}?board={BOARD}&type=view&idx={idx}"
            for name in _names(title, body):
                it = Item(brand=BRAND, name=name,
                          image=img if img.startswith("https://") else "",
                          released_at=when, is_new=True, url=url)
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
    return items
