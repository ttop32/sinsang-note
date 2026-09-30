"""이마트24.

/goods/list 는 헤더만 있는 껍데기라 쓸모없다. 실제 목록은 상품 3개 섹션
(행사 상품 / 차별화 상품 / Fresh Food)이 각각 서버렌더로 뿌린다. 브라우저 불필요.
섹션당 전체는 수십 페이지라 신상만 보는 이 사이트 용도에 맞춰 앞쪽만 긁는다.

신제품 신호가 없는 브랜드다. 2026-09-30 실측으로 확인한 내용:
  - NEW 뱃지 마크업(.itemTit span)은 존재하지만 전 섹션·전 페이지에서 항상
    style="opacity: 0" 이다. 세 섹션 180건을 훑어 보이는 NEW 는 0건이었다. 죽은 마크업이다.
  - 상단 메뉴·사이트맵·각 섹션의 카테고리 필터를 전부 뒤져도 '신상품' 목록이 없다.
    행사 섹션의 필터는 1+1 / 2+1 / 3+1 / 세일 / 골라담기 뿐이고,
    차별화·Fresh Food 의 필터는 브랜드명(성수310, 조선호텔…)과 식품종류다.
  - 상품명이 <a href="#none"> 이라 상세 페이지 자체가 없다. 목록 HTML 어디에도
    등록일·출시일 필드가 없고(날짜처럼 보이는 문자열은 개발자가 남긴 HTML 주석이다),
    별도 API 도 없다. 페이지가 곧 전부다.
그래서 is_new 는 None(모름)으로 둔다. align=RECENT 가 POPULAR 와 결과가 다르긴 하지만
그게 '등록 최신순'이라는 근거는 어디에도 없어서, 앞 페이지를 신제품이라 우기지 않는다.
이 브랜드의 신제품 판정은 전적으로 collect 단계의 어제 대비 diff 에 맡긴다.

행사 상품 섹션은 통째로 행사 매대다(필터가 1+1/2+1/3+1/세일/골라담기뿐). 여기서 온 건
promo 로 표시한다. 화면 상위가 전부 이마트24 2+1 로 덮였던 게 바로 이 섹션이다.

가격(.price, 예: "1,700 원")도 같이 내려오지만 Item 에 담을 자리가 없어 버린다.
"""
import time

import httpx
from selectolax.parser import HTMLParser

from . import base
from .base import UA, Item

BRAND = "이마트24"
URL = "https://emart24.co.kr/goods/{section}"
SECTIONS = {"event": "행사 상품", "pl": "차별화 상품", "ff": "Fresh Food"}
PROMO_SECTIONS = {"event"}   # 행사 매대. 신제품이 아니라 행사라서 실린 상품들이다.
MAX_PAGES = 25  # 섹션당 상한. 8 로는 세 섹션 모두 상한을 소진해 뒤쪽이 통째로 잘렸다.
DELAY = 0.4     # 연속 호출 간격(초)


def _labels(card) -> list:
    """혜택 뱃지(2+1, 1+1, 세일). NEW 뱃지는 항상 opacity:0 으로 숨겨져 있어 제외."""
    out = []
    tit = card.css_first(".itemTit")
    if not tit:
        return out
    for span in tit.css("span"):
        # "opacity: 0" 문자열 비교는 공백 없는 opacity:0 이나 0.0 을 놓친다.
        style = (span.attributes.get("style") or "").replace(" ", "")
        if "opacity:0" in style:
            continue
        text = " ".join(span.text().split())
        if text:
            out.append(text)
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    by_key: dict = {}
    with base.client() as c:
        for section, category in SECTIONS.items():
            promo = section in PROMO_SECTIONS
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
                        promo=promo,
                    ))

                # 섹션끼리 상품이 겹친다(FF 상품이 차별화/행사에도 뜬다).
                # 중복이라고 페이지를 끊으면 뒤 섹션이 통째로 날아가므로 그냥 건너뛰기만 한다.
                # 다만 행사 매대에도 걸린 상품은 어느 섹션에서 먼저 만났든 행사 상품이므로
                # promo 만은 살려서 합친다(섹션 순서에 따라 표시가 뒤집히지 않게).
                for it in parsed:
                    old = by_key.get(it.key)
                    if old is None:
                        by_key[it.key] = it
                        items.append(it)
                    elif it.promo:
                        old.promo = True
    return items
