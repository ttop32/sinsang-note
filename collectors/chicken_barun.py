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

`first_reg_date` 가 `2026.09.22` 꼴이고 12개 날짜로 갈린다. Item docstring 이
released_at 을 "가장 강한 신호" 라고 부르는 그 자리에 그대로 들어간다 — 점 세 개를
하이픈으로 바꾸는 게 전부다.

🔴 **다만 "일괄 덩어리가 아니다" 는 틀렸다.** 2026-10-02 전수 분포다.

    2024.05.23 ×13 ┐  사이트 구축 일괄. 둘이 이어진 하루고 합쳐서 **53건 중 26건(49%)**
    2024.05.24 ×13 ┘
    2026.06.19 ×10    두 번째 덩어리
    2025.07.09 ×4 · 2026.08.18 ×3 · 2025.09.24 ×2 · 2026.05.04 ×2 · 2026.08.07 ×2
    2024.11.21 ×1 · 2025.04.30 ×1 · 2026.07.21 ×1 · 2026.09.22 ×1

   절반이 이틀에 몰려 있다. 그 덩어리 안에서는 신구를 못 가린다 — 후라이드·양념 같은
   상시 메뉴가 전부 거기 있다.
   🔴 그리고 **`rules.untrust_bulk_dates()` 는 이걸 못 지운다.** 그 함수는
      `uploaded_at` 만 본다(2026-10-02 코드 확인). released_at 쪽에는 일괄 방어가
      아예 없다. 지금은 2024-05 라 60일 창 밖이라 조용하지만, 브랜드가 사이트를
      다시 지으면 **53건이 같은 날짜로 한꺼번에 신상이 된다.**
      그래도 여기서 날짜를 지우지는 않는다 — 덩어리 판정은 브랜드 전체를 봐야 하는
      일이고 규칙을 두 벌로 두면 안 된다(rules 모듈 머리말). 대신 적어 둔다.
   덩어리 밖 27건은 상품별로 다르고 진짜 정보다. 거기까지가 이 필드의 값어치다.

**요청 2번으로 끝난다**(분류 이름용 탭 HTML + 목록 AJAX). 이미지 HEAD 도 필요 없다.

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

⚠️ **TOTAL 은 53 인데 수집 결과는 52 건이다.** 파서가 샌 게 아니라 `base.make_key()`
   가 `내맘대로 반반` 과 `내맘대로 반반 (핫)` 을 같은 키로 접기 때문이다 — `_SIZE`
   정규식이 `핫` 을 **온도 표기**로 보고 털어낸다(카페의 `(HOT)`/`(ICED)` 를 위한
   규칙이다). 치킨에서 `(핫)` 은 온도가 아니라 **맵기 변형**이라 다른 상품인데,
   앞엣것만 남고 뒤엣것이 조용히 사라진다. 땅땅치킨의 `로'st치킨(HOT)+슈트트링 감자`
   도 같은 이유로 사라진다.
   어댑터에서 고칠 수 있는 게 아니다(키 규칙은 base 소관이고, 여기서 우회하면
   first_seen 이력이 끊긴다). base.py 쪽 과제로 넘긴다 — 2026-10-02 리뷰 보고.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "바른치킨"
SITE = "https://barunchicken.com"
API = SITE + "/itboard/front/product/product_list.ajax.php"
MENU = SITE + "/menu/index.php"

MAX_ITEMS = 300   # 폭주 방지. 현재 53건.
LIMIT = 200       # 한 번에 받을 개수. TOTAL 과 대조해 부분수집을 잡는다.
# 요청이 2번(탭 HTML + AJAX)뿐이라 체감은 없지만, 다른 어댑터와 같은 자리에
# 같은 이름으로 둔다. 상한·지연을 어댑터마다 다른 이름으로 두면 반드시 하나는
# 빠진다(notes/CRAWLING-POLICY.md §2-G).
DELAY = 0.3       # 요청 간격(초)

# `2026.09.22` 만 받는다. 이 필드는 released_at 으로 들어가는 **가장 강한 신호**라
# 형식이 바뀌면 조용히 틀린 날짜를 쓰느니 비우는 게 낫다(또래오래 `_DATE` 선례).
# `.replace(".", "-")` 만 걸어두면 `2026.09.22 14:33` 이나 epoch 가 그대로 들어간다.
_DATE = re.compile(r"^(\d{4})\.(\d{2})\.(\d{2})$")


def _released(raw: str) -> str:
    m = _DATE.match((raw or "").strip())
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


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

        time.sleep(DELAY)
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
                released_at=_released(p.get("first_reg_date")),
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
