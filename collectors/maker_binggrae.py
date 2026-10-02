"""빙그레 — 보도자료에서 신제품과 출시일을 뽑는다.

오뚜기·오리온·샘표·해태제과식품과 같은 계보다(보도자료 제목 → 상품명).
조인 규칙은 `collectors/maker_orion.py` 것을 그대로 가져왔다.

**뉴스룸 메뉴가 넷인데 쓸 수 있는 건 하나다.** 1차 조사가 여기서 틀렸다 —
`/news/news_new` 를 보고 "신제품이 없다" 고 접었는데 그건 **공지**다.

    /news/news_home · /news/news_new   새소식      ← 공지. 쓸 수 없다
    /news/news_announced               보도자료    ← ✅ 여기가 진짜다 (358건)
    /news/news_story                   빙그레 스토리
    /news/media_font                   미디어 라이브러리

수집 경로. 2026-10-02 실측:
  GET https://www.bing.co.kr/news/news_announced?page=N   200 / 40,537B
    <li class="td_line">
      <div class="num font_poppin">354</div>
      <div class="tit"><a href="/news/news_announced_view?anno_idx=359">
          빙그레, 식후 관리 습관 돕는 '식후관리 워터' 출시</a></div>
      <div class="date font_poppin">2026-08-27</div>
    </li>
  선택자 `li.td_line` → `.tit a`(제목·링크) · `.date`(날짜).
  페이지당 10건, `?page=N` 이 GET 으로 먹는다(2·3페이지 실측 확인).
  **인라인 base64 가 없다** — 크라운(10.8MB)과 정반대로 페이지당 40KB 다.

**사진은 목록에 없고 상세에만 있다.** 그래서 **조인을 통과한 건만** 상세를 연다.
  GET /news/news_announced_view?anno_idx=359   200 / 33,289B
    <img src="/upload/ckeditor/2026/08/cb7d09b5-0d1e-42f1-806b-8893390b691d">
  확장자가 없는 UUID 경로다. `/upload/` 는 robots 금지 경로가 아니다(아래).
  300일 창에서 상세를 여는 건 4건뿐이라 총 130KB 쯤 든다.

⚠️ **이 브랜드의 약점은 출시 밀도다.** 3페이지 30건(2026-03-25 ~ 2026-09-29)에서
   조인을 통과하는 게 **4건**이다. 나머지는 후원·협약·박람회·그림잔치·바둑대회·
   그란폰도·수상·해외 박람회다. 빙그레는 사회공헌·스포츠 후원 보도가 유난히 많은
   회사라 **역필터 비중이 다른 곳보다 크다.**

⚠️ **'출시' 가 붙었는데 식품이 아닌 게 있다.**
     빙그레, 바나나맛우유-이도온화 한정판 도자기 식기세트 출시   (2026-04-29)
   계보의 `_pick` 이 **따옴표가 없어서** 이미 버리지만, 여기 적어 둔다 —
   '출시' 키워드만으로는 못 거르는 자리다. `base.is_nonfood()` 도 '식기세트' 를
   모른다(확인함). 앞으로 따옴표가 붙어 나오면 이 줄을 근거로 막아야 한다.

⚠️ **건강기능식품 브랜드가 섞인다.** `프롬뉴트리`(효소·식이섬유 스틱)가
   보도자료에 '출시' 로 뜬다 — 실측 1건(2026-06-05, `프롬뉴트리 효소와 식이섬유
   플러스 알파CD`). 편의점 식품 축이 아니라 `_NOT_OUR_LINE` 으로 막는다.
   풀무원헬스케어·동원 GNC 와 같은 성격 문제다(notes/CANDIDATES-MAKER.md §판단 ⑤).

**제품 카탈로그는 쓸 게 없다.** `/product/list?type=1` 은 원본 HTML 에 상품명이
하나도 없고(62,298B), 브라우저로 렌더해도 나오는 건 `메로나 투게더 붕어싸만코…`
= **SKU 가 아니라 브랜드 단위**다. 신상 축이 애초에 없다. 데이터 출처인
`POST /product/getProductList` 는 본문 스키마를 못 맞췄다(400). 어차피 값이 없어
열지 않았다.

**일괄 등록 흔적 — 없다.** 30건의 `.date` 에 중복 날짜가 1쌍뿐이다
(2026-05-22 ×2). 일화 `<li class="time">` 같은 묶음이 아니다.

robots: `https://www.bing.co.kr/robots.txt` → **허용. 200, 101바이트.**
```
User-agent: *
Disallow: /admin
Disallow: /api
Allow: /
Sitemap:https://www.bing.co.kr/sitemap.xml
```
        `Allow: /` 가 `Disallow` **뒤**에 있어 정상 동작한다. 우리가 쓰는
        `/news/news_announced`·`/news/news_announced_view`·`/upload/` 는 어느
        규칙에도 안 걸린다. (제품 데이터 출처 `POST /product/getProductList` 는
        `/api/` 아래가 아니라 `Disallow: /api` 에도 안 걸린다 — 안 쓸 뿐이다.)
약관:   확인하지 않았다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "빙그레"
SITE = "https://www.bing.co.kr"
LIST = SITE + "/news/news_announced"
VIEW = SITE + "/news/news_announced_view"
PAGE_SIZE = 10
MAX_PAGES = 4        # 폭주 방지 상한. 40건이면 1년치다.
DAYS = 300
DELAY = 2.2

# 편의점 식품 축이 아닌 계열 브랜드. 주어(브랜드명)로 거르는 게 키워드보다 정확하다.
_NOT_OUR_LINE = ("프롬뉴트리",)   # 건강기능식품

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
         # 빙그레 실측 추가분. 후원·전시·펀딩 기사 축이다.
         "특별전", "그림잔치", "대회", "봉사", "펀딩", "공식",
         # 국내 출시가 아닌 건 화면에 올리면 거짓이 된다.
         "日", "美", "글로벌", "수출", "해외", "현지")
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱")
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")
_REPACK_HEAD = ("에디션", "라벨")
_REPACK_MID = ("테마", "에디션", "라벨", "컬래버", "콜라보")
_REPACK_NAME = ("에디션", "컬렉션", "한정판", "선물세트", "식기세트", "기획팩")


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
    """'2026-08-27' → 그대로. 월·일 범위를 검증한다."""
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
    for li in HTMLParser(html).css("li.td_line"):
        a = li.css_first(".tit a")
        d = li.css_first(".date")
        href = a.attributes.get("href", "") if a else ""
        if not a or "anno_idx=" not in href:
            continue
        out.append((_date(d.text(strip=True)) if d else "",
                    " ".join(a.text().split()),
                    SITE + href))
    return out


def _image(html: str) -> str:
    """상세 본문의 보도사진. `/upload/ckeditor/…` 하나뿐이다(확장자 없는 UUID)."""
    for img in HTMLParser(html).css("img"):
        src = (img.attributes.get("src") or "").strip()
        if src.startswith("/upload/"):
            return SITE + src
        if src.startswith("https://") and "/upload/" in src:
            return src
    return ""


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    cand: list[tuple] = []
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"page": page}))
            r.raise_for_status()
            rows = _rows(r.text)

            # 셀렉터가 바뀌면 조용히 0건이 되는 게 제일 나쁘다. 358건짜리
            # 게시판이라 1페이지는 반드시 와야 한다.
            if page == 1 and not rows:
                raise ValueError(
                    f"빙그레 보도자료 1페이지가 비었다. {r.url} → {len(r.content)}B, "
                    f"li.td_line {len(HTMLParser(r.text).css('li.td_line'))}개 — "
                    f"목록 셀렉터(li.td_line / .tit a / .date)가 바뀌었는지 확인하라")
            if not rows:
                break

            for released, title, url in rows:
                if released and released < floor:
                    continue
                name = _pick(title)
                if name:
                    cand.append((released, name, title, url))

            fresh = [d for d, _, _ in rows if d]
            if fresh and max(fresh) < floor:
                break
            if len(rows) < PAGE_SIZE:
                break

        items: list[Item] = []
        seen = set()
        for released, name, title, url in cand:
            time.sleep(DELAY)
            # 사진 한 장 때문에 상세를 연다. 실패해도 수집을 멈추지 않는다.
            try:
                d = base.retry(lambda: c.get(url))
                d.raise_for_status()
                image = _image(d.text)
            except Exception:
                image = ""
            it = Item(
                brand=BRAND,
                name=name,
                # 기사 제목이 그대로 설명이 된다. 앞의 회사명만 턴다.
                desc=re.sub(r"^\s*빙그레[^,]{0,10},\s*", "", title),
                image=image,
                released_at=released,
                is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                url=url,
            )
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)
    return items
