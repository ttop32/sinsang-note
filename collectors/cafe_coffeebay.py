"""커피베이(COFFEEBAY).

도메인이 둘로 갈려 있다. 2026-10-02 실측 —
  coffeebay.co.kr   443 연결거부. http 는 200 인데 본문이 **521바이트**다.
                    열어 보면 `<FRAMESET>` 한 줄이고 프레임 안이
                    `http://blog.naver.com/ykkang380` — 커피베이와 무관한
                    **개인 네이버 블로그**다. 옛 도메인이 남의 손에 넘어갔다.
  **coffeebay.com** 이 현재 본사 사이트다(Vercel). 푸터가
                    '(주)커피베이 | 대표이사 김명원 | 119-86-23354'.
  ⚠️ 힌트로 받은 coffeebanhada.com('커피에반하다', 같은 가맹본부)은 **다른
     브랜드의 다른 사이트**다(PHP). 구조가 전혀 안 겹쳐서 쓸모가 없었다.

www.coffeebay.com 은 Next.js **App Router**(turbopack) 라 `/menu/coffeebay` 를
그냥 받으면 본문이 '로딩중...' 이다. 상품이 HTML 에 0건이다.
번들 13개(합계 약 2.0MB)를 훑어서 내부 API 를 찾았다.
  - `c017d08e9d5d8012.js` 에 `brandId:27` 과 S3 배지 주소가 박혀 있다.
  - `e1b3949a95ecdbce.js`(1.4MB) 에 `getHomepageMenus` → `` `${e}/homepage-menus` ``,
    `useHomepageMenus({apiUrl, brandId}, {category, subcategory, keyword,
    labelType, status, page, size})`.
  - apiUrl 은 `ac9a4f7ea572dc58.js`·`c017d08e9d5d8012.js` 의
    **`https://brain.stg.togi.sh`** 다.
⚠️ 청크를 '문자열이 든 첫 파일' 로 고르면 틀린다(블루샥 선례). 여기서는
   `baseURL` 이 아니라 호스트 문자열이 들어간 청크가 둘이었고, 엔드포인트는
   그중 **큰 쪽**(1.4MB)에만 있었다. 그래서 어댑터는 번들을 안 읽고 위에서
   확정한 주소를 상수로 박는다 — 번들 해시는 배포마다 바뀌고, 매번 2MB 를
   받아 정규식을 돌리는 건 이 한 줄을 얻자고 치르기엔 비싸다.
   주소가 바뀌면 fetch() 가 RuntimeError 로 죽으니 조용히 틀리지는 않는다.

API 는 인증·Referer·토큰 없이 그냥 열린다. 페이지네이션이 Spring Page 모양
(`content` + `pageable.totalElements`)이고 size=1000 이면 한 번에 다 온다.

  GET https://brain.stg.togi.sh/homepage-menus?brandId=27&size=1000&status=VISIBLE

⚠️ `status` 를 안 주면 **비공개(HIDDEN) 238건이 섞여 온다**(전체 521건).
   화면에 없는 상품이고, 그중에 `new` 라벨이 5건 들어 있어서 그냥 받으면
   사이트에 뜨지도 않는 걸 신상이라고 올리게 된다. **반드시 VISIBLE 만 받는다.**

신제품 신호(2026-10-02 실측):
  - 각 상품에 `label` 이 있고 값이 `{type, image}` 한 개다. type 은 번들의
    `LABEL_TYPES`·`labelTypeOptions` 에 정의된 다섯 중 하나 —
    **없음 / new / best / season / signature**. 관리자 화면에서 고르는 값이다.
  - VISIBLE 283건 기준 분포: **new 19(6.7%) / season 35 / signature 11 /
    best 10 / 없음 208**. 라벨이 살아 움직인다는 증거가 분포 자체에 있다 —
    퀴즈노스(66건 전부 NEW)·롯데리아(BEST 에도 '신메뉴')처럼 한 값으로
    쏠려 있지 않고, `new` 가 가장 적다.
  - new 19건의 내용도 맞다. 붕어빵·토스트·크림치즈·공주밤빵 같은 가을 라인과
    익스프레스 쉐이크/주스 신설분이다. 아메리카노·카페라떼는 라벨이 없다.
  - `season`(붕어빵 등)을 new 로 세지 않는다. 시즌은 매년 돌아오는 것이고
    신제품이 아니다(할리스 '시즌메뉴' 아이콘과 같은 취급).
  - 라벨이 `new` 가 아닌 것은 브랜드가 '신제품 아님' 이라고 말한 것으로 보고
    is_new=False 로 내보낸다. 라벨 필드가 실제로 관리되고 있어서다.

**날짜는 어디에도 없다.** 목록 응답에도, 단건 상세(`/homepage-menus/{id}`)에도
createdAt·releasedAt 류 필드가 한 개도 없다(필드는 id/brandId/name/englishName/
image/label/description/nutrition/category/subcategory/sortOrder/showMainPage/
status 13개가 전부다). 보도자료격인 `/homepage-events` 에는 날짜가 있지만
행사 글이지 상품이 아니다. released_at·uploaded_at 둘 다 **비운다.**

category 는 `커피베이` / `익스프레스` 두 간판이다(익스프레스는 소형 매장
라인). 둘 다 (주)커피베이 메뉴라 한 브랜드로 받고, 화면 분류는 subcategory
(커피·베이직라떼·베이커리·디저트·MD …)를 쓴다.

굿즈는 **adapter 에서 찍지 않는다.** MD subcategory 23건 중 8건이
스틱커피·더치커피·원두(Whole Bean)다. 탐앤탐스처럼 탭 통째로 nonfood 를
찍으면 커피를 굿즈 칸에 넣게 된다. 이름으로 보는 base.is_nonfood 에 맡기면
텀블러·머그는 잡히고 '데미타스잔 SET' 2건이 샌다 — 둘 다 라벨이 없어서
화면에 오를 일이 없으니 그 오차를 받는다.

상품 상세 주소가 없다(SPA 라우트에도 상품 단위 경로가 없다). Item.url 은
category 에 맞는 메뉴 탭으로 보낸다.

robots.txt 는 **404**(Next.js 404 페이지)다. API 쪽도 404 JSON 이다.
403 이 아니므로 RFC 9309 상 '규칙 명시 없음' 이다(매머드커피와 같은 처지).
"""
import time

from . import base
from .base import Item

BRAND = "커피베이"
SITE = "https://www.coffeebay.com"
API = "https://brain.stg.togi.sh/homepage-menus"
BRAND_ID = 27
PAGE_SIZE = 1000     # 전체 521건, VISIBLE 283건. 한 번에 받는다
DELAY = 2.0

NEW_LABEL = "new"                 # best/season/signature 는 신상이 아니다
VISIBLE = "VISIBLE"               # HIDDEN 238건을 걷어내는 유일한 장치
EXPRESS = "익스프레스"
MIN_ITEMS = 100                   # 이보다 적으면 API 가 바뀐 것이다

# category → 사람이 여는 메뉴 탭. 상품 단위 주소가 없어 이게 최선이다.
TAB = {EXPRESS: f"{SITE}/menu/express"}
DEFAULT_TAB = f"{SITE}/menu/coffeebay"


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(API, params={
            "brandId": BRAND_ID, "size": PAGE_SIZE, "status": VISIBLE}))
        r.raise_for_status()
        body = r.json()
        time.sleep(DELAY)

    rows = body.get("content") or []
    if len(rows) < MIN_ITEMS:
        raise RuntimeError(f"커피베이 {len(rows)}건 — API 응답이 바뀌었을 수 있다")

    # size 를 넘겨 받지 못한 경우를 드러낸다. 조용한 부분수집을 막는다.
    total = (body.get("pageable") or {}).get("totalElements")
    if total and total > len(rows):
        raise RuntimeError(f"커피베이 {len(rows)}/{total}건만 받았다 — 페이징이 필요하다")

    items: list[Item] = []
    seen: dict = {}
    for row in rows:
        name = _clean(row.get("name"))
        if not name or row.get("status") != VISIBLE:
            continue
        label = row.get("label") or {}
        category = _clean(row.get("category"))
        sub = _clean(row.get("subcategory"))
        it = Item(
            brand=BRAND,
            name=name,
            name_en=_clean(row.get("englishName")),
            desc=_clean(row.get("description")),
            image=_clean(row.get("image")),
            # 화면 분류는 간판(커피베이/익스프레스)이 아니라 메뉴 종류를 쓴다
            category=sub or category,
            is_new=label.get("type") == NEW_LABEL,
            url=TAB.get(category, DEFAULT_TAB),
        )
        # 같은 상품이 두 간판에 걸쳐 있다(공주밤빵 등 16건). 먼저 온 쪽을
        # 남기되 **라벨은 합친다** — 한쪽만 new 로 찍혀 있을 때 순서에 따라
        # 신상 표시가 사라지면 안 된다.
        if it.key in seen:
            if it.is_new:
                seen[it.key].is_new = True
            continue
        seen[it.key] = it
        items.append(it)

    new = sum(1 for i in items if i.is_new)
    # 배지가 전건에 붙어 있으면 그건 신호가 아니라 장식이다(퀴즈노스 66/66).
    if new > len(items) // 2:
        raise RuntimeError(f"커피베이 new {new}/{len(items)}건 — 라벨을 믿을 수 없다")
    return items
