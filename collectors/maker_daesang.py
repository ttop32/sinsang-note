"""대상(청정원·종가) — 뉴스 게시판 JSON 에서 신제품과 출시일을 뽑는다.

**1·2·3차가 세 번 연속 "보류" 로 둔 브랜드다. 이번에 열고 밀도를 다시 쟀다.**
`notes/CANDIDATES-MAKER.md` §⑩ 은 파라미터와 응답 스키마까지 다 풀어 놓고도
**"밀도가 낮아 단독 브랜드로 올릴 값은 없다"** 로 접었다. 2026-10-02 에
10페이지 60건을 전수로 다시 받아 세어 보니 **그 판정이 맞다** — 다만
`N종` 규칙을 고친 뒤(아래) 창 안 수확이 **2건 → 3건**이 된다.
3건이면 CJ제일제당(36건 중 2건)과 같은 칸이라 **올리는 쪽으로 판단했다.**
(`notes/CANDIDATES-RAMEN-FROZEN.md` §5-7: "대기업 보도자료는 절반이 상품이
아니다. 건수가 적은 게 정상이고 '수집 실패'가 아니다.")

## 수집 경로 — 2026-10-02 실측

    POST https://www.daesang.com/proc/boardListJson.jsp
         b_id=notice & page=N & cate=news & sch_type= & sch_word= & lng=kr
    → 200 / 한 페이지 6건 / totalCount 271

⚠️ **`b_id` 는 `news` 가 아니라 `notice` 다.** 뉴스/공지 구분은 `cate` 가 한다.
   `b_id=news` 로 보내면 **에러가 아니라 `totalCount: 0` 이 조용히 온다** —
   빈 결과로 위장하는 함정이다(§⑩ 이 기록한 그대로 재확인했다).
       b_id=news   cate=news → totalCount 0    ← 함정
       b_id=notice cate=news → totalCount 271  ✅
⚠️ **응답 `Content-Type` 이 `text/html; charset=UTF-8` 인데 본문은 JSON** 이고
   **앞에 공백이 70여 자 붙어 있다.** `r.json()` 이 아니라
   `json.loads(r.text.strip())` 로 읽어야 한다.

응답 한 건(§⑩ 이 적은 스키마를 그대로 재확인했다):
    {"idx":"3284", "b_id":"notice", "cate":"news", "catename":"뉴스",
     "title":"대상 청정원, …‘피클링소스’ 출시",
     "reg_ymd":"2026.04.22", "reg_dt":"2026-04-22 13:59:23",
     "contents":"<p>…기사 전문…</p>",          ← 본문 전문이 목록에 온다
     "thum_1":"1788843561696.jpg", "file_1"~"file_4", "reg_ip":"172.30.21.65"}

🔴 **`reg_ip` 로 사내 사설 IP 가 그대로 노출된다. 읽지도 말고 로그에도 남기지 마라.**
   이 어댑터는 `title`·`reg_ymd`·`thum_1`·`idx` 네 키만 만진다.

## 날짜 — `reg_ymd` 는 보도일이 아니라 **등록일**이다

§⑩ 이 적은 두 가지를 그대로 확인했다.
  ① **하루 늦다.** 2026.09.08 등록 기사의 본문이 "…7일 밝혔다"로 쓴다.
  ② **묶음이 있다.** 60건에서 같은 날 2건 이상이 11쌍이다 —
     `2026.09.08 ×4`(13:30:30·13:31:57·13:41:38·13:59:23, **29분 안에 4건**) ·
     `2026.04.30 ×3` · `2025.11.24 ×3` · 나머지는 2건씩.
     롯데칠성·롯데웰푸드가 쓰는 '같은 날 4건' 임계에 **걸린다.**
→ 그래도 **`released_at` 에 쓴다.** 묶음 4건은 전부 ESG·기부·행사라 상품이
  아니고, 우리가 집는 출시 기사 3건은 **전부 단독 날짜**다(04.22 · 04.06 ·
  08.10). ±1일 오차는 감수한다. 동서식품 `regDt`(수개월 밀림)와는 급이 다르다.
⚠️ `reg_ymd` 가 없는 행은 **버린다.** `is_new=True` 를 날짜 없이 내보내면
  `rules.is_fresh()` 의 '날짜 없는 is_new' 분기가 STALE(90일) 동안 무조건
  화면에 올린다(`notes/CANDIDATES-RAMEN-FROZEN.md` §5-6, 농심 복각 사고).

## 밀도 — 10페이지 60건 전수(2025-07-03 ~ 2026-09-08)

출시 기사는 **3건뿐**이다:
    2026.08.10 대상 청정원, 알룰로스 신제품 3종 출시…’대체당 라인업 확대’
    2026.04.22 대상 청정원, ‘모노유즈’ 트렌드 반영한 용도형 식초 ‘피클링소스’ 출시
    2026.04.06 대상 청정원, 두 번 발효해 잡내 없이 깔끔한 ‘화이트식초’ 출시
나머지 57건은 기부·협약·박람회·포럼·수상·지분투자·할인기획전·광고캠페인,
그리고 **의약 바이오**(2025.12.19 독일 아미노산 기업 인수)다.
**3개월에 1건 꼴** — 이 레포에서 가장 낮은 축이다. 그래도 0 은 아니다.

🔴 **`N종` 을 통째로 버리지 않는다.** 오리온 계보 규칙(`_MULTI` 로 제목을 통째로
   폐기)을 그대로 쓰면 `알룰로스 신제품 3종 출시` 가 죽어 **3건이 2건이 된다.**
   신세계푸드(27건→0건)·풀무원(2건 손실)에서 같은 규칙이 브랜드를 통째로
   죽인 전례가 있다(`notes/CANDIDATES-RAMEN-FROZEN.md` §5-3).
   → **`maker_sajo.py` 처럼 꼬리(`N종`)만 떼고 상품은 살린다.**
   그리고 사조가 보탠 교훈대로 **따옴표 안만 쓰지 않는다** — 첫 따옴표부터
   동사 앞까지를 통째로 잡고 따옴표 기호만 턴다. 대상에서도 그게 맞다:
       `용도형 식초 ‘피클링소스’ 출시`  → 따옴표 안만 쓰면 '피클링소스'
       (여기선 따옴표가 상품명 전체를 감싸서 둘 다 같지만,
        `‘모노유즈’ 트렌드 반영한 용도형 식초 ‘피클링소스’` 처럼
        **앞 따옴표가 트렌드어**인 제목이 실재해서 '첫 따옴표부터' 는 위험하다)
   ⚠️ 그래서 대상은 사조와 **반대로** 간다 — 따옴표가 **여럿**이면 **마지막**
      따옴표를 쓴다(오리온 계보). 따옴표가 **없을 때만** 머리 전체를 쓴다.
      대상 제목은 `‘트렌드어’ … ‘상품명’ 출시` 꼴이 기본형이라 그렇다.

## 주어(회사명) 화이트리스트 — 키워드 역필터보다 정확하다

대상은 한 게시판에 **식품·바이오·소재·쇼핑몰·그룹 ESG** 가 다 섞인다.
60건의 주어를 세면:
    대상 / 대상 청정원 / 대상 청정원 호밍스 / 대상 청정원 그레인보우 / 대상 종가
        ← 우리가 쓰는 쪽(식품)
    **대상그룹**        ← ESG·캠페인·사회공헌·헌혈·장학. 상품이 아니다 (60건 중 11건)
    **대상 정원e샵**    ← 자사몰 **할인 기획전**. 상품이 아니라 행사다 (4건)
    **대상㈜**          ← 소재·바이오·IFT 전시 (1건)
`maker_pulmuone.py` 의 `_SUBJECTS` 와 같은 방식인데, 대상은 주어가
`대상 청정원 호밍스,` 처럼 **길게 늘어나서** 정확히 일치로는 못 받는다.
→ **접두(prefix) 일치**로 받되 **제외 접두를 먼저** 본다(`_DENY_LEAD`).
⚠️ `"대상" in title` 로 쓰면 안 된다 — `대상그룹`·`정원e샵` 이 전부 통과하고,
   게다가 **`대상` 은 '브랜드 대상 수상' 의 그 `대상`과 같은 글자**다.
   실제로 60건 중 `대상` 이라는 낱말이 상(賞) 뜻으로 쓰인 제목이 있다
   (`‘2026 뮤즈 크리에이티브 어워즈’ 2관왕`·`퍼스트브랜드 대상`).
   그래서 **문자열 포함이 아니라 접두 매칭**이어야 한다.

바이오·소재 축은 주어가 `대상,` 이라 화이트리스트를 통과한다 →
`_NOT_OUR_LINE` 으로 한 번 더 막는다(`아미노산`·`바이오`·`소재`·`의약`·`균주`).

## 분류 — 이 브랜드는 `냉동식품` 이 아니다

대상은 **장류·소스·조미료**가 본체이고, 냉동/간편식은 `호밍스`·`안주야` 라인이다.
창 안에 실제로 잡히는 3건이 **알룰로스(대체당)·피클링소스·화이트식초** 로
전부 조미료다. → `BRANDS` 세부분류를 **`조미료`** 로 적는다(`샘표` 와 같은 칸).
냉동식품 순위표에는 호밍스·안주야 때문에 남기되, 브랜드 분류는 실측을 따른다.

## 사진 — ⚠️ `verify_images()` 가 지운다. 알고 넣는다

`thum_1` 은 `/common/popup/download.jsp?realName=<파일명>` 으로 받는다.
2026-10-02 실측: **200 / 74,610바이트 / 매직바이트 `ffd8ffe0` = 진짜 JPEG**.
그런데 **`Content-Type: application/octet-stream;charset=UTF-8`** 에
`Content-Disposition: attachment` 다. `rules.verify_images()` 는
`content-type.startswith("image")` 를 요구하므로 **이 URL 은 전부 탈락하고
빈 문자열로 덮인다.** 즉 화면에는 사진이 안 나온다.
→ 그래도 URL 을 담는다. 이유 둘: ① 바이트는 진짜 이미지라 나중에 R2 미러링
(이슈 #5)을 할 때 바로 쓸 수 있다 ② 비워 두면 '사진이 없는 브랜드'로 보여
원인이 기록에서 사라진다. **`rules.py` 는 건드리지 않았다**(지시 사항).

robots: `https://www.daesang.com/robots.txt` → **200, 13바이트, text/plain.**
        원문 전체는 `User-Agent: *` **한 줄뿐이다** — 규칙이 하나도 없다.
        `Disallow` 가 없으므로 금지 경로도 없다. `Crawl-delay` 선언도 없다.
        그래도 `DELAY=2.2` 를 지킨다. UA 는 `base.UA` 그대로(위장 없음).
약관:   확인하지 않았다.
"""
import json
import re
import time
from datetime import date, timedelta

from . import base
from .base import Item

BRAND = "대상"
SITE = "https://www.daesang.com"
LIST = SITE + "/proc/boardListJson.jsp"
VIEW = SITE + "/kr/news/newsView.do"          # 상세. idx 로 연다
IMG = SITE + "/common/popup/download.jsp"     # ⚠️ octet-stream 으로 온다(위 참고)

MAX_PAGES = 10       # 한 페이지 6건 = 60건 ≈ 14개월. 폭주 방지 상한.
DAYS = 300
DELAY = 2.2

# 주어 화이트리스트. **접두**로 본다(문자열 포함 금지 — 위 docstring 참고).
# 제외를 먼저 보고, 그다음 허용을 본다.
_DENY_LEAD = ("대상그룹", "대상 정원e샵", "대상㈜", "대상홀딩스", "대상에프앤비")
_ALLOW_LEAD = ("대상 청정원", "대상 종가", "대상,", "대상 ")

# 식품 축이 아닌 것. 주어가 '대상,' 이라 화이트리스트를 통과해 버린다.
_NOT_OUR_LINE = ("아미노산", "바이오", "소재", "의약", "균주", "발효소재",
                 "라이신", "전분당", "펫", "반려")

# --- 제목 → 상품명 (maker_orion 계보 + maker_sajo 의 N종 꼬리떼기) ------------
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭|런칭)")
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
_QUOTE_CHARS = re.compile(r"[‘’'`“”\"]")
_TRAIL_SEP = re.compile(r"^\s*[·∙,、/]")
# 상품명 뒤에 붙는 수량·수식 꼬리. `3종`·`신제품 3종` 의 그 부분이다.
_COUNT_TAIL = re.compile(r"\s*\d+\s*종\s*$")
_NEW_TAIL = re.compile(r"\s*신제품\s*$")
_LEAD = re.compile(r"^\s*대상(그룹|㈜)?\s*(청정원|종가)?\s*(호밍스|그레인보우)?\s*[,·]?\s*")

_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "협약", "체결", "주주총회", "후원", "기부", "추모", "공모", "발대식",
         "심포지엄", "박람회", "팝업", "캠페인", "발탁", "앰배서더", "재단",
         "경연", "시상", "간담회", "개최", "스폰서", "리뉴얼", "실적",
         "매진", "진행", "참가", "참여", "전개", "지원", "프로젝트",
         "기획전", "할인", "세일", "인수", "투자", "포럼", "교육", "인증",
         "영상 공개", "광고", "행사", "제정", "동참", "선물세트",
         # 국내 출시가 아닌 건 화면에 올리면 거짓이 된다(크라운·삼립과 같은 축).
         "日", "美", "글로벌", "수출", "해외", "진출")
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱")
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")
_REPACK_HEAD = ("에디션", "라벨")
_REPACK_MID = ("테마", "에디션", "라벨", "컬래버", "콜라보")
_REPACK_NAME = ("에디션", "컬렉션", "한정판", "선물세트", "기획팩", "시리즈")


def _subject_ok(title: str) -> bool:
    """주어가 우리가 쓰는 식품 축인가. 제외 접두를 먼저 본다."""
    t = " ".join(title.split())
    if any(t.startswith(w) for w in _DENY_LEAD):
        return False
    return any(t.startswith(w) for w in _ALLOW_LEAD)


def _pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열."""
    t = " ".join(title.split())
    if any(w in t for w in _NOT_OUR_LINE):
        return ""
    if any(w in m.group(1) for m in _HEAD.finditer(t) for w in _REPACK_HEAD):
        return ""
    body = _HEAD.sub(" ", t)
    # ⚠️ `N종` 으로 제목을 버리지 않는다. 꼬리만 뗀다(위 docstring 🔴 참고).
    if any(w in body for w in _SKIP):
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
    # 대상 제목은 `‘트렌드어’ … ‘상품명’ 출시` 가 기본형이라 **마지막** 따옴표를 쓴다.
    # 따옴표가 아예 없으면(`알룰로스 신제품 3종 출시`) 주어를 떼고 머리 전체를 쓴다.
    q = list(_SINGLE.finditer(head))
    if q:
        quoted = q[-1]
        if any(w in head[quoted.end():] for w in _BETWEEN):
            return ""
        if _TRAIL_SEP.match(head[quoted.end():]):
            return ""
        name = quoted.group(1)
    else:
        name = _LEAD.sub("", head)
    name = _QUOTE_CHARS.sub("", name).strip()
    name = _NEW_TAIL.sub("", _COUNT_TAIL.sub("", name)).strip(" ,·∙!…")
    # 꼬리를 뗀 뒤에도 `신제품` 이 남는 꼴(`알룰로스 신제품`)을 한 번 더 턴다.
    name = _NEW_TAIL.sub("", name).strip(" ,·∙!…")
    if not (2 <= len(name) <= 40):
        return ""
    if any(c in name for c in "·∙&?"):
        return ""
    if any(w in name for w in _REPACK_NAME):
        return ""
    return name


def _date(s: str) -> str:
    """'2026.04.22' → '2026-04-22'. 월·일 범위를 검증한다."""
    m = re.match(r"^\s*(20\d{2})[-.](\d{1,2})[-.](\d{1,2})\s*$", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    items: list[Item] = []
    keys = set()
    seen = 0            # 읽은 행 수. 아래 가드의 진단용.
    stop = False
    with base.client(timeout=30) as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.post(LIST, data={
                "b_id": "notice", "page": page, "cate": "news",
                "sch_type": "", "sch_word": "", "lng": "kr"}))
            r.raise_for_status()
            # ⚠️ Content-Type 이 text/html 이고 앞에 공백이 70여 자 붙어 있다.
            data = json.loads(r.text.strip())
            rows = data.get("boardList") or []
            if not rows:
                break
            for b in rows:
                seen += 1
                title = " ".join((b.get("title") or "").split())
                released = _date(b.get("reg_ymd"))
                # 날짜가 없으면 버린다. is_new=True 를 날짜 없이 내보내면
                # rules.is_fresh() 가 90일 동안 무조건 화면에 올린다.
                if not released:
                    continue
                if released < floor:
                    stop = True
                    continue
                if not _subject_ok(title):
                    continue
                name = _pick(title)
                if not name:
                    continue
                thumb = (b.get("thum_1") or "").strip()
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=_LEAD.sub("", title),
                    # ⚠️ octet-stream 으로 와서 verify_images() 가 지운다(위 참고).
                    image=f"{IMG}?realName={thumb}" if thumb else "",
                    category="조미료",
                    released_at=released,
                    is_new=True,          # 브랜드가 '출시'라고 낸 기사다
                    url=f"{VIEW}?idx={b.get('idx')}" if b.get("idx") else SITE,
                )
                if it.key not in keys:
                    keys.add(it.key)
                    items.append(it)
            if stop:
                break

    # 파라미터가 하나만 틀려도 이 API 는 **에러가 아니라 빈 결과**를 준다
    # (b_id=news → totalCount 0). 그게 이 브랜드의 대표 함정이라 0행을 고장으로
    # 읽는다. 상품 0건은 고장이 아니다 — 3개월에 1건 꼴이라 실제로 0일 수 있다.
    if not seen:
        raise ValueError(
            "대상: boardListJson 이 0행을 돌려줬다. b_id=notice·cate=news 가 "
            "맞는지 확인하라 — b_id=news 로 보내면 에러 없이 totalCount 0 이 온다")
    return items
