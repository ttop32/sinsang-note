"""김가네 · 토마토도시락.

**두 브랜드를 한 파일에 둔 이유는 CMS 가 같아서다.** 주소 형태가
`/board/index.php?board=menu_01&sca=…` 로 글자까지 같고, '신메뉴' 를 별도 `sca`
값으로 빼 둔 설계도 같다(김가네 `sca=newmenu`, 토마토도시락 `sca=new`).
회사는 다르다 — (주)김가네(206-86-04573) 와 (주)다채원(204-86-24461) 이다.
파서가 공유되는 것뿐이니 한쪽 마크업이 바뀌면 그쪽만 갈라내면 된다.
(⚠️ 토마토도시락은 공정위 `분식` 의 **토마토김밥**((주)푸름에프앤에스)과 다른 회사다.)

둘 다 robots.txt 가 **200 / 21바이트 / `User-agent: * / Allow:/`** 이고
이용약관 문서가 아예 없다(푸터에 개인정보처리방침·이메일무단수집거부만).
전부 SSR 이고 TLS·이미지 모두 https 다. 혼합콘텐츠 문제가 없다.

## 신제품 신호가 두 브랜드에서 서로 다르다

### 김가네 — 상품별 NEW 배지. 신호 셋이 서로를 검증한다
🔴 **선행 조사(`notes/CANDIDATES-THIN.md` §3-2)가 "날짜도 배지도 없다"고 적어
둔 것을 정정한다. 배지가 있다.** 조사는 신메뉴 탭(`sca=newmenu`)만 봤는데,
그 탭의 카드에는 배지가 안 붙는다. **일반 카테고리 카드에 붙는다.**

    <div class="img rel" style="background-image:url('…')">
        <ul class="detail_ico abs"><li><img src="…/new.png" alt="NEW"></li></ul>

2026-10-02 실측 — 일반 카테고리 4장 74건 중 **NEW 6건**. 전수가 아니고,
같은 자리에 **BEST 7건**이 따로 붙어 섹션 장식도 아니다(달콤왕가탕후루의
14/14 전수 배지와 정반대다). 그리고 그 6건이 다른 두 신호와 정확히 겹친다.

| 신호 | 결과 |
|---|---|
| `detail_ico` 의 `alt="NEW"` | 꼬마김밥 · 함박정식 · 뚝배기불고기 · 어린이돈까스 · 물쫄면 · 찐만두 |
| `sca=newmenu` 탭 6건 | 같은 6건 |
| `data-idx` 최대 6개 (149·151·154·155·156·157, 일반 최대 148) | 같은 6건 |

셋이 독립적으로 같은 답을 낸다. **판정은 배지로 한다**(상품에 붙는 신호라
탭 큐레이션보다 강하다). 신메뉴 탭과 연번은 그 배지가 아직 관리되고 있는지
확인하는 **교차검증**으로만 쓴다 — `_cross_checked()` 가 매 수집마다 다시
센다. 셋이 어긋나기 시작하면(브랜드가 탭이나 배지 하나를 방치하면) 로그에
남을 자리이지 조용히 믿을 자리가 아니다.

⚠️ **일반 카테고리에서는 설명문이 HTML 주석 안에 들어 있다.**

    <p class="menu_name">꼬마김밥</p>
    <!-- <p class="menu_info text">한입에 쏙~~알찬 속재료를…</p> -->

렌더 텍스트만 뜨면 본문처럼 보이는, 이 레포가 네 번째로 만나는 함정이다
(노티드·푸르밀·원할머니·오봉도시락). 신메뉴 탭에서는 같은 `<p>` 가 주석
밖에 **살아 있어서** 설명은 그쪽에서만 가져온다.

### 토마토도시락 — 진짜 상품별 NEW 배지
`<div class="labels"><span class="new">` 가 **카테고리를 가리지 않고 따라다닌다.**
2026-10-01 실측: 전체 110건 중 3건(`돈불튀김`·`돈불김치볶음밥`·`치킨스테이크덮밥`),
`sca=7`(덮밥) 10건 중 1건, `sca=3`(기본도시락) 17건 중 1건. 신메뉴 탭에만
붙는 장식이 아니라 상품에 붙는 배지다. 달콤왕가탕후루의 14/14 전수 배지와
정반대 경우라 그대로 쓴다.

⚠️ **전체 목록(`sca=all`)을 받아야 한다.** 이름이 붙은 카테고리 6개를 다 더해도
54건뿐인데 전체는 108건이고, NEW 3건 중 `돈불김치볶음밥` 이 그 6개 어디에도
없다. 카테고리만 돌면 신상을 하나 잃는다. 그래서 전체를 받고, 분류명은
카테고리 6장을 따로 받아 `idx` 로 붙인다 — **절반(54/108)은 분류가 빈다.**
빠진 `sca` 값이 더 있나 찾아봤지만 `1·4·10·11` 은 0건이고 `9`(계절메뉴)도
0건이라, 나머지 54건은 CMS 에서 분류가 안 달린 상품들이다. 분류는 화면의
2단 분류(`brand_sub`)가 따로 책임지므로 여기서 비는 건 표시 손실뿐이다.

## 날짜는 두 브랜드 다 비운다 — 이미지 경로의 날짜는 출시일이 아니다

이미지 URL 이 `/upload/menu_01/2026_05_19/hero_…_2026_05_19_18_06_22.png` 꼴이라
날짜가 공짜로 들어오는 것처럼 보이는데, **김가네에서 반례가 잡혔다.**

    등심돈까스        idx=45   이미지 2026_05_19   ← idx 45 면 한참 전 상품이다
    순두부찌개        idx=20   이미지 2026_09_30   ← 어제
    매콤철판해물볶음밥 idx=138  이미지 2026_09_30

`idx=20` 짜리 오래된 상품의 이미지 날짜가 어제다. **사진만 교체해도 갱신된다.**
업로드 시각이지 출시일이 아니므로 `released_at` 은 물론 `uploaded_at` 에도
넣지 않는다. 신제품 판정은 위 두 신호와 collect 의 어제 대비 diff 에 맡긴다.

보도자료 게시판(`board=sns&sca=news`)도 봤다. 김가네는 **2022-04-27 에서 멈췄고**
(그 안에 '가을 신메뉴 7종' 같은 글이 있지만 2019년이다), 토마토도시락은 223건이
있으나 대표 학위 취득·수상 같은 회사 소식이라 상품 소스가 못 된다. 둘 다 안 쓴다.

## 상품별 주소
김가네는 **없다.** 카드가 `<a href="#none" data-idx="149">` 인 JS 모달이고,
검색엔진에 남은 `…&idx=102` 를 직접 받아 보면 `idx` 를 무시하고 목록을
그대로 돌려준다(PC·모바일 둘 다 확인). `url` 을 비워 `base.SITES` 폴백에 맡긴다.
토마토도시락은 **있다** — `…&sca=new&type=list&idx=266`.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRANDS = ["김가네", "토마토도시락"]

GIMGANE = "https://www.gimgane.co.kr"
TOMATO = "https://www.tomatodosirak.co.kr"
BOARD = "/board/index.php"
DELAY = 2.5   # robots 는 전면 허용이지만 둘 다 작은 사이트다. 여유를 둔다.

# 김가네 일반 카테고리. '김가네 추천 메뉴'(sca=new)는 신메뉴와 같은 성격의
# 큐레이션 탭이라 분류로 쓰지 않는다 — 넣으면 추천 상품의 분류가 '추천' 이 된다.
GIMGANE_CATEGORIES = (
    ("김밥류",  "2"),
    ("밥류",    "4"),
    ("분식류",  "3"),
    ("사이드류", "6"),
)
GIMGANE_NEW = "newmenu"

# 토마토도시락 카테고리. 분류명을 붙이는 용도고, 상품 자체는 sca=all 로 받는다.
TOMATO_CATEGORIES = (
    ("덮밥/마요/와퍼",      "7"),
    ("비빔밥/볶음밥/찌개",   "2"),
    ("기본도시락",          "3"),
    ("명품시리즈",          "5"),
    ("떡볶이/치킨/스파게티", "8"),
    ("반찬/사이드/추가",     "6"),
)

# style="… url('https://…/hero_x.png') …" / style="background-image: url('…')"
_BG = re.compile(r"url\(['\"]?([^'\")]+)")


def _text(node, sel) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _bg_image(node, sel) -> str:
    """배경 이미지로 깔린 상품 사진. 두 사이트 다 <img> 가 아니라 style 이다."""
    n = node.css_first(sel)
    m = _BG.search(n.attributes.get("style", "") or "") if n else None
    return m.group(1) if m else ""


def _badges(card) -> list:
    """카드 좌상단 아이콘. 지금 관측되는 값은 NEW 와 BEST 둘뿐이고 글자가
    아니라 이미지라 alt 로 읽는다."""
    return [a for a in (i.attributes.get("alt", "")
                        for i in card.css("ul.detail_ico img")) if a]


def _has_new_badge(card) -> bool:
    return "NEW" in _badges(card)


def _idx(card) -> int | None:
    a = card.css_first("a[data-idx]")
    v = a.attributes.get("data-idx", "") if a else ""
    return int(v) if v.isdigit() else None


def _get(c, root: str, **params) -> HTMLParser:
    r = base.retry(lambda: c.get(root + BOARD, params=params))
    r.raise_for_status()
    time.sleep(DELAY)
    return HTMLParser(r.text)


def _cross_check(badged: set, tab: set, badged_idx: set, all_idx: set) -> None:
    """배지·신메뉴 탭·연번 세 신호가 아직 같은 답을 내는지 확인한다.

    판정 자체는 배지로 한다. 여기서는 어긋난 사실만 드러내고 막지 않는다 —
    하나가 방치됐다고 나머지 둘이 맞는 걸 버리면 그게 더 손해다. 셋이 갈리면
    사람이 보고 고쳐야 하는 자리라 조용히 넘기지 않고 경고를 남긴다.
    """
    if badged != tab:
        print(f"[김가네] NEW 배지와 신메뉴 탭이 어긋난다: "
              f"배지만 {sorted(badged - tab)} / 탭만 {sorted(tab - badged)}")
    if badged_idx and all_idx:
        top = set(sorted(all_idx, reverse=True)[:len(badged_idx)])
        if top != badged_idx:
            print(f"[김가네] NEW 배지가 상위 연번과 어긋난다: "
                  f"배지 {sorted(badged_idx)} / 상위 {sorted(top)}")


def _gimgane() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        # 신메뉴 탭은 두 가지로 쓴다 — ① 교차검증 ② 설명문(일반 카테고리에서는
        # 주석 안이라 못 쓴다. 위 docstring 참고).
        new_cards = _get(c, GIMGANE, board="menu_01",
                         sca=GIMGANE_NEW).css("ul.menu_list li")
        tab_names = {_text(x, "p.menu_name") for x in new_cards}
        tab_names.discard("")
        descs = {_text(x, "p.menu_name"): _text(x, "p.menu_info")
                 for x in new_cards}

        rows = []     # (분류명, 카드)
        for category, sca in GIMGANE_CATEGORIES:
            for card in _get(c, GIMGANE, board="menu_01",
                             sca=sca).css("ul.menu_list li"):
                rows.append((category, card))

    # 신메뉴 탭에만 있고 일반 카테고리엔 없는 상품도 담는다. 지금은 6건 전부
    # 양쪽에 있지만 그게 보장된 구조는 아니다.
    seen = {_text(card, "p.menu_name") for _, card in rows}
    rows += [("신메뉴", card) for card in new_cards
             if _text(card, "p.menu_name") not in seen]

    badged, badged_idx, all_idx = set(), set(), set()
    for _, card in rows:
        i = _idx(card)
        if i is not None:
            all_idx.add(i)
        if _has_new_badge(card):
            badged.add(_text(card, "p.menu_name"))
            if i is not None:
                badged_idx.add(i)
    _cross_check(badged, tab_names, badged_idx, all_idx)

    for category, card in rows:
        name = _text(card, "p.menu_name")
        if not name:
            continue
        it = Item(
            brand="김가네",
            name=name,
            desc=descs.get(name, ""),
            image=_bg_image(card, ".img"),
            labels=_badges(card),
            category=category,
            # 상품별 배지만 True. 배지 없음은 '아니다'가 아니라 '모른다'다.
            is_new=True if name in badged else None,
            # 상품별 주소가 없다. SITES 폴백에 맡긴다(위 docstring 참고).
            url="",
        )
        if it.key in keys:
            continue
        keys.add(it.key)
        items.append(it)
    return items


def _tomato() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        # 분류명을 붙이기 위한 idx → 분류 지도. 상품 자체는 전체 목록에서 받는다.
        names = {}
        for category, sca in TOMATO_CATEGORIES:
            for card in _get(c, TOMATO, board="menu_01",
                             sca=sca).css("ul.menu_list li"):
                i = _idx(card)
                if i is not None:
                    names.setdefault(i, category)

        cards = _get(c, TOMATO, board="menu_01",
                     sca="all").css("ul.menu_list li")

    for card in cards:
        name = _text(card, "p.menu_tit")
        if not name:
            continue
        link = card.css_first("a[href]")
        href = link.attributes.get("href", "") if link else ""
        i = _idx(card)
        it = Item(
            brand="토마토도시락",
            name=name,
            image=_bg_image(card, ".menu_img"),
            category=names.get(i, ""),
            # 카테고리를 가리지 않고 따라다니는 상품별 배지다(위 실측 참고).
            is_new=True if card.css_first(".labels span.new") else None,
            url=TOMATO + href if href.startswith("/") else href,
        )
        if it.key in keys:
            continue
        keys.add(it.key)
        items.append(it)
    return items


def fetch() -> list[Item]:
    return _gimgane() + _tomato()
