"""바른치킨.

공정위 등록 가맹점 185개로 치킨 업종 26위. 규모는 작은데 **데이터 품질은 치킨 중 최상**이다.

────────────────────────────────────────────────────────────────────────
치킨 브랜드 중 유일하게 API 가 상품별 등록일을 그대로 내준다
────────────────────────────────────────────────────────────────────────
barunchicken.com 의 메뉴 목록 `/menu/index.php` 는 JS 렌더라 HTML 에 상품이 없다.
그런데 그 JS 가 때리는 AJAX 가 이름·이미지·분류·설명에 **등록일까지** 한 번에 준다.

    POST /itboard/front/product/product_list.ajax.php
    page=1&limit=200&sh=&shca=          ← shca 를 비우면 전 분류
    → {"TOTAL":53, "LIST":[{board_id, views, title, image_url,
                            category, content, first_reg_date}, …]}

`first_reg_date` 가 `2026.09.22` 꼴이고 2026-10-02 실측으로 **12개 날짜로 흩어진다**
(2024.05.23 / 2024.05.24 / 2024.11.21 / 2025.04.30 / 2025.07.09 / 2025.09.24 /
2026.05.04 / 2026.06.19 / 2026.07.21 / 2026.08.07 / 2026.08.18 / 2026.09.22).
일괄 덩어리가 아니라 상품별로 다르다. Item docstring 이 released_at 을 "가장 강한
신호" 라고 부르는 그 자리에 그대로 들어간다 — 점 세 개를 하이픈으로 바꾸는 게 전부다.

**요청 1번으로 끝난다.** 이미지 HEAD 도 필요 없다.

NEW 배지도 신메뉴 탭도 없다. 그래서 `is_new` 는 **전건 None** 이다. 날짜가 있으니
신제품 판정은 collect.py 의 날짜 창(WINDOW=60)이 한다 — 배지가 없다고 신호가 없는 게
아니라, 여기선 날짜가 배지보다 강하다.

분류는 코드(`M001`…)로만 오기 때문에 `/menu/index.php` 의 탭 마크업에서
`attr-seq` → `attr-tit` 를 읽어 한글 이름을 붙인다. 하드코딩하면 브랜드가 분류를
늘릴 때 코드가 그대로 화면에 뜬다. 2026-10-02 기준 M001 시그니쳐 메뉴 / M002 치킨 메뉴 /
M003 세트 메뉴 / M004 대새 메뉴 / M005 치킨케이크 메뉴 / M006 토핑 / M008 소스&시즈닝 /
M009 사이드메뉴 / M012 사이드메뉴(홀전용). 탭을 못 읽으면 코드를 그대로 쓴다 —
분류 이름 때문에 수집 전체를 죽일 일은 아니다.

🔴 **robots.txt 가 우리 경로를 막는 유일한 치킨 브랜드다.**

    User-agent: *
    Allow:/
    Disallow: /itboard/      ← 우리가 쓰는 AJAX 가 여기 있다
    Disallow: /common/ /font/ /js/ /plugin/ /rssBackup/

치킨 상위 30곳을 전수로 훑으면서 우리 UA 가 실제로 걸린 건 여기 하나다. 운영자 판단으로
수집하되, **삭제 요청이 오면 다투지 말고 즉시 내린다**(base.BRANDS 의 이마트24·도미노피자·
폴바셋 주석과 같은 처분). 우회로를 찾아봤지만 쓸 수 없었다 — 사람이 보는
`/menu/view.php?board_id=139&shca=M006` 은 Disallow 대상이 아니지만 **등록일을 안 찍는다**
(2026-10-02 실측, 날짜 문자열 0건). robots 를 지키려면 날짜를 통째로 잃는다.

세트(M003 4건)는 그대로 싣고 promo 는 전건 False 다. 할인·행사 표시가 없고, 세트 변형을
접는 건 rules.drop_sets() 담당이다.
조회수(`views`)는 Item 에 자리가 없어 버린다.
"""
import re

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "바른치킨"
SITE = "https://barunchicken.com"
API = SITE + "/itboard/front/product/product_list.ajax.php"
MENU = SITE + "/menu/index.php"

MAX_ITEMS = 300   # 폭주 방지. 현재 53건.
LIMIT = 200       # 한 번에 받을 개수. TOTAL 과 대조해 부분수집을 잡는다.


def _categories(client) -> dict:
    """메뉴 탭에서 `M001` → `시그니쳐 메뉴` 를 읽는다. 실패하면 빈 사전."""
    try:
        r = base.retry(lambda: client.get(MENU))
        r.raise_for_status()
    except Exception:
        return {}
    out = {}
    for a in HTMLParser(r.text).css("a.menuItem"):
        seq = a.attributes.get("attr-seq") or ""
        tit = " ".join((a.attributes.get("attr-tit") or "").split())
        if seq and tit:
            out[seq] = tit
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        cats = _categories(c)

        r = base.retry(lambda: c.post(
            API, data={"page": 1, "limit": LIMIT, "sh": "", "shca": ""}))
        r.raise_for_status()
        body = r.json()
        rows = body.get("LIST") or []
        if not rows:
            raise RuntimeError("상품 목록이 비었다 — AJAX 응답 형식이 바뀌었을 가능성")

        # 서버가 총건수를 알려준다. 공짜로 얻는 부분수집 가드라 쓴다 —
        # 페이지네이션이 생기는 날 조용히 앞부분만 가져오는 걸 여기서 잡는다.
        total = int(body.get("TOTAL") or 0)
        if total and len(rows) < total:
            raise RuntimeError(f"부분수집 의심 {len(rows)}/{total}건 — "
                               "페이지네이션이 생겼을 가능성")

        for p in rows[:MAX_ITEMS]:
            name = " ".join((p.get("title") or "").split())
            if not name:
                continue
            code = p.get("category") or ""
            img = p.get("image_url") or ""

            it = Item(
                brand=BRAND,
                name=name,
                desc=" ".join((p.get("content") or "").split()),
                image=SITE + img if img.startswith("/") else img,
                category=cats.get(code, code),
                # 브랜드가 적어준 등록일이다. 업로드 시각이 아니라서 released_at 이다.
                released_at=(p.get("first_reg_date") or "").replace(".", "-"),
                # NEW 배지도 신메뉴 탭도 없다. 모르는 건 모른다고 둔다 —
                # 날짜가 있으니 신제품 판정은 collect.py 의 날짜 창이 한다.
                is_new=None,
                # 할인·행사 표시가 없다. 세트는 promo 가 아니다.
                promo=False,
                url=(f"{SITE}/menu/view.php?board_id={p['board_id']}&shca={code}"
                     if p.get("board_id") else ""),
            )
            if it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)

        # 날짜가 이 어댑터의 존재 이유다. 전건 비면 응답 스키마가 바뀐 것이고,
        # 건수는 53 그대로라 collect.py 의 0건·급감 가드에 안 걸린다.
        if not any(i.released_at for i in items):
            raise RuntimeError("등록일이 전건 비었다 — first_reg_date 가 사라졌을 가능성")
    return items
