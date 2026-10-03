"""누구나홀딱반한닭.

공정위 등록 가맹점 260개로 치킨 업종 21위. superboard 계열 CMS 고 목록이 서버에서
그대로 렌더돼 나온다. 쿠키·세션 없이 열리고 브라우저도 불필요하다.

2026-09-30 조사(`notes/CANDIDATES-CHICKEN.md`)는 "내비에 신메뉴 카테고리가 분명히
있는데 URL 을 못 찾았다" 로 남겨뒀다. 찾았다 — **`?ca_id=01` 이 신메뉴다.**

목록은 `/product/list?ca_id=NN` 한 장씩이고 분류는 여덟이다. 분류 이름은 내비
(`a[href*="ca_id="]`)에서 읽는다. 하드코딩하면 브랜드가 분류를 바꿀 때 엉뚱한
이름이 붙는다 — chicken_goobne.py 가 탭 이름을 마크업에서 읽는 것과 같은 이유다.
2026-10-03 기준 01 신메뉴 6 / 02 세트메뉴 8 / 03 베이크치킨 6 / 04 로스트치킨 7 /
05 쌈닭메뉴 4 / 06 피자메뉴 5 / 07 풍미메뉴 9 / 08 미니메뉴 12 = 57건.
분류끼리 겹쳐서 고유 `wm_id` 는 53개이고, **최종 수집은 51건**이다 — 서로 다른
`wm_id` 두 쌍(`쌈닭파이팅` 17·30, `쏘핫레드홀릭` 33·72)이 같은 상품명을 달고 있어
`base.make_key()` 가 각각 하나로 접는다.
57 → 53 → 51 이 정상이다. 51 이 나온다고 파서를 의심하지 마라.
⚠️ 2026-10-02 판에는 50 → 46 → 45 라고 적혀 있었다. 그건 파서가 **맵기 아이콘이
   이름 안에 든 카드 7장을 조용히 흘린** 수치다(아래 `_cards` 주석). 옛 숫자를
   기준선으로 되살리지 마라.

신제품 신호:
  is_new  **`ca_id=01` 이 진짜 서버측 필터다.** 2026-10-03 실측으로 신메뉴 6건이
          전체 53건의 **진부분집합**이고(wm_id 집합으로 확인), 다른 분류는 각각
          다른 집합을 돌려준다. '전부 보여주는 페이지' 가 아니라 브랜드가 골라
          담는 칸이다. 거기 실린 것만 True 로 보고 나머지는 **None** 으로 둔다 —
          신메뉴 칸에 없다는 게 "오래됐다"의 증거는 못 된다.
          🔴 신메뉴 칸이 0건이면 RuntimeError 로 터뜨린다. 건수는 51 그대로라
          collect.py 의 0건 가드도 급감 가드도 안 걸리고 "이 브랜드는 신제품이
          없다"가 조용히 굳는다(교촌 선례).
  released_at / uploaded_at  **둘 다 비운다.** 날짜처럼 보이는 게 하나 있는데
          쓰면 안 된다 — 이미지 파일명이 `20260204144534_…`, `20260212161605_…`
          꼴이라 업로드 시각으로 읽고 싶어진다. 그런데 **53건이 2026-02-04 과
          2026-02-12 딱 두 날에 몰려 있다.** HEAD 로 Last-Modified 를 받아봐도
          같은 두 날이다(2026-10-02 실측). 사이트 리뉴얼 때 통째로 다시 올린
          흔적이지 상품별 출시일이 아니다. 전건에 2026-02 를 찍으면 51건이
          한꺼번에 '신상' 으로 올라온다. **가짜 날짜보다 빈 날짜가 낫다.**
          그래서 이 브랜드의 신호는 신메뉴 카테고리 하나뿐이고, 나머지는
          collect.py 의 '어제 없던 키가 오늘 있다' diff 가 판정한다.

⚠️ 이미지가 `<img src>` 가 아니라 `div.tmb` 의 인라인 `background-image:url('…')` 이다.
   주소에 `:443` 이 박혀 오는데(superboard 공통) 떼어도 열린다.

상품 상세는 팝업 `/popup/product_view?wm_id=N` 이다. 조각이 아니라 이름·설명이 든
독립 문서라 사람이 열어도 읽힌다(427바이트, 2026-10-02 확인). 그래서 그대로 url 로 쓴다.

세트메뉴(ca_id=02) 8건은 그대로 싣되 **is_new 를 주지 않는다** — 신메뉴 칸에 없다.
promo 는 전건 False 다. 할인·행사 표시가 없고, 세트 변형을 접는 건 rules.drop_sets() 담당이다.
가격은 목록에 없다.

robots.txt 에 `User-agent: *` 그룹이 **아예 없다.** 상용 봇 몇 개만 개별 지정돼 있어
우리 UA 는 어느 그룹에도 안 걸린다. 후라이드참잘하는집과 같은 CMS·같은 형태다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "누구나홀딱반한닭"
SITE = "https://www.nuguna-banhandak.co.kr"
LIST = SITE + "/product/list"
NEW_CATE = "01"        # 신메뉴. 내비 이름으로도 한 번 더 확인한다
NEW_LABEL = "신메뉴"

MAX_CATEGORIES = 20   # 폭주 방지. 현재 8개.
MAX_ITEMS = 200       # 폭주 방지. 현재 51건(카드 57, 고유 wm_id 53).
DELAY = 0.4           # 목록 요청 간격(초)

# 카드 한 장을 여는 링크. 이게 몇 개인지가 그 분류의 정답 건수다.
_POP = re.compile(r"/popup/product_view\?wm_id=(\d+)")
# 이미지가 <img src> 가 아니라 div.tmb 의 인라인 style 이라 속성에서 긁어낸다.
_BG = re.compile(r"background-image:\s*url\(['\"]?([^'\")]+)")


def _cards(html: str) -> list:
    """(wm_id, 이미지, 상품명) 목록. 카드 하나는 `<li>` 한 장이다.

    🔴 전에는 정규식 하나로 세 조각을 한꺼번에 떴는데, 상품명을
    `<span class="tit">([^<]*?)</span>` 로 받는 바람에 **이름 안에 태그가 든 카드가
    통째로 사라졌다.** 매운 메뉴는 `<span class="tit">쏘핫레드홀릭 <i class="ico_spicy">
    </i></span>` 처럼 맵기 아이콘이 이름 안에 들어 있어서 `[^<]` 에서 끊긴다.
    2026-10-03 실측 57장 중 7장이 그렇게 빠졌고, 그중 하나가 **신메뉴 칸의
    쏘핫레드홀릭(wm_id=72)** 이다 — 이 브랜드의 유일한 신제품 신호가 5/6 만 남은
    채로 조용히 수집됐다. 건수는 45 로 그럴듯해서 아무 가드에도 안 걸렸다.
    그래서 정규식 조립을 버리고 DOM 으로 읽는다. 이름은 `.text()` 라 안쪽 태그를 탄다.
    """
    out = []
    for a in HTMLParser(html).css("a[data-pop-href]"):
        m = _POP.search(a.attributes.get("data-pop-href") or "")
        li = a.parent
        if not m or li is None:
            continue
        tit = li.css_first("span.tit")
        name = " ".join(tit.text().split()) if tit else ""
        tmb = li.css_first("div.tmb")
        bg = _BG.search(tmb.attributes.get("style") or "") if tmb else None
        out.append((m.group(1), bg.group(1) if bg else "", name))
    return out


def _categories(html: str) -> list:
    """내비에서 (ca_id, 분류명). 순서는 유지하고 중복은 턴다."""
    out, seen = [], set()
    for a in HTMLParser(html).css('a[href*="ca_id="]'):
        m = re.search(r"ca_id=(\w+)", a.attributes.get("href") or "")
        name = " ".join(a.text().split())
        if m and name and m.group(1) not in seen:
            seen.add(m.group(1))
            out.append((m.group(1), name))
    return out


def _page(client, ca_id: str) -> str:
    r = base.retry(lambda: client.get(LIST, params={"ca_id": ca_id}))
    r.raise_for_status()
    return r.text


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        # 신메뉴 칸을 먼저 받는다. 분류 목록도 이 응답에서 읽어 요청을 아낀다.
        first = _page(c, NEW_CATE)
        cats = _categories(first)
        if not cats:
            raise RuntimeError("분류 내비를 못 읽었다 — 셀렉터가 깨졌을 가능성")

        new_ids = {wm for wm, _, _ in _cards(first)}
        # 신메뉴 칸이 비면 이 브랜드의 유일한 신호가 사라진 것이다.
        # 조용히 넘어가면 "신제품 없음" 이 영구히 굳는다.
        if not new_ids:
            raise RuntimeError("신메뉴 칸이 비었다 — 셀렉터가 깨졌을 가능성")

        pages = {NEW_CATE: first}
        for ca_id, _ in cats[:MAX_CATEGORIES]:
            if ca_id in pages:
                continue
            time.sleep(DELAY)
            pages[ca_id] = _page(c, ca_id)

        for ca_id, cate in cats[:MAX_CATEGORIES]:
            html = pages.get(ca_id, "")
            cards = _cards(html)
            # 🔴 카드 수와 파싱 수가 어긋나면 조용한 부분수집이다. 건수가 그럴듯하게
            # 남아서 collect.py 의 0건 가드도 FLOOR 도 통과한다(위 _cards 주석의 사고).
            on_page = set(_POP.findall(html))
            if {wm for wm, _, _ in cards} != on_page:
                raise RuntimeError(
                    f"누구나홀딱반한닭 ca_id={ca_id} 카드 {len(on_page)}장 중 "
                    f"{len({wm for wm, _, _ in cards})}장만 읽혔다 "
                    "— 마크업이 바뀌었을 가능성")
            for wm_id, img, name in cards:
                if not name:
                    continue
                image = img if img.startswith("http") else SITE + img
                it = Item(
                    brand=BRAND,
                    name=name,
                    image=image.replace(":443", ""),
                    labels=[NEW_LABEL] if wm_id in new_ids else [],
                    category=cate,
                    # 신메뉴 칸에 실렸는가 하나로 판정한다. 아닌 건 False 가 아니라 None.
                    is_new=True if wm_id in new_ids else None,
                    # 날짜는 전건 비운다. 파일명·Last-Modified 가 전부
                    # 2026-02-04/02-12 리뉴얼 일괄이라 출시일이 아니다(위 docstring).
                    released_at="",
                    uploaded_at="",
                    promo=False,
                    url=f"{SITE}/popup/product_view?wm_id={wm_id}",
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
                if len(items) >= MAX_ITEMS:
                    break

        if not items:
            raise RuntimeError("상품 목록이 비었다 — 셀렉터가 깨졌을 가능성")
    return items
