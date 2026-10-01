"""오뚜기 — 보도자료에서 신제품과 출시일을 뽑는다.

이 프로젝트의 가장 큰 구멍이 released_at 이다. 브랜드 24곳 중 출시일을 주는 곳이
3곳뿐이다. 제조사 보도자료는 날짜가 DOM 에 박혀 있어서 그 구멍을 메운다.
대신 상품 축이 거칠다 — 기사 하나가 "2종"·"시리즈"를 통째로 말한다. 그래서
상품명을 특정할 수 있는 기사만 남기고 나머지는 버린다(아래 _pick).

수집 경로. 2026-09-30 실측:
  - 목록 페이지 /pr/news 는 JS 렌더라 링크가 0개다.
  - 그 페이지의 boardList() 가 /pr/otgnews_list_json 을 그냥 GET 한다.
    쿠키·토큰이 없다. 한 번에 9건, itemsCount 로 전체 건수를 준다.
    boardTitle·showRegDateTxt·listImagePath 가 다 들어 있어 상세를 안 받아도 된다.
  - searchNewsCategory=PRESS 로 보도자료만 고른다(504건). 나머지는 '오뚜기 소식'이다.
조사 문서(docs/CANDIDATES-DIRECT.md §10-6)는 "홈에서 6건을 긁으라"고 적었는데,
이 JSON 을 쓰면 요청 1회당 9건이고 홈 파싱도 필요 없다. 홈은 쓰지 않는다.

날짜는 showRegDateTxt(화면에 찍히는 날짜)를 쓴다. regDate 는 그보다 하루씩 늦는
등록 시각이다. 45건 실측에서 날짜가 전부 달랐다 — 일괄 재등록 흔적이 없다.
⚠️ HTML 을 긁을 때는 상세 페이지 푸터의 웹접근성 인증 배지 유효기간(2024.12.18 등)이
같이 걸린다. JSON 을 쓰면 그 함정 자체가 없다.

robots: https://www.otoki.com/robots.txt → 404, 본문 0바이트. 규칙 없음 = 허용.
        (ottogi.co.kr 은 otoki.com 으로 도메인이 옮겨갔다)
약관: 홈 HTML 에 이용약관·법적고지 링크가 없다. 확인 못 함.
"""
import re
import time
from datetime import date, timedelta

from . import base
from .base import Item

BRAND = "오뚜기"
SITE = "https://www.otoki.com"
LIST = SITE + "/pr/otgnews_list_json"
MAX_PAGES = 8        # 한 페이지 9건. 폭주 방지 상한.
DAYS = 300           # 이보다 오래된 보도자료는 신제품 섹션에 쓸모가 없다.
DELAY = 2.2          # 요청 간격(초)

# --- 제목 → 상품명 -----------------------------------------------------------
# 보도자료 제목은 "㈜오뚜기, <수식어> ‘<상품명>’ 출시" 꼴이다. 상품명은 거의 항상
# 홑따옴표 안에 있다. 쌍따옴표 “…” 는 홍보 헤드라인이라 판정에서 통째로 뺀다.
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭)")
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
_MULTI = re.compile(r"\d+\s*종")
_TRAIL_SEP = re.compile(r"^\s*[·∙,、/]")

# 기사 자체가 신제품 기사가 아닌 경우. '출시'가 들어 있어도 버린다.
# 실측 예: "‘꼬깔콘 야장시리즈’ 출시 보름만 80만 봉 판매 돌파" — 실제 출시는 보름 전이다.
_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "협약", "체결", "주주총회", "후원", "기부", "추모", "공모", "발대식",
         "심포지엄", "박람회", "팝업", "캠페인", "발탁", "앰배서더", "재단",
         "경연", "시상", "간담회", "개최", "스폰서", "리뉴얼", "실적",
         "매진", "진행", "참가", "참여", "전개", "지원")
# 따옴표와 '출시' 사이에 이게 끼면 따옴표 안은 상품명이 아니라 제휴 상대다.
# 실측 예: "영화 ‘스트리트 파이터’ 협업… 한정판 패키지 출시" → 상품명이 영화 제목이 된다.
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱")
# '출시' 뒤에 실적 문구가 붙으면 그 날짜는 출시일이 아니라 기사 작성일이다.
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")

# 기존 제품의 테마/에디션 패키지 기사. 상품이 새 게 아니고 따옴표 안도 상품명이 아니다.
# 실측은 다른 제조사에서 났다 — 오리온 ‘박지훈 라벨’(제주용암수 스페셜 에디션),
# 롯데웰푸드 ‘토이 스토리 5’ 테마 ‘가나 초콜릿’(1975년부터 팔던 제품).
# 같은 제목 규칙을 복사해 쓰는 파일이라 같은 구멍이 여기에도 있다.
# ⚠️ _BETWEEN 검사를 head 전체로 넓히는 식으로는 못 고친다. 협업으로 '만든' 신제품까지
#    같이 죽는다 — GS25 채택분 '사워레몬요거트'·'초BIG!무쿠점보멜론구미' 2건으로 실증됐다
#    (docs/QA-REPORT.md §2-6). '협업'이라는 단어가 아니라 **위치**가 그 구분이다.
_REPACK_HEAD = ("에디션", "라벨")                              # “…” 헤드라인 안
_REPACK_MID = ("테마", "에디션", "라벨", "컬래버", "콜라보")      # 따옴표와 따옴표 사이


def _pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열.

    "젤리 2종 출시"처럼 기사 하나에 상품이 여럿이면 버린다. 억지로 '젤리 2종'을
    상품명으로 쓰지 않는다.
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
    # 닫는 따옴표 바로 뒤가 구분자면 상품이 더 이어진다.
    # 실측: "‘칡냉면’·’쫄냉면’ 출시" — 뒤쪽 따옴표가 여는 부호까지 ’ 라 정규식에 안 걸린다.
    if _TRAIL_SEP.match(head[quoted.end():]):
        return ""
    name = quoted.group(1).strip(" ,·∙")
    if len(name) < 2 or any(c in name for c in "·∙&?"):
        return ""
    return name


def _date(s: str) -> str:
    """'2026.09.28' → '2026-09-28'. 월·일 범위를 검증한다.

    범위를 안 보면 UUID 조각(`2026/06/92`)이 날짜로 둔갑한다(다른 제조사에서 실측).
    """
    m = re.match(r"^\s*(20\d{2})[-.](\d{1,2})[-.](\d{1,2})\s*$", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _abs(path: str) -> str:
    path = (path or "").strip()
    if not path:
        return ""
    return path if path.startswith("http") else SITE + path


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"pageIndex": page,
                                                       "searchNewsCategory": "PRESS"}))
            r.raise_for_status()
            rows = r.json().get("data") or []
            if not rows:
                break

            stop = False
            for row in rows:
                released = _date(row.get("showRegDateTxt") or row.get("regDate") or "")
                if released and released < floor:
                    stop = True
                    continue
                name = _pick(row.get("boardTitle") or "")
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    # 기사 제목이 그대로 설명이 된다. 앞의 회사명만 턴다.
                    desc=re.sub(r"^\s*\(?재?\)?㈜?[가-힣A-Za-z]*오뚜기[^,]*,\s*", "",
                                " ".join((row.get("boardTitle") or "").split())),
                    image=_abs(row.get("listImagePath")),
                    released_at=released,
                    is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                    url=f"{SITE}/pr/news-detail?idx={row.get('idx')}",
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)
            if stop:
                break
    return items
