"""와플샵(WAFFLE SHOP) — 벨기에식 리에주 와플·크로플 디저트 카페. **(CAFE, "베이커리")**

공정위 `제과제빵` 101곳 중 **41위(가맹점 22개)**. 운영사 (주)케이피엘코리아.
3차 조사(`notes/CANDIDATES-BAKERY3.md`)에서 컵넛 다음으로 날짜가 받쳐주는 곳이다.
2026-10-08 실측.

robots: `https://waffleshop.co.kr/robots.txt` 200 / 254바이트. 아임웹 기본 템플릿이다.
        막는 건 `/site_join*`·`/login`·`/logout.cm`·`/shop_cart`·`/?mode*`·`/admin` 뿐.
        **`/menu` 는 `Allow: /` 에 들어간다 — 무시할 규칙 자체가 없다.**
        푸터 `이용약관` 은 `/?mode=*` 라 robots 가 막는 경로고, 그래서 안 받았다.

## 경로 — `/menu` 한 장. 1,069KB 에 전부 들어 있다

```
GET https://waffleshop.co.kr/menu     아임웹 갤러리 위젯. 카드 121개(중복 포함)
```
카드는 `div._item.item_gallary` → 숨은 캡션 `div[id^=caption_]` 안의
`h4`(시즌 딱지 또는 영문명) · `p`(상품명), 썸네일은 `div._img_wrap` 의 `data-src`.
⚠️ **시즌 갤러리만** PC·모바일용으로 두 벌 깔린다. 전부가 아니다 —
   121 = 시즌 86(=43×2) + 상시 26(×1) + 빈 캡션 9(`img_wrap` 클래스가 `no_content`).
카드 121개 → 포스터·포장재·빈 캡션 41개를 버리고 → 이름 중복을 털어 **상품 52건**.

⚠️ 네비에 `/season`(시즌메뉴)·`/always`(상시메뉴)가 따로 있다. **둘 다 받아서
   대조했고 `/menu` 의 부분집합이다** — `/season` 상품 26종·`/always` 상품 26종,
   `/menu` 에 없는 것 **0건**. 그러니 `/menu` 한 장만 받으면 된다. 다시 파지 마라.
   (`/27`·`/29`·`/30` 은 쇼핑백·유니폼 등 가맹점 주문용이고 로그인 뒤 빈 페이지다.)

⚠️ **페이징 없다.** `href` 에 `page` 가 든 앵커는 로그인 링크 하나뿐이고,
   `/menu?page=2` 는 같은 장을 준다(70바이트 차이는 캐노니컬 URL 에코).
   2022년 시즌부터 2026년 가을까지가 **한 응답에 다 들어 있다.**

## 🔴 soft-404 — 상태코드·건수로는 못 가린다 (함정 ⑧)

```
/menu       200  1,069,335 B   item_gallary 121개   시즌 딱지 86개
/zzz-nope   200  1,223,834 B   item_gallary 184개   시즌 딱지  0개   ← 홈을 그대로 준다
/           200  1,223,835 B   item_gallary 184개   시즌 딱지  0개
```
없는 경로에 **홈이 오는데 그 홈에도 갤러리 카드가 184개 있다.** "카드가 0건이면
터뜨린다" 로는 못 잡는다 — 경로가 깨져도 홈의 184개를 조용히 긁어 온다.
그래서 가드를 **시즌 딱지 개수**에 건다. 그건 `/menu` 에만 있다.

## 🔴 날짜 — 아임웹 CDN 경로의 날짜. **절반은 진짜고 절반은 일괄 재업로드다**

```
https://cdn.imweb.me/thumbnail/20260105/1881bceaa9388.jpg
                               └── YYYYMMDD
```
그냥 쓰면 2022년 메뉴가 2025년 신상이 된다. 다행히 **브랜드가 카드마다 시즌을
직접 적어 놔서**(`h4` = `2026 가을`) 둘을 맞대 보면 진위가 그대로 드러난다:

```
h4            CDN 날짜       판정
2026 가을      2026-09-29    ✅ 연도 일치
2026 여름      2026-07-02    ✅
2026 봄        2026-03-13    ✅
2026 신년      2026-01-05    ✅
2025 겨울      2025-11-03    ✅
2025 가을      2025-09-02    ✅
2025 여름      2025-06-05    ✅
2025 봄        2025-05-29    ✅
2024 봄·여름·가을·겨울   전부 2026-01-05   🔴 연도 불일치 = 일괄 재업로드
2023 봄·여름·가을·겨울   전부 2025-02-21   🔴
2022 여름·할로윈·겨울    전부 2025-02-21   🔴
```
**연도가 어긋나면 날짜를 버린다**(7건). 버리면 `is_new` 도 없으니
`rules.is_fresh()` 가 올리지 않는다 — 2022~2024 메뉴가 오늘 신상으로 뜨는 길이 막힌다.

🔴 **연도만 보면 모자란다.** "같은 해 안에서의 재업로드"가 그대로 통과한다 —
2026 시즌 11건을 오늘 날짜로 재업로드하는 시나리오를 돌려 보니 `FRESH_MAX_RATIO`
(11/52=21%)도 `untrust_bulk_dates`(11<20)도 못 잡고 1월 상품이 오늘 신상으로 올라갔다.
그래서 **월까지 대조한다** — 계절까지 일정하게 맞기 때문에 쓸 수 있는 축이다
(가을→9월, 신년→1월 5일, 겨울→11월). 실측 월에 ±2개월을 준 것이 `SEASON_MONTHS` 다.

이 두 대조가 이 어댑터의 핵심 방어선이다.

상시 메뉴(와플 8종·크로플 7종·음료 11종)는 `h4` 가 시즌이 아니라 **영문명**이고
날짜가 2025-06-04·2025-06-26·2025-08-14 세 덩어리다 — 사이트 만들 때 올린 일괄이다.
교차 검증할 딱지가 없으니 그대로 `uploaded_at` 에 넣되(이미 60일 창 밖이다),
사이트를 새로 열며 사진을 갈아 끼우면 상시 메뉴 26건이 한꺼번에 신상이 되므로
아래 `FRESH_MAX_RATIO` 가드가 그걸 막는다.

**전부 `uploaded_at` 이다. `released_at` 은 비운다** — 브랜드가 "출시일"이라고 말한
값이 아니라 사진 올린 날이다(약한 신호는 약한 칸에).

🔴 **다만 `rules.untrust_bulk_dates()` 는 여기서 한 건도 안 지운다.** 묶음 크기가
`[1,2,2,2,2,2,3,3,4,11,13]` 이라 중앙값 2 → 임계 `max(BULK_MIN 20, 10×2)` = 20 인데
최대 묶음이 13 이다. 제일제면소(`korean_cheiljemyunso.py`)가 같은 상황을 적어 둔 것과
같다 — **rules 쪽 방어가 안 걸린다. 그래서 아래 `FRESH_MAX_RATIO` 가 유일한 바닥이다.**

## 신제품 신호 — **없다. `is_new` 는 전건 `None` 이다**

NEW 배지가 요소로도 글자로도 없다. 시즌 딱지는 2022년치에도 똑같이 붙어 있어서
"신제품이다"는 뜻이 아니다. `False` 로 두면 `is_new is False` 분기가 `released_at`
을 요구해 영구 0건이 되므로(함정 ④) **`None`** 이다. 판정은 날짜가 한다.

2026-10-08 기준 60일 창에 드는 건 **`2026 가을` 4건뿐**이다 —
카스테라 모찌 크로플 · 초코 모찌 크로플 · 옥수수 모찌 와플 · 씨앗 호떡 모찌 와플.

## 🔴 상품이 아닌 카드를 걸러낸다 (함정 ①)

갤러리에는 **포스터 1장짜리 카드와 포장재 카드가 섞여 있다.** 그대로 올리면
'2025겨울 시즌메뉴' 라는 이름의 상품이 생긴다.

```
버리는 것   2026 신년 시즌 · 2023 봄 시즌 · 2022 크리스마스 시즌 · 2025겨울 시즌메뉴
            할로윈 컨셉 시즌 디자인 · 패키지 · 2025 봄/여름/가을/겨울 박스 패키지 …
남기는 것   인절미 앙버터 와플 · 리얼 수박주스 · 씨앗 호떡 모찌 와플 …
```
규칙으로 거른다(열거하면 반드시 빠뜨린다) — 이름에 `패키지`·`시즌메뉴`·`시즌 디자인`
이 들었거나, 이름 자체가 시즌 딱지 꼴(`2023 봄 시즌`)이면 상품이 아니다.

⚠️ 캡션 하나에 상품이 둘·셋 묶여 들어오는 카드가 **17/52(32.7%)** 있다
   (`무화과 얼그레이 와플 / 그릭모모 크로플 / 12곡 곡물라떼`). **쪼개지 않는다.**
   이유는 셋이다 —
     ① 묶음은 **사진 한 장을 공유한다.** 쪼개면 서로 다른 N개 상품이 같은 사진을 쓴다.
     ② 접합자가 하나가 아니다 — ` / ` 말고 `&`·`과 ` 가 섞여 있다(17건 중 8건).
     ③ 쪼갠 조각은 **브랜드가 쓴 적 없는 이름**이다. 이름을 지어내지 않는다.
   (괄호 안 구분자 때문에 못 쪼갠다는 건 **이유가 아니다** — 괄호 깊이를 세면
    `말차라떼(HOT / ICE)` 도 깨지지 않고 갈린다. 검수에서 확인했다.)

## 범위 밖

술 없음. `박스 패키지` 는 포장재라 굿즈가 아니라 **버린다**(위 필터).

등록 제안: 유형 **`CAFE`**, 세부분류 **`베이커리`**.
⚠️ `FRANCHISE` 로 넣으면 1단 탭이 '카페'가 아니라 '외식'으로 간다
   (`taxonomy.primary_of()` 가 '프랜차이즈' 면 무조건 '외식'을 준다).
`디저트39`(CAFE, "디저트")는 선례가 **못 된다** — `디저트` 는 편의점 2depth 이름을
그대로 받은 칸이고(`taxonomy.py` 주석), 레포가 달롱도르·벤슨에서 같은 사유로 두 번
반대 판정을 했다. 와플·크로플은 구운 반죽이라 `베이커리` 가 맞다.
SITES `https://waffleshop.co.kr/menu`
"""
import re
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "와플샵"
SITE = "https://waffleshop.co.kr"
MENU = SITE + "/menu"

MIN_SEASON_TAGS = 30    # 2026-10-08 실측 86개. 홈(soft-404)은 0개다 — 모듈 주석 §soft-404
MIN_ITEMS = 40          # 실측: 카드 121개 → 포스터·포장재 41개 버리고 → 중복 제거 52건
DATED_MIN_RATIO = 0.75  # 실측 52건 중 45건(86.5%). 2022~2024 재업로드 7건은 일부러 버린다
FRESH_MAX_RATIO = 0.15  # 실측 4/52 = 7.7%. 2배 여유. 🔴 0.30 이었을 때
                        # '상시 음료 11건만 재업로드' 가 16건으로 겨우 걸렸다(여유 0.4건)
WINDOW = 60             # rules.WINDOW 와 같은 값. 가드 전용이라 여기서 다시 센다

# `h4` 가 시즌 딱지인가. `2026 가을`·`2022 할로윈`.
_SEASON = re.compile(r"^(20\d{2})\s*(신년|봄|여름|가을|겨울|할로윈)$")

# 썸네일 주소의 업로드 날짜. **`/thumbnail/` 만 본다.**
# 🔴 `/upload/S20250131...` 꼴도 있지만 그 숫자는 업로드일이 아니라
#    **아임웹 사이트 개설일**이다(전 파일이 같은 값 `2025-01-31` 을 준다).
#    날짜로 읽으면 전건이 같은 날짜가 된다. 실측상 갤러리 카드는 121/121 이
#    `/thumbnail/` 이고 `/upload/S` 는 로고·og:image·SNS 아이콘 5건뿐이다.
_CDN_DATE = re.compile(r"cdn\.imweb\.me/thumbnail/(\d{4})(\d{2})(\d{2})")

# 상품이 아닌 카드. 포스터 한 장·포장재다(모듈 주석 §상품이 아닌 카드).
# 열거하지 않고 규칙으로 센다 — 열거하면 반드시 빠뜨린다(base.shown_labels 와 같은 취지).
_NOT_PRODUCT_WORDS = ("패키지", "시즌메뉴", "시즌 메뉴", "컨셉", "디자인")
_NAME_IS_SEASON = re.compile(r"^20\d{2}\s*\S*\s*시즌")


def _is_product(name: str) -> bool:
    if not name:
        return False
    if _NAME_IS_SEASON.match(name):
        return False
    return not any(w in name for w in _NOT_PRODUCT_WORDS)


def _cards(html: str) -> list:
    """`div._item.item_gallary` → (h4, 상품명, 썸네일 주소). 중복은 호출부가 턴다."""
    out = []
    for it in HTMLParser(html).css("div._item.item_gallary"):
        cap = it.css_first("div[id^=caption_]")
        if cap is None:
            continue
        h4 = cap.css_first("h4")
        p = cap.css_first("p")
        wrap = it.css_first("div._img_wrap")
        # selectolax 는 값 없는 속성에 None 을 준다. 기본값이 안 먹는다.
        src = ""
        if wrap is not None:
            src = wrap.attributes.get("data-src") or ""
            if not src:
                # ⚠️ `data-bg` 는 CSS 함수 표기다 — `url(https://…jpg)`.
                #    그대로 쓰면 Item.image 에 `url(...)` 이 들어가 52장이 전부
                #    빈 네모가 된다. derive() 의 http:// 검사에도 안 걸려서
                #    조용히 샌다. 주소만 벗겨 쓴다.
                bg = wrap.attributes.get("data-bg") or ""
                mb = re.search(r"https?://[^)\s\"']+", bg)
                src = mb.group(0) if mb else ""
        out.append((
            " ".join(h4.text().split()) if h4 else "",
            " ".join(p.text().split()) if p else "",
            src,
        ))
    return out


# 시즌 딱지별로 **실측된 업로드 월**에 ±2개월을 준 것. 연도만 보면
# "같은 해 안에서의 재업로드" 가 그대로 통과한다 — 2026 시즌 11건을 오늘
# 날짜로 재업로드하는 시나리오를 돌려 보니 가드를 전부 빠져나갔다.
#
#   실측:  신년 1월 5일 / 봄 3월 13일·5월 29일 / 여름 6월 5일·7월 2일
#          가을 9월 2일·9월 29일 / 겨울 11월 3일
SEASON_MONTHS = {
    "신년":   {11, 12, 1, 2, 3},
    "봄":     {1, 2, 3, 4, 5, 6, 7},
    "여름":   {4, 5, 6, 7, 8, 9},
    "가을":   {7, 8, 9, 10, 11},
    "겨울":   {9, 10, 11, 12, 1},
    "할로윈": {8, 9, 10, 11, 12},
}


def _date_for(tag: str, src: str) -> str:
    """CDN 경로의 날짜. **시즌 딱지와 안 맞으면 버린다**(모듈 주석 §날짜).

    두 가지를 본다.
      · 연도 — 2024·2023·2022년 시즌이 전부 한 날짜(2026-01-05 / 2025-02-21)로
        올라와 있다. 사진을 일괄 재업로드한 자국이지 그때 나온 게 아니다.
      · 월  — 연도만 보면 **같은 해 안에서의 재업로드**가 통과한다. 딱지가
        말하는 계절의 월에서 ±2개월을 벗어나면 그것도 버린다.
    """
    m = _CDN_DATE.search(src or "")
    if not m:
        return ""
    when = "-".join(m.groups())
    season = _SEASON.match(tag)
    if not season:
        return when                       # 상시 메뉴. 대조할 딱지가 없다
    if season.group(1) != m.group(1):
        return ""                         # 연도 불일치
    months = SEASON_MONTHS.get(season.group(2))
    if months and int(m.group(2)) not in months:
        return ""                         # 계절과 월이 안 맞는다
    return when


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(MENU))
        r.raise_for_status()
        cards = _cards(r.text)

    # 🔴 건수로 가드하면 안 된다. 없는 경로가 홈을 주는데 홈에도 카드가 184개 있다.
    #    시즌 딱지는 /menu 에만 있다 — 그걸로 '제대로 된 장이 왔는지' 를 판정한다.
    tags = sum(1 for tag, _, _ in cards if _SEASON.match(tag))
    if tags < MIN_SEASON_TAGS:
        raise RuntimeError(
            f"{MENU}: 시즌 딱지가 {tags}개다(카드 {len(cards)}개) — 2026-10-08 실측은 "
            f"86개였다. **이 사이트는 없는 경로에 홈을 200 으로 돌려주고 그 홈에도 "
            f"갤러리 카드가 184개 있다.** 경로가 깨졌는지, 갤러리 위젯 마크업이 "
            f"바뀌었는지 확인하라")

    # 🔴 중복 제거는 **날짜가 가장 이른 카드**를 남긴다.
    # `초코 모찌 크로플` 은 2026 여름(2026-07-02)과 2026 가을(2026-09-29)에 둘 다
    # 있다. 문서 순서대로 첫 카드를 남기면 98일 된 상품이 9일 된 신상으로 올라간다.
    best: dict = {}
    dropped = 0
    for tag, name, src in cards:
        if not _is_product(name):
            dropped += 1
            continue
        when = _date_for(tag, src)
        key = base.make_key(BRAND, name)
        cur = best.get(key)
        # 날짜 없는 카드보다 날짜 있는 카드가 낫고, 날짜끼리는 이른 쪽이 낫다.
        if cur is None or (when and (not cur[0] or when < cur[0])):
            best[key] = (when, tag, name, src)

    items: list[Item] = []
    for when, tag, name, src in best.values():
        it = Item(
            brand=BRAND,
            name=name,
            # 상시 메뉴는 h4 가 영문명이다. 시즌 딱지면 영문명이 아니니 안 쓴다.
            name_en="" if _SEASON.match(tag) else tag,
            image=src,
            # 시즌 메뉴는 그 시즌에만 판다. 종료일을 주는 자리는 없어서 끝난 걸
            # 끊지는 못하고 표시만 한다(제일제면소·파이브가이즈와 같은 말).
            labels=["기간 한정"] if _SEASON.match(tag) else [],
            # 연도·월이 어긋나는 일괄 재업로드는 _date_for 가 버린다.
            uploaded_at=when,
            # NEW 배지가 없다. 시즌 딱지는 2022년치에도 붙어 있어 신제품 표시가
            # 아니다. False 로 두면 released_at 을 요구해 영구 0건이 된다.
            is_new=None,
            url=MENU,
        )
        items.append(it)

    if not dropped:
        raise RuntimeError(
            f"{BRAND}: 포스터·포장재 카드를 하나도 못 걸렀다 — 2026-10-08 실측은 "
            f"중복 포함 121개 중 '…시즌'·'박스 패키지'·'할로윈 컨셉 시즌 디자인' "
            f"꼴이 섞여 있었다. 필터가 헛돌면 '2025겨울 시즌메뉴' 가 상품으로 올라간다")

    if len(items) < MIN_ITEMS:
        raise RuntimeError(
            f"{BRAND}: 상품 {len(items)}건(카드 {len(cards)}개, 버린 것 {dropped}개) — "
            f"2026-10-08 실측은 52건이었다(카드 121개, 버린 것 41개). "
            f"캡션 `div[id^=caption_]` 의 h4/p 가 "
            f"바뀌었는지 확인하라")

    dated = sum(1 for i in items if i.uploaded_at)
    if dated < len(items) * DATED_MIN_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 날짜가 {dated}건뿐이다 — 썸네일이 "
            f"`cdn.imweb.me/thumbnail/<YYYYMMDD>/` 꼴이 아니거나, 시즌 딱지와 "
            f"연도가 어긋나는 일괄 재업로드가 늘었다. 2026-10-08 실측은 "
            f"52건 중 45건(86.5%)이 남았다(2022~2024 시즌 7건은 일부러 버린 것이다)")

    # 날짜가 유일한 판정 근거다. 사이트를 새로 열며 사진을 갈아 끼우면 상시
    # 메뉴 26건이 한꺼번에 최근 날짜를 갖는다(도미노 2026-09-14 선례).
    cutoff = (date.today() - timedelta(days=WINDOW)).isoformat()
    fresh = sum(1 for i in items if i.uploaded_at and i.uploaded_at >= cutoff)
    if fresh > len(items) * FRESH_MAX_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 {fresh}건의 업로드 날짜가 최근 {WINDOW}일 "
            f"안이다(기대 {FRESH_MAX_RATIO:.0%} 이하, 2026-10-08 실측 4/52=7.7%). "
            f"사진을 일괄 재업로드했는지 확인하라")
    return items
