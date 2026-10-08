"""베러먼데이(먼데이커피) — (카페, 커피).

공정위 `커피` 업종 가맹점 **136개**(2024년 말, 프차몰 순위 33위). 운영사 표기는
`베러먼데이커피 | BETTER MONDAY COFFEE` 인데 보도·공지에서는 스스로 `먼데이커피` 라
쓴다. 공정위 영업표지를 따라 **베러먼데이**로 둔다.

아임웹이다. 메뉴 내비가 `NEW / COFFEE / NON-COFFEE / BLENDED / TEA / JUICE&ADE /
DESSERT` 인데 **첫 칸 `/menu-new` 만 읽는다.**

  https://www.bettermonday.coffee/menu-new

⚠️ 나머지 6칸(`/menu-energy`·`/menu-drink`·`/menu-healthy`·`/menu-better`·
   `/menu-dessert`·`/menu-bottle`)은 배지도 날짜도 없는 메뉴판이라 **긁지 않는다.**

## 모양 — 출시 포스터 23장, 캡션에 개별 상품명 (2026-10-08 실측)

아임웹 갤러리 위젯이고 카드마다 `<h4>` 가 **묶음 제목**, `<p>` 가 **그 묶음에 든
개별 상품명 목록**이다. 1요청으로 23장이 다 온다.

```
업로드일      <h4> 묶음 제목                      <p> 상품명 목록
2026-08-07    [시즌] 수수하지만 특별해            사탕수수 쿨주스 | 사탕수수 라임에이드 | …(4)
2026-05-04    [시즌] 그 해 여름은                 오리지널 컵빙수 | 망고 컵빙수 | …(4)
2026-02-09    [리뉴얼] 더 맛있고 건강해진 신메뉴   ENERGYㅣREFRESHㅣRICHㅣFRUITY   ← 버린다
2025-12-01    [시즌] 이맘때 이 라떼               고구맛탕 라떼 | 스노우 말차 라떼 | …(6)
   …                                              …
2022-03-23    먼데이라떼                          베러먼데이 시그니처 음료        ← 버린다
```

### 쪼개는 규칙과 **일부러 버리는 것**

`<h4>` 는 캠페인 제목이라 상품명이 아니다(더벤티 `/new2022/menu/new.html` 180건이
기각된 자리). 상품은 `<p>` 쪽에 있다. 구분자로 쪼갠다 —
⚠️ **구분자가 세 종류다.** ASCII `|` · 전각 `｜`(U+FF5C) · **한글 자모 `ㅣ`**(U+3163).
   셋 다 안 받으면 `빅데이 아메리카노｜빅데이 디카페인 아메리카노…` 가 한 덩어리가 된다.

🔴 **구분자가 없는 카드는 통째로 버린다.** 그 자리에 들어 있는 게 상품명일 때도
   있고(`먼데이 초코 크루키`) 설명문일 때도 있어서(`베러먼데이 시그니처 음료`)
   구분이 안 된다. 설명문을 상품으로 올리는 쪽이 한 건 놓치는 쪽보다 나쁘다.
   2026-10-08 실측으로 23장 중 **2장**이 여기 걸린다(`[시즌 베이커리] CROOKIE`,
   `먼데이라떼`). 둘 다 2022·2024년 것이라 어차피 60일 창 밖이다.
   버리는 비율이 1/3을 넘으면 표기가 바뀐 것이므로 터뜨린다.

🔴 **`[리뉴얼]` 태그가 붙은 카드도 버린다.** "더 맛있고 건강해진 신메뉴" 는 기존
   메뉴를 고친 것이고, `<p>` 에 든 `ENERGY`·`REFRESH`·`RICH`·`FRUITY` 는 상품이
   아니라 **라인 이름**이다. 이 레포가 '재출시·리뉴얼을 신상으로 올리는' 사고로
   다섯 건을 차단한 적이 있다(피자스쿨 2015년 치즈피자 계보).

## 날짜 — 이미지 CDN 경로의 `YYYYMMDD`. **`uploaded_at` 에만**

이미지가 `https://cdn.imweb.me/thumbnail/20260807/<해시>.jpg` 다.

🔴 **이미지 시각은 가짜일 때가 많아서 공지 게시판과 대조했다**(컴포즈 149건
일괄·블루샥 배포시각·쑝쑝돈까스 CDN 재생성 선례). 2026-10-08 실측 —

`/news` 게시판 6쪽을 전부 받아 묶음마다 맞춰 봤다. **16묶음이 대조된다.**

```
CDN 날짜    공지 날짜    차    묶음
20260807  2026-08-07   0일   사탕수수 4종 출시
20260504  2026-05-04   0일   "그 해 여름은" 컵빙수 4종 출시
20251201  2025-12-01   0일   겨울 신메뉴 "이맘때 이 라떼"
20250804  2025-08-04   0일   허닭 X 먼데이커피 핫도그 2종 출시
20250512  2025-05-12   0일   "SUMMER in the CUP"
20250317  2025-03-17   0일   "Just do eat!" 출시
20241105  2024-11-05   0일   "Dazzling Holiday"
20231114  2023-11-14   0일   "PISTACHIO WINTER" 3종 출시
20250106  2025-01-07  -1일   "Every Strawberry"
20250929  2025-10-01  -2일   가을 신메뉴 "청송이네 분식"
20250711  2025-07-14  -3일   여름 2차 "Cool down? Drink up!"
20250613  2025-06-16  -3일   빅사이즈 출시
20240905  2024-09-10  -5일   "Deeply Fall"
20231013  2023-10-19  -6일   "TOFFEE NUT&LOTUS" 5종 출시
20231208  2023-12-14  -6일   크리스마스 시즌 음료 2종 출시
20260209  2026-02-02  +7일   리뉴얼 신메뉴 21종 ← 이 카드는 어차피 버린다
```
**절반이 정확히 같은 날이고, 나머지도 CDN 쪽이 0~6일 *먼저*다** — 포스터를 올려
두고 며칠 뒤 공지를 쓰는 순서라 앞뒤가 맞는다. 공지보다 **뒤인 적이 한 번도 없다.**
건수도 맞는다(사탕수수 4종·컵빙수 4종·핫도그 2종·피스타치오 3종·토피넛 5종).
배포 시각이면 전건이 같은 값이어야 하는데 2022-03-23 부터 2026-08-07 까지
23장이 전부 다르다. **진짜 날짜다.**

그래도 브랜드가 "출시일" 이라고 **말한** 값은 아니라 `released_at` 은 비우고
`uploaded_at` 에만 넣는다(파리바게뜨 312장 선례, `rules.untrust_bulk_dates()` 가
보는 자리도 여기다).

4년치가 한 페이지에 쌓여 있지만 **날짜가 다 있어서** 하이오커피식 '1년 바구니'
문제가 생기지 않는다 — `rules.is_fresh` 의 60일 창이 알아서 최근 묶음만 남긴다.
2026-10-08 기준으로 통과하는 건 0건이다(가장 최근이 8월 7일, 62일 전).

## 전건 `is_new=True` 인 이유

소스가 **브랜드가 직접 가른 출시 포스터 칸**이다(에밀리아젤라또 7/7 · 뚜레쥬르
11/442 와 같은 경우). 메뉴판 6칸은 읽지 않으므로 `False` 를 줄 항목 자체가 없다.

## 그 밖

- 상품 상세 페이지가 없다. `Item.url` 은 `/menu-new` 로 둔다.
- 이미지는 포스터라 **같은 묶음의 상품 여러 개가 같은 그림**을 쓴다. 의도한 것이다.
- `먼데이로또` 는 경품 이벤트고 상품이 아니라 이 칸에 없다. 굿즈·술 없음.
- robots(200, 219B): `User-agent: * / Allow: /` 에 Disallow 7줄이 로그인·장바구니·
  관리자·`/?mode*` 다. `/menu-new` 는 어디에도 안 걸린다. sitemap 도 적혀 있다.

등록 제안: 유형 `CAFE`, 세부분류 `커피`
          SITES `https://www.bettermonday.coffee/menu-new`
"""
import re

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "베러먼데이"
SITE = "https://www.bettermonday.coffee"
LIST_URL = f"{SITE}/menu-new"

MIN_CARDS = 12          # 2026-10-08 실측 23장
MIN_ITEMS = 45          # 2026-10-08 실측 71건
SKIP_MAX_RATIO = 1 / 3  # 구분자 없는 카드가 이보다 많으면 표기가 바뀐 것이다

# ⚠️ 세 종류다 — ASCII `|` · 전각 `｜`(U+FF5C) · 한글 자모 `ㅣ`(U+3163).
_SEP = re.compile(r"[|｜ㅣ]")
# `[시즌]`·`[리뉴얼]`·`[여름 시즌 1차]` 처럼 제목 앞에 붙는 태그.
_TAG = re.compile(r"^\s*\[([^\]]+)\]\s*")
_CDN_DATE = re.compile(r"cdn\.imweb\.me/thumbnail/(\d{4})(\d{2})(\d{2})/")
_BG_URL = re.compile(r"url\((['\"]?)(https?://[^)'\"]+)\1\)")

# 기존 메뉴를 고친 것이라 신상이 아니다. `<p>` 에 든 것도 상품이 아니라 라인 이름이다.
SKIP_TAGS = {"리뉴얼"}


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _image(card) -> str:
    node = card.css_first("._img_wrap")
    if not node:
        return ""
    # ⚠️ selectolax 의 .attributes.get(k, "") 는 **값 없는 속성에 None** 을 준다.
    for raw in (node.attributes.get("style") or "", node.attributes.get("data-bg") or ""):
        m = _BG_URL.search(raw)
        if m:
            return m.group(2)
    return ""


def _uploaded_at(img: str) -> str:
    m = _CDN_DATE.search(img or "")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    skipped = 0
    cards_with_caption = 0

    with base.client(headers={"Referer": SITE + "/"}) as c:
        r = base.retry(lambda: c.get(LIST_URL))
        r.raise_for_status()
        cards = HTMLParser(r.text).css(".item_gallary")
        if not cards:
            raise RuntimeError(
                f"{BRAND}: 갤러리 항목 0건 — 아임웹 위젯 마크업(.item_gallary)이 "
                f"바뀌었을 수 있다. 2026-10-08 실측은 23장이었다")

        for card in cards:
            cap = card.css_first("[id^=caption_]")
            if not cap:
                continue
            h = cap.css_first("h4")
            p = cap.css_first("p")
            title = _clean(h.text() if h else "")
            body = _clean(p.text() if p else "")
            if not title and not body:
                continue
            cards_with_caption += 1

            m = _TAG.match(title)
            tag = _clean(m.group(1)) if m else ""
            group = _TAG.sub("", title) if m else title
            if tag in SKIP_TAGS:
                continue

            # 구분자가 없으면 상품명인지 설명문인지 가를 수 없다. 통째로 버린다.
            if not _SEP.search(body):
                skipped += 1
                continue

            img = _image(card)
            uploaded = _uploaded_at(img)
            for part in _SEP.split(body):
                name = _clean(part)
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=group,            # 묶음 제목('그 해 여름은')
                    image=img,
                    category="신메뉴",
                    # 포스터 업로드일. 공지 게시판의 출시 공지와 하루도 안 틀리지만
                    # 브랜드가 '출시일' 이라고 적어 준 값은 아니라 released_at 은 비운다.
                    uploaded_at=uploaded,
                    is_new=True,
                    url=LIST_URL,
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)

    if cards_with_caption < MIN_CARDS:
        raise RuntimeError(
            f"{BRAND}: 캡션이 붙은 포스터가 {cards_with_caption}장뿐이다 — "
            f"2026-10-08 실측은 23장이었다")
    if skipped > cards_with_caption * SKIP_MAX_RATIO:
        raise RuntimeError(
            f"{BRAND}: 포스터 {cards_with_caption}장 중 {skipped}장에 상품 구분자"
            f"(`|`·`｜`·`ㅣ`)가 없다 — 2026-10-08 실측은 2장이었다. 캡션 표기가 "
            f"바뀌었으면 상품을 통째로 놓친다")
    if len(items) < MIN_ITEMS:
        raise RuntimeError(
            f"{BRAND}: 상품 {len(items)}건 — 2026-10-08 실측은 71건이었다. "
            f"캡션 구조가 바뀌었는지 확인하라")

    dated = sum(1 for i in items if i.uploaded_at)
    if dated < len(items) * 0.9:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 날짜를 {dated}건밖에 못 읽었다 — "
            f"이미지가 cdn.imweb.me/thumbnail/<날짜>/ 경로를 벗어났다. "
            f"날짜를 비우면 60일 창을 건너뛴다")

    # 전건이 같은 날이면 사이트 개편 일괄 재업로드다(컴포즈 2026-06-16 149건).
    # 그러면 4년치가 통째로 오늘 신상이 된다.
    days = {i.uploaded_at for i in items if i.uploaded_at}
    if len(days) < 3:
        raise RuntimeError(
            f"{BRAND}: 포스터 업로드일이 {sorted(days)} 뿐이다 — 일괄 재업로드로 "
            f"보인다. 2026-10-08 실측은 2022-03-23 ~ 2026-08-07 사이 19일이었다")
    return items
