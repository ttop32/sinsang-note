"""가마치통닭.

공정위 등록 가맹점 788개로 치킨 업종 8위다.

www.gamachi.co.kr 은 그누보드 게시판을 메뉴판으로 쓴다(`bo_table=1503987965`).
목록이 서버에서 통째로 렌더돼 나오고 쿠키·세션도 브라우저도 필요 없다.

    GET /b/menu           30건
    GET /b/menu?page=2    17건     → 합계 47건(이름 중복 2건 제외 45건)
    GET /b/menu?page=3     0건     → 여기서 멈춘다

⚠️ 사이트 자신은 `/b/menu&sca=…` 처럼 **`?` 가 아니라 `&` 로** 쿼리를 붙인다
   (그누보드 rewrite 가 그렇게 생겼다). 2026-10-02 실측 결과 `?page=2` 와
   `&page=2` 가 **바이트까지 같은 응답**을 준다. 표준 형태인 `?` 를 쓴다.

────────────────────────────────────────────────────────────────────────
🔴 신제품 신호가 이미지 Last-Modified 하나뿐이다
────────────────────────────────────────────────────────────────────────
없는 것부터 적는다. 다음 날을 위해 다시 찾지 말라고 남긴다.

  - **NEW·신메뉴 배지가 없다.** 카드에 배지 자리 자체가 없다.
  - **'신메뉴' 분류가 없다.** 분류는 치킨메뉴 / 사이드메뉴 / 삼계탕 셋뿐이다.
  - **상세 페이지에 등록일이 없다.** `/b/menu/62` 를 받아 보면 날짜 형식
    문자열이 **하나도** 안 나온다(2026-10-02 실측). 혹시 `2026-10-02` 같은 게
    보이면 그건 '오늘' 을 찍은 것이지 글 등록일이 아니다. 속지 마라.
  - **정렬이 시간순이 아니다.** 폼의 `sst=wr_sort2 asc` 다 — 운영자가 손으로
    매긴 진열 순서다. 첫 줄이 최신이라는 보장이 없다.
  - `wr_id`(`/b/menu/<n>`)는 1→77 로 단조증가해서 **순서 힌트**는 되지만
    🔴 번호를 날짜로 환산하지 마라. 그건 날짜가 아니다.

남은 건 썸네일의 Last-Modified 뿐이다. 2026-10-02 전 47장 실측 분포:

    2024-01-31 14 · 2024-02-14 4 · 2024-03-12 6 · 2024-05-16 1
    2025-01-08  3 · 2025-01-09 1 · 2025-01-20 1 · 2025-07-22 1
    2026-01-16  1 · 2026-04-28 3 · 2026-05-09 1 · 2026-06-30 8 · 2026-09-29 3

13개 날짜에 2년 반에 걸쳐 흩어져 있고 제일 큰 덩어리가 14/47(30%)다. 네네치킨
(82%가 한 날)이나 도미노 같은 **일괄 재업로드가 아니다** — 신구 구분에 쓸 만하다.
그래도 어디까지나 파일 업로드 시각이지 브랜드가 말해준 출시일이 아니라서
🔴 `released_at` 이 아니라 `uploaded_at` 에 넣는다. `released_at` 은 끝까지 빈다.

🔴 **`is_new` 는 전건 None 이다.** 브랜드가 '신제품' 이라고 말한 적이 없으니
   True 라고 적을 근거가 없고, 그렇다고 False 도 아니다(배지가 없다는 건 옛
   상품이라는 증거가 못 된다). 이 브랜드는 **collect.py 의 전날 대비 diff 와
   uploaded_at 날짜 창**으로만 신제품이 잡힌다. 합류 첫날에 아무것도 안 나오는
   게 정상이다 — 수집 실패로 읽지 마라.

🔴 날짜가 하나로 뭉치면 터뜨린다. 사이트를 개편하면서 이미지를 한 번에 다시
   올리면 전 메뉴가 그날 신상으로 둔갑한다. 서로 다른 날짜가 1개뿐이면
   이 브랜드의 **유일한 신호가 쓰레기가 된 것**이므로, 조용히 47건에 같은
   날짜를 찍느니 수집을 멈추는 쪽이 낫다.

────────────────────────────────────────────────────────────────────────
⚠️ 이용약관이 복제·유통·상업적 이용을 금지한다 (운영자 판단으로 수집)
────────────────────────────────────────────────────────────────────────
`/site-service` (이용약관) 회원 의무 조항 제10호가 이렇게 적혀 있다 —
"회사의 승인 없이 회사 인터넷 사이트의 서비스 정보 또는 개인정보를 복제 또는
유통시키거나 상업적으로 이용" 하는 행위 금지. 같은 취지의 조항이 이용제한
사유에도 한 번 더 있다.

base.BRANDS 가 이마트24·도미노피자·폴바셋을 적어둔 것과 같은 자리다.
notes/CRAWLING-POLICY.md §6-4 의 'robots 는 허용, 약관이 수집·복제 금지' 칸 —
**수집하되 기록하고, 삭제 요청이 오면 다투지 말고 즉시 내린다.**
(샘표처럼 다툼의 여지는 있다. 그 조항이 '회원의 의무' 절 안에 있고 우리는
회원이 아니다. 그래도 유리하게 읽지 않고 그냥 기록해 둔다.)

⚠️ robots.txt 는 **200 인데 본문이 0바이트**다(2026-10-02 실측). 상태코드만
   보면 규칙이 있는 것처럼 읽히지만 내용이 없으니 규칙도 없다. 404 와 같은
   취급이다. 🔴 403 과 헷갈리지 마라 — 403 은 RFC 9309 §2.3.1.4 상 전면 금지다
   (notes/CRAWLING-POLICY.md §6-2).

────────────────────────────────────────────────────────────────────────
나머지 판단
────────────────────────────────────────────────────────────────────────
분류  목록 전체(47건)와 분류별 목록(치킨메뉴 24 / 사이드메뉴 16 / 삼계탕 1 = 41)이
      **안 맞는다.** 6건은 어느 분류에도 안 들어가 있다. 그래서 분류별 목록으로
      수집하면 6건을 잃는다 — 전체 목록으로 긁고, 분류는 `sca` 3장을 따로 받아
      `wr_id` 로 이어 붙인다. 못 이은 6건은 분류를 비운다.
      분류 이름은 `nav#bo_cate li a` 에서 읽는다(하드코딩하면 늘 때 빈다).
url   카드 href 가 `/b/menu/62&page=1` 이다. 뒤의 `&page=` 는 목록 복귀용이라
      떼고 `/b/menu/62` 로 건다(2026-10-02 실측 200).
이름  '뼈닭강정'·'순살닭강정' 이 각각 두 번 올라와 있다(wr_id 51/57, 52/58).
      같은 Item.key 라 `seen` 이 뒤엣것을 버린다. 47 → 45 가 정상이다.
promo 할인·행사 표시가 사이트에 없다. 전건 False 다. 세트에는 promo 를 찍지
      않는다 — '떡볶이 모둠 튀김 세트' 류는 rules.drop_sets() 가 이름으로 본다.
image `/data/file/1503987965/thumb-…_368x368.{png,jpg}` 에 origin 을 붙인다.
      전부 https 라 base.derive() 의 http 폐기에 안 걸린다.
가격은 마크업에 자리(`p.price`)는 있지만 통째로 주석 처리돼 값이 없다.
"""
import re
import time
from email.utils import parsedate_to_datetime

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "가마치통닭"
SITE = "https://www.gamachi.co.kr"
LIST = SITE + "/b/menu"

DELAY = 0.5       # 목록 요청 간격(초). robots 가 비어 Crawl-delay 가 없으니 보수적으로.
IMG_DELAY = 0.15  # 이미지 HEAD 간격(초)
MAX_PAGES = 10    # 폭주 방지. 현재 2장.
MAX_ITEMS = 200   # 폭주 방지. 현재 47건.

# `/b/menu/62&page=1` → 62. 뒤의 page 는 목록 복귀용이라 url 에서도 뗀다.
_WR_ID = re.compile(r"/b/menu/(\d+)")


def _text(node, sel: str) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _page(client, **params) -> list:
    r = base.retry(lambda: client.get(LIST, params=params or None))
    r.raise_for_status()
    return HTMLParser(r.text)


def _categories(client, tree) -> dict:
    """wr_id → 분류명. 분류별 목록 3장을 따로 받아 전체 목록에 이어 붙인다.

    전체 47건 중 41건만 분류에 들어 있어서(docstring 참고) 분류별로 긁으면
    6건을 잃는다. 분류 이름은 마크업에서 읽어 늘어나도 따라가게 한다.
    """
    names = [" ".join(a.text().split()) for a in tree.css("nav#bo_cate li a")]
    names = [n for n in names if n]
    if not names:
        raise RuntimeError(
            "가마치통닭 분류 내비가 비었다 — 'nav#bo_cate li a' 가 안 걸린다. "
            "셀렉터가 깨졌을 가능성")
    out = {}
    for name in names:
        time.sleep(DELAY)
        t = _page(client, sca=name)
        for a in t.css("a.list_tit"):
            m = _WR_ID.search(a.attributes.get("href", ""))
            if m:
                out.setdefault(m.group(1), name)
    return out


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
        first = _page(c)
        categories = _categories(c, first)

        trees = [first]
        for page in range(2, MAX_PAGES + 1):
            time.sleep(DELAY)
            t = _page(c, page=page)
            if not t.css("div.gall_li"):
                break           # 빈 장이 나오면 끝이다. 3장째가 그렇다.
            trees.append(t)

        for tree in trees:
            for card in tree.css("div.gall_li"):
                a = card.css_first("a.list_tit")
                name = " ".join(a.text().split()) if a else ""
                if not name:
                    continue
                m = _WR_ID.search(a.attributes.get("href", ""))
                img = card.css_first("div.gall_href img")
                src = (img.attributes.get("src", "").strip() if img else "")

                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=_text(card, "div.gall_text_href p"),
                    image=SITE + src if src.startswith("/") else src,
                    category=categories.get(m.group(1), "") if m else "",
                    # 브랜드가 말해준 출시일이 아니다. 아래에서 이미지
                    # Last-Modified 로 uploaded_at 만 채운다.
                    released_at="",
                    # 🔴 전건 None. 이 사이트에는 NEW 배지도 신메뉴 분류도
                    # 등록일도 없다. True 라고 적을 근거가 없고 False 도 아니다.
                    is_new=None,
                    # 할인·행사 표시가 없다. 세트에는 promo 를 찍지 않는다
                    # (rules.drop_sets() 가 이름으로 거른다).
                    promo=False,
                    url=f"{SITE}/b/menu/{m.group(1)}" if m else "",
                )
                if it.key in seen:
                    continue       # '뼈닭강정'·'순살닭강정' 이 두 번씩 올라와 있다
                seen.add(it.key)
                items.append(it)
                if len(items) >= MAX_ITEMS:
                    break

        if not items:
            raise RuntimeError(
                "가마치통닭 메뉴 0건 — 'div.gall_li' / 'a.list_tit' 가 안 걸린다. "
                "셀렉터가 깨졌을 가능성")

        for it in items:
            time.sleep(IMG_DELAY)
            it.uploaded_at = _uploaded_at(c, it.image)

    # 아래 둘은 '건수는 멀쩡한데 신호만 사라진' 상태를 막는 가드다. 이 브랜드는
    # 날짜가 유일한 신호라, 날짜가 비거나 한 날로 뭉치면 collect.py 의 0건 가드도
    # FLOOR 도 통과한 채 신제품 판정이 조용히 죽는다.
    dated = [it.uploaded_at for it in items if it.uploaded_at]
    if len(dated) * 2 < len(items):
        raise RuntimeError(
            f"가마치통닭 업로드일 {len(items)}건 중 {len(dated)}건만 붙었다 — "
            f"이미지 호스트가 Last-Modified 를 끊었거나 경로가 바뀌었을 가능성. "
            f"이 브랜드의 유일한 신제품 신호다")
    if len(set(dated)) == 1:
        raise RuntimeError(
            f"가마치통닭 업로드일이 {dated[0]} 하나로 뭉쳤다 — 이미지 일괄 "
            f"재업로드일 가능성. 그대로 쓰면 전 메뉴가 그날 신상으로 둔갑한다 "
            f"(2026-10-02 실측은 13개 날짜에 흩어져 있었다)")
    return items
