"""더플레이스 — CJ푸드빌 이탈리안 비스트로. 빕스와 **같은 공용 API** 를 쓴다.

`collectors/western_vips.py` 가 찾아 둔 CJ푸드빌 브랜드 공용 API 의 두 번째
브랜드다. 청크의 브랜드 enum 이 `{VIPS, THEPLACE, CHEILJEMYUNSO, OLIPEPE}`
넷이고 그중 `THEPLACE` 다.

  GET https://brand-api.ivips.co.kr/menus/THEPLACE/category?page=0&size=100
  GET https://brand-api.ivips.co.kr/menus/THEPLACE/<categoryIdx>?page=N&size=100

⚠️ `page`·`size` 를 빼면 **400** 이다(`MSG_FO_00014`). 2026-10-08 재확인.
⚠️ `size=100` 을 줘도 서버가 무시하고 한 쪽에 10건만 준다. `totalPages` 를
   보고 끝까지 돌아야 41건이 다 나온다(빕스와 같은 함정).
⚠️ `Referer` 는 필요 없다. 헤더 없이도 200 이다(실측). 그래도 신원을 밝히는
   쪽이 맞아서 빕스와 같이 브랜드 사이트를 붙인다.

## 도메인 — `theplace.co.kr` 이 **아니다**

`www.theplace.co.kr` 는 https 가 **Connection refused**, http 는 **403/198B** 다.
남의 호스트다. 진짜 공식 사이트는 **`www.italiantheplace.co.kr`** 이고
`?ssoLoginYN=N` 을 붙여야 셸이 아니라 실제 페이지(23,200B)가 온다 — 빕스와
같은 CJ ONE SSO 리다이렉트 구조다. 머거본 `.co.kr`/`.com` 선례와 같은
도메인 오인 자리라 적어 둔다.

robots: `https://www.italiantheplace.co.kr/robots.txt` 200 / 980B.
        내용은 빕스와 같은 템플릿이다 — `User-agent: * / Disallow: /` 에
        Googlebot·NaverBot·Daumoa 만 `Allow`. **2026-10-02 운영자가 CJ푸드빌
        robots 무시를 승인**했고(빕스), 2026-10-08 지시로 같은 사이트군의
        나머지 브랜드를 연다. **UA 위장은 하지 않는다** — 삭제 요청이 오면
        즉시 내린다(이마트24·도미노피자와 같은 칸).

## 카테고리 — 7칸 전부 `NORMAL` (2026-10-08 실측)

```
idx=14 DESSERT          idx=13 STEAK            idx=12 PIZZA
idx=11 RISOTTO&GNOCCHI  idx=10 PASTA            idx= 9 ANTIPASTI
idx= 7 SALAD&SOUP
```
빕스에 있던 `SALAD`·`DELIVERY`·`ALLERGY` 칸이 **여기엔 없다.** 그래도
`SKIP_TYPES` 는 그대로 둔다 — 빕스처럼 나중에 생기면 재료·알레르기 표가
상품으로 올라온다. 상품 **41건**.

## 🔴 신제품 신호 — **NEW 배지가 0건이다. 날짜로 판정한다**

```
tag=NONE  41건 (100%)
tag=NEW    0건 (0%)      ← 빕스는 14건 중 1건(7.1%)이었다
```
`tag` 필드는 응답에 **있는데 이 브랜드는 안 쓴다.** 그래서 빕스처럼
`is_new=(tag == "NEW")` 로 쓰면 **41건이 전부 `False`** 가 되고,
`rules.is_fresh()` 의 `is_new is False` 분기가 `released_at` 을 요구하는데
이 API 는 출시일을 안 주므로 **이 브랜드는 영원히 화면에 0건**이 된다.

→ **`tag` 가 `NEW` 면 `True`, 아니면 `None`(모름)** 으로 둔다.
  `NONE` 은 브랜드가 "신제품이 아니다"라고 말한 게 아니라 **아무 말도 안 한
  것**이다. 그 자리를 `False` 로 단정하면 거짓이 된다.
  ⚠️ **빕스(`western_vips.py`)와 다른 처리다.** 거긴 `NEW` 가 실제로 쓰여서
  `False` 가 "안 붙였다"는 뜻을 갖지만, 여긴 필드 자체가 비어 있다.
  빕스 쪽은 출력이 깨끗한 걸 실측해 뒀으니 건드리지 않는다.

## 날짜 — `startDate`. **`released_at` 이 아니라 `uploaded_at`**

```
2025-11-14  36건 (88%)  ← 사이트 오픈 일괄 입력
2026-08-26   2건
2026-03-19   1건
2025-11-17   1건
2026-09-08   1건
```
36건이 하루에 몰려 있다. 빕스(11/14건이 2025-11-13)·파리바게뜨 312장과
같은 일괄 입력이라 **`uploaded_at` 에만 넣는다**(`rules.untrust_bulk_dates()`
가 보는 자리). 그 묶음은 `BULK_MIN=20`·`BULK_RATIO=10` 조건을 넘겨 무효화되고,
설령 안 걸려도 11개월 전이라 60일 창 밖이다.

### 🔴 몰려 있지 않은 날짜는 **진짜 출시일이다 — 외부 보도로 대조했다**

```
무화과 리코타 샐러드 · 무화과 티라미수   startDate 2026-08-26
    → 2026-09-01 보도 "제철 생무화과로 가을 메뉴…샐러드·티라미수 출시"
대하 로제 파파르델레                      startDate 2026-09-08
    → 2026-09-15 보도 "가을 시즌 신메뉴 '대하 로제 파파르델레' 선봬"
```
`startDate` 가 보도보다 **일주일쯤 빠르다**. 메뉴가 실제로 열린 날이고
보도가 뒤따른 것이다. 즉 이 브랜드에서 '일괄 묶음 밖의 `startDate`' 는
믿을 수 있는 신호다. 위 3건이 지금 60일 창 안에 드는 전부다(3/41, 7.3%).

⚠️ 같은 보도에 **'시즌 스페셜 세트'·'시즌 파티 세트'** 가 함께 나오는데
   API 에는 안 들어온다. 들어와도 `rules.drop_sets()` 가 이름으로 거른다.

## 기간 한정 — `endDate` 를 읽는다 (빕스 어댑터엔 없는 처리)

2026-10-08 실측에서 더플레이스는 **41건 전부 `9999-12-31`**(상시)이라 지금은
걸리는 게 없다. 그래도 같은 API 의 제일제면소가 가을 신메뉴 3종에 진짜
종료일(2026-11-26·11-27)을 넣고 있으므로 이 브랜드도 시즌 메뉴를 넣기
시작하면 같은 모양이 된다. 안 읽으면 **끝난 메뉴가 계속 올라온다.**
→ 종료일이 지나면 버리고, 상시가 아니면 `기간 한정` 라벨을 붙인다.
`displayStatus` 도 41건 전부 `Y` 라 지금은 거를 게 없다.

## 이미지

`imageUrl` 이 `images/THEPLACE/menus/<uuid>-<epoch ms>.png` 상대경로다.
앞머리는 CJ푸드빌 브랜드 사이트 아무 곳이나 같은 바이트를 주는데(실측 3곳
전부 200, 같은 길이) **자기 브랜드 호스트**를 붙인다.
`Content-Type` 이 `application/octet-stream` 으로 오지만 `rules._is_image()`
는 매직 바이트로 보므로 지워지지 않는다(대상 `download.jsp` 와 다른 경우다).

## 범위 밖

술은 메뉴에 없다(API 41건이 전부 전채·파스타·피자·스테이크·디저트).
와인 리스트는 API 에 올라오지 않는다.

등록 제안: 유형 `FRANCHISE`, 세부분류 `양식`
          SITES `https://www.italiantheplace.co.kr/menu`
"""
import time
from datetime import date, timedelta

from . import base
from .base import Item

BRAND = "더플레이스"
SITE = "https://www.italiantheplace.co.kr"
API = "https://brand-api.ivips.co.kr"
BRAND_CODE = "THEPLACE"
DELAY = 1.5
MAX_PAGES = 15   # 폭주 방지. 현재 가장 큰 칸(PASTA 10건)이 1페이지다.
MIN_CATES = 7    # 2026-10-08 실측 7칸. 줄면 페이징이 잘린 것이다
MIN_ITEMS = 30   # 2026-10-08 실측 41건

# 빕스에서 프런트가 목록 질의를 아예 걸지 않는 칸들. 더플레이스엔 아직 없지만
# 생기면 재료·알레르기 표가 상품으로 올라오므로 같은 목록을 들고 간다.
SKIP_TYPES = {"SALAD", "DELIVERY", "ALLERGY"}

# 60일 창 안에 드는 상품이 이 비율을 넘으면 일괄 입력이 새로 들어온 것으로 본다.
# 2026-10-08 실측 3/41 = 7.3%.
FRESH_MAX_RATIO = 0.35
WINDOW = 60      # rules.WINDOW 와 같은 값. 가드 전용이라 여기서 다시 센다


def _json(c, path: str, page: int = 0):
    # ⚠️ page·size 를 빼면 400 이다. size 는 서버가 무시하고 10건씩 준다.
    r = base.retry(lambda: c.get(f"{API}{path}", params={"page": page, "size": 100}))
    r.raise_for_status()
    body = r.json()
    if body.get("status") != 200:
        raise RuntimeError(f"{path}: status={body.get('status')} "
                           f"code={body.get('code')} error={body.get('error')}")
    return body.get("data") or {}


def _pages(c, path: str) -> list:
    """`totalPages` 를 보고 끝까지 돈다. 한 쪽에 10건씩만 온다."""
    rows = []
    for page in range(MAX_PAGES):
        data = _json(c, path, page)
        rows += data.get("content") or []
        if page + 1 >= (data.get("totalPages") or 1):
            break
        time.sleep(DELAY)
    return rows


def _image(images) -> str:
    """PC 용을 먼저. 상대경로라 브랜드 사이트 호스트를 붙인다."""
    rows = images or []
    pick = next((x for x in rows if (x or {}).get("deviceType") == "PC"), None)
    pick = pick or (rows[0] if rows else None)
    url = ((pick or {}).get("imageUrl") or "").lstrip("/")
    return f"{SITE}/{url}" if url else ""


def _limited(end: str) -> tuple:
    """(판매 종료일이 지났나, 기간 한정 라벨).

    API 가 `endDate` 를 준다. 상시 메뉴는 `9999-12-31 23:59:59` 이고, 기간
    한정 메뉴만 진짜 날짜가 들어온다(2026-10-08 실측: 제일제면소 가을 신메뉴
    3건이 2026-11-26·11-27). 빕스 어댑터는 이 필드를 안 읽는데, 안 읽으면
    **끝난 메뉴가 계속 올라온다** — 게다가 기간 한정 메뉴는 startDate 가
    최근이라 60일 창에 걸려 '신상'으로 뜬다. 그래서 여기서 둘 다 처리한다.
      · 종료일이 지났으면 버린다.
      · 상시(9999)가 아니면 `기간 한정` 라벨을 붙인다(파이브가이즈와 같은 말).
    """
    d = (end or "")[:10]
    if not d or d.startswith("9999"):
        return False, []
    return d < date.today().isoformat(), ["기간 한정"]


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()

    with base.client(headers={"Referer": SITE + "/",
                              "Accept": "application/json"}) as c:
        cats = _pages(c, f"/menus/{BRAND_CODE}/category")
        if not cats:
            raise RuntimeError(
                f"{API}/menus/{BRAND_CODE}/category: 카테고리 0건 — "
                f"2026-10-08 실측은 7칸이었다. 브랜드 코드가 바뀌었는지 확인하라")

        if len(cats) < MIN_CATES:
            raise RuntimeError(
                f"{BRAND}: 카테고리가 {len(cats)}칸이다 — 2026-10-08 실측은 "
                f"{MIN_CATES}칸(DESSERT/STEAK/PIZZA/RISOTTO&GNOCCHI/PASTA/"
                f"ANTIPASTI/SALAD&SOUP)이었다. 페이징이 잘렸는지 확인하라")

        live = [x for x in cats if (x.get("type") or "") not in SKIP_TYPES]
        if not live:
            raise RuntimeError(
                f"{BRAND}: 상품이 들어 있는 카테고리가 0칸이다 — type 값이 바뀌었다. "
                f"받은 값: {sorted({(x.get('type') or '') for x in cats})}")

        for cat in live:
            time.sleep(DELAY)
            for row in _pages(c, f"/menus/{BRAND_CODE}/{cat['idx']}"):
                name = " ".join((row.get("koreanMenuName") or "").split())
                if not name:
                    continue
                tag = (row.get("tag") or "").upper()
                over, labels = _limited(row.get("endDate") or "")
                if over:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    name_en=" ".join((row.get("englishMenuName") or "").split()),
                    desc=" ".join((row.get("description") or "").split()),
                    image=_image(row.get("images")),
                    labels=labels,
                    category=" ".join((cat.get("categoryName") or "").split()),
                    # 노출 시작일. 41건 중 36건이 2025-11-14 한 날에 몰린 사이트
                    # 오픈 일괄 입력이라 released_at 에 넣지 않는다(docstring).
                    uploaded_at=(row.get("startDate") or "")[:10],
                    # ⚠️ 빕스와 다르다. 이 브랜드는 tag 를 아예 안 써서(0/41)
                    #    NONE 을 False 로 읽으면 통째로 화면에서 사라진다.
                    #    '안 붙였다' 가 아니라 '모른다' 다.
                    is_new=True if tag == "NEW" else None,
                    url=SITE + "/menu",
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

    if len(items) < MIN_ITEMS:
        raise RuntimeError(
            f"{BRAND}: 상품 {len(items)}건 — 2026-10-08 실측은 41건이었다. "
            f"'koreanMenuName' 필드명이 바뀌었거나 totalPages 를 덜 돌았는지 "
            f"확인하라 (돈 칸: {[x.get('categoryName') for x in live]})")

    dated = sum(1 for i in items if i.uploaded_at)
    if dated < len(items) * 0.9:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 날짜를 {dated}건밖에 못 읽었다 — "
            f"'startDate' 가 비었다. 이 브랜드는 NEW 배지가 0건이라 날짜가 "
            f"유일한 신제품 신호다. 날짜가 없으면 전건이 화면에서 사라진다")

    # 🔴 이 브랜드의 유일한 신호가 날짜라서, 사이트를 다시 열며 startDate 를
    #    일괄 갱신하면 메뉴판 전체가 신상이 된다. rules.untrust_bulk_dates()
    #    가 1차 방어지만 어댑터에서도 바닥을 둔다.
    cutoff = (date.today() - timedelta(days=WINDOW)).isoformat()
    fresh = sum(1 for i in items if i.uploaded_at and i.uploaded_at >= cutoff)
    if fresh > len(items) * FRESH_MAX_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 {fresh}건의 startDate 가 최근 {WINDOW}일 "
            f"안이다(기대 {FRESH_MAX_RATIO:.0%} 이하, 2026-10-08 실측 3/41=7.3%). "
            f"사이트 개편으로 날짜가 일괄 갱신됐는지 확인하라 — 그대로 두면 "
            f"메뉴판 전체가 신상으로 올라간다")
    return items
