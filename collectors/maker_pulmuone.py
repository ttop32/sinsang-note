"""풀무원 — 뉴스룸 '브랜드 뉴스' 탭에서 신제품과 출시일을 뽑는다.

오뚜기·오리온·샘표·삼양식품과 같은 계보다(보도자료 제목 → 상품명).
조인 규칙은 `collectors/maker_orion.py` 것을 그대로 가져왔다.
아워홈 하나뿐이던 냉동·간편식 축을 메우는 어댑터다.

**1차 조사가 "어려움(목록이 JS)" 으로 접었던 브랜드다. JS 가 아니라 완전 SSR 이다.**
1차가 "날짜 토큰 1개" 라고 센 이유를 3차가 찾았다 — **날짜 포맷**이다.
풀무원은 `2026-09-23` 이 아니라 **`2026년 9월 23일`** 로 쓴다. `\\d{4}[-.]\\d{2}[-.]\\d{2}`
류 정규식으로 세면 0~1개로 보인다. (notes/CANDIDATES-MAKER.md §⑥)

수집 경로. 2026-10-02 실측:
  GET https://news.pulmuone.co.kr/pulmuone/newsroom/listPulmuone.do
      ?menu=312&pageIndex=1                                 200 / 136,778B
    <div class="fact_list_n01"><ul>
     <li><a href="/pulmuone/newsroom/viewNewsroom.do?id=3936">
       <div class="fl"><img src="/webfile/bbs/3/3936/20260914132550_[사진]th.jpg "/></div>
       <div class="fr">
         <div class="list_tit">풀무원, 고압으로 두 번 뽑아 격이 다른 식감
                               ‘식감혁신 본격 떡볶이’ 출시</div>
         <div class="list_desc">…기사 본문 전체…</div>
         <div class="list_date">2026년 9월 15일</div>
       </div></a></li>
  **제목이 잘리지 않는다.** 목록에 기사 본문까지 들어 있어 상세를 열 필요가 없다.
  페이지당 6건, `pageIndex=N` 이 GET 으로 먹는다(1·2·3 페이지 실측, 날짜가 내려간다).
  ⚠️ `img src` 앞뒤에 공백이 붙어 있다. strip 하지 않으면 깨진 URL 이 된다.

탭 구조(`menu` 파라미터). **312 만 쓴다**:
  311 기업뉴스 — GEO·실적·조직        ❌
  312 브랜드 뉴스 — ✅ 여기가 신제품이다
  313 뮤지엄김치간 — 전시·문화        ❌
  314 사회공헌 뉴스                   ❌

**⚠️ 이 브랜드의 유일한 진짜 문제 — 계열사가 섞인다.**
3페이지 18건의 주어를 세면 풀무원 본체는 절반도 안 된다:
    풀무원 · 올가홀푸드          ← 우리가 쓰는 쪽(식품)
    풀무원헬스케어 · 풀무원건강생활 ← **건강기능식품·퍼스널케어**
        '관절엔 콘드로이친 1200 퀵샷' · '리셋 슬림 다이어트 유산균 150' · '그린샷'
        '풀무원로하스 365 클린 바디워시' ← **바디워시다. 먹는 게 아니다**
    풀무원푸드앤컬처              ← **급식·공항 라운지**('스카이허브라운지 프리미엄')
    테이스티풀무원                ← 체험 클래스 브랜드
→ **키워드 역필터가 아니라 주어(회사명) 화이트리스트로 가른다.** `_SUBJECTS` 참고.
   역필터로는 '클린 바디워시' 를 못 막는다 — 이름에 비식품 단어가 하나도 없다.
   ⚠️ `"풀무원" in subject` 로 쓰면 안 된다. 풀무원헬스케어·풀무원건강생활·
      풀무원푸드앤컬처가 전부 통과한다. **정확히 일치**로만 본다.

**⚠️ 주어로 못 막는 구멍이 둘 있다 — 6페이지 36건 전수 실측으로 찾았다.**
  ① **본체가 내는 펫푸드.** `풀무원, 7세 이상의 반려견 위한 ‘아미오 건강담은
     Soft 현미간식’ 출시`(2026-08-25). 주어가 '풀무원' 이라 화이트리스트를
     통과하고 `base.is_nonfood()` 도 모른다 → `_NOT_OUR_LINE` 으로 막는다.
  ② **본체가 내는 주방 가전.** `‘스팀 솔루시온 멀티 오븐’`(2026-06-10) ·
     `‘그린더 에어드라이 음식물 처리기’`(2026-05-21). 지금은 `MAX_PAGES` 창
     밖이지만 새로 나오면 바로 들어온다 → `_APPLIANCE_TAIL` 로 `nonfood=True`
     를 찍는다(버리지 않는다).

**버리는 쪽 (3페이지 18건 전수 확인).**
  진행·성료·운영·실적·프로모션·기획전 7건 · 계열사(건기식·급식·퍼스널케어) 6건 ·
  `‘하루에 건강을 더하는 달걀’ 3종 출시`·`‘ORGA 저염 육수’ 2종 출시` 2건은
  **`N종` 규칙에 걸려 버린다**(maker_orion 과 같은 규칙, **아는 손실**이다).
  남는 건 `식감혁신 본격 떡볶이` · `생만두` · `콩나물국 요리키트` ·
  `저당 통현미 크런치볼`(올가홀푸드) 꼴이다.

**일괄 등록 흔적 — 없다.** 3페이지 18건의 날짜가 10-02 ~ 08-27 로 고르게 흩어져 있고
같은 날짜는 2쌍뿐이다(9/23 ×2, 9/15 ×2, 9/03 ×2). 롯데웰푸드 `<em>`(7개 날짜에
54건이 뭉친 일괄 등록)과 다르다. 이미지 경로의 업로드 시각(`20260914132550`)도
기사 날짜와 하루 안쪽으로 맞는다.

robots: https://news.pulmuone.co.kr/robots.txt → 200. `www.` 와 같은 파일(3,401B).
        `User-agent: *` 에 `Allow: /`, `Disallow: /Siteadmin/`. 뉴스룸은 허용이다.
약관:   확인하지 않았다.
"""
import re
import time
from datetime import date, timedelta
from urllib.parse import quote

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "풀무원"
SITE = "https://news.pulmuone.co.kr"
LIST = SITE + "/pulmuone/newsroom/listPulmuone.do"
VIEW = SITE + "/pulmuone/newsroom/viewNewsroom.do"
MENU = 312           # 브랜드 뉴스. 311=기업 / 313=김치간 / 314=사회공헌
MAX_PAGES = 6        # 한 페이지 6건. 폭주 방지 상한.
DAYS = 300
DELAY = 2.2

# 쓰는 계열사. **정확히 일치**로만 본다(위 docstring 의 함정 참고).
# 풀무원식품은 2026-10-02 목록에 안 나왔지만 본체 법인명이라 같이 둔다.
_SUBJECTS = {"풀무원", "풀무원식품", "올가홀푸드"}

# --- 제목 → 상품명 (maker_orion 과 같은 규칙) --------------------------------
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭|런칭)")
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
_TRAIL_SEP = re.compile(r"^\s*[·∙,、/]")
# ⚠️ `_MULTI`(\d+종) 는 **일부러 없앴다.** 이 어댑터는 `N종` 을 버리지 않고
#    꼬리만 턴다(`_COUNT_TAIL`). 상수를 남겨 두면 다음 사람이 되살려서
#    브랜드가 통째로 죽는다 — 이 라운드 최대 결함이 정확히 그거였다.

_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "협약", "체결", "주주총회", "후원", "기부", "추모", "공모", "발대식",
         "심포지엄", "박람회", "팝업", "캠페인", "발탁", "앰배서더", "재단",
         "경연", "시상", "간담회", "개최", "스폰서", "리뉴얼", "실적",
         "매진", "진행", "참가", "참여", "전개", "지원", "프로젝트",
         "오픈", "이벤트", "광고", "조회수", "할인", "신설", "운영", "수주",
         "기획전", "선물세트", "프로모션", "클래스", "멤버십",
         # 국내 출시가 아닌 건 화면에 올리면 거짓이 된다.
         "日", "美", "글로벌", "수출", "해외")

# ⚠️ **주어 화이트리스트로는 못 막는 구멍 — 본체(풀무원)가 내는 펫푸드.** 실측:
#     풀무원, 7세 이상의 반려견 위한 ‘아미오 건강담은 Soft 현미간식’ 출시 (2026-08-25)
#   `아미오` 가 풀무원의 반려동물 먹거리 브랜드다. 주어가 '풀무원' 이라
#   `_SUBJECTS` 를 통과하고, `base.is_nonfood()` 도 사료를 모른다(먹는 것이긴
#   하다 — 실측 False). `_SKIP` 에 넣으면 조용히 사라지는 게 아니라 의도대로
#   버려진다. 네 단어 다 사람 먹는 상품명에 안 쓰여 부분일치 사고가 없다
#   (⚠️ `펫` 한 글자로 줄이지 마라).
_NOT_OUR_LINE = ("아미오", "반려견", "반려묘", "반려동물")

# **본체가 내는 주방 가전.** 먹는 게 아니다. 실측 2건(지금은 `MAX_PAGES` 창
# 밖이지만 새로 나오면 바로 들어온다):
#     프리미엄 다용도 조리 가전 ‘스팀 솔루시온 멀티 오븐’ 출시      (2026-06-10)
#     열풍 노하우 적용한 ‘그린더 에어드라이 음식물 처리기’ 출시     (2026-05-21)
# `base.is_nonfood()` 는 둘 다 모른다(실측 확인). base 의 단어 목록을 늘리는
# 길은 안 간다 — '오븐' 을 부분일치로 넣으면 '오븐구이…' 류 식품이 조용히
# 사라진다(이 레포 2위 결함). 여기서는 **이름의 꼬리 토큰**으로만 보고,
# 버리지 않고 `nonfood=True` 로 표시해 내보낸다(GS25 '손앤박 하티' 와 같은 처리.
# rules.py 가 제조사 브랜드의 nonfood 를 양쪽 목록에서 빼므로 화면엔 안 뜬다).
_APPLIANCE_TAIL = ("오븐", "처리기", "정수기", "밥솥", "식기세척기", "인덕션",
                   "에어프라이어", "레인지")
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱")
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")
_REPACK_HEAD = ("에디션", "라벨")
_REPACK_MID = ("테마", "에디션", "라벨", "컬래버", "콜라보")
_REPACK_NAME = ("에디션", "컬렉션", "한정판", "선물세트", "기획세트", "기획팩")

# 🔴 **`N종` 을 버리지 않고 꼬리만 뗀다.** 오리온 규칙은 `N종` 이 들어간 제목을
# 통째로 버린다(따옴표 안이 상품이 아니라 라인 이름일 수 있어서). 풀무원은
# 따옴표 안이 **온전한 상품명**이라 그 걱정이 없는데, 버리면 진짜 신제품이 죽는다.
# 2026-10-02 실측 — 6페이지 36건 중 본체·올가홀푸드 21건에서 이 규칙에 죽은 것:
#     풀무원, ‘하루에 건강을 더하는 달걀’ 3종 출시…영양 강화 달걀 본격 확대
#     올가홀푸드, 국산 원물 본연의 감칠맛 살린 ‘ORGA 저염 육수’ 2종 출시
# 둘 다 진짜 신제품이고 따옴표 안이 그대로 상품명이다. 사조·면사랑·신세계푸드와
# 같은 판단이다. **따옴표 안만 쓰는 건 그대로 두고** `N종` 꼬리만 턴다.
_COUNT_TAIL = re.compile(r"\s*\d+\s*종\s*$")


def _pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열."""
    t = " ".join(title.split())
    # 본체 기사에 섞인 펫푸드. 주어 화이트리스트로는 못 막는다(위 주석 참고).
    if any(w in t for w in _NOT_OUR_LINE):
        return ""
    if any(w in m.group(1) for m in _HEAD.finditer(t) for w in _REPACK_HEAD):
        return ""
    body = _HEAD.sub(" ", t)
    # ⚠️ `_MULTI`(N종)로 버리지 않는다. 사유는 _COUNT_TAIL 위 주석.
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
    quoted = None
    for m in _SINGLE.finditer(head):
        quoted = m
    if not quoted or any(w in head[quoted.end():] for w in _BETWEEN):
        return ""
    if _TRAIL_SEP.match(head[quoted.end():]):
        return ""
    name = _COUNT_TAIL.sub("", quoted.group(1).strip()).strip(" ,·∙")
    if len(name) < 2 or any(c in name for c in "·∙&?!"):
        return ""
    if any(w in name for w in _REPACK_NAME):
        return ""
    return name


def _subject(title: str) -> str:
    """제목 맨 앞의 주어(회사명). '풀무원, 고압으로…' → '풀무원'."""
    return " ".join(title.split()).split(",", 1)[0].strip()


def _date(s: str) -> str:
    """'2026년 9월 23일' → '2026-09-23'. 이 사이트는 한글 포맷만 쓴다."""
    m = re.search(r"(20\d{2})\s*년\s*(\d{1,2})\s*월\s*(\d{1,2})\s*일", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _rows(html: str) -> list[tuple]:
    """목록 HTML → (날짜, 제목, href, 이미지) 목록."""
    out = []
    for li in HTMLParser(html).css(".fact_list_n01 li"):
        a, tit, dt = li.css_first("a"), li.css_first(".list_tit"), li.css_first(".list_date")
        if not (a and tit):
            continue
        img = li.css_first("img")
        # src 앞뒤에 공백이 붙어 온다. strip 하지 않으면 깨진 URL 이 된다.
        # ⚠️ 파일명에 한글·대괄호가 들어 있다(`…_[사진]th.jpg`). 퍼센트 인코딩
        #    하지 않으면 products.json 에 날글자 URL 이 박힌다(크라운 `_abs_image`
        #    와 같은 처리). 인코딩한 주소로 200 이 오는 걸 실측했다.
        # ⚠️ `data:` 는 담지 않는다 — `base.derive()` 는 `http://` 만 거르므로
        #    여기서 안 막으면 base64 가 그대로 저장된다(크라운 사례).
        src = (img.attributes.get("src") or "").strip() if img else ""
        if src.startswith("data:"):
            src = ""
        out.append((_date(dt.text() if dt else ""),
                    " ".join(tit.text().split()),
                    (a.attributes.get("href") or "").strip(),
                    SITE + quote(src) if src.startswith("/") else src))
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    subjects: set = set()        # 아래 가드의 진단용. 실제로 읽힌 주어들.
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"menu": MENU,
                                                       "pageIndex": page}))
            r.raise_for_status()
            rows = _rows(r.text)

            # 셀렉터가 바뀌면 조용히 0건이 되는 게 제일 나쁘다. 브랜드뉴스는
            # 주 4건씩 쌓이는 게시판이라 1페이지는 반드시 와야 한다.
            if page == 1 and not rows:
                raise ValueError(
                    f"풀무원 브랜드뉴스 1페이지가 비었다. {r.url} → "
                    f"{len(r.content)}B — 목록 셀렉터(.fact_list_n01 li / "
                    f".list_tit / .list_date)가 바뀌었는지 확인하라")
            if not rows:
                break

            for released, title, href, img in rows:
                subjects.add(_subject(title))
                if released and released < floor:
                    continue
                # 계열사 거르기. 키워드 역필터로는 '클린 바디워시' 를 못 막는다.
                if _subject(title) not in _SUBJECTS:
                    continue
                name = _pick(title)
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=re.sub(r"^\s*[^,]{2,10},\s*", "", title),
                    image=img,
                    released_at=released,
                    is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                    # 주방 가전은 먹는 게 아니다. 버리지 않고 표시만 한다.
                    nonfood=name.endswith(_APPLIANCE_TAIL),
                    url=SITE + href if href.startswith("/") else (href or LIST),
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

            fresh = [d for d, *_ in rows if d]
            if fresh and max(fresh) < floor:
                break

    # 날짜 포맷이 바뀌면 전건이 floor 밑으로 떨어져 조용히 0건이 된다.
    # 주어 화이트리스트가 낡아도 같은 모양으로 끝난다. 둘 다 예외가 아니라
    # '조용한 부분수집' 이라 collect.py 의 0건 가드로는 안 잡힌다.
    if not items and not (subjects & _SUBJECTS):
        raise ValueError(
            f"풀무원 브랜드뉴스에서 쓸 수 있는 주어가 하나도 없다. "
            f"읽힌 주어={sorted(subjects)} — 계열사명이 바뀌었는지 "
            f"_SUBJECTS 를 확인하라")
    return items
