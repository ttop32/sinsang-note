"""매일유업 — 보도자료에서 신제품과 출시일을 뽑는다.

오뚜기·오리온·샘표·해태제과식품과 같은 계보다(보도자료 제목 → 상품명).
조인 규칙은 `collectors/maker_orion.py` 것을 그대로 가져왔다.

**게시판이 셋인데 쓸 수 있는 건 하나다. 이게 이 사이트의 핵심이다.**

| 경로 | 이름 | 총건수 | 최신 | 판정 |
|---|---|---:|---|---|
| `/news/press.jsp` | **보도자료(자사 발표)** | **11** | 2026-09-29 | ✅ 이것만 쓴다 |
| `/news/news.jsp` | 매일뉴스 | 705 | 2026-08-07 | ❌ 전부 `[공지]` — 처리방침 개정·점검 안내 |
| `/news/news.jsp?scode=press` | 언론보도 스크랩 | 666 | **2020-06-22** | ❌ 6년째 멈춤 |

1차 조사가 `/news/news.jsp?scode=notice` 를 보고 "날짜 토큰 36개, 쉬움"으로
적었는데 **그 날짜는 공지 날짜**다. 쓸 수 있는 건 `/news/press.jsp` 쪽이다.

수집 경로. 2026-10-02 실측:
  GET https://www.maeil.com/news/press.jsp   200 / 169,193B
    <article class="lst_isotope" data-order="4">
      <div class="thumb"><a href="press_view.jsp?idx=8&sword=">
        <img src="/UploadedFiles/press/20260831132238633.jpg"></a></div>
      <div class="cont">
        <h1 class="wBk"><a href="press_view.jsp?idx=8">
            저당으로 가벼운 '어메이징 오트 말차' 출시</a></h1>
        <p class="writer"><span>2026.09.01</span></p>
        <p class="t1 wBk">…요약 본문…</p>
      </div>
    </article>
  선택자 `article.lst_isotope` → `h1 a`(제목·링크) · `p.writer span`(날짜) ·
  `p.t1`(요약) · `.thumb img`(사진).
  **목록에 요약문과 사진이 다 있다 — 상세를 열 필요가 없다.**

⚠️ **페이지네이션이 없다.** `idx` 가 2~12 로 연속이고 `paging` 토큰이 하나도
   없다. **게시판을 최근에 초기화한 것으로 보인다**(idx 가 1 이 아니라 2 부터
   시작한다). 과거 이력은 못 가져온다 — **증분 수집만 가능**하다.
   그래서 `DAYS` 를 계보 기본(300)으로 두되, 어차피 전체가 3개월치뿐이다.

⚠️ **건강기능식품·웰니스 브랜드가 절반이다.** `셀렉스`(근력단백질·썬화이버
   당솔브)가 보도자료에 자주 뜬다. 편의점 식품 축이 아니라 `_NOT_OUR_LINE`
   으로 막는다(빙그레 `프롬뉴트리`·풀무원헬스케어와 같은 성격 문제,
   notes/CANDIDATES-MAKER.md §판단 ⑤).
   ⚠️ `퓨어틴` 은 **단백질 '음료'** 라 남겼다 — 분말 보충제가 아니라
      우유 농축 RTD 다. 셀렉스(분말·건기식)와 축이 다르다.

⚠️ **이미지 파일명의 타임스탬프를 날짜로 쓰지 마라.**
     /UploadedFiles/press/20260831132238633.jpg  ↔  `p.writer` 2026.09.01
   여기선 파일명이 **하루 빠르다**. 크라운은 두 달 빠르고 해태는 하루 늦다.
   **어느 쪽으로도 못 믿는다.** 날짜는 `p.writer span` 에서만 읽는다.

**조인 결과: 11건 중 2건.** 전수로 훑은 버린 쪽 —
  행사·시상·방송·후원·해외입점 6건 · 건기식(셀렉스) 2건 ·
  `상하목장 콩물두유 3종`(묶음 기사, `_MULTI` 가 버린다. **진짜 신제품인데
  놓치는 아는 손실**이다) 1건.

robots: `https://www.maeil.com/robots.txt` → **200, 24바이트. 전문:**
```
User-agent: Yeti
Allow:/
```
        ⚠️ **`User-agent: *` 그룹이 아예 없다.** RFC 9309 상 우리 UA 에
        적용되는 규칙이 없으므로 금지는 아니지만, 네이버 하나만 상정한
        허용목록 형태라 "명시한 봇만 환영" 의도일 수 있다. 1·3차 조사가 둘 다
        "운영자 판단 필요"로 남겼고, **운영자가 robots 제약을 무시하기로
        결정**해서 등록한다. 참고로 페이지 `<meta name="Robots"
        content="INDEX, FOLLOW">` 는 색인 허용을 선언한다.
약관:   확인하지 않았다.
"""
import re
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "매일유업"
SITE = "https://www.maeil.com"
LIST = SITE + "/news/press.jsp"
DAYS = 300

# 편의점 식품 축이 아닌 계열 브랜드. 주어(브랜드명)로 거르는 게 키워드보다 정확하다.
# ⚠️ `퓨어틴`(단백질 음료 RTD)은 넣지 마라 — 분말 보충제가 아니다.
_NOT_OUR_LINE = ("셀렉스",)   # 건강기능식품·단백질 분말

# --- 제목 → 상품명 (maker_orion 과 같은 규칙) --------------------------------
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭|런칭)")
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
_MULTI = re.compile(r"\d+\s*종")
_TRAIL_SEP = re.compile(r"^\s*[·∙,、/]")
_NEXT_QUOTE = re.compile(r"^\s*[‘’'`]")

_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "협약", "체결", "주주총회", "후원", "기부", "추모", "공모", "발대식",
         "심포지엄", "박람회", "팝업", "캠페인", "발탁", "앰배서더", "재단",
         "경연", "시상", "간담회", "개최", "스폰서", "리뉴얼", "실적",
         "매진", "진행", "참가", "참여", "전개", "지원", "프로젝트",
         # 매일유업 실측 추가분.
         "방송", "홈쇼핑", "이벤트", "입점", "공모전", "부스",
         # 국내 출시가 아닌 건 화면에 올리면 거짓이 된다.
         "日", "美", "글로벌", "수출", "해외", "북미")
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱")
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")
_REPACK_HEAD = ("에디션", "라벨")
_REPACK_MID = ("테마", "에디션", "라벨", "컬래버", "콜라보")
_REPACK_NAME = ("에디션", "컬렉션", "한정판", "선물세트", "기획세트", "기획팩")


def _pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열."""
    t = " ".join(title.split())
    if any(w in t for w in _NOT_OUR_LINE):
        return ""
    if any(w in m.group(1) for m in _HEAD.finditer(t) for w in _REPACK_HEAD):
        return ""
    body = _HEAD.sub(" ", t)
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
    if not quoted or any(w in head[quoted.end():] for w in _BETWEEN):
        return ""
    rest = head[quoted.end():]
    if _TRAIL_SEP.match(rest) or _NEXT_QUOTE.match(rest):
        return ""
    hq = list(_SINGLE.finditer(head))
    if len(hq) >= 2 and not head[hq[-2].end():hq[-1].start()].strip():
        return ""
    name = quoted.group(1).strip(" ,·∙")
    if len(name) < 2 or any(c in name for c in "·∙&?!"):
        return ""
    if any(w in name for w in _REPACK_NAME):
        return ""
    return name


def _date(s: str) -> str:
    """'2026.09.01' → '2026-09-01'. 월·일 범위를 검증한다."""
    m = re.match(r"^\s*(20\d{2})[-.](\d{1,2})[-.](\d{1,2})\s*$", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _abs(path: str) -> str:
    path = (path or "").strip()
    if not path or path.startswith("data:"):
        return ""
    if path.startswith("http"):
        return path if path.startswith("https://") else ""
    return SITE + path


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST))
        r.raise_for_status()
        arts = HTMLParser(r.text).css("article.lst_isotope")

        # 셀렉터가 바뀌면 조용히 0건이 되는 게 제일 나쁘다. 11건짜리 게시판이라
        # 적지만 0 은 아니다.
        if not arts:
            raise ValueError(
                f"매일유업 보도자료가 비었다. {r.url} → {len(r.content)}B — 목록 "
                f"셀렉터(article.lst_isotope / h1 a / p.writer span)가 바뀌었는지 "
                f"확인하라")

        for art in arts:
            h = art.css_first("h1 a")
            w = art.css_first("p.writer span")
            if not h:
                continue
            title = " ".join(h.text().split())
            released = _date(w.text(strip=True)) if w else ""
            if released and released < floor:
                continue
            name = _pick(title)
            if not name:
                continue
            img = art.css_first(".thumb img")
            summary = art.css_first("p.t1")
            href = (h.attributes.get("href") or "").split("&")[0]
            it = Item(
                brand=BRAND,
                name=name,
                # 요약문이 목록에 있다. 없으면 제목을 쓴다.
                desc=" ".join((summary.text() if summary else title).split())[:200],
                # ⚠️ 파일명의 타임스탬프를 날짜로 줍지 마라(위 docstring).
                image=_abs(img.attributes.get("src") if img else ""),
                released_at=released,
                is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                url=f"{SITE}/news/{href}" if href else LIST,
            )
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)
    return items
