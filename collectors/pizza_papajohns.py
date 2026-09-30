"""파파존스.

도메인부터 조심해야 한다. 2026-09-30 실측:
  https://papajohns.co.kr      → connection refused
  https://www.papajohns.co.kr  → connection refused
  http://papajohns.co.kr       → 200, https://pji.co.kr 로 리다이렉트
그래서 pji.co.kr 을 직접 친다. papajohns.co.kr 은 https 가 아예 안 뜬다.

Next.js SSR 이라 목록·설명·가격이 전부 첫 HTML 에 들어온다. 브라우저 불필요.
__next_f 페이로드에는 상품 JSON 이 없어서(name/price 같은 키가 0회) HTML 을 파싱한다.

**robots.txt 가 없다.** https://pji.co.kr/robots.txt 는 404 인데 Next.js 가 404 페이지를
HTML 로 돌려준다(피자알볼로·GS25 와 같은 패턴이니 본문만 보고 규칙이 있다고 오판하면 안 된다).
상태코드가 404 라 규칙 부재는 맞다. 부재는 금지가 아니지만 허용도 아니라서
CRAWLING-POLICY §2 기준대로 지연을 2초로 더 길게 잡는다.

신제품 신호는 NEW 배지 하나다. 2026-09-30 실측:
  - 피자 24건 중 2건이 NEW. 피자 목록의 필터 탭(data-pizza-tab = ALL/NEW/BEST/
    SPECIALTY&THIN/CLASSIC/GREEN EAT)과 배지가 정확히 일치한다(교차검증됨).
  - 사이드 14건 중 3건이 NEW. 사이드·음료 페이지에는 필터 탭이 없고 배지만 있다.
배지가 없다고 신제품이 아니라고 단정하지는 않는다(피자헛·이삭토스트와 같은 선).
**출시일은 어디에도 없다.** 상품 id(1000~3241)가 증가 순서이긴 하지만 날짜로 환산할 근거가
없어서 released_at 은 전부 빈 값이다. 이 브랜드의 날짜 판정은 collect 의 diff 에 맡긴다.

한 상품이 HTML 에 네 번 나온다(모바일/데스크톱 breakpoint × 필터탭 ALL/개별).
카드 96개, 실제 상품 24개다. Item.key 로 지운다.

행사 표시는 없다. /menu/promotion·/menu/store-promotion 은 배너 페이지라 상품 카드가
0개고(실측), /menu/half-and-half 는 조합 화면이라 역시 0개다. 셋 다 받지 않는다.
그래서 promo 는 전부 False 다 — 없는 신호를 이름으로 추측해 만들지 않는다.

가격(L/F)이 HTML 에 있지만 Item 에 자리가 없어 버린다.
"""
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "파파존스"
ROOT = "https://pji.co.kr"
DELAY = 2.0     # robots.txt 가 없는 사이트라 더 길게 잡는다

# (분류명, 경로). 분류명은 사이트 내비게이션 표기 그대로다.
SOURCES = (
    ("피자",    "/menu/pizza"),
    ("사이드",  "/menu/other/side"),
    ("음료/소스", "/menu/other/drink"),
)

# 카드 컨테이너. 피자는 <a>, 사이드·음료는 <div> 라 태그가 아니라 클래스로 잡는다.
CARD = ".rounded-xl.bg-border-neutral-secondary"


def _own_text(node) -> str:
    """자식 <span> 을 뺀 제 텍스트만. 상품명 <p> 안에 NEW·THIN 배지 span 이 같이 있다."""
    parts = [n.text_content for n in node.iter(include_text=True) if n.tag == "-text"]
    return " ".join("".join(parts).split())


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        for category, path in SOURCES:
            r = base.retry(lambda: c.get(ROOT + path))
            r.raise_for_status()
            time.sleep(DELAY)

            for card in HTMLParser(r.text).css(CARD):
                title = card.css_first("p.font-bold")
                if not title:
                    continue
                name = _own_text(title)
                if not name:
                    continue
                labels = [" ".join(s.text().split()) for s in title.css("span")]
                labels = sorted({s for s in labels if s})

                desc = card.css_first("span.break-words")
                # 상품 이미지는 alt="메뉴" 다. 피자 카드 위에 겹쳐 놓은 로고 이미지는
                # alt 가 상품명이라 그걸로 구분한다(alt 로 안 거르면 로고를 집는다).
                img = card.css_first('img[alt="메뉴"]')

                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=" ".join(desc.text().split()) if desc else "",
                    image=img.attributes.get("src", "") if img else "",
                    labels=labels,
                    category=category,
                    # NEW 만 True. 배지 없음은 '아니다'가 아니라 '모른다'다.
                    is_new=True if "NEW" in labels else None,
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
    return items
