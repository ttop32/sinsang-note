"""면사랑 — 뉴스 게시판에서 신제품과 출시일을 뽑는다.

오뚜기·오리온·샘표·삼양식품과 같은 계보다(보도자료 제목 → 상품명).
조인 규칙은 `collectors/maker_orion.py` 것을 바탕으로 하되 **상품명 추출만
`collectors/maker_sajo.py` 쪽을 따랐다** — 사유는 아래 §제목 형식.

면·소스 전문기업이다(1991년 설립, 냉동면·생면·건면·밀키트·육수·소스).
**라면 제조사는 아니다.** 국내 라면 시장은 농심 55.5% · 오뚜기 21.1% ·
삼양식품 12.1% · 팔도 8.6% 로 상위 4사가 **97.3%** 를 먹고 네 곳 다 이미
붙어 있다(2025년 판매액, notes/CANDIDATES-RAMEN-FROZEN.md §라면).
면사랑은 그 바깥의 **면류·냉동면** 축이라 `brand_sub` 를 `냉동식품` 으로 둔다.

수집 경로. 2026-10-02 실측:
  GET https://www.noodlelovers.com/site/main/archive/post/category/news?cp=1
                                                          200 / 45,877B
    <ul class="news-item-list">
     <li class="news-item">
       <div class="thumbnail-wrap">
         <img src="/site/main/file/thumbnail/1527" alt="면사랑 냉동 소스 5종 출시"></div>
       <div class="text-wrap">
         <p class="title">면사랑, 중식·양식 냉동 소스 5종 출시</p>
         <div class="desc">- 별도 살균 과정 없이 …</div>
         <p class="date">2026-09-01</p>
         <div class="button default"><a href="/site/main/archive/post/면사랑-중식-양식-냉동-소스-5종-출시?cp=1…">
  **완전 SSR. 제목이 잘리지 않는다** — 상세를 열 필요가 없다.
  페이지당 10건, `?cp=N`(1·2·3 실측, 날짜가 내려간다).
  ⚠️ 상세 주소 슬러그가 **한글**이다. httpx 가 알아서 인코딩하니 손대지 마라.
  ⚠️ 썸네일은 `/site/main/file/thumbnail/<id>` 꼴이라 파일명에 날짜가 없다.

## 제목 형식 — 따옴표가 **없는 제목이 섞인다** (여기가 핵심)

오리온 계열 `_pick()` 은 "따옴표 안이 상품명" 을 전제한다. 면사랑은 절반이
따옴표를 안 쓴다. 30건 전수에서 본 두 꼴:
    면사랑, 여름 간편식 수요 겨냥 ‘냉동면밀키트’ 3종 출시     ← 따옴표 있음
    면사랑, 중식·양식 냉동 소스 5종 출시                      ← **따옴표 없음**
그대로 오리온 규칙을 쓰면 뒤쪽이 통째로 날아간다. 그래서 사조 방식을 쓴다 —
**주어(`…면사랑,`)를 떼고, 따옴표가 있으면 첫 따옴표부터, 없으면 머리 전체를
동사 앞까지 잡아** 따옴표 기호와 `N종` 꼬리를 턴다.
  ⚠️ 주어가 맨 앞에 없는 제목이 있다(`국물에 넣어도 쫄깃함 유지…면사랑, ‘수제비 2종’ 출시`).
     그래서 `^면사랑,` 이 아니라 **`^.*?면사랑,`** 으로 뗀다.
  ⚠️ `N종` 을 오리온처럼 '버린다' 로 두면 안 된다 — 면사랑 출시 기사의 **대부분**이
     `N종 출시` 라 그러면 수확이 0이 된다. 여기서는 **꼬리만 떼고 상품은 살린다.**
     사조도 같은 판단을 했다(`‘해표 더 고소한 김’ 2종 출시` → `해표 더 고소한 김`).

## 버리는 쪽 (3페이지 30건 전수 확인, 2025-08-22 ~ 2026-09-01)

출시·선봬 **8건**이 남고 22건이 버려진다:
    문화예술 사회공헌 7건 (신진 유망 연주자·어린이 동요사랑 합창제·에세이 공모전)
    행사·전시 4건 (미디어데이·웰스토리 푸드페스타·네이버 푸드페스타·컬리푸드페스타)
    할인·프로모션 4건 (면사랑데이·넾다세일·냉동밀키트 위크)
    판매 1위·라인업 강화 3건 · 공모/모집 2건 · TV CF 공개 1건 · 주주총회 공고 1건
남는 쪽 실측: `중식·양식 냉동 소스` · `냉동면밀키트` · `수제비` · `100%메밀면` ·
`가쓰오우동` · `깔끔한 멸치육수` · `프리미엄 만능바지락육수` · `쫄깃한 생칼국수` ·
`치즈가득통모짜`.
⚠️ `‘덜짠·저당’ 소스 4종 출시로 ‘누들 헬시’ 라인업 강화` 는 **아는 손실**이다 —
   진짜 출시 기사인데 `강화` 가 걸려 버려진다. 따옴표가 둘이고 뒤엣것이 라인업
   이름이라 살리려다 엉뚱한 이름을 집는 쪽이 더 나쁘다.

**일괄 등록 흔적 — 없다.** 30건 날짜가 전부 다르고 1년에 걸쳐 고르다.

robots: https://www.noodlelovers.com/robots.txt → 200 / 23바이트.
        `User-agent: *` / `Allow: /`. 이번 조사 중 가장 깨끗한 축이다.
약관:   확인하지 않았다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "면사랑"
SITE = "https://www.noodlelovers.com"
LIST = SITE + "/site/main/archive/post/category/news"
PER_PAGE = 10
MAX_PAGES = 4        # 한 페이지 10건 = 약 1년치. 폭주 방지 상한.
DAYS = 300
DELAY = 2.2

# --- 제목 → 상품명 (상품명 추출은 maker_sajo, 역필터는 maker_orion) ----------
_SUBJECT = re.compile(r"^.*?면사랑\s*,\s*")      # 주어가 맨 앞에 없는 제목이 있다
_QUOTED = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_QUOTE_CHARS = re.compile(r"[‘’'`“”\"]")
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭|런칭)")
_COUNT_TAIL = re.compile(r"\s*\d+\s*종\s*$")
_NEW_TAIL = re.compile(r"\s*신제품\s*$")

_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "협약", "체결", "주주총회", "후원", "기부", "추모", "공모", "발대식",
         "심포지엄", "박람회", "팝업", "캠페인", "발탁", "앰배서더", "재단",
         "경연", "시상", "간담회", "개최", "스폰서", "리뉴얼", "실적",
         "매진", "진행", "참가", "참여", "전개", "지원", "프로젝트",
         "오픈", "이벤트", "광고", "조회수", "할인", "선물", "프로모션",
         "모집", "공개", "강화", "1위", "페스타", "미디어데이", "공고",
         # 국내 출시가 아닌 건 화면에 올리면 거짓이 된다.
         "日", "美", "글로벌", "수출", "해외", "현지")


def _pick(title: str) -> str:
    """'면사랑, 중식·양식 냉동 소스 5종 출시' → '중식·양식 냉동 소스'.

    따옴표가 있으면 첫 따옴표부터, 없으면 주어를 뗀 머리 전체를 쓴다.
    상품을 특정 못 하면 빈 문자열.
    """
    t = " ".join(title.split())
    if any(w in t for w in _SKIP):
        return ""
    verb = None
    for m in _VERB.finditer(t):
        verb = m
    if not verb:
        return ""
    head = _SUBJECT.sub("", t[:verb.start()])
    q = list(_QUOTED.finditer(head))
    seg = head[q[0].start():] if q else head
    name = _QUOTE_CHARS.sub("", seg)
    name = _NEW_TAIL.sub("", _COUNT_TAIL.sub("", name.strip())).strip(" ,·∙!…")
    # 따옴표 없는 제목에서 통째로 잡은 머리는 수식어가 길게 붙어 있을 수 있다.
    if not (2 <= len(name) <= 40):
        return ""
    return name


def _date(s: str) -> str:
    """'2026-09-01' → '2026-09-01'. 월·일 범위를 검증한다."""
    m = re.match(r"^\s*(20\d{2})[-.](\d{1,2})[-.](\d{1,2})\s*$", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _rows(html: str) -> list[tuple]:
    """목록 HTML → (날짜, 제목, href, 이미지) 목록."""
    out = []
    for li in HTMLParser(html).css("ul.news-item-list li.news-item"):
        tit = li.css_first("p.title")
        if not tit:
            continue
        dt = li.css_first("p.date")
        a = li.css_first(".button a")
        img = li.css_first(".thumbnail-wrap img")
        src = (img.attributes.get("src") or "").strip() if img else ""
        href = (a.attributes.get("href") or "").strip() if a else ""
        out.append((_date(dt.text(strip=True) if dt else ""),
                    " ".join(tit.text().split()),
                    href,
                    SITE + src if src.startswith("/") else src))
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"cp": page}))
            r.raise_for_status()
            rows = _rows(r.text)

            # 셀렉터가 바뀌면 조용히 0건이 되는 게 제일 나쁘다. 1년에 30건씩
            # 쌓이는 게시판이라 1페이지는 반드시 와야 한다.
            if page == 1 and not rows:
                raise ValueError(
                    f"면사랑 뉴스 1페이지가 비었다. {r.url} → {len(r.content)}B — "
                    f"목록 셀렉터(ul.news-item-list li.news-item / p.title / "
                    f"p.date)가 바뀌었는지 확인하라")
            if not rows:
                break

            for released, title, href, img in rows:
                if released and released < floor:
                    continue
                name = _pick(title)
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=_SUBJECT.sub("", " ".join(title.split())),
                    image=img,
                    released_at=released,
                    is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                    url=SITE + href if href.startswith("/") else (href or LIST),
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

            fresh = [d for d, *_ in rows if d]
            if fresh and max(fresh) < floor:
                break
    return items
