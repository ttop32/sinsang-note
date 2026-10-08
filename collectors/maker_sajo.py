"""사조대림 — 사조그룹 '신제품' 전용 페이지에서 신제품과 출시일을 뽑는다.

보도자료 제목을 파싱하는 오리온·삼양 계보가 **아니다.** 사조는 그룹 사이트에
**신제품 전용 게시판**을 따로 두고 제목 형식까지 통일해 둬서, 팔도의 `신제품`
배지와 같은 '브랜드가 직접 켜고 끄는 신호' 로 읽는 쪽이 정확하다.
(보도자료 역필터는 쓸 데가 없다 — 게시판 자체가 신제품만 담는다.)

2차 조사가 "사조대림 — `www` 가 DNS 로는 풀리는데 80·443 둘 다 타임아웃. 대체
도메인을 추측하지 않았다" 로 남긴 구멍이다. 3차가 실측으로 메웠다:
**계열사 도메인(`sajodaerim.co.kr`)이 아니라 그룹 사이트 `www.sajo.co.kr` 이 정답**이고,
거기가 계열사 신제품을 전부 모아 준다. (notes/CANDIDATES-MAKER.md §⑧)

수집 경로. 2026-10-02 실측:
  GET https://www.sajo.co.kr/2026/product/new_product.asp?page=1   200 / 23,725B
    <div class="col_wrap">
     <div>
      <a class="img_area" href="./new_product_view.asp?idx=3800&page=1&searchstr=">
        <img src='https://www.sajo.co.kr/upload_data/board/thumbnail/20260802_TOP.png'></a>
      <div class="img_area_s"><img src="/upload_data/board/thumbnail/nt_ci_dr.png" alt="사조대림"></div>
      <a href="./new_product_view.asp?idx=3800&searchstr=">
        <strong class="img_tit">[사조대림] ‘해표 더 고소한 김’ 2종 출시</strong></a>
      <p class="date">2026.08.03</p>
     </div>
  페이지당 6건, `?page=N`. 2026-10-02 현재 **총 7건**(2페이지).
  썸네일이 **절대 URL(https)** 로 와서 그대로 쓸 수 있다.

**제목 형식이 통일돼 있다 — 이게 이 어댑터의 전부다.**
    [계열사] ‘상품명’ N종 출시          ← 따옴표가 있는 쪽
    [사조대림] 해표 순창궁 태양초 고추장 3종 출시   ← 따옴표가 없기도 하다
따옴표가 있으면 그 안을, 없으면 `[계열사]` 와 동사 사이를 상품명으로 본다.

**⚠️⚠️ 계열사는 `[...]` 제목 접두로 가른다. `img_area_s` 의 `alt` 를 믿지 마라.**
3차 조사 문서가 "계열사를 `alt` 로도 중복 제공한다" 고 적었는데 **틀렸다.**
2026-10-02 실측에서 **첫 행이 어긋난다**:
    제목 `[사조펫] '벤티 케어 오메가3' 신제품 출시`  ↔  alt `사조동아원`
CI 이미지가 밀려 붙은 것으로 보인다. alt 를 믿었으면 **펫푸드가 식품으로 올라간다.**
제목 접두는 7건 전부 정확했다.

**쓰는 계열사 (`_AFFILIATES`).** 그룹에 8개가 섞여 있다:
    사조대림 · 사조오양 · 사조씨푸드 ← ✅ 소비자 식품(어묵·수산가공·햄·간편식)
    사조산업 · 사조원                ← ✅ 축산·수산 원물
    사조동아원                       ← ❌ 제분. B2B 밀가루
    사조푸디스트                     ← ❌ 급식·휴게소. 편의점 상품이 아니다
    사조펫                           ← ❌ 펫푸드. 사람이 먹는 게 아니다
브랜드 이름은 **'사조대림'** 하나로 등록한다. 신제품 게시판 7건 중 6건이
사조대림이고, 나머지 계열사는 붙었다 말았다 해서 따로 칸을 내면 대부분 0건이 된다.

**거르는 것.**
  `[사조대림] ‘한알레시피’ 4종 **리뉴얼** 출시!`   ← 신제품이 아니다
  `[사조펫] …`                                    ← 펫푸드
  `… 선물세트 / 기획전 / 한정 …`                   ← 상품이 아니거나 신상이 아니다

**일괄 등록 흔적 — 없다.** 7건 날짜가 전부 다르다
(09.01 · 08.03 · 07.27 · 07.20 · 07.13 · 07.01 · 06.23). 썸네일 파일명의
`20260802` 도 보도일 08.03 과 하루 차로 맞는다 — 다만 **날짜는 `p.date` 를 쓴다**
(크라운 사례: 파일명 날짜는 재업로드로 덮인다).

## 🔴 2026-10-08 — **SAJO 뉴스 보드를 열었다. 신제품 게시판이 말라붙었다**

원래 이 docstring 은 이렇게 적어 뒀었다:

> **SAJO 뉴스(`/2026/product/sajo_news.asp`, 총 56건)는 쓰지 않는다.**
> 갱신은 더 빠르지만(최신 09.17 vs 신제품 09.01) CSR·안전점검·추석 선물세트·
> 휴게소 신메뉴가 섞여 있어 역필터를 또 얹어야 한다. 신제품 전용 게시판이 이미
> 있는데 그걸 두고 뉴스를 긁는 건 이 프로젝트가 경계하는 쪽이다.
> **신제품 게시판이 말라붙으면 그때 다시 본다.**

**그 조건이 왔다.** 2026-10-08 실측 —

| 보드 | 전체 | 최신 | 최신 **사조대림** 글 | 어댑터 수확 |
|---|---:|---|---|---:|
| 신제품 `new_product.asp` | **7건** (2026-06-23~09-01) | 2026-09-01(사조펫) | **2026-08-03** | 5 |
| SAJO 뉴스 `sajo_news.asp` | **57건** (2026-01-06~10-01) | 2026-10-01 | **2026-09-01** | +6 |

신제품 게시판은 **두 달 넘게 사조대림 글이 없고 전체가 7건**이다. 같은 기간
뉴스 보드에는 캠핑어묵탕·사각어묵·로얄크랩·간장소스·쥐포후라이드·골드 비엔나가
들어와 있다. → **5건 → 11건.** (신세계그룹 뉴스룸으로 신세계푸드를 5→12 로
올린 것과 같은 수법이다.)

### 뉴스 보드 — 마크업은 신제품 게시판과 **같다**

    GET https://www.sajo.co.kr/2026/product/sajo_news.asp?page=N   6건/페이지, 10페이지
    상세 ./sajo_news_view.asp?idx=NNNN
`.col_wrap > div` / `strong.img_tit` / `p.date` / `a.img_area` 가 그대로라
`_rows()` 를 **그대로 재사용**한다. 다른 건 제목 형식과 섞여 있는 것뿐이다.

⚠️ **날짜 내림차순이 아니다.** 실측에서 `04-29 · 04-16 · 04-15 · 04-01 ·
   03-12 · 03-26` 처럼 한 페이지 안에서도 뒤집힌다. **날짜를 보고 일찍 끊으면
   안 된다** — `DAYS` 창 밖은 버리되 페이징은 끝까지 돈다.

### 제목 형식이 다르다 — `[계열사]` 가 아니라 `사조대림,` 이다

신제품 게시판은 `[사조대림] …` 인데 뉴스 보드는 `사조대림, …` 다.
그래서 계열사를 **접두 + 쉼표**로 가른다(`_NEWS_LEAD`). 57건 주어 분포 —

    사조대림 17 · 푸디스트/사조푸디스트 20 · 사조그룹 5 · 취암장학재단 4 ·
    사조씨푸드 2 · 사조 1 · 기타(머리말이 따옴표로 시작하는 기사) 8

⚠️ `푸디스트`(급식·휴게소)는 `_AFFILIATES` 에 없어서 자동으로 빠진다.
   `사조,` 로 시작하는 글 1건은 **사조산업 대표 산업포장 수상** 기사다 —
   `사조` 자체는 계열사 이름이 아니므로 `_AFFILIATES` 에 넣지 않는다.
⚠️ 머리말이 앞에 붙는 기사는 **버린다**(`건강과 맛을 동시에.. 사조대림, 설탕줄인
   붕어빵ㆍ국화빵`). 아는 손실이다 — 주어 위치를 고정해야 남의 기사가 안 섞인다.

### 🔴 뉴스 보드만 보면 **리뉴얼을 신제품으로 읽는다** — 교차검증으로 막았다

    신제품 게시판  `[사조대림] ‘한알레시피’ 4종 **리뉴얼** 출시!`   → _SKIP 이 버린다
    뉴스 보드      `사조대림, ‘해표 한알레시피’ 4종 출시…`          → 버릴 근거가 없다

같은 상품인데 뉴스 보드 제목에는 `리뉴얼` 이라는 말이 없다. 역필터를 아무리
늘려도 못 잡는다. → **신제품 게시판이 `_SKIP` 으로 버린 제목의 따옴표 안 이름을
모아 두고(`_blocked`), 뉴스 보드 상품명이 그걸 품으면 버린다.** 이미 받아 둔
데이터로 하는 교차검증이라 요청이 늘지 않는다.

### 중복 — 같은 상품이 두 보드에서 **다른 이름·다른 날짜**로 온다

    신제품 2026-07-01 `‘쟌슨빌 베다위드체다’ 출시`
    뉴스   2026-07-24 `'쟌슨빌 캔햄 베다위드체다' 출시…`      ← '캔햄' 이 더 붙었다
    신제품 2026-07-13 `‘하우스&펍’ 소시지 3종 출시`
    뉴스   2026-08-07 `육식맨과 협업한 '하우스앤펍' 소시지 3종 출시`  ← & ↔ 앤
뉴스 보드 날짜가 **늘 더 늦다**(2~4주). `make_key` 는 공백만 털어서 이 둘을
못 묶는다. → **토큰 집합 비교**로 묶는다: `&→앤` 으로 맞추고 낱말로 쪼갠 뒤
**첫 낱말이 같고 한쪽이 다른 쪽의 부분집합**이면 같은 상품으로 본다.
'첫 낱말이 같을 것' 을 같이 거는 이유는 한 낱말짜리 이름이 남의 이름 안에
우연히 들어가 엉뚱하게 합쳐지는 것을 막기 위해서다.
**남기는 쪽은 신제품 게시판** — 날짜가 이르고 원래 어댑터가 내보내던 값이다.

### 뉴스 보드 제목은 **마지막** 따옴표를 쓴다 (신제품 게시판과 반대)

신제품 게시판은 `[계열사]` 를 떼면 바로 상품이라 **첫** 따옴표부터 잡는데,
뉴스 보드는 `롯데마트 단독 '캠핑어묵탕' 1만개 한정 출시` 처럼 **앞에 유통·협업
상대가 붙는다.** 첫 따옴표부터 잡으면 그게 상품명에 들어온다. → 마지막
따옴표부터 동사 앞까지를 잡고(`'하우스앤펍' 소시지 3종` → `하우스앤펍 소시지`),
꼬리의 수량·한정 표기를 떼어 낸다(`1만개 한정`·`3종`·`신제품`).

robots: https://www.sajo.co.kr/robots.txt → ⚠️ **판정 불가.** 200 / 3,861B 인데
        `<title>서비스 오류 안내</title>` HTML 이고, 없는 경로(`/zzz-nope-12345`)에도
        **바이트 단위로 같은 응답**을 준다. robots.txt 가 없고 모든 미지정 경로에
        공용 오류 셸을 주는 유형이다(해태 ht.co.kr 과 같다).
약관:   확인하지 않았다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "사조대림"
SITE = "https://www.sajo.co.kr"
LIST = SITE + "/2026/product/new_product.asp"
VIEW = SITE + "/2026/product/new_product_view.asp"
MAX_PAGES = 4        # 한 페이지 6건. 2026-10-02 현재 총 7건(2페이지). 상한.
DELAY = 2.2

# --- SAJO 뉴스 보드. 사유·실측은 docstring 🔴 --------------------------------
NEWS = SITE + "/2026/product/sajo_news.asp"
NEWS_VIEW = SITE + "/2026/product/sajo_news_view.asp"
NEWS_MAX_PAGES = 14   # 6건×14 = 84건. 2026-10-08 현재 57건(10페이지). 상한.
NEWS_DAYS = 300       # 이보다 오래된 기사는 신제품 섹션에 쓸모가 없다.
# 뉴스 보드에서 창 안 '쓰는 계열사' 행 가운데 상품으로 집히는 비율의 상한.
# 2026-10-08 실측 6/17 = 35.3%. 역필터가 풀리면 수상·실적까지 상품이 된다.
NEWS_MAX_PICK_RATIO = 0.70

# 소비자 식품을 내는 계열사만. 제목의 `[...]` 접두로 가른다(alt 는 못 믿는다).
_AFFILIATES = {"사조대림", "사조오양", "사조씨푸드", "사조산업", "사조원"}

_PREFIX = re.compile(r"^\s*\[([^\]]{2,12})\]\s*")
_QUOTED = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_QUOTE_CHARS = re.compile(r"[‘’'`“”\"]")
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭|런칭)")
# 상품명 뒤에 붙는 수량 표기. `2종`·`3종 출시` 의 그 부분이다.
_COUNT_TAIL = re.compile(r"\s*\d+\s*종\s*$")
_NEW_TAIL = re.compile(r"\s*신제품\s*$")

# 신제품 게시판이지만 신상이 아닌 것들이 섞인다.
# ⚠️ 2026-10-03 검수에서 `한정` → `한정판` 으로 **좁혔다.** 두 글자 `한정` 은
#    **`한정식` 을 문다**(`[사조대림] ‘한정식 도시락’ 출시` 로 실증). 사조는
#    어묵·햄·간편식을 내는 한식 제조사라 실제로 물릴 자리다. 이 레포가
#    `카스`→`카스테라` 28건으로 데인 것과 같은 모양이다. 다른 어댑터
#    (maker_orion·maker_cj 의 `_REPACK_NAME`)도 전부 `한정판` 을 쓴다 —
#    그쪽 표기에 맞췄다. 실측 7건에서 `한정` 으로 걸리던 기사는 0건이다.
_SKIP = ("리뉴얼", "선물세트", "기획세트", "기획전", "한정판", "프로모션",
         "이벤트", "캠페인", "에디션")

# --- 뉴스 보드 전용 ----------------------------------------------------------
# 주어는 **접두 + 쉼표**다(`사조대림, …`). 신제품 게시판의 `[사조대림]` 과 다르다.
_NEWS_LEAD = re.compile(r"^\s*(사조[가-힣]{2,6}),\s*")
# 뉴스 보드에만 섞여 있는 비상품 축. `_SKIP` 에 더해 **동사 앞 머리**에서만 본다
# (동사 뒤 꼬리에는 `…프리미엄 캔햄 라인업 확대` 처럼 멀쩡한 기사의 부제가 온다).
_NEWS_SKIP = ("성료", "수상", "선정", "체결", "협약", "MOU", "기부", "나눔",
              "점검", "공모", "개최", "매출", "영업이익", "돌파", "급증",
              "인하", "사명", "모집", "전달", "자리매김", "점유율", "운영",
              "성장", "흑자", "진출", "공급계약", "업무협약", "식품대상")
# 동사 **뒤**가 실적 문구면 그 날짜는 출시일이 아니라 기사 작성일이다.
_NEWS_TAIL = ("돌파", "만에", "만인", "완판", "누적", "기록")
# 상품명 꼬리의 수량·한정 표기. `1만개 한정`·`3종`·`신제품` 을 차례로 턴다.
_NEWS_QTY_TAIL = re.compile(
    r"(\s*\d+\s*종|\s*\d+\s*[만천]?\s*(개|봉|팩|캔|병)?\s*한정|\s*신제품|\s*한정)\s*$")
_NEWS_TOKEN = re.compile(r"[^0-9A-Za-z가-힣]+")


def _pick(title: str) -> str:
    """'[사조대림] ‘해표 더 고소한 김’ 2종 출시' → '해표 더 고소한 김'.

    따옴표가 없는 제목도 있다('[사조대림] 해표 순창궁 태양초 고추장 3종 출시').
    그때는 `[계열사]` 와 동사 사이를 상품명으로 본다.
    """
    t = " ".join(title.split())
    body = _PREFIX.sub("", t)
    if any(w in body for w in _SKIP):
        return ""
    verb = None
    for m in _VERB.finditer(body):
        verb = m
    if not verb:
        return ""
    head = body[:verb.start()]
    # 따옴표 **안**만 쓰면 수식어가 달린 상품명이 깎인다 —
    # `‘하우스&펍’ 소시지 3종 출시` 가 '하우스&펍'(브랜드)로 줄어든다.
    # 그래서 **첫 따옴표부터 동사 앞까지**를 통째로 잡고 따옴표 기호만 턴다.
    # 따옴표가 없으면 머리 전체를 쓴다(`해표 순창궁 태양초 고추장 3종 출시`).
    q = list(_QUOTED.finditer(head))
    seg = head[q[0].start():] if q else head
    name = _QUOTE_CHARS.sub("", seg)
    name = _NEW_TAIL.sub("", _COUNT_TAIL.sub("", name.strip())).strip(" ,·∙!")
    # 따옴표 없는 제목에서 통째로 잡은 머리는 수식어가 길게 붙어 있을 수 있다.
    # 2~40자 밖이면 상품을 특정 못 한 것으로 본다.
    if not (2 <= len(name) <= 40):
        return ""
    return name


def _news_affiliate(title: str) -> str:
    """뉴스 보드 제목의 주어. `사조대림, …` 의 '사조대림'. 없으면 빈 문자열.

    ⚠️ 주어가 **맨 앞**에 있을 때만 받는다. `건강과 맛을 동시에.. 사조대림, …`
       처럼 머리말이 앞에 붙은 기사는 버린다(아는 손실. docstring 참고).
    """
    m = _NEWS_LEAD.match(" ".join(title.split()))
    return m.group(1) if m else ""


def _news_pick(title: str) -> str:
    """뉴스 보드 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열.

    신제품 게시판의 `_pick` 과 두 군데가 다르다(docstring 마지막 절).
      ① **마지막** 따옴표부터 잡는다. 앞에 유통·협업 상대가 붙기 때문이다.
      ② 꼬리의 수량·한정 표기를 떼어 낸다(`1만개 한정`·`3종`).
    """
    t = " ".join(title.split())
    m = _NEWS_LEAD.match(t)
    if not m:
        return ""
    body = t[m.end():]
    verb = None
    for v in _VERB.finditer(body):
        verb = v
    if not verb:
        return ""
    head, tail = body[:verb.start()], body[verb.end():]
    if any(w in head for w in _SKIP) or any(w in head for w in _NEWS_SKIP):
        return ""
    if any(w in tail for w in _NEWS_TAIL):
        return ""
    q = list(_QUOTED.finditer(head))
    seg = head[q[-1].start():] if q else head
    name = _QUOTE_CHARS.sub("", seg).strip()
    # `1만개 한정`·`3종`·`신제품` 이 겹쳐 붙는다. 더 안 떨어질 때까지 턴다.
    for _ in range(4):
        cut = _NEWS_QTY_TAIL.sub("", name).strip(" ,·∙!…")
        if cut == name:
            break
        name = cut
    name = name.strip(" ,·∙!…")
    if not (2 <= len(name) <= 40):
        return ""
    return name


def _blocked_names(rows: list) -> set:
    """신제품 게시판이 `_SKIP` 으로 버린 제목에서 상품명을 모은다.

    뉴스 보드 제목에는 `리뉴얼` 같은 말이 안 붙어서 역필터로는 못 잡는다.
    이미 받아 둔 신제품 게시판 쪽에 그 사실이 적혀 있으니 거기서 가져온다
    (docstring 🔴 '리뉴얼을 신제품으로 읽는다'). 요청이 늘지 않는다.
    """
    out = set()
    for _released, title, *_rest in rows:
        body = _PREFIX.sub("", " ".join(title.split()))
        if not any(w in body for w in _SKIP):
            continue
        for q in _QUOTED.finditer(body):
            n = _norm(q.group(1))
            if len(n) >= 3:
                out.add(n)
    return out


def _norm(name: str) -> str:
    """비교용 정규화. `&` 를 `앤` 으로 맞추고 글자·숫자만 남긴다."""
    return _NEWS_TOKEN.sub("", name.replace("&", "앤")).lower()


def _tokens(name: str) -> list:
    """낱말 목록. `&` 를 `앤` 으로 맞춘다(`하우스&펍` ↔ `하우스앤펍`)."""
    return [w for w in _NEWS_TOKEN.split(name.replace("&", "앤").lower()) if w]


def _same_product(a: str, b: str) -> bool:
    """두 이름이 같은 상품인가. **첫 낱말이 같고 한쪽이 다른 쪽의 부분집합**.

    실측: `쟌슨빌 베다위드체다` ↔ `쟌슨빌 캔햄 베다위드체다`,
          `하우스&펍 소시지` ↔ `하우스앤펍 소시지`.
    '첫 낱말이 같을 것' 을 같이 거는 이유는 한 낱말짜리 이름이 남의 이름 안에
    우연히 들어가 엉뚱하게 합쳐지는 것을 막기 위해서다.
    """
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb or ta[0] != tb[0]:
        return False
    sa, sb = set(ta), set(tb)
    return sa <= sb or sb <= sa


def _affiliate(title: str) -> str:
    """제목 접두의 계열사명. 없으면 빈 문자열."""
    m = _PREFIX.match(" ".join(title.split()))
    return m.group(1).strip() if m else ""


def _date(s: str) -> str:
    """'2026.08.03' → '2026-08-03'. 월·일 범위를 검증한다."""
    m = re.match(r"^\s*(20\d{2})[-.](\d{1,2})[-.](\d{1,2})\s*$", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _rows(html: str) -> list[tuple]:
    """목록 HTML → (날짜, 제목, idx, 이미지) 목록."""
    out = []
    for div in HTMLParser(html).css(".col_wrap > div"):
        tit = div.css_first("strong.img_tit")
        if not tit:
            continue
        dt = div.css_first("p.date")
        a = div.css_first("a.img_area")
        img = a.css_first("img") if a else None
        src = (img.attributes.get("src") or "").strip() if img else ""
        m = re.search(r"idx=(\d+)", (a.attributes.get("href") or "") if a else "")
        out.append((_date(dt.text(strip=True) if dt else ""),
                    " ".join(tit.text().split()),
                    m.group(1) if m else "",
                    src if src.startswith("http") else (SITE + src if src.startswith("/") else "")))
    return out


def _fetch_new_product() -> tuple[list[Item], list]:
    """신제품 전용 게시판. (상품, 읽은 행 전체) 로 돌려준다.

    행 전체를 같이 돌려주는 이유는 뉴스 보드의 '리뉴얼' 교차검증에 쓰기
    때문이다(docstring 🔴). 요청을 다시 보내지 않으려고 여기서 들고 나간다.
    """
    items: list[Item] = []
    seen = set()
    all_rows: list = []
    affiliates: set = set()      # 아래 가드의 진단용. 실제로 읽힌 계열사들.
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"page": page}))
            r.raise_for_status()
            rows = _rows(r.text)

            # 셀렉터가 바뀌면 조용히 0건이 되는 게 제일 나쁘다.
            if page == 1 and not rows:
                raise ValueError(
                    f"사조 신제품 1페이지가 비었다. {r.url} → {len(r.content)}B — "
                    f"목록 셀렉터(.col_wrap > div / strong.img_tit / p.date)가 "
                    f"바뀌었는지 확인하라")
            if not rows:
                break
            all_rows += rows

            for released, title, idx, img in rows:
                aff = _affiliate(title)
                affiliates.add(aff)
                if aff not in _AFFILIATES:
                    continue
                name = _pick(title)
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=_PREFIX.sub("", " ".join(title.split())),
                    image=img,
                    released_at=released,
                    # 신제품 전용 게시판이다. 브랜드가 직접 켜고 끄는 신호다.
                    is_new=True,
                    url=f"{VIEW}?idx={idx}" if idx else LIST,
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

            if len(rows) < 6:        # 마지막 페이지
                break

    # 제목 접두가 사라지면 계열사를 못 가르게 되고, 그러면 전건이 조용히
    # 떨어져 0건이 된다. 펫푸드가 식품으로 올라가는 반대 사고보다 낫지만
    # 둘 다 조용하면 안 된다 — 터뜨린다.
    if not items and not (affiliates & _AFFILIATES):
        raise ValueError(
            f"사조 신제품에서 쓸 수 있는 계열사가 하나도 없다. "
            f"읽힌 계열사={sorted(affiliates)} — 제목의 '[계열사]' 접두 형식이 "
            f"바뀌었는지 확인하라")
    return items, all_rows


def _fetch_news(blocked: set) -> tuple[list[Item], dict]:
    """SAJO 뉴스 보드에서 '쓰는 계열사' 의 출시 기사를 뽑는다. (상품, 진단).

    ⚠️ 날짜가 내림차순이 아니다(docstring). 창 밖이라고 페이징을 끊지 않는다.
    """
    floor = (date.today() - timedelta(days=NEWS_DAYS)).isoformat()
    items: list[Item] = []
    rows_seen = 0
    ours = 0                      # 창 안 '쓰는 계열사' 행 수
    subjects: set = set()         # 가드 진단용
    with base.client() as c:
        for page in range(1, NEWS_MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(NEWS, params={"page": page}))
            r.raise_for_status()
            rows = _rows(r.text)
            if page == 1 and not rows:
                raise ValueError(
                    f"SAJO 뉴스 1페이지가 비었다. {r.url} → {len(r.content)}B — "
                    f"목록 셀렉터(.col_wrap > div / strong.img_tit / p.date)가 "
                    f"바뀌었는지 확인하라")
            if not rows:
                break
            rows_seen += len(rows)

            for released, title, idx, img in rows:
                aff = _news_affiliate(title)
                if aff:
                    subjects.add(aff)
                # 날짜 없는 is_new=True 는 90일 동안 화면에 눌러앉는다.
                if not released or released < floor:
                    continue
                if aff not in _AFFILIATES:
                    continue
                ours += 1
                name = _news_pick(title)
                if not name:
                    continue
                # 신제품 게시판이 '리뉴얼' 로 버린 상품이면 여기서도 버린다.
                norm = _norm(name)
                if any(b in norm for b in blocked):
                    continue
                items.append(Item(
                    brand=BRAND,
                    name=name,
                    desc=_NEWS_LEAD.sub("", " ".join(title.split())),
                    image=img,
                    released_at=released,
                    is_new=True,      # 브랜드가 '출시' 라고 낸 기사다
                    url=f"{NEWS_VIEW}?idx={idx}" if idx else NEWS,
                ))

            if len(rows) < 6:        # 마지막 페이지
                break

    return items, {"rows": rows_seen, "ours": ours, "subjects": subjects}


def fetch() -> list[Item]:
    """신제품 게시판을 먼저 돌리고 SAJO 뉴스 보드를 뒤에 더한다.

    순서에 뜻이 있다 — 두 보드가 같은 상품에 **다른 이름·다른 날짜**를 붙이고
    (실측 2~4주 차), 신제품 게시판 쪽이 이르고 짧다. 먼저 넣은 쪽을 남긴다.
    """
    items, prod_rows = _fetch_new_product()
    own = len(items)

    extra, diag = _fetch_news(_blocked_names(prod_rows))
    for it in extra:
        # `make_key` 는 공백만 턴다. `하우스&펍` ↔ `하우스앤펍`,
        # `쟌슨빌 베다위드체다` ↔ `쟌슨빌 캔햄 베다위드체다` 를 못 묶는다.
        if any(_same_product(it.name, x.name) for x in items):
            continue
        if it.key in {x.key for x in items}:
            continue
        items.append(it)

    # --- 뉴스 보드 가드 -----------------------------------------------------
    # ① 주어 형식이 바뀌면 전건이 조용히 떨어져 보강분이 0 이 된다.
    if not diag["ours"]:
        raise ValueError(
            f"SAJO 뉴스에서 쓸 수 있는 계열사 행이 0건이다(읽은 행 "
            f"{diag['rows']}). 읽힌 주어={sorted(diag['subjects'])} — 제목의 "
            f"'<계열사>,' 접두 형식이 바뀌었는지 확인하라 "
            f"(2026-10-08 실측 57행 중 사조대림 17행)")
    # ② 반대쪽. 역필터가 풀리면 수상·실적·급식 기사까지 상품이 된다.
    ratio = len(extra) / diag["ours"]
    if ratio > NEWS_MAX_PICK_RATIO:
        raise ValueError(
            f"SAJO 뉴스: 쓰는 계열사 {diag['ours']}행 중 {len(extra)}건"
            f"({ratio:.0%})이 상품으로 집혔다 — 기대 "
            f"{NEWS_MAX_PICK_RATIO:.0%} 이하(2026-10-08 실측 6/17=35%). "
            f"_NEWS_SKIP 이 풀렸는지 확인하라")
    # ③ 보강이 통째로 죽으면 원래 5건만 남는데 그건 '정상'처럼 보인다.
    if len(items) <= own:
        raise ValueError(
            f"사조대림: 뉴스 보드가 보탠 상품이 0건이다(신제품 게시판 {own}건 "
            f"그대로). 계열사 행 {diag['ours']}건은 읽혔다 — _news_pick 이 "
            f"전부 버렸는지 확인하라 (2026-10-08 실측 보강 후 11건)")
    return items
