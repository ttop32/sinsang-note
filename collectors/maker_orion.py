"""오리온 — 보도자료에서 신제품과 출시일을 뽑는다.

목록(/board/list/87)은 SSR 이라 날짜·링크가 그대로 보인다. 2026-09-30 실측:
    <h8>“햇감자에 바르고!…” 오리온, '포카칩 황치즈맛' ...</h8>
    <span class="date">2026.09.03</span>  →  /board/view/87?boardno=1423
⚠️ 목록의 제목은 40자쯤에서 잘린다. 상품명이 따옴표째 잘려 나가는 경우가 실제로
있어서(‘포카칩·스 …’) 목록만으로는 상품명을 못 뽑는다. 그래서 상세를 한 번씩
받아 `.title h4` 의 온전한 제목을 쓴다. 날짜는 목록 것과 상세 것이 같아서(실측
22건 전부 일치) 목록 날짜를 그대로 쓰고, 상세는 제목과 이미지만 가져간다.
검색(keyname=subject)은 500 이 떨어져 못 쓴다.

요청을 줄이려고 목록 단계에서 두 번 거른다.
  ① DAYS 보다 오래된 건 상세를 받지 않는다.
  ② 잘린 제목에서도 확실히 보이는 회사 공시성 단어(채용·매출·영업이익…)는 거른다.
     보도자료 제목 앞머리는 “…” 홍보 문구라 이 단계에서 세게 거르면 진짜 신제품이
     같이 날아간다(“완판됐던 한정판…” ‘초코송이 말차’ 정식 출시). 그래서 여기선
     최소한만 거르고, 본판정은 온전한 제목을 받은 뒤에 한다.

날짜는 목록 22건이 전부 다른 날이었다. 일괄 재등록 흔적이 없어 그대로 믿는다.

robots: https://www.orionworld.com/robots.txt → 200, text/plain, 본문 첫 글자 'u'.
        `User-agent: *` 에 `Disallow: /thdadmin/`, `Disallow: /upload/` 둘뿐.
        목록·상세(/board/)는 허용이다.
⚠️ 제품 이미지가 `/upload/editor/` — 즉 금지 경로다. CRAWLING-POLICY.md §6-3 대로
   URL 은 Item.image 에 담되 어댑터는 그 URL 을 절대 요청하지 않는다(HEAD 도 금지).
   이미지 R2 미러링(이슈 #5) 때 이 브랜드는 대상에서 빼야 한다.
약관: /html/100 '법적고지' — "'정보'는 비상업적이고 개인적인 용도를 위해서만
      제한적으로 제공… 상업적이거나 공공의 목적…으로 다운로드" 금지.
      robots 는 허용인데 약관이 막는 경우다(CRAWLING-POLICY.md §6-4 이마트24와 같은 칸).
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "오리온"
SITE = "https://www.orionworld.com"
LIST = SITE + "/board/list/87"       # 보도자료 게시판
MAX_PAGES = 3        # 한 페이지 10건. 폭주 방지 상한.
DAYS = 300
DELAY = 2.2

# 잘린 제목에서도 판정이 뒤집히지 않는 것만 넣는다. 본판정은 _pick 이 한다.
_PRESCREEN = ("채용", "매출", "영업이익", "주주총회", "신입사원", "분기")

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
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열."""
    t = " ".join(title.split())
    body = _HEAD.sub(" ", t)          # “…” 는 홍보 헤드라인이다
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
    """'2026.09.03' → '2026-09-03'. 월·일 범위를 검증한다."""
    m = re.search(r"(20\d{2})[-.](\d{1,2})[-.](\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _rows(html: str) -> list:
    out = []
    for a in HTMLParser(html).css("li a"):
        t, d = a.css_first("h8"), a.css_first("span.date")
        href = a.attributes.get("href", "")
        if not (t and d and "boardno=" in href):
            continue
        out.append((_date(d.text()), href.split("&")[0], " ".join(t.text().split())))
    return out


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    cand, stop = [], False
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"page": page}))
            r.raise_for_status()
            rows = _rows(r.text)
            if not rows:
                break
            for released, href, short in rows:
                if released and released < floor:
                    stop = True
                    continue
                if any(w in short for w in _PRESCREEN):
                    continue
                cand.append((released, href))
            if stop:
                break

        items: list[Item] = []
        seen = set()
        for released, href in cand:
            time.sleep(DELAY)
            r = base.retry(lambda: c.get(SITE + href))
            r.raise_for_status()
            doc = HTMLParser(r.text)
            node = doc.css_first(".title h4")
            name = _pick(node.text()) if node else ""
            if not name:
                continue
            # 본문 이미지. /upload/ 는 robots 금지 경로라 URL 만 담고 요청하지 않는다.
            img = ""
            for n in doc.css("img"):
                src = n.attributes.get("src", "")
                if src.startswith("/upload/"):
                    img = SITE + src
                    break
            it = Item(
                brand=BRAND,
                name=name,
                desc=re.sub(r"^\s*오리온(그룹)?,\s*", "", " ".join(node.text().split())),
                image=img,
                released_at=released,
                is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                url=SITE + href,
            )
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)
    return items
