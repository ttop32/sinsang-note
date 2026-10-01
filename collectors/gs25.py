"""GS25 — 상품 카탈로그가 없다. 보도자료에서 신제품과 출시일만 뽑는다.

**먼저 알아야 할 것: GS25 는 상품 목록을 웹에 두지 않는다.** 2026-10-01 실측:
  - `gs25.gsretail.com` 은 경로가 무엇이든(`/robots.txt`, 옛 상품 경로
    `/gscvs/ko/products/youus-freshfood`, `/products/...`) 전부 200 으로
    `https://www.gsretail.com/brand/gs25` 에 떨어진다. 906바이트 Vue SPA 껍데기다.
    옛 상품 페이지와 그 XHR(`youus-freshfood-search`)은 남아 있지 않다.
  - 앱(우리동네GS)의 웹 짝인 `m.woodongs.com` 은 robots 가 전면 허용이지만,
    번들(`/static/js/main.*.js`)의 라우트 142개가 전부 멤버십·결제·이벤트·약관
    웹뷰다. `goods`/`product` 목록 라우트가 하나도 없다. 카탈로그는 네이티브 앱
    전용이고, 그 백엔드(`b2c-apigw.woodongs.com`)는 전 경로 CloudFront 403 이다.
  - 본사 사이트 `www.gsretail.com` 도 IR·브랜드 소개 사이트다. 라우트에 상품
    목록이 없다(`/gs25list` 는 이름과 달리 신한카드 픽업 가능 '점포' 목록이다).
따라서 CU·세븐일레븐·이마트24 처럼 상품 목록을 훑는 어댑터는 만들 수 없다.
'전체 메뉴를 일단 긁는다'는 선택지 자체가 없다 — 긁을 목록이 존재하지 않는다.

남은 경로는 본사 보도자료 하나뿐이고, 이건 오뚜기·오리온과 **같은 종류의 소스**다.
그래서 그 둘의 규칙을 그대로 가져와 GS25 제목 버릇에 맞게 조인다.

수집 경로. 2026-10-01 실측:
  - 목록 페이지 `/news/press-releases` 는 Vue SPA 라 HTML 에 기사가 0건이다.
    그 화면이 부르는 JSON 이 `/api/homepage/news/news/selectPressRelease` 다.
    쿠키·토큰·CSRF 가 없고 `Accept: application/json` 만 주면 그대로 열린다
    (헤더를 안 주면 YAML 로 떨어진다. 반드시 명시한다).
  - `prrBzDvCd` 가 사업 구분이다. `02` = GS25 (`selectCommCdByGrpId?commGrpCd=BZ_DV_CD`
    로 확인: 01 GS리테일 / 02 GS25 / 03 GS THE FRESH / 04 GS SHOP / 05 POP 카드).
    `prrDvCd=01` 은 보도자료 종류다. 둘을 걸면 GS25 것만 962건 나온다.
  - `pageSize` 가 그대로 먹어서 100건씩 받는다. 전 구간이 요청 2~3회면 끝난다.

날짜는 `expsrBeginDttm`(노출 시작일)을 쓴다. 300건 실측에서 299건이 서로 다른
날짜였다. `regDttm`(등록 시각)은 278건이라 일괄 재등록 흔적이 있다 — 실제로
2026-08-25 하나에 13건이 몰려 있고 그 기사들의 노출일은 7/27~8/21 로 흩어진다
(한 달 가까이 벌어진다). 그래서 regDttm 은 쓰지 않는다.

목록 정렬은 regDttm 내림차순이라 노출일 기준으로는 완전한 내림차순이 아니다.
300건 중 1곳에서 20일짜리 역전이 있었다(7/24 다음이 8/13). 그래서 '오래된 기사를
처음 만나면 중단'하지 않고 **페이지에서 가장 새 기사까지 기준일보다 오래됐을 때만**
멈춘다. 한 페이지가 100건이라 이 정도 역전은 덮인다.

신제품 판정 근거는 '배지'가 아니라 **기사 자체**다. 브랜드가 '출시·론칭'이라고 낸
기사라서 is_new=True 로 둔다(오뚜기·오리온과 같은 근거). 대신 상품 축이 거칠고
GS25 제목은 그 둘보다 훨씬 시끄러워서, 상품을 특정 못 하는 기사는 통째로 버린다.
2026-10-01 실측으로 확인한 GS25 고유의 함정 4가지:
  ① 홑따옴표 헤드라인이 브랜드명 **앞**에 붙는다. 오뚜기는 쌍따옴표만 헤드라인이라
     그 규칙을 그대로 쓰면 헤드라인을 상품명으로 집는다.
     실측: "'슈링크플레이션' 역주행 상품 등장!...GS25, 990원 PB 용기면 선보인다"
     → '슈링크플레이션' 을 상품명으로 집었다. 그래서 브랜드명 앞은 통째로 버린다.
  ② 따옴표 안이 제휴 상대·IP 인 경우가 잦다. 실측 오집: '키키'(K팝 그룹, 실제
     상품은 젤라또바), '천국보다 아름다운'(드라마), 'D.P.2'(넷플릭스), '참이슬'
     (기존 브랜드, 실제 상품은 맞춤형 안주). → _BETWEEN 에 픽한·손잡고·드라마 등 추가.
  ③ 상품이 아니라 서비스·점포·정책 기사가 '론칭' 을 쓴다. 실측 오집:
     'AI 퍼스널컬러 진단'(서비스), '마감할인'(앱 기능), '내일택배'(배송). → _SKIP 확장.
  ④ '시리즈' 기사는 상품이 여럿이다. 실측 오집: '넘버원' 시리즈, '대식가 시리즈'.
     오뚜기의 `\\d+종` 규칙과 같은 취지라 '시리즈' 를 _SKIP 에 넣는다.
조인 뒤 최근 300일 74건 중 11건이 남았다. 11건 전부 제목을 눈으로 대조했고, 그중
6건은 기사 본문까지 열어 상품명이 실제로 그 상품을 가리키는지 확인했다(오집 0건).
⚠️ 본문 표기가 제목과 띄어쓰기만 다른 경우가 있다 — '삼포깐포도 하이볼'(제목) /
'삼포깐포도하이볼'(본문). base.make_key() 가 공백을 다 털어서 중복 판정엔 영향이 없다.
11건 중 '손앤박 하티' 1건은 화장품이라 nonfood=True 로 표시해 내보낸다(아래 _NONFOOD_TITLE).
같은 창의 오뚜기 15건·오리온 10건과 같은 급이다.

버리는 쪽도 눈으로 훑었다. 대부분 매출·수상·점포 기사라 버리는 게 맞다.
처음엔 '워터젤리 하이볼'(동사가 '제안')·'소프트 삼각김밥'(동사가 '첫 선')을
놓쳤는데, "동사를 넓히면 ③ 부류가 같이 들어온다"는 건 **실측해 보니 틀린 걱정**이라
_VERB 에 둘을 넣어 11건이 됐다(아래 _VERB 주석 참고). 그래도 남는 미수집은
제목이 상품을 특정하지 못하는 경우라, 못 믿을 걸 담느니 놓치는 쪽을 고른다.

수집량은 CU·세븐일레븐과 비교할 수준이 못 된다(연 10건 안팎). GS25 가 실제로
내는 신상품의 극히 일부, '본사가 보도자료를 낼 만큼 민 상품'만 잡힌다.
그래도 날짜가 정확하고 브랜드가 직접 '출시'라고 말한 건이라 신뢰도는 높다.

robots: `www.gsretail.com/robots.txt` → 200, text/plain. `User-agent: *` 에
        `Disallow: /api/` + `Crawl-delay: 10` + `Visit-time: 0400-0845`(UTC).
        우리가 쓰는 JSON 이 바로 그 `/api/` 다. 사용자 방침에 따라 수집하되,
        요청이 2~3회뿐이라 Crawl-delay 10초는 그냥 지킨다(총 20초, 비용이 없다).
        Visit-time 은 지키지 않는다 — 지키려면 현재 cron(KST 06:00)을 통째로
        옮겨야 하는데 그건 이 어댑터 혼자 결정할 일이 아니다.
        ⚠️ `gs25.gsretail.com` 에는 robots.txt 가 없다. 그 경로로 요청하면
        robots.txt 자리에서 HTML 이 돌아온다(상태코드 200). 404 와 혼동하지 마라.
약관: SPA 라 초기 HTML 에 약관이 없어 확인하지 못했다(CRAWLING-POLICY.md §4 와 동일).
⚠️ 기사 이미지가 `/api/public/fileUpload/...` — robots 금지 경로다.
   CRAWLING-POLICY.md §6-3 대로 URL 은 Item.image 에 담되 어댑터는 그 URL 을
   절대 요청하지 않는다(존재 확인 HEAD 도 금지). 이미지 R2 미러링(이슈 #5) 때
   이 브랜드는 대상에서 빼야 한다.

─────────────────────────────────────────────────────────────────────────────
2차 재조사 (2026-10-01). "상품 카탈로그 없음" 결론은 그대로 유지된다. 코드 무변경.
앞 조사가 안 봤거나 얕게 본 각도를 실측으로 다시 팠다. 다음 사람이 같은 데를
또 뒤지지 않게 '이번에 본 것과 그 결과'만 남긴다.

A. 앱 백엔드 `b2c-apigw.woodongs.com` 의 403 이 왜 403 인가 (앞 조사 미확인).
   - 헤더 탓이 아니다. base.UA / `Origin+Referer: m.woodongs.com` / `Accept: json` /
     `curl/8.7.1` UA / 빈 UA 전부 403(919B, `x-cache: Error from cloudfront`).
     CloudFront 응답은 "Request blocked" — WAF 차단이지 앱이 주는 401/403 이 아니다.
     즉 UA·Origin·Referer 를 맞춘다고 열리는 종류가 아니다(사용자 방침=UA 허용인데도).
   - 단 하나 열린 게 있다: `GET /catalog/`(끝 슬래시) → 200, 208B JSON 인포뱃지
     {"App name":"gst-b2c-catalog-api","API version":"v1","Build time":"2026-09-16..."}.
     슬래시 없는 `/catalog` 과 그 하위는 전부 403. 이건 서비스가 살아 있다는 신호일 뿐
     상품 목록이 아니다. 그 아래 실제 카탈로그 엔드포인트는 '우리동네GS'(픽업·배달·
     결제가 붙은 로그인 앱)의 인증 영역이다. 더 들어가려면 토큰/로그인이 필요 →
     사용자 방침(인증 우회 금지)에 걸린다. 그래서 여기서 멈춘다. ⚠️ 엔드포인트 경로
     퍼징은 하지 않았다(스캐닝으로 취급됨). 공개로 열린 건 `/catalog/` 인포뱃지뿐이다.
   - `m.woodongs.com/static/js/main.*.js` 번들에서 뽑은 base URL 들을 직접 쳐 봤다:
       b2c-bff.woodongs.com → 403(CloudFront)   b2c-pay.woodongs.com → 403(CloudFront)
       gs25.gsretail.com:5443 → connect timeout(방화벽)
       super.gsretail.com:7643 / super.gsretail.com → DNS NXDOMAIN
       memdev.gsretail.com:6143 → connect timeout
     공개로 상품을 주는 곳은 없다. 번들의 카탈로그 호출은 전부 B2C_BASE_URL(apigw)
     +런타임 토큰 조합이라 로그인 없이는 못 부른다.

B. 서브도메인·sitemap·앱 셸 (앞 조사 보강).
   - `m.woodongs.com/robots.txt` → `User-agent: * / Disallow:`(전면 허용).
   - `m.woodongs.com/sitemap.xml` → 진짜 sitemap 이 아니다. SPA catch-all 이 랜딩
     HTML 을 돌려준다(og:title="우리동네GS — 앱 다운로드"). 즉 이 호스트는 앱
     다운로드 랜딩 + 웹뷰 셸이고, 상품 목록 라우트가 없다는 앞 결론을 재확인.
   - `www.gsretail.com/sitemap.xml` → 906B 브랜드 SPA 껍데기(앞의 리다이렉트와 동일).
     robots 의 `#Sitemap: /sitemap.xml` 은 주석 처리돼 있어 실 sitemap 은 제공 안 됨.

C. 보도자료 전수 재훑기 (앞 조사가 "동사 넓히면 서비스가 섞인다"던 걸 검수가 반증한 뒤
   9→11 로 올린 그 소스). 962건(아카이브 2008-07-04~2026-09-22) 전부 받아 최근 300일
   창 75건을 다시 봤다. 채택 12건(중복 '소프트 삼각김밥' 제거하면 실 11건, 현행 그대로).
   버린 63건 제목을 전부 눈으로 읽었다. 결과: 전부 올바른 탈락이다.
     · 매출·수상·점포·서비스·상생·수출·협약 = _SKIP 정상 작동.
     · 'n종 출시'(설 5종 등) = _MULTI 정상.  '넘버원/대식가 시리즈' = _SKIP 시리즈 정상.
     · '키키'(K팝) 젤라또바 = _BETWEEN '픽한' 으로 정상 탈락(따옴표 안=IP).
     · '치즈 미역국∙카레 당면 상품화' = 이름에 ∙(두 상품) → 정상 탈락.
   가장 아깝다 싶은 2건도 담을 수 없다:
     · '1인분 피자'(배민 협업, 2026-02-11) — _SKIP 의 '매출'·'배달'에 걸림. 제목이
       퀵커머스 매출·배민 협업 중심이고 '1인분 피자'는 일반 서술어다. '배달'을 빼면
       진짜 배달 서비스 기사가 들어온다(교환 조건이 나쁨).
     · '딸기샌드위치 판매 개시'(2025-12-09) — 동사 없음(판매 개시/돌아왔다), 재출시
       시즌 상품, 상품명이 따옴표에도 없어 애초에 추출 불가.
   결론: 보도자료 픽에서 '진짜 신제품인데 놓친 것'은 없다. _VERB/_SKIP 를 넓혀 이 둘을
   잡으려 하면 과거 오염 사례(행사·서비스 혼입)를 되부른다. 레포 방침(못 믿을 걸 담느니
   놓친다)대로 무변경 유지.

D. 행사 페이지(1+1/2+1) — 공개 목록은 앱 전용(apigw, 인증)이고 웹 공개본이 없다.
   보도자료에 행사 기사는 있으나(예 '달콤페스티벌') _SKIP 의 '이벤트·캠페인·행사·혜택'
   이 이미 막는다. 행사를 신상으로 올릴 위험은 현재 어댑터엔 없다.

E. GS 계열 타 웹자산(GS SHOP·GS THE FRESH 등)은 GS25 PB 편의점 신상을 공개
   카탈로그로 올리는 곳이 아니다(홈쇼핑/수퍼마켓, 상품축이 다름). 요기요/배민 GS25
   입점은 위치+플랫폼 인증이 필요한 배달 메뉴(점포 재고)라 '신상 피드'가 아니고
   방침상 인증 우회 금지에 걸린다. 수집원으로 쓸 수 없다.

종합: 상품 카탈로그는 여전히 수집 불가(앱 전용·인증·WAF). 보도자료 외 새 공개 경로
없음. 보도자료 픽도 이미 최적점에 있다. 그래서 코드는 손대지 않았다.
"""
import re
import time
from datetime import date, timedelta

from . import base
from .base import Item

BRAND = "GS25"
SITE = "https://www.gsretail.com"
LIST = SITE + "/api/homepage/news/news/selectPressRelease"
VIEW = SITE + "/news/press-releases/detail"
BZ_GS25 = "02"       # 사업구분코드. BZ_DV_CD 공통코드에서 GS25.
PRR_PRESS = "01"     # 보도자료 종류.
PAGE_SIZE = 100      # 그대로 먹는다. 300일 창이 한 페이지에 덮인다.
MAX_PAGES = 3        # 폭주 방지 상한. 현재 1페이지면 끝난다.
DAYS = 300           # 이보다 오래된 보도자료는 신제품 섹션에 쓸모가 없다.
DELAY = 10.0         # robots 의 Crawl-delay. 요청이 2~3회뿐이라 그냥 지킨다.

# --- 제목 → 상품명 (maker_ottogi 와 같은 규칙 + GS25 함정 보강) ----------------
# '제안'·'첫 선' 은 오뚜기·오리온에 없는 GS25 전용 추가분이다. 넓히면 서비스 기사가
# 같이 들어올까 봐 처음엔 뺐는데, 실제로 돌려 보니 근거 없는 걱정이었다 —
# 아카이브 300건 전수에서 추가 유입이 정확히 2건이고 둘 다 진짜 신제품이다
# (워터젤리 하이볼·소프트 삼각김밥, 본문에서 '출시' 확인). 서비스 기사는 _SKIP 의
# 서비스·앱·배달·택배·점포가 이미 막고 있다. 잃는 건도 0건이었다.
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭|상품화|제안|첫 선)")
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
_MULTI = re.compile(r"\d+\s*종")
_TRAIL_SEP = re.compile(r"^\s*[·∙,、/]")
# 홑따옴표 헤드라인이 브랜드명 앞에 붙는다(함정 ①). 브랜드명 앞은 판정에서 통째로 뺀다.
# ⚠️ 알려진 한계: 이 절단이 _SKIP 도 같이 무력화한다. 브랜드명 '앞'에 있는 매출·돌파는
#    걸러지지 않는다. 현재 채택 건 전수 검사에서 이 구멍으로 새어 들어온 건 0건이라
#    그대로 둔다. GS25 의 제목 버릇(헤드라인→브랜드명→본문)이 바뀌면 드러날 구조다.
_BRAND_TOKEN = re.compile(r"GS25|지에스25")

# 기사 자체가 신제품 기사가 아닌 경우. '출시'가 들어 있어도 버린다.
# 앞쪽은 maker_ottogi 와 같고, 뒤쪽 두 줄이 GS25 실측으로 덧댄 것이다(함정 ③④).
_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "협약", "체결", "주주총회", "후원", "기부", "추모", "공모", "발대식",
         "심포지엄", "박람회", "팝업", "캠페인", "발탁", "앰배서더", "재단",
         "경연", "시상", "간담회", "개최", "스폰서", "리뉴얼", "실적",
         "매진", "진행", "참가", "참여", "전개", "지원",
         "서비스", "플랫폼", "매장", "점포", "오픈", "앱", "배달", "택배",
         "구독", "할인", "혜택", "이벤트", "시리즈", "로봇", "창업", "수출")
# 따옴표와 '출시' 사이에 이게 끼면 따옴표 안은 상품명이 아니라 제휴 상대다(함정 ②).
# ⚠️ 일부러 따옴표 '뒤쪽'만 본다. head 전체로 넓히지 마라 — 채택 건 중 2건이 죽는다.
#   '사워레몬요거트'        ("TXT 연준∙요아정 협업 '사워레몬요거트' 선봬") — 따옴표 앞에 '협업'
#   '초BIG!무쿠점보멜론구미' ("공동 개발 '초BIG!…' 선봬")                  — 따옴표 앞에 '협업','공동'
# 둘 다 진짜 신제품이고 상품명도 정확하다. 협업으로 '만든' 신제품과 협업 상대를
# 상품명으로 '오집'한 경우는 '협업'이라는 단어만으로 못 가른다. 위치가 그 구분이다.
# '속'(드라마 속 '…') 은 넣지 않는다. 한 글자라 계속·소속·약속·속도에 걸린다.
# base.py 가 경고하는 한국어 단어경계 문제고, '드라마' 로 이미 잡힌다.
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱",
            "픽한", "손잡고", "공동", "드라마", "영화", "넷플릭스", "맞춤형")
# '출시' 뒤에 실적 문구가 붙으면 그 날짜는 출시일이 아니라 기사 작성일이다.
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")

# 먹는 게 아닌 상품. base.NONFOOD_WORDS 가 상품명만 보는 데 비해 이쪽은 기사 제목을
# 본다 — '손앤박 하티'(화장품)처럼 상품명만으로는 굿즈인지 알 수 없는 게 걸린다.
# base.py 경고대로 좁게 잡는다. 기사 제목이라 상품명보다 오탐 여지가 적다.
_NONFOOD_TITLE = ("메이크업", "화장품", "뷰티", "굿즈")


def _pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열.

    "젤리 2종 출시"처럼 기사 하나에 상품이 여럿이면 버린다. 억지로 '젤리 2종'을
    상품명으로 쓰지 않는다.
    """
    t = " ".join(title.split())
    body = _HEAD.sub(" ", t)
    # 브랜드명 앞은 홍보 헤드라인이다. 뒤쪽만 본다.
    b = _BRAND_TOKEN.search(body)
    if b:
        body = body[b.end():]
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
    # 닫는 따옴표 바로 뒤가 구분자면 상품이 더 이어진다.
    if _TRAIL_SEP.match(head[quoted.end():]):
        return ""
    name = quoted.group(1).strip(" ,·∙")
    if len(name) < 2 or any(c in name for c in "·∙&?"):
        return ""
    return name


def _date(s: str) -> str:
    """'2026-09-22 00:00:00' → '2026-09-22'. 월·일 범위를 검증한다.

    범위를 안 보면 UUID 조각(`2026/06/92`)이 날짜로 둔갑한다(다른 브랜드에서 실측).
    """
    m = re.match(r"^\s*(20\d{2})[-.](\d{1,2})[-.](\d{1,2})", s or "")
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
    # Accept 를 안 주면 같은 주소가 YAML 을 돌려준다. 반드시 명시한다.
    with base.client(headers={"Accept": "application/json"}) as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={
                "expsrYn": "Y", "prrDvCd": PRR_PRESS, "prrBzDvCd": BZ_GS25,
                "pageNum": page, "pageSize": PAGE_SIZE}))
            r.raise_for_status()
            body = r.json()
            # 응답 모양이 바뀌면 조용히 0건이 되는 게 제일 나쁘다. 1페이지는 반드시
            # 기사가 와야 한다(GS25 보도자료는 962건짜리 아카이브다). 안 오면 드러낸다.
            if page == 1 and not (body.get("list") or []):
                raise ValueError(
                    f"GS25 보도자료 1페이지가 비었다. 응답 키={sorted(body)} "
                    f"totalCount={body.get('totalCount')!r} — "
                    f"prrBzDvCd/prrDvCd 코드나 응답 스키마가 바뀌었는지 확인하라")
            rows = body.get("list") or []
            if not rows:
                break

            dates = [_date(row.get("expsrBeginDttm") or "") for row in rows]
            for row, released in zip(rows, dates):
                if released and released < floor:
                    continue
                title = " ".join((row.get("prrTitle") or "").split())
                name = _pick(title)
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    # 기사 제목이 그대로 설명이 된다. 앞의 브랜드명만 턴다.
                    desc=re.sub(r"^\s*GS25[^,]*,\s*", "", title),
                    name=name,
                    image=_abs(row.get("pcFileUrl")),
                    released_at=released,
                    is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                    nonfood=any(w in title for w in _NONFOOD_TITLE),
                    url=f"{VIEW}?prrSeqno={row.get('prrSeqno')}",
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

            # 목록이 노출일 기준 완전한 내림차순이 아니라서(20일짜리 역전 실측),
            # 기사 하나가 오래됐다고 끊지 않는다. 페이지에서 가장 새 기사까지
            # 기준일보다 오래됐을 때만 멈춘다.
            fresh = [d for d in dates if d]
            if fresh and max(fresh) < floor:
                break
            if len(rows) < PAGE_SIZE:
                break
    return items
