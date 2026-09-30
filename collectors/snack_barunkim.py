"""바르다김선생.

/menu/list.html?bs=<분류> 가 쿠키·세션 없이 카드를 그대로 내려준다. UTF-8, 브라우저 불필요.
한 페이지 6건이고 무한스크롤이라 pg 파라미터로 이어 받는다(pg 범위를 넘기면 빈 목록).
분류는 6개다: 김밥·밥과 면·만두·계절/별미·세트·PB상품.

죠스떡볶이와 같은 회사(나상균)의 같은 CMS(newriver)다. 마크업이 거의 같다.

이용약관(/footer/term.html)에 스크래핑·복제·영리이용 금지 조항이 없다.
이 조사 묶음에서 약관이 깨끗한 게 확인된 유일한 브랜드다.
반면 **robots.txt 는 404(HTML)** 라 허용도 금지도 아니다. 그래서 간격을 길게 잡는다.

신제품 신호 — 2026-09-30 실측. **조사 내용과 두 군데가 다르다.**
  1. 조사는 "홈에 '신메뉴 출시' 라벨이 상품마다 SSR" 이라고 적었는데, 홈의 그
     블록은 지금 **HTML 주석(`<!-- -->`) 안에 들어 있는 죽은 마크업**이다.
     강릉 장칼국수·눈꽃치즈 닭갈비 덮밥·바른 참기름 막국수 셋 다 주석 안이고,
     살아 있는 건 '추천 메뉴 / 김선생이 추천하는 메뉴 네 가지' 배너 한 장뿐이라
     상품 목록이 아니다. 렌더 텍스트만 뜨면 주석이 본문처럼 보이는 함정이다.
     그래서 **홈은 받지 않는다.**
  2. 조사가 못 본 신호가 목록에 있다. 카드에 `<span class="tag new">출시</span>`
     가 붙는다. tag 는 4종이다 — new(출시) · best(인기) · recom(추천) · season(계절).
     상품마다 켜고 끄는 배지라 이게 이 브랜드의 진짜 신제품 신호다.
  3. /menu/new.html 도 SSR 이긴 한데 상품 목록이 아니라 **배너 이미지 슬라이더**다
     (alt 텍스트 말고는 상품 정보가 없고 링크가 비어 있다). 그래서 쓰지 않는다.

is_new 는 tag new 가 붙은 것만 True 로 올리고, 없는 건 False 가 아니라 None 이다
(이삭토스트·피자헛과 같은 선 — 배지 없음은 '아니다'가 아니라 '모른다'다).
released_at 은 어디에도 없다. 대신 썸네일 경로 /uploads/product/YYYYMMDD…… 를
uploaded_at 에 넣는다. 2018~2023 에 고루 흩어져 있어(한 달에 몰린 재업로드 흔적이 없다)
상품별 등록 시점으로는 쓸 만하다. 그래도 브랜드가 말한 출시일은 아니라 released_at 은 비운다.

상세 페이지(/menu/view.html?seq=…)는 해당 분류 전체를 슬라이더로 담고 있어서
한 요청에 설명문까지 다 온다. 그런데 설명문 전문 게재는 CRAWLING-POLICY §3-① 이
제일 큰 리스크로 꼽은 항목이라 이삭토스트와 같이 desc 는 비워 둔다.
url 에는 목록이 주는 상품별 상세 주소를 그대로 담는다. 가격은 사이트에 없다.
"""
import re
import time
from urllib.parse import urljoin

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "바르다김선생"
ROOT = "https://teacherkim.co.kr"
URL = ROOT + "/menu/list.html"
PAGE_SIZE = 6     # 한 페이지 6건. 이보다 적게 오면 다음 장이 없다.
MAX_PAGES = 15    # 폭주 방지. 현재 최대 2페이지.
DELAY = 2.5       # robots.txt 가 없는 브랜드다. 허용도 금지도 아니니 간격을 길게 잡는다.

# (분류명, bs 코드). 004003 은 존재하지 않는다(사이트 nav 에도 없다).
CATEGORIES = (
    ("김밥",      "004001"),
    ("밥과 면",   "004002"),
    ("만두",      "004004"),
    ("계절/별미", "004006"),
    ("세트",      "004007"),
    ("PB상품",    "004005"),
)

# span.tag 의 두 번째 클래스 → 화면 라벨. new 만 신제품 신호다.
TAGS = {"new": "출시", "best": "인기", "recom": "추천", "season": "계절"}


def _text(node, sel) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _uploaded_at(img_url: str) -> str:
    """썸네일 경로의 등록 날짜(/uploads/product/20210524768709.png)를 YYYY-MM-DD 로."""
    m = re.search(r"/uploads/product/(\d{4})(\d{2})(\d{2})", img_url)
    if not m:
        return ""
    y, mo, d = (int(g) for g in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _tags(card) -> list:
    """카드에 붙은 배지 클래스를 라벨로. 없으면 빈 목록."""
    out = []
    for sp in card.css("span.tag"):
        for cls in sp.attributes.get("class", "").split():
            if cls in TAGS:
                out.append(TAGS[cls])
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        for category, bs in CATEGORIES:
            for page in range(1, MAX_PAGES + 1):
                r = base.retry(lambda: c.get(URL, params={"bs": bs, "pg": page}))
                r.raise_for_status()
                time.sleep(DELAY)

                cards = HTMLParser(r.text).css("#menu_list .list_wrap li")
                for card in cards:
                    name = _text(card, ".infobox .tit")
                    link = card.css_first("a")
                    if not name or not link:
                        continue
                    img = card.css_first(".imgs img")
                    src = img.attributes.get("src", "") if img else ""
                    labels = _tags(card)
                    it = Item(
                        brand=BRAND,
                        name=name,
                        name_en=_text(card, ".infobox .en"),
                        image=urljoin(ROOT, src) if src else "",
                        labels=labels,
                        category=category,
                        uploaded_at=_uploaded_at(src),
                        # '출시' 배지만 True. 배지 없음은 모름이지 아님이 아니다.
                        is_new=True if "출시" in labels else None,
                        url=urljoin(URL, link.attributes.get("href", "")),
                    )
                    if it.key in keys:
                        continue
                    keys.add(it.key)
                    items.append(it)

                # 꽉 차지 않은 페이지면 다음 장이 없다. 확인 사살용 요청을 아낀다.
                if len(cards) < PAGE_SIZE:
                    break
    return items
