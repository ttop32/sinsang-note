"""롯데웰푸드 — 보도자료에서 신제품을 뽑는다. 날짜는 대부분 못 믿는다.

목록(/prcenter/news)이 SSR 이라 상세를 안 받아도 된다. 2026-09-30 실측:
    <a href="/prcenter/news/2133?page=1&searchType2=Y">
      <div class="img"><img src=" https://webimage.ldcc.co.kr/upload/…png" alt="…"></div>
      <div class="list-txt"><div class="fnt-title-s2"><span>제목</span></div>
                            <em>2026-09-21</em></div>
    </a>
제목이 잘리지 않고 통째로 들어 있다. img src 앞에 공백이 하나 붙어 있어 strip 한다.

⚠️⚠️ **`<em>` 날짜는 출시일이 아니다. 등록일이다 — 그것도 일괄 등록이다.**
docs/CANDIDATES-DIRECT.md 는 이 날짜를 출시일로 보고 이 브랜드를 추천했는데,
54건을 실제로 받아 보니 서로 다른 날짜가 7개뿐이었다:
    2026-04-21 ×14 · 2026-06-15 ×9 · 2026-06-05 ×9 · 2026-07-27 ×7 · 2026-03-13 ×6 …
기사 내용과 대조하면 날짜가 **뒤로 밀려 있다**:
    '설 연휴' 졸음운전 캠페인 → 2026-03-13 (설은 2월 중순)
    '화이트데이 겨냥' 말랑카우 초코볼젤리 → 2026-04-21 (화이트데이는 3월 14일)
    '초복 앞두고' 일월정 흑마늘 삼계탕 → 2026-09-04 (초복은 7월)
한두 달씩 늦다. 이걸 released_at 에 넣으면 두 달 전 상품이 오늘 나온 신상으로
찍힌다. mega.py 가 이미지 일괄 재업로드 타임스탬프를 released_at 에 안 넣은 것과
같은 이유다.

그래서 **같은 날짜가 BULK 건 이상 몰리면 그 날짜는 uploaded_at 으로만 쓰고
released_at 은 비운다.** 날짜가 그날 하나뿐이면(가장 최신 글이 그렇다 — 2133 은
2026-09-21 단독) 개별 등록으로 보고 released_at 에 넣는다. 사이트가 앞으로
건건이 올리면 자동으로 채워지고, 또 일괄 등록하면 자동으로 비워진다.

robots: https://www.lottewellfood.com/robots.txt → **404 + text/html, 본문 36KB,
        첫 글자 '<'**. robots 가 아니라 홈페이지 HTML 이다. 규칙을 알 수 없다 —
        허용도 금지도 아니다. 그래서 요청 간격을 다른 곳보다 넓게(DELAY) 잡는다.
⚠️ 그리고 페이지에 `<meta name="robots" content="noindex, nofollow">` 가 붙어 있다.
   색인 거부지 크롤 금지는 아니지만, robots.txt 를 못 읽는 상태와 겹친다.
약관: /policy/use — 푸터 링크가 주석 처리돼 숨어 있다. "회원은 서비스를 이용하여
      얻은 정보를 사전승낙 없이 복사, 복제…할 수 없다"(회원 대상 조항).
      CRAWLING-POLICY.md §6-4 '약관이 금지' 칸에 해당한다. **운영자 판단이 필요하다.**
"""
import re
import time
from collections import Counter
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "롯데웰푸드"
SITE = "https://www.lottewellfood.com"
LIST = SITE + "/prcenter/news"
MAX_PAGES = 6        # 한 페이지 9건. 신제품 기사 비율이 낮아 조금 깊게 본다.
DAYS = 300
DELAY = 3.0          # robots 를 못 읽는 곳이라 간격을 넓게 잡는다
BULK = 4             # 같은 날짜가 이만큼 몰리면 일괄 등록으로 본다

_ROW = re.compile(r"^/prcenter/news/\d+")

# --- 제목 → 상품명 (maker_ottogi 와 같은 규칙) --------------------------------
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭)")
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
_MULTI = re.compile(r"\d+\s*종")
_TRAIL_SEP = re.compile(r"^\s*[·∙,、/]")

_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "협약", "체결", "주주총회", "후원", "기부", "추모", "공모", "발대식",
         "심포지엄", "박람회", "팝업", "캠페인", "발탁", "앰배서더", "재단",
         "경연", "시상", "간담회", "개최", "스폰서", "리뉴얼", "실적",
         "매진", "진행", "참가", "참여", "전개", "지원")
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱")
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")


def _pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열.

    이 브랜드 제목은 앞머리가 “…” 홍보 문구다. 그걸 안 빼면 홍보 문구가 상품명으로
    잡힌다(“시집이 캔디가 된다면?”). 또 '젤리 2종 선봬'처럼 상품이 여럿인 기사도
    버린다 — 상품명을 '젤리 2종'으로 쓸 수는 없다.
    """
    t = " ".join(title.split())
    body = _HEAD.sub(" ", t)
    if any(w in body for w in _SKIP) or _MULTI.search(body):
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
    if len(name) < 2 or any(c in name for c in "·∙&?"):
        return ""
    return name


def _date(s: str) -> str:
    """'2026-09-21' → '2026-09-21'. 월·일 범위를 검증한다."""
    m = re.search(r"(20\d{2})[-.](\d{1,2})[-.](\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _rows(html: str) -> list:
    out = []
    for a in HTMLParser(html).css("a"):
        href = a.attributes.get("href", "")
        if not _ROW.match(href):
            continue
        title = a.css_first(".list-txt span")
        day = a.css_first("em")
        img = a.css_first(".img img")
        out.append({
            "url": SITE + href.split("?")[0],
            "date": _date(day.text()) if day else "",
            "title": " ".join(title.text().split()) if title else "",
            "image": (img.attributes.get("src", "") if img else "").strip(),
        })
    return out


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    rows, stop = [], False
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"page": page}))
            r.raise_for_status()
            page_rows = _rows(r.text)
            if not page_rows:
                break
            for row in page_rows:
                if row["date"] and row["date"] < floor:
                    stop = True
                    continue
                rows.append(row)
            if stop:
                break

    # 같은 날짜에 몰린 글은 일괄 등록이다. 그 날짜는 출시일로 쓰지 않는다.
    bulk = {d for d, n in Counter(r["date"] for r in rows).items() if d and n >= BULK}

    items: list[Item] = []
    seen = set()
    for row in rows:
        name = _pick(row["title"])
        if not name:
            continue
        solo = row["date"] and row["date"] not in bulk
        it = Item(
            brand=BRAND,
            name=name,
            desc=re.sub(r"^\s*롯데웰푸드[^,]*,\s*", "", row["title"]),
            image=row["image"],
            uploaded_at=row["date"],
            released_at=row["date"] if solo else "",
            is_new=True,     # 브랜드가 '출시'라고 낸 기사다
            url=row["url"],
        )
        if it.key not in seen:
            seen.add(it.key)
            items.append(it)
    return items
