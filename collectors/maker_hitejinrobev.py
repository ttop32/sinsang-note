"""하이트진로음료 — 보도자료에서 신제품과 출시일을 뽑는다.

하이트진로**음료**는 주류사가 아니라 **무알코올·생수·탄산 자회사**다.
브랜드가 `블랙보리`·`진로토닉워터`·`석수`·`티도씨`·`하이트제로`·`테라 제로` 다.
2차 조사가 음료 6곳을 돌아 롯데칠성 하나만 건졌는데 그 라운드에 이 회사가
빠져 있었다(notes/CANDIDATES-MAKER.md §⑨). 음료 축의 두 번째 소스다.

오뚜기·오리온·샘표·해태제과식품과 같은 계보다(보도자료 제목 → 상품명).
조인 규칙은 `collectors/maker_orion.py` 것을 그대로 가져왔다.

수집 경로. 2026-10-02 실측:
  GET https://www.hitejinrobeverage.com/ko/community/news        200 / 49,533B
    <a href="https://www.hitejinrobeverage.com/ko/community/news/647"
       class="ui-board-item">
      <p class="board-no">182</p>
      <p class="board-title">하이트진로음료, 검정보리 더한 이색 제로 탄산
                             '블랙보리 콜라' 출시</p>
      <p class="board-date">2026.07.13</p>
    </a>
  선택자 `a.ui-board-item` → `.board-no` · `.board-title` · `.board-date`.
  **완전 SSR.** 1페이지 20건, 페이지는 `?page=N`(목록 하단 링크로 확인).
  ⚠️ 글번호(`board-no` 182)와 URL id(647)가 **다르다.** 증분·식별은 URL id 로 해라.

🔴 **주류를 넣지 않는다 — 이 브랜드의 핵심 결정이다.**
   운영자가 국민건강증진법 제8조의2(광고 주체 제한)를 근거로 주류를 안 다루기로
   했다(근거 전문은 `collectors/base.py` 의 ALCOHOL 절).
   그런데 **`base.is_alcohol()` 은 이 회사 상품을 하나도 못 잡는다.** 실측:
       is_alcohol('테라 제로')              → False
       is_alcohol('하이트제로0.00 레몬&유자') → False
   이유가 둘 다 base.py 주석에 적혀 있다 — `테라` 는 **카스테라**를 물어서,
   `하이트` 는 **제조사명이라 음료까지 문다**고 일부러 뺀 단어다. 그리고
   `_ZERO_ABV`(`(?<!\\d)0\\.0(?!\\d)`)는 `0.00` 에 **안 걸린다**(뒤가 숫자라
   lookahead 가 막는다). 즉 **base 쪽에 기대면 그대로 통과한다.**
   → 단어 목록을 건드리는 건 이 레포에서 두 번째로 잦은 사고라(`카스`→카스테라
     28건 소멸) **base.py 는 손대지 않고 여기서 막는다.** `_ALCOHOL_LINE` 참고.

   **무엇을 빼고 무엇을 남겼나.**
     ❌ `테라 제로` · `하이트제로0.00 …`
        — 맥주 브랜드(테라·하이트)의 **논알코올 맥주**다. 법적으로는 주류가
          아니지만 **주류 브랜드를 그대로 쓴 맥주 모방 제품**이라, 올리면
          사실상 그 맥주 브랜드 광고가 된다. 업계 자신도 같은 사이트에서
          제품 소개엔 연령 게이트를 건다(base.py ALCOHOL 절의 21곳 실측).
     ✅ `블랙보리 콜라` · `진로토닉워터 청귤` · `석수` · `티도씨`
        — 보리음료·토닉워터·생수·차다. 술을 모방하지 않는다.
   ⚠️ **`진로토닉워터` 는 판단이 갈릴 수 있다.** 이름에 소주 브랜드 `진로` 가
      들어 있다. 다만 토닉워터는 소주의 무알코올판이 아니라 **독립 음료 카테고리**
      (칵테일 믹서)라 남겼다. 운영자가 반대로 보면 `_ALCOHOL_LINE` 에 `진로` 를
      더하면 된다 — **그 한 줄이 이 판단의 전부다.**
      (2024-02-08 `‘진로토닉 와일드피치’ 칵테일 쉐이커 기획세트 출시` 는
       **굿즈 묶음**이라 따로 버린다 — 🔴 전에 여기 "`_REPACK_NAME` 이 버린다" 고
       적었는데 **틀린 서술이었다.** `_REPACK_NAME` 은 뽑힌 이름만 보는데 이름은
       `진로토닉 와일드피치` 라 '기획세트' 가 안 들어간다. 2026-10-02 검수에서
       잡혀 `_GOODS_AFTER`(따옴표 뒤를 본다)를 새로 넣어 막았다.)

⚠️ **판매실적이 출시를 사칭한다. 이 브랜드에서 가장 비싼 함정이다.**
     2026-07-16  하이트진로 '테라 제로' 병 제품, 출시 10일 만에 90만 병 완판
     2026-07-02  하이트진로음료, '테라 제로' 출시 100일 만에 누적 판매 400만 캔 돌파
   `출시` 키워드만 쓰면 **테라 제로의 출시일이 3월 16일이 아니라 7월 2일로 밀린다.**
   계보의 `_TAIL`(`돌파`·`만에`·`완판`·`누적`)이 이미 셋 다 막는다(실측 확인).

⚠️ **사진이 없다.** 목록에 썸네일이 없고, 상세(`/ko/community/news/647`,
   44,026B)는 **본문이 JS 로 들어온다** — 원본 HTML 에 기사 텍스트도 사진도
   하나도 없다(`upload`·`file`·`attach` 경로 0건, `data:` 0건). 브랜드 페이지
   (`/ko/brand/blackboricola` 등)는 **브랜드 단위**라 맛 변형 상품에 붙이면
   거짓이 된다. → **Item.image 를 비운다.** 지어내지 않는다.

⚠️ **글 간격이 들쭉날쭉하다.** 2026년은 월 1~3건인데 2025년 하반기 이전으로
   가면 2025.02 → 2024.02 → 2023.06 으로 1년씩 뛴다. 그래서 `DAYS` 를 계보
   기본(300)이 아니라 **400** 으로 잡았다 — 300이면 1~2건밖에 안 남는다.
   그래도 과거 이력 수집은 기대치를 낮춰라.

**조인 결과: 1페이지 20건(2023-06-09 ~ 2026-08-07) 중 2건.**
버린 쪽도 전수로 훑었다 — 수상 4건 · 콜라보 기획전/이벤트 5건 · 광고 온에어 1건 ·
시음부스 1건 · 칼럼성 글 1건 · 판매실적 2건 · 논알코올 맥주 2건 · 기획세트 1건.

robots: `https://www.hitejinrobeverage.com/robots.txt` → **허용. 200, 150바이트.**
        `User-agent: *` 에 `Disallow: /manage$`·`/manage/`·`/*/manage$`·
        `/*/manage/` 넷뿐 + sitemap. `/ko/community/news` 는 안 걸린다.
약관:   확인하지 않았다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "하이트진로음료"
SITE = "https://www.hitejinrobeverage.com"
LIST = SITE + "/ko/community/news"
PAGE_SIZE = 20
MAX_PAGES = 2        # 폭주 방지 상한. 1페이지가 이미 3년치다.
DAYS = 400           # 글 간격이 들쭉날쭉하다. 위 docstring 참고.
DELAY = 2.2

# 🔴 주류 브랜드의 논알코올 라인. base.is_alcohol() 이 못 잡는다(위 docstring).
#    base.py 의 단어 목록은 건드리지 않는다 — 여기서만 막는다.
#    ⚠️ 상품명이 아니라 **기사 제목 전체**에 대고 본다. 제목에 '테라 제로' 가
#       있으면 그 기사는 통째로 그 제품 기사다.
_ALCOHOL_LINE = ("테라 제로", "테라제로", "하이트제로", "하이트 제로", "올프리")
# ⚠️ `올프리` 는 2026-10-02 검수에서 보탰다. 같은 게시판에 `하이트진로음료,
#    제로 넘어 '올프리'로 시장 공략`(2023-05-25)이 있는데 **올프리도 하이트진로의
#    논알코올 맥주 브랜드**다. 그 글은 `_VERB` 가 없어서 우연히 안 걸렸을 뿐,
#    `무알코올 맥주 '올프리' 출시` 꼴이 오면 그대로 수집된다.
#    세 글자라 부분일치가 걱정되는데, 이 게시판 2페이지 40건 전수에 `올프리` 가
#    든 제목은 그 1건뿐이고 음료 상품명에 '올프리' 가 들어갈 자리가 없다.

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
         # 하이트진로음료 실측 추가분.
         "광고", "온에어", "기획전", "시음", "이벤트", "체험단",
         "日", "美", "글로벌", "수출", "해외")
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱")
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")
_REPACK_HEAD = ("에디션", "라벨")
_REPACK_MID = ("테마", "에디션", "라벨", "컬래버", "콜라보")
_REPACK_NAME = ("에디션", "컬렉션", "한정판", "선물세트", "기획세트", "기획팩")
# 🔴 따옴표 **뒤**(상품명과 동사 사이)에 이게 오면 상품이 아니라 굿즈 묶음이다.
# 2026-10-02 검수 지적: `‘진로토닉 와일드피치’ 칵테일 쉐이커 기획세트 출시`
# (2024-02-08)는 docstring 이 "`_REPACK_NAME` 이 버린다" 고 적었는데 **틀렸다.**
# `_REPACK_NAME` 은 뽑힌 **이름**만 보는데 이름은 `진로토닉 와일드피치` 라
# '기획세트' 가 안 들어간다. 지금은 `DAYS=400` 창 밖이라 안 나올 뿐이고,
# 같은 모양이 또 오면 **칵테일 쉐이커 굿즈 세트가 상품으로 올라간다.**
_GOODS_AFTER = ("기획세트", "선물세트", "기획팩", "쉐이커", "굿즈", "키트")


def _pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열."""
    t = " ".join(title.split())
    if any(w in t for w in _ALCOHOL_LINE):
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
    if any(w in rest for w in _GOODS_AFTER):
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
    """'2026.07.13' → '2026-07-13'. 월·일 범위를 검증한다."""
    m = re.match(r"^\s*(20\d{2})[-.](\d{1,2})[-.](\d{1,2})\s*$", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _rows(html: str) -> list[tuple]:
    """목록 HTML → (날짜, 제목, 상세주소) 목록."""
    out = []
    for a in HTMLParser(html).css("a.ui-board-item"):
        t = a.css_first(".board-title")
        d = a.css_first(".board-date")
        href = (a.attributes.get("href") or "").strip()
        if not (t and d and "/community/news/" in href):
            continue
        out.append((_date(d.text(strip=True)),
                    " ".join(t.text().split()),
                    href if href.startswith("http") else SITE + href))
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"page": page}))
            r.raise_for_status()
            rows = _rows(r.text)

            # 셀렉터가 바뀌면 조용히 0건이 되는 게 제일 나쁘다. 185번까지 쌓인
            # 게시판이라 1페이지는 반드시 와야 한다.
            if page == 1 and not rows:
                raise ValueError(
                    f"하이트진로음료 보도자료 1페이지가 비었다. {r.url} → "
                    f"{len(r.content)}B, a.ui-board-item "
                    f"{len(HTMLParser(r.text).css('a.ui-board-item'))}개 — 목록 "
                    f"셀렉터(a.ui-board-item / .board-title / .board-date)가 "
                    f"바뀌었는지 확인하라")
            if not rows:
                break

            for released, title, url in rows:
                if released and released < floor:
                    continue
                name = _pick(title)
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    # 기사 제목이 그대로 설명이 된다. 앞의 회사명만 턴다.
                    desc=re.sub(r"^\s*하이트진로(음료)?[^,]{0,8},\s*", "", title),
                    # 사진이 없다. 지어내지 않는다(위 docstring).
                    image="",
                    released_at=released,
                    is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                    url=url,
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

            fresh = [d for d, _, _ in rows if d]
            if fresh and max(fresh) < floor:
                break
            if len(rows) < PAGE_SIZE:
                break
    return items
