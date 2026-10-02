"""왓더버거 — 메뉴판이 아니라 **이벤트 게시판의 '출시' 글**에서 뽑는다.

(주)라이징스타. `whattheburger.co.kr` 은 그누보드5다. 홈(`/`)은 인트로 한 장이고
본체는 `/page.php?p_id=…` 와 `/bbs/board.php?bo_table=…` 다.

## 메뉴 페이지를 안 쓰는 이유 — 신호가 0건이다

`/page.php?p_id=menu` 에 전체 메뉴가 SSR 로 다 있다(213KB). 그런데
2026-10-02 전수 실측에서 **`NEW`·`신메뉴`·`신제품`·`출시`·`badge` 가 전부 0회**다.
이미지도 `…/pages/menu/img/menu_1-1.jpg` 처럼 테마에 박힌 단순 연번이라
날짜가 없다. 메뉴판을 긁으면 상시 메뉴 100여 건이 전부 '신상'으로 올라간다.

반면 **이벤트 게시판에는 날짜가 있다.** 그래서 슬로우캘리·theborn·GS25 와
같은 구조로 간다 — 출시 글만 골라 담는다.

    목록  /bbs/board.php?bo_table=gallery3        (왓더뉴스 > 이벤트, 갤러리 스킨)
    상세  /bbs/board.php?bo_table=gallery3&wr_id=N

'왓더뉴스' 아래 다른 두 게시판은 쓰지 않는다 — `gallery1`(홍보광고)은 유튜버
협찬 영상, `gallery2`(가맹점 인터뷰)는 창업 콘텐츠다.

## 역필터 — 이벤트 게시판은 상품 피드가 아니다

8건 전수를 눈으로 훑고 규칙을 맞췄다(2026-10-02).

| 제목 | 작성일 | 판정 |
|---|---|---|
| `[8월 옥수수 페스티벌 신메뉴 출시안내]` | 26-07-28 | **담는다** |
| `새우⚔️엑스팔리버 버거 출시` | 26-06-30 | **담는다** |
| `[8월 신메뉴 왓더버거 1+1 특별 매장 방문 혜택]` | 26-07-27 | 뺀다 — '신메뉴' 가 들었지만 1+1 행사다 |
| `[8월에도 배달 할인은 계속됩니다!]` | 26-08-03 | 뺀다 |
| `[모르면 손해! 왓더버거 APP에서는 더 싸게!]` | 26-07-27 | 뺀다 |
| `[왓더런치? 갓더런치! 점심 할인 이벤트]` | 26-07-27 | 뺀다 |
| `[7월 2주차] 쿠팡이츠 선착순 4,000원 할인!` | 26-07-10 | 뺀다 |
| `[배달보다 7,300원 저렴한 매장 전용 꼬끼오팩]` | 26-07-10 | 뺀다 |

규칙은 **제목에 `출시` 가 있고 제외어가 없을 것** 하나다. '신메뉴' 를 조건에
넣으면 안 된다 — 1+1 행사 글이 바로 그 단어를 쓴다(위 표 3행). 이게
`notes/` 가 경고하는 '가짜 신호' 의 교과서적인 사례라 규칙을 거꾸로 세웠다.

## 상품명 — 본문의 라인업 목록이 먼저, 없으면 제목

`[8월 옥수수 페스티벌 신메뉴 출시안내]` 처럼 제목이 캠페인 이름인 글이 있다.
제목만 쓰면 '옥수수 페스티벌' 이 상품이 돼 버린다. 본문에 라인업이 두 모양으로
들어 있어서 그걸 먼저 본다(2026-10-02 실측 12건, 전부 실제 메뉴다).

    <h2>[더티 옥수수 버거 라인업]</h2>
    <h3>- 더티옥수수 셧더버거</h3>  <p>달달한 옥수수와 …</p>     ← 버거 6종
    <h2>더티 옥수수 사이드도 놓치지 마세요!</h2>
    <ul><li>더티옥수수 스리마요 치킨박스</li> …</ul>              ← 사이드 6종

`<li>` 까지 보는 건 사이드 6종을 잃지 않기 위해서다. 다만 목록은 유의사항·
행사 안내에도 쓰이는 태그라 **길이와 제외어로 거른다**(`_looks_like_product`).
라인업이 하나도 안 잡히면 제목에서 꾸밈을 털어 **한 건**으로 담는다
(`새우⚔️엑스팔리버 버거 출시` → `새우⚔️엑스팔리버 버거`). 슬로우캘리와 같은
방침이다 — 쪼갤 근거가 없으면 쪼개지 않는다.

이모지(`⚔️`)는 브랜드가 실제로 쓰는 상품명이라 지우지 않는다.

## 날짜

상세의 `작성일 26-06-30 17:44` 이 유일한 날짜다. 2자리 연도라 `20` 을 붙인다.
브랜드가 그 날 출시를 알린 글이므로 `released_at` 으로 쓴다(슬로우캘리·샘표·
오리온 보도자료 어댑터와 같은 근거). 목록에는 날짜가 아예 안 나와서 담을 글은
상세를 한 번씩 받아야 한다. `is_new` 는 전부 True — '출시' 글만 담기 때문이다.

이미지는 상세 상단 첨부(`#bo_v_img`)를 쓰고 없으면 본문 첫 장을 쓴다.
한 글의 상품 여러 건은 **같은 대표 이미지**를 공유한다 — 본문 이미지가
라인업 순서와 1:1 로 대응한다는 보장이 없어서(옥수수 글은 상품 12건에
이미지 2장이다) 억지로 짝지우지 않는다.

robots.txt: 200/115바이트, `User-agent: * / Allow: / Disallow: /adm/ /install/`.
우리가 때리는 `/bbs/board.php` 는 걸리지 않는다. 사이트맵은 2020년에 멈춰
있고 주소가 구 도메인(`xn--o39av2myyrdd.com`)이라 쓰지 않는다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "왓더버거"
ROOT = "https://whattheburger.co.kr"
LIST_URL = ROOT + "/bbs/board.php"
BO_TABLE = "gallery3"          # 왓더뉴스 > 이벤트
DELAY = 2.0
MAX_POSTS = 20                 # 폭주 방지. 현재 글이 8건이고 담는 건 2건이다.

_RELEASE = "출시"
# 제목에 이게 있으면 상품 글이 아니다. 위 docstring 의 8건 전수 표가 근거다.
_NOT_PRODUCT = ("1+1", "할인", "쿠폰", "이벤트", "혜택", "APP", "앱")

_LEAD_BRACKET = re.compile(r"^\s*\[([^\]]*)\]\s*(.*)$")
_TAIL = re.compile(r"\s*(?:신메뉴\s*)?출시\s*(?:안내|소식)?\s*[!！.]*\s*$")
_LINE_HEAD = re.compile(r"^[-·•]\s*")
_WRITTEN = re.compile(r"(\d{2})-(\d{2})-(\d{2})")

# 라인업 목록에 섞여 들어오는 안내문을 거른다. 상품명은 짧고 값·기간이 없다.
_NOT_NAME = ("원", "%", "할인", "이벤트", "쿠폰", "기간", "매장", "주문",
             "유의", "문의", "안내", "참여", "※")
_NAME_MAX = 30


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _is_product_post(title: str) -> bool:
    return _RELEASE in title and not any(w in title for w in _NOT_PRODUCT)


def _looks_like_product(name: str) -> bool:
    """라인업 줄이 상품명인가. 길거나 안내문 냄새가 나면 버린다."""
    if not (2 <= len(name) <= _NAME_MAX):
        return False
    return not any(w in name for w in _NOT_NAME)


def _from_title(title: str) -> str:
    """제목에서 상품 이름. `[8월 …]` 처럼 통째로 괄호면 안의 말을 쓴다."""
    m = _LEAD_BRACKET.match(title)
    if m:
        inner, rest = m.group(1).strip(), m.group(2).strip()
        title = rest or inner
    return _TAIL.sub("", title).strip()


def _lineup(con) -> list:
    """본문에서 상품명 목록. 못 찾으면 빈 리스트."""
    names = []
    for node in con.css("h3"):
        t = _clean(node.text())
        if not t.startswith(("-", "·", "•")):
            continue
        t = _LINE_HEAD.sub("", t).strip()
        if _looks_like_product(t):
            names.append(t)
    for node in con.css("ul li"):
        t = _LINE_HEAD.sub("", _clean(node.text())).strip()
        if _looks_like_product(t):
            names.append(t)
    return list(dict.fromkeys(names))


def _posts(doc) -> list:
    """목록에서 (제목, 주소). 갤러리 스킨이라 표가 아니라 li 카드다."""
    out = []
    for li in doc.css("li.gall_li"):
        a = li.css_first("a.gall_con")
        h = li.css_first("h6")
        if not a or not h:
            continue
        title, href = _clean(h.text()), a.attributes.get("href", "")
        if title and href:
            out.append((title, href))
    return out


def _detail(c, href: str) -> tuple:
    """상세 1장. (released_at, 대표 이미지, 본문 노드)."""
    r = base.retry(lambda: c.get(href))
    r.raise_for_status()
    time.sleep(DELAY)

    doc = HTMLParser(r.text)
    dt = doc.css_first(".if_date")
    m = _WRITTEN.search(_clean(dt.text()) if dt else "")
    released = f"20{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""

    con = doc.css_first("#bo_v_con")
    img = doc.css_first("#bo_v_img img") or (con.css_first("img") if con else None)
    return released, (img.attributes.get("src", "") if img else ""), con


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST_URL, params={"bo_table": BO_TABLE}))
        r.raise_for_status()
        time.sleep(DELAY)

        posts = _posts(HTMLParser(r.text))
        if not posts:
            raise RuntimeError(f"{LIST_URL}?bo_table={BO_TABLE}: 글 목록이 비었다")

        for title, href in posts[:MAX_POSTS]:
            if not _is_product_post(title):
                continue
            released, image, con = _detail(c, href)
            names = _lineup(con) if con is not None else []
            if not names:
                one = _from_title(title)
                if not one:
                    continue
                names = [one]
            for name in names:
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=_from_title(title) if len(names) > 1 else "",
                    image=image,
                    released_at=released,
                    is_new=True,      # '출시' 글만 담는다
                    url=href,
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
    return items
