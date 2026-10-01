"""동서식품 — 보도자료에서 신제품과 출시일을 뽑는다.

오뚜기·오리온·GS25 와 같은 종류의 소스다. 그 셋의 규칙을 가져와 동서식품 제목
버릇에 맞게 조인다. 상품 카탈로그를 훑는 어댑터가 아니다 — 왜 아닌지는 아래
'보지 않은 것이 아니라, 보고 안 쓴 것' 에 적었다.

수집 경로. 2026-10-01 실측:
  - 목록 화면 `/mediaCenter/news/list/1` 은 jQuery 가 그리는 껍데기다. 기사 0건이
    들어 있다(`'크리치오' in html` → False). 상세 `/mediaCenter/news/info/2685` 도
    같다. **200 이 떨어진다고 내용이 있는 게 아니다.**
  - 그 화면의 `newsFunc.js` 가 부르는 JSON 이 `POST /api/news/listData/{page}` 다.
    쿠키·토큰·CSRF 가 없고 빈 바디 `{}` 로 그냥 열린다. **GET 이 아니라 POST 다.**
  - 한 페이지 10건 고정이다. `recordCountPerPage`·`pageSize` 를 바디로 넘겨도
    서버가 무시한다(둘 다 실측, 응답 `recordCountPerPage` 가 10 그대로). 그래서
    300일 창에 4~5회 요청이 든다.
  - 상세 주소와 썸네일 주소도 같은 JS 에 있다:
      `location.href = "/mediaCenter/news/info/" + news_idx`
      `'<img src="/common/imageShow/' + thumbImgInfo[0].fileId + '">'`
    썸네일은 `lstAtchFileVO` 중 `fileKnd == "thumbImg"` 인 항목의 `fileId` 다.

⚠️ **제목 필드는 `sj` 다. `nttSj` 가 아니다.** 2026-10-01 재실측:

    cn · cnHtml · fileGroupId · firstIndex · idx · isShow · isTop · lstAtchFileVO ·
    pageSize · rank · recordCountPerPage · regDt · regId · regIp · showDt · sj · viewCnt

`'nttSj' in rows[0]` → False, `'sj' in rows[0]` → True 로 직접 찍어 확인했다.
조사 문서 초판이 `nttSj` 로 적었다가 검수에서 정정된 자리다(notes/QA-REPORT.md §13).
틀린 키는 `.get()` 이 `None` 을 돌려주므로 **예외 없이 조용히 0건**이 된다.
그래서 아래 fetch() 가 1페이지에서 `sj` 키의 존재 자체를 검사하고 없으면 터뜨린다.

**날짜는 `regDt` 가 아니라 `showDt` 를 쓴다 — 조사 문서와 다르다.**
조사 문서는 `regDt` 가 분 단위라는 점을 가치로 적었는데, 80건을 받아 세 보니
`regDt` 는 **일괄 재등록 흔적이 있는 등록 시각**이다:

    regDt 2025-05-28 14:04~14:14 에 7건이 몰려 있고, 그 7건의 showDt 는
    2025-04-23 ~ 2025-05-26 로 **33일에 걸쳐 흩어진다.**
    regDt 2025-03-20 16:11~16:16 에도 3건(showDt 03-11·03-14·03-20).
    80건 중 15건에서 regDt 날짜 ≠ showDt. 서로 다른 날짜 수는 regDt 67 / showDt 79.

GS25 의 `regDttm` 과 똑같은 모양이다(collectors/gs25.py docstring). 게다가
**사이트가 화면에 찍는 날짜도 `showDt`** 다 — `newsFunc.js` 가 목록·상세 세 군데서
전부 `newsInfo.showDt.replace(/-/g, '.')` 를 쓴다. `Item.released_at` 은 어차피
YYYY-MM-DD 라 분 단위에서 얻는 게 없다. `showDt` 가 비면 `regDt` 날짜로 떨어진다.

목록 정렬도 `showDt` 내림차순이다(80건 전수에서 완전 내림차순, `regDt` 는 아님).
그래도 GS25 처럼 **페이지에서 가장 새 기사까지 기준일보다 오래됐을 때만** 멈춘다.

신제품 판정 근거는 배지가 아니라 **기사 자체**다. 브랜드가 '출시'라고 낸 기사라서
is_new=True 로 둔다(오뚜기·오리온·GS25 와 같은 근거).

2026-10-01 에 80건(8페이지)을 받아 제목을 전수로 눈으로 훑고 조인 규칙을 맞췄다.
동서식품 제목에서 확인한 함정:
  ① **홍보 헤드라인이 따옴표 없이 회사명 앞에 붙는다.**
     "크래커로 즐기는 색다른 타코의 맛 동서식품, 신제품 '리츠 크래커 멕시칸 타코맛' 출시"
     "세 겹으로 한층 더 바삭한 … 동서식품, 신제품 '포스트 크리치오 쿠키' 출시"
     쌍따옴표 헤드라인도 있다("물보다 맛있는 한 잔" 동서식품, …). GS25 와 같은
     대응을 쓴다 — 회사명 앞은 통째로 버린다(_BRAND_TOKEN).
  ② **기존 제품의 한정판·에디션 포장 기사**가 '출시' 정필터를 통과한다. 실측 2건:
       "동서식품, '컬러 오브 맥심' 한정판 패키지 출시"   (맥심은 1980년대 제품)
       "동서식품, '오레오 마인크래프트 무비 에디션' 한정판 출시"
     _BETWEEN 에 '한정판' 한 단어를 더해 둘 다 잡았다(빼고 돌리면 둘 다 들어온다).
     notes/QA-REPORT.md §2-6 이 통과시킨 기사 단위 규칙(_REPACK_HEAD/_REPACK_MID)도
     같은 계보대로 들고 있다 — 오늘 데이터에선 놀고 있지만 이유가 있다(해당 주석 참고).
     ⚠️ §2-6 이 기각한 "따옴표 앞까지 _BETWEEN 을 넓혀라" 는 쓰지 않았다.
  ③ **먹는 게 아닌 상품이 '출시' 기사로 나온다.** 실측:
       "동서식품, 캡슐커피 머신 '카누 바리스타 오아시스' 출시"  ← 커피 머신
     상품명('카누 바리스타 오아시스')만 보면 `base.NONFOOD_WORDS` 가 못 잡는다.
     GS25 의 '손앤박 하티'(화장품)와 같은 자리라 같은 방식으로 푼다 —
     기사 제목을 보는 _NONFOOD_TITLE 을 두고 **버리지 않고 nonfood=True 로 표시**한다.
  ④ '2종'·'3종' 기사가 잦다(카누 바리스타 아이스용 캡슐 2종, 애사비 콤부차 3종,
     포스트 오레오오즈바 2종, 티오피 배럴 에이지드향 2종). 오뚜기의 `\\d+종` 규칙이
     그대로 먹는다.
  ⑤ 회사명이 아예 없는 제목이 있다("오레오와 방탄소년단의 만남! …"). GS25 처럼
     회사명을 못 찾으면 자르지 않고 그대로 본다(그 건은 상품명에 '&' 가 있어 어차피
     버려진다 — 콜라보 한정판이다).

**'제안'·'첫 선' 은 _VERB 에 넣지 않았다.** GS25 는 실측으로 넣어 2건을 얻었는데,
동서식품 80건에는 그 동사를 쓰는 신제품 기사가 0건이고 "식생활 제안" 류 홍보
기사만 걸린다. 넓혀서 얻는 게 없어 좁은 쪽을 골랐다.

조인 결과 80건(2025-03-11 ~ 2026-10-01, 약 570일) 중 **10건**이 남는다. 10건 전부
제목을 눈으로 대조했고, 그중 7건은 상품 카탈로그(`releaseDt`)에 같은 상품이 실존하는지
교차로 확인했다(오집 0건). 버린 쪽도 전수로 훑었다 — '출시/선봬' 가 든 20건 중
버린 10건은 전부 '2종·3종' 묶음 기사 6건, 기존 제품 한정판 2건, 콜라보 한정판 1건
('오레오 & 방탄소년단', 상품명에 '&'), 회사명 없는 1건이다. 버리는 게 맞다.
최근 300일로 좁히면 **6건**이 남는다(아래 실행 결과). 월 1~2건 수준이고, 편의점 3사와 비교할
물량이 아니다.

**보지 않은 것이 아니라, 보고 안 쓴 것 — 상품 카탈로그 `POST /api/product/listData/{n}`**
notes/CANDIDATES-DIRECT2.md §8-8 이 "신제품 플래그가 있는지 안 봤다" 고 남긴 자리다.
2026-10-01 에 26페이지 253건을 전부 받아 봤다. **신제품 플래그는 없지만
`releaseDt` 가 있고, 그게 진짜 출시일이다.** 보도자료 날짜와 교차검증했다:

    포스트 크리치오 마시멜로   보도 2026-09-29 / releaseDt 2026-10-01
    포스트 그래놀라 제로슈거…  보도 2026-07-29 / releaseDt 2026-07-30
    카누 바리스타 오아시스     보도 2026-07-27 / releaseDt 2026-07-30
    카누 아이스 샷 아메리카노  보도 2026-05-06 / releaseDt 2026-05-08
    포스트 그래놀라 저당 렌틸  보도 2026-04-13 / releaseDt 2026-04-17
    리츠 크래커 바삭김        보도 2025-05-26 / releaseDt 2025-05-28
    카누 싱글오리진 콜롬비아   보도 2025-11-24 / releaseDt 2025-11-27

최근 300일 기준 카탈로그 쪽이 **20건 안팎**이고 보도자료 쪽이 3건이다. 보도자료가
안 난 상품(맥심 티오피 바닐라 라떼·스타벅스 RTD 3종·카누 인피니트 피크·필라델피아
크림치즈 미니 등)이 카탈로그에만 있다. 상품명도 제목 파싱 없이 `prodName` 으로
깨끗하게 나오고 `categoryNm`·`brandNm`·`explain` 까지 붙는다.
**그런데도 이 어댑터는 보도자료를 쓴다 — 작업 지시가 보도자료형이었기 때문이다.**
전환은 운영자 판단거리라 여기 근거만 남긴다. 전환할 때 알아야 할 것 3가지:
  - `releaseDt` 가 2015-07-11/12 인 행이 38건 이상이다. **CMS 이관 시각**이지
    출시일이 아니다. 300일 창을 쓰면 자동으로 걸러지지만 전체를 쓰면 안 된다.
  - 목록이 **출시일 순이 아니다.** 브랜드(`brandOrdr`) 묶음 안에서만 내림차순이라
    최근 건만 받으려 해도 26페이지를 다 받아야 한다(요청 26회).
  - 페이지 크기는 여기서도 10 고정이다(`recordCountPerPage` 300 을 넘겨도 10).

robots: `https://www.dongsuh.co.kr/robots.txt` → **404 인데 본문이 HTML 이다**
        (`text/html`, 1,245B, 홈 화면). 0바이트 404(= 규칙 부재, 오뚜기)와 다르다.
        규칙을 읽을 수 없으므로 판정 불가로 보고 **간격을 보수적으로 잡았다**
        (DELAY=5.0, 이 레포 기본 2.2 의 두 배 이상). notes/CANDIDATES-DIRECT2.md
        §5-4·§7-⑤ 가 요구한 처리다. `/api/` 를 금지하는 규칙도 당연히 없다
        (규칙 자체가 없다).
약관: **있다. 그리고 복제·배포 제한 조항이 있다.** 링크가 아니라 홈 푸터의 모달이라
      눈에 잘 안 띈다 — `<dialog data-modal="agreement">` 안에 전문 4,654자가
      SSR 로 들어 있다(`/main` 을 받아서 그 선택자로 꺼내면 된다).
      제13조 ② 「이용자는 동서식품을 이용함으로써 얻은 정보를 동서식품의 사전승낙 없이
      복제, 전송, 출판, 배포, 방송 기타 방법에 의하여 **영리목적으로** 이용하거나
      제3자에게 이용하게 하여서는 안됩니다」
      크롤러·스크래퍼·매크로를 금지하는 조항은 **없다**(해당 단어 0회).
      다만 제2조가 "이용자"를 **회원가입한 자**로 정의한다 — 우리는 가입하지 않는다.
      거기에 '영리목적' 단서까지 붙어 그대로 걸리는지는 애매하다.
      base.py 의 이마트24·도미노피자·폴바셋 주석과 같은 성격이라 **BRANDS 등록 시
      같은 블록에 적는 것을 권한다**(판단은 운영자 몫이다).
      (notes/CANDIDATES-DIRECT2.md §7-⑦ 이 "약관을 한 건도 못 읽었다" 고 남긴 자리다.)
"""
import re
import time
from datetime import date, timedelta

from . import base
from .base import Item

BRAND = "동서식품"
SITE = "https://www.dongsuh.co.kr"
LIST = SITE + "/api/news/listData/"          # + page. GET 아니라 POST.
VIEW = SITE + "/mediaCenter/news/info/"      # + idx
IMG = SITE + "/common/imageShow/"            # + fileId
PAGE_SIZE = 10       # 서버 고정. 바디로 늘려도 무시한다(실측).
MAX_PAGES = 8        # 폭주 방지 상한. 300일 창은 4~5페이지면 덮인다.
DAYS = 300           # 이보다 오래된 보도자료는 신제품 섹션에 쓸모가 없다.
DELAY = 5.0          # robots 를 읽을 수 없다(HTML). 기본 2.2 보다 보수적으로 잡는다.

# --- 제목 → 상품명 (maker_ottogi 와 같은 규칙 + 동서식품 함정 보강) -----------
# '제안'·'첫 선' 은 일부러 뺐다. GS25 는 실측으로 2건을 얻었지만 동서식품 80건에선
# 얻는 게 0건이고 "건강한 식생활 제안" 류 홍보 기사만 들어온다.
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭)")
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
_MULTI = re.compile(r"\d+\s*종")
_TRAIL_SEP = re.compile(r"^\s*[·∙,、/]")
# 홍보 헤드라인이 회사명 앞에 붙는다(함정 ①). 따옴표가 없는 경우가 더 흔해서
# _HEAD 로는 안 걸린다. GS25 와 같이 회사명 앞은 판정에서 통째로 뺀다.
# ⚠️ GS25 와 같은 한계를 그대로 안는다 — 이 절단이 회사명 '앞'의 _SKIP 도 무력화한다.
#    80건 전수에서 이 구멍으로 새어 들어온 건 0건이라 그대로 둔다.
# ⚠️ 회사명이 없는 제목도 있다(함정 ⑤). 못 찾으면 자르지 않는다.
# ⚠️ 이 절단도 80건에서는 결과를 바꾸지 않는다(빼도 추가·유실 0건) — 관측된 헤드라인
#    셋이 전부 따옴표를 안 썼기 때문이다. 그래도 둔다. GS25 가 바로 이 자리에서
#    '슈링크플레이션'(헤드라인)을 상품명으로 집었고, 동서식품도 헤드라인을 앞에 붙이는
#    같은 버릇을 가졌다. 헤드라인에 홑따옴표가 한 번 끼는 순간 터지는 자리다.
_BRAND_TOKEN = re.compile(r"동서식품|㈜동서")

# 기사 자체가 신제품 기사가 아닌 경우. '출시'가 들어 있어도 버린다.
# maker_ottogi 와 **글자 하나까지 같다.** 동서식품 80건 전수에 돌려 보니 이것만으로
# 충분했다 — 사회공헌(기탁·성금·봉사·연탄)·자체 행사(입신최강전·바리스타 챔피언십·
# 커피클래식·문학상)·가격 조정·포인트 적립 기사는 전부 _VERB 가 없어서 알아서 빠진다.
# 처음엔 '기탁·성금·봉사·오픈·표창·인증·한정판·패키지' 등 25개를 더 넣어 봤는데
# **24개가 아무 일도 안 했고(추가유입 0건), 나머지 하나('인증')는 진짜 신제품을 죽였다** —
#   "동서식품, RA인증 ‘카누 싱글 오리진 콜롬비아 톨리마’ 신제품 출시"
#   (상품 카탈로그의 releaseDt 2025-11-27 로 실존 확인)
# 그래서 전부 뺐다. 없어도 되는 규칙은 넣지 않는다.
_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "협약", "체결", "주주총회", "후원", "기부", "추모", "공모", "발대식",
         "심포지엄", "박람회", "팝업", "캠페인", "발탁", "앰배서더", "재단",
         "경연", "시상", "간담회", "개최", "스폰서", "리뉴얼", "실적",
         "매진", "진행", "참가", "참여", "전개", "지원")
# 따옴표와 '출시' 사이에 이게 끼면 따옴표 안은 상품명이 아니라 제휴 상대이거나
# 기존 제품의 포장이다.
# '한정판' 한 단어가 동서식품 실측 추가분이고, **이 한 단어가 함정 ② 두 건을 다 잡는다**:
#   "동서식품, ‘컬러 오브 맥심’ 한정판 패키지 출시"              (맥심 = 기존 제품)
#   "동서식품, ‘오레오 마인크래프트 무비 에디션’ 한정판 출시"
# 빼고 돌리면 둘 다 신제품으로 올라온다(실측). GS25 가 더한 공동·드라마·영화·맞춤형은
# 동서식품에선 추가유입 0건이라 넣지 않았다.
# ⚠️ 일부러 따옴표 '뒤쪽'만 본다. head 전체로 넓히지 마라 —
#    notes/QA-REPORT.md §2-6 이 시험하고 기각한 해법이다(GS25 채택분 2건이 죽는다).
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱",
            "한정판")
# '출시' 뒤에 실적 문구가 붙으면 그 날짜는 출시일이 아니라 기사 작성일이다.
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")

# 기존 제품의 테마/에디션 패키지 기사. notes/QA-REPORT.md §2-6 이 세 브랜드 채택분
# 전수에 돌려 통과시킨 규칙 그대로다(틀린 2건만 버리고 맞는 9건은 전부 살았다).
# ⚠️ 동서식품 80건에서는 **이 두 줄이 아무 일도 안 한다**(빼도 추가유입 0건) —
#    위 _BETWEEN 의 '한정판' 이 먼저 잡기 때문이다. 그래도 지우지 않는다.
#    이 둘이 막는 건 "‘토이 스토리’ 테마 ‘맥심 모카골드’ 출시" 꼴인데, 동서식품은
#    기존 제품 한정판 기사를 실제로 쓰는 브랜드고('컬러 오브 맥심'·'오레오 … 에디션')
#    그 꼴이 나오면 _BETWEEN 으로는 못 막는다. 같은 계보 4개 파일이 같은 블록을 쓴다.
_REPACK_HEAD = ("에디션", "라벨")                            # “…” 헤드라인 안
_REPACK_MID = ("테마", "에디션", "라벨", "컬래버", "콜라보")    # 따옴표와 따옴표 사이

# 먹는 게 아닌 상품(함정 ③). base.NONFOOD_WORDS 는 상품명만 보는데, '카누 바리스타
# 오아시스' 는 이름만으로 커피 머신인지 알 수 없다. 기사 제목이 "캡슐커피 머신 …"
# 이라고 말해 준다. GS25 의 _NONFOOD_TITLE 과 같은 자리·같은 방식이다.
# base.py 경고대로 좁게 잡는다 — 기사 제목이라 상품명보다 오탐 여지가 적다.
# 새 한국어 단어는 전체 data/products.json 상품명 7,162건에 대고 셌다 —
# '머신' 0건·'화장품' 0건·'뷰티' 0건, '굿즈' 1건(이미 nonfood). **식품 오탐 0.**
_NONFOOD_TITLE = ("머신", "굿즈", "화장품", "뷰티")


def _pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열.

    "캡슐 2종 출시"처럼 기사 하나에 상품이 여럿이면 버린다. 억지로 '캡슐 2종'을
    상품명으로 쓰지 않는다.
    """
    t = " ".join(title.split())
    # “…” 홍보 헤드라인 안에 에디션/라벨이 있으면 기존 제품의 패키지 기사다.
    if any(w in m.group(1) for m in _HEAD.finditer(t) for w in _REPACK_HEAD):
        return ""
    body = _HEAD.sub(" ", t)
    # 회사명 앞은 홍보 헤드라인이다. 뒤쪽만 본다. 회사명이 없으면 그대로 본다.
    b = _BRAND_TOKEN.search(body)
    if b:
        body = body[b.end():]
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
    if _TRAIL_SEP.match(head[quoted.end():]):
        return ""
    name = quoted.group(1).strip(" ,·∙")
    if len(name) < 2 or any(c in name for c in "·∙&?"):
        return ""
    return name


def _date(s: str) -> str:
    """'2026-09-29 09:12' 또는 '2026-09-29' → '2026-09-29'. 월·일 범위를 검증한다.

    범위를 안 보면 UUID 조각(`2026/06/92`)이 날짜로 둔갑한다(다른 브랜드에서 실측).
    """
    m = re.match(r"^\s*(20\d{2})[-.](\d{1,2})[-.](\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _thumb(files) -> str:
    """lstAtchFileVO 에서 썸네일 fileId 를 찾아 이미지 주소로 만든다.

    newsFunc.js 가 `fileKnd == 'thumbImg'` 인 것만 골라 쓴다. 본문 이미지
    (`fileKnd` 가 다르다)를 집으면 카드에 엉뚱한 사진이 뜬다.
    """
    for f in files or []:
        if isinstance(f, dict) and f.get("fileKnd") == "thumbImg" and f.get("fileId"):
            return IMG + f["fileId"]
    return ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    with base.client(headers=headers) as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            # GET 이 아니라 POST 다. 바디는 빈 객체면 된다.
            r = base.retry(lambda: c.post(LIST + str(page), json={}))
            r.raise_for_status()
            data = (r.json() or {}).get("data") or {}
            rows = data.get("newsInfoList") or []

            if page == 1:
                # 응답 모양이 바뀌면 조용히 0건이 되는 게 제일 나쁘다.
                # 1페이지는 반드시 기사가 와야 한다(522건짜리 아카이브다).
                if not rows:
                    raise ValueError(
                        f"동서식품 보도자료 1페이지가 비었다. data 키={sorted(data)} "
                        f"paginationInfo={data.get('paginationInfo')!r} — "
                        f"응답 스키마가 바뀌었는지 확인하라")
                # 필드명 하나로 전건 None 이 되는 자리다. 조사 문서 초판이 제목 키를
                # 'nttSj' 로 적었다가 검수에서 잡혔다(notes/QA-REPORT.md §13).
                # 키가 사라지면 조용히 0건이 되므로 여기서 드러낸다.
                missing = [k for k in ("sj", "showDt", "idx") if k not in rows[0]]
                if missing:
                    raise ValueError(
                        f"동서식품 보도자료 응답에 {missing} 키가 없다. "
                        f"실제 키={sorted(rows[0])} — 필드명이 바뀌었는지 확인하라")
            if not rows:
                break

            # 날짜는 showDt. regDt 는 일괄 재등록 흔적이 있다(docstring 참고).
            dates = [_date(row.get("showDt") or row.get("regDt") or "") for row in rows]
            for row, released in zip(rows, dates):
                if released and released < floor:
                    continue
                title = " ".join((row.get("sj") or "").split())
                name = _pick(title)
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    # 기사 제목이 그대로 설명이 된다. 앞의 헤드라인+회사명만 턴다.
                    desc=re.sub(r"^.*?(?:동서식품|㈜동서)[^,]*,\s*", "", title),
                    image=_thumb(row.get("lstAtchFileVO")),
                    released_at=released,
                    is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                    nonfood=any(w in title for w in _NONFOOD_TITLE),
                    url=VIEW + str(row.get("idx")),
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

            # 목록은 showDt 내림차순이지만(80건 전수 확인) GS25 처럼 기사 하나가
            # 오래됐다고 끊지 않는다. 페이지에서 가장 새 기사까지 기준일보다
            # 오래됐을 때만 멈춘다.
            fresh = [d for d in dates if d]
            if fresh and max(fresh) < floor:
                break
            if len(rows) < PAGE_SIZE:
                break
    return items
