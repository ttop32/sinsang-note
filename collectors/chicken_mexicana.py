"""멕시카나.

공정위 등록 가맹점 738개로 치킨 업종 11위다.

⚠️ **대문이 메뉴로 가는 길을 알려주지 않는다.** `mexicana.co.kr` 로 들어가면
`/intro.asp` 로 리다이렉트되는데 그 페이지는 렌더 텍스트가 101자뿐인 인트로 화면이다.
진짜 홈은 `/main/index.asp` 고, 메뉴는 `/menu/product.asp` 다. 대문만 보고
'수집할 게 없다'고 판정하기 딱 좋은 구조라 적어둔다.

목록은 옛 ASP 라 서버에서 그대로 렌더돼 나온다. 쿠키·세션 없이 열리고 브라우저도
불필요하다. 상품 카드는 `div.pList > ul > li` 안에
`dl.tit > dt`(이름) · `dd`(설명) · `p.money strong`(권장소비자가격) ·
`p.thumbFull > img`(이미지) 로 들어 있다.

🔴 **신제품 신호는 이미지 Last-Modified 하나뿐이다.**
NEW 배지도, '신메뉴' 탭도, 출시일·등록일 표기도 **없다**. 분류 탭 5개는 전부
맛·부위 축이지 신구 축이 아니다. 그래서 **is_new 는 전건 None 이다** —
'신제품이 아니다(False)'가 아니라 '브랜드가 말해주지 않았다'는 뜻이다.
배지가 없는 걸 없다고 적는 게 정직한 결과다. 없는 배지를 지어내지 마라.

2026-10-02 실측 33건의 Last-Modified 분포다.
    2022-07-26 ×15   2022-11-16 ×1   2023-02-17 ×2   2023-06-20 ×2
    2024-09-02 ×1    2024-12-02 ×1   2024-12-31 ×2   2025-03-20 ×2
    2025-07-31 ×3    2025-09-10 ×2   2026-05-19 ×1   2026-05-20 ×1
12개 날짜로 흩어진다. 2022-07-26 덩어리 15건은 사이트 이관·일괄 재업로드 흔적이라
그 안에서는 신구를 못 가리지만, 나머지 18건은 제품별로 흩어져 있어 기준선으로 쓸 만하다.
어디까지나 파일이 서버에 올라간 시각이지 브랜드가 말해준 출시일이 아니다. 그래서
**released_at 은 전건 비운다** — 출시일 칸에 업로드일을 넣으면 그 뒤로는 구분이 안 된다.

목록은 최신순으로 보이지만(1페이지 머리가 2026-05 업로드분이다) **순서는 날짜가 아니다.**
순서를 날짜로 환산하지 마라.

분류(Item.category)는 `?catecode=` 탭 5개에서 받는다. 2026-10-02 실측으로 다섯 탭이
33건을 **겹침 없이 정확히 분할**한다(3+9+2+16+3=33). 요청 6번이 더 들지만 그만한 값은
한다 — 화면 2단 칩이 분류로 갈린다. 다만 상품의 **정본 목록은 전체 탭**이고, 분류 탭은
이름→분류 지도를 만드는 데만 쓴다. 분류 탭 하나가 깨져도 상품을 잃지 않게 하려는 것이다.

⚠️ **페이지 번호를 짐작하지 마라.** 푸라닭은 마지막 페이지를 넘겨도 같은 페이지를 다시
돌려줘서 무한히 같은 상품을 긁게 된다. 멕시카나는 2026-10-02 실측상 page=4·5 가
빈 목록을 주지만(재서빙 아님) 그 동작에 기대지 않는다. 페이저(`div.paging span.num`)가
마지막 페이지 번호를 알려주므로 **그 숫자만큼만** 돈다. 그 범위 안의 페이지가 비면
부분 수집이므로 조용히 넘어가지 않고 터뜨린다.

이미지 주소는 `/USERFILES/product/<한글 파일명>` 이다. https 로 열리고, 한글이라
요청 전에 퍼센트 인코딩해야 한다. 저장도 인코딩한 쪽으로 한다(브라우저가 알아서 해주지만
우리가 HEAD 로 때리는 주소와 같아야 추적이 쉽다).

상품별 페이지가 없다. 카드에 `<a>` 자체가 없어서 url 은 비우고 base.SITES 폴백으로
브랜드 메뉴 페이지로 보낸다(처갓집·김가네와 같은 처분).

가격(권장소비자가격)은 목록에 있지만 Item 에 자리가 없어 버린다.
할인·행사 표시가 없는 카탈로그라 promo 는 전건 False 다. '멕시콤보'·'치필링 반반' 은
행사가 아니라 구성·맛 조합이고, 세트 판정은 rules.drop_sets() 가 이름으로 한다.

robots.txt 는 두 줄이 전부다 — `User-agent: Yeti` / `Allow:/`.
🔴 **`*` 그룹이 아예 없다.** 그러니 "robots 가 우리를 허용한다"가 아니라
"우리 UA(base.UA)에 **매칭되는 규칙이 하나도 없다**"가 정확한 표현이다. 네이버 봇에게만
말을 걸어둔 파일이고, 그 밖의 봇에 대한 의사 표시는 없다. 수집은 운영자 판단이다.
"""
import re
import time
from email.utils import parsedate_to_datetime
from urllib.parse import quote

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "멕시카나"
SITE = "https://www.mexicana.co.kr"
LIST = SITE + "/menu/product.asp"

# 분류 탭. 1000001('전체')은 뺐다 — 아래 전체 목록과 같은 내용이다.
CATEGORIES = [
    ("1100001", "후라이드"),
    ("1100004", "양념"),
    ("1100005", "시즈닝"),
    ("1100002", "순살"),
    ("1100003", "부위별"),
]

MAX_PAGES = 10    # 폭주 방지. 현재 전체 3페이지, 분류별 1~2페이지.
MAX_ITEMS = 200   # 폭주 방지. 현재 33건.
DELAY = 0.4       # 목록 요청 간격(초)
IMG_DELAY = 0.15  # 이미지 HEAD 간격(초)


def _text(node, sel: str) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _image(li) -> str:
    """카드 썸네일. 파일명이 한글이라 퍼센트 인코딩해서 돌려준다."""
    img = li.css_first("p.thumbFull > img")
    src = (img.attributes.get("src", "") if img else "").strip()
    return SITE + quote(src) if src.startswith("/") else ""


def _last_page(doc) -> int:
    """페이저가 알려주는 마지막 페이지 번호. 못 읽으면 1페이지로 본다."""
    n = doc.css_first("div.paging span.num")
    nums = [int(x) for x in re.findall(r"\d+", n.text())] if n else []
    return min(max(nums), MAX_PAGES) if nums else 1


def _cards(doc) -> list:
    """상품 카드. 상단 내비에도 <li> 가 많아서 목록 컨테이너로 좁힌다."""
    return doc.css("div.pList > ul > li")


def _list(client, code: str) -> list:
    """한 탭(전체 또는 분류)의 전 페이지 카드. 페이저가 센 만큼만 돈다."""
    r = base.retry(lambda: client.get(
        LIST, params={"page": 1, "CateCode": code, "searchstr": ""}))
    r.raise_for_status()
    doc = HTMLParser(r.text)
    cards = _cards(doc)
    last = _last_page(doc)

    for page in range(2, last + 1):
        time.sleep(DELAY)
        p = base.retry(lambda n=page: client.get(
            LIST, params={"page": n, "CateCode": code, "searchstr": ""}))
        p.raise_for_status()
        more = _cards(HTMLParser(p.text))
        # 페이저가 있다고 한 페이지가 비었다. 조용히 넘기면 그 페이지 상품이
        # 통째로 사라진 채 건수만 줄어든다 — 부분 수집이라 터뜨린다.
        if not more:
            raise RuntimeError(
                f"CateCode={code!r} {page}/{last} 페이지가 비었다 — "
                "셀렉터가 깨졌을 가능성")
        cards += more
    return cards


def _uploaded_at(client, img_url: str) -> str:
    """이미지의 Last-Modified 를 날짜로. 실패하면 조용히 비운다."""
    if not img_url:
        return ""
    try:
        lm = client.head(img_url).headers.get("last-modified", "")
        return parsedate_to_datetime(lm).date().isoformat() if lm else ""
    except Exception:
        return ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        # 분류 지도부터. 상품의 정본은 아래 전체 탭이고 여기서는 분류만 가져온다.
        category = {}
        for code, name in CATEGORIES:
            time.sleep(DELAY)
            for li in _list(c, code):
                n = _text(li, "dl.tit > dt")
                if n:
                    category.setdefault(n, name)
        # 다섯 탭이 전부 비면 탭 구조가 바뀐 것이다. 상품은 전체 탭에서 따로
        # 받으므로 건수는 33 그대로고, 분류만 조용히 전건 공백이 된다.
        if not category:
            raise RuntimeError("분류 탭이 전부 비었다 — 셀렉터가 깨졌을 가능성")

        time.sleep(DELAY)
        for li in _list(c, "")[:MAX_ITEMS]:
            name = _text(li, "dl.tit > dt")
            if not name:
                continue
            it = Item(
                brand=BRAND,
                name=name,
                desc=_text(li, "dl.tit > dd"),
                image=_image(li),
                category=category.get(name, ""),
                # NEW 배지도 신메뉴 탭도 없다. '아니다(False)'가 아니라
                # '브랜드가 말해주지 않았다'라서 None 이다. 위 docstring 참고.
                is_new=None,
                # 할인·행사 표시가 없는 카탈로그다. 세트는 promo 가 아니다
                # (rules.drop_sets() 가 이름으로 거른다).
                promo=False,
                # 상품별 페이지가 없다. base.SITES 폴백으로 떨어진다.
                url="",
            )
            if it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)

        # 전체 탭이 비면 건수 가드가 걸리기 전에 여기서 드러낸다.
        if not items:
            raise RuntimeError("전체 목록이 비었다 — 셀렉터가 깨졌을 가능성")

        for it in items:
            time.sleep(IMG_DELAY)
            it.uploaded_at = _uploaded_at(c, it.image)
    return items
