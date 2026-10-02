"""브라운돈까스((주)브라운F&C).

돈까스 중위권 14곳 중 **상품 단위 신상 신호가 있는 유일한 브랜드**다. 나머지는
창업모집 랜딩이거나 메뉴가 통째로 이미지라 상품을 글자로 꺼낼 수가 없다.

메뉴는 `/sub/menu{1,2,3,4,5,6}.php` 6장이 전부다. 평범한 SSR HTML 이고 쿠키·세션·
브라우저가 필요 없다. 카테고리당 1요청, 총 6요청에 40건이다(2026-10-02 실측).
robots.txt 는 `User-agent: * / Allow:/` 로 전면 허용이다.

페이지 번호와 카테고리가 어긋나 있다 — 시그니처가 menu6, 사이드가 menu3 이고
오믈렛(menu4)·카레(menu5)가 돈까스(menu1)·스테이크(menu2) 사이를 건너뛴다.
화면 탭 순서대로 CATEGORIES 에 적어뒀으니 번호로 유추하지 마라.

신제품 신호가 둘이고, **둘 다 혼자서는 못 믿는다.** 2026-10-02 에 40건 전부 실측한
결과를 아래에 적어둔다.

  is_new  카드마다 `.img .tag span` 에 NEW / BEST 배지가 붙는다. 40건 중 NEW 20건,
          BEST 14건이고 둘 다 붙은 게 3건이다(소세지 오믈렛·마늘폭탄 카레·
          눈꽃 치즈 떡볶이). 브랜드가 손으로 관리하는 값이라 **낡는다.**
          실제로 '카레 돈까스'·'카레 함박스테이크'·'카레라이스'·'어린이돈까스'·
          '눈꽃 치즈 떡볶이' 5건은 아직 NEW 인데 이미지가 2021-06-25 자다. 4년이
          넘었으니 신상일 리 없다.
          그래서 이삭토스트·피자헛과 같은 선을 지킨다 — **NEW 는 True 로 올리되
          배지가 없다고 False 로 뒤집지 않는다**(모름이지 아님이 아니다).
          낡은 배지는 collect 쪽에서 날짜와 대조해 걸러진다.

  uploaded_at  상품 이미지의 HTTP `Last-Modified` 헤더. 이게 이 사이트에서 유일하게
          **상품별로 갈리는** 시간 값이다. 40건이 다섯 무더기로 또렷하게 나뉜다 —
            2020-08-05  3건 (스테이크 전부)
            2021-06-25 21건 (사이트 구축 당시 원본. 07:27:23 13건 + 08:46:47 8건)
            2024-04-12  1건 (쫄면)
            2024-10-07 10건 (오믈렛 5 + 카레 2 + 토마호크 3)
            2025-11-26  5건 (시그니처 2 + 더블돈까스 2 + 고소들기름모밀 1)
          전부 같은 날짜로 뭉치면 사이트 일괄 재업로드라 버려야 하는데(돈까스클럽이
          정확히 그 경우다 — 메뉴 이미지 18장이 전부 2026-09-29 하루 안에 다시
          올라가 있어 날짜가 통째로 죽었다) 여기는 그렇지 않다.

          **교차검증에 쓸 물증이 하나 더 있다.** 사이드의 '고소들기름모밀' 이미지는
          파일명이 `side_img251126.jpg` 인데, 이 파일의 Last-Modified 가
          2025-11-26 이다. 브랜드가 파일명에 박아둔 날짜와 서버 헤더가 **정확히
          일치한다.** 헤더가 실제 올린 시점이라는 걸 사이트 스스로 말해주는 셈이다.
          (세븐일레븐 '신상품' 탭처럼 신호가 가짜인 사례가 있어 이걸 먼저 확인했다.)

**그래도 released_at 에는 넣지 않는다.** 이건 브랜드가 "출시일"이라고 적어둔 값이
아니라 이미지 파일을 쓴 시각이다. 둘이 어긋나는 걸 눈으로 봤다 — '어린이돈까스'는
NEW 배지가 붙어 있는데 2021년 이미지(`tonkatsu_img15.jpg`)를 그대로 재사용한다.
사진을 안 바꾸고 상품만 올린 경우라 업로드 시각이 출시일보다 오래됐다. 반대로
2021-06-25 07:27:23 로 **초 단위까지 똑같은** 파일이 13개 있는데(돈까스·시그니처
계열) 그건 그날 한꺼번에 옮긴 흔적이지 그 13종이 같은 날 나왔다는 뜻이 아니다.
본아이에프 cmdtListImg 와 같은 처분 — uploaded_at 까지만이다.

released_at 을 채울 길은 이 브랜드에 없다. 공지사항은 글이 **딱 한 건**이고
('홈페이지 리뉴얼 오픈', 2020-08-13), 언론보도는 11건인데 마지막이 2021-12-07 이고
전부 수상·기부·코로나 지원이라 메뉴 얘기가 하나도 없다. 상세는 별도 페이지가 아니라
같은 HTML 안의 CSS 라이트박스(`.lb-overlay`)라 더 받을 것도 없다.

이미지 HEAD 는 상품 수만큼 늘어나므로 URL 단위로 캐시해서 중복 요청을 없앤다.
같은 사진을 두 카드가 쓰는 경우가 있다(40건 중 고유 이미지 40장이라 지금은 절감이
0이지만, 재사용이 늘어도 요청이 안 늘게 둔다). 지금 총 요청은 6 + 40 = 46 회다.

Item.url 은 카테고리 페이지 주소에 카드가 거는 `#image-N` 앵커를 붙인 것이다.
라이트박스가 `:target` 으로 열리는 구조라 이 주소로 들어가면 그 상품 설명이 바로
펼쳐진다. 앵커 번호는 **페이지마다 1부터 다시 시작하니** 페이지 주소와 반드시
짝지어 써야 한다.

가격은 사이트 어디에도 없다. 이용약관은 찾지 못했다 — 푸터에 개인정보처리방침과
이메일무단수집거부만 있다. 금지 조항을 확인하지 못했다는 뜻이지 없다는 뜻은 아니다.
"""
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "브라운돈까스"
HOST = "https://browntonkatsu.com"
PAGE_URL = HOST + "/sub/{}.php"
DELAY = 1.3          # 요청 간격(초)
MAX_HEADS = 80       # 폭주 방지. 현재 고유 이미지 40장.

# (카테고리명, 페이지 슬러그). 화면 탭 순서다. 번호와 순서가 어긋나 있으니
# docstring 의 경고를 읽고 나서 손대라.
CATEGORIES = (
    ("시그니처",  "menu6"),
    ("돈까스",    "menu1"),
    ("스테이크",  "menu2"),
    ("오믈렛",    "menu4"),
    ("카레",      "menu5"),
    ("사이드",    "menu3"),
)

NEW_BADGE = "NEW"


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _name(card) -> tuple:
    """카드 제목에서 (한글명, 영문명).

    `<span class="title">양념치킨까스<small>Sweet & Spicy Chicken Cutlet</small></span>`
    처럼 영문이 자식 <small> 로 들어있다. 통째로 text() 하면 둘이 붙어버리므로
    직계 텍스트만 떼어 한글명으로 쓴다.
    """
    t = card.css_first("span.title")
    if not t:
        return "", ""
    small = t.css_first("small")
    return _clean(t.text(deep=False)), _clean(small.text()) if small else ""


def _uploaded_at(c, src: str, cache: dict) -> str:
    """이미지의 Last-Modified 를 YYYY-MM-DD 로. 받아올 수 없으면 비운다.

    출시일이 아니라 파일을 쓴 시각이다 — docstring 의 유보 사항을 읽어라.
    실패해도 예외로 올리지 않는다. 날짜가 비는 건 상품을 통째로 잃는 것보다 가볍고,
    셀렉터가 깨진 것과 달리 '드러나야 할 고장'이 아니다.
    """
    if src in cache:
        return cache[src]
    if len(cache) >= MAX_HEADS:
        return ""
    out = ""
    try:
        r = base.retry(lambda: c.head(HOST + src))
        lm = r.headers.get("last-modified", "")
        if lm:
            # 'Wed, 26 Nov 2025 01:06:00 GMT'
            from email.utils import parsedate_to_datetime
            out = parsedate_to_datetime(lm).date().isoformat()
    except Exception:
        out = ""
    cache[src] = out
    time.sleep(DELAY)
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    keys: set = set()
    stamps: dict = {}
    with base.client() as c:
        for category, slug in CATEGORIES:
            page = PAGE_URL.format(slug)
            r = base.retry(lambda: c.get(page))
            r.raise_for_status()
            time.sleep(DELAY)

            cards = HTMLParser(r.text).css("#menu .tabcontent > ul > li")
            if not cards:
                raise RuntimeError(
                    f"브라운돈까스 {category}({slug}): 상품 0건 — 셀렉터가 깨졌을 수 있다")

            for card in cards:
                name, name_en = _name(card)
                if not name:
                    continue
                key = base.make_key(BRAND, name)
                if key in keys:
                    continue
                keys.add(key)

                badges = [_clean(b.text()) for b in card.css(".img .tag span")]
                img = card.css_first(".img img")
                src = img.attributes.get("src", "") if img else ""
                anchor = card.css_first(".img a")
                href = anchor.attributes.get("href", "") if anchor else ""
                desc = card.css_first(".lb-overlay .desc p.txt")

                items.append(Item(
                    brand=BRAND,
                    name=name,
                    name_en=name_en,
                    desc=_clean(desc.text()) if desc else "",
                    image=HOST + src if src.startswith("/") else src,
                    labels=[b for b in badges if b],
                    category=category,
                    # 이미지 업로드 시각. 출시일이 아니다(docstring 참고).
                    uploaded_at=_uploaded_at(c, src, stamps) if src else "",
                    # NEW 만 True 로 올린다. 배지 없음은 '아니다'가 아니라 '모른다'다.
                    is_new=True if NEW_BADGE in badges else None,
                    # 1+1·할인 행사가 이 사이트에 없다. 세트도 메뉴에 없다.
                    promo=False,
                    # 라이트박스가 :target 으로 열려서 앵커까지 붙이면 설명이 펼쳐진다.
                    url=page + href if href.startswith("#") else page,
                ))
    return items
