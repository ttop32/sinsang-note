"""우지커피(OOZY COFFEE) — 보도자료의 '출시' 기사에서 뽑고, 메뉴판으로 검증한다.

(주)우지에프앤비. `oozycoffee.com` 은 아임웹(imweb) SSR 이고 경로가 숫자다
(`/27`·`/28`…). 2026-10-03 실측 기준으로 쓸 수 있는 면이 세 종류인데, **셋 중
어느 하나만으로는 신상을 못 가린다.** 셋을 어떻게 조합했는지가 이 어댑터의 전부다.

## ① 메뉴 카테고리 면 — 이름·사진은 있는데 날짜가 거짓이다

    NEW=/Vision  COFFEE=/coffee  COLD BREW=/27  BEVERAGE=/28  FRAPPE=/29
    ADE&MOJITO=/30  TEA&JUICE=/31  DESSERT=/32

`div.item_container._item_container` 안에 `p.title`(상품명) + `span.body`(설명) +
`div.img_wrap[data-src]`(이미지)가 들어 있다. 8면 합쳐 **상품 260종**이 나온다.
⚠️ `p.title` 의 텍스트에는 `span.body` 가 **중첩돼 같이 딸려 나온다.**
`p.title` 을 그대로 쓰면 이름이 `흑임자 모닝커피흑임자의 고소함, 묵직한 풍미에…`
가 된다. 꼬리의 body 를 떼야 상품명이다(`_name()`).

여기 날짜로 쓸 만한 건 이미지 CDN 경로의 `/YYYYMMDD/` 뿐인데 **못 쓴다.**
260종의 분포가 이렇다.

    20260407 153건(58.8%)  20260930 19  20260715 15  20260915 12  20260916 13
    20260623 11  20260408 8  20260429 4  20260804 6  20260331 6  …

**절반 이상이 2026-04-07 하루**다. 사이트를 통째로 다시 올린 날이고 상품 날짜가
아니다. 나머지도 믿을 게 못 된다 — `아포카토` 는 2026-07-15 인데 7/20 기사가
"기존 인기 메뉴"라고 쓰고, `서울플로트`·`참깨그라니따` 는 2025-10 출시인데
이미지가 2026-09-30 이다(사진만 다시 찍어 올렸다). 그래서 CDN 날짜는
**released_at·uploaded_at 어느 쪽으로도 내보내지 않는다.** 아래 한 자리에서만
쓴다 — 일괄 재업로드 묶음을 '기존 상품' 표식으로 쓰는 역필터(③).

## ② NEW 면(/Vision) — 상품명이 없다

컨테이너 24개(PC·모바일 중복이라 실 12종)가 **전부 `p.title` 이 빈 문자열**이고
`img_wrap._img_wrap.no_content` 포스터 한 장씩만 있다. 이미지 업로드일도
20260623·20260916 두 묶음뿐이다. 이름이 없으니 상품으로 만들 수 없다. 이 면은
메뉴 색인에도 넣지 않는다(이름 0건이라 자동으로 빠진다).

## ③ 보도자료(/57) — 날짜가 여기 있다. 그래서 여기가 본 소스다

아임웹 게시판(`?bmode=view&idx=…`)이고 5면 50건이다.

**먼저 일괄 재등록부터 셌다.** 버거운버거 `/NEWS` 가 24건 중 22건(92%)이
2026-08-20 한 날이라 못 쓴 전례가 있어서다. 우지커피는 50건의
`meta[article:published_time]` 이 **서로 다른 날짜 28개**로 흩어진다.
가장 큰 묶음이 2026-05-07 **6건(12%)**, 다음이 2024-12-31·2025-03-19 각 5건이다.
같은 출시를 여러 매체가 받아쓴 묶음이지 관리자의 몰아 올리기가 아니다 — 쓴다.

날짜는 `meta[property=article:published_time]` 을 쓴다(상세 HTML 의 JSON-LD
`datePublished` 와 같은 값이다). 목록에는 날짜가 안 나온다(`hide_time` 클래스).
브랜드가 그 날 출시를 알린 글이므로 `released_at` 에 넣는다 — 왓더버거·슬로우캘리·
GS25·오뚜기 보도자료 어댑터와 같은 근거다.

## 상품명을 어떻게 뽑나 — 홑따옴표만으로는 안 된다

한국 보도자료는 상품명을 `‘…’` 로 감싼다. 그런데 **그 따옴표가 상품만 감싸지
않는다.** 실측한 오집이 이렇다.

    ‘헬시플레저’ ‘웰니스 콘셉트’ ‘경험형 디저트’ ‘식감 중심 디저트’  → 마케팅 용어
    ‘32Oz 대용량’ ‘맛의 다양성’ ‘커피 이상의’                      → 수식어
    ‘2026 브랜드 고객충성도 대상’ ‘가맹하고 싶은 프랜차이즈 산업전망’   → 수상 이름
    ‘며 ’                                                  → 인용부호 짝이 어긋난 조각
    ‘우지말차’ ‘아포가토’ ‘딥카페라떼’                            → **기존 메뉴**(비교 대상)

금지어 목록으로 거르는 길도 있지만 늘어나기만 하고 끝이 없다. 대신
**①의 메뉴 색인과 교집합**을 쓴다. 따옴표 안의 말이 지금 메뉴판에 실제로 있는
상품명과 (공백을 턴 뒤) 정확히 일치할 때만 상품으로 본다. 위 오집 전부가
메뉴판에 없어서 한 건도 안 걸린다. 사이트 자신이 정답지다.

마지막 부류(기존 메뉴)만 교집합을 통과한다. 그건 **BULK 역필터**로 뗀다 —
이미지가 일괄 재업로드일(실측 2026-04-07, 전체의 58.8%) 묶음에 속한 상품은
그 날 이미 메뉴에 있던 것이므로, 그 뒤 기사가 언급해도 신상이 아니다.
`딥카페라떼`(2026-06-25 기사에 '호주식 커피'의 비교 대상으로 등장)가 여기서
떨어진다. 일괄일은 **박아두지 않고 매번 센다** — 한 날짜가 전체의 30%를 넘으면
그 날이 일괄일이다(현재 2026-04-07 하나뿐). 재업로드가 또 일어나도 따라간다.

## 기사 고르기

제목에 출시어(`신메뉴`·`신제품`·`출시`·`선보`·`라인업`·`공개`)가 있고 제외어가
없을 것. 제외어는 50건 제목을 전수로 읽고 맞췄다 — 가맹·수상·선정·협약·기부·
돌파·호점·이벤트·시상·앱·대출·박람회·채용·오픈·증정식·포토. 50건 중 32건이 남고,
그중 **상품이 실제로 잡히는 건 22건**이다. 나머지 10건은 "내달 4일 출시 예정"
류의 예고 기사라 본문에 상품명이 안 나온다 — 0건이 정상이다.

⚠️ `is_new=True` 를 전건에 붙이지만 이건 '전건 NEW 배지' 와 다른 얘기다.
배지를 믿은 게 아니라 **출시 기사만 담았기 때문**이다. 메뉴판 260종 중
44종(17%)만 올라온다. 전건 가드는 그래서 배지 비율이 아니라 "메뉴 색인 대비
너무 많이 담기면 교집합이 깨진 것"으로 건다(`_MAX_SHARE`).

## 중복 — 같은 출시를 여러 매체가 쓴다

`리얼수박주스` 는 2025-04-29·2026-05-07·2026-06-22·2026-06-25 네 기사에 나온다.
**가장 이른 기사 날짜**를 쓴다. 이 사이트는 신상만 모으는 곳이고, 계절 메뉴의
재출시는 신상이 아니다 — 늦은 날짜를 쓰면 작년 메뉴가 올해 신상으로 올라간다.

## 그 밖

이미지·설명·분류는 메뉴 색인에서 가져온다(보도자료 본문 사진은 포스터 한 장이라
상품마다 짝지을 수 없다). CDN 은 https 라 `base.derive()` 가 지우지 않는다.
`Item.url` 은 그 기사 주소를 건다. 요청은 메뉴 8 + 목록 5 + 상세 32 로 45회쯤이다.

robots.txt: `oozycoffee.com/robots.txt` 는 200/0바이트(빈 파일)라 금지 규칙이 없다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "우지커피"
ROOT = "https://oozycoffee.com"
BOARD_PATH = "/57"                 # 보도자료
# 메뉴 카테고리. /Vision(NEW)은 상품명이 비어 있어 뺐다(docstring §②).
MENU_PATHS = ("/coffee", "/27", "/28", "/29", "/30", "/31", "/32")
# 화면에 쓸 분류. 사이트 내비 MENU 하위 이름 그대로다.
CATEGORIES = {
    "/coffee": "커피", "/27": "콜드브루", "/28": "베버리지", "/29": "프라페",
    "/30": "에이드&모히또", "/31": "티&주스", "/32": "디저트",
}

DELAY = 2.0
MAX_LIST_PAGES = 5                 # 폭주 방지. 현재 5면 50건이 전부다.
MAX_POSTS = 60                     # 폭주 방지. 상세를 받는 건 제목 통과분뿐이다.
MIN_MENU = 150                     # 메뉴 색인이 이보다 적으면 선택자가 깨진 것이다
# 담긴 상품이 메뉴 색인의 이 비율을 넘으면 교집합이 망가진 것으로 본다.
# 실측 44/260 = 17%. 메뉴판을 통째로 담는 사고를 막는 가드다.
_MAX_SHARE = 0.50
# 한 CDN 날짜가 메뉴 색인의 이 비율을 넘으면 일괄 재업로드일이다(실측 58.8%).
_BULK_SHARE = 0.30

# 제목 고르기. 근거는 docstring §기사 고르기.
_RELEASE = ("신메뉴", "신제품", "출시", "선보", "라인업", "공개")
_NOT_PRODUCT = ("가맹", "수상", "대상", "선정", "협약", "기부", "돌파", "호점",
                "이벤트", "시상", "앱", "대출", "박람회", "채용", "오픈",
                "증정식", "포토", "완판", "기여")

# 본문의 상품명 후보. 홑따옴표 두 종류(‘’ 와 ')를 다 받는다.
_QUOTED = re.compile(r"[‘']([^’'‘]{2,30})[’']")
_PUBLISHED = re.compile(
    r"article:published_time'?\"?\s+content='?\"?(\d{4}-\d{2}-\d{2})")
# 이미지 CDN 경로의 업로드일. `https://cdn.imweb.me/thumbnail/20260916/xxx.png`
_CDN_DAY = re.compile(r"/(\d{8})/")
_LIST_NOTICE = re.compile(r"^공지\s*")
_LIST_BADGE = re.compile(r"\s*N$")      # 목록 제목 꼬리의 새 글 배지


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _flat(s: str) -> str:
    return (s or "").replace(" ", "")


def _name(con) -> tuple:
    """카드에서 (상품명, 설명). `p.title` 이 `span.body` 를 품고 있어 꼬리를 뗀다."""
    t = con.css_first("p.title")
    b = con.css_first("span.body")
    full = _clean(t.text()) if t is not None else ""
    body = _clean(b.text()) if b is not None else ""
    if body and full.endswith(body):
        full = full[:len(full) - len(body)].strip()
    return full, body


def _menu(c) -> dict:
    """메뉴 색인. 공백 턴 상품명 → (표시용 이름, 분류, 이미지, 설명, CDN 날짜)."""
    out = {}
    for path in MENU_PATHS:
        r = base.retry(lambda: c.get(ROOT + path))
        r.raise_for_status()
        time.sleep(DELAY)
        for con in HTMLParser(r.text).css("div.item_container._item_container"):
            name, desc = _name(con)
            if not name:
                continue
            iw = con.css_first("div.img_wrap")
            src = iw.attributes.get("data-src", "") if iw is not None else ""
            m = _CDN_DAY.search(src or "")
            # PC·모바일 섹션에 같은 카드가 두 번 들어 있다. 먼저 본 쪽을 쓴다.
            out.setdefault(_flat(name),
                           (name, CATEGORIES.get(path, ""), src or "",
                            desc, m.group(1) if m else ""))
    if len(out) < MIN_MENU:
        raise RuntimeError(f"우지커피 메뉴 색인 {len(out)}건 — "
                           "카테고리 면의 item_container 선택자가 깨졌다")
    return out


def _bulk_days(menu: dict) -> set:
    """일괄 재업로드일. 한 날짜가 전체의 30%를 넘으면 그 날이다(docstring §③)."""
    days = {}
    for v in menu.values():
        if v[4]:
            days[v[4]] = days.get(v[4], 0) + 1
    tot = sum(days.values()) or 1
    return {d for d, n in days.items() if n / tot > _BULK_SHARE}


def _posts(c) -> list:
    """보도자료 목록에서 (제목, 주소). 목록에 날짜는 없다."""
    out = []
    for page in range(1, MAX_LIST_PAGES + 1):
        r = base.retry(lambda: c.get(ROOT + BOARD_PATH, params={"page": page}))
        r.raise_for_status()
        time.sleep(DELAY)
        cards = HTMLParser(r.text).css("div.list-style-card")
        if not cards:
            break
        for cd in cards:
            a = cd.css_first("a.post_link_wrap")
            t = cd.css_first("div.title")
            if a is None or t is None:
                continue
            title = _LIST_BADGE.sub("", _LIST_NOTICE.sub("", _clean(t.text())))
            href = a.attributes.get("href", "")
            if title and href:
                out.append((title, href))
    if not out:
        raise RuntimeError(f"{ROOT}{BOARD_PATH}: 보도자료 목록이 비었다")
    # 같은 글이 여러 면에 걸쳐 중복될 일은 없지만 주소 기준으로 한 번 턴다.
    seen, uniq = set(), []
    for title, href in out:
        if href in seen:
            continue
        seen.add(href)
        uniq.append((title, href))
    return uniq[:MAX_POSTS]


def _is_product_post(title: str) -> bool:
    return (any(w in title for w in _RELEASE)
            and not any(w in title for w in _NOT_PRODUCT))


def _detail(c, href: str) -> tuple:
    """기사 1장. (released_at, 본문 텍스트)."""
    r = base.retry(lambda: c.get(ROOT + href))
    r.raise_for_status()
    time.sleep(DELAY)
    m = _PUBLISHED.search(r.text)
    view = HTMLParser(r.text).css_first("div.board_view")
    return (m.group(1) if m else ""), (_clean(view.text()) if view is not None else "")


def fetch() -> list[Item]:
    with base.client() as c:
        menu = _menu(c)
        bulk = _bulk_days(menu)

        # 상품명 → (가장 이른 기사 날짜, 기사 주소). 같은 출시를 여러 매체가 쓴다.
        found: dict = {}
        for title, href in _posts(c):
            if not _is_product_post(title):
                continue
            released, body = _detail(c, href)
            if not released or not body:
                continue
            for q in _QUOTED.findall(body):
                m = menu.get(_flat(q))
                if m is None or m[4] in bulk:
                    continue
                prev = found.get(m[0])
                if prev is None or released < prev[0]:
                    found[m[0]] = (released, href)

    if not found:
        raise RuntimeError("우지커피 0건 — 보도자료 본문에서 메뉴판과 겹치는 "
                           "상품명을 하나도 못 찾았다")
    if len(found) > len(menu) * _MAX_SHARE:
        raise RuntimeError(f"우지커피 {len(found)}건 / 메뉴 {len(menu)}건 — "
                           "따옴표 교집합이 깨져 메뉴판을 통째로 담고 있다")

    items = []
    for name, (released, href) in found.items():
        _, category, image, desc, _day = menu[_flat(name)]
        items.append(Item(
            brand=BRAND,
            name=name,
            desc=desc,
            image=image,
            category=category,
            released_at=released,
            is_new=True,            # '출시' 기사에서만 담는다(docstring)
            url=ROOT + href,
        ))
    items.sort(key=lambda i: i.released_at, reverse=True)
    return items
