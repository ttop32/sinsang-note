"""매머드커피(MAMMOTH COFFEE).

도메인부터 조심해야 한다. mammothcoffee.co.kr 은 TLS 인증서 호스트명이 안 맞는다.
정답은 mmthcoffee.com 이다(2026-09-30 실측).

/sub/menu/new_list.php 가 신메뉴 전용 페이지다. 쿠키·세션 없이 SSR 로 24건이
한 번에 온다. 페이징도 AJAX 도 없다. 목록만 보면 1요청이다. 브라우저 불필요.

신제품 신호:
  is_new  브랜드가 '신메뉴' 탭으로 직접 묶어 준 목록이다. 이 페이지에 실린 것은
          전건 True 로 둔다. 다른 탭(매머드 익스프레스·매머드커피)은 읽지 않으므로
          '신제품 아님'을 확인한 상품이 없다. False 를 주는 항목은 없다.
  날짜    브랜드가 날짜를 어디에도 주지 않는다. 이미지 파일명이 해시라
          (3ddce86ec0abf4e5beff45c3aade8ac7.png) 메가·폴바셋식 uploaded_at 도 못 쓴다.
          released_at · uploaded_at 둘 다 비운다. 없는 날짜를 만들지 않는다.
  순서    마크업의 상품 id(goViewB(839))가 대체로 내림차순이라 등록 순서로는 쓸 수
          있지만 날짜가 아니다. 정렬에도 쓰지 않는다(841 이 839 보다 뒤에 있는 등
          완전한 내림차순이 아니다).

⚠️ robots.txt 가 **404** 다(Apache 기본 404 페이지, 2026-09-30 재확인).
403 이었다면 RFC 9309 상 전면 금지지만 404 는 '규칙 명시 없음'이라 제한이 없다
(CRAWLING-POLICY.md §1 의 CU 와 같은 처지). 규칙이 없는 만큼 간격은 보수적으로
2.5초를 쓴다.

url 은 상세 팝업 조각(/sub/menu/list_coffee_view.php?menuSeq=839)을 쓴다.
브랜드에 독립 상품 페이지가 없다 — goViewB() 가 이 조각을 받아 모달에 끼워 넣는
구조다. 조각이라 스타일이 안 붙지만 이미지·상품명·설명·영양정보가 다 들어 있고
상품 단위로 구분되는 URL 은 이것뿐이다. 조각이 싫으면 신메뉴 페이지 한 장으로
떨어뜨리면 되는데, 그러면 24건이 전부 같은 링크가 된다.

desc 와 온도 표기(only ICE)는 목록에 없고 이 상세 조각에만 있다. 신메뉴 24건이
이 브랜드에서 우리가 화면에 올릴 전부라 24건 다 받는다(폴바셋 선례).
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "매머드커피"
SITE = "https://mmthcoffee.com"
LIST_URL = f"{SITE}/sub/menu/new_list.php"
VIEW_URL = f"{SITE}/sub/menu/list_coffee_view.php"
DELAY = 2.5          # robots.txt 가 없는 사이트다. 보수적으로 간다.
MAX_DETAILS = 60     # 폭주 방지. 현재 신메뉴는 24건.


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _abs(src: str) -> str:
    if not src:
        return ""
    return src if src.startswith("http") else SITE + src


def _detail(c, seq: str) -> tuple:
    """상세 조각에서 (desc, labels). 조각이 비면 조용히 빈 값으로 둔다."""
    r = base.retry(lambda: c.get(VIEW_URL, params={"menuSeq": seq}))
    r.raise_for_status()
    doc = HTMLParser(r.text)

    # 설명은 .txt_area 안에 <p> 여러 개로 들어온다. 첫 문단이 상품 소개고
    # 그 뒤는 '■ 알레르기 유발 성분' 같은 고지사항이라 뺀다.
    desc = ""
    area = doc.css_first(".txt_area")
    for p in area.css("p") if area else []:
        t = _clean(p.text())
        if t and not t.startswith(("■", "*", "※")):
            desc = t
            break

    # .i_tit 의 li.eng 는 [영문명, '* only ICE'] 순이다. 온도 표기만 라벨로 쓴다.
    labels = []
    for li in doc.css(".i_tit li.eng"):
        m = re.search(r"only\s+(ICE|HOT)", _clean(li.text()), re.I)
        if m:
            labels.append(m.group(1).upper())
    return desc, labels


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client(headers={"Referer": LIST_URL}) as c:
        r = base.retry(lambda: c.get(LIST_URL))
        r.raise_for_status()
        cards = HTMLParser(r.text).css(".cate a[href*='goViewB']")
        # 목록이 통째로 비면 조용한 0건 수집이 된다. 예외로 올려 드러낸다.
        if not cards:
            raise RuntimeError("매머드커피 신메뉴 0건 — 셀렉터가 깨졌을 수 있다")

        pending = []                                  # (Item, menuSeq)
        for card in cards:
            name = _clean(card.css_first("strong").text()) if card.css_first("strong") else ""
            if not name:
                continue
            eng = card.css_first(".eng")
            img = card.css_first("img")
            m = re.search(r"goViewB\((\d+)\)", card.attributes.get("href", ""))
            seq = m.group(1) if m else ""
            it = Item(
                brand=BRAND,
                name=name,
                name_en=_clean(eng.text()) if eng else "",
                image=_abs(img.attributes.get("src", "") if img else ""),
                is_new=True,
                url=f"{VIEW_URL}?menuSeq={seq}" if seq else "",
            )
            if it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)
            if seq:
                pending.append((it, seq))

        for it, seq in pending[:MAX_DETAILS]:
            time.sleep(DELAY)
            it.desc, it.labels = _detail(c, seq)

    return items
