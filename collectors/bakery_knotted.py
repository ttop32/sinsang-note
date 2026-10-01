"""노티드.

정본 도메인은 `knottedstore.com` 이다. `knotted.co.kr`·`knotted.kr` 은 같은 자리표시
호스트고 `cafeknotted.com` 은 미국 법인이라 전부 다른 사이트다. 푸터의 사업자등록번호
248-81-00620(주식회사 지에프에프지)로 확인했다.

**http 로 붙는다. verify=False 를 쓰지 않는다.** TLS 인증서가 2026-09-06 에 만료됐고
(notAfter=Sep 6 23:59:59 2026 GMT) 평문 HTTP 는 정상이다. `CRAWLING-POLICY.md` §6-1 이
이 경우를 '`http://` 로 수집한다. 허용'으로 정해 뒀다. 검증을 끄면 만료를 못 보고
지나가므로 끄지 않는다.

아임웹(imweb)이고 /menu 한 번(약 1MB)에 전 메뉴가 SSR 로 들어온다. 2026-09-30 실측.
갤러리 위젯 하나가 상품 목록이고 캡션 div 에 이름이 들어 있다.

  GET http://www.knottedstore.com/menu → ._item.item_gallary 129개

**129개 중 상품은 79개다.** 나머지는 매장 42개와 포장옵션 6개, 빈 항목이다.
캡션의 <p>(부제)가 매장이면 주소, 옵션이면 '1봉 5개(최대 10봉) - 0원' 처럼 채워져
있고 상품만 비어 있어서 그걸로 가른다. 위젯 순서로 자르지 않는 건 순서가 바뀌면
매장이 상품으로 새기 때문이다.

**NEW 문자열을 세지 않는다.** 홈 HTML 에 NEW 가 41회 나오지만 37회가

    <div class="ns-icon"> <!--<span class="new bg-brand">NEW</span>--> …

형태의 주석이다. 파서로 살아있는 노드를 세면 `.ns-icon .new` 가 0개다. 아임웹 테마에
배지 슬롯은 있는데 브랜드가 꺼 놨다. 문자열 카운트로 판정했으면 오판이었다.
배지가 꺼져 있을 뿐 '신제품이 아니다'라고 선언한 건 아니므로 is_new 는 None 으로
두고 신제품 판정은 collect 의 어제 대비 diff 에 맡긴다.

**날짜는 uploaded_at 까지만 쓴다.** 이미지 경로가 cdn.imweb.me/thumbnail/YYYYMMDD/ 라
등록 시점이 드러나고 79건 전부에 붙는다. 다만 고유 일자가 32개뿐이고 2024-03-14
하루에 13건이 몰려 있다(이미지 일괄 재등록). 출시일로 올리면 그날 13종이 나온 걸로
오보가 난다. 모달 코드(m20260902…)에도 같은 날짜가 박혀 있지만 이미지 쪽이
커버리지가 낫고 둘이 어긋나는 건도 많아 이미지 경로만 본다.

url 은 비운다. 카드 링크가 `javascript:SITE.openModalMenu(...)` 라 상품별 주소가
서버에 존재하지 않는다. base.SITES 의 브랜드 메뉴 URL 로 떨어진다.

robots.txt: 200 text/plain 215B, 본문 첫 글자 'U'. 아임웹 기본 템플릿이고
/menu 는 제한 밖이다. `Disallow: /?mode*` 라는 쿼리스트링 규칙이 있는데 우리는
`?mode=` 를 붙이지 않는다. 이용약관 문서는 사이트에서 찾지 못했다.

가격은 /menu 에 없다. 홈의 배송상품(.shop-item)에는 있지만 그건 굿즈·선물세트라
메뉴가 아니고, Item 에 price 필드도 없어서 담지 않는다.
"""
import re

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "노티드"
# TLS 만료(2026-09-06)로 http 전용. 위 docstring 참고.
MENU = "http://www.knottedstore.com/menu"

_DATE = re.compile(r"/thumbnail/(\d{4})(\d{2})(\d{2})/")


def _caption(item):
    """숨겨진 캡션 div. h4 가 이름, p 가 부제(매장 주소·옵션 가격)다."""
    cap = item.css_first("[id^=caption_]")
    if cap is None:
        return "", ""
    h4, p = cap.css_first("h4"), cap.css_first("p")
    return (" ".join(h4.text().split()) if h4 else "",
            " ".join(p.text().split()) if p else "")


def _image(item) -> str:
    """원본 이미지. 없으면 배경으로 깔린 썸네일이라도 쓴다."""
    tw = item.css_first(".text_wrap")
    src = tw.attributes.get("data-src", "") if tw else ""
    if src:
        return src
    iw = item.css_first(".img_wrap")
    bg = iw.attributes.get("data-bg", "") if iw else ""
    m = re.search(r"url\((.*?)\)", bg)
    return m.group(1) if m else ""


def _uploaded_at(src: str) -> str:
    """이미지 경로의 등록 날짜. 출시일이 아니라서 released_at 에는 안 넣는다."""
    m = _DATE.search(src or "")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(MENU))
        r.raise_for_status()

        for node in HTMLParser(r.text).css("._item.item_gallary"):
            name, sub = _caption(node)
            # 부제가 있으면 매장(주소)이거나 포장옵션(가격)이다. 상품은 비어 있다.
            if not name or sub:
                continue
            it = Item(brand=BRAND, name=name)
            if it.key in seen:
                continue
            seen.add(it.key)

            img = _image(node)
            it.image = img
            it.uploaded_at = _uploaded_at(img)
            items.append(it)
    return items
