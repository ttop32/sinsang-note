"""교촌치킨.

kyochon.com 은 예전 방식의 ASP 사이트라 목록이 서버에서 그대로 렌더돼 나온다.
쿠키·세션 없이 열리고 브라우저도 불필요하다. 응답은 UTF-8(EUC-KR 아님).

신메뉴 소스가 두 군데인데 서로 내용이 다르다.
  - /menu/newmenu.asp        상단 '신메뉴' 메뉴. 지금은 블랙시크릿 3종.
  - /menu/chicken.asp?code=21 치킨 탭 안의 '신메뉴'. 지금은 윙콤비·한마리 12종.
둘 다 브랜드가 직접 '신메뉴'라고 붙여놓은 목록이라 합집합을 is_new=True 로 본다.
다만 newmenu.asp 쪽 이미지는 2025-10 에 올라간 것들이라 갱신이 멈춘 듯하고,
code=21 쪽이 2026-08 로 최신이다. 어느 쪽이 진짜 최신인지는 사이트만 봐서는 못 가린다.

출시일·등록일을 알려주는 곳은 목록·상세·공지 어디에도 없다. released_at 은 비운다.
이미지 파일명에도 타임스탬프가 없어서, uploaded_at 은 이미지의 Last-Modified 로 채운다.
2025-10-30 에 몰린 덩어리(사이트 이관분)가 있긴 하지만 나머지는 제품별로 흩어져 있어
신구 구분에는 쓸 만하다. 어디까지나 파일 업로드 시각이지 출시일은 아니다.

상품 페이지는 목록 카드가 이미 달고 있는 상대경로 view.asp?id=...&cg=... 다.
추가 요청 없이 /menu/ 를 앞에 붙이기만 한다.

burger.asp 와 dream.asp 는 목록이 비어 있어(각각 빈 <ul>, 빈 문서) 대상에서 뺐다.
가격(권장소비자가격)이 목록에 있지만 Item 에 자리가 없어 버린다.
행사/세트 상품을 구분할 표시는 없다. '반반…[간장+레드]' 같은 건 세트가 아니라 맛 조합이라
promo 는 전부 False 로 둔다.
"""
import time
from email.utils import parsedate_to_datetime

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "교촌치킨"
SITE = "https://www.kyochon.com"
MENU = SITE + "/menu/"

# 전체 목록 (경로, 화면상 분류)
LISTS = [
    ("chicken.asp", "치킨"),
    ("side.asp", "사이드"),
    ("drink.asp", "음료"),
    ("liquor.asp", "주류"),
]
# 브랜드가 '신메뉴'라고 내건 목록. 여기 이름이 나오면 is_new=True.
NEW_LISTS = ["newmenu.asp", "chicken.asp?code=21"]

DELAY = 0.4  # 목록 요청 간격(초)
IMG_DELAY = 0.15  # 이미지 HEAD 간격(초)


def _names(node) -> str:
    dt = node.css_first("dt")
    return " ".join(dt.text().split()) if dt else ""


def _url(node) -> str:
    """카드 안의 상세 링크(view.asp?id=...&cg=...). 상대경로라 /menu/ 를 붙인다."""
    a = node.css_first("a[href*='view.asp']")
    href = a.attributes.get("href", "") if a else ""
    return MENU + href if href else ""


def _desc(node) -> str:
    dd = node.css_first("dd")
    return " ".join(dd.text().split()) if dd else ""


def _page(client, path: str) -> list:
    r = base.retry(lambda: client.get(MENU + path))
    r.raise_for_status()
    return HTMLParser(r.text).css("ul.menuProduct > li")


def _page_delayed(client, path: str) -> list:
    time.sleep(DELAY)
    return _page(client, path)


# 헤더가 없는 것과 우리 쪽이 죽은 것은 다르다. 앞은 정상이고(상시 메뉴는
# Last-Modified 를 안 주는 경우가 많다 — 실측 59%) 뒤는 그날 수집이 통째로
# 날짜를 잃는 사고다. 그런데 둘 다 빈 문자열로 끝나서 구분이 안 됐다.
# 던진 횟수를 세어 두고 fetch 끝에서 본다.
_HEAD_FAIL = 0
_HEAD_FAIL_MAX = 0.3   # 이 비율을 넘게 던지면 우리 쪽 문제로 본다


def _head_guard(tried: int) -> None:
    """HEAD 가 너무 많이 터졌으면 조용히 넘어가지 않는다."""
    if tried and _HEAD_FAIL / tried > _HEAD_FAIL_MAX:
        raise RuntimeError(
            f"이미지 HEAD {tried}건 중 {_HEAD_FAIL}건이 예외로 끝났다 "
            "— 날짜를 통째로 잃는 상태라 수집을 실패로 본다")


def _uploaded_at(client, img_url: str) -> str:
    """이미지의 Last-Modified 를 날짜로. 헤더가 없으면 빈 문자열."""
    global _HEAD_FAIL
    if not img_url:
        return ""
    try:
        lm = client.head(img_url).headers.get("last-modified", "")
    except Exception:
        _HEAD_FAIL += 1
        return ""
    try:
        return parsedate_to_datetime(lm).date().isoformat() if lm else ""
    except (TypeError, ValueError):
        return ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        # 먼저 '신메뉴' 목록을 받아 이름을 걷어둔다. 같은 페이지를 두 번 때리지 않게
        # 노드도 같이 들고 있다가, 전체 목록에 없는 건(블랙시크릿 등)은 뒤에서 거둔다.
        new_pages = []
        new_names = set()
        for path in NEW_LISTS:
            time.sleep(DELAY)
            lis = _page(c, path)
            new_pages.append(lis)
            new_names |= {n for li in lis if (n := _names(li))}

        # 비어 있으면 셀렉터가 깨진 것이다. 건수는 112 그대로라 collect.py 의
        # 0건 가드도 FLOOR 도 발동하지 않아 "교촌은 신제품이 없다"가 조용히 굳는다.
        if not new_names:
            raise RuntimeError("신메뉴 목록이 비었다 — 셀렉터가 깨졌을 가능성")

        sources = [(_page_delayed(c, p), cat) for p, cat in LISTS]
        sources += [(lis, "치킨") for lis in new_pages]

        for lis, category in sources:
            for li in lis:
                name = _names(li)
                if not name:
                    continue
                img = li.css_first("p.img img")
                src = img.attributes.get("src", "") if img else ""
                is_new = name in new_names
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=_desc(li),
                    image=SITE + src if src.startswith("/") else src,
                    labels=["신메뉴"] if is_new else [],
                    category=category,
                    is_new=is_new,
                    url=_url(li),
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)

        for it in items:
            time.sleep(IMG_DELAY)
            it.uploaded_at = _uploaded_at(c, it.image)
    _head_guard(sum(1 for it in items if it.image))
    return items
