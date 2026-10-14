"""엘리팝(ALLEY PUB) — 요리맥주 전문점. (프랜차이즈, 안주)

등록 담당자에게: `(FRANCHISE, "안주")` ·
SITES `http://www.alleypub.co.kr/new/board/index.php?board=menu_01&sca=new`   (⚠️ `/new/` 하위가 본체)

운영 SY프랜차이즈. 공정위 `주점` 가맹점 5+ 중 **가맹점 32개**(프차몰 실측). 10-08 주점 조사 1~26위 구간에
있었는데 그 표에서 빠져 있던 곳이다(`notes/CANDIDATES-PUB2.md`). 도메인은 운영사 아임웹(`syfranchise.imweb.me`)
의 패밀리 링크로 찾았다. 2026-10-14 실측.

## 경로 — 메뉴 게시판 `menu_01` 의 칸 10개 중 9개

```
GET http://www.alleypub.co.kr/new/board/index.php?board=menu_01&sca=<칸>
    new 트렌디한 신메뉴 7 · 22 HOT&SPICY 9 · 5 SPECIAL 5 · 13 PLATTERS 3 · 15 PIZZA&PASTA 7 ·
    21 DRY SNACKS 3 · 14 DESSERTS 6 · 7 FRESH SALADS 3 · 2 CHICKEN&CHIPS 9 · (10 주류 43 — 안 받는다)
```
칸 이름·코드는 홈 내비(`a[href*="board=menu_01&sca="]`)가 준다. 칸마다 3~9건, 페이지 링크 0개(페이징 없음).
카드 = `ul.grid_list > li[data-idx]` → `p.board_txt`(상품명) · `.grid_img` 의 `background-image` · `span.menu_new_ico`.

## 신호 ① — `span.menu_new_ico` **요소 배지**

`트렌디한 신메뉴` 칸 7/7(100%), 음식 칸 전체 합쳐 이름 기준 **NEW 9 / 음식 44**(20%).
⚠️ 신메뉴 칸은 같은 상품을 **다른 `data-idx`** 로 한 벌 더 깐다(`꿀호떡` #421 신메뉴칸 / #412 디저트칸).
이름(공백 제거)으로 합친다 — `치즈오븐 스파게티` / `치즈오븐스파게티` 도 같은 상품이다.
배지는 둘 중 하나라도 있으면 True(디저트 칸의 `꿀호떡` 엔 배지가 없다).
⚠️ 배지가 **묵는다** — `엘리 플래터`(#181)·`파인메론`(#405)은 2024-11 사진에 NEW 가 아직 달려 있다. 날짜가 판정한다.

## 신호 ② — 이미지 경로의 **업로드 시각**

```
/new/upload/menu_01/2025_05_08/admin_1BhIs_2025_05_08_11_04_02.jpg
                    └─ YYYY_MM_DD ┘
```
음식 44건 전건에서 읽힌다. 분포: 2025-05-08 신메뉴 7종 · 2024-11-06/07 · 2024-07-15 · **2023-10-20 일괄 28건**
(메뉴판 전체 재업로드) · 2016~2018 주류.
🔴 **사진 교체가 있다** — `data-idx` 는 전역 일련번호인데 `엘리 플래터` #181 이 2024-11-07 사진을 달고 있다
(#199 이후가 2018~2023). 숲속호두와 같은 **번호 보정**을 한다: "나보다 번호 큰 카드의 가장 이른 업로드일" 로 깎는다
(항상 옛날 방향). #181 → 2023-10-20(주류 칸을 안 받으므로 음식 카드끼리만 비교). NEW 상품을 60일 창 밖으로 미는 보정이 생기면 깎지 않고 터뜨린다(번호 재활용 대비).
그래도 사진 날짜라 `uploaded_at` 에만 넣는다. 2023-10-20 28건은 `rules.untrust_bulk_dates()` 임계(20) 안에 든다.

## 🍺 주류는 안 받는다

`sca=10 주류` 칸(맥주·하이볼·소주 43건, `한맥 600ml` 에 NEW 배지)을 통째로 안 읽는다. 남은 음식 44건을
`base.is_alcohol(name, category, brand)` 로 재면 **0건**이다(이름·분류로만 판정). 그래도 걸리면 그 건만 버린다.

## 오늘(2026-10-14) 화면 — 0건이 정상

가장 최근 업로드가 **2025-05-08(17개월 전)** 이다. 이 브랜드는 메뉴를 해마다 한두 번 묶어서 갈아 끼운다
(2023-10 · 2024-07 · 2024-11 · 2025-05). 다음 개편 때 그날 올라온 NEW 카드가 잡힌다.
⚠️ 17개월째 멈춰 있다는 건 사이트를 버렸을 가능성도 뜻한다 — 1년 더 0건이면 빼도 된다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "엘리팝"
SITE = "http://www.alleypub.co.kr"
HOME = SITE + "/new/"
LIST = SITE + "/new/board/index.php?board=menu_01&sca={}"
ALCOHOL_SCA = {"10"}          # 주류 칸
DELAY = 1.2
WINDOW = 60

MIN_CATS = 6            # 실측 음식 칸 9개(신메뉴 칸 포함)
MIN_ITEMS = 30          # 실측 음식 44건(이름 합친 뒤)
MAX_ITEMS = 200
NEW_MAX_RATIO = 0.5     # 실측 9/44
DATED_MIN_RATIO = 0.9   # 실측 44/44
FRESH_MAX_RATIO = 0.3   # 실측 0/44

_SCA = re.compile(r"board=menu_01&(?:amp;)?sca=(\w+)")
_UP = re.compile(r"/upload/menu_01/(\d{4})_(\d{2})_(\d{2})/")


def _norm(name: str) -> str:
    return re.sub(r"\s+", "", name)


def fetch() -> list[Item]:
    with base.client() as c:
        h = base.retry(lambda: c.get(HOME))
        h.raise_for_status()
        cats = {}
        for a in HTMLParser(h.text).css("a"):
            m = _SCA.search(a.attributes.get("href") or "")
            label = " ".join(a.text().split())
            if m and label and m.group(1) not in ALCOHOL_SCA:
                cats.setdefault(m.group(1), label)
        if len(cats) < MIN_CATS:
            raise RuntimeError(f"{BRAND}: 메뉴 칸 {cats} — 실측 음식 9칸이었다. 홈 내비가 바뀌었는지 보라")

        cards = []          # (idx, 이름, 날짜, NEW, 칸이름, sca)
        for sca, label in cats.items():
            time.sleep(DELAY)
            r = base.retry(lambda sca=sca: c.get(LIST.format(sca)))
            r.raise_for_status()
            lis = HTMLParser(r.text).css("ul.grid_list > li[data-idx]")
            if not lis:
                raise RuntimeError(f"{BRAND}: '{label}' 칸(sca={sca})이 0건 — 'ul.grid_list > li' 가 깨졌다")
            for li in lis:
                nm = li.css_first("p.board_txt")
                name = " ".join(nm.text().split()) if nm else ""
                if not name:
                    continue
                img = li.css_first(".grid_img")
                st = (img.attributes.get("style") or "") if img else ""
                dm = _UP.search(st)
                src = re.search(r"url\('([^']+)'\)", st)
                cards.append(dict(
                    idx=int(li.attributes.get("data-idx") or 0), name=name,
                    raw="-".join(dm.groups()) if dm else "",
                    new=li.css_first("span.menu_new_ico") is not None,
                    cat=label, sca=sca,
                    image=(SITE + src.group(1)) if src and src.group(1).startswith("/") else (src.group(1) if src else "")))

    # 번호 보정 — 숲속호두와 같다(모듈 주석 §신호 ②).
    cutoff = (date.today() - timedelta(days=WINDOW)).isoformat()
    floor = ""
    for cd in sorted(cards, key=lambda x: x["idx"], reverse=True):
        d = cd["raw"]
        if d and floor and floor < d:
            if cd["new"] and d >= cutoff > floor:
                raise RuntimeError(
                    f"{BRAND}: NEW 카드 #{cd['idx']} {cd['name']!r} 사진은 {d} 인데 더 큰 번호가 {floor} 에 "
                    f"올라왔다. 번호 재활용인지 사진 교체인지 눈으로 보라")
            d = floor
        cd["date"] = d
        if cd["raw"] and (not floor or cd["raw"] < floor):
            floor = cd["raw"]

    merged: dict = {}
    for cd in cards:
        k = _norm(cd["name"])
        cur = merged.get(k)
        if cur is None:
            merged[k] = dict(cd)
            continue
        cur["new"] = cur["new"] or cd["new"]
        if cur["sca"] == "new" and cd["sca"] != "new":      # 분류는 신메뉴 칸이 아닌 쪽
            cur["cat"], cur["sca"] = cd["cat"], cd["sca"]
        if cd["date"] and (not cur["date"] or cd["date"] < cur["date"]):   # 이른 쪽(안전)
            cur["date"] = cd["date"]

    items: list[Item] = []
    dropped_alcohol = []
    for cd in sorted(merged.values(), key=lambda x: x["idx"], reverse=True):
        if base.is_alcohol(cd["name"], cd["cat"], BRAND):
            dropped_alcohol.append(cd["name"])
            continue
        items.append(Item(
            brand=BRAND, name=cd["name"], image=cd["image"], category=cd["cat"],
            uploaded_at=cd["date"],
            # 배지가 묵는다 — 날짜를 못 읽으면 배지를 주지 않는다(함정 ④).
            is_new=True if (cd["new"] and cd["date"]) else None,
            url=LIST.format(cd["sca"])))

    if not MIN_ITEMS <= len(items) <= MAX_ITEMS:
        raise RuntimeError(f"{BRAND}: 음식 {len(items)}건 — 실측 44건이었다. 칸별 구조를 보라")
    new = sum(1 for i in items if i.is_new)
    dated = sum(1 for i in items if i.uploaded_at)
    if dated < len(items) * DATED_MIN_RATIO:
        raise RuntimeError(f"{BRAND}: {len(items)}건 중 날짜 {dated}건 — 이미지 경로가 "
                           f"'/upload/menu_01/YYYY_MM_DD/' 꼴이 아니게 됐다. 실측 44/44")
    if not new:
        raise RuntimeError(f"{BRAND}: NEW 배지 0건 — 실측 9건. 'span.menu_new_ico' 가 바뀌었는지 보라")
    if new > len(items) * NEW_MAX_RATIO:
        raise RuntimeError(f"{BRAND}: NEW {new}/{len(items)} — 실측 9/44. 배지 요소가 전체에 붙었는지 보라")
    fresh = sum(1 for i in items if i.uploaded_at and i.uploaded_at >= cutoff)
    if fresh > len(items) * FRESH_MAX_RATIO:
        raise RuntimeError(f"{BRAND}: {fresh}/{len(items)} 건이 최근 {WINDOW}일 업로드 — 메뉴판을 통째로 "
                           f"다시 올렸는지 보라(2023-10-20 28건 선례)")
    return items
