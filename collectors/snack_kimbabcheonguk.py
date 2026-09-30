"""김밥천국.

도메인은 kimbab1009.com 이다. 푸터에 상표디자인번호(41-0165887-0000)와
사업자등록번호(214-88-85173)가 찍혀 있어 동일 상표를 쓰는 다른 법인
(kimbabcheongug.co.kr 등)과 구분된다. 어느 날 메뉴가 통째로 달라 보이면
도메인부터 다시 확인해야 한다.

Imweb 빌더 사이트지만 상품은 SSR 이다. 브라우저 불필요, UTF-8, 1요청.
메뉴 분류는 /25 김밥 · /26 식사 · /27 분식 · /28 돈까스 · /29 계절메뉴 · /31 신메뉴 인데
우리 용건이 신제품이라 /31 한 장만 받는다.

**robots.txt 가 /?mode* 를 막는다.** 푸터의 이용약관 링크가 /?mode=policy 라
약관 원문은 받을 수 없고 이 어댑터도 요청하지 않는다. 즉 이 브랜드는
"약관에 금지 조항이 없다"가 아니라 "약관을 확인하지 못했다" 상태로 붙는 것이다.
삭제 요청이 오면 다투지 말고 즉시 내린다.

신제품 신호 — 2026-09-30 실측. **조사 기대와 어긋난 부분이 있다.**
  - /31 은 브랜드가 '신메뉴'라고 이름 붙인 분류지만 75건이 쌓여 있고,
    김밥·라면·호박죽·수제비처럼 /27 분식 분류와 겹치는 상시 메뉴가 섞여 있다.
    최근 것만 골라 둔 페이지가 아니라 8년치 누적 아카이브다.
  - 그래서 is_new 는 브랜드 표시대로 True 로 올리되, 썸네일 경로의 업로드
    날짜를 uploaded_at 에 같이 실어 보낸다. 이미지 날짜가 2017-04-16 과
    2024-12-15/16 두 덩어리뿐이라(그 사이 8년이 비어 있다) collect 의 STALE
    판정에서 대부분 걸러진다. 배지를 믿되 날짜로 늙은 걸 거르는 건
    이삭토스트·피자헛과 같은 처리다.
  - released_at 에는 넣지 않는다. 브랜드가 말한 출시일이 아니라 CDN 업로드
    날짜고, 두 덩어리로 뭉쳐 있는 모양 자체가 일괄 재업로드 흔적이다
    (메가MGC커피 2024-06 81건과 같은 함정).

같은 이름이 여러 번 나온다(오므돈까스 4건, 까르보떡볶이 3건 — 촬영컷만 다르다).
계약대로 Item.key 로 접는다. 이름이 비어 있는 카드가 2건 있어 그건 버린다.
가격 정보는 /46 메뉴단가 에 따로 있는데 Item 에 자리가 없어 받지 않는다.
상품 상세 페이지가 없다(라이트박스라 URL 이 안 바뀐다). url 은 비워 둔다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "김밥천국"
URL = "https://kimbab1009.com/31"
CATEGORY = "신메뉴"
DELAY = 2.0   # robots 에 Crawl-delay 는 없다. 1요청뿐이라 여유를 둔다.


def _text(node, sel) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _uploaded_at(img_url: str) -> str:
    """CDN 경로의 업로드 날짜(/thumbnail/20241216/…)를 YYYY-MM-DD 로."""
    m = re.search(r"/thumbnail/(\d{4})(\d{2})(\d{2})/", img_url)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def _image(card) -> str:
    """지연로딩이라 실제 파일은 data-original 에 있고 src 는 저해상도 자리채움이다."""
    n = card.css_first("img")
    if not n:
        return ""
    return n.attributes.get("data-original", "") or n.attributes.get("src", "")


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(URL))
        r.raise_for_status()
        time.sleep(DELAY)

        for card in HTMLParser(r.text).css("div._item.item_gallary"):
            # 상품명·설명은 라이트박스용 숨은 캡션에 들어 있다.
            cap = card.css_first("div[id^=caption_]")
            name = _text(cap, "h4") if cap else ""
            if not name:
                continue          # 이름 없는 빈 카드 2건
            img = _image(card)
            it = Item(
                brand=BRAND,
                name=name,
                desc=_text(cap, "p"),
                image=img,
                category=CATEGORY,
                uploaded_at=_uploaded_at(img),
                # 브랜드가 '신메뉴'로 분류한 페이지다. 낡은 항목은 uploaded_at 을
                # 보고 collect 가 거른다.
                is_new=True,
            )
            if it.key in keys:
                continue          # 같은 상품의 다른 촬영컷
            keys.add(it.key)
            items.append(it)
    return items
