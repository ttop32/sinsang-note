"""명랑핫도그.

메뉴 대분류에 NEW 가 있어 신제품이 URL 로 분리돼 있다.
/menu/new(=/menu/new.html) 가 SSR 이고 UTF-8, 브라우저 불필요, 1요청이면 끝난다.
요거프레소와 같은 CMS 라 마크업 구조가 거의 같다.

robots.txt 는 `Allow: /` 에 `/sadmin/` 만 제외다(2026-09-30 재확인).
AI 봇을 여럿 이름 붙여 `Allow: /` 로 따로 열어 두기까지 했다.
⚠️ 다만 이용약관(/policy/term.html)이 요거프레소와 **한 글자도 다르지 않은**
제작사 템플릿이고 내용이 **도메인 등록 서비스 약관**이다. 브랜드의 의사표시로
보기 어렵다.

신제품 신호 — 2026-09-30 실측.
  - 카드의 `.img-wrap` 클래스에 `new` 가 붙는다. /menu/new 의 7건 전부에 있고,
    다른 분류(/menu/menu.html?depth1=4 핫도그 12건)에는 **한 건도 없다.**
    켜고 끄는 배지라는 뜻이라 그대로 is_new=True 로 쓴다.
  - 날짜를 말해주는 자리는 없다. 썸네일 경로 /upload/product/202604/…_20260415094353.png
    의 꼬리는 파일 업로드 시각이라 uploaded_at 까지만 쓴다. 202604·202511·202605
    세 덩어리로 흩어져 있어 일괄 재업로드 흔적은 아니다.

**조사 내용과 다르다.** "캐러셀 중복이 심해 같은 세트가 8번 반복된다"고 돼 있는데
/menu/new 에는 중복이 **없다**(7건 7키). 조사가 본 반복은 이 페이지가 아니라
다른 화면의 캐러셀로 보인다. 그래도 계약대로 Item.key 로 접고 들어간다.

이 브랜드는 상품명이 '명랑's 치즈스틱(오리지널/내슈빌/허니 치폴레)' 처럼
괄호로 맛을 가르는 3종 묶음이 둘이다. base.make_key 가 사이즈·온도 표기만 털고
맛 표기는 남기도록 돼 있어서 6건이 그대로 살아남는다. 괄호를 통째로 지우던
예전 규칙이었다면 각각 1건으로 합쳐졌을 자리다.

url 은 카드가 가리키는 /pop/menu-popup.html?uid=N 을 그대로 쓴다. 팝업용 조각
페이지라 헤더·푸터가 없지만, 영양성분·알레르기 성분이 들어 있는 그 상품의
브랜드 공식 페이지가 맞다. 가격 정보는 없다.
"""
import re
import time
from urllib.parse import urljoin

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "명랑핫도그"
ROOT = "https://myungranghotdog.com"
URL = ROOT + "/menu/new"
CATEGORY = "NEW"
DELAY = 2.0   # robots 에 Crawl-delay 는 없다. 1요청뿐이라 여유를 둔다.

# .img-wrap 의 아이콘 클래스 → 화면 라벨. origin·myungrang 은 '오리지널' 장식이라 뺀다.
ICONS = {"new": "NEW", "hot": "HOT"}


def _text(node, sel) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _image(card) -> str:
    """썸네일은 img[src] 가 아니라 .img-bx 의 background-image 에 들어 있다.

    img 태그는 base_360X360.webp 자리채움이라 그걸 담으면 전부 같은 그림이 된다.
    """
    n = card.css_first(".img-bx")
    if not n:
        return ""
    m = re.search(r"url\(['\"]?(.*?)['\"]?\)", n.attributes.get("style", ""))
    return urljoin(ROOT, m.group(1)) if m else ""


def _uploaded_at(img_url: str) -> str:
    """파일명 꼬리의 업로드 타임스탬프(_20260415094353.png)를 날짜로."""
    m = re.search(r"_(\d{4})(\d{2})(\d{2})\d{6}\.\w+$", img_url)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(URL))
        r.raise_for_status()
        time.sleep(DELAY)

        for card in HTMLParser(r.text).css("ul.gallery-menu-list > li"):
            name = _text(card, ".menu-name")
            link = card.css_first("a")
            if not name or not link:
                continue
            wrap = card.css_first(".img-wrap")
            classes = wrap.attributes.get("class", "").split() if wrap else []
            labels = [ICONS[c] for c in classes if c in ICONS]
            img = _image(card)
            it = Item(
                brand=BRAND,
                name=name,
                desc=_text(card, ".menu-dec"),
                image=img,
                labels=labels,
                category=CATEGORY,
                uploaded_at=_uploaded_at(img),
                # NEW 아이콘만 True. 없으면 모름(False 로 내릴 근거가 없다).
                is_new=True if "NEW" in labels else None,
                # href 가 '../pop/menu-popup.html?uid=50' 이라 /menu/ 기준으로 푼다.
                url=urljoin(URL, link.attributes.get("href", "")),
            )
            if it.key in keys:
                continue
            keys.add(it.key)
            items.append(it)
    return items
