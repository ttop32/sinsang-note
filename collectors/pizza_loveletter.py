"""피자와 치킨의 러브레터. 등록 담당자에게: **(FRANCHISE, "피자")**.

(주)디에스푸드가 2004년부터 하는 피자+치킨 세트 브랜드. 공정위 `피자` 가맹점 44개.
사이트는 손으로 짠 PHP 고 메뉴가 `kind` 3칸에 나뉘어 있다.

```
GET http://loveletterds.com/menu/2200_menu.php?kind=N     ← 본문. 한 쪽에 최대 15건
GET http://loveletterds.com/menu/menu_list.php?kind=N&page=P  ← 16번째부터 붙이는 ajax
```

⚠️ **https 가 없다.** `https://loveletterds.com` 은 붙지 않는다. http 로 간다.
⚠️ 도메인이 `loveletter.co.kr` 류가 아니라 **`loveletterds.com`**(디에스푸드)이다.

## 🔴 ajax 엔드포인트만 긁으면 조용히 모자란다 — 여기서 걸릴 뻔했다

처음에 `menu_list.php?kind=1&page=0` 만 받고 **6건**으로 셌다. 그런데 본문 페이지의
`var p_total` 은 **14** 다. `page=0` 은 15건짜리 쪽수 계산에서 엉뚱한 조각을 주고
`page=1` 부터는 빈 응답이다:

```
menu_list.php?kind=1&page=0  →  6건   ← 이것만 보면 6건이 '전부' 로 보인다
menu_list.php?kind=1&page=1  →  0건
2200_menu.php?kind=1         → 14건   ← 진짜 전부. p_total=14 와 일치
```

**본문 페이지를 기준으로 삼고, `p_total` 이 본문 건수보다 많을 때만 ajax 로
뒷장을 붙인다.** 실측(2026-10-08) `kind=3` 이 `p_total=19` 인데 본문에 15건이라
`page=1` 로 4건을 더 받는다. 200 이 왔다고 다 받은 게 아니다(함정 9).

세 칸 합 **41건**. 칸 이름은 페이지에서 찾는다 — 박아두면 조용히 어긋난다.

```
kind=1 피자          14건
kind=2 치킨           8건
kind=3 세트&사이드     19건
```

## 배지 — `span.new` **5/41 (12.2%)** (2026-10-08 전수 실측)

```
no=120  치즈인 순살치킨 (4조각)   NEW
no=119  치즈인 순살치킨 (10조각)  NEW
no=117  양념치킨 피자            NEW
no=116  감튀마운틴피자           NEW
no=112  요거트 치즐러 치킨        NEW
나머지 36건 배지 없음
```

100% 가 아니고 다른 종류(BEST/HIT)가 섞여 있지도 않다. `span.new` 하나뿐이다.
배지가 붙은 5건은 상품 id `no` 가 큰 쪽에 몰려 있어서(120·119·117·116·112 /
전체 최댓값 120) 순서와 배지가 대체로 맞는다.

안 붙은 36건은 `False` 가 아니라 **`None`** 이다(피자스쿨·뽕뜨락과 같은 선).

## 🔴 날짜가 **없다**

목록에도 `menu_view.php` 상세에도 등록일이 없다. `released_at`·`uploaded_at` 을
비우고 `is_new` 만 준다 — `rules.is_fresh` 가 `first_seen` + `STALE` 로 수명을
끊는다(설빙·빽다방 경로).

⚠️ **공지 게시판은 못 쓴다.** `/community/3301_notice_list.php` 에 `[신메뉴 출시]`
글이 timestamp 까지 달려 10건 있는데 **2024-11-15 에서 멈췄다.** 지금 NEW 가 붙은
5건은 거기 하나도 없다. 날짜를 가져다 붙일 데가 없다는 뜻이다(모스버거는 같은
모양의 게시판이 살아 있어서 쓸 수 있었다 — 여긴 아니다).

⚠️ **이미지 파일명을 날짜로 쓰지 않는다.** 경로가 `260916_040200_master_….png`
꼴이라 `YYMMDD_HHMMSS` 가 그대로 박혀 있고, NEW 5건이 260916·260916·260916·
260430·251210 으로 꽤 그럴듯하다. 그래도 **안 쓴다** — 함정 7(피자마루에서
2020-08-21 등록 상품의 파일명이 2025-03-17 이었다). 사진만 갈아도 올라간다.
여기서도 `버팔로윙`·`버팔로봉`(260430)이 NEW 없이 같은 날짜를 달고 있어서
파일명이 '출시'가 아니라 '업로드'라는 게 드러난다.

## 나머지

  - 이미지는 목록이 `background-image:url(../../upload/menu/…)` 로 준다.
    `../` 를 털고 루트에 붙이면 `http://loveletterds.com/upload/menu/…` 이고
    직접 받아 **image/png 200** 을 확인했다.
  - 설명은 `menu_view.php?kind=&no=` 상세에만 있다. 41번을 더 받아야 해서
    넣지 않았다(가맹점 44개짜리 브랜드다). 이름·이미지·분류·배지로 충분하다.
  - `…세트` 10건은 그대로 내보낸다. 본품이 있는 것은 `rules.drop_sets()` 가 턴다.
  - 상품명 41건을 전부 눈으로 읽었다. 주류·비식품은 없다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "피자와치킨의러브레터"
ROOT = "http://loveletterds.com"          # ⚠️ https 없음
MAIN = ROOT + "/menu/2200_menu.php"
AJAX = ROOT + "/menu/menu_list.php"
DELAY = 1.5
MAX_PAGES = 5            # 폭주 방지. 2026-10-08 실측은 칸당 ajax 1쪽 이하다.

MIN_ITEMS = 32           # 2026-10-08 실측 41건
BADGE_MAX_RATIO = 1 / 3  # 2026-10-08 실측 5/41 = 12.2%

_VIEW = re.compile(r"funView\((\d+),\s*(\d+)\)")
_TOTAL = re.compile(r"p_total\s*=\s*(\d+)")
_BG = re.compile(r"url\(\s*['\"]?(.*?)['\"]?\s*\)")
_UP = re.compile(r"^(?:\.\./)+")


def _kinds(c) -> list:
    """(kind, 칸 이름). 페이지에서 찾는다 — 박아두면 칸이 바뀔 때 어긋난다."""
    r = base.retry(lambda: c.get(MAIN, params={"kind": 1}))
    r.raise_for_status()
    out = []
    for a in HTMLParser(r.text).css("a[href*='kind=']"):
        h = a.attributes.get("href") or ""
        if "&no=" in h:                   # 상품 바로가기. 칸 nav 가 아니다
            continue
        m = re.search(r"kind=(\d+)", h)
        name = " ".join(a.text().split())
        if m and name and m.group(1) not in [k for k, _ in out]:
            out.append((m.group(1), name))
    return out


def _cards(html: str) -> list:
    """funView(kind,no) 를 단 li 만. 네비·푸터의 li 는 걸리지 않는다."""
    return [li for li in HTMLParser(html).css("li")
            if li.css_first("a[onclick*='funView']") is not None]


def _image(li) -> str:
    th = li.css_first(".thumbs")
    m = _BG.search((th.attributes.get("style") or "")) if th is not None else None
    if not m or not m.group(1):
        return ""
    # '../../upload/menu/x.png' → 'http://loveletterds.com/upload/menu/x.png'
    return ROOT + "/" + _UP.sub("", m.group(1).strip())


def fetch() -> list[Item]:
    items: list[Item] = []
    seen: set[str] = set()
    badged = 0

    with base.client() as c:
        kinds = _kinds(c)
        if not kinds:
            raise RuntimeError(
                f"{BRAND}: 메뉴 칸(kind)을 하나도 못 읽었다 — 'a[href*=kind=]' 가 바뀌었다")
        for kind, cat in kinds:
            time.sleep(DELAY)
            r = base.retry(lambda: c.get(MAIN, params={"kind": kind}))
            r.raise_for_status()
            m = _TOTAL.search(r.text)
            if not m:
                raise RuntimeError(
                    f"{BRAND}: kind={kind}({cat}) 에서 p_total 을 못 찾았다. "
                    "이 값이 없으면 몇 건을 덜 받았는지 알 수 없다")
            want = int(m.group(1))
            cards, page = _cards(r.text), 1
            # 🔴 본문이 기준이다. 모자랄 때만 ajax 로 뒷장을 붙인다.
            #    ajax 를 처음부터 쓰면 page=0 이 6건만 주고 조용히 끝난다.
            while len(cards) < want and page <= MAX_PAGES:
                time.sleep(DELAY)
                rr = base.retry(lambda: c.get(AJAX, params={"kind": kind, "page": page}))
                rr.raise_for_status()
                more = _cards(rr.text)
                if not more:
                    break
                cards += more
                page += 1
            if len(cards) < want:
                raise RuntimeError(
                    f"{BRAND}: kind={kind}({cat}) 가 p_total={want} 인데 "
                    f"{len(cards)}건밖에 못 받았다. ajax 쪽수 규칙이 바뀌었다 "
                    "— 모자란 채로 내보내면 급감 가드에도 안 걸린다")

            for li in cards:
                a = li.css_first("a[onclick*='funView']")
                mv = _VIEW.search(a.attributes.get("onclick") or "")
                nm = li.css_first("h4.name")
                name = " ".join(nm.text().split()) if nm is not None else ""
                if not name:
                    continue
                is_new = li.css_first("span.new") is not None
                badged += is_new
                no = mv.group(2) if mv else ""
                it = Item(
                    brand=BRAND,
                    name=name,
                    image=_image(li),
                    category=cat,
                    # 사이트 어디에도 날짜가 없다. 이미지 파일명의 YYMMDD 는
                    # 업로드일이라 안 쓴다(함정 7, docstring 참고).
                    is_new=True if is_new else None,
                    url=f"{MAIN}?kind={kind}&no={no}" if no else f"{MAIN}?kind={kind}",
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

    if len(items) < MIN_ITEMS:
        raise RuntimeError(
            f"{BRAND}: 상품 {len(items)}건 — 2026-10-08 실측은 41건이었다 "
            f"(칸별 14/8/19). 본 칸: {[c for _, c in kinds]}")

    if not any(i.image for i in items):
        raise RuntimeError(f"{BRAND}: 이미지가 0건 — '.thumbs' 의 background-image 가 바뀌었다")

    # 🔴 날짜가 없는 브랜드라 배지가 유일한 근거다. 양쪽을 다 막는다.
    if badged > len(items) * BADGE_MAX_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 {badged}건에 NEW 가 붙었다 "
            f"(기대 {BADGE_MAX_RATIO:.0%} 이하, 2026-10-08 실측 5/41=12.2%). "
            "템플릿이 배지를 무조건 찍게 바뀌었는지 보라")
    if badged == 0:
        raise RuntimeError(
            f"{BRAND}: NEW 배지가 0건이다 — 2026-10-08 실측은 5건이었다. "
            "'span.new' 가 바뀌었다면 날짜가 없어 신제품을 영영 못 집는다")
    return items
