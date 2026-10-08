"""파스쿠찌(CAFFE PASCUCCI). (주)파리크라상 — SPC 계열이다.

pascucci.co.kr 과 caffe-pascucci.co.kr 이 같은 호스트(210.116.76.120)이고
후자는 전자로 301 된다. 고전적인 ASP SSR 이라 브라우저가 필요 없다.

  /product/productList.asp?typeCode=<8자리>   분류별 상품 목록(페이징 없음)
  /product/ajax/productDetail.asp (POST productSeq=)   상세 조각

## 🔴 "신제품 신호 없음" 은 오판이었다 — 배지가 **이미지 태그**다

1차 조사가 "NEW/New 가 전부 'NEWS' 메뉴 이름" 이라며 접었던 곳이다. 그
판정은 **문자열 `NEW` 를 센 결과**였고, 파스쿠찌 배지에는 그 글자가 없다.

    <div class="icon"><img src="/lib/images/contents/ic_pro_new.png" alt="신제품"></div>

배지가 `<img>` 다. 파일명이 `ic_pro_new.png`, alt 가 **한글 '신제품'** 이라
`NEW`·`new`·`badge`·`label` 어느 것으로 세도 0건이 나온다. DOM 노드를 봐야
보인다.

**전수 실측(2026-10-03) — 분류 19면 297건 중 7건(2.4%)에만 붙어 있다.**

    3673 아이스 여주 고구마 라떼 · 3672 여주 고구마 라떼 · 3671 여주쌀 라떼
    3670 여주쌀 그라니따 · 3669 여주쌀 젤라또 · 3668 에그베이컨 프레쉬 샌드위치
    3667 크런치 두부칩 흑임자

교차검증이 깨끗하다 — 배지 7건이 **productSeq 최상위 7개와 정확히 같고 중간에
구멍이 없다**(3667~3673 연속). 전건에 붙은 가짜 배지(퀴즈노스 66/66·버거운버거
58/58)도 아니고, 아무 데나 붙은 것(버거킹 31%)도 아니다. 분류별로도 시즌음료 4·
젤라또 1·델리 1·디저트 1 로 흩어져 있어 '한 카테고리를 통째로 NEW 로 찍은' 것도
아니다.

## 썸네일 합성 배지는 **없다**(요청대로 확인했다)

컴포즈커피 선례가 있어 297장을 전부 받아 확인했다.
  - 네 귀퉁이 1/4 의 '흰색 아님' 비율 1,188개(297장×4)를 셌다. 분포가
    0.0 에 1,058개, 0.1~0.5 에 82개, 1.0 에 48개다. **1.0 쪽 48개(12장)는
    배지가 아니라 배경이 검은 상품컷**이다(캡슐커피 박스·츄러스·파운드케이크·
    티 파우치·블랙 머그 등). 배지로 갈리는 틈이 없다.
  - 297장을 80px 로 줄여 전수를 눈으로 훑었다. 배지가 합성된 그림은 0장이다.
  파스쿠찌는 배지를 썸네일에 굽지 않고 DOM 으로 얹는다. 위 `.icon` 이 그것이다.

## 날짜는 없다 — 그리고 파일명 숫자를 날짜로 쓰지 않는다

상세 조각에 등록일·출시일이 없다(이름·설명·가격·영양정보뿐). 공지사항 18건은
해피포인트·개인정보처리방침 같은 운영 공지뿐이고, 이벤트 9건은 제휴 할인이라
상품이 아니다. 보도자료 메뉴는 HTML 주석 처리돼 있다.

⚠️ 솔깃한 함정이 하나 있다. 신상 7건 중 6건의 이미지 파일명이 `0928_…`,
1건이 `0930_…` 으로 **MMDD 처럼 보인다**(오늘이 2026-10-03 이니 말이 된다).
그런데 같은 자리에 `2405_`·`2407_`·`2501_` 로 시작하는 파일이 4건 더 있다 —
이쪽은 MMDD 로 읽으면 24월·25월이고 **YYMM** 으로 읽어야 말이 된다. 한 필드에
두 규칙이 섞여 있으니 날짜로 못 쓴다. released_at·uploaded_at 둘 다 비운다.
나머지 286건은 `f_17945.png` 처럼 접두 자체가 없다.

이미지 Last-Modified 도 쓰지 않는다(컴포즈커피 149건 일괄 재업로드 선례).

## is_new 를 False 로 찍지 않는 이유

배지가 없는 290건에 `is_new=False` 를 주면 "브랜드가 신제품이 아니라고 말했다"
가 되고, 날짜가 없는 이 브랜드에서는 그게 곧 **영구 배제**다(rules.is_fresh 의
is_new is False 분기는 released_at 을 요구한다). 배지를 다는 걸 한 번 빠뜨리면
그 상품은 영영 못 올라온다. 그래서 None(모름)으로 두고 diff 경로를 살려 둔다 —
합류 첫날 기준선이 막아주므로 카탈로그가 통째로 신상이 될 염려는 없다.

## 분류

depth2(커피·음료·케이크·푸드·상품) 5개는 **첫 자식의 목록을 그대로 돌려준다**
(커피 5건 = 이탈리안커피 5건). 그래서 leaf 19면만 돈다 — 합계가 정확히 297 로
떨어지고 중복이 없다.

텀블러 24 · 머그 31 · 기타상품 18 = **73건은 굿즈**라 nonfood 로 표시한다
(전건 눈으로 확인했다 — 트레이·캐니스터·드리퍼·모카포트·와인 스토퍼). 반면
원두 11(드립백·캡슐)과 티 22(티트라 티백)는 먹는 것이라 그대로 둔다.

robots.txt 는 `Disallow: /cucciman/` 과 `/upload/` 두 줄뿐이다. 상품 목록
(/product/)은 막혀 있지 않고, 사진이 /upload/ 아래다 — 운영자 판단으로 수집하되
UA 는 위장하지 않는다(이마트24·도미노피자와 같은 칸).
"""
import time
import urllib.parse

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "파스쿠찌"
SITE = "https://www.pascucci.co.kr"
LIST_URL = f"{SITE}/product/productList.asp"
DETAIL_URL = f"{SITE}/product/ajax/productDetail.asp"
DELAY = 2.0
MAX_DETAILS = 30     # 폭주 방지. 상세는 신상(배지)에만 받는다 — 현재 7건.

# 분류 leaf 코드 → 화면에 쓸 이름. depth2(00010010 커피 등 5개)는 첫 자식과
# 같은 목록을 돌려주므로 넣지 않는다(위 docstring §분류).
CATEGORIES = {
    "00100010": "이탈리안커피", "00100020": "커피(HOT)",
    "00100030": "커피(ICED)", "00100040": "콜드브루",
    "00200010": "시즌음료", "00200020": "그라니따",
    "00200030": "티", "00200050": "기타음료",
    "00210010": "조각케이크", "00210020": "홀케이크",
    "00300010": "젤라또", "00300020": "델리",
    "00300030": "브레드", "00300040": "디저트",
    "00400010": "원두", "00400011": "티(상품)",
    "00400020": "텀블러", "00400030": "머그", "00400060": "기타상품",
}

# 굿즈 분류. 73건 전건을 눈으로 확인했다(위 docstring §분류).
GOODS_CATEGORIES = {"텀블러", "머그", "기타상품"}

# 신제품 배지 이미지. 글자가 아니라 파일명으로 가른다.
NEW_ICON = "ic_pro_new"


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _abs(src: str) -> str:
    """사진 주소. 파일명에 한글이 들어 있어 경로를 퍼센트 인코딩한다."""
    if not src:
        return ""
    if src.startswith("http"):
        return src
    return SITE + urllib.parse.quote(src)


def _desc(c, seq: str) -> str:
    """상세 조각의 제품 설명. <br/> 로 줄바꿈이 들어 있어 한 줄로 편다."""
    r = base.retry(lambda: c.post(DETAIL_URL, data={"productSeq": seq}))
    r.raise_for_status()
    node = HTMLParser(r.text).css_first(".productDetail p.desc")
    if not node:
        return ""
    # 주의사항(`* 구운 여주쌀 원료 특성상…`)은 설명이 아니라 고지라 끊는다.
    txt = _clean(node.text())
    return _clean(txt.split("*")[0])


def fetch() -> list[Item]:
    items: dict[str, Item] = {}      # productSeq → Item. 분류가 겹쳐도 한 번만.

    with base.client(headers={"Referer": LIST_URL}) as c:
        for n, (code, label) in enumerate(CATEGORIES.items()):
            if n:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST_URL, params={"typeCode": code}))
            r.raise_for_status()
            cards = HTMLParser(r.text).css("a.product")
            if not cards:
                continue
            for a in cards:
                seq = a.attributes.get("data-productseq", "")
                h2 = a.css_first("h2")
                name = _clean(h2.text()) if h2 else ""
                if not seq or not name or seq in items:
                    continue
                en = a.css_first(".titleEng")
                img = a.css_first(".proListImg img")
                icon = a.css_first(".icon img")
                is_new = bool(icon and NEW_ICON in (icon.attributes.get("src") or ""))
                items[seq] = Item(
                    brand=BRAND,
                    name=name,
                    name_en=_clean(en.text()) if en else "",
                    image=_abs(img.attributes.get("src", "") if img else ""),
                    category=label,
                    # 배지가 없는 건 '모름'이다. False 로 찍지 않는 이유는 docstring.
                    is_new=True if is_new else None,
                    nonfood=label in GOODS_CATEGORIES,
                    url=f"{LIST_URL}?typeCode={code}&productSeq={seq}",
                )

        # 분류가 통째로 비면 조용한 부분수집이 된다. 예외로 올려 드러낸다.
        if len(items) < 150:
            raise RuntimeError(f"파스쿠찌 {len(items)}건 — 상품 목록 구조가 "
                               "바뀌었을 수 있다")

        # 설명은 상세 조각에만 있다. 화면에 오를 신상에만 받는다(297건을 다 받으면
        # 10분이고, 그 대부분은 배지도 날짜도 없어 애초에 안 올라간다).
        fresh = [it for it in items.values() if it.is_new]
        for it in fresh[:MAX_DETAILS]:
            seq = it.url.rsplit("productSeq=", 1)[-1]
            time.sleep(DELAY)
            it.desc = _desc(c, seq)

    return list(items.values())
