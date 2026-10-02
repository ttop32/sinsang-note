"""동원F&B — 뉴스 목록에서 신제품과 출시일을 뽑는다.

오뚜기·오리온·샘표·삼양식품과 같은 계보다(보도자료 제목 → 상품명).
조인 규칙은 `collectors/maker_orion.py` 것을 그대로 가져왔다.
아워홈·풀무원과 함께 냉동·간편식 축을 메운다.

1차 조사가 남긴 "상세에 날짜 **확인 못 함**" 을 3차가 해소했다 — **상세가 아니라
목록이 날짜를 준다.** 그리고 1차가 쓴 URL `…/News/` 는 지금 404 다.
정확한 경로는 `/services/Customer/News/News_List` 다.
(notes/CANDIDATES-MAKER.md §⑦)

수집 경로. 2026-10-02 실측:
  GET https://www.dongwonfnb.com/services/Customer/News/News_List   200 / 65,967B
    <ul class="newsList">
     <li class="item"><div class="newsItem event">
       <div class="articleLabel ico2 news">보도자료</div>          ← 분류를 서버가 준다
       <div class="newsImg"><a href="/services/Customer/News/News_View?contentno=1376">
         <img src="/upload/2026/08/19/08/24/1787095456451/3dbc….jpg"></a></div>
       <dl class="newsArticle">
         <dt class="newsTit"><h3><a href="…contentno=1376">
             동원F&B, 바삭한 식감 극대화한 냉동 치킨 ‘케바삭’ 출시</a></h3></dt>
         <dd class="newsCont">…요약…</dd></dl>
       <div class="newsInfo"><span class="date">2026-08-19</span>
                             <span class="readNum">38</span></div>

**⚠️ 목록 제목은 40자쯤에서 잘린다.** 오리온과 같은 함정이다. 실측:
    '동원F&B, 과일 퓨레·식이섬유 더한 '덴마크 과일담은 가공유’ ...'   ← '출시' 가 잘렸다
    '동원F&B, 모델 방탄소년단 진과 함께한 두 번째 ‘동원참치’ 광...'   ← '광고' 가 잘렸다
동사가 잘려 나가면 신제품인지 광고인지 가를 수가 없다. 그래서 **상세를 한 번씩
받아 `.boardTit` 의 온전한 제목**을 쓴다. 날짜는 목록 것을 그대로 쓴다
(상세 `.date` 와 8건 전부 일치).
  GET …/News_View?contentno=1379   200 / 57,278B
    <div class="boardColH"><span class="event">보도자료</span></div>
    <span class="boardTit">동원F&B, 과일 퓨레·식이섬유 더한 '덴마크 과일담은 가공유’ 출시</span>
    <span class="boardInfo"><span class="date">2026-09-16</span></span>
  ⚠️ 제목의 따옴표가 짝이 안 맞는다 — 여는 건 ASCII `'`, 닫는 건 `’` 다.
     `_SINGLE` 이 양쪽 집합을 다 받게 돼 있어 그대로 동작한다. 좁히지 마라.

**⚠️ 1페이지 8건만 받을 수 있다.** SSR 목록에 페이지 링크가 하나도 없다
(`News_List` 로 가는 `<a>` 가 내비 자기 자신뿐). 더 보기는 Ajax 다.
증분 수집에는 충분하지만 **과거 이력(649건)은 못 가져온다.** 1페이지 8건이
2026-08-05 ~ 09-30 = 약 2개월치라 신상 창(60일)과 거의 같다.

**⚠️ 섞이는 것 — 전부 걸러야 한다.**
  펫푸드    `반려견용 기능성 사료 ‘뉴트리플랜 데일리뮨’ 출시` ← 사람이 먹는 게 아니다
  건강기능식품 `추석 맞이 건강기능식품 프로모션 진행` (GNC·천지인)
  선물세트  `‘2026 추석 선물세트’ 출시`
  광고      `모델 방탄소년단 진과 함께한 두 번째 ‘동원참치’ 광고…`
  공법 도입 `40주년 양반김, ‘질소충전공법(Fresh-Lock)’ 도입하며…` ← 상품이 아니다
1페이지 8건 중 실제로 남는 건 `케바삭`(냉동 치킨)·`덴마크 과일담은 가공유` 꼴이다.
`‘리얼 관자 크랩스’·‘어!델리’` 같은 2종 동시 출시 건은 상품을 하나로 특정할 수
없어 버린다(**아는 손실**. 오리온·삼양과 같은 규칙).

**일괄 등록 흔적 — 없다.** 8건의 날짜가 전부 다르다
(09-30 · 09-18 · 09-16 · 08-20 · 08-19 · 08-13 · 08-11 · 08-05).

robots: https://www.dongwonfnb.com/robots.txt → `*` 그룹이 `/services/Customer/News/`
        를 **명시 허용**한다. 이번 제조사 조사 중 가장 잘 쓰인 robots 다.
        `Disallow: /*Ajax*` · `/*ajax*` · `/*_json*` · `/*Json*` · `/*Proc*` 가 걸려
        있어 '더 보기' 경로는 원래부터 금지였다(그래서 1페이지만 받는 게 자연스럽다).
🔴 1차 기록 정정 — **뉴스 이미지는 금지 경로가 아니다.**
        실제 이미지 `/upload/…`, robots 금지 경로 `/uploadFile/`·`/uploadFile2/`.
        **다른 경로다.** 오리온 `/upload/` 금지 사례와 혼동하지 마라 — 동원은 반대다.
약관:   확인하지 않았다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "동원F&B"
SITE = "https://www.dongwonfnb.com"
LIST = SITE + "/services/Customer/News/News_List"
DAYS = 300
DELAY = 2.2

LABEL = "보도자료"      # 공지는 안 쓴다

# --- 제목 → 상품명 (maker_orion 과 같은 규칙 + 동원 함정 보강) ---------------
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭|런칭)")
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
_MULTI = re.compile(r"\d+\s*종")
_TRAIL_SEP = re.compile(r"^\s*[·∙,、/]")

_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "협약", "체결", "주주총회", "후원", "기부", "추모", "공모", "발대식",
         "심포지엄", "박람회", "팝업", "캠페인", "발탁", "앰배서더", "재단",
         "경연", "시상", "간담회", "개최", "스폰서", "리뉴얼", "실적",
         "매진", "진행", "참가", "참여", "전개", "지원", "프로젝트",
         "오픈", "이벤트", "광고", "조회수", "할인", "프로모션", "도입",
         # 동원 실측 추가분. 펫푸드와 건강기능식품이 같은 게시판에 섞여 온다.
         # ⚠️ '펫' 한 글자는 넣지 않는다 — 두 글자 미만 토큰은 상품명을 문다.
         "반려견", "반려묘", "반려동물", "뉴트리플랜", "펫푸드",
         "건강기능식품", "건기식",
         # 국내 출시가 아닌 건 화면에 올리면 거짓이 된다.
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
    quoted = None
    for m in _SINGLE.finditer(head):
        quoted = m
    if not quoted or any(w in head[quoted.end():] for w in _BETWEEN):
        return ""
    if _TRAIL_SEP.match(head[quoted.end():]):
        return ""
    name = quoted.group(1).strip(" ,·∙")
    if len(name) < 2 or any(c in name for c in "·∙&?!"):
        return ""
    if any(w in name for w in _REPACK_NAME):
        return ""
    return name


def _date(s: str) -> str:
    """'2026-09-16' → '2026-09-16'. 월·일 범위를 검증한다."""
    m = re.match(r"^\s*(20\d{2})[-.](\d{1,2})[-.](\d{1,2})\s*$", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _rows(html: str) -> list[tuple]:
    """목록 HTML → (날짜, 분류, href, 이미지) 목록. 제목은 잘려 있어 안 쓴다."""
    out = []
    for li in HTMLParser(html).css(".newsList li.item"):
        a = li.css_first(".newsTit h3 a")
        if not a:
            continue
        lab = li.css_first(".articleLabel")
        dt = li.css_first(".newsInfo .date")
        img = li.css_first(".newsImg img")
        src = (img.attributes.get("src") or "").strip() if img else ""
        out.append((_date(dt.text(strip=True) if dt else ""),
                    lab.text(strip=True) if lab else "",
                    (a.attributes.get("href") or "").strip(),
                    SITE + src if src.startswith("/") else src))
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST))
        r.raise_for_status()
        rows = _rows(r.text)

        # 셀렉터가 바뀌면 조용히 0건이 되는 게 제일 나쁘다. 649건짜리 게시판이라
        # 1페이지는 반드시 와야 한다.
        if not rows:
            raise ValueError(
                f"동원F&B 뉴스 목록이 비었다. {r.url} → {len(r.content)}B — "
                f"목록 셀렉터(.newsList li.item / .newsTit h3 a / "
                f".newsInfo .date)가 바뀌었는지 확인하라")

        for released, label, href, img in rows:
            if label and label != LABEL:
                continue
            if released and released < floor:
                continue
            # 목록 제목은 40자쯤에서 잘려 동사가 사라진다. 상세에서 온전한 제목을 받는다.
            time.sleep(DELAY)
            d = base.retry(lambda: c.get(SITE + href if href.startswith("/") else href))
            d.raise_for_status()
            node = HTMLParser(d.text).css_first(".boardTit")
            title = " ".join(node.text().split()) if node else ""
            name = _pick(title)
            if not name:
                continue
            it = Item(
                brand=BRAND,
                name=name,
                desc=re.sub(r"^\s*동원F&B,\s*", "", title),
                image=img,
                released_at=released,
                is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                url=SITE + href if href.startswith("/") else (href or LIST),
            )
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)
    return items
