"""샐러디.

⚠️ 이용약관 제12조 2항이 수집·재배포를 막는다. 2026-09-30 실측(`/popup/location`):

    2. 이용자는 '회사'의 서비스를를 이용함으로써 얻은 정보를 '회사'의 사전 승낙 없이
       복제, 송신, 출판, 배포, 방송 기타 방법에 의하여 영리목적으로 이용하거나
       제3자에게 이용하게 하여서는 안됩니다.

`base.py` 가 폴바셋을 같은 사유로 '수집하되 기록' 처분한 것과 사실상 같은 문구다.
운영자 방침("robots 는 열려 있고 약관만 금지면 수집하되 기록")에 따라 붙이되,
여기 남겨 둔다. 삭제 요청이 오면 다투지 말고 즉시 내린다.
한 가지 차이는 이 약관이 제1·2조에서 '샐러디 모바일 Application 회원'을 대상으로
정의한다는 점이다(이디야와 같은 구조). 비회원이 공개 웹페이지만 읽는 경우에
구속력이 있는지는 다툼의 여지가 있으나, 그 판단은 우리 몫이 아니라 브랜드 몫으로 둔다.
robots.txt 는 200 `User-agent: * / Allow: /` — 경로 제한 없음.

목록은 라인이 둘이다(매장 타입이 갈린다). SSR 이고 브라우저 불필요.
  /menu/list_1              — 43건(새로운 메뉴·베스트 메뉴 제외 기준)
  /menu2/list_1?menu2=1     — 45건
두 라인에 같은 상품이 겹쳐 실리므로 Item.key 로 합친다.

`list_2?type=topping` / `list_3?type=side` 는 받지 않는다. 2026-09-30 실측 결과
상품 목록이 아니라 재료 토핑표(양파·토마토·견과류…)고, `.menu_list` 구조가 아니며
NEW 배지가 0건이다. 조사 문서는 라인당 3장씩 6요청을 예상했는데 실제로 쓸모 있는 건
라인당 1장, 총 2요청이다.

신제품 신호:
  is_new  `<b class="tagbox"><span class="new">NEW</span></b>`. 브랜드가 골라 다는
          배지라 없으면 '신제품 아님'으로 보고 False 를 준다(폴바셋 선례).
          같은 상품이 '새로운 메뉴' 섹션과 카테고리 섹션에 중복으로 실려 배지 수가
          상품 수의 두 배로 보인다 — 2026-09-30 line1 배지 6개 = 실제 3건,
          line2 배지 4개 = 실제 2건, 두 라인 합쳐 고유 3건이다.
          조사 문서의 "NEW 6 / NEW 4" 는 배지 수를 센 것이라 실제 건수와 다르다.
  released_at  비운다. 목록·상세 어디에도 날짜가 없다.
  uploaded_at  비운다. 이미지 파일명 앞의 `2038866161` 은 시각처럼 보이지만
          모든 파일에 동일하게 붙는 게시판(superboard) 접두사다. 날짜가 아니다.

labels 에는 NEW 를 뺀 나머지 태그(BEST / LOW SUGAR / VEGAN)를 담는다.
promo 는 쓰지 않는다. 할인·행사 표시가 없다.
"""
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "샐러디"
HOST = "https://salady.com"
DELAY = 2.0

# (경로, 쿼리). 두 라인은 취급 메뉴가 갈리고 상품 idx 체계도 서로 다르다.
LINES = [
    ("/menu/list_1", None),
    ("/menu2/list_1", {"menu2": "1"}),
]

# 상품 카테고리가 아니라 편집 섹션. 여기 실린 건 아래 카테고리 섹션과 중복이다.
SECTION_TITLES = {"새로운 메뉴", "베스트 메뉴"}


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _abs(src: str) -> str:
    if not src:
        return ""
    # 이미지 src 에 기본 포트가 박혀 나온다(https://salady.com:443/…). 군더더기라 턴다.
    src = src.replace("https://salady.com:443/", "https://salady.com/")
    return src if src.startswith("http") else HOST + src


def _name_en(info) -> str:
    """`.info p` 안에서 태그박스를 뺀 나머지가 영문명이다."""
    p = info.css_first("p") if info else None
    if not p:
        return ""
    tags = p.css_first(".tagbox")
    text = p.text()
    if tags:
        text = text.replace(tags.text(), " ")
    return _clean(text)


def fetch() -> list[Item]:
    items: list[Item] = []
    by_key: dict = {}
    with base.client() as c:
        for path, params in LINES:
            r = base.retry(lambda: c.get(HOST + path, params=params))
            r.raise_for_status()
            boxes = HTMLParser(r.text).css(".menu_list .list_box")
            if not boxes:
                raise RuntimeError(f"샐러디 {path}: 목록 0건 — 셀렉터가 깨졌을 수 있다")

            for box in boxes:
                h5 = box.css_first(".title h5")
                title = _clean(h5.text()) if h5 else ""
                category = "" if title in SECTION_TITLES else title

                for li in box.css("ul > li"):
                    info = li.css_first(".info")
                    h6 = info.css_first("h6") if info else None
                    name = _clean(h6.text()) if h6 else ""
                    if not name:
                        continue
                    tags = [_clean(s.text()) for s in li.css(".tagbox span")]
                    tags = [t for t in tags if t]
                    a = li.css_first("a")
                    img = li.css_first("img")

                    it = by_key.get(base.make_key(BRAND, name))
                    if it:
                        # '새로운 메뉴'·'베스트 메뉴' 섹션과 카테고리 섹션에 같은 상품이
                        # 두 번 실리고, 두 라인에도 겹친다. 신호만 합치고 한 건으로 둔다.
                        it.is_new = it.is_new or ("NEW" in tags)
                        for t in tags:
                            if t != "NEW" and t not in it.labels:
                                it.labels.append(t)
                        if not it.category and category:
                            it.category = category
                        continue

                    it = Item(
                        brand=BRAND,
                        name=name,
                        name_en=_name_en(info),
                        image=_abs(img.attributes.get("src", "") if img else ""),
                        labels=[t for t in tags if t != "NEW"],
                        category=category,
                        is_new=("NEW" in tags),
                        url=_abs(a.attributes.get("href", "") if a else ""),
                    )
                    by_key[it.key] = it
                    items.append(it)

            time.sleep(DELAY)
    return items
