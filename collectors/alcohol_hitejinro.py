"""하이트진로 — 보도자료에서 신제품과 출시일을 뽑는다.

주류 제조사 중 유일하게 넣을 수 있는 곳이다. `notes/CANDIDATES-ALCOHOL.md` 가
13곳을 조사했는데 오비맥주·수입사 3곳은 **성인 인증 게이트** 뒤라 접근 자체가
막히고, 국순당(2022-01 정지)·서울장수·무학·배상면주가는 뉴스가 멈췄거나 날짜가
아예 없다. 여기만 전부 통과했다.

⚠️ 같은 사이트의 **제품 페이지는 성인 인증 뒤**다. 보도자료만 쓴다.

수집 경로. 2026-10-02 실측:
  - `GET /socialmedia/press_list.asp?page=N` — 완전 SSR(95KB). 7건씩, 223페이지.
  - 한 행에 날짜·제목·요약·이미지가 다 들어 있어 상세를 안 받아도 된다.
  - robots.txt 는 22바이트 `User-agent: * / Allow:/` 다. 가장 깨끗한 형태.

제목은 오뚜기와 같은 꼴이라 그쪽 규칙(collectors/maker_ottogi.py `_pick`)을
그대로 가져왔다. 하이트진로만의 차이 셋:

  ① **홑따옴표 헤드라인이 회사명 앞에 붙는다.** GS25 와 같은 함정이다.
     실측: `‘일품진로 전용쌀 100% 사용’하이트진로, ‘일품진로 1924 헤리티지’ 한정판 출시`
     앞의 따옴표를 상품명으로 집으면 '일품진로 전용쌀 100% 사용' 이 된다.
     그래서 **회사명 앞은 통째로 버린다.**
  ② **`<h3 class="title">` 이 잘려 있다**(`…ULTRA JA...`). `<p class="content">`
     첫머리에 안 잘린 제목이 그대로 있어서 거기서 딴다. 소제목은 `-` 로 이어지니
     첫 `-` 앞까지가 제목이다.
  ③ 🔴 **미래 날짜가 실제로 들어온다.** 1페이지 최신 기사가 `2026 10.29` 인데
     조사일이 2026-10-01 이었고 다음 기사가 09.22 다. 사이트 쪽 오타로 보이지만
     **날짜가 이 어댑터의 전부**라 그냥 믿으면 안 된다. 오늘보다 뒤면 버린다.

28건(4페이지) 실측에서 상품 기사는 4건이다 — '일품진로 1924 헤리티지'·'일품진로
하이볼 선물세트'·'테라 스파클링'·'일품진로 26년산'. 월 1~2건으로 동서식품과 같은
급이다. 걸러낸 것 중 눈으로 확인한 경계 사례: `‘켈리’ 패키지 리뉴얼`(출시가 아님),
`‘참이슬 후레쉬 부산 에디션’ 출시`(에디션=기존 제품 재포장), `‘진로 아이스백팩’`
(굿즈). 앞의 둘은 `_VERB`·`_REPACK` 이 막고, 굿즈는 base.is_nonfood 가 가른다.

⚠️ 주류다. 이 사이트는 주류를 한동안 통째로 뺐다가 운영자 지시로 열었다.
사유와 되돌릴 조건은 rules.is_fresh 주석 참고.
"""
import re
import time
from datetime import date, timedelta

from . import base
from .base import Item

BRAND = "하이트진로"
SITE = "https://www.hitejinro.com"
LIST = SITE + "/socialmedia/press_list.asp"
MAX_PAGES = 10       # 한 페이지 7건. 폭주 방지 상한.
DAYS = 300           # 이보다 오래된 보도자료는 신제품 섹션에 쓸모가 없다.
DELAY = 2.2          # 요청 간격(초)

_ROW = re.compile(r'<td class="date">(.*?)</tr>', re.S)
_DATE = re.compile(r"<small>(\d{4})</small>\s*(\d{1,2})\.(\d{1,2})")
_CONTENT = re.compile(r'<p class="content">(.*?)</p>', re.S)
_IMG = re.compile(r'<td class="imgbox">.*?<img[^>]+src="([^"]+)"', re.S)
_SEQ = re.compile(r'press_view\.asp\?seq=(\d+)')
_TAG = re.compile(r"<[^>]+>")

# 회사명 앞은 홍보 헤드라인이다(위 §①). 여기서부터가 진짜 제목이다.
_LEAD = re.compile(r"하이트진로\s*,")
# 소제목은 '-' 로 이어 붙는다. 첫 '-' 앞까지가 제목이다.
_SUBHEAD = re.compile(r"\s*-\s.*$", re.S)

# --- 제목 → 상품명 (오뚜기 규칙) ---------------------------------------------
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭)")
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
_MULTI = re.compile(r"\d+\s*종")
_TRAIL_SEP = re.compile(r"^\s*[·∙,、/]")

# 상품 기사가 아닌 것. 주류 회사는 후원·캠페인·ESG 기사가 특히 많아서
# 오뚜기 목록에 그쪽 말을 더 넣었다(28건 실측에서 24건이 여기 걸린다).
_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "후원", "개최", "참가", "캠페인", "기부", "나눔", "봉사", "실천", "동행",
         "보고서", "발표", "공개", "육성", "투자", "리뉴얼", "축제", "시음회")
# 따옴표와 '출시' 사이에 이 말이 있으면 따옴표는 상품명이 아니다.
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "캠페인")
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")
# 기존 제품의 재포장 기사. 신상이 아니다.
_REPACK = ("에디션", "라벨", "패키지", "한정판매")
# 소제목에 이게 있으면 라벨·디자인만 바꾼 기사다(아래 _is_repack).
_REPACK_SUB = ("라벨", "디자인 적용", "패키지 리뉴얼", "디자인 리뉴얼")


def _summary(block: str) -> str:
    """한 행의 요약 전체. 제목 + '-' 로 이어진 소제목들이다(위 §②)."""
    m = _CONTENT.search(block)
    if not m:
        return ""
    t = _TAG.sub(" ", m.group(1))
    t = (t.replace("&#39;", "'").replace("&amp;", "&")
          .replace("&quot;", '"').replace("&nbsp;", " "))
    return " ".join(t.split())


def _title(summary: str) -> str:
    """요약에서 제목만. 첫 '-' 앞까지다."""
    return " ".join(_SUBHEAD.sub("", summary).split())


def _is_repack(summary: str) -> bool:
    """라벨·디자인만 바꾼 한정판인가. 소제목이 그걸 말해준다.

    제목만 보면 못 가른다 — `진로(JINRO) 'K-POP 스타 두꺼비' 한정판 출시` 와
    `'일품진로 1924 헤리티지' 한정판 출시` 가 같은 모양이다. 앞은 기존
    청포도에이슬에 **라벨만 바꾼 것**이고(소제목: "두꺼비 디자인 적용, 수출 전용
    청포도에이슬 한정판 출시", 본문도 "'K-POP 스타 두꺼비' 라벨을 적용한
    한정판"), 뒤는 전용쌀로 새로 증류한 술이다. 기사 본문까지 열어 확인했다.

    그래서 제목이 아니라 **소제목까지 포함한 요약 전체**를 본다. 제목에만
    이 말이 들어간 경우는 `_REPACK` 이 따로 막는다.
    """
    sub = summary[len(_title(summary)):]
    return any(w in sub for w in _REPACK_SUB)


def _pick(title: str) -> str:
    """제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열.

    규칙은 collectors/maker_ottogi.py `_pick` 과 같다. 다른 건 맨 앞에서
    회사명 앞을 떼는 것뿐이다 — 하이트진로는 홍보 헤드라인이 홑따옴표라
    그걸 안 떼면 헤드라인을 상품명으로 집는다(위 §①).
    """
    t = " ".join(title.split())
    m = _LEAD.search(t)
    if not m:
        return ""
    body = _HEAD.sub(" ", t[m.end():])
    if any(w in body for w in _SKIP) or _MULTI.search(body):
        return ""
    verb = None
    for v in _VERB.finditer(body):
        verb = v
    if not verb or any(w in body[verb.end():] for w in _TAIL):
        return ""
    head = body[:verb.start()]
    if any(w in head for w in _REPACK):
        return ""
    quoted = None
    for q in _SINGLE.finditer(head):
        quoted = q
    if not quoted or any(w in head[quoted.end():] for w in _BETWEEN):
        return ""
    if _TRAIL_SEP.match(head[quoted.end():]):
        return ""
    name = quoted.group(1).strip(" ,·∙")
    if len(name) < 2 or any(c in name for c in "·∙&?"):
        return ""
    return name


def _date_of(block: str, today: str) -> str:
    """'2026 09.08' → '2026-09-08'. 범위와 미래 날짜를 검증한다(위 §③)."""
    m = _DATE.search(block)
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    got = f"{y:04d}-{mo:02d}-{d:02d}"
    return "" if got > today else got


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    today = date.today().isoformat()
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    rows_seen = 0
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"page": page}))
            r.raise_for_status()
            blocks = _ROW.findall(r.text)
            if not blocks:
                break
            rows_seen += len(blocks)

            stop = False
            for blk in blocks:
                released = _date_of(blk, today)
                # 날짜를 못 읽은 행은 버리되 중단 판정에는 넣지 않는다.
                # 미래 날짜 한 건 때문에 수집이 멈추면 안 된다.
                if not released:
                    continue
                if released < floor:
                    stop = True
                    continue
                summary = _summary(blk)
                if _is_repack(summary):
                    continue
                title = _title(summary)
                name = _pick(title)
                if not name:
                    continue
                img = _IMG.search(blk)
                seq = _SEQ.search(blk)
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=_LEAD.sub("", title, count=1).strip(" ,"),
                    image=img.group(1) if img else "",
                    released_at=released,
                    is_new=True,      # 브랜드가 '출시'라고 낸 기사다
                    url=f"{SITE}/socialmedia/press_view.asp?seq={seq.group(1)}"
                        if seq else SITE,
                    # 주류 제조사다. 굿즈(백팩·키링)만 빼고 전부 술로 본다 —
                    # 이름만 보는 base.is_alcohol 로는 '테라 스파클링' 을 못 잡는다.
                    alcohol=not base.is_nonfood(name, ""),
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)
            if stop:
                break

    # 목록이 통째로 안 읽히면 0건으로 조용히 끝난다. 그건 수집 성공이 아니다.
    if rows_seen < 7:
        raise RuntimeError(f"하이트진로 보도자료를 {rows_seen}행밖에 못 읽었다 "
                           "— 목록 마크업이 바뀌었을 수 있다")
    return items
