"""타래퀸 — Strapi API 의 `tags` 에서 **`new` 라벨이 붙은 상품만** 받는다.

공정위 `아이스크림/빙수`(K1) 가맹점 수 **17개**(2024년 말, 가맹본부 2000에프앤비(주)).
주력이 '타래 빙수'(실 모양으로 뽑은 눈꽃빙수)라 `brand_sub` 는 `빙수` 다.
타래 아이스크림·타래빵·커피도 같이 판다.

## HTML 로는 못 읽는다 — **JS 가 API 에서 받아 그린다**

  GET https://www.taraequeen.com/menu   200 / 51,629B
    서버가 주는 HTML 의 메뉴 자리는 **"준비된 메뉴가 없습니다"** 다.
    상품 이름은 schema.org JSON-LD(`"@type":"MenuItem"`)로 58개가 들어 있는데
    **배지(new/season/signature/best)는 거기 없다.** 이름만 긁으면 전부
    '신상' 으로 올리게 된다 — 그래서 JSON-LD 는 안 쓴다.

브라우저로 열어 `performance.getEntriesByType('resource')` 를 찍어 보니
(JS 렌더 사이트에 maker_shinsegaefood 가 쓴 그 방법) XHR 하나가 나왔다:

  GET https://taraequeen-production.up.railway.app/api/products
        ?filters[category][$eq]=tarae_bingsu&populate=*
        &pagination[page]=1&pagination[pageSize]=8&sort[0]=order:asc …

필터를 걷어내고 한 번에 받으면 전건이 온다:

  GET https://taraequeen-production.up.railway.app/api/products
        ?populate=*&pagination[pageSize]=100            200 / 116,619B
    {"data":[{"id":221,"title":"초코쉘 요거트 타래 아이스크림",
              "description":"요거트 타래 아이스크림 + 초코쉘",
              "category":"tarae_icecream","productId":"ice_chocoshell",
              "createdAt":"2026-02-20T04:32:10.027Z","isSignature":false,
              "tags":[], "imageUrl":{"url":"https://taraequeen-assets.s3…jpg",
                                     "formats":{"large":{"url":…}}}}, …],
     "meta":{"pagination":{"page":1,"pageSize":100,"pageCount":1,"total":58}}}
  Strapi v5 다. 한 장에 58건이 다 온다(pageCount=1) → 페이지네이션 불필요.

## 신상 판정 — `tags[].label == "new"` **딱 하나만** 본다

⚠️ **여기가 설빙이 틀린 바로 그 자리다.** `tags` 에는 네 가지 라벨이 섞여 온다:
```
new        1건   돼x바 타래 빙수      ← 이것만 신상이다
season     1건   생딸기 타래 빙수      (제철 메뉴. 신상 아님)
signature  1건   팥 인절미 타래 빙수   (시그니처. 신상 아님)
best       1건   애플망고 타래 빙수    (인기 메뉴. 신상 아님)
```
배지가 '있다/없다'로 세면 4건이 되고, 그중 3건은 몇 년째 파는 간판 메뉴다.
설빙이 `span.flag` 의 **문구를 안 보고** 세는 바람에 2013년부터 팔던
인절미설빙을 신상으로 올린 사고가 정확히 이것이다(14 → 4건으로 정정).
**라벨 문자열을 `new` 로 못 박아 비교한다.**

비율(2026-10-02 실측): 전체 **58건 중 `new` 1건 = 1.7%**.
(분류별: tarae_bingsu 18 · beverage 15 · tarae_icecream 13 · coffee 7 · tarae_bread 5)
퀴즈노스(66건 전부 NEW)와 정반대로 아주 인색한 배지라 믿을 만하다.
0% 거나 과반이 되면 `fetch()` 끝에서 터뜨린다.

## 날짜는 **쓰지 않는다** — 일괄 등록이다

`createdAt` 분포가 **2026-02-19(15건) · 2026-02-20(42건) · 2026-02-21(1건)** 이다.
사흘에 58건이 몰려 있다 = 사이트를 새로 만들면서 한꺼번에 집어넣은 값이다.
`updatedAt`·`publishedAt` 도 같은 날짜다. 컴포즈 149건이 하루에 몰린 것과 같은
모양이라 **출시일로 쓸 수 없다.** `released_at`·`uploaded_at` 을 비워 둔다.
지어내지 않는다 — 이 브랜드는 `is_new` 와 `first_seen` 으로만 판정된다.

robots: https://www.taraequeen.com/robots.txt → 200 / 293B.
        `User-Agent: * / Allow: / / Disallow: /api/ …` — 그런데 **그 `/api/` 는
        이 Next.js 호스트의 경로고, 우리가 받는 건 다른 호스트**다.
        https://taraequeen-production.up.railway.app/robots.txt → 200 / 121B,
        내용이 전부 주석이라 **규칙이 하나도 없다 = 제한 없음**이다.
        `Crawl-delay` 선언 없음.
약관:   확인하지 않았다.
"""
from . import base
from .base import Item

BRAND = "타래퀸"
SITE = "https://www.taraequeen.com"
MENU = SITE + "/menu"
API = ("https://taraequeen-production.up.railway.app/api/products"
       "?populate=*&pagination[pageSize]=100")
DELAY = 2.2

# ⚠️ 이 문자열만 신상이다. season·signature·best 를 같이 세면 간판 메뉴가 올라간다.
NEW_LABEL = "new"
MAX_NEW_RATIO = 0.5


def _image(row: dict) -> str:
    """imageUrl.formats.large → medium → 원본 순으로 고른다. https 만 쓴다."""
    img = row.get("imageUrl") or {}
    if not isinstance(img, dict):
        return ""
    fmts = img.get("formats") or {}
    for key in ("large", "medium", "small", "thumbnail"):
        u = ((fmts.get(key) or {}).get("url") or "").strip()
        if u.startswith("https://"):
            return u
    u = (img.get("url") or "").strip()
    return u if u.startswith("https://") else ""


def _labels(row: dict) -> list[str]:
    out = []
    for t in (row.get("tags") or []):
        if isinstance(t, dict):
            lab = (t.get("label") or "").strip().lower()
            if lab:
                out.append(lab)
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(API))
        r.raise_for_status()
        data = r.json()
        rows = data.get("data") or []

        if not rows:
            raise ValueError(
                f"타래퀸 상품 API 가 빈 목록을 돌려줬다. {API} → "
                f"{len(r.content)}B / meta={data.get('meta')} — "
                f"엔드포인트가 바뀌었는지 확인하라")

        # 한 장에 다 와야 한다. pageCount 가 늘면 뒷장을 놓친다.
        pages = ((data.get("meta") or {}).get("pagination") or {}).get("pageCount")
        if pages and int(pages) > 1:
            raise ValueError(
                f"타래퀸 상품이 {pages}장으로 늘었다(pageSize=100). "
                f"페이지네이션을 추가해야 한다")

        seen_labels = set()
        for row in rows:
            seen_labels.update(_labels(row))

        # ── 배지 비율 가드 ────────────────────────────────────────────
        # 배지는 '있다'가 아니라 '어떤 문구가 전체의 몇 %냐'로 믿는다.
        # 2026-10-02 실측 58건 중 new 1건(1.7%). 0% 면 라벨 문자열이 바뀐
        # 것이고, 과반이면 배지가 장식으로 바뀐 것이다.
        newish = [row for row in rows if NEW_LABEL in _labels(row)]
        if not newish:
            raise ValueError(
                f"타래퀸 '{NEW_LABEL}' 라벨이 {len(rows)}건 중 0건이다. "
                f"읽힌 라벨={sorted(seen_labels)} — tags[].label 문구가 "
                f"바뀌었는지 확인하라(팔도 선례)")
        if len(newish) > len(rows) * MAX_NEW_RATIO:
            raise ValueError(
                f"타래퀸 '{NEW_LABEL}' 라벨이 {len(rows)}건 중 {len(newish)}건"
                f"({len(newish) / len(rows):.0%})이다. 과반이 신상일 수는 없다 — "
                f"배지가 장식으로 바뀌었는지 확인하라(퀴즈노스 선례)")

        for row in newish:
            name = " ".join((row.get("title") or "").split())
            if not name:
                continue
            it = Item(
                brand=BRAND,
                name=name,
                desc=" ".join((row.get("description") or "").split()),
                image=_image(row),
                category=(row.get("category") or ""),
                # createdAt 은 사흘에 58건이 몰린 일괄 등록값이라 안 쓴다.
                is_new=True,
                url=MENU,
            )
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)
    return items
