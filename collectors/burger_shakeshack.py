"""쉐이크쉑 — SPC 가 돌리는 한국 공식 사이트의 메뉴 한 장.

⚠️ **https 가 아니라 http 다.** `www.shakeshack.kr`·`shakeshack.kr` 둘 다
443 이 **Connection refused** 이고(2026-10-02 실측) 80 만 열려 있다. 80 은
`main.jsp` 로 보내는 2줄짜리 리다이렉트 셸이다. `verify=False` 로 풀 문제가
아니다 — 포트가 아예 안 열려 있다. `shakeshackkorea.com` 류 대체 도메인은
DNS 가 안 풀린다. 글로벌 `shakeshack.com` 은 미국 메뉴라 쓸 수 없다.

http 라서 **이미지는 화면에 안 뜬다.** `base.derive()` 가 혼합 콘텐츠를 막으려고
`http://` 이미지를 지운다(에그드랍·노티드 선례). 그래도 주소는 채워 둔다 —
사이트가 https 를 열면 그날부터 사진이 살아난다.

    GET http://shakeshack.kr/sub/menu.jsp     (70KB, 완전 SSR, 요청 1회)

## 신제품 신호 — 썸네일 `<p>` 의 `limited` 클래스

메뉴 카드가 이렇게 생겼다.

    <li>
      <p class="menu-image limited" style="background:url('/resources/images/menu/burger_261001.jpg')"></p>
      <h3>Shackhouse BBQ Burger<span></span></h3>
      <h3 class="h3-kr">쉑하우스 바비큐 버거</h3>
      <p class="body-normal-kr …">…스모키 BBQ 소스와 훈연 베이컨을 더해… 시즌 한정 버거</p>

`limited` 가 브랜드가 직접 붙이는 '시즌 한정' 표시다. 페이지 맨 위의
`LIMITED-TIME OFFER / 시즌 한정 메뉴` 배너와 짝을 이룬다.

🔎 **대문자 `NEW` 를 세면 안 된다.** 이 페이지의 `NEW` 는 1회뿐이고
`신메뉴` 5회는 전부 **SEO 키워드 메타와 주석 처리된 문단**이다. 화면에 뜨는
배지가 아니다. 클래스로만 가른다.

## 교차검증 — 이미지 파일명의 날짜가 보도자료 날짜와 맞는다

썸네일 파일명이 `burger_261001.jpg` 처럼 `_YYMMDD` 다. 2026-10-02 전수 실측
(메뉴 55건) 결과 `limited` 는 6건이고 그중 5건이 `261001` 이다.

| limited | 파일명 날짜 | 상품 |
|---|---|---|
| ✅ | 2026-10-01 | 쉑하우스 바비큐 버거 · 쉑하우스 바비큐 치킨 · 쉑하우스 바비큐 프라이 · 스모어 쉐이크 · 피치레몬에이드 |
| ✅ | 2026-03-06 | 어니언링 ← **반례.** 봄 시즌 한정이었는데 7개월째 클래스가 안 내려갔다 |

`/sub/newsnevent.jsp` 의 2026.10.01 자 글 「가을 한정 '쉑하우스 바비큐' 시리즈
출시」가 본문에서 **버거·치킨·프라이·스모어 쉐이크 4종**을 이름까지 들어
설명한다. 메뉴 쪽 `261001` 5건 중 4건이 그 글과 글자까지 같다(나머지
피치레몬에이드는 같은 날 올라온 한정 음료로, 글에는 없다). 배지와 보도자료가
서로를 받쳐준다.

반례(어니언링)가 있으니 **배지만 믿으면 안 된다.** 그래서 파일명 날짜를
`uploaded_at` 에 같이 넣는다. `rules.is_fresh` 가 `is_new=True` 라도 날짜가
창 밖이면 내리므로 어니언링은 자동으로 걸러진다. 배지·날짜 둘 다 있을 때만
화면에 오른다.

날짜는 `released_at` 이 아니다. 파일명이 알려주는 건 이미지를 올린 날이다
(`notes/BRAND-CANDIDATES.md` §6-5). 일괄 재업로드 봉우리는 없다 — 55건이
2023-08 ~ 2026-10 에 흩어져 있고 같은 날 최다가 4건(`dog_260429_0N`)이다.

`limited` 가 없는 카드는 `is_new=None` 이다. False 가 아니다 — '여긴 한정이
아님' 을 명시하는 표시가 따로 없다(프랭크버거 `icon_none` 과 다르다).
날짜가 아예 없는 상시 메뉴(`burger_shackstack.jpg` 처럼 파일명이 영문)는
`uploaded_at` 도 비니 diff 경로로 간다.

## 담지 않는 것

`/sub/newsnevent.jsp` 는 교차검증에만 썼다. 그쪽 글 제목이 시리즈 단위
(`'쉑하우스 바비큐' 시리즈 4종`)라 상품명을 본문에서 지어내야 하는데, 메뉴
페이지가 개별 이름을 이미 정확히 주고 있어 쓸 이유가 없다. 매장 오픈·1+1
행사 글도 섞여 있다.

가격(`W 10,9` = 10,900원 표기)은 Item 에 자리가 없어 버린다. 상품별 주소도
없다 — 카드의 유일한 링크는 전 상품이 공유하는 해피콘 '구매하기' 외부
주소다. `url` 은 비우고 `base.SITES` 폴백에 맡긴다.

robots.txt 는 404(HTML)다. 이용약관에 수집 금지 조항은 찾지 못했다.
"""
import re

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "쉐이크쉑"
ROOT = "http://shakeshack.kr"          # 443 이 refused 다. https 로 바꾸지 마라.
MENU_URL = ROOT + "/sub/menu.jsp"
MAX_ITEMS = 300                        # 폭주 방지. 현재 55건.

LIMITED_CLASS = "limited"              # 브랜드가 붙이는 '시즌 한정' 표시

_BG_URL = re.compile(r"url\(\s*['\"]?([^'\")]+)")
# 파일명 꼬리의 `_YYMMDD`. 뒤에 `_01` 같은 일련번호가 더 붙기도 한다.
_FILE_DATE = re.compile(r"_(\d{2})(\d{2})(\d{2})(?:_\d+)?\.(?:jpg|jpeg|png|webp)$", re.I)
_TM = re.compile(r"\s*(?:TM|™)\s*$")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _image(node) -> str:
    """썸네일이 <img> 가 아니라 style 의 background-image 로 들어 있다."""
    m = _BG_URL.search(node.attributes.get("style", "") if node is not None else "")
    if not m:
        return ""
    src = m.group(1).strip()
    if src.startswith("http"):
        return src
    # `../resources/…` 와 `/resources/…` 가 섞여 있다. 둘 다 사이트 루트 기준이다.
    return ROOT + "/" + src.lstrip("./")


def _uploaded_at(src: str) -> str:
    """파일명 꼬리 `_YYMMDD` 가 업로드 날짜다. 없으면 빈 문자열."""
    m = _FILE_DATE.search(src or "")
    if not m:
        return ""
    yy, mm, dd = m.groups()
    return f"20{yy}-{mm}-{dd}"


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(MENU_URL))
        r.raise_for_status()

    doc = HTMLParser(r.text)
    tabs = doc.css("div.tab_content")
    if not tabs:
        raise RuntimeError(f"{MENU_URL}: div.tab_content 가 0개다(마크업이 바뀌었다)")

    items: list[Item] = []
    seen = set()
    for tab in tabs:
        h2 = tab.css_first("h2")
        kr = h2.css_first(".h2-kr") if h2 is not None else None
        category = _clean(kr.text()) if kr is not None else _clean(h2.text() if h2 else "")
        for li in tab.css(".ss-menu-list li"):
            thumb = li.css_first("p.menu-image")
            headings = li.css("h3")
            if len(headings) < 2:
                continue                      # 영문·한글 h3 두 줄이 한 쌍이다
            name = _clean(headings[1].text())
            name_en = _TM.sub("", _clean(headings[0].text()))
            if not name:
                continue
            desc = li.css_first("p.body-normal-kr")
            src = _image(thumb)
            limited = LIMITED_CLASS in (
                (thumb.attributes.get("class") or "").split() if thumb is not None else [])
            it = Item(
                brand=BRAND,
                name=name,
                name_en=name_en,
                desc=_clean(desc.text()) if desc is not None else "",
                image=src,
                labels=["시즌 한정"] if limited else [],
                category=category,
                uploaded_at=_uploaded_at(src),
                is_new=True if limited else None,
            )
            if it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)
            if len(items) > MAX_ITEMS:
                raise RuntimeError(f"{BRAND}: 상품이 {MAX_ITEMS}건을 넘었다")

    if not items:
        raise RuntimeError(f"{MENU_URL}: 메뉴 카드에서 상품을 하나도 못 뽑았다")
    return items
