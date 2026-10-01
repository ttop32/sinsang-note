"""CU(씨유).

product.do 는 껍데기만 내려주고, 목록은 /product/productAjax.do 에 listForm 의
hidden 값을 그대로 POST 해서 받는다. 쿠키·세션 없이 열리고 브라우저도 불필요.
'더보기' 버튼도 같은 엔드포인트를 pageIndex 만 올려 다시 부르는 구조다.

신상품만 따로 모은 목록은 없다(상단 메뉴는 전체 상품 / CU 차별화 상품 / 행사상품 셋뿐).
대신 카테고리별로 최신등록순(searchCondition=setC)으로 훑으면서 NEW 태그가 붙은 것만
거두고, 태그가 끊기는 페이지에서 멈춘다. 설명문은 목록에 없어서 상세(view.do)를
상품당 한 번씩 더 본다.

## NEW 배지는 진짜 선별 표시다 (2026-10-01 실측)

'666건이 전부 NEW 라 신호 값이 0' 이라는 의심을 원본 HTML 로 직접 대조했다.
어댑터가 NEW 인 것만 담고 나서 센 수라서 생기는 착시다. **거른 뒤가 아니라
거르기 전의 카드**를 세면:
  - 7개 카테고리에서 읽은 카드 **1,200건 중 NEW 가 667건(55.6%)**이다.
    어댑터가 무조건 True 를 넣는 게 아니라 `.tag .new` 가 실제로 있는 것만 담는다.
  - 최신등록순으로 내려가면 NEW 가 한 지점에서 뚝 끊기고 그 뒤로는 0이다.
    (음료 1p 35 → 2p 1 → 3p 0 / 식품 6p 35 → 7p 5 → 8p 1 → 9p 0 /
     과자류 5p 40 → 6p 5 → 7p 0 / 즉석조리는 1p 부터 3건뿐)
  - 카드 마크업의 개발자 주석이 태그 종류를 다 적어놨다:
    `<!-- [D] .tag > span .new : new / .best : best -->`. NEW·BEST 둘뿐이고
    더 좁은 배지(주차 표시·'이번주 신상' 같은 것)는 없다.
  - 정렬도 더 좁힐 게 없다. searchCondition 을 setA~setE 로 바꿔보면
    setA 와 setC 가 완전히 같고(최신등록순), setB 는 다른 축(인기로 보임),
    setD 는 0건, setE·빈값은 오래된순이다. 최신등록순이 이미 제일 좁다.

## 등록일: 상품 데이터엔 없고, 이미지 CDN 헤더에 있다 (2026-10-01 실측)

목록·상세 어디에도 날짜 필드가 없다. 상세 HTML 에서 날짜처럼 보이는 문자열
(2019-05-23·2022-02-18·20230829 …)은 **상품이 달라도 집합이 완전히 같다**.
gdIdx 28374(과자)와 20533(즉석조리)을 받아 대조했고 한 글자도 다르지 않았다.
개발자가 script 태그에 남긴 주석과 에셋 버전이지 상품 등록일이 아니다.
`/brand_info/news_list.do` 의 '새로운소식'도 쓸 수 없다 — 50건을 받아보면
'9월 모아보기'·'9월 쓔퍼세일'·'CU Pay 허브페이지'처럼 전부 월간 행사 공지이고
상품 출시 기사가 아니다.

대신 **상품 이미지의 Last-Modified 헤더**가 등록 시점을 준다.
이미지는 `//<CDN>/product/<바코드>.jpg` 라 경로엔 타임스탬프가 없지만, 헤더엔 있다.
NEW 667건 전부에 HEAD 를 쳐서 받아본 결과:
  - 667건 **전부** Last-Modified 가 있다. 날짜는 29종이고 월요일에 몰린다
    (09-29 78건 · 09-15 50건 · 09-07 60건 · 08-31 60건 · 08-24 53건 …).
    상품 사진을 주 단위 배치로 올리는 운영이라 해상도는 '주' 단위다.
  - 등록 일련번호 gdIdx 와의 **스피어만 상관이 0.991** 이다. 역전을 따로 세봐도
    gdIdx<27600 중 9월 이후 날짜 0건, gdIdx>=28200 중 8/2 이전 날짜 0건이다.
    즉 이 집합 안에선 사진 재업로드로 옛 상품이 최근 날짜를 얻는 오염이 없다.
  - 가장 오래된 NEW 가 2026-05-11 이다. **NEW 배지가 143일까지 붙어 있다**는 뜻이고,
    배지만으로는 '오늘의 신상'이 될 수 없다는 근거다. 그래서 이 날짜를
    uploaded_at 으로 넘겨 collect 의 60일 창에 걸리게 한다.

⚠️ 이건 출시일이 아니라 **사진을 올린 배치 시각**이다. 그래서 released_at 이 아니라
uploaded_at 에 넣는다. 도미노처럼 사이트 개편으로 사진을 일괄 재업로드하면
옛 상품이 최근 날짜를 갖게 된다 — 실제로 NEW 가 아닌 구상품에서 그런 건을 봤다
(gdIdx 24212 할리스 아메리카노, 사진 2026-09-01). NEW 배지가 그 오염을 막아주는
구조라, **NEW 로 거른 뒤에만** 이 날짜를 쓴다. 배지 없이 날짜만으로 뽑으면 안 된다.
HEAD 는 상품당 한 번뿐이고 바코드 주소라 값이 안 바뀌므로 desc 와 같은 캐시를 탄다.

그리고 이 날짜는 **빼는 데만 쓰고 넣는 데는 쓰지 않는다**. 행사 라벨이 붙은
상품에는 아예 채우지 않는다(`_fill_uploaded`). 근거가 약한 날짜 하나로
'행사 라벨이 붙은 건 신상으로 올리지 않는다'는 규칙을 뒤집지 않기 위해서다.
2026-10-01 실측으로 효과를 둘 다 재봤다:
  - 날짜를 전건에 채우면 화면 496 → 395. 158건이 빠지고 **57건이 새로 붙는데
    그 57건이 전부 1+1·2+1 행사 상품**이다(collect.is_fresh 가 날짜가 있으면
    행사 veto 를 건너뛴다).
  - 행사 상품을 빼고 채우면 화면 496 → 338. 빠지는 158건은 그대로고 새로
    붙는 건 0건이다. 순수 감산이라 이쪽을 쓴다.

가격은 목록·상세 모두 들고 있지만(예: 5,500원) Item 에 담을 자리가 없어 버린다.

robots.txt 는 cu.bgfretail.com 도 이미지 CDN 도 404(규칙 없음)다. 명시적 허용이
아니므로 요청 간격을 넉넉히 둔다.
"""
import datetime
import email.utils
import re
import time

import httpx
from selectolax.parser import HTMLParser

from . import base
from .base import UA, Item

BRAND = "CU"
LIST_URL = "https://cu.bgfretail.com/product/productAjax.do"
VIEW_URL = "https://cu.bgfretail.com/product/view.do"
REFERER = "https://cu.bgfretail.com/product/product.do?category=product&depth2=4"

# 전체상품 페이지의 3depth 탭. gomaincategory() 가 넘기는 코드값 그대로다.
CATEGORIES = {
    "10": "간편식사", "20": "즉석조리", "30": "과자류", "40": "아이스크림",
    "50": "식품", "60": "음료", "70": "생활용품",
}
MAX_PAGES = 20   # 폭주 방지. 현재 최대 9페이지(식품)에서 NEW 가 끊긴다.
DELAY = 0.15     # 요청 간격. 상세까지 합쳐 700회쯤 두드리므로 반드시 둔다.
IMG_DELAY = 0.05  # 이미지는 원본 서버가 아니라 CDN 이라 간격을 조금 좁게 둔다.

# 2026-10-01 실측 베이스라인. 아래 가드가 이 수치를 근거로 '조용한 0건'을 막는다.
MEASURED_CARDS = 1200   # 7개 카테고리에서 읽은 카드 수
MEASURED_NEW = 667      # 그 중 NEW 배지가 붙은 수


def _text(node, sel):
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _gd_idx(card) -> str:
    """상세 링크가 a 태그로 없고 onclick="view(28352);" 로만 상품코드가 나온다."""
    for sel in (".prod_img", ".name"):
        n = card.css_first(sel)
        m = re.search(r"view\((\d+)\)", n.attributes.get("onclick", "") or "") if n else None
        if m:
            return m.group(1)
    return ""


def _view_url(gd: str) -> str:
    """상품 상세 주소. gdIdx 를 못 뽑았으면 빈 값(브랜드 메뉴 페이지로 폴백된다)."""
    return f"{VIEW_URL}?category=product&gdIdx={gd}" if gd else ""


def _labels(card) -> list:
    """1+1·2+1 배지는 span 글자로, NEW·BEST 태그는 img alt 로 붙어 있다."""
    out = []
    for sp in card.css(".badge span, .tag span"):
        t = " ".join(sp.text().split())
        if not t:
            img = sp.css_first("img")
            t = (img.attributes.get("alt", "") or "").strip() if img else ""
        t = t.upper()
        if t and t not in out:
            out.append(t)
    return out


def _promo(card) -> bool:
    """행사 상품. 마크업 주석 그대로 .badge > span.plus1 = 1+1, .plus2 = 2+1."""
    return card.css_first(".badge .plus1, .badge .plus2") is not None


def _form(cat: str, page: int) -> dict:
    """listForm 의 hidden 필드 그대로. setC=최신등록순, listType=1 은 이어붙이기."""
    return {"pageIndex": str(page), "searchMainCategory": cat, "searchSubCategory": "",
            "listType": "1", "searchCondition": "setC", "searchUseYn": "N",
            "gdIdx": "0", "codeParent": cat, "search1": "", "search2": "",
            "searchKeyword": ""}


def _fill_desc(client, items: list, gd_by_key: dict, known: dict) -> int:
    """설명문은 목록에 없으니 상세를 상품당 한 번씩 긁는다. 실패하면 빈 값으로 둔다.

    설명문은 사실상 바뀌지 않는데 상품이 600건대라 매일 전량을 다시 긁으면
    하루 700요청이 된다. 이미 받아둔 건 재사용하고 새로 나타난 것만 긁는다.
    """
    fetched = 0
    for it in items:
        cached = known.get(it.key, {}).get("desc")
        if cached:
            it.desc = cached
            continue
        gd = gd_by_key.get(it.key)
        if not gd:
            continue
        fetched += 1
        try:
            r = client.get(VIEW_URL, params={"category": "product", "gdIdx": gd})
            r.raise_for_status()
        except httpx.HTTPError:
            continue
        finally:
            time.sleep(DELAY)
        tree = HTMLParser(r.text)
        it.desc = " ".join(" ".join(n.text().split())
                           for n in tree.css(".prodExplain li")).strip()
    return fetched


def _fill_uploaded(client, items: list, known: dict) -> int:
    """등록 시점. 상품 데이터엔 없고 이미지의 Last-Modified 헤더에만 있다.

    출시일이 아니라 사진을 올린 배치 시각이라 released_at 이 아니라 uploaded_at 이다.
    근거와 한계(주 단위 해상도, 재업로드 오염, NEW 로 거른 뒤에만 쓰는 이유)는
    모듈 docstring 에 적어뒀다.

    **행사 상품엔 날짜를 채우지 않는다.** 이 날짜는 '빼는 데'만 쓰고 '넣는 데'는
    쓰지 않는다는 뜻이다. collect.is_fresh() 는 날짜가 있으면 그걸 우선해서
    행사 라벨 veto 를 건너뛴다. 그런데 우리가 가진 건 출시일이 아니라 사진을 올린
    시각이라, 1+1 이 붙은 상품이 '갓 나와서 도입행사를 하는 것'인지 '옛 상품을
    행사에 올리며 사진을 다시 찍은 것'인지 구분해주지 못한다. 세븐일레븐
    '신상품' 탭이 바로 후자였다(해태 연양갱이 2+1 을 달고 신상품으로 올라온다).
    근거가 약한 날짜로 행사 veto 를 뒤집지 않는다 — 날짜를 채우면 행사 상품
    57건이 새로 화면에 오른다(2026-10-01 실측).

    desc 와 같은 이유로 캐시를 탄다 — 바코드 주소라 한 번 받은 값이 바뀌지 않는다.
    헤더가 없거나 실패하면 빈 값으로 둔다(없는 걸 지어내지 않는다).
    """
    fetched = 0
    for it in items:
        if it.promo:                       # 위 docstring: 행사 상품엔 안 채운다
            continue
        cached = known.get(it.key, {}).get("uploaded_at")
        if cached:
            it.uploaded_at = cached
            continue
        if not it.image:
            continue
        fetched += 1
        try:
            r = client.head(it.image)
            r.raise_for_status()
        except httpx.HTTPError:
            continue
        finally:
            time.sleep(IMG_DELAY)
        stamp = email.utils.parsedate(r.headers.get("last-modified") or "")
        if stamp:
            it.uploaded_at = datetime.date(*stamp[:3]).isoformat()
    return fetched


def fetch(known: dict | None = None) -> list[Item]:
    items: list[Item] = []
    gd_by_key: dict = {}
    seen_cards = 0
    headers = {"User-Agent": UA, "X-Requested-With": "XMLHttpRequest", "Referer": REFERER}
    with base.client(headers=headers) as c:
        for code, cat_name in CATEGORIES.items():
            for page in range(1, MAX_PAGES + 1):
                r = c.post(LIST_URL, data=_form(code, page))
                r.raise_for_status()
                cards = HTMLParser(r.text).css("li.prod_list")
                seen_cards += len(cards)
                # 카테고리 1페이지가 비는 건 정상일 수 없다(7개 전부 40건씩 온다).
                # 셀렉터나 폼 필드가 바뀌면 여기서 조용히 0건이 되므로 드러낸다.
                if page == 1 and not cards:
                    raise ValueError(
                        f"CU {cat_name}(code={code}) 1페이지가 비었다. "
                        f"응답 {len(r.text)}바이트 — li.prod_list 셀렉터나 "
                        f"listForm hidden 필드가 바뀌었는지 확인하라")

                fresh = 0
                for card in cards:
                    # 최신등록순이라 NEW 가 끊긴 뒤는 전부 구상품이다
                    if card.css_first(".tag .new") is None:
                        continue
                    fresh += 1
                    name = _text(card, ".name p")
                    if not name:
                        continue
                    img = card.css_first(".prod_img img")
                    src = (img.attributes.get("src", "") or "") if img else ""
                    gd = _gd_idx(card)
                    it = Item(
                        brand=BRAND,
                        name=name,
                        image="https:" + src if src.startswith("//") else src,
                        labels=_labels(card),
                        category=cat_name,
                        is_new=True,          # NEW 배지 = 브랜드가 붙인 최근등록 표시
                        promo=_promo(card),   # 1+1·2+1 은 행사로 따로 뺀다
                        # 상세는 어차피 _fill_desc 가 같은 gdIdx 로 긁는다. 요청은 안 늘고
                        # 사용자가 카드에서 바로 그 상품 페이지로 간다.
                        url=_view_url(gd),
                    )
                    if it.key in gd_by_key:
                        continue
                    gd_by_key[it.key] = gd
                    items.append(it)

                time.sleep(DELAY)
                # NEW 가 한 건도 없거나 더보기가 사라지면 이 카테고리는 끝
                if not cards or not fresh or "더보기" not in r.text:
                    break

        # NEW 가 전 카테고리에서 0건이면 그건 'CU 에 신상이 없는 날'이 아니라
        # .tag .new 가 바뀐 것이다(실측 1,200건 중 667건이 NEW 다).
        if not items:
            raise ValueError(
                f"CU 카드 {seen_cards}건을 읽었는데 NEW 가 0건이다 "
                f"(2026-10-01 실측 {MEASURED_CARDS}건 중 {MEASURED_NEW}건). "
                f"'.tag .new' 셀렉터가 바뀌었는지 확인하라")

        n = _fill_desc(c, items, gd_by_key, known or {})
        print(f"  CU 상세 요청 {n}건 (캐시 {len(items) - n}건)")

    # 이미지는 원본이 아니라 CDN 이라 커넥션을 따로 연다.
    # (원본용 X-Requested-With·Referer 를 CDN 에 보낼 이유가 없다.)
    with base.client() as ic:
        n = _fill_uploaded(ic, items, known or {})
    want = sum(1 for it in items if not it.promo)   # 행사 상품은 애초에 안 채운다
    dated = sum(1 for it in items if it.uploaded_at)
    print(f"  CU 이미지 HEAD {n}건 (캐시 {want - n}건) → 등록일 {dated}/{want}건 "
          f"(행사 {len(items) - want}건 제외)")
    # 대상 전량에 날짜가 안 붙으면 60일 창이 못 걸려 배지만으로 전량이 통과한다.
    # 실측은 666건 중 대상 전건에 헤더가 있었으므로 0건이면 헤더가 사라진 것이다.
    if want and not dated:
        raise ValueError(
            f"CU 비행사 {want}건 전부 이미지 Last-Modified 를 못 받았다 "
            "(2026-10-01 실측은 666건 전건에 헤더가 있었다). CDN 이 헤더를 "
            "끊었는지 확인하라 — 날짜 없이 NEW 배지만 믿으면 143일치가 통째로 올라온다")
    return items
