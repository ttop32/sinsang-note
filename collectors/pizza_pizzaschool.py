"""피자스쿨. 등록 담당자에게: **(FRANCHISE, "피자")**.

가맹점 628개로 공정위 `피자`(I1) 1위다. 사이트가 워드프레스고 **REST API 가
그대로 열려 있다.** 메뉴는 `portfolio` 커스텀 포스트 타입 한 곳에 전부 있고
`per_page=100` 한 번에 63건이 다 온다(X-WP-Total 63 / X-WP-TotalPages 1 로
확인했다. 페이징은 필요 없지만 헤더가 늘면 알아채게 루프는 남겨뒀다).

⚠️ **https 를 쓰면 안 된다.** 2026-10-08 실측:
  https://pizzaschool.net/...  → ConnectError, 자체서명 인증서(CERTIFICATE_VERIFY_FAILED)
  http://pizzaschool.net/...   → 200 application/json, https 리다이렉트 없음
verify=False 로 뚫지 않고 http 로 간다(스쿨푸드·퀴즈노스와 같은 칸).

## 날짜 — `date` 를 쓰고 `modified` 는 버린다

63건의 `date` 분포를 전부 셌다(2026-10-08 실측). 날짜 26개에 63건이고
**중앙값이 1건**이다:
  2015-08-19 10 · 2015-11-18 10 · 2017-01-18 5 · 2017-02-15 4 · 2017-02-16 1
  2018-06-22 2 · 2018-08-22 1 · 2018-08-23 1 · 2018-12-17 1 · 2019-03-19 2
  2019-07-30 1 · 2019-08-08 6 · 2020-04-08 1 · 2021-06-21 1 · 2021-07-02 1
  2021-08-12 2 · 2022-06-23 2 · 2022-12-23 1 · 2023-03-03 1 · 2023-06-08 1
  2023-12-26 1 · 2024-07-02 2 · 2025-03-14 1 · 2026-01-01 1 · 2026-04-09 1
  2026-07-23 3
몰린 날이 셋 있지만(2015 두 번 = 사이트 개장, 2017·2019 = 토핑·소스 일괄 등록)
**전부 6년 이상 묵었고** 60일 창에 닿지 않는다. 최근 5년치는 1~3건씩 흩어져
있어 일괄 재업로드 모양이 아니다. 그래서 `released_at` 에 넣는다.

진짜 출시일이라는 교차 근거 셋:
  1. `_embed` 로 받은 대표 이미지의 업로드 시각이 최근 8건 전부 `date` 와
     같은 날이다(2024-07-02 · 2025-03-14 · 2026-01-01 · 2026-04-09 · 2026-07-23).
  2. 같은 워드프레스의 `banner` 포스트 타입에 `홈페이지하단배너_타코피자`
     (2026-07-23) · `홈페이지하단배너_콘치즈피자`(2026-01-01) 가 **같은 날짜로**
     따로 올라와 있다. 메뉴 등록과 홈 배너 교체가 같은 날 이뤄졌다는 뜻이다.
  3. 내용이 연도와 맞는다 — 치즈·페퍼로니·콤비네이션이 2015, 트러플 라인이
     2021~2022, 불닭고구마가 2023, 타코피자가 2026-07 이다.

**`modified` 는 쓰지 않는다.** 일괄 편집 자국이라 신호가 아니다 — 63건 중
2026-01-07 에 15건, 2025-03-14 에 10건, 2025-12-18 에 9건, 2024-10-27 에 7건이
한꺼번에 찍혀 있고 그 안에 2015년 치즈피자·페퍼로니피자가 들어 있다.
(가격 개정·이미지 교체로 보인다.) `modified` 를 썼으면 11년 된 메뉴판이
통째로 신상이 됐을 것이다.

## 신제품 배지 — `portfolio_entries` 의 `신메뉴` 분류

배지가 아니라 분류(taxonomy)다. **63건 중 2건(3.2%)** 에만 붙어 있고
둘 다 최신 날짜(2026-07-23)의 비프타코피자·치킨타코피자다. 100% 가 아니니
장식이 아니고, '신제품 전용 목록' 도 아니다 — `portfolio` 는 메뉴판 전체다.
분류 6종과 건수(2026-10-08 실측): 신메뉴 2 · 스쿨스페셜피자 25 · 클래식피자 11 ·
사이드 21 · 추가토핑 12 · 메인대표상품 19.

⚠️ 분류 id 를 박아두지 않고 이름으로 찾는다. 같은 날(2026-07-23) 올라온
할라피뇨는 사이드라 `신메뉴` 가 안 붙었다 — 운영자가 손으로 고르는 분류라
붙은 것만 True 로 보고 **안 붙은 건 False 가 아니라 None** 으로 둔다
(파파존스와 같은 선). 어차피 이 브랜드는 `released_at` 이 본 신호다.

## 나머지

  - 이미지: `_embed=wp:featuredmedia` 한 방으로 **63/63 전건**이 채워진다.
    전부 lh3.googleusercontent.com 이고 셋을 직접 받아 image/jpeg 200 을 확인했다.
    `content.rendered` 는 Avia 빌더 HTML 덩어리라 거기서 <img> 를 집으면
    장식 이미지가 섞인다. 쓰지 않는다.
  - 설명: `excerpt.rendered` 가 깨끗하다(63/63). 끝에 붙은
    `<strong class="price">` 는 가격이라 떼고 넣는다. Item 에 가격 자리가 없다.
  - 영문명: `content.rendered` 의 `.av-subheading` 앞머리에 있다. 다만 구분자가
    ` l `(소문자 L)·` | ` 로 섞이고 `할라피뇨 | Jalapeno` 처럼 순서가 뒤집힌
    것도 있어서, 쪼갠 조각 중 **ASCII 뿐인 것**을 고른다. 영문이 없는 건
    (갈릭 스프레드·트러플크림소스) 그냥 빈 값이다.
  - 다른 post_type 에는 메뉴가 없다(2026-10-08 실측). `banner` 34건은 홈 배너,
    `post` 267건은 매장 오픈·기부 소식, `page` 43건은 공지·알레르기 안내다.
  - 상품명 63건을 전부 눈으로 읽었다. 분류 제목이나 중복은 섞여 있지 않다.
    피자가 아닌 것(사이드 21 · 추가토핑 12)이 섞여 있지만 전부 먹는 것이라
    그대로 내보내고 `category` 로 구분한다. 주류·비식품은 하나도 없다.
    `치킨스틱&#038;윙` 처럼 HTML 엔티티가 든 이름이 있어 unescape 한다.
"""
import collections
import html
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "피자스쿨"
# ⚠️ http 다. https 는 자체서명 인증서라 연결 자체가 안 된다(docstring 참고).
ROOT = "http://pizzaschool.net"
API = ROOT + "/wp-json/wp/v2"
DELAY = 1.5      # 요청 간격(초). 분류 1회 + 목록 1회뿐이라 넉넉히 둔다.
PER_PAGE = 100
MAX_PAGES = 5    # 폭주 방지. 현재 1페이지다.

NEW_TERM = "신메뉴"     # 이 분류에 든 것만 is_new=True
# Item.category 로 쓸 분류를 고르는 순서. 한 상품이 분류 넷에 걸쳐 있는 일이
# 흔해서(타코피자 = 신메뉴·스쿨스페셜피자·클래식피자·메인대표상품) 하나를 골라야 한다.
# '신메뉴' 는 분류가 아니라 배지고, '메인대표상품' 은 추천 표시라 맨 뒤에 둔다.
CATEGORY_ORDER = ("사이드", "추가토핑", "클래식피자", "스쿨스페셜피자", "메인대표상품")

# av-subheading 을 쪼개는 구분자. ` l `(소문자 L) 과 ` | ` 가 섞여 있고
# 뒤쪽 공백이 없는 것도 있다(`... Mousse l피자스쿨의 ...`).
_SPLIT = re.compile(r"\s[l|｜]\s?")
_ASCII = re.compile(r"^[A-Za-z0-9 .,&'+/()-]+$")

# 한 날짜에 전체의 이만큼이 몰리면 사이트 재구축으로 전 상품이 '오늘 등록' 이
# 된 것이다. 그대로 두면 메뉴판 63건이 통째로 신상이 된다. 지금 최대 묶음은
# 10/63(16%)이라 여유가 넉넉하다.
BULK_SHARE = 1 / 3


def _terms(c) -> dict:
    """분류 id → 이름. id 를 코드에 박으면 사이트가 분류를 다시 만들 때 조용히 어긋난다."""
    r = base.retry(lambda: c.get(f"{API}/portfolio_entries",
                                 params={"per_page": PER_PAGE}))
    r.raise_for_status()
    return {t["id"]: t["name"] for t in r.json()}


def _posts(c) -> list:
    """portfolio 전건. 지금은 1페이지지만 X-WP-TotalPages 를 보고 더 돌린다."""
    out, page = [], 1
    while page <= MAX_PAGES:
        r = base.retry(lambda: c.get(f"{API}/portfolio",
                                     params={"per_page": PER_PAGE, "page": page,
                                             "_embed": "wp:featuredmedia"}))
        r.raise_for_status()
        out += r.json()
        total_pages = int(r.headers.get("X-WP-TotalPages") or 1)
        if page >= total_pages:
            break
        page += 1
        time.sleep(DELAY)
    return out


def _image(post: dict) -> str:
    media = (post.get("_embedded") or {}).get("wp:featuredmedia") or []
    return (media[0].get("source_url") or "") if media else ""


def _desc(post: dict) -> str:
    """excerpt 에서 가격(<strong class="price">)만 떼고 남긴 설명."""
    t = HTMLParser(post.get("excerpt", {}).get("rendered", "") or "")
    for n in t.css("strong.price"):
        n.decompose()
    return " ".join(t.text().split())


def _name_en(post: dict) -> str:
    """av-subheading 조각 중 ASCII 뿐인 것. 없으면 빈 값."""
    sub = HTMLParser(post.get("content", {}).get("rendered", "") or "").css_first(
        ".av-subheading")
    if sub is None:
        return ""
    for part in _SPLIT.split(" ".join(sub.text().split())):
        part = part.strip()
        if part and _ASCII.match(part) and re.search(r"[A-Za-z]", part):
            return part
    return ""


def fetch() -> list[Item]:
    with base.client() as c:
        terms = _terms(c)
        time.sleep(DELAY)
        posts = _posts(c)

    items: list[Item] = []
    seen = set()
    for post in posts:
        name = " ".join(html.unescape(
            post.get("title", {}).get("rendered", "") or "").split())
        if not name:
            continue
        names = [terms.get(t, "") for t in (post.get("portfolio_entries") or [])]
        category = next((x for x in CATEGORY_ORDER if x in names), "")
        it = Item(
            brand=BRAND,
            name=name,
            name_en=_name_en(post),
            desc=_desc(post),
            image=_image(post),
            category=category,
            # 등록일이 곧 출시일이다. modified 는 일괄 편집이라 안 쓴다(docstring).
            released_at=(post.get("date") or "")[:10],
            # 분류 '신메뉴' 가 붙은 것만 True. 안 붙은 건 '아니다'가 아니라 '모른다'다.
            is_new=True if NEW_TERM in names else None,
            url=post.get("link", "") or "",
        )
        if it.key in seen:
            continue
        seen.add(it.key)
        items.append(it)

    if not items:
        raise RuntimeError("피자스쿨 portfolio 가 0건 — API 경로나 post_type 이 바뀌었다")
    dated = [it for it in items if it.released_at]
    if not dated:
        raise RuntimeError("피자스쿨 date 가 전건 비었다 — 응답 모양이 바뀌었다")
    if not any(it.image for it in items):
        raise RuntimeError("피자스쿨 대표 이미지가 0건 — _embed 응답이 바뀌었다")
    # 사이트를 다시 세우면 63건이 전부 '오늘 등록' 으로 찍힌다. 건수는 그대로라
    # collect.py 의 0건·급감 가드에 안 걸리고 메뉴판이 통째로 신상이 된다.
    top, n = collections.Counter(it.released_at for it in dated).most_common(1)[0]
    if n > len(dated) * BULK_SHARE:
        raise RuntimeError(
            f"피자스쿨 date 가 {top} 한 날짜에 {n}/{len(dated)}건 몰렸다 "
            "— 사이트 재구축 일괄등록으로 보인다. released_at 으로 쓰면 안 된다")
    return items
