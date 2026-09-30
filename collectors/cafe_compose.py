"""컴포즈커피.

함정은 첫 페이지다. composecoffee.com/ 은 레이아웃 이름이 'opening' 인 스플래시라
본문이 없다. 본체는 /index1 이하이고 Rhymix(XE 계열) SSR 이라 브라우저는 필요 없다.
메뉴는 갤러리 모듈이다 — /index.php?mid=compose&act=dispCafemenuGalleryList.

**요청 수를 27회에서 10회로 줄였다.** 조사는 카테고리 9개를 각각 돌아 9×약3페이지 =
약 27요청으로 봤는데, 실측해 보니 `category_srl` 을 **빼면 '전체'** 가 되고
그게 그냥 10페이지(페이지당 20건, 약 200건)다. 카테고리를 다 도는 것과 같은 상품을
10요청으로 받는다. `list_count` 같은 페이지 크기 파라미터는 서버가 무시한다
(list_count=100 을 줘도 20건, 페이지 수 그대로 — 2026-09-30 실측).

대신 카테고리 이름(커피ㆍ콜드브루 / 베버리지 / …)을 잃는다. 전체 목록은
category_srl 을 안 달아 주기 때문이다. 요청을 2.7배 더 쓰면서까지 채울 값은
아니라고 봤다. category 는 비워 둔다.

신제품 신호가 **하나도 없다.** 2026-09-30 실측으로 확인한 내용:
  - NEW 배지 없음. 페이지의 NEW 는 전부 'NEWS' 메뉴 이름이다.
  - 신메뉴 전용 카테고리 없음. '추천메뉴'는 추천이지 신제품이 아니다.
  - 날짜 문자열 0건. 이미지가 /files/attach/images/272857/873/337/<해시>.jpg 인데
    가운데 숫자는 item_srl 을 3자리씩 쪼갠 것이지 날짜가 아니다.
  - 상세(dispCafemenuGalleryItem)에도 날짜·설명이 없다. 영양정보뿐이다.
그래서 is_new 는 **전건 None(모름)** 이고 released_at·uploaded_at·desc 는 비운다.
이 브랜드의 신제품 판정은 전적으로 collect 단계의 어제 대비 diff 에 맡긴다.
합류 첫날 신제품 0건이 정상이다. 메가·파스쿠찌와 같은 처지다.

item_srl 이 내림차순(337873 밤 티라미수 → 303749 에스프레소)이라 등록 순서로는
보이지만 날짜가 아니다. 신호로 쓰지 않는다.

robots 재확인(2026-09-30, **200**): `User-agent: *` 에 Disallow 9줄이 전부
게시판 디렉터리(/board_xIbz35/, /qnaw/, /corp_s_w/, /AS/ …)고 마지막이 `Allow:/` 다.
**원문을 눈으로 읽었다.** 쿼리스트링 와일드카드(`Disallow: /?mode*` 같은 것)는
한 줄도 없어서 can_fetch 가 놓칠 규칙 자체가 없다. 우리가 때리는 /index.php 는
어느 Disallow 에도 걸리지 않는다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "컴포즈커피"
SITE = "https://composecoffee.com"
LIST_URL = f"{SITE}/index.php"
PARAMS = {"mid": "compose", "act": "dispCafemenuGalleryList"}   # category_srl 없음 = 전체
MAX_PAGES = 20   # 폭주 방지. 현재 10페이지.
DELAY = 2.0


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _abs(src: str) -> str:
    if not src:
        return ""
    return src if src.startswith("http") else SITE + src


def _item_url(href: str) -> str:
    """상세 URL 은 item_srl 로 직접 짠다. 목록이 준 href 에는 우리가 보고 있던
    page 번호가 묻어 있어서 그대로 두면 카드 링크에 페이지 상태가 새어 나간다."""
    m = re.search(r"item_srl=(\d+)", href or "")
    if not m:
        return ""
    return (f"{LIST_URL}?mid={PARAMS['mid']}"
            f"&act=dispCafemenuGalleryItem&item_srl={m.group(1)}")


def _last_page(doc) -> int:
    """페이지네이션의 '끝 페이지' 링크에서 총 페이지 수. 없으면 1."""
    a = doc.css_first(".pagination a.nextEnd")
    m = re.search(r"page=(\d+)", a.attributes.get("href", "")) if a else None
    return int(m.group(1)) if m else 1


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    last = MAX_PAGES
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > last:
                break
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST_URL, params=PARAMS | {"page": page}))
            r.raise_for_status()
            doc = HTMLParser(r.text)
            if page == 1:
                last = min(_last_page(doc), MAX_PAGES)
            cards = doc.css("a.cafemenu-menu-item")
            if not cards:
                break

            parsed = []
            for card in cards:
                node = card.css_first(".cafemenu-menu-name")
                name = _clean(node.text()) if node else ""
                if not name:
                    continue
                img = card.css_first("img")
                parsed.append(Item(
                    brand=BRAND,
                    name=name,
                    image=_abs(img.attributes.get("src", "") if img else ""),
                    url=_item_url(card.attributes.get("href", "")),
                ))

            # 범위를 넘긴 page 를 서버가 마지막 페이지로 되돌려주는 경우를 막는다
            if not parsed or all(it.key in seen for it in parsed):
                break
            for it in parsed:
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

    # 1페이지만 받고 끝나면 파라미터가 바뀐 것이다. 조용한 부분수집을 막는다.
    if len(items) < 20:
        raise RuntimeError(f"컴포즈커피 {len(items)}건 — 목록 구조가 바뀌었을 수 있다")
    return items
