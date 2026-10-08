"""컵넛(cupnut) — 링도넛·디저트 카페. **(CAFE, "도넛")**

공정위 `제과제빵` 101곳 중 **32위(가맹점 25개)**. 3차 조사(`notes/CANDIDATES-BAKERY3.md`)
에서 **상품마다 날짜가 나오는** 몇 안 되는 곳이라 어댑터를 만들었다. 2026-10-08 실측.

⚠️ 파일 이름이 `bakery_` 가 아니라 `cafe_` 다. 기존 `bakery_*` 9개는 전부 세부분류가
   `베이커리` 이고, 세부분류 `도넛` 의 선례인 던킨은 `cafe_dunkin.py` 다.

robots: `https://cupnut.co.kr/robots.txt` 200 / **22바이트** — `User-agent: *` + `Allow:/`.
        금지 경로가 하나도 없다. 푸터 법적 링크는 `/policy/private`(개인정보처리방침)
        하나뿐이고 웹사이트 이용약관 페이지가 없다. 복제·크롤러 금지 조항 없음.

## 경로 — 메뉴 다섯 칸. 그게 전부다

```
GET /product/list?s_category1=5000000   NEW         21건
GET /product/list?s_category1=1000000   COFFEE      11건
GET /product/list?s_category1=2000000   BEVERAGE    39건
GET /product/list?s_category1=3000000   DONUT       11건
GET /product/list?s_category1=4000000   DESSERTS    21건
                                        ──────────────────
                                        합계       103건 → 이름 합치기 후 **97건**
```
카드는 `div.lineup li` → `h3`(한글명) · `p`(영문명) · `img`(썸네일).
**상품 상세 페이지가 없다** — `li` 안에 `<a>` 가 아예 없다. 그래서 `url` 은
**그 상품이 들어 있던 분류 페이지**로 둔다(NEW 칸이 아니라 실제 칸 쪽).

⚠️ **페이징은 없다. 다만 파라미터 이름을 조심해라.** 이 CMS 의 페이징 파라미터는
   `page` 가 아니라 **`paging`** 이다 — `/sitemap.xml` 이 매장 목록을
   `.../store/store?...&paging=1..7` 로 직접 알려 준다. 함정 ⑧(한화갤러리아는
   파라미터가 `p` 였다)에 걸릴 자리라 **올바른 이름으로 다시 쟀다**:

```
s_category1=2000000            200 / 23,610B / 카드 39
s_category1=2000000&paging=2   200 / 23,610B / 카드 39   ← 상품 목록은 paging 을 무시한다
(대조군) /store/store          21,912B → &paging=2 는 22,077B   ← 매장 목록은 반응한다
```
   마크업 근거도 같다 — BEVERAGE 페이지의 앵커 14종에 `page`/`paging` 이 든 href 가
   **0개**, `onclick`·`data-page`·`form`·`select` 도 0개, 페이지네이션류 클래스는
   `page-top`(맨 위로) 하나뿐이다. 사이트맵의 상품 URL 도 이 5칸이 전부다.
   ⚠️ 응답 **길이**는 같지만 바이트가 같지는 않다(sha1 이 매번 다르다 — 동적 토큰).

⚠️ **없는 분류도 없는 경로도 전부 200 이다.** soft-404 사이트다.
```
s_category1=9999999  200 / 11,317B / 카드 0      s_category1=6000000  200 / 11,317B / 0
/product/list        200 /  6,184B / 카드 0      /zzz-nope            200 /  6,557B / 0
```
   `raise_for_status()` 는 사실상 죽은 줄이다. **판정은 전부 건수로 한다.**

## 🔴 신제품 신호 — `NEW` 칸은 있지만 **그대로 믿으면 안 된다. 33개월짜리 바구니다**

`NEW` 칸 21건의 날짜가 **2023-12-19 ~ 2026-09-15 (32.9개월)** 에 걸쳐 있고,
한 칸 안에서 계절이 서로 모순된다 — 함정 ③ 의 하이오커피(1년치 바구니)보다 심하다:

```
[시즌한정] 컵빙수 2종        2026-05-18     ← 여름
크리스마스 딸기 프리미엄 에디션   2025-12-23     ← 겨울
[시즌한정] 리얼수박주스        2025-04-30     ← 여름
[시즌한정]페스츄리 겨울 간식 2종  2025-12-23     ← 겨울
크리스피 페스츄리 크로플        2023-12-19     ← 2년 10개월 전
```
수박주스와 크리스마스 딸기가 나란히 있다. **진열 칸이지 신제품 목록이 아니다.**
그래서 `is_new` 로는 쓰되 **날짜가 최종 판정을 하게** 둔다(`rules.is_fresh()` 는
`is_new is True` 여도 `stamped` 가 있으면 날짜를 따른다). `NEW` 칸에 없는 상품은
브랜드가 아무 말도 안 한 것이므로 **`None`** 이다 — `False` 로 두면
`is_new is False` 분기가 `released_at` 을 요구해 영구 0건이 된다(함정 ④).

배지 비율: **97건 중 21건 = 21.6%** (합치기 전 21/103 = 20.4%).

**요소 배지는 없다 — 전수로 확인했다.** 5칸의 `.lineup li` 안 태그는
`{li, div×2, img, h3, p}` 뿐이고 **`span` 이 0개**다. 클래스도 `img`/`img type2`/`txt`
뿐인데 `type2` 는 NEW·DESSERTS 21건 **전건**에 똑같이 붙는 레이아웃 클래스다.
각 분류 페이지의 `new` 문자열 등장은 **0회**(홈도 0회)다.

## 날짜 — 썸네일 경로의 업로드 시각. **103건 전건에서 읽힌다**

```
/_public/uploadFiles/goods/20260915092404271/L4RFOU4AOBCUAX4FT4ZU.jpg
                           └── YYYYMMDDHHMMSSmmm (17자리)
```
이 레포는 원래 이미지 날짜를 잘 안 믿는다(컴포즈커피 149건 전부 같은 값 = 배포
시각). 그래서 **두 가지로 검증했다.**

**① 분포 — 28개 날짜로 갈린다.** 한 값으로 뭉치지 않는다.
```
2023-12-28  37건   ← 사이트 오픈 일괄
2024-05-30  11건 / 2025-07-11  9건 / 2025-12-23  9건 / 2025-11-03  6건
2025-11-04  3건 / 그 외 22개 날짜가 1~2건씩
```

**② 썸네일 `Last-Modified` 와 대조 — 초 단위로 맞는다.**
```
플랫오트2종          dir 2026-09-15 09:24:04 KST   LM 2026-09-15 00:24:32 GMT  (+28초)
[시즌한정] 컵빙수 2종    dir 2026-05-18 09:27:37      LM 2026-05-18 00:28:27 GMT  (+50초)
크리스마스 딸기시리즈     dir 2025-12-23 09:17:10      LM 2025-12-23 00:17:34 GMT  (+24초)
미니넛 3구 기프트 세트    dir 2026-02-06 16:20:16      LM 2026-02-06 07:21:14 GMT  (+58초)
```
시·분이 전부 업무시간(09~17시)인 것도 사람이 하나씩 올린 모양이다.

**🔴 그런데 `released_at` 은 아니다 — 반증 2건.** 디렉터리는 최초 업로드를 유지한 채
사진만 나중에 교체된 것이 있다:
```
플랫오트            dir 2026-06-12 10:25   그런데 LM 2026-08-27 13:28 KST
[시즌한정] 리얼수박주스   dir 2025-04-30 16:17   그런데 LM 2026-05-18 09:28 KST
```
'사진을 올린 날'이지 '출시일'이 아니다. **`uploaded_at` 에만 넣는다.** 그 자리라야
`rules.untrust_bulk_dates()` 가 본다 — 실행해 보면 중앙값 1 × `BULK_RATIO` 10,
`BULK_MIN` 20 → 임계 20 이고 **2023-12-28 의 37건이 실제로 지워진다.**

## 이름 충돌 — `[시즌한정]` 접두 때문에 같은 상품이 두 장 뜬다

`make_key()` 는 괄호 안 사이즈 표기만 털고 **대괄호 접두는 남긴다.** 그대로 두면
아래 6쌍이 카드 두 장이 된다. **6쌍 모두 영문명까지 같아** 같은 상품이 확실하다:

```
옥수수도넛        NEW 2026-08-12 / DONUT    2026-08-12   en=Oksusu Donut
플랫오트          NEW 2026-06-12 / COFFEE   2026-07-08   en=Flat Oat
리얼수박주스       NEW 2025-04-30 / BEVERAGE 2025-04-30   en=Real Watermelon Juice
티슈브레드        NEW 2025-11-07 / DESSERTS 2025-11-07   en=Tissue Bread
소금빵           NEW 2025-10-02 / DESSERTS 2023-12-28   en=Salted Butter Roll
두바이스타일(도넛)   NEW 2024-05-30 / DONUT    2024-11-12   en=Dubai Style Donut
```
**대괄호 접두와 공백을 턴 이름**으로 합친다. 합칠 때
  · 이름은 **긴 쪽** — `[시즌한정]` 이 붙은 쪽이 정보가 더 많다.
  · 분류는 **NEW 가 아닌 쪽** — NEW 는 진열 칸이지 그 상품의 분류가 아니다.
    `url` 도 그 칸을 가리킨다(안 그러면 97건 전부가 NEW 칸을 가리키는데 그중
    76건은 거기에 없다).
  · 🔴 날짜는 **늦은 쪽**. 이게 중요하다 — 이른 쪽을 쓰면 `소금빵` 이
    2023-12-28 오픈 일괄에 들어가 `untrust_bulk_dates()` 에 날짜를 통째로 뺏기고,
    그러면 `is_new=True` + 날짜 없음이 돼 **`is_fresh()` 의 배지 분기로 빠져
    60일 창을 건너뛴다.** 늦은 날짜 셋(2025-10-02 / 2026-07-08 / 2024-11-12)은
    전부 60일 창 밖이라 신상으로 둔갑할 수 없다 — 늦은 쪽이 안전하다.
  · `is_new` 는 둘 중 하나라도 NEW 칸에 있으면 True.

## 기간 한정

이름이 **`[시즌한정]` 으로 시작할 때만** `기간 한정` 라벨을 붙인다(파이브가이즈·
제일제면소가 쓰는 말과 같게). ⚠️ "아무 대괄호" 로 판정하면 안 된다 — 접두 분포가
`[시즌한정] 14건 / [시그니처] 1건` 이라 상시 메뉴인 `[시그니처] 크렘브륄레도넛` 에
'기간 한정' 이 잘못 붙는다. 종료일을 주는 자리는 사이트 어디에도 없어서 끝난
상품을 끊지는 못한다 — 날짜가 60일 창을 벗어나면 알아서 내려간다.

## 범위 밖

술 없음. 굿즈는 `미니넛 3구/9구 기프트 세트` 둘뿐인데 먹는 것이라 굿즈가 아니다.

등록 제안: 유형 **`CAFE`**, 세부분류 **`도넛`**(던킨과 같은 칸).
⚠️ `FRANCHISE` 로 넣으면 1단 탭이 '카페'가 아니라 '외식'으로 간다.
SITES `https://cupnut.co.kr/product/list?s_category1=5000000`
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "컵넛"
SITE = "https://cupnut.co.kr"
LIST = SITE + "/product/list?s_category1="
DELAY = 1.5

# (분류 코드, 칸 이름, 2026-10-08 실측 건수).
# 칸별 실측치를 상수로 들고 있어야 "한 칸만 반쯤 깨진" 경우를 잡는다 —
# 전체 하한(MIN_ITEMS)만으로는 97→81 까지 조용히 통과한다.
CATEGORIES = [
    ("5000000", "NEW", 21),        # ⚠️ 신제품 목록이 아니라 진열 칸이다(모듈 주석)
    ("1000000", "COFFEE", 11),
    ("2000000", "BEVERAGE", 39),
    ("3000000", "DONUT", 11),
    ("4000000", "DESSERTS", 21),
]
NEW_CODE = "5000000"

CAT_MIN_RATIO = 0.70    # 칸별 실측치의 이 비율 밑으로 떨어지면 터뜨린다
MIN_ITEMS = 80          # 2026-10-08 실측 103건 → 합치기 후 97건
MAX_ITEMS = 300         # 폭주 방지 상한
NEW_MAX_RATIO = 0.50    # 실측 21/97 = 21.6%
DATED_MIN_RATIO = 0.95  # 실측 97/97 = 100%
# 실측 3/97 = 3.1%. 여유를 크게 두면 안 된다 — 0.35 였을 때 "33건 부분 재업로드"
# 까지 통과했고, 그 경우 날짜를 잃은 2024~2025년 상품 9건이 배지만으로 올라갔다.
FRESH_MAX_RATIO = 0.15
WINDOW = 60             # rules.WINDOW 와 같은 값. 가드 전용이라 여기서 다시 센다

# `/_public/uploadFiles/goods/20260915092404271/XXXX.jpg` 의 앞 8자리.
_UPLOAD_DIR = re.compile(r"/goods/(\d{4})(\d{2})(\d{2})\d*/")

# 합치기용. 이름 맨 앞의 **아무** 대괄호를 턴다 — `[시즌한정] 옥수수도넛` 과
# `옥수수도넛` 을 같은 상품으로 본다(실측 오합치 0건/103).
_LEAD_BRACKET = re.compile(r"^\s*\[[^\[\]]*\]\s*")

# 라벨용. **`[시즌한정]` 일 때만** 이다. 아무 대괄호로 하면 상시 메뉴인
# `[시그니처] 크렘브륄레도넛` 에 '기간 한정' 이 붙는다.
_SEASON_PREFIX = re.compile(r"^\s*\[\s*시즌\s*한정\s*\]")


def _norm(name: str) -> str:
    """합치기 키. 대괄호 접두와 공백만 턴다(모듈 주석 §이름 충돌)."""
    return _LEAD_BRACKET.sub("", name).replace(" ", "")


def _upload_date(src: str) -> str:
    """썸네일 경로의 업로드 시각 → 'YYYY-MM-DD'. 못 읽으면 빈 문자열."""
    m = _UPLOAD_DIR.search(src or "")
    return "-".join(m.groups()) if m else ""


def _rows(html: str) -> list:
    """`div.lineup li` → (한글명, 영문명, 썸네일 주소).

    썸네일 `src` 는 `/_public/...` 상대경로다. 삼송빵집과 같이 여기서 호스트를
    붙여 둔다 — `base.derive()` 는 `http://` 만 다루고 상대경로는 그대로
    흘려보내서, 우리 페이지에서 깨진 네모가 된다.
    """
    out = []
    for li in HTMLParser(html).css(".lineup li"):
        h3 = li.css_first("h3")
        name = " ".join(h3.text().split()) if h3 else ""
        if not name:
            continue
        en = li.css_first("p")
        img = li.css_first("img")
        # selectolax 는 값 없는 속성에 None 을 준다. 기본값이 안 먹는다.
        src = (img.attributes.get("src") or "") if img else ""
        if src.startswith("/"):
            src = SITE + src
        out.append((
            name,
            " ".join(en.text().split()) if en else "",
            src,
        ))
    return out


def fetch() -> list[Item]:
    merged: dict = {}      # _norm(이름) → 합쳐진 한 건
    per_cat: dict = {}

    with base.client() as c:
        for i, (code, label, expect) in enumerate(CATEGORIES):
            if i:
                time.sleep(DELAY)
            url = LIST + code
            r = base.retry(lambda url=url: c.get(url))
            r.raise_for_status()      # soft-404 사이트라 사실상 안 걸린다. 판정은 건수로 한다
            rows = _rows(r.text)
            per_cat[label] = len(rows)
            # 칸 하나가 통째로 비거나 반쯤 깨지면 그 칸의 상품이 영원히 안
            # 올라오는데 전체 건수로는 잘 안 보인다. 칸마다 바닥을 둔다.
            if len(rows) < expect * CAT_MIN_RATIO:
                raise RuntimeError(
                    f"{url}: '{label}' 칸 {len(rows)}건 — 2026-10-08 실측은 {expect}건이었다. "
                    f"'.lineup li > h3' 가 깨졌거나 분류 코드가 바뀌었다. "
                    f"(없는 분류·없는 경로에도 200 을 주는 사이트라 상태코드로는 못 가린다) "
                    f"여기까지 받은 칸: {per_cat}")

            for name, en, src in rows:
                key = _norm(name)
                when = _upload_date(src)
                cur = merged.get(key)
                if cur is None:
                    merged[key] = dict(name=name, name_en=en, image=src,
                                       when=when, is_new=(code == NEW_CODE),
                                       category=label, code=code)
                    continue
                # 같은 상품이 두 칸에 있다. 규칙은 모듈 주석 §이름 충돌 참고.
                if len(name) > len(cur["name"]):
                    cur["name"], cur["name_en"], cur["image"] = name, en, src
                # 분류·링크는 NEW 칸이 아닌 쪽을 남긴다.
                if cur["code"] == NEW_CODE and code != NEW_CODE:
                    cur["category"], cur["code"] = label, code
                # 🔴 늦은 쪽. 이른 쪽을 쓰면 소금빵이 오픈 일괄에 끌려들어가
                #    날짜를 잃고 배지만으로 60일 창을 건너뛴다.
                if when and when > (cur["when"] or ""):
                    cur["when"] = when
                cur["is_new"] = cur["is_new"] or (code == NEW_CODE)

    items: list[Item] = []
    seen = set()
    for row in merged.values():
        it = Item(
            brand=BRAND,
            name=row["name"],
            name_en=row["name_en"],
            image=row["image"],
            # 종료일을 주는 자리가 없다. 끝난 상품을 끊지는 못하고 표시만 한다.
            labels=["기간 한정"] if _SEASON_PREFIX.match(row["name"]) else [],
            category=row["category"],
            # 썸네일 경로의 업로드 시각. 2023-12-28 에 37건이 몰린 오픈 일괄이
            # 섞여 있고 사진만 나중에 갈린 것도 있어 released_at 에 넣지 않는다.
            uploaded_at=row["when"],
            # NEW 칸은 33개월짜리 진열 칸이다. True 로 두되 날짜가 판정한다.
            # 칸에 없는 상품은 브랜드가 아무 말도 안 한 것이므로 None 이다
            # (False 로 두면 released_at 을 요구해 영구 0건이 된다).
            is_new=True if row["is_new"] else None,
            # 상세 페이지가 없다. 그 상품이 실제로 들어 있던 칸을 가리킨다.
            url=LIST + row["code"],
        )
        if it.key not in seen:
            seen.add(it.key)
            items.append(it)

    total = sum(per_cat.values())
    if not MIN_ITEMS <= len(items) <= MAX_ITEMS:
        raise RuntimeError(
            f"{BRAND}: 상품 {len(items)}건(합치기 전 {total}건) — 2026-10-08 실측은 "
            f"103건 → 합치기 후 97건이었다(기대 {MIN_ITEMS}~{MAX_ITEMS}). "
            f"칸별 실측: {per_cat}")

    new_count = sum(1 for i in items if i.is_new)
    if not new_count:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 NEW 칸이 0건 — 분류 코드 "
            f"s_category1={NEW_CODE} 가 바뀌었는지 확인하라. "
            f"2026-10-08 실측은 21건이었다")
    if new_count > len(items) * NEW_MAX_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 {new_count}건이 NEW 칸이다 — 2026-10-08 "
            f"실측은 97건 중 21건(21.6%)이었다. 다른 칸을 못 받았는지 확인하라. "
            f"칸별 실측: {per_cat}")

    dated = sum(1 for i in items if i.uploaded_at)
    if dated < len(items) * DATED_MIN_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 날짜를 {dated}건밖에 못 읽었다 — 썸네일 "
            f"경로가 '/_public/uploadFiles/goods/<YYYYMMDDHHMMSSmmm>/' 모양이 "
            f"아니다. 2026-10-08 실측은 97/97 이었다. **날짜가 없으면 NEW 칸의 "
            f"2023년 상품이 배지만으로 오늘 신상이 된다**")

    # NEW 칸이 3년치 바구니라 날짜가 유일한 방어선이다. 사이트를 다시 열며
    # 사진을 일괄 재업로드하면 메뉴판이 통째로 최근 날짜를 갖는다(도미노 선례).
    cutoff = (date.today() - timedelta(days=WINDOW)).isoformat()
    fresh = sum(1 for i in items if i.uploaded_at and i.uploaded_at >= cutoff)
    if fresh > len(items) * FRESH_MAX_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 {fresh}건의 업로드 시각이 최근 {WINDOW}일 "
            f"안이다(기대 {FRESH_MAX_RATIO:.0%} 이하, 2026-10-08 실측 3/97=3.1%). "
            f"사진을 일괄 재업로드했는지 확인하라")
    return items
