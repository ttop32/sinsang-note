"""이삭토스트.

menu.php 가 쿠키·세션 없이 HTML 을 그대로 돌려준다. UTF-8. 브라우저 불필요.
페이지당 20건이고, 범위를 넘긴 page 는 서버가 1페이지를 되돌려준다(메가와 같은 패턴).

신제품 신호가 두 개다. 2026-09-30 실측(전 카테고리 60건):
  - prdcode 앞 6자리가 YYMMDD 다. 60건 전부 유효한 과거 날짜로 파싱되고
    미래 날짜가 하나도 없다. 연도 분포는 23년 23건 / 24년 8건 / 25년 11건 / 26년 18건이라
    2023-06 사이트 구축 때 몰아 넣고 이후 조금씩 추가한 모양과 정확히 맞는다.
    다만 브랜드가 "출시일"이라고 써놓은 값은 아니다. 등록일일 가능성이 있다.
    스타벅스 new_SDATE 와 같은 급의 유보를 달아두고 released_at 에 넣는다.
  - NEW 배지(/img/new.svg alt=NEW)가 60건 중 8건에 붙어 있다.
배지는 손으로 관리해서 낡는다. '디카페인 아메리카노'(2025-04-24)는 아직 NEW 인데
'프렌치 브리오슈 베이컨감자'(2026-07-10)에는 NEW 가 없다. 그래서 피자헛과 같은 선을
지킨다 — NEW 는 True 로 올리되 배지 없음을 False 로 뒤집지 않는다(모름이지 아님이 아니다).
낡은 배지는 collect 쪽에서 released_at 과 대조해 걸러진다.

세트메뉴 23건은 토스트 단품의 세트 구성이라 promo 로 찍는다(피자헛 lclass='S' 와 같은 취급).
'리얼 칠리 새우 세트'는 '리얼 칠리 새우'와 별개의 신제품이 아니다.

상품 이미지는 /admin/data/product2/<prdcode>_R.png 인데 robots.txt 가 /admin/ 을 막는다.
그래서 **어댑터는 이 URL 을 절대 요청하지 않는다**(피자헛처럼 HEAD 로 확인하지 않는다).
URL 을 Item.image 에 담기만 한다. 실제 요청은 우리 봇이 아니라 방문자 브라우저가 하고,
robots.txt 는 자동 수집기에 대한 규칙이지 사람이 여는 브라우저에 대한 규칙이 아니다.
**다만 CRAWLING-POLICY §3 의 완화책대로 나중에 썸네일을 우리 스토리지로 옮기게 되면
그때는 우리 서버가 /admin/ 을 직접 받는 것이라 robots 위반이 된다.** 이 브랜드는
그 미러링 대상에서 빼거나 브랜드에 따로 물어야 한다.

상세페이지(ptype=view)에는 한 줄 설명과 원재료가 있지만 받지 않는다. 60건이면 요청이
목록의 10배가 되고, 설명문 전문 게재는 CRAWLING-POLICY §3-① 에서 제일 큰 리스크로 꼽은 항목이다.
그래서 desc 는 비워둔다. 가격 정보는 사이트 어디에도 없다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "이삭토스트"
URL = "https://www.isaac-toast.co.kr/menu/menu.php"
IMG_ROOT = "https://www.isaac-toast.co.kr"
PAGE_SIZE = 20          # 한 페이지 20건. 이보다 적게 오면 다음 페이지가 없다.
MAX_PAGES = 10          # 폭주 방지. 현재 최대 2페이지.
DELAY = 1.0             # 요청 간격(초)

# (카테고리명, catcode). 소스&과일잼은 하위코드 10111000 이 0건이라 상위 10110000 을 쓴다.
CATEGORIES = (
    ("토스트",        "10101000"),
    ("세트메뉴",      "10101100"),
    ("사이드",        "10101200"),
    ("음료",          "10101300"),
    ("소스 & 과일잼", "10110000"),
)


def _text(node, sel) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _released_at(prdcode: str) -> str:
    """prdcode 앞 6자리 YYMMDD 를 날짜로. 날짜로 안 읽히면 조용히 버린다."""
    m = re.match(r"(\d{2})(\d{2})(\d{2})", prdcode)
    if not m:
        return ""
    y, mo, d = (int(g) for g in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"20{y:02d}-{mo:02d}-{d:02d}"


def _image(card) -> str:
    """썸네일은 img[src] 가 아니라 style 의 background-image 에 들어있다.

    dt 의 직계 img 만 본다. NEW 배지(div.icon > img)도 dt 안에 있어서
    'dt img' 로 잡으면 배지가 먼저 걸리고 썸네일을 통째로 놓친다(8건 실측).
    """
    node = card.css_first("dt > img")
    if not node:
        return ""
    m = re.search(r"url\(['\"]?(.*?)['\"]?\)", node.attributes.get("style", ""))
    return IMG_ROOT + m.group(1) if m and m.group(1).startswith("/") else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen, keys = set(), set()
    with base.client() as c:
        for category, catcode in CATEGORIES:
            for page in range(1, MAX_PAGES + 1):
                r = base.retry(lambda: c.get(URL, params={
                    "ptype": "list", "catcode": catcode, "page": page}))
                r.raise_for_status()
                time.sleep(DELAY)

                cards = HTMLParser(r.text).css("div.pro_list dl")
                parsed = []
                for card in cards:
                    link = card.css_first("a")
                    name = _text(card, "h4")
                    if not link or not name:
                        continue
                    m = re.search(r"prdcode=(\d+)", link.attributes.get("href", ""))
                    if not m:
                        continue
                    badges = [i.attributes.get("alt", "").strip()
                              for i in card.css(".icon img")]
                    parsed.append((m.group(1), Item(
                        brand=BRAND,
                        name=name,
                        name_en=_text(card, "small"),
                        image=_image(card),
                        labels=[b for b in badges if b],
                        category=category,
                        released_at=_released_at(m.group(1)),
                        # NEW 만 True 로 올린다. 배지 없음은 '아니다'가 아니라 '모른다'다.
                        is_new=True if "NEW" in badges else None,
                        # 세트는 collect.drop_sets() 담당. promo 는 할인·행사 전용.
                        promo=False,
                    )))

                # 범위를 넘긴 page 는 서버가 1페이지를 되돌려주므로, 전부 기존 코드면 종료
                if not parsed or all(code in seen for code, _ in parsed):
                    break
                for code, it in parsed:
                    if code in seen:
                        continue
                    seen.add(code)
                    # prdcode 는 다른데 Item.key 가 같은 쌍이 하나 있다
                    # ('포테이토 팝(시즈닝)' vs '포테이토 팝' — key 가 괄호를 턴다).
                    # 계약대로 key 기준으로 지우고, 목록이 최신순이라 새 쪽이 남는다.
                    if it.key in keys:
                        continue
                    keys.add(it.key)
                    items.append(it)
                # 꽉 차지 않은 페이지면 다음 장이 없다. 확인 사살용 요청을 아낀다.
                if len(parsed) < PAGE_SIZE:
                    break
    return items
