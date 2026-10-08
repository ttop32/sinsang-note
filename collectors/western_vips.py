"""빕스(VIPS).

`BRAND-CANDIDATES.md` 가 **"우리를 명시적으로 막는 유일한 브랜드"** 로 적어둔 곳이다.

```
User-agent: * / Disallow: /     (Googlebot·NaverBot 만 허용)
```

**2026-10-02 운영자가 robots 무시를 승인**해서 다시 연다.

그리고 **사이트가 그 사이 통째로 바뀌었다.** 1차 기록의 "홈이 CJ ONE SSO 로 리다이렉트"
는 더 이상 맞지 않는다. 지금은 Next.js App Router 고, 메뉴는 **인증 없이 열린 JSON API**
가 준다. 2026-10-08 실측.

## 경로를 찾은 방법 (다음 사람이 헤매지 않게)

1. `https://www.ivips.co.kr/` 는 **196바이트짜리 `location.replace()` 스크립트**다.
   `?ssoLoginYN=N` 을 붙여야 실제 페이지(22KB)가 온다. 이걸 모르면 "빈 셸"로 오판한다.
2. 그 페이지에 `__NEXT_DATA__` 는 없다. RSC 스트림(`self.__next_f.push`)뿐이고
   **메뉴 데이터는 거기 없다** — 클라이언트가 따로 받아 온다.
3. API 주소는 청크 `_next/static/chunks/574-*.js` 안에 있다.
   `https://brand-api.ivips.co.kr` + `getMenuCategoryList: /menus/{brand}/category`
   / `getMenuList: /menus/{brand}/{categoryIdx}`.

  GET https://brand-api.ivips.co.kr/menus/VIPS/category?page=0&size=100
  GET https://brand-api.ivips.co.kr/menus/VIPS/<categoryIdx>?page=N&size=100

⚠️ **`page`·`size` 를 빼면 400 이다**(`MSG_FO_00014 요청 값을 확인해주세요`). 200 이
아니라 400 이라 금방 드러나긴 한다.
⚠️ **`size` 를 100 으로 줘도 한 쪽에 10건만 온다.** 서버가 무시한다. `totalPages` 를
보고 끝까지 돌아야 14건이 다 나온다(처음에 10건만 받고 끝낼 뻔했다).
그래서 `_pages()` 가 **카테고리 목록에도 똑같이** `totalPages` 를 따라간다. 카테고리
쪽은 2026-10-08 현재 `totalElements=4 / totalPages=1` 이라 한 번에 다 오지만, 칸이
늘면 조용히 잘릴 자리라 같은 함수로 돈다.

이 API 는 CJ푸드빌 공용이다 — 청크의 브랜드 enum 이
`{VIPS, THEPLACE, CHEILJEMYUNSO, OLIPEPE}` 다. **뚜레쥬르는 여기 없다**(자체 EUC-KR
ASP 사이트를 그대로 쓴다). 그래서 `bakery_tlj` 와 상품이 겹치지 않는다.
나머지 세 브랜드(더플레이스·제일제면소·올리페페)는 이번 지시 범위 밖이라 건드리지 않았다.

## 카테고리 — 메뉴가 실제로 들어 있는 건 하나뿐이다

```
idx=16 알레르기 정보  type=ALLERGY
idx=15 온라인몰      type=DELIVERY   → 목록 0건
idx= 6 MAIN         type=NORMAL     → 14건  ★
idx= 1 샐러드바      type=SALAD      → 목록 0건
```

`SALAD`·`DELIVERY`·`ALLERGY` 는 **프런트 코드도 목록 질의를 걸지 않는다**(청크에
`enabled: n.type !== SALAD && n.type !== DELIVERY && n.type !== ALLERGY`). 빕스의
간판인 샐러드바가 통째로 빠지지만 **거기엔 상품 데이터가 없다** — 이미지 배너뿐이다.
그래서 `type == "NORMAL"` 만 돈다.

**14건이 전부다. 카테고리를 덜 돈 게 아니다.** 근거를 적어 둔다 — 카테고리 응답이
`totalElements=4 / totalPages=1` 이고(위 네 칸이 그 넷이다), `SALAD`·`DELIVERY` 도
실제로 받아 봤는데 둘 다 `totalElements=0` 이었다. 디저트·사이드·음료 같은 칸은
**애초에 API 에 없다**(음료는 `MAIN` 안의 `에이드(애플망고/자몽)` 한 줄이 전부다).
빕스는 메인 스테이크만 개별 상품으로 올리고 나머지는 샐러드바 이미지로 때운다.
수가 작아서 다음에 조용히 0~3건이 돼도 급감 가드에 안 걸리므로 **아래 `MIN_ITEMS`
바닥 가드**를 따로 뒀다.

브랜드 파라미터는 청크의 enum 이 전부다 — `{VIPS, THEPLACE, CHEILJEMYUNSO, OLIPEPE}`.
계절 브랜드나 숨은 코드는 없고, 뚜레쥬르도 없다.

## 신제품 신호 — `tag` 필드. **14건 중 NEW 1건 (7.1%)**

```
tag=NEW   1건  비스큐 랍스터&채끝 스테이크
tag=BEST  2건  안심&채끝 스테이크 · 스테이크 플래터
tag=NONE 11건
```

⚠️ **`tag` 가 있다고 세면 안 된다.** 얌샘김밥(`div.prBadge` 에 BEST 19·HOT 8·COOL 6)
이 정확히 그 사고였다. 여기도 `BEST` 가 섞여 있으니 **값이 `NEW` 인지** 본다.

⚠️ **그 NEW 1건은 `startDate` 가 2025-11-13 이다 — 11개월 전이다.** 배지를 켜 두고
안 끄는 전형이고, 설빙이 2013년 메뉴를 신상으로 올린 것과 같은 모양이다. 날짜가 함께
오므로 `collect` 의 60일 창이 걸러 준다 — **그래서 날짜를 비우면 안 된다.**

## 날짜 — `startDate`. **`released_at` 이 아니다**

`startDate`(노출 시작일)·`registerDate`(등록 시각)·`updateDate` 셋이 온다. 그런데
**14건 중 11건이 `2025-11-13` 한 날에 몰려 있다**(그날 `registerDate` 시각이
17:24~19:49 로 줄줄이다). 사이트를 새로 열면서 메뉴를 한꺼번에 입력한 것이지
그날 11종이 출시된 게 아니다. 파리바게뜨 312장·아웃백 `20250422` 28건과 같은 함정이라
**`uploaded_at` 에만 넣는다**(`rules.untrust_bulk_dates()` 가 보는 자리). 브랜드가
"출시일"이라고 말한 값이 아니므로 `released_at` 은 비운다.

```
2025-11-13  11건   ← 사이트 오픈 일괄 입력
2026-04-06   1건   에이드(애플망고/자몽)
2025-10-31   1건   포터하우스 스테이크
```

## 이미지

`imageUrl` 이 `images/VIPS/menus/<uuid>-<epoch ms>.png` 상대경로로 온다.
청크가 쓰는 앞머리는 두 개인데 **S3 쪽은 403 이다**:

  https://prod-foodville-brand-assets.s3.ap-northeast-2.amazonaws.com/… → 403
  https://www.ivips.co.kr/…                                            → 200 ✔

`images[]` 는 `deviceType` 이 `PC`/`MO` 로 나뉜다. PC 를 먼저 찾고 없으면 첫 장을 쓴다.

술은 `MAIN` 14건에 없다(스테이크·랍스터·에이드). `BEVERAGES` 류 칸 자체가 없다.

등록 제안: 유형 `FRANCHISE`, 세부분류 `양식`.
"""
import time

from . import base
from .base import Item

BRAND = "빕스"
SITE = "https://www.ivips.co.kr"
API = "https://brand-api.ivips.co.kr"
BRAND_CODE = "VIPS"
DELAY = 1.5
MAX_PAGES = 10   # 폭주 방지. 현재 MAIN 이 2페이지(14건)다.
MIN_CATES = 4    # 2026-10-08 실측. 칸이 줄면 API 가 바뀐 것이다
MIN_ITEMS = 10   # 2026-10-08 실측 14건. 메뉴가 작아 급감 가드가 안 걸린다

# 프런트가 목록 질의를 아예 걸지 않는 칸들. 실제로 받아 봐도 0건이다.
SKIP_TYPES = {"SALAD", "DELIVERY", "ALLERGY"}


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
    """PC 용을 먼저. S3 앞머리는 403 이라 사이트 호스트를 붙인다."""
    rows = images or []
    pick = next((x for x in rows if (x or {}).get("deviceType") == "PC"), None)
    pick = pick or (rows[0] if rows else None)
    url = ((pick or {}).get("imageUrl") or "").lstrip("/")
    return f"{SITE}/{url}" if url else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()

    with base.client(headers={"Referer": SITE + "/",
                              "Accept": "application/json"}) as c:
        cats = _pages(c, f"/menus/{BRAND_CODE}/category")
        if not cats:
            raise RuntimeError(
                f"{API}/menus/{BRAND_CODE}/category: 카테고리 0건 — "
                f"2026-10-08 실측은 4칸이었다")

        if len(cats) < MIN_CATES:
            raise RuntimeError(
                f"{BRAND}: 카테고리가 {len(cats)}칸이다 — 2026-10-08 실측은 4칸"
                f"(MAIN/샐러드바/온라인몰/알레르기 정보)이었다. 페이징이 잘렸는지 "
                f"확인하라")

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
                # ⚠️ tag 가 있다고 세면 안 된다. BEST 가 2건 섞여 있다.
                tag = (row.get("tag") or "").upper()
                it = Item(
                    brand=BRAND,
                    name=name,
                    name_en=" ".join((row.get("englishMenuName") or "").split()),
                    desc=" ".join((row.get("description") or "").split()),
                    image=_image(row.get("images")),
                    category=" ".join((cat.get("categoryName") or "").split()),
                    # 노출 시작일이다. 14건 중 11건이 2025-11-13 한 날에 몰린
                    # 사이트 오픈 일괄 입력이라 released_at 에 넣지 않는다.
                    uploaded_at=(row.get("startDate") or "")[:10],
                    is_new=(tag == "NEW"),
                    url=SITE + "/menu",
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

    # 14건짜리 메뉴라 0 건이 아니어도 조용히 반 토막 날 수 있다. 바닥을 둔다.
    if len(items) < MIN_ITEMS:
        raise RuntimeError(
            f"{BRAND}: 상품 {len(items)}건 — 2026-10-08 실측은 MAIN 칸 14건이었다. "
            f"'koreanMenuName' 필드명이 바뀌었거나 totalPages 를 덜 돌았는지 확인하라 "
            f"(돈 칸: {[x.get('categoryName') for x in live]})")
    new_count = sum(1 for i in items if i.is_new)
    if new_count == len(items):
        raise RuntimeError(
            f"{BRAND}: {len(items)}건이 전부 tag=NEW 다 — 2026-10-08 실측은 "
            f"14건 중 1건(7.1%)이었다. 메뉴판이 통째로 신상으로 올라간다")
    dated = sum(1 for i in items if i.uploaded_at)
    if dated < len(items) * 0.9:
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 중 날짜를 {dated}건밖에 못 읽었다 — "
            f"'startDate' 가 비었다. 날짜를 비우면 60일 창을 건너뛴다")
    return items
