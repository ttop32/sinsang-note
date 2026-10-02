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

신제품 신호가 **HTML 에는** 하나도 없다. 2026-09-30 실측:
  - 마크업에 NEW 배지 없음. 페이지의 NEW 는 전부 'NEWS' 메뉴 이름이다.
  - 신메뉴 전용 카테고리 없음. '추천메뉴'는 추천이지 신제품이 아니다.
  - 날짜 문자열 0건. 이미지가 /files/attach/images/272857/873/337/<해시>.jpg 인데
    가운데 숫자는 item_srl 을 3자리씩 쪼갠 것이지 날짜가 아니다.
  - 상세(dispCafemenuGalleryItem)에도 날짜·설명이 없다. 영양정보뿐이다.

**그런데 배지가 썸네일 그림 안에 합성돼 있다.** 그래서 한동안 200건 수집하고
화면에 0건이었다 — 마크업만 보고 "신호 없음" 으로 접었던 것이다.

썸네일 우하 사분면의 노랑(#FFD800) 비율로 가른다. 2026-10-02 전수 실측:
  - 200장 중 **16장이 0.0850~0.0948**, 그 다음이 **0.0186** 으로 뚝 끊긴다.
  - 중간대 11장(0.001~0.05)은 망고·계란듬뿍·사과 생크림 같은 **노란 음식**이다.
    전부 경계에서 한참 아래라 섞일 염려가 없다.
  - 나머지 173장은 0.0000 이다. 애매한 값이 하나도 없다.
  - 200장 받는 데 20초. 매일 돌릴 만하다.
경계는 그 틈 한가운데인 0.05 에 둔다(_BADGE_MIN).

⚠️ **이미지 Last-Modified 는 쓰지 마라.** 컴포즈 LM 은 2026-06-16 에 149건이
몰린 일괄 재업로드다. LM 으로 창 안에 들어오는 41건과 배지 16건은 13건만
겹친다. 배지가 브랜드가 실제로 붙인 신호고 LM 은 우리 쪽 착시다.

날짜는 여전히 없다. released_at·uploaded_at·desc 는 비우고, 배지가 있는 것만
is_new=True 로 둔다.

item_srl 이 내림차순(337873 밤 티라미수 → 303749 에스프레소)이라 등록 순서로는
보이지만 날짜가 아니다. 신호로 쓰지 않는다.

robots 재확인(2026-09-30, **200**): `User-agent: *` 에 Disallow 9줄이 전부
게시판 디렉터리(/board_xIbz35/, /qnaw/, /corp_s_w/, /AS/ …)고 마지막이 `Allow:/` 다.
**원문을 눈으로 읽었다.** 쿼리스트링 와일드카드(`Disallow: /?mode*` 같은 것)는
한 줄도 없어서 can_fetch 가 놓칠 규칙 자체가 없다. 우리가 때리는 /index.php 는
어느 Disallow 에도 걸리지 않는다.
"""
import io
import re
import time

from PIL import Image

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


# 썸네일에 합성된 NEW 배지. 우하 사분면의 노랑 비율로 본다(위 docstring).
_BADGE_RGB = (0xFF, 0xD8, 0x00)
_BADGE_TOL = 24       # 채널당 허용 오차. JPEG 압축 때문에 정확히 안 맞는다.
_BADGE_MIN = 0.05     # 실측 간격 0.0186 ↔ 0.0850 한가운데


def _has_badge(c, url: str) -> bool:
    """썸네일 우하 사분면에 NEW 배지가 찍혀 있는가.

    못 받거나 못 읽으면 False 다 — 배지가 없는 쪽으로 틀리는 게 안전하다.
    여기서 틀려서 True 가 되면 상시 메뉴가 신상으로 올라간다.
    """
    if not url:
        return False
    try:
        im = Image.open(io.BytesIO(base.retry(lambda: c.get(url)).content)).convert("RGB")
    except Exception:
        return False
    w, h = im.size
    px = im.crop((w // 2, h // 2, w, h)).getdata()
    r0, g0, b0 = _BADGE_RGB
    hit = sum(1 for r, g, b in px
              if abs(r - r0) < _BADGE_TOL and abs(g - g0) < _BADGE_TOL
              and abs(b - b0) < _BADGE_TOL)
    return len(px) > 0 and hit / len(px) >= _BADGE_MIN


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

    # 썸네일을 받아 배지를 본다. 목록을 다 모은 뒤에 한 번만 돈다.
    # 배지 0건은 '오늘 신상이 없다'일 수도 있어서 실패로 보지 않는다. 다만
    # 그림을 **한 장도 못 읽으면** 그건 우리 쪽 고장이다.
    read = 0
    with base.client() as c:
        for it in items:
            if not it.image:
                continue
            read += 1
            if _has_badge(c, it.image):
                it.is_new = True
    if items and read == 0:
        raise RuntimeError("컴포즈커피 썸네일을 한 장도 못 읽었다 "
                           "— 이미지 주소가 바뀌었을 수 있다")
    return items
