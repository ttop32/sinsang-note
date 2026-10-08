"""한화갤러리아 보도자료 — 파이브가이즈·벤슨 두 브랜드가 함께 쓰는 공용 모듈.

**이 파일은 어댑터가 아니다.** `BRAND`·`BRANDS`·`fetch()` 가 **일부러 없다** —
collect.orphans() 는 `BRANDS`/`BRAND` 가 없는 모듈을 건너뛰므로(실측: 그 분기가
`if not names: continue` 다) ADAPTERS 에 등록하지 않아도 경고가 나지 않는다.
collectors/ 안에서 fetch() 가 없는 파일은 base.py 말고 이게 처음이라 적어 둔다.

쓰는 쪽은 두 곳이다.
    collectors/burger_fiveguys.py  — 메뉴판 '기간 한정' 블록 + 여기서 더한다
    collectors/dessert_benson.py   — 자사몰 NEW 탭 + 여기서 더한다
`rows()` 가 **모듈 수준에 캐시**돼 있어서, 두 어댑터가 한 프로세스(collect.main)
에서 돌면 목록 HTML 을 **한 번만** 받는다. 따로 받게 두면 같은 6페이지를 두 번
긁게 된다.

## 🔴 페이징은 JS 가 아니다 — 파라미터 이름이 달랐을 뿐이다 (2026-10-08 정정)

notes/RECHECK-ROBOTS-MAKER.md §한화갤러리아 에 "`?page=2…5` 를 줘도 본문이
21,904B 로 전부 동일하다(쿼리가 아니라 JS 로 넘긴다)" 라고 적혀 있는데
**틀렸다.** 목록 HTML 안의 페이저가 직접 알려준다:

    <div class="pagination">
      <span class="page is-current">1</span>
      <a href="/promotion/news?p=1" class="page">2</a>
      …
      <a href="/promotion/news?p=5" class="next">

즉 **경로는 `.html` 없는 `/promotion/news` 이고 파라미터는 `p` 이며 0부터**다.
`news.html?page=2` 가 같은 바이트를 돌려준 건 정적 파일 `news.html` 이 모르는
쿼리를 무시했기 때문이다. 실측(2026-10-08) —

    /promotion/news?p=0   200 / 21,904B  12건  2026-10-02 ~ 2026-05-28
    /promotion/news?p=1   200 / 21,902B  12건  2026-05-21 ~ 2026-03-12
    /promotion/news?p=2   200 / 22,050B  12건  2026-03-02 ~ 2025-12-10
    …
    /promotion/news?p=7   200 / 21,754B  12건  2025-04-28 ~ 2025-03-09

12페이지(144건)를 받아 2024-04-08 까지 끊김 없이 이어지는 것을 확인했다.
서버가 그려 주는 HTML 이라 XHR 도 브라우저도 필요 없다. `DAYS` 창을 벗어나면
멈추므로 평소 요청은 3페이지다.

## robots.txt 는 **없다** (soft-404)

    https://www.hanwhagalleria.co.kr/robots.txt
      → 200 / 1,047B / content-type: text/html
      → 본문이 `<title>페이지를 찾을 수 없습니다. | 한화갤러리아</title>` 인
        404 안내 페이지다.
robots 파일이 없는 것이다(규칙 없음 = 허용). **200 을 성공으로 읽으면 안 되는**
교과서 사례라 그대로 적어 둔다 — 상태코드가 아니라 본문을 봐야 한다.

## 🔴 이 게시판의 진짜 성격 — 144건 중 115건이 **백화점 기사**다

여기는 '한화갤러리아' 법인 전체의 보도자료다. 2026-10-08 전수(12페이지 144건)
실측 분포:

    갤러리아百(백화점) 기사  78건   명품·시계·주얼리·전시·팝업·웨딩페어·선물세트
    벤슨                    29건
    파이브가이즈             18건
    그 외(한화 그룹 소식 등) 19건

그래서 **제목에서 브랜드를 식별하는 것이 이 모듈의 첫 일**이다. 제목에 브랜드
이름이 없으면 통째로 버린다. `벤슨` 이 짧은 말이라 다른 단어에 섞일까 봐 144건
전건의 `벤슨` 출현 문맥(앞뒤 8자)을 찍어서 확인했다 — **29건 전부 브랜드를
가리켰다.** 오탐은 0건이다(`스티븐슨`·`벤슨앤헤지스` 류가 없다).
`FG코리아` 는 0건, `에프지코리아` 는 1건인데 그마저 MOU 체결 기사다.

## 출시 기사는 4년치에 사실상 없다 — 그게 정상이다

브랜드 기사 47건(벤슨 29 + 파이브가이즈 18)의 성격은 이렇다.

    출점·오픈·호점·입점·상륙 …… 24건   ← 매장 이야기지 상품이 아니다
    팝업·행사·캠페인·콜라보 ……… 12건
    실적·돌파·인기몰이 ………………  7건
    **신제품 출시** ………………………  4건
         2026-07-02 벤슨, 하츠투하츠 협업 '레몬탱' 출시          ← 집는다
         2026-04-29 벤슨, 여름 시즌 메뉴 출시                     ← 상품명 없음
         2026-01-26 벤슨, 신제품 쿠키샌드∙썬데 출시              ← 둘을 이어 붙인 이름
         2025-09-28 벤슨, 엔믹스와 콜라보 신제품 출시            ← 상품명 없음

**파이브가이즈는 18건 전부 매장·실적 기사다. 출시 기사가 0건이다.**
0~1건이 이 소스의 정상 수확이고 '수집 실패'가 아니다.

## 제목 → 상품명

정본은 `collectors/maker_ottogi.py` 의 `_pick()` 이다. 그 규칙을 그대로 쓰고
여기서만 두 가지를 더했다.

① **맨 앞 ‘…’ 홍보 헤드라인을 떼어낸다**(`_LEAD`).
   오뚜기 규칙은 “…” 만 헤드라인으로 보고 지우는데, 이 게시판은 **홑따옴표로도
   헤드라인을 쓴다.** 안 떼면 헤드라인이 상품명이 된다 — 실측 오탐:
       ‘셰프가 만든 프리미엄 디저트’ 벤슨, 신제품 쿠키샌드∙썬데 출시
         → 동사 앞 마지막 따옴표가 헤드라인이라 '셰프가 만든 프리미엄 디저트'
            가 상품명으로 나온다.
   떼도 진짜 상품명은 안 다친다(실측 47건). 이 게시판에서 상품명을 감싼
   따옴표는 **항상 주어 뒤**에 온다 — 위치가 그 구분이다.
② `_SKIP` 에 **매장·행사 축**을 넣었다(`호점`·`출점`·`상륙`·`입점`·`오픈` 등).
   신세계푸드가 '노브랜드 버거' 를 통째로 뺀 것과 같은 판단이다.
   ⚠️ `협업` 은 `_SKIP` 에 **넣지 않았다.** 넣으면 유일한 수확인 '레몬탱'
      (하츠투하츠 협업 신규 플레이버)이 죽는다. 오뚜기처럼 `_BETWEEN` 에만
      둔다 — 따옴표와 동사 **사이**에 있을 때만 제휴 상대로 본다.

`47건 전건으로 검증`했고 통과하는 건 '레몬탱' 하나다. 백화점 기사 115건은
브랜드 이름이 없어서 `_pick` 까지 가지도 않는다.

## 날짜

목록·상세 모두 `<time class="date" datetime="2026-07-02">` 로 준다.
144건의 날짜가 전부 다르고 2024-04 ~ 2026-10 으로 고르다 — **일괄 등록 흔적이
없다.** 그래서 `released_at` 에 넣는다(`uploaded_at` 이 아니다).

## 상세 페이지

`/promotion/news/id/<uuid>?p=0` 이 서버렌더다. `figure.top-cover img` 에
큰 사진이, 그 아래 `<p>` 에 본문이 있다. 뽑힌 기사(현재 1건)만 들어가서
`desc`·`image` 를 채운다. 목록 썸네일보다 상세 사진이 크다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

SITE = "https://www.hanwhagalleria.co.kr"
LIST = SITE + "/promotion/news"        # ⚠️ `.html` 을 붙이면 `p` 가 안 먹는다
NEWS_HTML = SITE + "/promotion/news.html"   # 사람이 여는 면(1페이지 고정)
PER_PAGE = 12
MAX_PAGES = 12       # 폭주 방지. 실측 144건까지 받아 봤다.
MIN_ROWS = 6         # 1페이지가 이보다 적으면 목록이 깨진 것으로 본다(정상 12)
DAYS = 300
DELAY = 2.0

# --- 제목 → 상품명 (maker_ottogi._pick 계보) ---------------------------------
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭)")
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
# 제목 **맨 앞**의 홑따옴표 헤드라인. 사유는 docstring ①.
_LEAD = re.compile(r"^\s*[‘'`][^’'`]{2,60}[’'`]\s*")
_MULTI = re.compile(r"\d+\s*종")
_TRAIL_SEP = re.compile(r"^\s*[·∙,、/]")

# 오뚜기 `_SKIP` + 이 게시판의 매장·행사 축. 사유는 docstring ②.
_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "협약", "체결", "주주총회", "후원", "기부", "추모", "공모", "발대식",
         "심포지엄", "박람회", "팝업", "캠페인", "발탁", "앰배서더", "재단",
         "경연", "시상", "간담회", "개최", "스폰서", "리뉴얼", "실적",
         "매진", "진행", "참가", "참여", "전개", "지원", "프로모션", "할인",
         "이벤트", "모집", "인수", "MOU",
         # 매장 이야기. 백화점·외식 보도자료의 대부분이고 상품이 아니다.
         "호점", "출점", "오픈", "상륙", "입점", "로드숍", "매장", "점포",
         "운영", "조성", "확대", "강화", "소개", "증가", "인기몰이",
         # 백화점 축. 상품이 아니라 행사·전시·선물세트다.
         "전시", "선물세트", "예약판매", "페어", "페스타", "아트위크")
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱")
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")
_REPACK_HEAD = ("에디션", "라벨")
_REPACK_MID = ("테마", "에디션", "라벨", "컬래버", "콜라보")


def pick(title: str, brand: str) -> str:
    """보도자료 제목에서 그 브랜드의 상품명을 뽑는다. 아니면 빈 문자열.

    브랜드 이름이 제목에 없으면 **남의 기사**다(백화점 기사가 115/144건).
    """
    t = " ".join((title or "").split())
    if brand not in t:
        return ""
    if any(w in m.group(1) for m in _HEAD.finditer(t) for w in _REPACK_HEAD):
        return ""
    body = _LEAD.sub("", _HEAD.sub(" ", t).strip())
    if any(w in body for w in _SKIP) or _MULTI.search(body):
        return ""
    qs = list(_SINGLE.finditer(body))
    if len(qs) >= 2 and any(w in body[qs[-2].end():qs[-1].start()] for w in _REPACK_MID):
        return ""
    verb = None
    for m in _VERB.finditer(body):
        verb = m
    if not verb or any(w in body[verb.end():] for w in _TAIL):
        return ""
    head = body[:verb.start()]
    quoted = None
    for m in _SINGLE.finditer(head):
        quoted = m
    # 따옴표가 없으면 상품을 특정 못 한 것이다(오뚜기와 같은 판단).
    # 실측: `벤슨, 여름 시즌 메뉴 출시` · `벤슨, 연말 맞아 신제품 케이크∙아이스크림 출시`
    if not quoted or any(w in head[quoted.end():] for w in _BETWEEN):
        return ""
    if _TRAIL_SEP.match(head[quoted.end():]):
        return ""
    name = quoted.group(1).strip(" ,·∙")
    if len(name) < 2 or any(c in name for c in "·∙&?"):
        return ""
    # 브랜드·회사 이름 자체가 뽑히는 기사(`‘벤슨(Benson)’ 5월 론칭`)는 상품이 아니다.
    if brand in name or "갤러리아" in name:
        return ""
    return name


def _text(el) -> str:
    return " ".join(el.text().split()) if el is not None else ""


def _rows(html: str) -> list[dict]:
    """목록 HTML → [{date, title, href, image}]."""
    out = []
    for li in HTMLParser(html).css("li.press-item"):
        a = li.css_first("a")
        t = li.css_first("time.date")
        ti = li.css_first("p.press-title")
        if not (a and ti):
            continue
        img = li.css_first("img.press-img")
        out.append({
            # ⚠️ selectolax 는 값 없는 속성에 None 을 준다. 기본값이 안 먹는다.
            "date": (t.attributes.get("datetime") or "") if t is not None else "",
            "title": _text(ti),
            "href": (a.attributes.get("href") or ""),
            "image": (img.attributes.get("src") or "") if img is not None else "",
        })
    return out


_CACHE: list[dict] | None = None


def rows() -> list[dict]:
    """보도자료 목록. **한 프로세스에서 한 번만 받는다**(두 어댑터가 공유).

    1페이지가 비면 `raise` 한다 — 목록 0행은 소스 고장이다. 상품 0건은
    정상이라 그건 각 어댑터가 `ALLOW_EMPTY` 로 다룬다.
    """
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    out: list[dict] = []
    with base.client() as c:
        for p in range(MAX_PAGES):
            if p:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"p": p}))
            r.raise_for_status()
            page = _rows(r.text)
            if p == 0 and len(page) < MIN_ROWS:
                raise RuntimeError(
                    f"한화갤러리아 보도자료 1페이지가 {len(page)}행이다"
                    f"(기대 {PER_PAGE}행). {r.url} → {len(r.content)}B — 경로"
                    f"(`/promotion/news`, `.html` 없음)나 `p` 파라미터,"
                    " 셀렉터(li.press-item / p.press-title / time.date)가"
                    " 바뀌었는지 확인하라")
            if not page:
                break
            out += page
            dates = [x["date"] for x in page if x["date"]]
            if dates and max(dates) < floor:
                break
    _CACHE = out
    return out


def _detail(c, url: str) -> tuple[str, str]:
    """상세 페이지에서 (설명 한 문단, 큰 사진). 실패하면 빈 값."""
    try:
        r = base.retry(lambda: c.get(url))
        r.raise_for_status()
    except Exception:
        return "", ""
    d = HTMLParser(r.text)
    art = d.css_first("article.news")
    if art is None:
        return "", ""
    img = art.css_first("figure.top-cover img")
    src = (img.attributes.get("src") or "") if img is not None else ""
    desc = ""
    for p in art.css("div.l-wrap p"):
        t = _text(p)
        # `■ …` 는 소제목이고 `[끝]` 은 보도자료 종료 표시다.
        if len(t) >= 20 and not t.startswith("■"):
            desc = t
            break
    return desc, src


def items(brand: str, **extra) -> list[Item]:
    """그 브랜드의 보도자료 신제품. `extra` 는 Item 에 그대로 넘긴다."""
    picked = []
    for r in rows():
        name = pick(r["title"], brand)
        if name:
            picked.append((name, r))

    out: list[Item] = []
    if not picked:
        return out
    with base.client() as c:
        for i, (name, r) in enumerate(picked):
            if i:
                time.sleep(DELAY)
            url = SITE + r["href"] if r["href"].startswith("/") else r["href"]
            desc, img = _detail(c, url) if url else ("", "")
            out.append(Item(
                brand=brand,
                name=name,
                desc=desc or r["title"],
                image=img or r["image"],
                # 날짜가 전건 제각각이라 일괄 등록이 아니다 → released_at.
                released_at=r["date"],
                is_new=True,          # 브랜드가 '출시' 라고 낸 기사다
                url=url or NEWS_HTML,
                **extra,
            ))
    return out
