"""CU(씨유).

product.do 는 껍데기만 내려주고, 목록은 /product/productAjax.do 에 listForm 의
hidden 값을 그대로 POST 해서 받는다. 쿠키·세션 없이 열리고 브라우저도 불필요.
'더보기' 버튼도 같은 엔드포인트를 pageIndex 만 올려 다시 부르는 구조다.

신상품만 따로 모은 목록은 없다(상단 메뉴는 전체 상품 / CU 차별화 상품 / 행사상품 셋뿐).
대신 카테고리별로 최신등록순(searchCondition=setC)으로 훑으면서 NEW 태그가 붙은 것만
거두고, 태그가 끊기는 페이지에서 멈춘다. 설명문은 목록에 없어서 상세(view.do)를
상품당 한 번씩 더 본다.

## NEW 배지는 진짜 선별 표시다 (2026-10-01 실측)

'666건이 전부 NEW 라 신호 값이 0' 이라는 의심을 원본 HTML 로 직접 대조했다.
어댑터가 NEW 인 것만 담고 나서 센 수라서 생기는 착시다. **거른 뒤가 아니라
거르기 전의 카드**를 세면:
  - 7개 카테고리에서 읽은 카드 **1,200건 중 NEW 가 667건(55.6%)**이다.
    어댑터가 무조건 True 를 넣는 게 아니라 `.tag .new` 가 실제로 있는 것만 담는다.
  - 최신등록순으로 내려가면 NEW 가 한 지점에서 뚝 끊기고 그 뒤로는 0이다.
    (음료 1p 35 → 2p 1 → 3p 0 / 식품 6p 35 → 7p 5 → 8p 1 → 9p 0 /
     과자류 5p 40 → 6p 5 → 7p 0 / 즉석조리는 1p 부터 3건뿐)
  - 카드 마크업의 개발자 주석이 태그 종류를 다 적어놨다:
    `<!-- [D] .tag > span .new : new / .best : best -->`. NEW·BEST 둘뿐이고
    더 좁은 배지(주차 표시·'이번주 신상' 같은 것)는 없다.
  - 정렬도 더 좁힐 게 없다. searchCondition 을 setA~setE 로 바꿔보면
    setA 와 setC 가 완전히 같고(최신등록순), setB 는 다른 축(인기로 보임),
    setD 는 0건, setE·빈값은 오래된순이다. 최신등록순이 이미 제일 좁다.

## NEW 는 '신제품'이 아니라 'CU 에 새로 등록됨'이다 (2026-10-02 실측)

위 절은 배지가 **선별 표시**라는 것까지만 맞다. 무엇을 선별하는지는 다르다.
운영자가 "기존 과자가 신제품으로 잡힌다"고 지적해서 전수로 대조했고, 배지가
가리키는 건 상품의 나이가 아니라 **상품코드(gdIdx)의 나이**였다.
  - 배지는 상품마다 고정이다. 같은 상품을 키워드 검색·기본정렬·최신등록순
    어디로 불러도 같다(세븐일레븐 '신상품' 탭처럼 엔드포인트를 바꾸면 사라지는
    가짜가 아니다). 같은 제품군의 옛 상품코드엔 안 붙는다 — 쿠크다스초코케잌
    (28242) NEW / 쿠크다스크림(5195)·쿠크다스커피(13937) 없음.
  - 그런데 **옛 상품을 새 코드로 다시 올려도 붙는다.** 오리온)초코칩쿠키256g
    (28089)은 바코드 8801117122409 이고 식약처 품목제조보고일이 **1986-02-15**,
    다나와 등록은 2021-04 다. 40년 된 상품이 NEW 로 올라온다.
    튀김)애플파이(28310)도 'CU)애플파이' 품목제조보고가 2020-09-25 다.
  - 농산물은 아예 주기적이다. 데일리)거봉컵200g(21368, NEW 없음)이 있는데
    데일리)거봉500g(팩)(28028)·거봉1kg(박스)(27977)이 NEW 로 뜬다.
  - 출시와 CU 입점 사이 시차도 크다. 오리온)스윙칩까르보불닭은 2026-06-25
    출시인데 우리 날짜가 2026-08-24 다(60일 창을 99일째에 통과한다).
그래서 **NEW 배지는 아래 이미지 날짜의 오염을 막아주지 못한다.** 날짜가
'사진을 올린 때'인 것과 배지가 'CU 에 등록된 때'인 것이 같은 한계다 —
둘 다 출시일이 아니라 입점일이다. 걸러낼 수 있었던 건 태그로 딱 떨어지는
생과일·채소뿐이고(PRODUCE_TAGS), 포장식품은 CU 데이터 안에 가를 신호가 없다.
자세한 전수 판정표와 남은 선택지는 notes/CU-NEW-AUDIT.md 에 적어뒀다.

## 등록일: 상품 데이터엔 없고, 이미지 CDN 헤더에 있다 (2026-10-01 실측)

목록·상세 어디에도 날짜 필드가 없다. 상세 HTML 에서 날짜처럼 보이는 문자열
(2019-05-23·2022-02-18·20230829 …)은 **상품이 달라도 집합이 완전히 같다**.
gdIdx 28374(과자)와 20533(즉석조리)을 받아 대조했고 한 글자도 다르지 않았다.
개발자가 script 태그에 남긴 주석과 에셋 버전이지 상품 등록일이 아니다.
`/brand_info/news_list.do` 의 '새로운소식'도 쓸 수 없다 — 50건을 받아보면
'9월 모아보기'·'9월 쓔퍼세일'·'CU Pay 허브페이지'처럼 전부 월간 행사 공지이고
상품 출시 기사가 아니다.

대신 **상품 이미지의 Last-Modified 헤더**가 등록 시점을 준다.
이미지는 `//<CDN>/product/<바코드>.jpg` 라 경로엔 타임스탬프가 없지만, 헤더엔 있다.
NEW 667건 전부에 HEAD 를 쳐서 받아본 결과:
  - 667건 **전부** Last-Modified 가 있다. 날짜는 29종이고 월요일에 몰린다
    (09-29 78건 · 09-15 50건 · 09-07 60건 · 08-31 60건 · 08-24 53건 …).
    상품 사진을 주 단위 배치로 올리는 운영이라 해상도는 '주' 단위다.
  - 등록 일련번호 gdIdx 와의 **스피어만 상관이 0.991** 이다. 역전을 따로 세봐도
    gdIdx<27600 중 9월 이후 날짜 0건, gdIdx>=28200 중 8/2 이전 날짜 0건이다.
    즉 이 집합 안에선 사진 재업로드로 옛 상품이 최근 날짜를 얻는 오염이 없다.
  - 가장 오래된 NEW 가 2026-05-11 이다. **NEW 배지가 143일까지 붙어 있다**는 뜻이고,
    배지만으로는 '오늘의 신상'이 될 수 없다는 근거다. 그래서 이 날짜를
    uploaded_at 으로 넘겨 collect 의 60일 창에 걸리게 한다.

⚠️ 이건 출시일이 아니라 **사진을 올린 배치 시각**이다. 그래서 released_at 이 아니라
uploaded_at 에 넣는다. 도미노처럼 사이트 개편으로 사진을 일괄 재업로드하면
옛 상품이 최근 날짜를 갖게 된다 — 실제로 NEW 가 아닌 구상품에서 그런 건을 봤다
(gdIdx 24212 할리스 아메리카노, 사진 2026-09-01). **NEW 로 거른 뒤에만** 이 날짜를
쓴다 — 배지 없이 날짜만으로 뽑으면 안 된다. 다만 배지가 그 오염을 막아준다고
썼던 건 틀렸다(위 절). 배지도 날짜도 출시일이 아니라 입점일을 가리킨다.
HEAD 는 상품당 한 번뿐이고 바코드 주소라 값이 안 바뀌므로 desc 와 같은 캐시를 탄다.

그리고 이 날짜는 **빼는 데만 쓰고 넣는 데는 쓰지 않는다**. 행사 라벨이 붙은
상품에는 아예 채우지 않는다(`_fill_uploaded`). 근거가 약한 날짜 하나로
'행사 라벨이 붙은 건 신상으로 올리지 않는다'는 규칙을 뒤집지 않기 위해서다.
2026-10-01 실측으로 효과를 둘 다 재봤다:
  - 날짜를 전건에 채우면 화면 496 → 395. 158건이 빠지고 **57건이 새로 붙는데
    그 57건이 전부 1+1·2+1 행사 상품**이다(collect.is_fresh 가 날짜가 있으면
    행사 veto 를 건너뛴다).
  - 행사 상품을 빼고 채우면 화면 496 → 338. 빠지는 158건은 그대로고 새로
    붙는 건 0건이다. 순수 감산이라 이쪽을 쓴다.

## 상품 분류: 1depth 7개로는 모자라고, 상세의 '태그'가 답이다 (2026-10-01 실측)

전체상품 메뉴의 7개(간편식사·즉석조리·과자류·아이스크림·식품·음료·생활용품)는
너무 거칠다. '간편식사' 하나에 도시락·김밥·샌드위치·버거가 다 들어 있어서
"도시락끼리 모아보기"가 안 된다. 더 좁힐 길을 둘 찾았고, 뒤엣것을 쓴다.

**① listForm 의 `searchSubCategory` (숨은 2depth).** 화면에 메뉴가 안 그려질 뿐
서버는 받아준다. 1~19 가 7개 대분류에 나뉘어 붙어 있다(간편식사 1·2·3,
즉석조리 4·5·6, 과자류 7·8, 아이스크림 9, 식품 10·11·12, 음료 13·14·15,
생활용품 16·17·18·19). 엄밀한 분할이라 좋지만 **이름이 없다**(사이트 어디에도
2depth 라벨이 안 나온다) — 내가 지어 붙여야 해서 안 썼다. 다만 아래 태그 표를
만들고 검산하는 데 썼다.

**② 상세 페이지의 `ul.prodTag` (쓰는 쪽).** 상품마다 CU 가 직접 붙인 분류 태그다
(예: '도시락'+'간편식사', '냉장디저트'+'디저트', '용기면'+'가공식사').
**요청이 하나도 안 는다** — `_fill_desc` 가 이미 상품마다 상세를 긁고 있고,
같은 응답에서 한 줄 더 읽을 뿐이다. NEW 619건 전수에 적용해 **폴백 0건**,
즉 전건이 태그로 분류됐다.

태그 뭉치는 지저분하다. 순서가 고정이 아니고(['스낵','과자류'] 와
['즉석조리','제조음료'] 가 섞여 나온다), 행사 배지(1+1·2+1)와 PB 이름
(PBICK·델라페·득템·405)이 같은 자리에 끼어든다. 그래서 '몇 번째 태그'가 아니라
**아래 TAG_CATEGORY 를 위에서부터 훑어 먼저 걸리는 것**을 쓴다. 좁은 이름이
앞, 넓은 이름이 뒤다(삼각김밥 → 김밥 → 간편식사 순).

눈으로 확인하고 알게 된 것들(고치지 말고 알고 있어라):
  - `면)미트볼듬뿍토마토면` 의 태그가 '도시락' 이다. CU 가 그렇게 분류했다.
    바로 옆 `면)함박듬뿍매콤라구면` 은 '조리면' 이라 라면으로 간다. 브랜드
    자체가 일관되지 않은 것이라 우리가 이름으로 덮어쓰지 않는다.
  - `튀김)애플파이` 의 태그가 '즉석후라이드·튀김류' 다. CU 튀김 매대는 치킨도
    파이도 같이 판다. 그래서 튀김류를 '치킨' 이 아니라 '즉석식' 으로 옮긴다.
  - '커피차류' 는 커피 전용이 아니라 커피·차 묶음이다(티젠 수박우롱아이스티가
    여기 걸린다). 커피로 옮기면 아이스티가 커피 칩에 뜬다 → 음료로 보낸다.
  - 핫도그 2건은 SUBS 에 자리가 없어 햄버거로 보낸다.

⚠️ **생활용품은 이름을 바꾸지 마라.** base.NONFOOD_CATEGORIES 가 읽는 값이고
지금 51건이 그걸로 굿즈로 빠진다. 화장품·스타킹·문구류처럼 더 좁은 태그가
있어도 전부 '생활용품' 한 값으로 모은다(NONFOOD_TAGS). 숙취해소제·건강기능식품도
먹는 것이긴 하지만 CU 가 생활용품 대분류에 넣었고 지금도 그렇게 걸러지고 있어서
그대로 둔다 — 바꾸면 굿즈 목록이 흔들린다.

상품명 접두(`도)`·`김)`·`샌)`)는 **쓰지 않는다.** 실제로 2depth 와 거의 맞지만
(sub=1 이 전부 `도)`·`면)`·`샐)`) 제조사 접두와 섞여서 못 가른다 — `삼립)`·
`롯데)`·`피치)`·`선명)` 이 전부 같은 모양이다. 사이트가 태그로 정답을 주는데
이름을 추론할 이유가 없다.

가격은 목록·상세 모두 들고 있지만(예: 5,500원) Item 에 담을 자리가 없어 버린다.

robots.txt 는 cu.bgfretail.com 도 이미지 CDN 도 404(규칙 없음)다. 명시적 허용이
아니므로 요청 간격을 넉넉히 둔다.
"""
import datetime
import email.utils
import re
import time

import httpx
from selectolax.parser import HTMLParser

from . import base
from .base import UA, Item

BRAND = "CU"
LIST_URL = "https://cu.bgfretail.com/product/productAjax.do"
VIEW_URL = "https://cu.bgfretail.com/product/view.do"
REFERER = "https://cu.bgfretail.com/product/product.do?category=product&depth2=4"

# 전체상품 페이지의 3depth 탭. gomaincategory() 가 넘기는 코드값 그대로다.
CATEGORIES = {
    "10": "간편식사", "20": "즉석조리", "30": "과자류", "40": "아이스크림",
    "50": "식품", "60": "음료", "70": "생활용품",
}
MAX_PAGES = 20   # 폭주 방지. 현재 최대 9페이지(식품)에서 NEW 가 끊긴다.
DELAY = 0.15     # 요청 간격. 상세까지 합쳐 700회쯤 두드리므로 반드시 둔다.
IMG_DELAY = 0.05  # 이미지는 원본 서버가 아니라 CDN 이라 간격을 조금 좁게 둔다.

# 2026-10-01 실측 베이스라인. 아래 가드가 이 수치를 근거로 '조용한 0건'을 막는다.
MEASURED_CARDS = 1200   # 7개 카테고리에서 읽은 카드 수
MEASURED_NEW = 667      # 그 중 NEW 배지가 붙은 수

# 상세의 ul.prodTag 태그 → 화면용 분류. **위에서부터 먼저 걸리는 것**을 쓰므로
# 좁은 이름이 앞, 넓은 이름이 뒤여야 한다(삼각김밥 → 김밥, 냉장디저트 → 디저트).
# 근거와 눈으로 확인한 예외는 모듈 docstring 참고. NEW 619건 전수 폴백 0건.
TAG_CATEGORY = (
    ("도시락", "도시락"), ("샐러드", "샐러드"),
    ("삼각김밥", "김밥"), ("주먹밥", "김밥"), ("김밥", "김밥"), ("유부", "김밥"),
    ("샌드위치", "샌드위치"), ("핫도그", "햄버거"), ("햄버거", "햄버거"),
    ("용기면", "라면"), ("봉지면", "라면"), ("조리면", "라면"), ("면류", "라면"),
    # 튀김 매대는 치킨도 파이도 같이 판다. 치킨으로 보내면 애플파이가 섞인다.
    ("즉석후라이드", "즉석식"), ("후라이드", "즉석식"), ("튀김류", "즉석식"),
    ("오뎅", "즉석식"),
    ("즉석도너츠", "도넛"), ("도너츠", "도넛"),
    ("베이커리", "베이커리"), ("빵", "베이커리"),
    ("즉석원두커피", "커피"), ("커피(자동)", "커피"), ("제조음료", "커피"),
    ("캔/병커피", "커피"), ("커피음료", "커피"),
    ("아이스크림케이", "아이스크림"), ("아이스크림", "아이스크림"),
    ("냉장디저트", "디저트"), ("디저트", "디저트"), ("푸딩", "디저트"), ("떡", "디저트"),
    ("냉장젤리", "과자"), ("소프트캔디", "과자"), ("기능성캔디", "과자"),
    ("토이캔디", "과자"), ("캔디류", "과자"), ("젤리", "과자"),
    ("초콜릿", "과자"), ("껌", "과자"), ("과자류", "과자"), ("스낵", "과자"),
    ("소스류", "조미료"), ("조미료류", "조미료"),
    ("마른안주류", "안주"), ("냉장안주", "안주"), ("안주류", "안주"),
    ("핫바", "안주"), ("육가공류", "안주"),
    ("즉석밥류", "즉석식"), ("즉석식", "즉석식"), ("가공식사", "즉석식"),
    ("간편식", "즉석식"),
    ("김치류", "식재료"), ("김치", "식재료"), ("반찬류", "식재료"),
    ("정육", "식재료"), ("채소", "식재료"), ("과일", "식재료"),
    ("통조림", "식재료"), ("가공란", "식재료"), ("치즈", "식재료"),
    ("김", "식재료"), ("햄", "식재료"), ("소시지", "식재료"), ("식재료", "식재료"),
    ("탄산음료", "음료"), ("탄산수", "음료"), ("건강음료", "음료"),
    ("기능건강음료", "음료"), ("에너지음료", "음료"), ("과즙음료", "음료"),
    ("차음료", "음료"), ("차류", "음료"),
    # 커피차류는 커피 전용이 아니라 커피·차 묶음이다(아이스티가 여기 걸린다).
    ("커피차류", "음료"),
    ("아이스드링크", "음료"), ("요구르트", "음료"), ("가공유", "음료"),
    ("흰우유", "음료"), ("우유", "음료"), ("논알콜맥주", "음료"), ("음료", "음료"),
)

# 생과일·채소. **신제품이 아니라서 아예 안 담는다**(fetch 끝에서 뺀다).
# CU 가 철마다 같은 농산물을 새 상품코드로 다시 올려서 NEW 배지가 붙는다 —
# 데일리)거봉컵200g(gdIdx 21368, NEW 없음)이 이미 있는데 데일리)거봉500g(팩)
# (28028)·거봉1kg(박스)(27977)이 NEW 로 올라온다. 거봉이 새로 나올 리 없다.
# 이름이 아니라 **태그 문자열을 통째로** 맞추므로 '카스/카스테라' 식 부분일치
# 사고가 없다. 2026-10-02 실측: CU 666건 중 과일 16·채소 4건, 전부 원물이고
# 다른 태그가 섞인 건 0건이다. 이름에 글자가 들어가는 포코피아)과일젤리와
# CJ)솥반뿌리채소영양밥은 태그가 달라서 안 걸린다(실측).
# ⚠️ '정육'(4건)은 일부러 뺐다. 도드람)한돈삼겹살300g 같은 원물과
# 미트)간장삼겹살구이350g 같은 양념 가공품이 같은 태그를 쓴다 — 가르는 신호가
# 없어서 넣으면 진짜 신상을 같이 떨어뜨린다. 남는 오탐 2건은 알고 두는 것이다.
PRODUCE_TAGS = frozenset({"과일", "채소"})
PRODUCE = "농산물"      # 이 분류가 붙으면 수집에서 뺀다. 화면엔 안 나간다.
# 원물에 같이 붙어도 되는 태그. 이것 말고 좁은 태그가 하나라도 더 있으면 원물로
# 안 본다(_category 참고). 실측 20건은 전부 과일·채소 + 식재료 조합이다.
PRODUCE_ONLY = PRODUCE_TAGS | {"식재료"}

# 전부 '생활용품' 한 값으로 모은다. ⚠️ base.NONFOOD_CATEGORIES 가 읽는 값이라
# 더 좁은 이름(화장품·스타킹·문구류)으로 쪼개면 굿즈 필터가 깨진다.
NONFOOD_TAGS = frozenset({
    "건강기능", "건강지향식품", "건강기능식품", "숙취해소제", "의약외품", "안전상비의약품",
    "화장품", "색조화장품", "바디케어", "미용소품", "목욕세면", "헤어스타일링",
    "면도용품", "구강용품", "위생용품", "생리용품", "콘돔", "신변잡화",
    "의류용품", "스타킹", "양말", "생활잡화", "문구류", "세제", "일회용품",
    "우산", "우천용상품", "통합교통카드", "이어폰", "소형가전",
    "사료", "반려동물용품", "생활용품",
})

# 1depth 이름은 분류 태그가 아니라 '넓은 묶음'이다. 좁은 태그를 다 훑은 뒤에만 본다.
_MAIN_TAGS = frozenset(CATEGORIES.values())

# 태그가 하나도 없을 때 떨어질 자리. 1depth 이름을 그대로 쓰되 다른 브랜드와
# 글자를 맞춘다('과자류'는 이마트24·화면 쪽 이름이 '과자'다).
MAIN_FALLBACK = {"과자류": "과자"}

# 태그에서 나올 수 있는 분류 값 전체. 캐시한 값이 아직 쓸 만한지 판정하는 데 쓴다.
# '식재료' 는 뺀다 — 과일·채소가 예전엔 그 값으로 저장됐다. 캐시를 태우면 위
# PRODUCE_TAGS 거르기가 **이미 받아둔 농산물에는 영영 안 걸린다**(상세를 다시
# 안 읽으니 태그를 못 본다). 2026-10-02 실측으로 상세 요청이 하루 **46건** 는다
# (남은 식재료 26건 + 매일 다시 받아서 버리는 농산물 20건 — 농산물은 수집에서
# 빠지니 products.json 에 안 남고, 그래서 캐시가 영영 안 생긴다. 알고 두는 비용이다).
RESOLVED_CATEGORIES = frozenset(
    [cat for _, cat in TAG_CATEGORY if cat != "식재료"] + ["생활용품"])


def _category(tags: list, main: str) -> str:
    """상세 태그에서 분류를 고른다. 못 고르면 1depth 이름을 그대로 둔다.

    1depth 이름(간편식사·식품 …)은 태그로도 붙는데 그건 '넓은 묶음'이라
    좁은 태그를 전부 훑은 **뒤에** 본다. 그래야 ['도시락','간편식사'] 에서
    도시락이 이긴다(순서가 고정이 아니라 ['간편식사','도시락'] 로도 온다).
    """
    t = set(tags)
    # 생과일·채소(fetch 가 여기서 걸러낸다). **좁은 태그가 그것뿐일 때만** 원물로
    # 본다. 먼저 보고 바로 반환하면 CU 가 가공품에 '과일'을 하나 더 붙이는 날
    # 그 상품이 말없이 사라진다 — ['과일','과즙음료'] 가 음료가 아니라 농산물이
    # 돼서 수집에서 빠진다. 지금은 공존 0건이지만 조용히 사라지는 길은 막는다.
    narrow = {tag for tag, _ in TAG_CATEGORY if tag in t and tag not in _MAIN_TAGS}
    if (narrow & PRODUCE_TAGS) and narrow <= PRODUCE_ONLY:
        return PRODUCE
    for tag, cat in TAG_CATEGORY:
        if tag in t and tag not in _MAIN_TAGS:
            return cat
    if t & NONFOOD_TAGS:
        return "생활용품"
    for tag, cat in TAG_CATEGORY:          # 여기까지 오면 1depth 태그뿐이다
        if tag in t:
            return cat
    # 태그가 아예 없는 상품. 전처럼 1depth 로 떨어뜨리되 이름만 통일한다
    # (실측 619건에선 한 건도 여기 안 왔다).
    return MAIN_FALLBACK.get(main, main)


def _text(node, sel):
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _gd_idx(card) -> str:
    """상세 링크가 a 태그로 없고 onclick="view(28352);" 로만 상품코드가 나온다."""
    for sel in (".prod_img", ".name"):
        n = card.css_first(sel)
        m = re.search(r"view\((\d+)\)", n.attributes.get("onclick", "") or "") if n else None
        if m:
            return m.group(1)
    return ""


def _view_url(gd: str) -> str:
    """상품 상세 주소. gdIdx 를 못 뽑았으면 빈 값(브랜드 메뉴 페이지로 폴백된다)."""
    return f"{VIEW_URL}?category=product&gdIdx={gd}" if gd else ""


def _labels(card) -> list:
    """1+1·2+1 배지는 span 글자로, NEW·BEST 태그는 img alt 로 붙어 있다."""
    out = []
    for sp in card.css(".badge span, .tag span"):
        t = " ".join(sp.text().split())
        if not t:
            img = sp.css_first("img")
            t = (img.attributes.get("alt", "") or "").strip() if img else ""
        t = t.upper()
        if t and t not in out:
            out.append(t)
    return out


def _promo(card) -> bool:
    """행사 상품. 마크업 주석 그대로 .badge > span.plus1 = 1+1, .plus2 = 2+1."""
    return card.css_first(".badge .plus1, .badge .plus2") is not None


def _form(cat: str, page: int) -> dict:
    """listForm 의 hidden 필드 그대로. setC=최신등록순, listType=1 은 이어붙이기."""
    return {"pageIndex": str(page), "searchMainCategory": cat, "searchSubCategory": "",
            "listType": "1", "searchCondition": "setC", "searchUseYn": "N",
            "gdIdx": "0", "codeParent": cat, "search1": "", "search2": "",
            "searchKeyword": ""}


def _fill_desc(client, items: list, gd_by_key: dict, known: dict) -> tuple:
    """상세를 상품당 한 번씩 긁어 **설명문과 분류**를 함께 채운다.

    설명문은 사실상 바뀌지 않는데 상품이 600건대라 매일 전량을 다시 긁으면
    하루 700요청이 된다. 이미 받아둔 건 재사용하고 새로 나타난 것만 긁는다.

    분류(ul.prodTag)도 같은 응답에서 읽으므로 **요청이 하나도 안 는다.**
    캐시는 설명문과 분류가 **둘 다** 쓸 만할 때만 탄다 — 설명문만 보고 건너뛰면
    분류가 영영 안 채워진다. '쓸 만한 분류'는 태그에서 나올 수 있는 값
    (RESOLVED_CATEGORIES)인지로 판정한다. 옛 수집분의 1depth 이름
    (간편식사·과자류·식품·즉석조리)은 거기 없으니 다시 긁는다.
      ⚠️ 음료·아이스크림·생활용품은 1depth 이름이면서 분류 값이기도 해서
      옛 값이 그대로 통과한다. 그 셋은 태그로 다시 풀어도 거의 같은 값이 나와
      (실측 115건 중 2건만 커피로 갈린다) 한 번 지나가는 오차로 두고 넘긴다.
      전량을 다시 긁으면 매일 115요청이 늘어난다.

    실패하면 설명문은 빈 값, 분류는 1depth 이름(= 예전 동작)으로 남는다.
    """
    fetched = tagged = 0
    for it in items:
        prev = known.get(it.key, {})
        cached_desc = prev.get("desc")
        cached_cat = prev.get("category")
        if cached_desc and cached_cat in RESOLVED_CATEGORIES:
            it.desc = cached_desc
            it.category = cached_cat
            tagged += 1
            continue
        gd = gd_by_key.get(it.key)
        if not gd:
            continue
        fetched += 1
        try:
            r = client.get(VIEW_URL, params={"category": "product", "gdIdx": gd})
            r.raise_for_status()
        except httpx.HTTPError:
            continue
        finally:
            time.sleep(DELAY)
        tree = HTMLParser(r.text)
        it.desc = " ".join(" ".join(n.text().split())
                           for n in tree.css(".prodExplain li")).strip()
        # ⚠️ 'ul.prodTag' 로만 고르면 안 된다. 상세 하단 '카테고리 베스트 상품'
        # 블록에 같은 클래스가 또 있어서 **옆 상품의 태그와 1+1·2+1 행사 라벨**
        # 까지 딸려 온다. 20건 표본에서 12건이 달랐다 —
        # 서주)포도젤로바 는 ['2+1','아이스크림','1+1','2+1','2+1','2+1'] 이고
        # 행사 라벨이 맨 앞이다. 아래 분류 표는 '먼저 걸리는 것' 을 쓰므로
        # 그 순서가 그대로 판정에 끼어든다. 자기 태그는 #taglist 하나다.
        tags = [" ".join(n.text().split())
                for n in tree.css("ul.prodTag#taglist li")]
        tags = [t for t in tags if t]
        if tags:
            it.category = _category(tags, it.category)
            tagged += 1
    return fetched, tagged


def _fill_uploaded(client, items: list, known: dict) -> int:
    """등록 시점. 상품 데이터엔 없고 이미지의 Last-Modified 헤더에만 있다.

    출시일이 아니라 사진을 올린 배치 시각이라 released_at 이 아니라 uploaded_at 이다.
    근거와 한계(주 단위 해상도, 재업로드 오염, NEW 로 거른 뒤에만 쓰는 이유)는
    모듈 docstring 에 적어뒀다.

    **행사 상품엔 날짜를 채우지 않는다.** 이 날짜는 '빼는 데'만 쓰고 '넣는 데'는
    쓰지 않는다는 뜻이다. collect.is_fresh() 는 날짜가 있으면 그걸 우선해서
    행사 라벨 veto 를 건너뛴다. 그런데 우리가 가진 건 출시일이 아니라 사진을 올린
    시각이라, 1+1 이 붙은 상품이 '갓 나와서 도입행사를 하는 것'인지 '옛 상품을
    행사에 올리며 사진을 다시 찍은 것'인지 구분해주지 못한다. 세븐일레븐
    '신상품' 탭이 바로 후자였다(해태 연양갱이 2+1 을 달고 신상품으로 올라온다).
    근거가 약한 날짜로 행사 veto 를 뒤집지 않는다 — 날짜를 채우면 행사 상품
    57건이 새로 화면에 오른다(2026-10-01 실측).

    desc 와 같은 이유로 캐시를 탄다 — 바코드 주소라 한 번 받은 값이 바뀌지 않는다.
    헤더가 없거나 실패하면 빈 값으로 둔다(없는 걸 지어내지 않는다).
    """
    fetched = 0
    for it in items:
        if it.promo:                       # 위 docstring: 행사 상품엔 안 채운다
            continue
        cached = known.get(it.key, {}).get("uploaded_at")
        if cached:
            it.uploaded_at = cached
            continue
        if not it.image:
            continue
        fetched += 1
        try:
            r = client.head(it.image)
            r.raise_for_status()
        except httpx.HTTPError:
            continue
        finally:
            time.sleep(IMG_DELAY)
        stamp = email.utils.parsedate(r.headers.get("last-modified") or "")
        if stamp:
            it.uploaded_at = datetime.date(*stamp[:3]).isoformat()
    return fetched


def fetch(known: dict | None = None) -> list[Item]:
    items: list[Item] = []
    gd_by_key: dict = {}
    seen_cards = 0
    headers = {"User-Agent": UA, "X-Requested-With": "XMLHttpRequest", "Referer": REFERER}
    with base.client(headers=headers) as c:
        for code, cat_name in CATEGORIES.items():
            for page in range(1, MAX_PAGES + 1):
                r = c.post(LIST_URL, data=_form(code, page))
                r.raise_for_status()
                cards = HTMLParser(r.text).css("li.prod_list")
                seen_cards += len(cards)
                # 카테고리 1페이지가 비는 건 정상일 수 없다(7개 전부 40건씩 온다).
                # 셀렉터나 폼 필드가 바뀌면 여기서 조용히 0건이 되므로 드러낸다.
                if page == 1 and not cards:
                    raise ValueError(
                        f"CU {cat_name}(code={code}) 1페이지가 비었다. "
                        f"응답 {len(r.text)}바이트 — li.prod_list 셀렉터나 "
                        f"listForm hidden 필드가 바뀌었는지 확인하라")

                fresh = 0
                for card in cards:
                    # 최신등록순이라 NEW 가 끊긴 뒤는 전부 구상품이다
                    if card.css_first(".tag .new") is None:
                        continue
                    fresh += 1
                    name = _text(card, ".name p")
                    if not name:
                        continue
                    img = card.css_first(".prod_img img")
                    src = (img.attributes.get("src", "") or "") if img else ""
                    gd = _gd_idx(card)
                    it = Item(
                        brand=BRAND,
                        name=name,
                        image="https:" + src if src.startswith("//") else src,
                        labels=_labels(card),
                        category=cat_name,
                        is_new=True,          # NEW 배지 = 브랜드가 붙인 최근등록 표시
                        promo=_promo(card),   # 1+1·2+1 은 행사로 따로 뺀다
                        # 상세는 어차피 _fill_desc 가 같은 gdIdx 로 긁는다. 요청은 안 늘고
                        # 사용자가 카드에서 바로 그 상품 페이지로 간다.
                        url=_view_url(gd),
                    )
                    if it.key in gd_by_key:
                        continue
                    gd_by_key[it.key] = gd
                    items.append(it)

                time.sleep(DELAY)
                # NEW 가 한 건도 없거나 더보기가 사라지면 이 카테고리는 끝
                if not cards or not fresh or "더보기" not in r.text:
                    break

        # NEW 가 전 카테고리에서 0건이면 그건 'CU 에 신상이 없는 날'이 아니라
        # .tag .new 가 바뀐 것이다(실측 1,200건 중 667건이 NEW 다).
        if not items:
            raise ValueError(
                f"CU 카드 {seen_cards}건을 읽었는데 NEW 가 0건이다 "
                f"(2026-10-01 실측 {MEASURED_CARDS}건 중 {MEASURED_NEW}건). "
                f"'.tag .new' 셀렉터가 바뀌었는지 확인하라")

        n, tagged = _fill_desc(c, items, gd_by_key, known or {})
        print(f"  CU 상세 요청 {n}건 (캐시 {len(items) - n}건) → 분류 "
              f"{tagged}/{len(items)}건")
        # 상세의 ul.prodTag 가 사라지면 분류가 통째로 1depth 7개로 돌아간다.
        # 목록은 멀쩡히 오니까 화면에선 '도시락 칩이 사라졌네' 로만 보인다.
        # 2026-10-01 실측은 NEW 619건 전건이 태그로 풀렸으므로 0건이면 고장이다.
        if items and not tagged:
            raise ValueError(
                f"CU {len(items)}건 전부 상세에서 분류 태그를 못 읽었다 "
                f"(2026-10-01 실측은 619건 전건이 풀렸다). "
                f"view.do 의 'ul.prodTag#taglist li' 가 바뀌었는지 확인하라")

        # 생과일·채소는 신제품이 아니다(PRODUCE_TAGS). 태그는 상세를 읽어야
        # 보이므로 여기서 뺀다 — 아래 이미지 HEAD 도 그만큼 덜 친다.
        raw = sum(1 for it in items if it.category == PRODUCE)
        if raw:
            items = [it for it in items if it.category != PRODUCE]
            print(f"  CU 생과일·채소 {raw}건 제외 (철마다 다시 올라오는 원물)")

    # 이미지는 원본이 아니라 CDN 이라 커넥션을 따로 연다.
    # (원본용 X-Requested-With·Referer 를 CDN 에 보낼 이유가 없다.)
    with base.client() as ic:
        n = _fill_uploaded(ic, items, known or {})
    want = sum(1 for it in items if not it.promo)   # 행사 상품은 애초에 안 채운다
    dated = sum(1 for it in items if it.uploaded_at)
    print(f"  CU 이미지 HEAD {n}건 (캐시 {want - n}건) → 등록일 {dated}/{want}건 "
          f"(행사 {len(items) - want}건 제외)")
    # 대상 전량에 날짜가 안 붙으면 60일 창이 못 걸려 배지만으로 전량이 통과한다.
    # 실측은 666건 중 대상 전건에 헤더가 있었으므로 0건이면 헤더가 사라진 것이다.
    if want and not dated:
        raise ValueError(
            f"CU 비행사 {want}건 전부 이미지 Last-Modified 를 못 받았다 "
            "(2026-10-01 실측은 666건 전건에 헤더가 있었다). CDN 이 헤더를 "
            "끊었는지 확인하라 — 날짜 없이 NEW 배지만 믿으면 143일치가 통째로 올라온다")
    return items
