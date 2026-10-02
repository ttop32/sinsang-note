"""삼양식품 — 보도자료 '제품뉴스' 탭에서 신제품과 출시일을 뽑는다.

오뚜기·오리온·샘표·해태제과식품과 같은 계보다(보도자료 제목 → 상품명).
조인 규칙은 `collectors/maker_orion.py` 것을 그대로 가져왔다.
오뚜기·팔도 다음으로 라면 축을 메우는 세 번째 제조사다(농심·CJ 는 robots 전면차단).

**1차 조사가 "불가"로 접었던 브랜드다.** `/kor/brand/list.do`(제품 카탈로그)가
JS 렌더인 건 **지금도 맞다** — 108KB 원본에 한글 텍스트가 내비·페이저뿐이다.
그런데 **보도자료 경로는 완전히 다르다.** 1차는 이 경로를 열지 않았다.
("카탈로그가 JS 다" ≠ "보도자료도 JS 다". notes/CANDIDATES-MAKER.md §①)

수집 경로. 2026-10-02 실측:
  GET https://www.samyangfoods.com/kor/publicity/press/list.do
      ?searchCateCd=035002&pageIndex=1&pageUnit=30          200 / 124,245B
    <tr>
      <td class="num">244</td>
      <td class="">제품뉴스</td>
      <td class="subject">
        <a href="#" onclick="javascript:fnView('./view.do', 1361); return false;">
          삼양식품, 추석 맞아 ‘삼양1963 X 짜르르 우지 선물세트’ 한정 출시…</a></td>
      <td>2026.08.31</td>
    </tr>
  **완전 SSR.** 선택자: `tr` 중 `td.subject` 가 있는 것 → `td.subject a`(제목),
  마지막 `td`(날짜), `onclick` 의 숫자(seq).

  파라미터(목록 하단 `<form id="searchForm" method="get">` 의 hidden 에서 읽었다):
    `searchCateCd` 035001 기업뉴스 / **035002 제품뉴스(244건)** / 035003 ESG뉴스
    `pageIndex`   1부터
    `pageUnit`    기본 12. **`pageUnit=30` 을 GET 으로 넣으면 실제로 30행이 온다**
                  (실측 확인). 한 번에 30건이라 1페이지면 10개월을 덮는다.

⚠️ **'제품뉴스' ≠ '출시'.** 244건 카테고리지만 최근 30건 중 실제 신제품 출시는
   5건 안팎이다. 나머지는 수상(레드닷·iF·미각상), 팝업/백일잔치, 캠페인 조회수,
   브랜드 론칭, 캐릭터 플랫폼(삼양애니·페포) 오픈, 트레일런 대회다.
   계보의 `_SKIP`/`_TAIL` 이 대부분 걷어내고, 아래 두 개를 더 보탰다.

⚠️ **해외 전용 신제품이 섞인다.** `삼양식품, 日 신제품 '불닭카레' 2종 출시`
   (2026-03-23)는 일본 전용이다. 국내 편의점 화면에 올리면 거짓이 된다.
   `日`·`美`·`글로벌`·`수출`·`해외` 역필터가 **필수**다(실측으로 이 1건이 걸린다).

⚠️ **없는 `seq` 도 200 에 껍데기를 준다.** `view.do?seq=1399` 가
   **200 / 108,494B** 인데 본문·제목·날짜가 전부 없다. 동서식품과 같은 함정이다.
   → **상태코드로 검증하지 마라.** 어차피 이 어댑터는 상세를 열지 않는다(아래).

⚠️ **사진이 없다.** 목록은 썸네일 없는 게시판 테이블이고, 상세
   (`view.do?seq=1349`, **425,011B**)는 본문 사진이 전부
   `data:image/png;base64,…` 인라인이라 **주소가 없다**(`/cmm/`·`FileDown` 류
   링크 0건). 건당 425KB 를 받아도 건질 게 없다.
   → **상세를 열지 않고 Item.image 를 비운다.** 지어내지 않는다.
   (크라운처럼 `data:` 를 담으면 products.json 이 터진다. `base.derive()` 는
    `http://` 만 거르지 `data:` 는 통과시킨다.)

**새로 보탠 조인 규칙 1개** — **브랜드 론칭을 상품으로 읽지 않는다.**
    삼양식품, 대사 전문 헬스케어 브랜드 ‘스핀들’ 론칭        ← 상품이 아니다
    삼양식품 탱글 브랜드 신제품 ‘바질토마토 프로틴파스타’ 출시 ← 상품이다
  둘 다 따옴표 **앞**에 '브랜드' 가 있어서 위치로는 못 가른다. **동사로 갈린다** —
  `론칭/런칭` + '브랜드' 면 브랜드 출범이고, `출시` 면 제품이다. `_pick` 참고.

**일괄 등록 흔적 — 없다.** 제품뉴스 30건의 날짜에 중복이 0건이다
(2025-11-03 ~ 2026-08-31). 동서식품 `regDt` 같은 묶음이 아니다.

**조인 결과: 1페이지 30건(2025-11-03 ~ 2026-08-31) 중 최근 300일에서 3건.**
전수로 훑은 버린 쪽 —
  수상 3건 · 캐릭터 플랫폼/스토어 2건 · 팝업·백일잔치 3건 · 캠페인/조회수 4건 ·
  대회·서포트럭 2건 · 할인 프로모션 1건 · 해외전용 1건 ·
  `‘삼양1963 X 짜르르 우지 선물세트’ 한정 출시`(선물세트) 1건 ·
  따옴표 없는 진짜 신제품 1건(`불닭납작당면 2인분 파우치 형태 출시`,
  **아는 손실**. 상품명을 특정할 수 없어 버린다).

robots: `https://www.samyangfoods.com/robots.txt` → **허용. 200, 89바이트.**
```
User-agent: *
Allow: /

# Sitemap files
Sitemap: http://www.samyangfood.co.kr/sitemap.xml
```
        이번 제조사 조사 중 **가장 깨끗한 robots** 다.
        ⚠️ 선언된 사이트맵은 **존재하지 않는다** — `samyangfoods.com/sitemap.xml`
        과 `samyangfood.co.kr/sitemap.xml` 둘 다 404 + 209바이트 Apache 기본
        404 다. 사이트맵으로 목록을 얻을 생각은 버려라.
약관:   확인하지 않았다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "삼양식품"
SITE = "https://www.samyangfoods.com"
LIST = SITE + "/kor/publicity/press/list.do"
VIEW = SITE + "/kor/publicity/press/view.do"
CATE = "035002"      # 제품뉴스. 035001=기업뉴스 / 035003=ESG뉴스
PAGE_UNIT = 30       # GET 으로 먹는다(실측). 1페이지가 10개월치다.
MAX_PAGES = 2        # 폭주 방지 상한.
DAYS = 300
DELAY = 2.2

# --- 제목 → 상품명 (maker_orion 과 같은 규칙 + 삼양 함정 보강) ----------------
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭|런칭)")
_LAUNCH_ONLY = re.compile(r"(론칭|런칭)")   # 브랜드 출범에 쓰이는 동사
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
         # 삼양 실측 추가분. 캐릭터 플랫폼(페포)·행사·광고 축이다.
         "오픈", "이벤트", "광고", "조회수", "첫선", "첫 공개", "잔치", "할인",
         # 국내 출시가 아닌 건 화면에 올리면 거짓이 된다. '日 신제품 불닭카레'.
         "日", "美", "글로벌", "수출", "해외")
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱")
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")
_REPACK_HEAD = ("에디션", "라벨")
_REPACK_MID = ("테마", "에디션", "라벨", "컬래버", "콜라보")
_REPACK_NAME = ("에디션", "컬렉션", "한정판", "선물세트", "기획세트", "기획팩")


def _pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열."""
    t = " ".join(title.split())
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
    # 삼양 보강 — '브랜드 ‘X’ 론칭' 은 브랜드 출범이지 상품 출시가 아니다.
    # '브랜드 신제품 ‘X’ 출시' 는 상품이라 **동사로** 가른다(위 docstring).
    if _LAUNCH_ONLY.match(verb.group(1)) and "브랜드" in head:
        return ""
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
    """'2026.08.31' → '2026-08-31'. 월·일 범위를 검증한다."""
    m = re.match(r"^\s*(20\d{2})[-.](\d{1,2})[-.](\d{1,2})\s*$", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _rows(html: str) -> list[tuple]:
    """목록 HTML → (날짜, 제목, seq) 목록."""
    out = []
    for tr in HTMLParser(html).css("tr"):
        subj = tr.css_first("td.subject")
        if not subj:
            continue
        a = subj.css_first("a")
        tds = tr.css("td")
        if not a or len(tds) < 2:
            continue
        m = re.search(r"fnView\(\s*'[^']*'\s*,\s*(\d+)\s*\)",
                      a.attributes.get("onclick") or "")
        out.append((_date(tds[-1].text(strip=True)),
                    " ".join(a.text().split()),
                    m.group(1) if m else ""))
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"searchCateCd": CATE,
                                                       "pageIndex": page,
                                                       "pageUnit": PAGE_UNIT}))
            r.raise_for_status()
            rows = _rows(r.text)

            # 셀렉터가 바뀌면 조용히 0건이 되는 게 제일 나쁘다. 제품뉴스만
            # 244건짜리 게시판이라 1페이지는 반드시 와야 한다.
            if page == 1 and not rows:
                raise ValueError(
                    f"삼양식품 제품뉴스 1페이지가 비었다. {r.url} → "
                    f"{len(r.content)}B — 목록 셀렉터(tr / td.subject a / 마지막 td)"
                    f"가 바뀌었는지 확인하라")
            if not rows:
                break

            for released, title, seq in rows:
                if released and released < floor:
                    continue
                name = _pick(title)
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    # 기사 제목이 그대로 설명이 된다. 앞의 회사명만 턴다.
                    desc=re.sub(r"^\s*삼양식품[^,]{0,10},\s*", "", title),
                    # 사진이 없다. 상세 본문 사진이 전부 인라인 base64 다
                    # (위 docstring). 지어내지 않는다.
                    image="",
                    released_at=released,
                    is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                    url=f"{VIEW}?seq={seq}" if seq else LIST,
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

            fresh = [d for d, _, _ in rows if d]
            if fresh and max(fresh) < floor:
                break
            if len(rows) < PAGE_UNIT:
                break
    return items
