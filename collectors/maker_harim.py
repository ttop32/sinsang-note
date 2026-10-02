"""하림 · 하림산업 — 보도자료에서 신제품과 출시일을 뽑는다. 브랜드 둘, 소스 둘.

**1차 조사의 "robots 전면차단" 제외를 뒤집는다.**
`notes/CANDIDATES-MAKER.md` §0 은 하림을 **광동제약·이마트·갤러리아와 함께
"robots 전면차단 4곳"** 으로 묶고 §끝 표에 **"다시 뒤지지 말 것"** 이라고 적었다.
robots 자체는 그 판정이 맞다(아래 robots 원문). 그런데 **운영자 승인으로 robots
제약을 무시하는 이번 조사 기준에서는 보도자료 게시판이 그냥 열린다** — SSR 이고
날짜·제목·요약·썸네일이 전부 목록에 있다. 오늘 같은 사유로 접혀 있던 농심·
CJ제일제당이 둘 다 열린 것과 같은 칸이다.

브랜드를 둘로 나눈다. **같은 '하림' 이름을 쓰지만 법인도 사이트도 다르다.**
  · **하림**     (주)하림 — 닭고기·육가공. `harim.com` 보도자료 게시판
  · **하림산업** 하림산업(주) — 더미식·푸디버디·맥시칸(라면·밥·만두·소스).
                 `harimholdings.com` 뉴스룸 검색
`collectors/snack_gimgane.py` 의 `BRANDS = [...]` 꼴을 따랐다.

────────────────────────────────────────────────────────────────────────
## 소스 ① 하림 — `https://www.harim.com/main/?menu=52` (보도자료)

2026-10-02 실측. 그누보드가 아니라 자체 PHP. 목록 한 건의 마크업:

    <ul class="list" id="list">
      <li><a href="./?menu=52&amp;mode=view&amp;no=3076" title="… 내용 보기">
        <div class="img_box">
          <img src="../data/upload/thumbnail_20260929141354_50965.png" alt="… 섬네일 파일" />
        </div>
        <div>
          <p class="date">최신뉴스 <span>2026-09-29</span></p>
          <p class="tit">하림 ‘수비드 닭가슴살’로 챙기는 든든한 단백질 식단 제안</p>
          <p class="txt">“일교차 큰 9월 환절기, …”</p>
        </div>
      </a></li>

목록 하나에 **날짜·제목·요약·썸네일이 다 있다.** 상세를 받을 이유가 없어서
안 받는다(오리온은 목록 제목이 40자에서 잘려 상세를 받아야 했는데, 여기는
`p.tit` 이 온전하다 — 81건 전수로 `title=` 속성과 대조해 일치를 확인했다).
`p.txt` 가 부제라서 그대로 `desc` 로 쓴다.

⚠️ **`?menu=52` 를 루트에 붙이면 안 된다.** `https://www.harim.com/?menu=52` 는
   **301 로 `/main/` 에 보내면서 쿼리를 버린다.** 그래서 홈(112,883B)이 그대로
   오고, 홈에도 'NEWS ROOM' 블록에 최신뉴스 3건이 박혀 있어서 **파싱이 성공한
   것처럼 보인다.** 정본은 `/main/?menu=52` 다.
⚠️ **페이지 파라미터는 `page` 가 아니라 `pno` 다.** `page=2..6` 을 보내도
   **6페이지가 전부 같은 131,335바이트**로 왔다(md5 동일). 에러가 아니라
   1페이지를 조용히 반복한다 — `notes/CANDIDATES-MAKER.md` §"틀린 파라미터가
   에러 대신 빈 결과를 준다"(대상 `b_id=news`)와 같은 함정인데, 여기는
   **빈 결과가 아니라 '같은 결과'** 라서 더 안 보인다. 9건 × 61페이지다.

**날짜 — 일괄 등록 흔적 없음.** 9페이지 81건(2026-03-09 ~ 2026-09-29)을
전수로 세었다. 같은 날 2건 이상이 11쌍 있는데 최대가 5건(2026-07-09·2026-06-23)
이고 그 5건은 **내용이 서로 다른 별개 기사**다(삼계탕 나눔·지속가능경영보고서
발간·채용·쿠팡 선론칭·배민 선론칭). 롯데칠성·롯데웰푸드가 쓰는 '같은 날 4건이면
일괄' 임계에 형식상 걸리지만 **본문이 다 달라서 일괄 재등록이 아니다.**
보도자료를 몰아서 올리는 날이 있을 뿐이고 날짜 자체는 보도일과 맞는다.

**출시 밀도.** 81건 중 제목에 `출시|론칭|선봬|선보` 가 든 게 17건이다.
나머지는 봉사단·헌혈·기부·협약·증설·발대식·채용·ESG 다.

────────────────────────────────────────────────────────────────────────
## 소스 ② 하림산업 — `harimholdings.com` 뉴스룸 **검색**

하림산업 자체 사이트(`harim-foods.com`)도 보도자료 게시판이 있다
(`/bbs/board.php?bo_table=bo1`, 그누보드). **쓰지 않는다 — 죽어 있다.**
2026-10-02 실측으로 전수를 받아 보니 **최신 글이 2025-11-06** 이고
그 아래가 2025-02-17 ×6 · 2024-07-09 ×5 · 2023-05-08 ×8 처럼 **일괄 등록
덩어리**다. 11개월째 멈춘 게시판이라 DAYS 창에 한 건도 안 들어온다.
(robots 는 `User-agent: * / Allow:/` 로 깨끗하다. 막혀서 안 쓰는 게 아니다.)

살아 있는 채널은 **지주사 뉴스룸**이다. 2026-10-02 실측:

    POST/GET https://harimholdings.com/kr/sub/newsroom/search_result.asp
             ?s_keyword=하림산업&s_type=NEWS
    → 200 / 67,086B / 한 번에 전부 온다(**페이징이 없다**)

    <section class="search-result" id="NEWS_LIST">
      …
      <tr>
        <td><a href="./news_view.asp?b_idx=<64자 hex>&s_keyword=하림산업"
               class="title">[하림산업] '오리지널 치킨스톡' 출시</a></td>
        <td><span class="date">2026.08.18</span></td>
      </tr>

**제목 앞에 `[회사명]` 태그가 붙는다 — 주어 화이트리스트가 공짜로 생긴다.**
`maker_pulmuone.py` 의 `_SUBJECTS` 가 풀려는 문제를 이 사이트는 스스로 풀어
준다. 지주사 피드는 계열이 심하게 섞이는데(`[팬오션]` 해운 · `[선진]`·
`[팜스코]`·`[천하제일사료]` 축산/사료 · `[NS홈쇼핑]` 홈쇼핑 ·
`[홈플러스 익스프레스]` 유통), 태그가 정확히 일치할 때만 받으면 다 걸러진다.
⚠️ **`"하림" in title` 로 쓰면 안 된다.** `[하림]`·`[하림산업]`·`[하림그룹]`·
   `하림푸드` 가 전부 통과하고, 본문에 '하림' 이 들어간 `[선진]` 기사까지 샌다.
   `_TAG` 로 **대괄호 태그만** 뽑아 정확히 일치로 본다.

⚠️ **목록 134행 중 56행만 뉴스다.** 검색 결과는 `이슈 & 뉴스(56)` 와
   `미디어 포커스(78)` 를 **한 페이지에 두 섹션으로** 싣는다. `s_type=NEWS` 를
   붙여도 **134행이 그대로 온다**(탭은 JS 로 숨길 뿐이다). 미디어 포커스는
   외부 언론 기사(`[르포] …`·`'닭 회사' 하림 가보니…`)라 태그가 없고 상품도
   아니다. 그래서 **`#NEWS_LIST` 섹션 안에서만** 행을 읽는다. 섹션을 안 잡고
   `css('tr')` 로 긁으면 78건의 남의 기사가 같이 들어온다.

⚠️ **검색 결과는 날짜순이 아니라 적합도순이다.** 첫 세 줄이 2026.09.04 →
   2026.03.24 → 2025.09.01 이다. **중간에 끊으면 안 된다** — 전부 읽고
   날짜로 거른다(어차피 한 요청이라 비용이 같다).

⚠️ **상세 페이지를 받지 않는다. 사진을 못 쓴다.** `news_view.asp` 는
   **1,082,000바이트(1MB)** 이고, 그 대부분이 **본문 사진 하나를 통째로
   `data:` URI(base64 1,051,042자)로 인라인**한 것이다. `<img src>` 중
   URL 로 된 건 로고·공유아이콘·화살표 같은 UI 뿐이고 **상품 사진의 URL 이
   없다.** `Item.image` 에 `data:` 를 넣으면 `rules.verify_images()` 가
   HTTP 로 받아 볼 수 없고 JSON 만 1MB씩 부푼다. → **하림산업 항목은
   `image=""` 로 둔다.** 제목·날짜는 목록에 이미 다 있으므로 1MB 짜리
   상세를 1건당 한 번씩 받을 이유가 전혀 없다.
   (`CRAWLING-POLICY.md` 가 경고한 '10MB 넘는 페이지' 와 같은 축이다.)

**날짜 — 일괄 등록 흔적 없음.** `#NEWS_LIST` 56건의 날짜가 2019-03-04 ~
2026-09-30 에 고르게 흩어져 있고 **같은 날 2건이 한 쌍도 없다.**

────────────────────────────────────────────────────────────────────────
## 조인 규칙 — `maker_orion.py` 계보 그대로 + 하림 보강

`_pick()` 은 오리온 것을 가져왔고(`maker_ottogi`·`maker_pulmuone`·
`maker_spcsamlip` 과 같은 계보), 하림에서 실측한 것만 보탰다.

보탠 것은 **`_SKIP` 단어 몇 개뿐**이다. 새 규칙을 만들지 않았다.
  · `입점`·`판매처`·`확대` — `'별미요리' 3종 GS더프레시에 입점하며 판매처 확대`
  · `모집`·`위촉`·`해단식`·`견학`·`인증`·`증설`·`기공식`·`리모델링`
  · `이벤트`·`챌린지`·`온에어`·`자리매김`·`1위`·`나눔`·`전달`
  · `공급`·`가격` — `닭고기 가격 상승은 AI에 따른 공급 부족 때문`(시황 해명)
계열 축 역필터도 넣었다(`_NOT_OUR_LINE`). 과제 지시에 나온 두 축이다.
  · **펫푸드** — 하림펫푸드(`밥이보약`·`더리얼`). 사람이 먹는 게 아니다.
  · **부동산** — `양재도시첨단물류단지`. 지주사 피드 내비에 실제로 있다.
  두 축 다 지금 창(DAYS=300)에는 안 보이지만, 보이면 바로 들어오는 자리다.
  `base.is_nonfood()` 는 '밥이보약' 을 모른다 — 이름에 비식품 단어가 없다.

**버리는 진짜 신제품 — `N종` 이 제일 크다. 아는 손실이다.**
하림은 제목에 `N종` 을 유난히 자주 쓴다. 두 소스 137건 전수로 세면
`N종` 때문에 버려지는 **진짜 출시 기사가 11건**이다:
    '냄비요리' 신제품 2종 · 신제품 '중화 닭요리' 4종 · '별미요리' 2종 ·
    '소스닭가슴살' 3종 · 닭가슴살 햄 '챔' 신제품 4종 · 신제품 '오븐구이' 3종 ·
    '직화 불맛포차 시리즈' 4종 · '찹스테이크' 2종 · 신제품 '직화 닭가슴살' 3종 ·
    맥시칸 '저당 소스' 4종 · 푸디버디 '리틀죽' 3종 · '육즙핫도그' 2종
`_MULTI` 는 `maker_orion`·`maker_pulmuone`·`maker_spcsamlip` 이 전부 쓰는
계보 규칙이고, 그 셋이 모두 docstring 에 같은 손실을 적어 두었다
(풀무원 `‘ORGA 저염 육수’ 2종` · 삼립 `‘탕종 또띠아 3종’`). **여기서만
규칙을 바꾸면 레포 안에서 브랜드마다 기준이 달라진다.** 계보를 따르고
손실을 적어 둔다. ⚠️ 운영자에게: `N종` 을 살릴지는 **레포 전체**에서 한 번에
정할 문제다(살린다면 '따옴표 안을 라인명으로 등록' 이 되므로 이름의 뜻이 바뀐다).
그 밖에 버리는 것:
  · `소용량 ‘구워먹는 닭’ 배민B마트에서 선론칭 진행` — `진행`(채널 한정 선출시)
  · `신제품 ‘쯔란 봉 양념구이’ GS더프레시에서 판매` — 동사가 `판매`라 `_VERB` 밖
  · `‘2026 추석 선물세트’ 출시`·`가정의 달 선물세트 출시` — 선물세트(`_REPACK_NAME`)
  · `냉동 국물요리 7종 패키지 리뉴얼 출시` — `리뉴얼`

────────────────────────────────────────────────────────────────────────
## robots / 약관

**`https://www.harim.com/robots.txt` → 200, 41바이트, text/plain. 원문 전체:**
    User-agent: *
    Disallow: /
    Allow: /main/
⚠️ **`Disallow: /` 가 먼저이고 `Allow: /main/` 이 뒤에 온다.** 1차가
"전면차단"이라 읽은 근거다. 다만 가장 긴 일치 규칙을 우선하는 해석에서는
**우리가 쓰는 `/main/?menu=52` 는 `Allow: /main/` 에 걸려 허용**이고,
썸네일 `/data/upload/...` 는 `Disallow: /` 쪽이다.
**이번 조사는 운영자 승인으로 robots 제약을 무시한다.** `Crawl-delay` 선언은
없다. 그래도 `DELAY=2.2` 를 지킨다. UA 는 `base.UA` 그대로(위장 없음).

**`https://harimholdings.com/robots.txt` → 200, 6,656바이트.** 주석까지 붙은
긴 파일이다. 머리말 원문:
    # 하림지주 robots.txt
    # 정책(2026-07 AI 검색 최적화 No.07):
    #   1) 주요 AI 크롤러(학습용+검색용) 공개 페이지 전면 허용
    #   2) 관리자·백엔드(/site/), 업로드(/upload/)는 수집 차단
    #   3) 악성/스크래퍼 봇 전면 차단
`GPTBot`·`OAI-SearchBot`·`PerplexityBot`·`Google-Extended` 등을 명시 허용하고
`/site/`·`/upload/` 만 막는다. 우리가 쓰는 `/kr/sub/newsroom/` 은 금지 밖이다.
(상품 사진이 `data:` URI 라 `/upload/` 를 요청할 일 자체가 없다.)

**`https://harim-foods.com/robots.txt` → 200, 58바이트** (쓰지 않는 사이트):
    User-agent: *
    Allow:/

    User-agent: SemrushBot
    Disallow: /
약관: 세 사이트 모두 이용약관 문서를 찾지 못했다. 푸터에 개인정보처리방침만 있다.

## 도메인 함정 (다음 사람이 또 치지 않게)
추측으로 친 도메인은 전부 빈손이었다 — `themeesik.com`·`themiesik.com`·
`harimsanup.com`·`thezipsik.com`·`thesik.co.kr`·`harimfood.co.kr` **전부
NXDOMAIN**, `harimfood.com` 은 **인증서 Hostname mismatch**.
정답은 `harim.com`(하림) / `harim-foods.com`(하림산업, 죽은 게시판) /
`harimholdings.com`(지주, 살아 있는 피드) 셋이다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRANDS = ["하림", "하림산업"]

SITE = "https://www.harim.com"
LIST = SITE + "/main/?menu=52"                 # 보도자료. ⚠️ 루트에 붙이면 쿼리가 날아간다
HOLD = "https://harimholdings.com"
SEARCH = HOLD + "/kr/sub/newsroom/search_result.asp"
VIEW = HOLD + "/kr/sub/newsroom/"              # news_view.asp 는 1MB 라 받지 않는다

MAX_PAGES = 9        # 한 페이지 9건(전체 61페이지). 9×9=81건 ≈ 7개월. 폭주 방지 상한.
DAYS = 300
DELAY = 2.2

# 지주사 피드에서 받을 주어. 대괄호 태그와 **정확히 일치**할 때만 받는다.
# `[하림]` 은 소스 ① 과 겹치므로 여기서는 받지 않는다(중복은 Item.key 로도 걸리지만,
# 소스 ① 쪽이 요약·사진까지 있어 그쪽을 정본으로 둔다).
_TAG = re.compile(r"^\s*\[([^\]]{1,20})\]\s*")
_HOLD_SUBJECTS = {"하림산업"}

# 제목 앞머리의 주어. 상품명이 아니라 회사 이름이라 desc 에서 떼어 낸다.
_LEAD = re.compile(r"^\s*하림(산업|그룹|푸드)?\s*[,·]\s*")

# --- 제목 → 상품명 (maker_orion 계보 그대로) ----------------------------------
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
         # --- 하림 보강 (두 소스 137건 전수로 뽑았다) ---
         "입점", "판매처", "확대", "모집", "위촉", "해단식", "견학", "인증",
         "증설", "기공식", "리모델링", "이벤트", "챌린지", "온에어",
         "자리매김", "1위", "나눔", "전달", "공급", "가격", "협력", "상생",
         # 국내 출시가 아닌 건 화면에 올리면 거짓이 된다(크라운·삼립과 같은 축).
         "日", "美", "글로벌", "수출", "해외", "진출")
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱")
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")
_REPACK_HEAD = ("에디션", "라벨")
_REPACK_MID = ("테마", "에디션", "라벨", "컬래버", "콜라보")
_REPACK_NAME = ("에디션", "컬렉션", "한정판", "선물세트", "기획팩", "시리즈")

# 계열 축. 하림 이름을 달고 나오지만 이 서비스의 축이 아니다.
# 펫푸드는 base.is_nonfood() 가 '밥이보약'·'더리얼' 을 모른다 — 이름만으론 못 막는다.
_NOT_OUR_LINE = ("펫푸드", "반려", "밥이보약", "더리얼", "강아지", "고양이",
                 "물류단지", "양재", "부동산", "사료", "양돈", "종계", "부화장")


def _pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열."""
    t = " ".join(title.split())
    if any(w in t for w in _NOT_OUR_LINE):
        return ""
    # “…” 홍보 헤드라인 안에 에디션/라벨이 있으면 기존 제품의 패키지 기사다.
    if any(w in m.group(1) for m in _HEAD.finditer(t) for w in _REPACK_HEAD):
        return ""
    body = _HEAD.sub(" ", t)          # “…” 는 홍보 헤드라인이다
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
    if any(w in name for w in _REPACK_NAME):
        return ""
    return name


def _date(s: str) -> str:
    """'2026-09-29' / '2026.08.18' → '2026-09-29'. 월·일 범위를 검증한다."""
    m = re.search(r"(20\d{2})[-.](\d{1,2})[-.](\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _harim(c, floor: str, rows: list) -> list:
    """소스 ① (주)하림 보도자료. 목록에 날짜·제목·요약·썸네일이 다 있다."""
    items, stop = [], False
    for page in range(1, MAX_PAGES + 1):
        if page > 1:
            time.sleep(DELAY)
        # ⚠️ 페이지 파라미터는 pno 다. page 를 보내면 1페이지를 조용히 반복한다.
        r = base.retry(lambda: c.get(LIST, params={"pno": page}))
        r.raise_for_status()
        found = 0
        for a in HTMLParser(r.text).css("ul.list li a"):
            href = a.attributes.get("href", "")
            if "mode=view" not in href:
                continue
            found += 1
            dt = a.css_first("p.date span")
            tit = a.css_first("p.tit")
            if not tit:
                continue
            released = _date(dt.text()) if dt else ""
            title = " ".join(tit.text().split())
            rows.append(title)                 # 아래 가드가 쓸 진단용
            if released and released < floor:
                stop = True
                continue
            name = _pick(title)
            if not name:
                continue
            img = a.css_first(".img_box img")
            src = img.attributes.get("src", "") if img else ""
            txt = a.css_first("p.txt")
            items.append(Item(
                brand="하림",
                name=name,
                desc=_LEAD.sub("", " ".join(txt.text().split())) if txt else "",
                # 목록은 /main/ 기준 상대경로(../data/upload/…)다.
                image=SITE + "/" + src.lstrip("./") if src else "",
                category="냉동식품",
                released_at=released,
                is_new=True,                   # 브랜드가 '출시'라고 낸 기사다
                url=SITE + "/main/" + href.lstrip("./"),
            ))
        if not found or stop:
            break
    return items


def _sanup(c, floor: str, rows: list) -> list:
    """소스 ② 하림산업. 지주사 뉴스룸 검색 한 방으로 전부 온다(페이징 없음)."""
    r = base.retry(lambda: c.get(SEARCH, params={"s_keyword": "하림산업",
                                                 "s_type": "NEWS"}))
    r.raise_for_status()
    # ⚠️ 섹션을 잡아야 한다. 통째로 tr 을 긁으면 '미디어 포커스' 78건이 섞인다.
    sec = HTMLParser(r.text).css_first("#NEWS_LIST")
    if sec is None:
        raise ValueError(
            "하림산업: 검색 결과에서 #NEWS_LIST 섹션을 못 찾았다. "
            "마크업이 바뀌었는지 확인하라 — 이 섹션을 안 잡으면 "
            "'미디어 포커스'(외부 언론 기사)가 상품으로 올라간다")
    items = []
    for tr in sec.css("tr"):
        a = tr.css_first("a.title")
        if a is None:
            continue
        title = " ".join(a.text().split())
        rows.append(title)
        tag = _TAG.match(title)
        # 대괄호 태그가 정확히 일치할 때만 받는다('하림' 부분일치 금지).
        if not tag or tag.group(1).strip() not in _HOLD_SUBJECTS:
            continue
        dt = tr.css_first("span.date")
        released = _date(dt.text()) if dt else ""
        # ⚠️ 적합도순이라 중간에 break 하면 안 된다. 끝까지 읽고 날짜로 거른다.
        if released and released < floor:
            continue
        body = _TAG.sub("", title)
        name = _pick(body)
        if not name:
            continue
        items.append(Item(
            brand="하림산업",
            name=name,
            desc=_LEAD.sub("", body),
            # 상세의 상품 사진이 1MB base64 data: URI 라 URL 이 없다. 비워 둔다.
            image="",
            category="냉동식품",
            released_at=released,
            is_new=True,
            url=VIEW + a.attributes.get("href", "").lstrip("./"),
        ))
    return items


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    seen_a: list = []       # 소스 ① 이 읽은 제목 전부. 아래 가드의 진단용.
    seen_b: list = []       # 소스 ② 쪽
    items: list[Item] = []
    keys = set()
    with base.client(timeout=40) as c:
        got_a = _harim(c, floor, seen_a)
        time.sleep(DELAY)
        got_b = _sanup(c, floor, seen_b)

    # 두 소스 중 하나가 통째로 죽으면 조용히 반쪽만 올라간다. 그게 이 레포가
    # 가장 여러 번 데인 모양이라(maker_paldo·maker_nongshim·maker_sajo 끝의 가드)
    # **목록 자체가 비는 것**을 고장으로 읽는다. 상품 0건은 고장이 아니다 —
    # 출시 기사가 한동안 없을 수는 있다. 그래서 '제목 0건' 만 터뜨린다.
    if not seen_a:
        raise ValueError(
            f"하림: {LIST} 목록에서 제목을 한 건도 못 읽었다. "
            "셀렉터(ul.list li a / p.tit)나 pno 파라미터가 바뀌었는지 확인하라")
    if not seen_b:
        raise ValueError(
            "하림산업: 지주사 뉴스룸 검색에서 제목을 한 건도 못 읽었다. "
            f"{SEARCH}?s_keyword=하림산업&s_type=NEWS 의 #NEWS_LIST 를 확인하라")
    # 태그가 통째로 사라지면(마크업 변경) 하림산업이 조용히 0건이 된다.
    if not any(_TAG.match(t) for t in seen_b):
        raise ValueError(
            f"하림산업: 검색 결과 {len(seen_b)}건 중 '[회사명]' 태그가 0건이다. "
            "태그로 계열사를 가르고 있으므로 태그가 없어지면 가를 수가 없다 — "
            "제목 표기가 바뀌었는지 확인하라")

    for it in got_a + got_b:
        if it.key not in keys:
            keys.add(it.key)
            items.append(it)
    return items
