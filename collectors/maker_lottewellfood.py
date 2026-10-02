"""롯데웰푸드 — 보도자료에서 신제품을 뽑는다. 날짜는 대부분 못 믿는다.

목록(/prcenter/news)이 SSR 이라 상세를 안 받아도 된다. 2026-09-30 실측:
    <a href="/prcenter/news/2133?page=1&searchType2=Y">
      <div class="img"><img src=" https://webimage.ldcc.co.kr/upload/…png" alt="…"></div>
      <div class="list-txt"><div class="fnt-title-s2"><span>제목</span></div>
                            <em>2026-09-21</em></div>
    </a>
제목이 잘리지 않고 통째로 들어 있다. img src 앞에 공백이 하나 붙어 있어 strip 한다.

⚠️⚠️ **`<em>` 날짜는 출시일이 아니다. 등록일이다 — 그것도 일괄 등록이다.**
notes/CANDIDATES-DIRECT.md 는 이 날짜를 출시일로 보고 이 브랜드를 추천했는데,
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

🔴 **2026-10-02 — 등록했다. 아래 '제외' 서술은 뒤집혔다.**
`base.BRANDS`·`base.SITES`·`collect.ADAPTERS` 세 곳에 전부 올렸다. 전에
`notes/QA-REPORT.md` §2-9 가 "robots 404+HTML · noindex · 일괄 등록 날짜 세 가지로
제외가 타당하다" 고 적었는데, 그중 둘이 해소됐다:
  · **robots·약관 — 운영자가 "robots.txt·이용약관 제약은 무시한다" 고 승인했다**
    (2026-10-02 과자·음료 제조사 라운드. 대신 UA 는 위장하지 않는다 —
     `base.UA` 로 신원을 밝히고, 삭제 요청이 오면 다투지 말고 즉시 내린다.
     base.BRANDS 의 이마트24·도미노피자·폴바셋·동서식품·샘표와 같은 칸이다).
  · **일괄 등록 날짜 — 아래 `BULK` 규칙이 이미 처리하고 있다.** 같은 날짜가
    `BULK` 건 이상이면 그 날짜를 `uploaded_at` 에만 넣고 `released_at` 은 비운다.
    2026-10-02 실측에서 수집 4건이 **전부** `released_at` 이 빈 채로 나왔다 —
    규칙이 설계대로 돌고 있다는 뜻이다.
  · 남은 하나(`<meta name="robots" content="noindex, nofollow">`)는 **색인 거부지
    크롤 금지가 아니다.** 그래서 막지 않는다.
⚠️ 세부분류는 `(MAKER, "과자")` 로 등록했다. 롯데웰푸드는 과자·빙과·육가공·
   간편식을 다 하는 종합사라 **한 칸으로는 어디를 골라도 일부가 어긋난다**
   (실측: 4건 중 `일월정 흑마늘 삼계탕`·`파스퇴르 그릭` 2건이 과자가 아니다).
   주력(빼빼로·몽쉘·가나)을 따라 '과자' 로 두었다. 정석은 `taxonomy.VENDOR_SUBS`
   로 **상품별 분류**를 쓰는 것인데(hy프레딧 선례), **이 사이트는 보도자료만
   주고 상품별 분류를 안 준다** — 그래서 지금은 못 쓴다.

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

# 기존 제품의 테마/에디션 패키지 기사. 상품이 새 게 아니고 따옴표 안도 상품명이 아니다.
# 실측: 롯데웰푸드, 디즈니코리아와 함께 ‘토이 스토리 5’ 테마 ‘가나 초콜릿’ 제품 출시
#       — ‘가나 초콜릿’은 1975년부터 팔던 대표 제품이다. 신제품이 아니라 테마 패키지다.
# ⚠️ _BETWEEN 검사를 head 전체로 넓히는 식으로는 못 고친다. 협업으로 '만든' 신제품까지
#    같이 죽는다 — GS25 채택분 '사워레몬요거트'·'초BIG!무쿠점보멜론구미' 2건으로 실증됐다
#    (notes/QA-REPORT.md §2-6). '협업'이라는 단어가 아니라 **위치**가 그 구분이다.
_REPACK_HEAD = ("에디션", "라벨")                              # “…” 헤드라인 안
_REPACK_MID = ("테마", "에디션", "라벨", "컬래버", "콜라보")      # 따옴표와 따옴표 사이


def _pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열.

    이 브랜드 제목은 앞머리가 “…” 홍보 문구다. 그걸 안 빼면 홍보 문구가 상품명으로
    잡힌다(“시집이 캔디가 된다면?”). 또 '젤리 2종 선봬'처럼 상품이 여럿인 기사도
    버린다 — 상품명을 '젤리 2종'으로 쓸 수는 없다.
    """
    t = " ".join(title.split())
    # “…” 홍보 헤드라인 안에 에디션/라벨이 있으면 기존 제품의 패키지 기사다.
    if any(w in m.group(1) for m in _HEAD.finditer(t) for w in _REPACK_HEAD):
        return ""
    body = _HEAD.sub(" ", t)
    if any(w in body for w in _SKIP) or _MULTI.search(body):
        return ""
    # ‘A’ 테마 ‘B’ 꼴 — 마지막 두 따옴표 사이가 테마/에디션이면 B 는 기존 제품이다.
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
            # 셀렉터가 바뀌면 조용히 0건이 되는 게 제일 나쁘다. 1페이지는 반드시
            # 기사가 와야 한다(수백 건짜리 보도자료 게시판이다).
            # 2026-10-02 검수 지적 — 이 어댑터만 이 가드가 없어서, `_ROW` 정규식을
            # 깨뜨리면(= 사이트 URL 체계 변경) 예외 없이 0건을 돌려줬다.
            if page == 1 and not page_rows:
                raise ValueError(
                    f"롯데웰푸드 보도자료 1페이지가 비었다. {r.url} → "
                    f"{len(r.content)}B — 목록 셀렉터(a[href^=/prcenter/news/] / "
                    f".fnt-title-s2 / em)가 바뀌었는지 확인하라")
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
