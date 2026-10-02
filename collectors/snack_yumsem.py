"""얌샘김밥.

도메인은 yumsem.com 이다(`yamsaem.co.kr` 은 NXDOMAIN — 로마자 표기를 추측하면
안 맞는다). 워드프레스 + Elementor 사이트인데 **메뉴가 글(post)로 관리된다.**
`yumsem-menu` 커스텀 포스트 타입이 show_in_rest 로 열려 있어 REST 로 전수가 온다.

  GET /wp-json/wp/v2/yumsem-menu?per_page=100&orderby=date&order=desc&_embed=…
      → X-WP-Total: 154, X-WP-TotalPages: 2

**이 레포에서 날짜가 진짜인 몇 안 되는 외식 브랜드다.** CMS 가 글 등록일을
`date` 로 주고, 화면(/yumsem-gimbap/yumsem-basic/)의 NEW 배지 8건이 정확히
등록일 상위 묶음(2026-04-23 네 건 · 2025-10-29 세 건)과 일치한다. 두 신호가
독립적으로 같은 답을 낸다. 배지를 따로 긁지 않는 건 그래서다 — 분류 페이지를
여러 장 더 받아야 하는데 날짜가 이미 같은 답을 주고, 날짜 쪽이 더 정밀하다.

⚠️ **`date` 가 전부 출시일인 건 아니다. 2023-11-23 하루에 62건이 몰려 있다.**
사이트를 워드프레스로 옮기면서 한 번에 import 한 자국이다(그 앞뒤로
2023-09-04 12건, 2024-09-24 12건도 묶음이다). 지금은 3년 전이라 신선도
판정에서 어차피 걸러지지만, **브랜드가 사이트를 다시 옮기면 154건이 전부
그날 날짜를 달고 신상으로 쏟아진다.** 그때는 released_at 을 믿으면 안 된다.
하루에 열 건 넘게 같은 날짜로 들어오면 그 날짜는 출시일이 아니라 이관일이다.

그래도 released_at 에 넣는다. Item 계약이 "출시일/등록일"이라 등록일이 여기고,
묶음 출시(연 2~3회)가 이 브랜드의 실제 운영 방식이라 2026-04-23 네 건 같은
덩어리는 오보가 아니라 사실이다.

분류 택소노미(`menu_categories`)가 계층형이라 한 상품에 서너 개가 붙는다.
  parent=75 '모든 메뉴'  → [ 베이직 ] · [ 플러스 ] · [ 메인 인기 상품 ]  (브랜드 라인)
  parent=48 '오늘 뭐먹지?' → 매콤 · 담백 · 든든 · 얼큰 · 시원 · 따뜻 · 간식 · 소풍  (맛 태그)
  parent=41/61            → 김밥(베이직) · 분식 · 식사 · 사이드메뉴 · 계절메뉴 · 모다기
세 번째 묶음만 상품 분류다. 그래서 택소노미를 한 번 받아 부모를 보고 고른다
(요청 1회 추가). 이름만으로 거르면 '계절메뉴'·'분식' 처럼 양쪽 라인에 같은
이름이 따로 있는 걸 못 가른다.

설명은 없다. content 가 Elementor 레이아웃 HTML 뿐이고 본문 텍스트가 0자다.
이미지는 featured_media 이고 전부 https 다. 상품별 주소는 link 필드에 있다.

robots.txt: 200, 310바이트. `/wp-admin/` 과 `/*.phtml$` 만 막는다. `/wp-json/` 은
막혀 있지 않다. 이용약관은 푸터에 링크가 없어 확인하지 못했다.
"""
import time

from . import base
from .base import Item

BRAND = "얌샘김밥"
ROOT = "https://yumsem.com"
API = ROOT + "/wp-json/wp/v2/yumsem-menu"
TAXONOMY = ROOT + "/wp-json/wp/v2/menu_categories"
PER_PAGE = 100
MAX_PAGES = 5    # 폭주 방지. 현재 2페이지(154건).
DELAY = 2.0

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
    keys = set()
    with base.client() as c:
        names = _categories(c)
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
                it = Item(
                    brand=BRAND,
                    name=name,
                    image=_image(post),
                    category=_category(post, names),
                    # CMS 등록일. 위 docstring 의 이관 묶음 경고를 같이 읽을 것.
                    released_at=(post.get("date") or "")[:10],
                    # 브랜드가 NEW 라고 표시한 걸 API 에서는 못 본다. 날짜가
                    # 그 자리를 대신하므로 '모른다'로 둔다(아니다가 아니다).
                    is_new=None,
                    url=post.get("link", ""),
                )
                if it.key in keys:
                    continue
                keys.add(it.key)
                items.append(it)

            # 꽉 차지 않은 페이지면 다음 장이 없다.
            if len(posts) < PER_PAGE:
                break
    return items
