"""숲속호두(숲속호두과자) — 페스츄리 호두과자 카페. **(CAFE, "베이커리")**

등록 담당자에게: `(CAFE, "베이커리")` ·
SITES `https://soopssokhodu.com/?module=Goods&action=SiteGoods&sMode=SELECT_FORM&sCurrSortCd=001`

공정위 `제과제빵` 101곳 중 **23위(가맹점 23개)**. 운영사 (주)달숲(고양시).
프차몰 표기는 `숲속호두과자` 인데 사이트·보도자료가 스스로 `숲속호두` 라 부른다 — 그 이름을 쓴다.
3차 조사(`notes/CANDIDATES-BAKERY3.md` §4-1)가 "1순위, 상품명·이미지 짝짓기만 남았다"고
남긴 자리다. 2026-10-14 실측.

## 경로 — 메뉴 다섯 칸. 그게 전부다

```
GET /?module=Goods&action=SiteGoods&sMode=SELECT_FORM&sCurrSortCd=001   호두과자  8건
                                                        ...=002   호두팝    5건
                                                        ...=003   커피      3건
                                                        ...=004   음료      8건
                                                        ...=005   패키지    7건
                                                                  ──────────────
                                                                  합계     31건
```
🔴 **`sMode=SELECT_FORM` 을 빼면 200 인데 내용이 비어 있다**(12,405B, `<!--Start 내용-->`
   과 `<!--End 내용-->` 사이가 공백). 3차 조사 노트의 주소엔 이게 빠져 있었다. 함정 ⑦ 그대로라
   가드를 건수에 건다.

카드는 `#prod_item_wrap li` → `p.tit`(한글명) · `p.txt`(영문명) · `.img img`(썸네일) ·
`a[onclick="Goodswview('<칸>','<상품번호>')"]`. 상세는 팝업 JS 라 따로 받지 않는다.
페이징 없음 — 칸마다 3~8건이고 페이지 링크·파라미터가 마크업에 0개다.

## 신제품 신호 ① — `신메뉴 / 베스트메뉴` 캐러셀의 **아이콘 이미지**

각 칸 위에 `p.menu_tit` = `신메뉴 / 베스트메뉴` 캐러셀이 있고 카드마다 `.ico img` 가 붙는다.
**배지가 글자가 아니라 이미지다** — 파일을 받아 눈으로 봤다:
```
/image/sub/ico1.png   초록 원에 "NEW"
/image/sub/ico2.png   노란 원에 왕관 + "BEST"
```
캐러셀에 없는 상품은 브랜드가 아무 말도 안 한 것이므로 `None` 이다(함정 ③).

배지 비율 — 아이콘 기준 **NEW 6 · BEST 15**(목록 안 13 + 캐러셀에만 있는 2) / 33. 최종 27건 중 NEW 6건(22%). 날짜와 맞대면 NEW 가 **19개월 묵은 것도 있다**:
```
레몬 페스츄리 호두과자            NEW  2026-07-07
말차호두과자 9입 베스트 팩          NEW  2026-02-05   (뉴스 '말차 호두…' 2026-02-19 보도와 맞는다)
딸기크림라떼·딸기에이드·딸기 제주 말차라떼·말차라떼   NEW  2025-03-19   ← 봄 딸기 시즌. 19개월째 NEW
```
그래서 `is_new=True` 로 두되 **날짜가 최종 판정**을 한다(`rules.is_fresh()` 는 날짜가 있으면
배지보다 날짜를 따른다). 날짜를 못 읽은 NEW 는 `is_new` 를 주지 않는다 — 날짜 없는 NEW 는
60일 창을 건너뛰기 때문이다(함정 ④, 딸기 4종이 그 길로 올라간다).

## 신제품 신호 ② — 썸네일 파일명 = PHP `uniqid()`. 업로드 시각이 박혀 있다

```
upload_dir/goods/6271744426a4c4a7c05829.jpg
                 └ 난수 ┘└─ uniqid 13자 ─┘   앞 8자 0x6a4c4a7c = 1783384700 = 2026-07-07 09:38 KST
```
33/33 전건에서 읽힌다(검수에서 31장의 `Last-Modified` 와 대조 — 30장 0초, 1장 −1초). 분포는
**2022-06-07 ~ 2026-07-07, 날짜 10종**으로 흩어지고
시각이 전부 업무시간(09~18시)이다 — 배포 시각이 아니라 사람이 하나씩 올린 것이다.

🔴 **그런데 사진 교체가 있다 — 상품번호가 그걸 드러낸다.** `Goodswview` 의 상품번호는
칸을 가로지르는 **전역 일련번호**다(001 칸에 84·52, 005 칸에 83, 004 칸에 75~78). 번호가
큰 상품이 먼저 등록됐을 리 없으니 업로드 날짜도 번호 순서를 따라야 하는데, 어긋난 게 있다:
```
#20 호두과자 간편세트          2025-09-18   ← #31 초코라떼(2022-10-11)보다 번호가 작다
#21 호두과자 점보 패키지 24입    2025-09-18
#70 호두과자 4입 베스트팩       2025-09-18   ← #72 호두라떼(2024-12-27)보다 번호가 작다
#71 호두과자 24입 베스트 팩     2025-09-18
```
(같은 식으로 #58·#59 8입·15입 팩도 2025-09-18 → 2024-10-08 로 깎인다. 보정 대상 **6건**.)
패키지 칸 사진을 2025-09-18 에 한꺼번에 갈아 끼운 것이다(7장 중 6장이 그날 14:33~14:34).
그래서 **"나보다 번호가 큰 상품 중 가장 이른 업로드일"로 내 날짜를 깎는다** —
내 등록일 ≤ 나중 번호의 등록일 ≤ 그 사진의 업로드일이라 이 값은 **등록일의 상한**이다.
깎는 방향이 항상 '더 옛날'이라 옛 상품이 신상으로 둔갑하는 쪽으로는 절대 안 움직인다.
위 6건은 2022-10-11·2024-10-08·2024-12-27 로 내려간다. 남는 구멍: **가장 큰 번호의 사진을
교체하면 깎을 기준이 없다** — 그건 `FRESH_MAX_RATIO` 가 일괄 교체만 잡는다.

🔴 **번호 재활용** — 반대 방향 위험도 있다. 브랜드가 옛 상품 레코드의 이름·사진을 바꿔 새 메뉴로
쓰면 보정이 진짜 신상을 창 밖으로 밀어낸다(번호 공백이 53개라 숨김·재활용이 있는 CMS 다).
그래서 **NEW 아이콘을 단 상품을 60일 창 안→밖으로 미는 보정이 생기면 깎지 않고 터뜨린다.**
NEW 가 없는 상품의 재업로드는 조용히 깎는다(그게 이 보정의 목적이다).

그래도 '사진을 올린 날'이지 출시일이 아니므로 `uploaded_at` 에만 넣는다(함정 ⑤).

## 오늘(2026-10-14) 화면

수집 **27건**(목록 31 + 캐러셀에만 있는 2 − 입수 포장 6). 가장 최근 업로드가 2026-07-07(99일 전)이라
**0건이 정상**이다. 다음 신메뉴 사진이 올라오면 바로 잡힌다.

## 분류

호두과자·커피·음료를 파는 매장형 디저트 카페다 → 유형 `CAFE`. 세부분류는 호두과자를
`베이커리` 로 둔다(제과제빵 업종, 송사부고로케·삼송빵집과 같은 칸). `패키지` 칸은
호두과자 입수별 포장이다. `호두과자 N입 베스트 팩`·`간편세트`·`점보 패키지` 처럼 **맛 이름 없이
'호두과자 + 입수·포장 말'뿐인 6건은 뺀다** — `drop_sets()`·`merge_variants()` 가 `N입` 을 떼지 않아
`30입 베스트 팩` 이 새로 생기면 신상으로 뜬다(검수 지적). `말차호두과자 9입 베스트 팩` 은 낱개가
001 칸에 없는 **유일한 말차 호두과자**라 남긴다.

캐러셀에만 있고 목록에 없는 상품(#39 레몬에이드·#40 제주 청귤에이드)도 받는다 — NEW 가 그렇게
올라오면 흔적 없이 빠지기 때문이다. 페이지 탭(`sCurrSortCd`)이 `CATEGORIES` 와 다르면 터뜨린다.
"""
import re
import time
from datetime import date, datetime, timedelta, timezone

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "숲속호두"
SITE = "https://soopssokhodu.com/"
LIST = SITE + "?module=Goods&action=SiteGoods&sMode=SELECT_FORM&sCurrSortCd="
DELAY = 1.5

# (칸 코드, 칸 이름, 2026-10-14 실측 건수). 칸별 바닥을 둬야 한 칸만 비는 걸 잡는다.
CATEGORIES = [
    ("001", "호두과자", 8),
    ("002", "호두팝", 5),
    ("003", "커피", 3),
    ("004", "음료", 8),
    ("005", "패키지", 7),
]
CAT_MIN_RATIO = 0.8
MIN_ITEMS = 22          # 실측 27(목록 31 + 캐러셀 전용 2 − 입수 포장 6)
MAX_ITEMS = 120
NEW_MAX_RATIO = 0.5     # 실측 6/33 = 18%(아이콘 기준, 포장 제외 전)
DATED_MIN_RATIO = 0.9   # 실측 33/33
# 실측 0/27. 사진을 칸째로 갈아 끼우면(2025-09-18 패키지 6장 선례) 번호 보정이 못 잡는
# 최신 번호 묶음이 한꺼번에 최근 날짜를 갖는다. 그걸 터뜨린다.
FRESH_MAX_RATIO = 0.3
WINDOW = 60             # rules.WINDOW 와 같은 값. 가드 전용

ICONS = {"ico1.png": True,    # NEW — 이미지를 받아 눈으로 확인(모듈 주석)
         "ico2.png": None}    # BEST — 신제품이라는 말이 아니다
_GID = re.compile(r"Goodswview\('(\d+)'\s*,\s*'(\d+)'\)")
_KST = timezone(timedelta(hours=9))
_TAB = re.compile(r"sMode=SELECT_FORM&(?:amp;)?sCurrSortCd=(\d{3})")
# '호두과자' + 입수·포장 말만 있는 이름. 맛 이름이 붙으면 안 걸린다.
_PACK_ONLY = re.compile(r"^호두과자(?:\s*(?:\d+\s*입|베스트|팩|패키지|점보|간편|세트))+\s*$")


def _uniqid_date(src: str) -> str:
    """`upload_dir/goods/<난수><uniqid 13자>.jpg` → 'YYYY-MM-DD'(KST). 못 읽으면 ''."""
    stem = (src or "").rsplit("/", 1)[-1].split(".")[0]
    if len(stem) < 14 or not re.fullmatch(r"[0-9a-f]+", stem[-13:]):
        return ""
    ts = int(stem[-13:][:8], 16)
    d = datetime.fromtimestamp(ts, _KST).date()
    # 사이트 오픈(2022) 이전이나 미래면 uniqid 가 아니다 — 파일명 규칙이 바뀐 것이다.
    if not date(2020, 1, 1) <= d <= date.today() + timedelta(days=1):
        return ""
    return d.isoformat()


def _gid(node) -> int | None:
    a = node.css_first("a")
    m = _GID.search((a.attributes.get("onclick") or "") if a else "")
    return int(m.group(2)) if m else None


def _card(node, label: str, code: str, is_new) -> dict | None:
    """캐러셀 `.item` 이든 목록 `li` 든 같은 모양이다 → dict."""
    gid = _gid(node)
    tit = node.css_first("p.tit")
    name = " ".join(tit.text().split()) if tit else ""
    if gid is None or not name:
        return None
    en = node.css_first("p.txt")
    img = node.css_first(".img img")
    src = (img.attributes.get("src") or "") if img else ""
    if src and not src.startswith("http"):
        src = SITE + src.lstrip("/")
    return dict(gid=gid, name=name, name_en=" ".join(en.text().split()) if en else "",
                image=src, raw_date=_uniqid_date(src), category=label, code=code,
                is_new=is_new)


def fetch() -> list[Item]:
    rows: dict = {}          # 상품번호 → dict
    per_cat: dict = {}
    unknown_icons: set = set()
    tabs_seen: set = set()

    with base.client() as c:
        for i, (code, label, expect) in enumerate(CATEGORIES):
            if i:
                time.sleep(DELAY)
            url = LIST + code
            r = base.retry(lambda url=url: c.get(url))
            r.raise_for_status()
            t = HTMLParser(r.text)
            tabs_seen |= set(_TAB.findall(r.text))

            badges = {}
            carousel = []
            for it in t.css(".owl-carousel .item"):
                ico = it.css_first(".ico img")
                fname = ((ico.attributes.get("src") or "") if ico else "").rsplit("/", 1)[-1]
                if fname not in ICONS:
                    unknown_icons.add(fname)
                    continue
                card = _card(it, label, code, ICONS[fname])
                if card:
                    badges[card["gid"]] = ICONS[fname]
                    carousel.append(card)

            n = 0
            for li in t.css("#prod_item_wrap li"):
                card = _card(li, label, code, None)
                if not card:
                    continue
                card["is_new"] = badges.get(card["gid"])
                n += 1
                rows.setdefault(card["gid"], card)
            per_cat[label] = n
            if n < expect * CAT_MIN_RATIO:
                raise RuntimeError(
                    f"{url}: '{label}' 칸 {n}건 — 2026-10-14 실측은 {expect}건이었다. "
                    f"'#prod_item_wrap li' 가 깨졌거나 sMode=SELECT_FORM 이 빠졌다 "
                    f"(빠지면 200 에 빈 본문이 온다). 여기까지: {per_cat}")
            # 캐러셀에만 있고 목록엔 없는 상품(실측: 음료 칸 #39 레몬에이드·#40 제주
            # 청귤에이드, 둘 다 BEST). NEW 가 이렇게 올라오면 흔적 없이 빠지므로 같이 받는다.
            for card in carousel:
                rows.setdefault(card["gid"], card)

    if unknown_icons:
        raise RuntimeError(
            f"{BRAND}: 모르는 캐러셀 아이콘 {sorted(unknown_icons)} — 2026-10-14 실측은 "
            f"ico1.png(NEW)·ico2.png(BEST) 둘뿐이었다. 이미지를 받아 보고 ICONS 에 넣어라")
    known = {code for code, _, _ in CATEGORIES}
    if tabs_seen != known:
        raise RuntimeError(
            f"{BRAND}: 메뉴 칸이 바뀌었다 — 페이지 탭 {sorted(tabs_seen)} / 어댑터 "
            f"{sorted(known)}. 새 칸의 신상이 조용히 빠지지 않게 CATEGORIES 를 고쳐라")

    # 날짜 가드를 먼저 — 날짜를 못 읽으면 아래에서 is_new 도 지워져 'NEW 0건' 으로 오진한다.
    dated = sum(1 for r in rows.values() if r["raw_date"])
    if dated < len(rows) * DATED_MIN_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(rows)}건 중 날짜를 {dated}건만 읽었다 — 썸네일 파일명이 "
            f"uniqid 꼴이 아니게 됐다. 실측은 33/33 이었다")
    new = sum(1 for r in rows.values() if r["is_new"])
    if not new:
        raise RuntimeError(
            f"{BRAND}: NEW 아이콘이 0건 — 2026-10-14 실측은 6건이었다. 캐러셀 "
            f"'.owl-carousel .item .ico img' 가 바뀌었는지 확인하라")
    if new > len(rows) * NEW_MAX_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(rows)}건 중 NEW 가 {new}건 — 실측은 6/33(18%)이었다. "
            f"아이콘 의미가 바뀌었는지 이미지를 다시 봐라")

    cutoff = (date.today() - timedelta(days=WINDOW)).isoformat()
    # 번호 보정 — 나보다 번호가 큰 상품 중 가장 이른 업로드일로 깎는다(모듈 주석 §신호 ②).
    floor = ""
    for r in sorted(rows.values(), key=lambda r: r["gid"], reverse=True):
        d = r["raw_date"]
        if d and floor and floor < d:
            # 🔴 NEW 아이콘을 단 상품을 창 밖으로 밀어내는 보정은 하지 않고 멈춘다 —
            #    옛 번호를 재활용한 진짜 신메뉴일 수 있다(모듈 주석 §번호 재활용).
            if r["is_new"] and d >= cutoff > floor:
                raise RuntimeError(
                    f"{BRAND}: NEW 상품 #{r['gid']} {r['name']!r} 의 사진은 {d} 인데 더 큰 "
                    f"번호의 상품이 {floor} 에 올라왔다. 옛 번호 재활용인지 사진 교체인지 "
                    f"눈으로 보고 정하라")
            d = floor
        r["date"] = d
        if r["raw_date"] and (not floor or r["raw_date"] < floor):
            floor = r["raw_date"]

    items: list[Item] = []
    seen = set()
    for r in sorted(rows.values(), key=lambda r: r["gid"], reverse=True):
        # 패키지 칸의 '호두과자 N입 …' 은 같은 호두과자의 입수만 다른 포장이다. 새 입수가
        # 생기면 신상으로 뜨므로 뺀다. `말차호두과자 9입` 처럼 맛이 붙은 건 남는다.
        if _PACK_ONLY.match(r["name"]):
            continue
        it = Item(
            brand=BRAND,
            name=r["name"],
            name_en=r["name_en"],
            image=r["image"],
            category=r["category"],
            uploaded_at=r["date"],
            # NEW 아이콘이 있어도 날짜를 못 읽었으면 주지 않는다 — 19개월 묵은 NEW 가 있다.
            is_new=True if (r["is_new"] and r["date"]) else None,
            url=LIST + r["code"],
        )
        if it.key not in seen:
            seen.add(it.key)
            items.append(it)

    if not MIN_ITEMS <= len(items) <= MAX_ITEMS:
        raise RuntimeError(
            f"{BRAND}: 상품 {len(items)}건 — 2026-10-14 실측은 27건이었다"
            f"(기대 {MIN_ITEMS}~{MAX_ITEMS}). 칸별: {per_cat}")
    fresh = sum(1 for i in items if i.uploaded_at and i.uploaded_at >= cutoff)
    if fresh > len(items) * FRESH_MAX_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 {fresh}건이 최근 {WINDOW}일 업로드다 — 실측 0/27. "
            f"사진을 일괄 교체했는지 확인하라(2025-09-18 패키지 6장 선례)")
    return items
