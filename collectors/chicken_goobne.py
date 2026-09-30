"""굽네치킨.

신제품 전용 페이지 /menu/new_p?gubun=new_menu_list 가 전부 SSR 이다. 브라우저 불필요.
다만 그 페이지에 상품 카드는 없다. 목록은 페이지 안의 JS 객체 tabMenuData 에 있고
(탭별로 {value: gubun, text: 상품명}), 실제 카드는 같은 URL 에 gubun 을 바꿔
AJAX 로 받아오는 HTML 조각이다. 그래서 목록 1요청 + 상품 N요청으로 읽는다.
2026-09-30 실측 8건이라 하루 9요청이다.

robots.txt 는 2026-09-30 재확인했다(§보고 참고). Disallow 는 /menu/new.jsp 와
/brd/notice/list 둘뿐이고 나머지는 Allow:/ 다. 우리 경로 /menu/new_p 는 접두어가
달라 can_fetch 가 True 이고, /menu/new.jsp 는 지금 404(JSON)를 돌려주는 죽은 경로다.
그래도 이름이 비슷해 오해 소지가 있으니, Disallow 가 /menu/new 접두어로 넓어지면
즉시 이 어댑터를 빼야 한다.

신제품 신호:
  - is_new  이 목록 자체가 브랜드가 고른 '신제품' 이라 전건 True 로 둔다.
  - uploaded_at  썸네일 경로의 /menu_new/260908_seoul/ 앞 6자리(YYMMDD)다.
    상품마다 캠페인 폴더가 따로 있고 날짜도 흩어져 있어(260602·260618·260713·260908)
    메가·노브랜드버거 같은 일괄 재업로드 흔적은 아니다. 그래도 브랜드가 '출시일'이라고
    말해준 값이 아니라 경로에서 읽은 값이라 released_at 이 아니라 uploaded_at 까지만 쓴다.
    8건 중 4건만 이 형식이고 나머지는 상시 메뉴 이미지 경로라 날짜가 없다.
가격은 페이지에 없다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "굽네치킨"
URL = "https://www.goobne.co.kr/menu/new_p"
LIST_GUBUN = "new_menu_list"
DELAY = 1.0      # robots 에 Crawl-delay 는 없다. 상품 요청이 건당 1회라 1초면 충분하다.
MAX_ITEMS = 40   # 폭주 방지. 현재 8건.


def _text(node, sel) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _uploaded_at(img_url: str) -> str:
    """썸네일 경로의 캠페인 폴더 날짜(.../menu_new/260908_seoul/...)를 YYYY-MM-DD 로."""
    m = re.search(r"/menu_new/(\d{2})(\d{2})(\d{2})_", img_url)
    return f"20{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def _menu_data(html: str) -> tuple:
    """목록 페이지의 tabMenuData 를 (gubun 순서, gubun→분류) 로 푼다.

    탭 0 은 '전체'라 분류로 쓰지 않고, 1번 탭부터가 치킨·피자·사이드다.
    탭 이름은 마크업(.maintab li span)에서 읽어 브랜드가 탭을 늘려도 따라가게 한다.
    """
    tabs = [" ".join(n.text().split())
            for n in HTMLParser(html).css(".maintab li span")]
    m = re.search(r"tabMenuData\s*=\s*\{(.*?)\n\s*\};", html, re.S)
    if not m:
        return [], {}

    order, category = [], {}
    for block in re.finditer(r"(\d+)\s*:\s*\[(.*?)\]", m.group(1), re.S):
        idx = int(block.group(1))
        for gubun in re.findall(r"value\s*:\s*'([^']+)'", block.group(2)):
            if idx == 0:
                order.append(gubun)          # '전체' 탭 순서를 그대로 쓴다
            elif idx < len(tabs):
                category.setdefault(gubun, tabs[idx])
    return order, category


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client(headers={"Referer": f"{URL}?gubun={LIST_GUBUN}"}) as c:
        r = base.retry(lambda: c.get(URL, params={"gubun": LIST_GUBUN}))
        r.raise_for_status()
        order, category = _menu_data(r.text)

        for gubun in order[:MAX_ITEMS]:
            time.sleep(DELAY)
            d = base.retry(lambda g=gubun: c.get(URL, params={"gubun": g}))
            d.raise_for_status()
            card = HTMLParser(d.text)

            name = _text(card, ".left .textbox h4")
            if not name:
                continue
            img = card.css_first(".left .box > img")
            # src 앞에 공백·탭이 붙어 오는 조각이 있다(new_combination).
            image = img.attributes.get("src", "").strip() if img else ""

            it = Item(
                brand=BRAND,
                name=name,
                desc=_text(card, ".left .textbox p"),
                image=image,
                category=category.get(gubun, ""),
                uploaded_at=_uploaded_at(image),
                is_new=True,          # 신제품 전용 페이지에 실린 상품이다
            )
            if it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)
    return items
