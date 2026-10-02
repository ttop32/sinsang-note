"""후라이드 참 잘하는집(후참잘).

공정위 등록 가맹점 280개로 치킨 업종 19위. superboard 계열 CMS 라 목록이 서버에서
그대로 렌더돼 나온다. 누구나홀딱반한닭과 같은 CMS 다. 브라우저 불필요.

목록은 `/menu/menuN?ca_id=NN` 세 장이다(치킨 11 / 세트 7 / 사이드 15 = 33건).
분류 이름은 내비(`a[href*="ca_id="]`)에서 읽는다 — 하드코딩하면 분류가 바뀔 때
엉뚱한 이름이 붙는다. ⚠️ 내비에 `ca_id=01` 이 '후참잘메뉴'(대분류)와 '치킨메뉴'
(소분류) 두 이름으로 중복 등장한다. 뒤에 오는 소분류 쪽이 상품 분류로 맞다.

신제품 신호가 둘인데 **세기가 많이 다르다.**

① `released_at` — 소식 게시판 `/story/news` 의 출시 공지. (강함, 단 희소함)
   `신메뉴 청양먹태치킨 출시!` / `26.05.21` 처럼 제목과 등록일이 같이 있다.
   제목에 '신메뉴' 나 '출시' 가 들어가고 **그 안에 우리가 가진 상품 이름이 통째로
   들어 있을 때만** 그 날짜를 쓴다(부어치킨 `chicken_boor.py` 와 같은 수법).
   2026-10-02 실측으로 게시판 전체가 16건뿐이고 쓸 수 있는 건 청양먹태치킨 하나다.
   ⚠️ 같은 게시판에 `후참잘 전용앱 출시, 참 잘했다!` 가 있다 — '출시' 가 들어가지만
   상품이 아니다. 이름 대조를 안 하면 엉뚱한 상품에 날짜가 붙는다. 그래서
   **공지에서 상품을 만들지 않는다.** 공지는 이미 가진 상품의 날짜를 채울 때만 쓴다.
   `10월 후참잘 할인소식!` 같은 행사 공지도 같은 이유로 상품이 되지 않는다.

② `uploaded_at` — 이미지 Last-Modified. (약함)
   2026-10-02 실측으로 흩어지긴 한다 — 2026-05-21 ×2, 2025-10-14, 2023-12-01,
   2024-01-16 묶음, 그리고 **2026-08-10**.
   🔴 그 2026-08-10 이 함정이다. **`후라이드치킨`** — 이 브랜드에서 가장 오래된
   기본 메뉴 — 이 전체에서 가장 최신 날짜를 달고 있다. 사진을 새로 찍어 갈아끼운
   것이지 새로 나온 게 아니다. 이미지 mtime 은 업로드 시각이지 출시일이 아니라는
   걸 이 브랜드가 교과서처럼 보여준다. 그래서 released_at 에는 절대 안 넣는다.
   ①이 청양먹태치킨에 준 2026-05-21 과 그 상품의 이미지 mtime 이 정확히 같다는 게
   그나마 이 신호를 믿을 근거인데, 반례(후라이드치킨)가 같이 있으니 거기까지다.

`is_new` 는 **전건 None** 이다. NEW 배지도 신메뉴 탭도 없다. 메뉴판 전체를 신상으로
찍지 않는다. 날짜가 약하니 이 브랜드는 대체로 collect.py 의 '어제 없던 키가 오늘
있다' diff 로 잡히게 된다. 그게 정직한 상태다.

⚠️ 이미지 주소에 `:443` 이 박혀 온다(superboard 공통). 떼어도 열린다.
세트메뉴(ca_id=02) 7건은 그대로 싣고 분류에 '세트메뉴' 라고 적어 사람이 알아보게 둔다.
promo 는 전건 False — 할인·행사 표시가 상품에는 없다. 세트 변형은 rules.drop_sets() 담당.

robots.txt 에 `User-agent: *` 그룹이 **없다.** Googlebot-Image·bingbot·SemrushBot·
AhrefsBot·DotBot·ZoominfoBot 만 개별 차단하고 Yeti·NaverBot 은 허용한다. 우리 UA 는
어느 그룹에도 안 걸리므로 금지 대상이 아니다('robots 가 허용한다' 와는 다른 말이다).
"""
import re
import time

from email.utils import parsedate_to_datetime
from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "후라이드 참 잘하는집"
SITE = "https://www.hoocham.com"
NEWS = SITE + "/story/news"

MAX_CATEGORIES = 12   # 폭주 방지. 현재 3개.
MAX_ITEMS = 200       # 폭주 방지. 현재 33건.
MAX_NEWS_PAGES = 5    # 폭주 방지. 현재 2페이지(16건).
DELAY = 0.5           # 목록 요청 간격(초)
IMG_DELAY = 0.15      # 이미지 HEAD 간격(초)

# 상품 한 건. 이미지와 이름이 형제가 아니라 거리를 둔 채로 붙어 있다.
_ITEM = re.compile(
    r'<img src="(https?://www\.hoocham\.com(?::443)?'
    r'/superboard/data/product/thumb/[^"]+)"'
    r'[\s\S]{0,300}?<span class="tit">([^<]*)</span>')

# 출시 공지만 본다. 둘 다 없으면 상품 소식이 아니다.
_LAUNCH = ("신메뉴", "출시")
# 상품 이름이 이보다 짧으면 제목 안에서 우연히 걸린다. 대조에서 뺀다.
MIN_MATCH = 3


def _flat(s: str) -> str:
    return re.sub(r"\s+", "", s or "")


def _categories(html: str) -> list:
    """내비에서 (경로, ca_id, 분류명).

    ⚠️ 대분류와 소분류가 **같은 주소**를 가리킨다. `/menu/menu1?ca_id=01` 이
    '후참잘메뉴'(대분류)이기도 하고 '치킨메뉴'(소분류)이기도 하다. 상품 분류로
    맞는 건 소분류라서 **중첩된 `ul` 안쪽만** 본다. 푸터(`#fnb`)에도 같은 주소가
    '후참잘메뉴' 로 한 번 더 나오는데 그것도 이 셀렉터에 안 걸린다.
    """
    out = {}
    for a in HTMLParser(html).css('li ul li a[href*="ca_id="]'):
        href = a.attributes.get("href") or ""
        m = re.search(r"(/menu/menu\d+)\?ca_id=(\w+)", href)
        name = " ".join(a.text().split())
        if m and name:
            out[m.group(2)] = (m.group(1), name)
    return [(p, cid, n) for cid, (p, n) in out.items()]


def _news(client) -> list:
    """소식 게시판에서 (제목, YYYY-MM-DD). 실패하면 빈 목록 — 보조 신호다."""
    rows = []
    for pg in range(1, MAX_NEWS_PAGES + 1):
        try:
            time.sleep(DELAY)
            r = base.retry(lambda p=pg: client.get(NEWS, params={"page": p}))
            r.raise_for_status()
        except Exception:
            break
        found = 0
        for li in HTMLParser(r.text).css("li"):
            sbj, info = li.css_first("span.sbj"), li.css("ul.info li")
            if not (sbj and info):
                continue
            found += 1
            title = " ".join(sbj.text().split())
            # `26.05.21` → `2026-05-21`. 두 자리 연도라 20xx 로 편다.
            m = re.match(r"(\d{2})\.(\d{2})\.(\d{2})$", info[0].text().strip())
            if m:
                rows.append((title, f"20{m.group(1)}-{m.group(2)}-{m.group(3)}"))
        if not found:
            break
    return rows


def _released(name: str, news: list) -> str:
    """공지 제목에 이 상품 이름이 통째로 들어 있으면 그 등록일. 여럿이면 가장 이른 날."""
    flat = _flat(name)
    if len(flat) < MIN_MATCH:
        return ""
    hits = [d for title, d in news
            if any(k in title for k in _LAUNCH) and flat in _flat(title)]
    return min(hits) if hits else ""


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
        r = base.retry(lambda: c.get(f"{SITE}/menu/menu1", params={"ca_id": "01"}))
        r.raise_for_status()
        cats = _categories(r.text)
        if not cats:
            raise RuntimeError("분류 내비를 못 읽었다 — 셀렉터가 깨졌을 가능성")

        pages = {"01": r.text}
        for path, cid, _ in cats[:MAX_CATEGORIES]:
            if cid in pages:
                continue
            time.sleep(DELAY)
            p = base.retry(lambda q=path, i=cid: c.get(SITE + q, params={"ca_id": i}))
            p.raise_for_status()
            pages[cid] = p.text

        news = _news(c)

        for path, cid, cate in cats[:MAX_CATEGORIES]:
            for img, name in _ITEM.findall(pages.get(cid, "")):
                name = " ".join(name.split())
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    image=img.replace(":443", ""),
                    category=cate,
                    # 브랜드가 공지에 적어준 등록일. 없으면 비운다.
                    released_at=_released(name, news),
                    # NEW 배지도 신메뉴 탭도 없다. 모르는 건 모른다고 둔다.
                    is_new=None,
                    promo=False,
                    url=f"{SITE}{path}?ca_id={cid}",
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
                if len(items) >= MAX_ITEMS:
                    break

        if not items:
            raise RuntimeError("상품 목록이 비었다 — 셀렉터가 깨졌을 가능성")

        # released_at 이 찬 건은 더 강한 신호를 이미 들고 있다. HEAD 를 아낀다.
        for it in items:
            if it.released_at:
                continue
            time.sleep(IMG_DELAY)
            it.uploaded_at = _uploaded_at(c, it.image)
    return items
