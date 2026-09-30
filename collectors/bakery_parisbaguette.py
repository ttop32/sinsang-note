"""파리바게뜨.

워드프레스 사이트고 REST API 가 인증 없이 열려 있다. robots.txt 는 /wp-admin/ 만
막는다. 브라우저 불필요. 2026-09-30 실측.

  GET www.paris.co.kr/wp-json/wp/v2/product?per_page=100&page=N   상품 (X-WP-Total 535)
  GET www.paris.co.kr/wp-json/wp/v2/product_category?per_page=100 카테고리 이름 47종

**응답에 UTF-8 BOM 이 붙는다.** json.loads(r.text) 가 그대로 터지니
r.content.decode("utf-8-sig") 로 받는다. r.json() 도 쓰면 안 된다.

**date 를 released_at 에 넣지 않는다.** 여기가 이 어댑터의 핵심 판단이다.
API 가 상품마다 date 를 주고 기본 정렬이 date 내림차순이라 출시일처럼 보이지만,
535건의 날짜 분포를 세어보니 뭉쳐 있었다.

    2026-08-26  104건      2026-08 한 달   245건 (전체의 46%)
    2026-08-28   67건      고유 일자        125일
    2026-08-12   22건

2026-08-26 의 104건을 열어 보면 후레쉬 식빵·웨하스·고로케·피자빵처럼 오래된
상시 판매 품목이다. 하루에 신제품 104종이 나온 게 아니라 사이트 개편 때 일괄
재발행된 것이고, 104건 중 102건이 modified 까지 같은 날이다.
메가MGC커피(173건 중 81건이 2024-06)와 같은 함정이라 date 는 uploaded_at 까지만 쓴다.
그걸 released_at 에 넣었으면 8월 26일에 104개 신제품이 나온 걸로 보도된다.

**신제품 표시가 없다.** product_tag 는 535건 전부 비어 있고, 카테고리 47종(브레드·
케이크·샌드위치/샐러드·선물·디저트/스낵·커피/음료·간편식과 그 하위)에 NEW·신제품
칸이 없다. HTML 목록(/products/)에도 NEW 배지가 없다. 그래서 is_new 는 전부 None 이고
신제품 판정은 collect 의 어제 대비 diff 에 맡긴다.

설명과 이미지는 본문에 없다. content.rendered 가 전부 빈 문자열이고 이미지는
featured_media 의 id 로만 오는데, 535번 미디어 API 를 때릴 일은 아니다. 대신 같은
응답의 yoast_head(Yoast SEO 14.9 가 찍는 meta 블록)에 og:description 과 og:image 가
완성된 채로 들어 있어 거기서 뽑는다. 이 버전은 yoast_head_json 을 주지 않아
문자열을 정규식으로 긁는다. 커버리지는 이미지 534/535, 설명 516/535 다.

약관은 해피포인트카드 회원 약관(주식회사 에스피씨클라우드)이고 제22조②가
"회원"의 "영리목적" 이용을 제한한다. 크롤링을 명시로 금지하지는 않는다.
**회원가입을 하면 이 약관이 계약으로 구속력을 가지므로 가입하지 않는다.**

가격 정보는 API 에 아예 없다.
"""
import html
import json
import re
import time

from . import base
from .base import Item

BRAND = "파리바게뜨"
API = "https://www.paris.co.kr/wp-json/wp/v2"
FIELDS = "id,date,link,title,product_category,yoast_head"
PER_PAGE = 100
MAX_PAGES = 12  # 폭주 방지. 현재 6페이지(535건).
DELAY = 1.2     # 요청 간격(초)


def _json(c, path: str, **params):
    r = base.retry(lambda: c.get(f"{API}/{path}", params=params))
    r.raise_for_status()
    time.sleep(DELAY)
    # BOM 을 벗기지 않으면 json 이 Unexpected UTF-8 BOM 으로 죽는다.
    return json.loads(r.content.decode("utf-8-sig"))


def _og(head: str, prop: str) -> str:
    m = re.search(rf'<meta property="og:{prop}" content="([^"]*)"', head or "")
    return html.unescape(m.group(1)) if m else ""


def _categories(c) -> dict:
    """id → (이름, 상위 id). 상품은 [상위, 하위] 를 같이 달고 오므로 둘 다 필요하다."""
    rows = _json(c, "product_category", per_page=PER_PAGE,
                 _fields="id,name,parent")
    return {x["id"]: (html.unescape(x["name"]), x["parent"]) for x in rows}


def _category(ids: list, cats: dict) -> str:
    """가장 구체적인 카테고리 하나. [30, 31] 이면 '브레드' 말고 '간식빵'."""
    named = [(i, cats[i]) for i in ids or [] if i in cats]
    if not named:
        return ""
    child = next((n for _, (n, parent) in named if parent), None)
    return child or named[0][1][0]


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        cats = _categories(c)
        for page in range(1, MAX_PAGES + 1):
            rows = _json(c, "product", per_page=PER_PAGE, page=page,
                         _fields=FIELDS)
            if not rows:
                break

            for p in rows:
                name = " ".join(html.unescape(
                    (p.get("title") or {}).get("rendered") or "").split())
                if not name:
                    continue
                head = p.get("yoast_head") or ""
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=_og(head, "description"),
                    image=_og(head, "image"),
                    category=_category(p.get("product_category"), cats),
                    # 워드프레스 발행일. 출시일이 아니다 — 모듈 주석 참고.
                    uploaded_at=(p.get("date") or "")[:10],
                    url=p.get("link") or "",
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

            if len(rows) < PER_PAGE:
                break
    return items
