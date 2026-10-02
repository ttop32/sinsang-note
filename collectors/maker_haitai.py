"""해태제과식품 — 뉴스 API 에서 신제품과 출시일을 뽑는다.

오뚜기·오리온·샘표·GS25 와 같은 계보다(보도자료 제목 → 상품명). 다른 점은
소스가 HTML 이 아니라 **깨끗한 JSON API** 라는 것 하나뿐이라 조인 규칙은
`collectors/maker_orion.py` 것을 그대로 가져왔다.

수집 경로. 2026-10-02 실측:
  GET https://www.ht.co.kr/api/external/sweet/news?offset=0&limit=50   14,971B
  {"sweetNewsSelectDtos":[
     {"newsBoardId": 93066,
      "newsBoardTitle": "해태제과, 한입에 쏙 ! ‘후렌치파이 미니 피넛버터크림’ 출시",
      "newsBoardMediaPressDt": "2026-09-17",        ← 보도일. 이게 released_at 이다
      "thumbnailFileId": 204544,
      "fileNm": "O99667_20260917180059-thumbnail.jpg"}, …],
   "totalCount": 728}
  `offset`·`limit` 둘 다 GET 으로 먹는다. limit=120 이 41KB 라 한 번에 받는다.

썸네일 주소는 원본 HTML 에 없다. 페이지가 **blob: URL** 로 그려서 눈으로는
안 보이고, 브라우저 네트워크 로그를 떠서 찾았다:
  GET /api/external/sweet/news/fileNm?fileNm={fileNm}&thumbnailFileId={id}
  → 200 image/png 466,929B   (실측: fileNm=H23179_20261001151955-thumbnail.png)
`fileNm` 과 `thumbnailFileId` **둘 다** 있어야 한다. 하나만 보내면 셸이 온다.
우리는 이 주소를 Item.image 에 담기만 하고 어댑터가 직접 요청하지는 않는다.

⚠️ **상세 주소가 없다.** 사이트가 SPA 라 모든 경로가 같은 3,849바이트 셸을
   돌려준다 — `/api/external/sweet/news/93066`·`/sweet/newsView?…` 를 쳐 봐도
   전부 그 셸이다(md5 동일). 지어낸 주소를 Item.url 에 넣으면 눌렀을 때 404 가
   뜨므로 **비워 두고 SITES 의 목록 주소로 떨어지게 한다.**
⚠️ **상태코드로 검증하지 마라.** 위와 같은 이유로 없는 경로도 200 이다.
   JSON 키(`sweetNewsSelectDtos`) 유무로만 판정한다.

**제품 API 는 안 쓴다.** 왜 안 쓰는지가 이 브랜드의 핵심이다.
  GET /api/external/product/list/productListByCategory?productCategoryId=&offset=0&limit=500
  → 96건 전부가 79,840B 에 온다. `productNewIconYn` 불리언까지 준다. 그런데
  ① `createdDttm` 이 **사이트 개편 일괄 등록**이다. 96건의 날짜를 세면
     2024-08-22 ×28 · 2024-08-26 ×16 · 2024-09-27 ×11 · 2024-08-21 ×8 …
     로 71건이 2024-08~09 에 몰려 있다. 동서식품 `regDt` 와 같은 사고다.
  ② **NEW 배지가 늙는다.** `충전시간` 은 2024-08-26 생성인데 아직
     `productNewIconYn: true` 다(2026-10-02 실측). 수동 관리라 안 내려간다.
     그대로 믿으면 2년 된 상품이 신상으로 올라간다.
  ③ 최근 분에도 묶음이 있다 — 2026-07-30 에 4건(11:26·11:27·13:32·13:37).
     하루 4개 출시가 아니라 콘텐츠 일괄 갱신이다.
  ④ 교차검증 1건: `와샤오롱` 이 뉴스 2026-09-09, 제품 `createdDttm` 2026-09-23.
     **보도가 먼저고 카탈로그 등록이 2주 뒤**다. 날짜는 뉴스 쪽이 맞다.
  그리고 ⑤ 뉴스에 나온 신제품 중 카탈로그에 없는 게 더 많다(멜론 포키·구운나초·
  연어초밥맛 전부 `productNm` 에 0건). 이름 보강 소스로도 값이 없다.
  → **신상 판정도 날짜도 뉴스 API 로만 한다.**

⚠️ **`fileNm` 의 타임스탬프를 날짜로 쓰지 마라.** 최신 건은 `…_20261001152853-…`
   인데 `newsBoardMediaPressDt` 는 2026-09-30 이다(업로드 시각이 하루 늦다).
   크라운제과는 반대로 파일명이 두 달 **빠르다**. 어느 쪽으로도 못 믿는다.

**일괄 등록 흔적 — 없다.** 120건의 `newsBoardMediaPressDt` 를 세어 보면
2024-02-26 ~ 2026-09-30 에 고르게 퍼져 있고 같은 날 2건이 1쌍뿐이다
(2024-08-27 ×2). 일화 `<li class="time">` 같은 묶음이 없어 그대로 믿는다.

**이 피드는 지주(크라운해태) 기사가 절반이다.** 120건 중 40건 가까이가
국악·조각·창신제·한음영재·디스크골프·눈꽃축제 같은 메세나·행사다. 계보의
`_SKIP`/`_TAIL` 이 대부분 걷어내고, 남는 건 애초에 `_VERB`('출시'·'론칭'…)가
없어서 빠진다.

**해태에서 새로 보탠 조인 규칙 3개** (120건 제목을 전수로 눈으로 훑고 맞췄다):
  ① **따옴표 안이 '에디션' 이면 기존 제품의 포장 기사다.** 계보의 `_REPACK_HEAD`
     는 “…” 헤드라인 안만 보는데, 해태는 **상품명 자리에 그대로** 쓴다.
       '쿨 에디션' 한정판 출시 / '후렌치파이 감각 탐험 에디션' 출시
     → `_REPACK_NAME` 으로 이름 자체를 본다. 둘 다 버려진다.
  ② **따옴표 안이 맛 이름뿐인 경우가 잦다.** 해태는 "<제품라인> ‘<맛>’ 출시"
     로 쓴다 — `포키 극세 ‘멜론’`, `가루비감자칩 ‘연어초밥맛’`.
     그대로 담으면 화면에 **'멜론'** 이라는 상품이 뜬다. 제품라인을 따오려면
     조사·수식어를 가르는 규칙이 필요한데 그건 못 믿을 걸 담는 쪽이라
     **놓치는 쪽을 골랐다**(계보 전체의 방침, sempio.py 와 같다).
     판정: 공백 없이 3자 이하이거나 '맛' 으로 끝나면 버린다.
  ③ **제목 머리의 서브브랜드를 상품명 앞에 붙인다.** `해태 빨라쪼, … ‘고르곤졸라
     치즈’ 출시` 의 상품은 '고르곤졸라 치즈' 가 아니라 '빨라쪼 고르곤졸라 치즈' 다.
     `^해태\\s+(\\S+),` 로 서브브랜드가 잡힐 때만 붙인다(실측: 빨라쪼·고향만두·
     홈런볼·샌드에이스·포키·글리코). `해태,`·`해태제과,` 는 서브브랜드가 아니라
     안 붙는다.
  그리고 이름에 `!` 가 들어가면 버린다 — 상품명이 아니라 구호다
  (`‘특명! 과자를 지켜라!’`). 계보의 금지문자 `·∙&?` 에 `!` 를 더한 것이다.

조인 결과 120건(2024-02-26 ~ 2026-09-30) 중 **최근 300일에서 5건**이 남는다.
전수로 눈을 대고 센 손실도 적어 둔다 — '출시'가 든 기사 중 버리는 것들:
  · `N종`·`N탄` 묶음 기사 (두바이스타일 5종, 가을 카페 에디션 4종, 햇밤 5종…)
  · **따옴표가 아예 없는 진짜 신제품** — `프리미엄 버터링 출시`(2026-09-21),
    `우리쌀로 만든 진짜 쌀만두 출시`(2025-02-18). 상품명을 특정할 수 없어 버린다.
  · **`출시` 동사가 없는 진짜 신제품** — `… ‘에이스 씬 솔티카라멜’!`(2026-04-20).
    제목 끝이 느낌표라 `_VERB` 가 안 걸린다. 제품 API 에 `에이스 씬 솔티카라멜맛`
    으로 실재하는 상품이다. **아는 손실**이고, 동사 없이 따 오면 행사·수상
    기사가 통째로 딸려 오므로 열지 않았다.

robots: `https://www.ht.co.kr/robots.txt` → **200, 3,849B, `text/plain` 인데
        내용은 HTML 이다.** 존재할 수 없는 경로(`/zzz-does-not-exist-12345`)와
        **md5 가 바이트 단위로 같다**(5e27b0b11ed9). 즉 robots.txt 는 없고
        SPA 가 모든 경로에 공용 셸을 준다 — 규칙을 읽을 수 없는 '판정 불가' 다
        (notes/CANDIDATES-MAKER.md §③). 운영자 판단으로 수집한다.
약관:   확인하지 않았다. SPA 라 푸터 링크도 같은 셸로 떨어진다.
"""
import re
import time
from datetime import date, timedelta

from . import base
from .base import Item

BRAND = "해태제과식품"
SITE = "https://www.ht.co.kr"
NEWS = SITE + "/api/external/sweet/news"
IMAGE = NEWS + "/fileNm"
LIMIT = 120          # 한 번에 받는 건수. 41KB. 300일 창을 넉넉히 덮는다.
MAX_PAGES = 2        # 폭주 방지 상한. 240건이면 2년치다.
DAYS = 300
DELAY = 2.2

# --- 제목 → 상품명 (maker_orion 과 같은 규칙 + 해태 함정 보강) ----------------
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
         # 해태 실측 추가분. 지주(크라운해태)의 메세나·행사 기사 축이다.
         "국악", "조각전", "창신제", "한음", "공연", "축제", "대회", "출간",
         # 국내 출시가 아닌 건 화면에 올리면 거짓이 된다(삼양식품 §①-2 와 같은 축).
         "日", "美", "글로벌", "수출", "해외")
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱")
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")
_REPACK_HEAD = ("에디션", "라벨")
_REPACK_MID = ("테마", "에디션", "라벨", "컬래버", "콜라보")
# 해태 보강 ① — 따옴표 '안' 이 포장 기사를 가리키는 경우. 계보엔 없다.
_REPACK_NAME = ("에디션", "컬렉션", "한정판", "선물세트", "기획팩")

# 해태 보강 ③ — 제목 머리의 서브브랜드. `해태 빨라쪼,` 꼴만 잡는다.
# `해태,`·`해태제과,` 는 회사명이라 안 걸린다(공백 뒤에 또 토큰이 와야 한다).
_SUBBRAND = re.compile(r"^\s*해태\s+([가-힣A-Za-z0-9]{2,10})\s*,")


def _weak(name: str) -> bool:
    """상품명이 아니라 '맛 이름' 뿐인가 (해태 보강 ②).

    `포키 극세 ‘멜론’`·`가루비감자칩 ‘연어초밥맛’` 처럼 제품라인은 따옴표 밖에
    있고 안에는 맛만 있는 제목이 잦다. 제품라인을 따오려면 조사·수식어를 가르는
    규칙이 필요한데 못 믿을 걸 담는 쪽이라 버리는 쪽을 골랐다.
    """
    return (" " not in name and len(name) <= 3) or name.endswith("맛")


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
    rest = head[quoted.end():]
    if _TRAIL_SEP.match(rest) or _NEXT_QUOTE.match(rest):
        return ""
    hq = list(_SINGLE.finditer(head))
    if len(hq) >= 2 and not head[hq[-2].end():hq[-1].start()].strip():
        return ""
    name = quoted.group(1).strip(" ,·∙")
    # `!` 는 계보의 금지문자에 해태에서 보탠 것이다 — `‘특명! 과자를 지켜라!’`
    # 처럼 구호를 따옴표에 넣는 제목이 있다.
    if len(name) < 2 or any(c in name for c in "·∙&?!"):
        return ""
    if any(w in name for w in _REPACK_NAME) or _weak(name):
        return ""
    # 서브브랜드를 앞에 붙인다. '빨라쪼 고르곤졸라 치즈' 가 '고르곤졸라 치즈'
    # 보다 정확하다. 이미 들어 있으면 두 번 붙이지 않는다.
    sub = _SUBBRAND.match(t)
    if sub and sub.group(1) not in name:
        name = f"{sub.group(1)} {name}"
    return name


def _date(s: str) -> str:
    """'2026-09-17' → 그대로. 월·일 범위를 검증한다."""
    m = re.match(r"^\s*(20\d{2})[-.](\d{1,2})[-.](\d{1,2})\s*$", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _image(row: dict) -> str:
    """썸네일 주소. fileNm 과 thumbnailFileId 가 둘 다 있어야 그림이 온다."""
    fid, fnm = row.get("thumbnailFileId"), row.get("fileNm")
    if not fid or not fnm:
        return ""
    from urllib.parse import quote
    return f"{IMAGE}?fileNm={quote(str(fnm))}&thumbnailFileId={fid}"


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    with base.client() as c:
        for page in range(MAX_PAGES):
            if page:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(NEWS, params={"offset": page * LIMIT,
                                                       "limit": LIMIT}))
            r.raise_for_status()
            # ⚠️ 상태코드로 검증하지 마라 — SPA 라 없는 경로도 200 에 셸을 준다.
            #    JSON 키가 있는지로 판정한다.
            try:
                data = r.json()
                rows = data["sweetNewsSelectDtos"]
            except Exception as e:
                raise ValueError(
                    f"해태 뉴스 API 가 JSON 을 안 준다. {r.url} → {len(r.content)}B, "
                    f"content-type={r.headers.get('content-type')} — SPA 공용 셸로 "
                    f"떨어졌는지(= 경로가 바뀌었는지) 확인하라") from e
            if page == 0 and not rows:
                raise ValueError(
                    f"해태 뉴스 API 가 0건이다. {r.url} → totalCount="
                    f"{data.get('totalCount')} — 728건짜리 아카이브라 비어 있을 수 없다")
            if not rows:
                break

            for row in rows:
                title = " ".join((row.get("newsBoardTitle") or "").split())
                released = _date(row.get("newsBoardMediaPressDt") or "")
                if released and released < floor:
                    continue
                name = _pick(title)
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    # 기사 제목이 그대로 설명이 된다. 앞의 회사명만 턴다.
                    desc=re.sub(r"^\s*해태(제과)?(식품)?[^,]{0,10},\s*", "", title),
                    name=name,
                    image=_image(row),
                    released_at=released,
                    is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                    # 상세 주소가 없다(SPA). SITES 의 목록 주소로 떨어진다.
                    url="",
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

            fresh = [_date(x.get("newsBoardMediaPressDt") or "") for x in rows]
            fresh = [d for d in fresh if d]
            if fresh and max(fresh) < floor:
                break
            if len(rows) < LIMIT:
                break
    return items
