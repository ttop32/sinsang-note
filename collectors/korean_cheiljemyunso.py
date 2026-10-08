"""제일제면소 — CJ푸드빌 한식 면요리. 빕스와 **같은 공용 API** 를 쓴다.

`collectors/western_vips.py` 가 찾아 둔 CJ푸드빌 브랜드 공용 API 의 세 번째
브랜드다. 청크의 브랜드 enum `{VIPS, THEPLACE, CHEILJEMYUNSO, OLIPEPE}` 중
`CHEILJEMYUNSO` 다.

  GET https://brand-api.ivips.co.kr/menus/CHEILJEMYUNSO/category?page=0&size=100
  GET https://brand-api.ivips.co.kr/menus/CHEILJEMYUNSO/<categoryIdx>?page=N&size=100

⚠️ `page`·`size` 를 빼면 **400** 이다(`MSG_FO_00014`).
⚠️ `size=100` 을 줘도 서버가 무시하고 한 쪽에 10건만 준다. `totalPages` 를
   보고 끝까지 돌아야 22건이 다 나온다.

사이트는 `https://www.cheiljemyunso.co.kr` 이고 **`?ssoLoginYN=N` 을 붙여야**
셸(218B, CJ ONE SSO 리다이렉트) 대신 실제 페이지(23,107B)가 온다. 빕스와
같은 함정이다.

robots: 200 / 976B. 빕스와 같은 템플릿 — `User-agent: * / Disallow: /` 에
        Googlebot·NaverBot·Daumoa 만 `Allow`. **2026-10-02 운영자가 CJ푸드빌
        robots 무시를 승인**했고(빕스), 2026-10-08 지시로 같은 사이트군의
        나머지 브랜드를 연다. **UA 위장은 하지 않는다.**

## 카테고리 — 4칸 (2026-10-08 실측)

```
idx=24  가을 신메뉴   type=NORMAL   3건   ★ 브랜드가 직접 '신메뉴' 라고 쓴 칸
idx= 4  일품요리     type=NORMAL   9건
idx= 3  면/밥        type=NORMAL   6건
idx= 2  도시락 주문   type=LUNCH    4건
```
⚠️ **`LUNCH` 를 빼면 안 된다.** 빕스의 `SKIP_TYPES`(SALAD/DELIVERY/ALLERGY)
   는 '상품이 안 들어 있는 칸' 목록이다. `LUNCH` 는 다르다 — 도시락 4종이
   실제 상품으로 들어 있다(제일 명가/돈까스/모둠 도시락·수제 주먹밥 도시락).
   그래서 `SKIP_TYPES` 는 빕스 것 그대로 두고 `LUNCH` 는 더하지 않는다.

상품 **22건**.

## 신제품 신호 — `tag`. **22건 중 NEW 3건 (13.6%)**

```
tag=NEW   3건  가을 산해진미 한상 · 얼큰 버섯 소고기 전골 · 낙지 한 마리 해물 칼국수
tag=BEST  3건  해물 미나리전 · 얼큰 샤브 칼국수 · 샤브 칼국수
tag=NONE 16건
```
⚠️ **`tag` 가 있다고 세면 안 된다.** `BEST` 가 3건 섞여 있다. 값이 `NEW`
   인지 본다(얌샘김밥 `div.prBadge` 사고와 같은 자리).

배지 3건은 `가을 신메뉴` 칸의 3건과 **정확히 일치**하고, 셋 다 `startDate`
가 `2026-09-08` 이다. 배지와 날짜가 서로를 받쳐 준다.

## 날짜 — `startDate`. **`released_at` 이 아니라 `uploaded_at`**

```
2025-11-13   9건 (41%)  ← 사이트 오픈 일괄 입력
2026-09-08   3건        ← 가을 신메뉴 3종. NEW 배지와 일치
2025-12-23   3건
2026-06-17 / 2026-03-18 / 2026-03-03 / 2025-11-17 / 2025-11-18 /
2025-11-14 / 2025-11-11  각 1건
```
9건이 하루에 몰려 있다(빕스는 11/14건이 2025-11-13 — **같은 날이다.**
세 브랜드가 한꺼번에 사이트를 열었다). 일괄 입력이라 **`uploaded_at` 에만
넣는다**(`rules.untrust_bulk_dates()` 가 보는 자리). 브랜드가 "출시일"
이라고 말한 값이 아니므로 `released_at` 은 비운다.

⚠️ 9건은 `BULK_MIN=20` 에 못 미쳐 `untrust_bulk_dates()` 가 안 지운다.
   그래도 11개월 전이라 60일 창 밖이고, `is_new` 도 `False` 라 올라오지
   않는다. 지금은 안전하지만 **사이트를 다시 열며 날짜를 일괄 갱신하면**
   메뉴판 전체가 신상이 된다 — 아래 `FRESH_MAX_RATIO` 가드가 그걸 막는다.

## 기간 한정 — `endDate` 를 읽는다 (빕스 어댑터엔 없는 처리)

상시 메뉴는 `endDate` 가 `9999-12-31 23:59:59` 고, 기간 한정 메뉴만 진짜
날짜가 온다. 2026-10-08 실측 — 22건 중 3건(가을 신메뉴 3종)이 2026-11-26·
11-27 이다. 안 읽으면 **끝난 메뉴가 계속 올라온다.** 게다가 기간 한정은
`startDate` 가 최근이라 60일 창에 그대로 걸린다 — 가장 신상으로 보이는
자리라 가장 먼저 썩는다. → 종료일이 지나면 버리고, 상시가 아니면
`기간 한정` 라벨을 붙인다(파이브가이즈가 쓰는 말과 같게).
`displayStatus` 는 22건 전부 `Y` 라 지금은 거를 게 없다.

## 이미지

`imageUrl` 이 `images/CHEILJEMYUNSO/menus/<uuid>-<epoch ms>.jpg` 상대경로다.
CJ푸드빌 브랜드 사이트 아무 호스트나 같은 바이트를 주는데(실측 3곳 전부
200, 같은 길이) **자기 브랜드 호스트**를 붙인다. `Content-Type` 이
`application/octet-stream` 으로 오지만 `rules._is_image()` 는 매직 바이트로
보므로 지워지지 않는다.

## 범위 밖

술은 API 22건에 없다. 주류 칸 자체가 없다.

## 🔴 올리페페(OLIPEPE)는 **열리지 않는다** — 같은 지시 범위였다

같은 API 로 붙었는데 **카테고리가 `totalElements=0 / totalPages=0`** 이다.
사이트(`www.olipepe.co.kr/?ssoLoginYN=N`, 23,770B, "올리페페 | 이탈리안
비스트로 | CJ푸드빌 공식 사이트")는 살아 있는데 **`/menu` 가 404(14,629B)**
다. robots.txt 에는 `/menu` 가 `Allow` 로 적혀 있지만 그건 CJ푸드빌 브랜드
사이트에 똑같이 복사된 템플릿이라 그 경로가 실재한다는 근거가 못 된다
(200·Allow 함정). → **어댑터를 만들지 않았다.** 메뉴가 올라오면
이 파일을 복사해 `BRAND_CODE` 만 바꾸면 된다.

등록 제안: 유형 `FRANCHISE`, 세부분류 `한식`
          SITES `https://www.cheiljemyunso.co.kr/menu`
"""
import time
from datetime import date, timedelta

from . import base
from .base import Item

BRAND = "제일제면소"
SITE = "https://www.cheiljemyunso.co.kr"
API = "https://brand-api.ivips.co.kr"
BRAND_CODE = "CHEILJEMYUNSO"
DELAY = 1.5
MAX_PAGES = 15   # 폭주 방지. 현재 가장 큰 칸(일품요리 9건)이 1페이지다.
MIN_CATES = 4    # 2026-10-08 실측 4칸
MIN_ITEMS = 15   # 2026-10-08 실측 22건

# ⚠️ 빕스 것 그대로다. `LUNCH`(도시락 주문)는 **넣지 않는다** — 거긴 상품이
#    실제로 들어 있다(docstring §카테고리).
SKIP_TYPES = {"SALAD", "DELIVERY", "ALLERGY"}

# 60일 창 안에 드는 상품이 이 비율을 넘으면 일괄 입력이 새로 들어온 것으로 본다.
# 2026-10-08 실측 3/22 = 13.6%.
FRESH_MAX_RATIO = 0.45
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
                f"2026-10-08 실측은 4칸이었다. 브랜드 코드가 바뀌었는지 확인하라 "
                f"(같은 API 의 OLIPEPE 가 정확히 이 모양으로 0건이다)")

        if len(cats) < MIN_CATES:
            raise RuntimeError(
                f"{BRAND}: 카테고리가 {len(cats)}칸이다 — 2026-10-08 실측은 "
                f"{MIN_CATES}칸(가을 신메뉴/일품요리/면·밥/도시락 주문)이었다. "
                f"페이징이 잘렸는지 확인하라")

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
                # ⚠️ tag 가 있다고 세면 안 된다. BEST 가 3건 섞여 있다.
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
                    # 노출 시작일이다. 22건 중 9건이 2025-11-13 한 날에 몰린
                    # 사이트 오픈 일괄 입력이라 released_at 에 넣지 않는다.
                    uploaded_at=(row.get("startDate") or "")[:10],
                    is_new=(tag == "NEW"),
                    url=SITE + "/menu",
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

    if len(items) < MIN_ITEMS:
        raise RuntimeError(
            f"{BRAND}: 상품 {len(items)}건 — 2026-10-08 실측은 22건이었다. "
            f"'koreanMenuName' 필드명이 바뀌었거나 totalPages 를 덜 돌았는지 "
            f"확인하라 (돈 칸: {[x.get('categoryName') for x in live]})")

    new_count = sum(1 for i in items if i.is_new)
    if new_count == len(items):
        raise RuntimeError(
            f"{BRAND}: {len(items)}건이 전부 tag=NEW 다 — 2026-10-08 실측은 "
            f"22건 중 3건(13.6%)이었다. 메뉴판이 통째로 신상으로 올라간다")

    dated = sum(1 for i in items if i.uploaded_at)
    if dated < len(items) * 0.9:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 날짜를 {dated}건밖에 못 읽었다 — "
            f"'startDate' 가 비었다. 날짜를 비우면 60일 창을 건너뛴다")

    # 일괄 9건은 BULK_MIN(20)에 못 미쳐 rules 쪽 방어가 안 걸린다. 사이트를
    # 다시 열며 날짜를 일괄 갱신하면 메뉴판 전체가 신상이 되므로 바닥을 둔다.
    cutoff = (date.today() - timedelta(days=WINDOW)).isoformat()
    fresh = sum(1 for i in items if i.uploaded_at and i.uploaded_at >= cutoff)
    if fresh > len(items) * FRESH_MAX_RATIO:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 {fresh}건의 startDate 가 최근 {WINDOW}일 "
            f"안이다(기대 {FRESH_MAX_RATIO:.0%} 이하, 2026-10-08 실측 3/22=13.6%). "
            f"사이트 개편으로 날짜가 일괄 갱신됐는지 확인하라")
    return items
