"""도미노피자.

/goods/list 가 서버에서 완성된 HTML 을 그대로 내려준다. 쿠키·세션·브라우저 불필요.
응답은 EUC-KR(Content-Type 에 charset 이 박혀 있어 httpx 가 알아서 디코딩한다).
페이징이 없고 카테고리 한 장에 전 상품이 다 들어있어서 3회만 받으면 끝난다.

신제품 신호가 둘 다 있는 편한 브랜드다. 2026-09-30 실측:
  - 피자 목록 맨 위에 <div id="category-new"> 'New' 섹션이 따로 있다. 1순위 소스.
  - 카드마다 <span class="label sale">NEW</span> 배지가 붙는다. C0101·C0201 에서 확인.
    같은 'label sale' 클래스를 '시그니처' 도 쓰므로 클래스가 아니라 글자로 판정한다.
행사 상품은 사이드 카테고리의 '콤보' 섹션과 '특가' 배지로 드러난다. 그건 promo 로 뺀다.

출시일은 어디에도 없다. 이미지 파일명 앞의 날짜(20260914_*.jpg)는 출시일이 아니라
이미지 업로드 시각이다. 실제로 2020년부터 파는 슈퍼디럭스가 20260914 로 찍혀 있다.
그래서 uploaded_at 에만 넣고 released_at 은 비운다.
도미노뉴스(/bbs/newsList?type=N) 도 봤지만 명절 영업안내·약관 개정뿐이고
신메뉴 출시 공지는 없다.

가격은 목록에 있지만(L 36,900원~) Item 에 자리가 없어 버린다.
⚠️ robots.txt 는 /goods/ 를 Allow 하지만, 사이트 푸터에 '사전 서면동의 없이 ...
상업적 목적으로 전재·전송·스크래핑' 금지 문구가 있다. 상업적 이용 전에 확인이 필요하다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import UA, Item

BRAND = "도미노피자"
URL = "https://www.dominos.co.kr/goods/list"

# 상단 GNB 가 가리키는 카테고리 전부. 파라미터 없이 받으면 C0101 과 같다.
CATEGORIES = ("C0101", "C0201", "C0202")
NEW_SECTION_ID = "category-new"   # 'New' 섹션 헤더의 id
PROMO_LABELS = {"특가"}
PROMO_SECTIONS = {"콤보"}
DELAY = 1.0                       # 요청 간격(초). 3회뿐이라 넉넉히 둔다.


def _name(card) -> str:
    """.subject 안에는 상품명 텍스트와 .label-box 가 같이 들어있다. 직계 텍스트만 뗀다."""
    n = card.css_first(".subject")
    return " ".join(n.text(deep=False).split()) if n else ""


def _image(card) -> str:
    """목록은 lazyload 라 진짜 주소가 src 가 아니라 data-src 에 있다."""
    n = card.css_first(".prd-img img")
    return n.attributes.get("data-src", "") if n else ""


def _uploaded_at(img_url: str) -> str:
    """이미지 파일명 앞의 업로드 날짜(20260914_JBSQ60U8.jpg)."""
    m = re.search(r"/(\d{4})(\d{2})(\d{2})_", img_url)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def _parse(html: str) -> list[tuple]:
    """(섹션id, 섹션명, 카드) 목록. 섹션 헤더와 목록이 형제라 순서대로 훑는다."""
    out = []
    for art in HTMLParser(html).css("article.menu-list-area"):
        sec_id, sec_name = "", ""
        for child in art.iter():
            cls = child.attributes.get("class", "") or ""
            if "title-wrap-center" in cls:
                title = child.css_first("h3.title-type")
                sec_id = child.attributes.get("id", "") or ""
                sec_name = " ".join(title.text().split()) if title else ""
            elif "menu-list" in cls:
                out += [(sec_id, sec_name, li) for li in child.css("li")]
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        for ctgr in CATEGORIES:
            r = base.retry(lambda: c.get(URL, params={"dsp_ctgr": ctgr}))
            r.raise_for_status()

            page = []
            for sec_id, sec_name, card in _parse(r.text):
                name = _name(card)
                if not name:
                    continue  # '하프앤하프 더보기' 같은 링크 타일
                labels = [" ".join(n.text().split()) for n in card.css(".label")]
                img = _image(card)
                page.append(Item(
                    brand=BRAND,
                    name=name,
                    desc=" ".join(" ".join(n.text().split())
                                  for n in card.css(".hashtag span")).strip(),
                    image=img,
                    labels=labels,
                    category=sec_name,
                    uploaded_at=_uploaded_at(img),
                    is_new=(sec_id == NEW_SECTION_ID or "NEW" in labels) or None,
                    promo=bool(set(labels) & PROMO_LABELS) or sec_name in PROMO_SECTIONS,
                ))

            # 이 카테고리가 NEW 를 하나라도 달고 있으면, 안 달린 건 '신제품 아님'으로
            # 읽어도 된다. 하나도 없으면 배지를 안 쓰는 분류일 수 있으니 None 으로 둔다.
            # (실측: C0101·C0201 은 NEW 가 있고, C0202 음료·소스는 하나도 없다)
            if any(it.is_new for it in page):
                for it in page:
                    if it.is_new is None:
                        it.is_new = False

            for it in page:
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)
            time.sleep(DELAY)
    # 배지·섹션 id 가 바뀌면 전건 None 이 되는데 건수는 그대로라
    # collect.py 의 0건 가드도 FLOOR 도 발동하지 않는다. 조용히 굳는 걸 막는다.
    if items and all(it.is_new is None for it in items):
        raise RuntimeError("NEW 신호가 하나도 없다 — 배지·섹션 id 가 바뀌었을 가능성")

    return items
