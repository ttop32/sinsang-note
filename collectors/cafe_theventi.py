"""더벤티(theventi).

theventi.co.kr/ 은 /new2022/main/intro.html 스플래시로 가고 본체가 /new2022/ 아래다.

**조사 문서가 가리킨 /new2022/menu/new.html 은 쓰지 않는다.** 그 페이지의 180건은
상품이 아니라 **홍보 포스터**다. 실측한 항목 이름이 '26년 브랜드캠페인_옥수수',
'26년 제로 음료 3종', '26년 여름 시즌 마시는 빙수 3종' 이고 마크업도 slick 캐러셀
(`.menu_new ul.slick > li`)이다. 상품명이 아니라 캠페인 제목이라 Item.name 에 넣으면
카드가 이상해진다. 조사에서 지적된 '시즌 묶음' 문제가 바로 이것이다.

대신 **/new2022/menu/all.html 의 '신메뉴' 탭**을 쓴다(2026-09-30 실측). 조사가
'요청 5회를 다 써서 확인 못 했다'고 남긴 연결이 여기서 풀린다. 탭이 ?mode=1..8 이고
기본값(mode 생략)이 mode=1 = 신메뉴다. **1요청에 개별 상품 25건**이 온다.
상품마다 이름·상세 uid·NEW 배지·ICE/HOT·개별 타임스탬프 이미지가 다 붙어 있다.
묶음을 억지로 쪼갤 필요가 없었다. 묶음 페이지와 상품 페이지가 애초에 다른 페이지였다.

신제품 신호:
  is_new  카드의 <i data-tag='NEW'>. 신메뉴 탭 25건 전건에 붙어 있고, 대조로 받아 본
          mode=2(커피) 20건에는 **한 건도 없다**. 브랜드가 선별해서 다는 배지다.
          그래서 배지가 없으면 False 가 아니라, 우리가 신메뉴 탭만 읽으므로
          False 를 줄 항목 자체가 없다.
  날짜    이미지 파일명 끝의 타임스탬프(_20260901180947)를 uploaded_at 에만 쓴다.
          released_at 에는 넣지 않는다. 브랜드가 말하는 출시일이 아니다.
          다만 메가(173건 중 81건이 한 달에 뭉침)와 달리 여기는 초 단위로 다 다르고
          한 달 최대 10건이라 일괄 재업로드 흔적이 없다 — 조사 내용과 일치한다.

url 은 상세 팝업 조각(all-view.new.html?uid=564)이다. 브랜드에 독립 상품 페이지가
없다(목록의 a.popup-link 가 이 조각을 받아 모달로 띄운다). 조각이라 스타일이 안
붙지만 이미지·상품명·설명·영양정보가 들어 있고 상품 단위 URL 은 이것뿐이다.

desc 는 목록에 없고 상세 조각에만 있다. 신메뉴 25건이 이 브랜드에서 화면에 올릴
전부라 25건 다 받는다(폴바셋 선례).

robots 는 깨끗하다. 2026-09-30 재확인 — 200, `User-agent: * / Allow: /`.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "더벤티"
SITE = "https://www.theventi.co.kr"
LIST_URL = f"{SITE}/new2022/menu/all.html"       # 파라미터 없으면 mode=1(신메뉴)
DELAY = 2.0
MAX_DETAILS = 60     # 폭주 방지. 현재 신메뉴는 25건.


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _abs(src: str) -> str:
    if not src:
        return ""
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("http://"):        # 목록이 이미지 절대경로를 http 로 준다
        return "https://" + src[len("http://"):]
    return src if src.startswith("http") else SITE + src


def _uploaded_at(img_url: str) -> str:
    """이미지 파일명 끝의 업로드 타임스탬프(_20260901180947)를 날짜로."""
    m = re.search(r"_(\d{4})(\d{2})(\d{2})\d{6}\.", img_url)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def _desc(c, uid: str) -> str:
    """상세 조각의 소개문(.txt). 뒤에 붙는 고지사항 줄은 떼어낸다."""
    r = base.retry(lambda: c.get(f"{SITE}/new2022/menu/all-view.new.html", params={"uid": uid}))
    r.raise_for_status()
    node = HTMLParser(r.text).css_first(".menu_desc_wrap .txt")
    if not node:
        return ""
    # <br> 로 나뉜 첫 문단만 쓴다. 그 뒤는 '*포도씨가 포함될 수 있습니다' 류다.
    first = node.html.split("<br")[0] if node.html else ""
    return _clean(HTMLParser(first).text()) if first else _clean(node.text())


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST_URL))
        r.raise_for_status()
        cards = HTMLParser(r.text).css(".menu_list li.item > a")
        if not cards:
            raise RuntimeError("더벤티 신메뉴 0건 — 셀렉터가 깨졌을 수 있다")

        pending = []                                  # (Item, uid)
        for card in cards:
            tit = card.css_first(".tit")
            name = _clean(tit.text()) if tit else ""
            if not name:
                continue
            img = card.css_first(".img_bx img")
            src = _abs(img.attributes.get("src", "") if img else "")
            m = re.search(r"uid=(\d+)", card.attributes.get("href", ""))
            uid = m.group(1) if m else ""
            it = Item(
                brand=BRAND,
                name=name,
                image=src,
                labels=[n.attributes.get("class", "").upper()
                        for n in card.css(".type i") if n.attributes.get("class")],
                uploaded_at=_uploaded_at(src),
                is_new=bool(card.css_first("[data-tag='NEW']")),
                url=f"{SITE}/new2022/menu/all-view.new.html?uid={uid}" if uid else "",
            )
            if it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)
            if uid:
                pending.append((it, uid))

        for it, uid in pending[:MAX_DETAILS]:
            time.sleep(DELAY)
            it.desc = _desc(c, uid)

    return items
