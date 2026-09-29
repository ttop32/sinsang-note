"""이마트24.

/goods/list 는 헤더만 있는 껍데기라 쓸모없다. 실제 목록은 상품 3개 섹션
(행사 상품 / 차별화 상품 / Fresh Food)이 각각 서버렌더로 뿌린다. 브라우저 불필요.
align=RECENT(최신순)가 진짜로 동작해서(POPULAR 와 결과가 다름) 앞 페이지가 곧 신상이다.
섹션당 전체는 수십 페이지라 신상만 보는 이 사이트 용도에 맞춰 앞쪽만 긁는다.

가격(.price, 예: "1,700 원")도 같이 내려오지만 Item 에 담을 자리가 없어 버린다.
"""
import time

import httpx
from selectolax.parser import HTMLParser

from .base import UA, Item

BRAND = "이마트24"
URL = "https://emart24.co.kr/goods/{section}"
SECTIONS = {"event": "행사 상품", "pl": "차별화 상품", "ff": "Fresh Food"}
MAX_PAGES = 8   # 섹션당 상한. 20건/페이지, 최신순이라 앞쪽이 신상. 전체는 event 51p+.
DELAY = 0.4     # 연속 호출 간격(초)


def _labels(card) -> list:
    """혜택 뱃지(2+1, 1+1, 세일). NEW 뱃지는 항상 opacity:0 으로 숨겨져 있어 제외."""
    out = []
    tit = card.css_first(".itemTit")
    if not tit:
        return out
    for span in tit.css("span"):
        style = span.attributes.get("style") or ""
        if "opacity: 0" in style:
            continue
        text = " ".join(span.text().split())
        if text:
            out.append(text)
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with httpx.Client(headers={"User-Agent": UA}, timeout=20, follow_redirects=True) as c:
        for section, category in SECTIONS.items():
            for page in range(1, MAX_PAGES + 1):
                time.sleep(DELAY)
                r = c.get(URL.format(section=section),
                          params={"search": "", "page": page,
                                  "category_seq": "", "align": "RECENT"})
                r.raise_for_status()
                cards = HTMLParser(r.text).css("section.itemList .itemWrap")
                if not cards:
                    break   # 범위를 넘긴 page 는 빈 목록을 돌려준다

                parsed = []
                for card in cards:
                    name_node = card.css_first(".itemtitle a")
                    name = " ".join(name_node.text().split()) if name_node else ""
                    if not name:
                        continue
                    img_node = card.css_first(".itemSpImg img")
                    parsed.append(Item(
                        brand=BRAND,
                        name=name,
                        image=img_node.attributes.get("src", "") if img_node else "",
                        labels=_labels(card),
                        category=category,
                    ))

                # 섹션끼리 상품이 겹친다(FF 상품이 차별화/행사에도 뜬다).
                # 중복이라고 페이지를 끊으면 뒤 섹션이 통째로 날아가므로 그냥 건너뛰기만 한다.
                for it in parsed:
                    if it.key not in seen:
                        seen.add(it.key)
                        items.append(it)
    return items
