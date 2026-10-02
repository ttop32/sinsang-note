"""동경에서먹었던규동(동경규동) — 공지 게시판의 '신메뉴 출시' 글.

tokyo-gyudong.com 은 아임웹이다. SSR 이라 브라우저는 필요 없지만 페이지 한 장이
30만 자가 넘는다(위젯별 인라인 CSS). 2026-10-02 실측으로 상품 쪽 구조는 이렇다.

  /menu
      상품 **이름은 있는데 그게 전부다.** 갤러리 위젯에 34종이 이름+사진으로
      깔려 있고 NEW 배지도, 날짜도, '신메뉴' 분류도 없다(`신메뉴` 문자열이 페이지
      전체에 0회). 이걸 통째로 넣으면 상설 메뉴 34건이 전부 신상이 된다.
  /notice  ← 'NEWS'
      여기가 신호다. 글 15건(2페이지)이고 제목·날짜·본문이 다 있다.
      **브랜드가 '출시'라고 말한 글만** 고른다.

신제품 신호:
  is_new       채택분 전건 True. 제목이 `신메뉴`/`메뉴`와 `출시`/`선보`를 같이
               말하고, 상세 본문도 `[신메뉴 출시]` 또는 "신메뉴 … 출시했다"로
               한 번 더 확인된다(아래 _CONFIRM).
  released_at  목록의 `li.time` 이 `title="2026-03-09 10:25"` 로 분 단위까지 준다.
               출시를 알리는 글이라 출시일에 가장 가까운 값이다. 날짜만 쓴다.
               ⚠️ 2026-03-09 글 본문은 "3월 9일부터 … 판매된다"라 등록일과
               판매 시작일이 같았다. 다만 2026-01-07 글은 본문이 "본격적인 여름
               시즌을 맞아"라고 써 **기사 자체가 철 지난 재게시**다. 등록일을
               출시일로 믿는 데는 그만큼의 오차가 있다.

**제목만으로는 못 거른다.** 15건 중 상품 글은 일부고 나머지가 기부 캠페인·방송
출연·수상이다. 그렇다고 느슨하게 잡으면 `카레맛집`·`시그니처 규동` 같은 2024-12
사이트 구축 때 몰아 올린 메뉴 홍보 카드(날짜가 전부 12/16~12/18)가 신상으로
올라온다. 그래서 **'출시'라고 말한 글만** 받는다. 그 결과 아래 둘은 일부러 버린다.
    갓튀긴 왕새우튀김 우동   (2025-03-06)  — 출시라고 안 썼다
    대파듬뿍 네기규동        (2025-03-06)  — 〃
덜 가져오는 쪽이 없는 신상을 만들어내는 쪽보다 낫다.

상품명 뽑기:
  ① 본문에 `△`/`▲` 글머리표가 둘 이상이면 그게 상품 목록이다.
     "이번에 선보인 신메뉴는 △불닭마요규동 △불닭가라아게동 △불닭치즈나베
      △불닭멘치카츠카레 △불닭치즈규동 △불닭가츠동 등 총 6종" → 6건.
     ⚠️ 이 글은 제목이 `삼양식품 정품 '불닭소스' 활용한 신메뉴 출시` 라
     따옴표만 보면 **소스 이름**(재료)을 상품으로 집는다. 글머리표를 먼저 보는
     이유가 이거다.
  ② 글머리표가 없으면 제목의 `‘…’` 를 쓴다.
     "동경규동, 봄 신메뉴 ‘순두부야끼규나베’ 출시" → 순두부야끼규나베
     단, 따옴표 뒤에 `활용`·`사용`이 붙으면 그건 재료지 상품이 아니라 버린다.
  ③ 둘 다 없으면 제목에서 브랜드 접두와 출시 꼬리를 털어 쓴다.
     "캬베츠 가라아게동 출시" → 캬베츠 가라아게동
  그리고 `N종`만 남은 제목(`겨울 나베 3종 출시`·`돼지갈비동 2종 출시`)은
  **버린다.** 상품을 특정 못 하기 때문이다 — 오리온 어댑터의 _MULTI 와 같은 선.
  본문에도 개별 이름이 없어서(본문 전문이 "겨울나베 3종이 출시되었습니다") 캘 수도 없다.

이미지는 상세의 `og:image` 다. 글마다 다르고(`/thumbnail/20260309/…`) https 다.
본문은 `.board_txt_area` 에 있다. 아임웹 공통 클래스라 og:description 과 같은 값이
들어오지만, 길이 제한이 없는 쪽이 본문 노드라 그쪽을 읽는다.

desc 는 비운다. 본문이 통신사 기사 전문인 글이 섞여 있어 그대로 담으면 남의
기사를 싣는 꼴이 된다(CRAWLING-POLICY §3-①).

robots.txt: `Allow: /` 에 `/site_join`·`/login`·`/logout.cm`·`/shop_cart`·
            `/?mode*`·`/admin` 만 Disallow. `/notice` 는 허용이다.
            `/?mode*` 에 걸리지 않게 상세는 `bmode=view` 쿼리로만 연다
            (아임웹이 쓰는 파라미터는 `mode` 가 아니라 `bmode` 다).
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "동경에서먹었던규동"
SITE = "https://tokyo-gyudong.com"
LIST = SITE + "/notice"
MAX_PAGES = 6     # 폭주 방지. 현재 2페이지(전체 15건).
DELAY = 2.0

# 제목 선별. 둘 다 있어야 한다.
_NOUN = ("신메뉴", "메뉴", "규동", "나베", "우동", "카레", "동")
_VERB = ("출시", "선보")
# 통과하고도 상품 글이 아닌 것들. 전부 실측에서 걸린 제목이다.
_SKIP = ("캠페인", "기부", "방영", "선호도", "수상", "협약", "오픈", "리뉴얼",
         "이벤트", "채용", "모집", "성료", "시상")
# 본문이 한 번 더 확인해 주는 말. 없으면 제목만 믿지 않고 버린다.
_CONFIRM = re.compile(r"신메뉴|출시")

_BULLET = re.compile(r"[△▲■]\s*([^\s△▲■]{2,30})")
_QUOTED = re.compile(r"[‘'']([^’'']{2,28})[’'']")
_MULTI = re.compile(r"\d+\s*종")
# 제목 머리의 브랜드 표기. `동경규동, ` · `동경규동-` · `[신메뉴 출시] `
_LEAD = re.compile(r"^\s*(?:\[[^\]]*\]\s*)?(?:일식\s*전문\s*브랜드\s*)?"
                   r"(?:동경(?:에서먹었던)?규동)\s*[,\-–]?\s*")
_TAIL = re.compile(r"\s*(?:정식\s*)?(?:출시|선보(?:인다|여|였다)?)"
                   r"(?:\s*안내|합니다|했습니다)?\s*[!！.。]*\s*$")
# 따옴표 뒤가 이러면 상품이 아니라 재료·콘셉트다.
_NOT_PRODUCT_AFTER = ("활용", "사용", "콘셉트", "컨셉", "주제", "테마", "모티브")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _date(s: str) -> str:
    m = re.search(r"(20\d{2})-(\d{2})-(\d{2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _wanted(title: str) -> bool:
    t = _clean(title)
    if any(w in t for w in _SKIP):
        return False
    return any(w in t for w in _NOUN) and any(w in t for w in _VERB)


def _from_title(title: str) -> list:
    """제목 → 상품명. 특정 못 하면 빈 목록."""
    t = _clean(title)
    # ② 따옴표. 뒤에 '활용'·'콘셉트' 가 붙으면 재료·콘셉트라 버린다.
    for m in _QUOTED.finditer(t):
        tail = t[m.end():m.end() + 14]
        if not any(w in tail for w in _NOT_PRODUCT_AFTER):
            return [m.group(1).strip(" ,·")]
    # ③ 접두·꼬리를 털고 남은 것
    t = _TAIL.sub("", _LEAD.sub("", t)).strip(" ,·-")
    # 'N종' 만 남으면 상품을 특정 못 한 것이다
    if len(t) < 2 or _MULTI.search(t):
        return []
    return [t]


def _names(body: str, title: str) -> list:
    bullets = [b.strip(" ,·") for b in _BULLET.findall(body)]
    names = [b for b in bullets if len(b) >= 2] if len(bullets) >= 2 else _from_title(title)
    seen, out = set(), []
    for n in names:
        flat = n.replace(" ", "")
        if flat and flat not in seen:
            seen.add(flat)
            out.append(n)
    return out


def _rows(html: str) -> list:
    """(날짜, 상세 URL, 제목)."""
    out = []
    for row in HTMLParser(html).css("ul.li_body"):
        a = row.css_first("a.list_text_title")
        tm = row.css_first("li.time")
        if not (a and tm):
            continue
        href = a.attributes.get("href", "")
        when = _date(tm.attributes.get("title", "") or tm.text())
        m = re.search(r"idx=(\d+)", href)
        if m and when:
            out.append((when, m.group(1), _clean(a.text())))
    return out


def fetch() -> list[Item]:
    cand, seen_id = [], set()
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            r = base.retry(lambda: c.get(LIST, params={"page": page}))
            r.raise_for_status()
            rows = _rows(r.text)
            if not rows:
                if page == 1:
                    raise RuntimeError("동경규동 /notice: 글 0건 — 셀렉터가 깨졌을 수 있다")
                break
            # 범위를 넘긴 page 는 마지막 페이지를 되돌려준다(실측: page=3 이 page=2 와 동일).
            if all(i in seen_id for _, i, _ in rows):
                break
            for when, idx, title in rows:
                if idx in seen_id:
                    continue
                seen_id.add(idx)
                if _wanted(title):
                    cand.append((when, idx, title))
            time.sleep(DELAY)

        items: list[Item] = []
        seen = set()
        for when, idx, title in cand:
            time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"bmode": "view",
                                                       "idx": idx, "t": "board"}))
            r.raise_for_status()
            doc = HTMLParser(r.text)
            atc = doc.css_first(".board_txt_area")
            if atc is None:
                raise RuntimeError(f"동경규동 idx={idx}: 본문(.board_txt_area)이 없다")
            body = _clean(atc.text())
            if not _CONFIRM.search(body):
                continue      # 제목만 그래 보였던 글. 조용히 넘긴다.
            img = ""
            for m in doc.css("meta"):
                if m.attributes.get("property") == "og:image":
                    img = m.attributes.get("content", "")
                    break
            for name in _names(body, title):
                it = Item(
                    brand=BRAND,
                    name=name,
                    image=img,
                    released_at=when,
                    is_new=True,
                    url=f"{LIST}?bmode=view&idx={idx}&t=board",
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)
    return items
