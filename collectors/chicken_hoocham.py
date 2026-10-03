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
   2026-10-02 전수 대조 결과(공지 16건 × 상품 33건) 붙은 건 청양먹태치킨 하나뿐이고
   오매칭은 0건이었다. 전용앱 글에도 아무 상품이 안 붙는다 — 확인했다.
   ⚠️ 남아 있는 구멍 하나: 2019년 글 `신메뉴 심쿵! 핫도그 출시~!` 는 상품명이
      정확히 `핫도그` 인 상품이 생기면 걸린다(3글자라 MIN_MATCH 를 통과한다).
      지금은 그런 상품이 없다. 생기면 2019년 날짜가 붙으므로, 메뉴에 `핫도그` 가
      등장하면 이 줄을 다시 보라.

② ~~`uploaded_at` — 이미지 Last-Modified~~ **쓰지 않는다. 비운다.**
   🔴 처음엔 '약한 신호' 로 넣었다가 뺐다. **이 신호는 약한 게 아니라 틀렸다.**
   2026-10-02 실측 33건 분포 —
       2024-01-16 ×15(45%) · 2021-05-25 ×4 · 2026-05-21 ×3 · 2021-09-10 ×2 ·
       2026-08-13 · 2026-08-10 · 2025-10-14 · 2023-12-01 … (12개 날짜)
   덩어리 하나가 45% 인 것도 문제지만 진짜 문제는 **덩어리 밖**이다. 전체에서
   가장 최신 축인 **2026-08-10 이 `후라이드치킨`** — 이 브랜드에서 가장 오래된
   간판 메뉴 — 에 붙어 있고, **2026-08-13 은 `떡꼬치`** 다. 둘 다 사진을 새로
   찍어 갈아끼운 것이지 새로 나온 게 아니다.
   그대로 두면 `rules.is_fresh()` 의 날짜 창(60일)에 걸려 **후라이드치킨이
   신상 목록에 올라간다.** 실제로 그 상태로 수집·배포됐다(2026-10-02 리뷰에서
   재현). 이 서비스에서 제일 큰 거짓말이 메뉴판을 신상으로 내보내는 것이고,
   그게 바로 이 두 줄이다.
   `rules.untrust_bulk_dates()` 도 못 막는다 — 1건짜리 날짜라 묶음이 아니다.
   그래서 **가짜 날짜보다 빈 날짜가 낫다**(네네치킨·누구나홀딱반한닭과 같은
   처분). 이미지 HEAD 도 아예 보내지 않는다 — 쓰지 않을 값에 32요청을 쓸 이유가
   없다.
   🔴 "흩어지니까 쓸 만하다" 며 되살리지 마라. 흩어져 있는 게 문제가 아니라
      **가장 최신 두 건이 가장 오래된 메뉴**라는 게 문제다. 반례가 신호 자체를
      무효로 만든다.

`is_new` 는 **전건 None** 이다. 마크업에는 NEW 배지도 신메뉴 탭도 없다.
🔴 ⚠️ **다만 "이 브랜드엔 신제품 표시가 없다" 는 틀렸다 — 배지가 그림 안에 있다.**
   2026-10-02 전수 확인: 썸네일 33장 중 `청양먹태치킨`(580×470, 좌상단 x≈150-280,
   y≈95-205)에 **빨간 원형 `NEW` 스티커가 픽셀로 그려져** 있다. 마크업에는
   흔적이 없다. 컴포즈커피가 똑같이 당한 경우다(배지가 썸네일에 구워져 있어
   마크업만 믿은 어댑터가 0건을 냈다).
   지금은 그 한 건을 ①(공지 2026-05-21)이 이미 잡고 있어서 실질 손해가 없지만,
   **공지 없이 배지만 붙는 상품이 나오면 통째로 놓친다.** 이미지 배지 판독은
   이 어댑터 범위 밖이라 여기서는 기록만 남긴다(notes/IMAGE-BADGES.md 후속).
   거꾸로, 배지가 `후라이드치킨` 에는 **없다**는 사실이 위 ②의 판단을 뒷받침한다.

메뉴판 전체를 신상으로 찍지 않는다. 날짜가 ① 한 건뿐이라 이 브랜드는 대체로
collect.py 의 '어제 없던 키가 오늘 있다' diff 로 잡히게 된다. 그게 정직한 상태다.

⚠️ 이미지 주소에 `:443` 이 박혀 온다(superboard 공통). 떼어도 열린다.
세트메뉴(ca_id=02) 7건은 그대로 싣고 분류에 '세트메뉴' 라고 적어 사람이 알아보게 둔다.
promo 는 전건 False — 할인·행사 표시가 상품에는 없다. 세트 변형은 rules.drop_sets() 담당.

robots.txt 에 `User-agent: *` 그룹이 **없다.** Googlebot-Image·bingbot·SemrushBot·
AhrefsBot·DotBot·ZoominfoBot 만 개별 차단하고 Yeti·NaverBot 은 허용한다. 우리 UA 는
어느 그룹에도 안 걸리므로 금지 대상이 아니다('robots 가 허용한다' 와는 다른 말이다).
"""
import re
import time

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

# 상품 한 건. 이미지와 이름이 형제가 아니라 거리를 둔 채로 붙어 있다.
_ITEM = re.compile(
    r'<img src="(https?://www\.hoocham\.com(?::443)?'
    r'/superboard/data/product/thumb/[^"]+)"'
    r'[\s\S]{0,300}?<span class="tit">([^<]*)</span>')

# 카드 한 장당 정확히 하나. 위 `_ITEM` 이 몇 장을 흘렸는지 세는 데만 쓴다.
#
# 🔴 같은 superboard CMS 를 쓰는 누구나홀딱반한닭에서 이 모양의 정규식이 사고를
# 냈다. 상품명을 `<span class="tit">([^<]*)</span>` 로 받는데, 맵기 아이콘이
# 이름 안에 들어간 카드(`<span class="tit">쏘핫레드홀릭 <i class="ico_spicy"></i>
# </span>`)가 `[^<]` 에서 끊겨 **카드 7장이 통째로 사라졌다**(그중 하나가 신메뉴).
# 건수가 그럴듯하게 남아서 collect.py 의 0건 가드도 FLOOR 도 통과했다.
# 후참잘은 2026-10-03 실측으로 33/33 이 멀쩡하지만, 브랜드가 같은 아이콘을 쓰기
# 시작하면 똑같이 당한다. 세어서 어긋나면 터뜨린다.
_TIT = re.compile(r'<span class="tit">')

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
    """소식 게시판에서 (제목, YYYY-MM-DD).

    🔴 조용히 빈 목록을 돌려주지 않는다. 게시판이 죽거나 마크업이 바뀌면
    released_at 이 전건 사라지는데, 상품 건수는 33 그대로라 collect.py 의
    0건 가드도 FLOOR 도 안 걸린다. 이 브랜드가 가진 **유일한 출시일 신호**라
    그 상태가 조용히 굳으면 아무도 못 알아챈다. 그래서 '글이 한 건도 안 읽히면'
    터뜨린다 — '출시 공지가 없다'(정상일 수 있다)와 '게시판을 못 읽었다'(사고)를
    가르는 선이 거기다.
    """
    rows = []
    posts = 0
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
        posts += found
        if not found:
            break
    if not posts:
        raise RuntimeError(
            "후참잘 소식 게시판에서 글을 한 건도 못 읽었다 — 'span.sbj' / "
            "'ul.info li' 가 안 걸린다. 이 브랜드의 유일한 출시일 신호라, "
            "날아가도 상품 건수는 그대로여서 아무도 못 알아챈다")
    return rows


def _released(name: str, news: list) -> str:
    """공지 제목에 이 상품 이름이 통째로 들어 있으면 그 등록일. 여럿이면 가장 이른 날."""
    flat = _flat(name)
    if len(flat) < MIN_MATCH:
        return ""
    hits = [d for title, d in news
            if any(k in title for k in _LAUNCH) and flat in _flat(title)]
    return min(hits) if hits else ""


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
            html = pages.get(cid, "")
            found = _ITEM.findall(html)
            cards = len(_TIT.findall(html))
            # 조용한 부분수집을 막는다. 카드 수와 파싱 수가 어긋나면 터뜨린다(_TIT 주석).
            if len(found) != cards:
                raise RuntimeError(
                    f"후참잘 ca_id={cid} 카드 {cards}장 중 {len(found)}장만 읽혔다 "
                    "— 상품명 안에 태그가 생겼거나 마크업이 바뀌었을 가능성")
            for img, name in found:
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
                    # 🔴 이미지 Last-Modified 는 쓰지 않는다. 가장 최신 두 건이
                    # 후라이드치킨·떡꼬치(둘 다 사진만 갈아끼운 간판 메뉴)라
                    # 그대로 쓰면 메뉴판이 신상으로 올라간다(docstring ②).
                    uploaded_at="",
                    # 마크업에는 NEW 배지도 신메뉴 탭도 없다. 모르는 건 모른다고
                    # 둔다. (썸네일 그림 안에는 배지가 있다 — docstring 참고)
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
    # 이미지 HEAD 는 보내지 않는다. 받아봐야 쓰지 않을 값이다(docstring ②).
    return items
