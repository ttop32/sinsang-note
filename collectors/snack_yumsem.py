"""얌샘김밥.

도메인은 yumsem.com 이다(`yamsaem.co.kr` 은 NXDOMAIN — 로마자 표기를 추측하면
안 맞는다). 워드프레스 + Elementor 사이트인데 **메뉴가 글(post)로 관리된다.**
`yumsem-menu` 커스텀 포스트 타입이 show_in_rest 로 열려 있어 REST 로 전수가 온다.

  GET /wp-json/wp/v2/yumsem-menu?per_page=100&orderby=date&order=desc&_embed=…
      → X-WP-Total: 154, X-WP-TotalPages: 2

날짜와 배지를 **둘 다** 가져온다. REST 가 날짜를, 화면 2장이 배지를 준다.

## ⚠️ 배지는 REST 에 없다. 화면을 따로 받아야 한다

🔴 **처음엔 "화면의 NEW 배지가 등록일 상위 묶음과 일치하니 배지는 안 긁어도
된다"고 적고 날짜만 썼다. 검수에서 그 전제가 깨졌다.** 2026-10-02 실측 —
NEW 배지 8건 중 **`유부우동`(basic-27)은 등록일이 2022-08-16** 이다. 4년 전
상품인데 브랜드가 배지를 붙여 뒀다. 반대로 등록일 상위인 `전복통계란말이김밥`
(2026-04-22)에는 배지가 **없다**. 두 신호는 같은 답을 내지 않는다.

레포 규칙은 "`is_new=True` 는 브랜드가 신제품이라고 표시한 것만"이다.
**브랜드는 표시했는데 우리가 안 읽고 있었다.** 그래서 화면 2장을 더 받는다.

REST 쪽엔 배지가 없다는 것도 확인했다 — `menu_categories` 34개 term 을 전수로
받아 봐도 `NEW`·`신메뉴` 계열 term 이 0건이고, `acf` 는 전건 빈 배열이다.

### ⚠️ 배지 요소가 네 종류다. 존재만 세면 41건이 전부 신상이 된다

    <div class="elementor-element … prBadge …">
        <div class="elementor-widget-container">NEW</div>

2026-10-02 실측(화면 2장 합계) — `div.prBadge` **41개**:

    BEST 19 · NEW 8 · HOT 8 · COOL 6

`.prBadge` 가 있다고 세면 41건이 전부 신상이 된다. **안의 글자가 정확히
`NEW` 인 것만** 센다(다른 브랜드에서 `span.flag` 존재만 보고 세다가 10년 된
간판 메뉴가 신상으로 올라간 사고가 같은 날 있었다).

배지는 `.prBadge` 의 할아버지 칸 안에 있는 `a[href*="/yumsem-menu/"]` 로 상품에
붙인다. REST 의 `link` 와 같은 주소라 그대로 맞춰진다.

## ⚠️ 날짜는 `released_at` 이 아니라 `uploaded_at` 에 넣는다

CMS 등록일이라 `released_at` 에 넣고 싶어지는데 **그러면 안 된다.**
2026-10-02 실측 분포(수집 후 96건):

    2023-11-23  45건  ← 워드프레스 이관 자국
    2024-09-24  10건
    2022-04-05   8건

`rules.untrust_bulk_dates()` 가 이런 묶음을 잡아 무효화하는데 **그 함수는
`uploaded_at` 만 본다.** `rules.is_fresh()` 는 두 필드를 같은 자격으로 쓰므로
(`released_at or uploaded_at`) **효력은 똑같고 보호 장치만 한쪽에 있다.**
파리바게뜨가 정확히 반대 방향으로 가다 홈 1,237장 중 312장을 메뉴판으로
채운 사고가 그 함수 docstring 에 남아 있다. 여기선 그 교훈대로 간다 —
**효력은 안 잃고 가드만 얻는다.** 덤으로 `collect` 가 합류 첫날 first_seen 을
`uploaded_at` 으로 소급해 줘서 전건이 '오늘'로 몰리지도 않는다.

(2026-04-23 네 건 같은 작은 묶음은 진짜 출시일이 맞다. `BULK_MIN = 20` 이라
그런 건 가드에 안 걸린다. 걸리는 건 45건짜리 이관분뿐이다.)

## 분류

`menu_categories` 가 계층형이라 한 상품에 서너 개가 붙는다.
  parent=75 '모든 메뉴'  → [ 베이직 ] · [ 플러스 ] · [ 메인 인기 상품 ]  (브랜드 라인)
  parent=48 '오늘 뭐먹지?' → 매콤 · 담백 · 든든 · 얼큰 · 시원 · 따뜻 · 간식 · 소풍  (맛 태그)
  parent=41/61            → 김밥(베이직) · 분식 · 식사 · 사이드메뉴 · 계절메뉴 · 모다기
세 번째 묶음만 상품 분류다. 그래서 택소노미를 한 번 받아 부모를 보고 고른다.
이름만으로 거르면 '계절메뉴'·'분식' 처럼 양쪽 라인에 같은 이름이 따로 있는
걸 못 가른다.

## 그 밖에

⚠️ **154건을 받아 96건이 남는다.** 같은 요리가 `[ 베이직 ]`·`[ 플러스 ]` 두
라인에 각각 글로 등록돼 있어서(분식 16+14, 식사 29+18 …) `Item.key` 가 겹친다.
계약대로 접되, **날짜 내림차순으로 받으므로 남는 건 나중에 등록된 쪽**이다.
라인별로 따로 올리려면 이름에 라인을 붙여야 하는데, 그러면 make_key 가 바뀌어
first_seen 이력이 통째로 끊긴다(base.py 의 🔴 경고). 접는 쪽을 택했다.
⚠️ 접힐 때 **배지가 붙은 쪽이 이기게** 한다 — 안 그러면 NEW 가 플러스 라인에만
붙어 있을 때 베이직 쪽이 먼저 들어와 배지를 잃는다.

설명은 없다. content 가 Elementor 레이아웃 HTML 뿐이고 본문 텍스트가 0자다.
이미지는 featured_media 이고 전부 https 다(3건은 비어 있다).
상품별 주소는 link 필드에 있다.

robots.txt: 200, 310바이트. `/wp-admin/` 과 `/*.phtml$` 만 막는다. `/wp-json/` 은
막혀 있지 않다. 이용약관은 푸터에 링크가 없어 확인하지 못했다.
"""
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "얌샘김밥"
ROOT = "https://yumsem.com"
API = ROOT + "/wp-json/wp/v2/yumsem-menu"
TAXONOMY = ROOT + "/wp-json/wp/v2/menu_categories"
PER_PAGE = 100
MAX_PAGES = 5    # 폭주 방지. 현재 2페이지(154건).
DELAY = 2.0

# 배지가 붙어 있는 화면. 상품 라인이 둘이라 두 장이다.
BADGE_PAGES = (
    ROOT + "/yumsem-gimbap/yumsem-basic/",
    ROOT + "/yumsem-gimbap/yumsem-plus/",
)
# `.prBadge` 에는 BEST·HOT·COOL 도 들어온다. 글자가 정확히 이것일 때만 신상이다.
NEW_BADGE = "NEW"

# 상품 분류의 부모 term id. 41=[ 베이직 ] 61=[ 플러스 ].
# 여기 안 든 부모(75 모든 메뉴 · 48 오늘 뭐먹지?)는 브랜드 라인과 맛 태그다.
MENU_PARENTS = (41, 61)


def _categories(c) -> dict:
    """term id → 분류명. 상품 분류인 것만 담는다(부모가 베이직/플러스인 것)."""
    r = base.retry(lambda: c.get(TAXONOMY, params={"per_page": PER_PAGE}))
    r.raise_for_status()
    time.sleep(DELAY)
    return {t["id"]: t["name"] for t in r.json()
            if t.get("parent") in MENU_PARENTS}


def _link_of(badge) -> str:
    """배지가 가리키는 상품 주소. 배지 자신에는 없어서 위로 올라가 찾는다."""
    n = badge.parent
    for _ in range(4):
        if n is None:
            return ""
        a = n.css_first("a[href*='/yumsem-menu/']")
        if a:
            return (a.attributes.get("href") or "").rstrip("/")
        n = n.parent
    return ""


def _badged(c) -> set:
    """NEW 배지가 붙은 상품 주소들. 배지는 REST 에 없다(위 docstring 참고)."""
    out, seen = set(), 0
    for url in BADGE_PAGES:
        r = base.retry(lambda: c.get(url))
        r.raise_for_status()
        time.sleep(DELAY)

        for badge in HTMLParser(r.text).css("div.prBadge"):
            seen += 1
            # ⚠️ 존재가 아니라 글자다. BEST·HOT·COOL 이 같은 클래스로 온다.
            if " ".join(badge.text().split()) != NEW_BADGE:
                continue
            link = _link_of(badge)
            if link:
                out.add(link)
    if seen and not out:
        # 배지가 0건이면 건수는 96 그대로라 collect 의 0건·급감 가드에 안 걸리고
        # 화면에서만 조용히 '신상 없는 브랜드' 가 된다. 로그에 이유를 남긴다.
        print(f"[{BRAND}] prBadge {seen}개 중 NEW 가 0건이다 — 배지가 내려간 건지 "
              f"글자가 바뀐 건지 확인해야 한다")
    return out


def _category(post, names: dict) -> str:
    """상품 분류 하나. 여러 개면 먼저 붙은 것을 쓴다('계절메뉴' 와 '분식' 이
    같이 붙는 상품이 있는데 둘 다 상품 분류라 고를 근거가 없다)."""
    for tid in post.get("menu_categories") or ():
        if tid in names:
            return names[tid]
    return ""


def _image(post) -> str:
    """대표 이미지. 전부 https 다. 3건은 대표 이미지가 비어 있다."""
    media = (post.get("_embedded") or {}).get("wp:featuredmedia") or []
    return media[0].get("source_url", "") if media else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen: dict = {}      # key → items 안의 자리. 배지 가진 쪽이 이기게 한다.
    with base.client() as c:
        names = _categories(c)
        badged = _badged(c)
        for page in range(1, MAX_PAGES + 1):
            r = base.retry(lambda: c.get(API, params={
                "per_page": PER_PAGE, "orderby": "date", "order": "desc",
                "page": page, "_embed": "wp:featuredmedia",
            }))
            r.raise_for_status()
            posts = r.json()
            time.sleep(DELAY)

            for post in posts:
                name = " ".join(
                    (post.get("title") or {}).get("rendered", "").split())
                if not name:
                    continue
                link = (post.get("link") or "").rstrip("/")
                it = Item(
                    brand=BRAND,
                    name=name,
                    image=_image(post),
                    category=_category(post, names),
                    # CMS 등록일. released_at 이 아닌 이유는 위 docstring 참고.
                    uploaded_at=(post.get("date") or "")[:10],
                    # 화면의 NEW 배지. 없으면 '아니다'가 아니라 '모른다'다.
                    is_new=True if link in badged else None,
                    url=post.get("link", ""),
                )
                old = seen.get(it.key)
                if old is None:
                    seen[it.key] = len(items)
                    items.append(it)
                elif it.is_new and not items[old].is_new:
                    # 같은 이름이 두 라인에 있고 배지가 늦게 온 쪽에만 붙었다.
                    # 접으면서 배지를 잃지 않게 그쪽으로 바꿔 끼운다.
                    items[old] = it

            # 꽉 차지 않은 페이지면 다음 장이 없다.
            if len(posts) < PER_PAGE:
                break
    return items
