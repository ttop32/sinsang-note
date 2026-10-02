"""던킨.

Inertia.js 사이트라 HTML 최상단 엘리먼트의 data-page 속성에 페이지 props 가 JSON 으로
통째로 들어있다. 클래스 이름을 훑는 것보다 이쪽이 훨씬 덜 깨져서 JSON 만 읽는다.
쿠키·토큰 없이 열리고 브라우저 불필요. 2026-09-30 실측.

신제품 신호는 카테고리 하나다. **DONUT(cat=1) 밑에만 '신제품'(sub=1) 서브카테고리가 있다.**
나머지 대분류 넷(FOOD·COFFEE·BEVERAGE·SNACK & MORE)에는 신제품 칸이 아예 없어서,
도넛이 아닌 신제품은 브랜드가 알려주지 않는다. 그래서 전체 메뉴판을 받아서
'신제품' 칸에 든 것만 is_new=True 로 올리고, 나머지는 None 으로 둔 채
collect 의 어제 대비 diff 에 맡긴다. 신제품 탭만 받으면 커피·음료 신제품은 영영 못 잡는다.

**그 결과 같은 출시가 반으로 갈린다.** 도넛 쪽만 보이고 같은 날 같은 콜라보로 나온
비도넛 쪽이 통째로 안 보인다. 2026-10-02 실측:
  · `들기름 메밀 츄이스티 by 오스틴 강`(DONUT, 보임) ↔ `콘치즈 크로크무슈 by 오스틴 강`(FOOD, 안 보임)
  · `학화 호도 먼치킨 세트(5개입)`(보임) ↔ 학화 라인 5종(안 보임). **세트는 보이는데 구성품이 안 보인다.**

그래서 이미지 Last-Modified 로 같은 출시를 되붙인다(_regroup). ⚠️ **날짜만으로
묶으면 안 된다.** 2026-09-15 묶음 8건은 신제품 1건(정통 보름달 도넛)에 블루베리
머핀·퀸아망·올리브 치아바타 같은 **상시 베이커리 7건**이 같이 들어 있다. 그래서
날짜가 같고 **이름까지 겹칠 때만** 묶는다 — 첫 낱말이 같거나(학화) 꼬리가
통째로 같거나(by 오스틴 강). 첫 낱말은 맛·형태를 가리키는 흔한 말이면 안 쓴다
(_GENERIC) — '초코'·'딸기'로 묶으면 메뉴판 절반이 한 묶음이 된다.
215건 전수로 돌려 6건이 붙었고 상시 메뉴는 0건이었다.

LM 은 묶는 데만 쓰는 게 아니라 **떨구는 데도 쓴다.** 날짜가 없으니 브랜드가
'신제품' 칸에 넣어둔 채 안 내리면 영영 신상으로 남는다. 실제로 허니 바이츠
(LM 2026-03-31)·말돈 소금우유 도넛(2026-04-21)이 반년째 떠 있었다. 신상으로
표시한 것에만 LM 을 uploaded_at 에 넣어 STALE 가드에 걸리게 한다.
⚠️ **전건에 넣으면 안 된다** — 그러면 상시 메뉴가 날짜만으로 창 안에 들어온다.

**출시일이 없다.** 상품 레코드에 날짜 필드가 하나도 없고(id/TITLE/E_TITLE/카테고리/
이미지/색상/TOP_YN/SEASON_MENU_DIV/SORTNUM 이 전부다).
그래서 released_at 은 전부 빈 값이고 desc 도 받을 데가 없다. 가격 정보도 없다.

**상세 페이지는 있다.** 앞서 '/menu/<id> 는 404' 라고 적어둔 건 맞지만(2026-09-30 재확인)
경로를 잘못 짚은 것이었다. 목록 HTML 의 카드 링크가 /menu/view?cat=&sub=&id= 이고
그 페이지의 props.product 에 해당 상품이 들어온다. 요청은 안 늘린다 — cat·sub·id 가
이미 JSON 레코드(dd_product_cat1_id / dd_product_cat2_id / id)에 있어 조립만 하면 된다.
검증(2026-09-30): id=6021 은 200 이고 props.product.TITLE 이 '학화 호도 먼치킨 세트(5개입)'.
없는 id 도 200 이고 product 만 null 이라 상태코드로는 못 가린다.

받는 구조에서 조심할 것 세 가지:
  - 한 페이지 12건이고 page 파라미터로 넘긴다. 다만 **다음 페이지가 없으면 서버가
    1페이지를 그대로 되돌려준다**(cat=1&sub=1&page=2 가 같은 5건). 0건 종료만 믿으면
    같은 걸 무한히 다시 받는다. 메가처럼 '전부 기존 id' 조건도 같이 둔다.
  - COFFEE(cat=6)는 SUBCATEGORY_DIV_YN=1 이라 products 대신 productCats 키로 오고,
    sub 을 줘도 그 대분류 전체를 돌려준다. 그래서 dd_product_cat2_id 로 한 번 더 거른다.
  - 카테고리 트리는 props.categories[0]["data"] 에 있다. 리스트 한 겹이 더 있다.

행사 표시는 메뉴에 없다. 프로모션은 별도 /event 영역이라 받지 않는다. promo 는 전부 False 다.
"""
import email.utils as eu
import json
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "던킨"
URL = "https://www.dunkindonuts.co.kr/menu"
VIEW_URL = URL + "/view?cat={}&sub={}&id={}"   # 목록 카드가 거는 상세 링크와 같은 꼴
IMG_ROOT = "https://www.dunkindonuts.co.kr"
NEW_CAT = "신제품"      # DONUT 밑의 신제품 서브카테고리 이름
PAGE_SIZE = 12          # 한 페이지 12건. 이보다 적게 오면 다음 페이지가 없다.
MAX_PAGES = 12          # 폭주 방지. 현재 최대 2페이지.
DELAY = 1.0             # 요청 간격(초)


def _props(c, **params) -> dict:
    r = base.retry(lambda: c.get(URL, params=params))
    r.raise_for_status()
    time.sleep(DELAY)
    node = HTMLParser(r.text).css_first("[data-page]")
    if not node:
        raise RuntimeError(f"data-page 가 없다: {params}")
    return json.loads(node.attributes["data-page"])["props"]


def _rows(props: dict) -> list:
    """대분류에 따라 products 로 오기도 하고 productCats 로 오기도 한다."""
    box = props.get("products") or props.get("productCats") or {}
    return box.get("data") or []


# 첫 낱말로 묶으면 안 되는 흔한 말. 맛·형태·온도를 가리키는 것들이다.
_GENERIC = {"초코", "딸기", "커피", "우유", "치즈", "바나나", "생", "허니", "더블",
            "아이스", "밀크", "바닐라", "카라멜", "녹차", "말차", "흑임자", "앙버터",
            "오리지널", "클래식", "시즌", "신상", "쿠키", "도넛", "라떼", "크림",
            "민트", "레몬", "사과", "포도", "(앳홈)"}
_TAIL_MIN = 4     # 꼬리가 이보다 짧으면 우연이다


def _lastmod(c, url: str) -> str:
    """이미지가 서버에 올라간 날. 없으면 빈 문자열."""
    if not url:
        return ""
    try:
        s = base.retry(lambda: c.head(url)).headers.get("Last-Modified")
        return eu.parsedate_to_datetime(s).date().isoformat() if s else ""
    except Exception:
        return ""


def _tail(a: str, b: str) -> str:
    """두 이름이 공유하는 꼬리. 낱말 하나짜리는 안 친다('by 오스틴 강'은 친다)."""
    n = 0
    while n < min(len(a), len(b)) and a[-1 - n] == b[-1 - n]:
        n += 1
    t = a[len(a) - n:].strip() if n else ""
    return t if len(t) >= _TAIL_MIN and " " in t else ""


def _regroup(items: list) -> None:
    """같은 출시인데 도넛이 아니라서 빠진 것을 되붙인다. 제자리에서 고친다.

    묶는 조건은 **날짜와 이름이 둘 다** 겹치는 것이다. 날짜만 보면 같은 날
    올라온 상시 베이커리가 통째로 딸려 온다(위 docstring 의 2026-09-15 묶음).
    """
    with base.client() as c:
        lm = {it.name: _lastmod(c, it.image) for it in items}
    seeds = {}
    for it in items:
        if it.is_new and lm.get(it.name):
            seeds.setdefault(lm[it.name], []).append(it.name)

    for it in items:
        day = lm.get(it.name, "")
        if it.is_new:
            # 브랜드가 '신제품' 칸에서 안 내린 묵은 것을 STALE 가드에 넘긴다.
            if day:
                it.uploaded_at = day
            continue
        if not day:
            continue
        head = it.name.split(" ")[0]
        for sn in seeds.get(day, []):
            same_head = (head == sn.split(" ")[0] and len(head) >= 2
                         and head not in _GENERIC)
            if same_head or _tail(it.name, sn):
                it.is_new = True
                it.uploaded_at = day
                break


def fetch() -> list[Item]:
    items: list[Item] = []
    seen, keys = set(), set()
    with base.client() as c:
        tree = _props(c)["categories"][0]["data"]
        pairs = [(c1["id"], c2["id"], c2["PRODUCT_CAT2_NM"])
                 for c1 in tree for c2 in c1.get("PRODUCT_CAT2") or []]

        for cat, sub, sub_name in pairs:
            for page in range(1, MAX_PAGES + 1):
                raw = _rows(_props(c, cat=cat, sub=sub, page=page))
                rows = [r for r in raw if r.get("dd_product_cat2_id") == sub]
                # 다음 페이지가 없으면 서버가 1페이지를 되돌려준다. 전부 기존이면 종료.
                if not rows or all(r["id"] in seen for r in rows):
                    break
                for r in rows:
                    if r["id"] in seen:
                        continue
                    seen.add(r["id"])
                    name = " ".join((r.get("TITLE") or "").split())
                    if not name:
                        continue
                    img = r.get("MAIN_IMG_FILE") or ""
                    it = Item(
                        brand=BRAND,
                        name=name,
                        name_en=" ".join((r.get("E_TITLE") or "").split()),
                        image=IMG_ROOT + img if img.startswith("/") else img,
                        category=r.get("PRODUCT_CAT1_NM") or "",
                        # 브랜드가 '신제품' 칸에 넣은 것만 True. 나머지는 모름(None).
                        is_new=True if sub_name == NEW_CAT else None,
                        # 순회 중인 칸이 아니라 레코드가 말하는 제 카테고리를 쓴다.
                        url=VIEW_URL.format(r.get("dd_product_cat1_id") or cat,
                                            r.get("dd_product_cat2_id") or sub, r["id"]),
                    )
                    # 같은 상품이 여러 칸에 걸쳐 있을 수 있다. 계약대로 key 로 지운다.
                    if it.key in keys:
                        continue
                    keys.add(it.key)
                    items.append(it)
                # 꽉 차지 않은 페이지면 다음 장이 없다. 확인 사살용 요청을 아낀다.
                # 거른 뒤가 아니라 거르기 전 개수로 본다(COFFEE 는 남의 것도 섞여 온다).
                if len(raw) < PAGE_SIZE:
                    break
    _regroup(items)
    return items
