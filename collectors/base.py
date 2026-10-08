from dataclasses import dataclass, asdict, field
import os
import re
import time

import httpx

import taxonomy

# 공개 봇이니 신원을 밝힌다. 브라우저를 위장하면 사이트 운영자가 우리를 식별하거나
# 연락하거나 선별 차단할 방법이 없다. robots.txt 의 UA별 규칙에도 매칭되지 않는다.
UA = "sinsang-note/1.0 (+https://github.com/ttop32/sinsang-note)"


# 괄호 안이 '같은 상품의 사이즈·온도 표기'일 때만 턴다.
# 예전엔 괄호를 통째로 지웠는데 그러면 맛·종류 변형까지 합쳐져 상품이 사라졌다.
# 미스터피자 '더블치즈(씬)' 9건이 클래식에 흡수됐고, bhc 크리스피번 3종과
# 파파존스 파스타 3종도 각각 1건이 됐다.
_SIZE = re.compile(
    r"^(L|M|S|XL|EX|대|중|소|Mini|Regular|Large|HOT|ICE|ICED|아이스|핫|"
    r"\d+\s*(ml|mL|L|g|G|kg|인분|개입|P|입))$", re.I)


def make_key(brand: str, name: str) -> str:
    """중복 판정 키. 사이즈·온도 표기만 털고 나머지 괄호 내용은 남긴다."""
    def drop(m):
        inner = m.group(1).strip()
        return "" if _SIZE.match(inner) else m.group(0)
    n = re.sub(r"\(([^)]*)\)", drop, name)
    n = re.sub(r"\s+", "", n)
    return f"{brand}:{n}"


# 브랜드 유형. 화면에서 이 축으로 나눠 보여준다.
CVS = "편의점"
CAFE = "카페"
FRANCHISE = "프랜차이즈"
MAKER = "제조사"     # 편의점에 상품을 넣는 식품 제조사. 보도자료가 출시일을 준다

# 브랜드 → (유형, 세부분류). 어댑터가 각자 선언하면 표기가 어긋나므로 여기 한 곳에 둔다.
# 세부분류는 프랜차이즈에서만 쓴다(햄버거/피자/치킨).
# 빵집·빙수·아이스크림·도넛은 '외식'이 아니라 카페로 묶는다. 한국에서는
# 끼니가 아니라 커피 옆에서 먹는 것이고, 사용자가 찾는 자리도 거기다.
BRANDS = {
    "메가MGC커피": (CAFE, "커피"),
    "스타벅스":    (CAFE, "커피"),
    "이디야커피":  (CAFE, "커피"),
    "설빙":        (CAFE, "빙수"),
    "빽다방":      (CAFE, "커피"),
    "커피빈":      (CAFE, "커피"),
    "폴바셋":      (CAFE, "커피"),
    "CU":         (CVS, ""),
    "세븐일레븐":  (CVS, ""),
    "이마트24":    (CVS, ""),
    "GS25":       (CVS, ""),
    "맘스터치":    (FRANCHISE, "햄버거"),
    "버거킹":      (FRANCHISE, "햄버거"),
    "BBQ":        (FRANCHISE, "치킨"),
    "bhc치킨":     (FRANCHISE, "치킨"),
    "교촌치킨":    (FRANCHISE, "치킨"),
    "피자헛":      (FRANCHISE, "피자"),
    "미스터피자":  (FRANCHISE, "피자"),
    "파파존스":    (FRANCHISE, "피자"),
    "도미노피자":  (FRANCHISE, "피자"),
    "피자스쿨":    (FRANCHISE, "피자"),
    "피자마루":    (FRANCHISE, "피자"),
    "굽네치킨":    (FRANCHISE, "치킨"),
    "처갓집양념치킨": (FRANCHISE, "치킨"),
    "푸라닭":      (FRANCHISE, "치킨"),
    "부어치킨":    (FRANCHISE, "치킨"),
    "또래오래":    (FRANCHISE, "치킨"),
    "자담치킨":    (FRANCHISE, "치킨"),
    "땅땅치킨":    (FRANCHISE, "치킨"),
    "페리카나":    (FRANCHISE, "치킨"),
    "바른치킨":    (FRANCHISE, "치킨"),
    "누구나홀딱반한닭": (FRANCHISE, "치킨"),
    "후라이드 참 잘하는집": (FRANCHISE, "치킨"),
    "꾸브라꼬숯불치킨": (FRANCHISE, "치킨"),
    "치킨플러스":  (FRANCHISE, "치킨"),
    "멕시카나":    (FRANCHISE, "치킨"),
    "호식이두마리치킨": (FRANCHISE, "치킨"),
    "60계":       (FRANCHISE, "치킨"),
    "네네치킨":    (FRANCHISE, "치킨"),
    "가마치통닭":  (FRANCHISE, "치킨"),
    "노랑통닭":    (FRANCHISE, "치킨"),
    "프랭크버거":  (FRANCHISE, "햄버거"),
    "맥도날드":    (FRANCHISE, "햄버거"),
    "롯데리아":    (FRANCHISE, "햄버거"),
    "노브랜드버거": (FRANCHISE, "햄버거"),
    "왓더버거":    (FRANCHISE, "햄버거"),
    "쉐이크쉑":    (FRANCHISE, "햄버거"),
    "파이브가이즈": (FRANCHISE, "햄버거"),
    "버거운버거":  (FRANCHISE, "햄버거"),
    "오뚜기":      (MAKER, "라면"),
    "팔도":        (MAKER, "라면"),
    "오리온":      (MAKER, "과자"),
    "롯데칠성음료": (MAKER, "음료"),
    # 직영몰이라 남의 브랜드도 판다. 그래도 '제조사' 로 두는 건 1단 '가공식품' 이
    # 누가 만들었나가 아니라 무엇이냐 축이기 때문이다(TAXONOMY §3). 세부분류를
    # '음료' 가 아니라 '냉동식품' 으로 둔 근거는 collectors/fredit.py docstring.
    # 주류 제조사 중 유일하게 넣을 수 있는 곳이다. 나머지 12곳은 성인 인증
    # 게이트 뒤이거나 뉴스가 멈췄다(notes/CANDIDATES-ALCOHOL.md).
    # 카페·디저트·분식 중위권. 가드(collect.orphans)가 잡아낸 미등록분이다.
    "카페봄봄":     (CAFE, "커피"),
    "커피베이":     (CAFE, "커피"),
    "하이오커피":   (CAFE, "커피"),
    "카페만월경":   (CAFE, "커피"),
    # 🔴 아래 넷은 **CAFE 다. FRANCHISE 가 아니다.** 미등록분을 일괄로 붙일 때
    # 전부 FRANCHISE 로 들어갔는데, 그러면 taxonomy.primary_of() 가 '외식' 을
    # 줘서 **같은 업종이 1단 탭 두 곳으로 갈린다** — 설빙·배스킨라빈스·요아정은
    # '카페' 에 있는데 빙동댕·타래퀸만 '외식' 에 앉는다. 이 파일 맨 위 규칙이
    # "빵집·빙수·아이스크림·도넛은 '외식'이 아니라 카페로 묶는다" 이고,
    # 공정위도 이 넷을 설빙·배스킨라빈스와 **같은 업종(K1 아이스크림/빙수)**
    # 으로 묶는다(2026-10-03 등록 71건 직접 확인).
    # 달롱도르는 세부분류도 고쳤다 — 정식명이 '달롱도르요거트아이스크림' 이라
    # '디저트'(편의점이 쓰는 칸)가 아니라 요아정과 같은 '아이스크림' 이 맞다.
    "빙동댕":       (CAFE, "빙수"),
    "달롱도르":     (CAFE, "아이스크림"),
    "에밀리아젤라또": (CAFE, "아이스크림"),
    "타래퀸":       (CAFE, "빙수"),
    "빨라쪼":       (CAFE, "아이스크림"),   # 공정위 영업표지 `빨라쪼 델 프레도`, 젤라또
    "33떡볶이":   (FRANCHISE, "분식"),
    "병아리김밥":   (FRANCHISE, "분식"),
    "김밥킹":       (FRANCHISE, "분식"),
    "모락떡볶이":   (FRANCHISE, "분식"),
    "태리로제떡볶이": (FRANCHISE, "분식"),
    "떡군이네떡볶이": (FRANCHISE, "분식"),
    "백억커피":     (CAFE, "커피"),
    "디저트39":   (CAFE, "디저트"),
    "엽기떡볶이":  (FRANCHISE, "분식"),
    "앤티앤스":     (CAFE, "베이커리"),
    "송사부고로케": (CAFE, "베이커리"),
    # 프리미엄 아이스크림 브랜드다. 자사몰 카테고리 실측이 아이스크림 20 ·
    # 프리팩 8 · 아이스크림 케이크 11 · 커피/음료 11 · 디저트 3 이고 홈에
    # '아이스크림' 이 9회 '음료' 가 2회 나온다. '디저트' 는 편의점이 쓰는
    # 칸이라 달롱도르를 같은 사유로 옮긴 선례가 바로 위에 있다 —
    # 설빙·배스킨라빈스·요아정·에밀리아젤라또와 같은 칸이 맞다.
    "벤슨":        (CAFE, "아이스크림"),
    "더플레이스":   (FRANCHISE, "양식"),
    "제일제면소":   (FRANCHISE, "한식"),
    "하이트진로":  (MAKER, "주류"),
    "하림":         (MAKER, "냉동식품"),
    "하림산업":     (MAKER, "식재료"),
    "아워홈":      (MAKER, "냉동식품"),
    "동서식품":    (MAKER, "커피"),
    "샘표":        (MAKER, "조미료"),
    # 2026-10-02 추가. 과자·음료 제조사 전수 조사(notes/MAKER-SNACK-DRINK.md)에서
    # 나온 분이다. 전부 보도자료형(오리온 계보)이고, 신상 판정 근거와 함정은
    # 각 어댑터 docstring 에 적혀 있다.
    #   해태제과식품 — 뉴스 JSON API. 제품 API 의 createdDttm·productNewIconYn 은
    #                 일괄등록·늙은 배지라 안 쓴다
    #   크라운제과   — 보도자료(날짜) + 제품 카탈로그(사진). ⚠️1페이지 10.8MB
    #   롯데웰푸드   — 등록일이 일괄이라 released_at 을 비우고 uploaded_at 만 쓴다.
    #                 전엔 robots 404+HTML·noindex·약관 때문에 뺐는데,
    #                 운영자가 robots·약관 제약 무시를 승인해 등록한다
    #   삼양식품     — 보도자료 '제품뉴스' 탭(035002). 사진 없음(상세가 base64)
    #   빙그레       — 보도자료. 사진은 상세에서 한 장
    #   매일유업     — 보도자료 11건뿐(게시판 초기화). ⚠️robots 에 `*` 그룹 없음
    #   하이트진로음료 — 무알코올·생수·탄산 자회사. 사진 없음(상세가 JS).
    #                   ⚠️테라 제로·하이트제로(논알코올 맥주)는 어댑터가 뺀다
    "해태제과식품": (MAKER, "과자"),
    "크라운제과":  (MAKER, "과자"),
    "롯데웰푸드":  (MAKER, "과자"),
    "삼양식품":    (MAKER, "라면"),
    "빙그레":      (MAKER, "음료"),
    "매일유업":    (MAKER, "음료"),
    "하이트진로음료": (MAKER, "음료"),
    # 같은 조사의 냉동·간편식 분. 셋 다 계열사가 섞여 들어와서 어댑터가
    # 주어(회사명) 화이트리스트로 거른다 — 건기식·급식·펫푸드·제분은 뺀다.
    #   풀무원     — 뉴스룸 '브랜드 뉴스' 탭(menu=312). ⚠️날짜가 `2026년 9월 23일`
    #   동원F&B    — 보도자료. ⚠️1페이지 8건이 상한이다(2페이지가 Ajax)
    #   사조대림   — 신제품 전용 게시판. 제목 접두 `[계열사]` 로 거른다
    #                (⚠️CI 이미지의 alt 는 어긋난다 — 사조펫 글에 사조동아원 CI)
    "풀무원":      (MAKER, "냉동식품"),
    "동원F&B":     (MAKER, "냉동식품"),
    "사조대림":    (MAKER, "냉동식품"),
    # SPC삼립 — 보도자료 JSON API(`/api/public/press-releases`). 2차가
    # `/brand/bakery` 한 경로만 보고 "신제품 신호 없음" 으로 접었는데,
    # **출시 밀도가 이번 조사 1위**다(120건 중 81건이 출시 기사, 68%).
    # ⚠️세부분류가 '과자' 가 아니라 '베이커리' 인 이유: 삼립은 빵·호빵·떡이
    #   중심이고 과자(파삭칩·누네띠네)는 그중 일부다(어댑터 docstring).
    "SPC삼립":     (MAKER, "베이커리"),
    # ── 라면·냉동식품·냉동피자 전수 조사(2026-10-02) ───────────────────
    # 순위표·불가 사유는 notes/CANDIDATES-RAMEN-FROZEN.md.
    #   농심      — 라면 점유율 1위. 본사 보도자료는 **죽어 있어서**(브라우저로
    #               열어도 목록이 빈 화면) 브랜드관 신제품 면을 읽는다. 날짜가
    #               없어 이미지 파일명의 epoch 를 uploaded_at 에 넣는다.
    #   CJ제일제당 — 냉동·간편식 1위. 보도자료 밀도가 낮다(3개월 2건)
    #   신세계푸드 — 이마트 피자(냉동피자) 축의 유일한 국내 소스. 3개월 1~2건
    # ⚠️ 농심·CJ 는 1차 조사가 'robots 전면차단' 으로 접었던 곳이다. 운영자
    #    판단으로 수집하되 **UA 위장은 하지 않는다**. 삭제 요청이 오면 즉시 내린다
    #    (이마트24·도미노피자와 같은 칸).
    # ⚠️ 냉동피자는 `피자` 가 아니라 `냉동식품` 으로 둔다. `피자` 칸은 도미노·
    #    피자헛 같은 **외식** 프랜차이즈가 쓰고 있고, brand_sub 는 상품별이 아니라
    #    브랜드 단위라서 냉동피자 전업사가 없는 지금 구조로는 종합식품사를
    #    통째로 `피자` 로 찍게 된다. 근거는 위 노트 §냉동피자 분류.
    "농심":        (MAKER, "라면"),
    "CJ제일제당":  (MAKER, "냉동식품"),
    "신세계푸드":  (MAKER, "냉동식품"),
    # 면·소스 전문기업. **라면 제조사가 아니다** — 국내 라면은 농심 55.5% ·
    # 오뚜기 21.1% · 삼양식품 12.1% · 팔도 8.6% 로 상위 4사가 97.3% 이고 넷 다
    # 이미 붙어 있다. 면사랑은 그 바깥의 냉동면·생면·밀키트·육수 축이라
    # '라면' 이 아니라 '냉동식품' 으로 둔다.
    "면사랑":      (MAKER, "냉동식품"),
    # 대상(청정원). **냉동식품이 아니라 조미료**다 — 호밍스·안주야 라인이 있지만
    # 본체는 장류·소스·조미료고 실측 수집분도 전부 조미료였다(알룰로스·피클링소스·
    # 화이트식초). 샘표와 같은 칸에 둔다. 근거는 collectors/maker_daesang.py docstring.
    # ⚠️ 사진은 `/common/popup/download.jsp` 로 와서 octet-stream 이다.
    #    rules.verify_images() 가 전부 지운다 — 알고 넣은 것이니 '깨졌다'고 읽지 마라.
    "대상":        (MAKER, "조미료"),
    # 빙과 **전업** 제조사. 국내 빙과는 롯데웰푸드 39.8% · 빙그레 28.1% ·
    # 해태아이스크림 14.6% 로 셋이 83% 고, 그 아래 전업사는 ㈜서주와 ㈜라벨리
    # 둘뿐이다. 군납·PB 비중이 커서 자사 브랜드 신제품이 드물다 —
    # **0건이 정상**이고 '수집 실패'가 아니다(theborn 과 같은 칸).
    "라벨리":      (MAKER, "아이스크림"),
    "배스킨라빈스": (CAFE, "아이스크림"),
    # ── 아이스크림·빙수 전수 조사(2026-10-03) ─────────────────────────
    # 순위는 공정위 `아이스크림/빙수`(K1) 가맹점 수. 2026-10-03 에 등록 71건을
    # 직접 받아 확인했다(notes/FRANCHISE-MASTER.md §디저트/아이스크림).
    # ⚠️ 공정위에 **같은 회사가 두 줄**로 올라 있다 —
    #    `카페요아정` 372개 · `요거트아이스크림의 정석` 187개.
    #    사업자등록번호가 `696-86-02195` 로 같다(상호만 트릴리언즈 → 요아정).
    #    브랜드를 둘로 넣으면 같은 상품이 두 번 올라가므로 **하나로 합친다.**
    # ⚠️ 공지 게시판이 2025-02-10 에서 멈춰 있어 **0건이 정상**이다.
    #    theborn 과 같은 칸이다 — '수집 실패'로 읽지 마라.
    "요아정":      (CAFE, "아이스크림"),
    "던킨":        (CAFE, "도넛"),
    "이삭토스트":  (FRANCHISE, "샌드위치"),
    "파리바게뜨":  (CAFE, "베이커리"),
    "뚜레쥬르":    (CAFE, "베이커리"),
    "나폴레옹과자점": (CAFE, "베이커리"),
    "브레댄코":    (CAFE, "베이커리"),
    "홍루이젠":    (CAFE, "베이커리"),
    "노티드":      (CAFE, "베이커리"),
    "삼송빵집":    (CAFE, "베이커리"),
    "본죽":        (FRANCHISE, "한식"),
    "본죽&비빔밥":  (FRANCHISE, "한식"),
    "본도시락":    (FRANCHISE, "도시락"),
    "본설렁탕":    (FRANCHISE, "한식"),
    "본우리반상":  (FRANCHISE, "한식"),
    "멘지":        (FRANCHISE, "일식"),
    "본흑염소·능이삼계탕": (FRANCHISE, "한식"),
    "이지브루잉커피": (CAFE, "커피"),
    "요거프레소":  (CAFE, "커피"),
    "매머드커피":  (CAFE, "커피"),
    "더벤티":      (CAFE, "커피"),
    "컴포즈커피":  (CAFE, "커피"),
    "투썸플레이스": (CAFE, "커피"),
    "엔제리너스":   (CAFE, "커피"),
    "할리스":      (CAFE, "커피"),
    "탐앤탐스":    (CAFE, "커피"),
    "블루샥":      (CAFE, "커피"),
    "공차":        (CAFE, "커피"),
    "카페051":     (CAFE, "커피"),
    "우지커피":    (CAFE, "커피"),
    "팔공티":      (CAFE, "커피"),
    "카페베네":    (CAFE, "커피"),
    "읍천리382":   (CAFE, "커피"),
    "파스쿠찌":    (CAFE, "커피"),
    "텐퍼센트커피": (CAFE, "커피"),
    "카페인중독":  (CAFE, "커피"),
    "하삼동커피":  (CAFE, "커피"),
    # (주)프로젝트비 한 본사의 두 브랜드. 어댑터도 collectors/cafe_projectb.py 하나다.
    "고망고":      (CAFE, "커피"),
    "차얌":        (CAFE, "커피"),
    "달리는커피":  (CAFE, "커피"),
    "쥬씨":        (CAFE, "커피"),
    "매스커피":    (CAFE, "커피"),
    "김밥천국":    (FRANCHISE, "분식"),
    "바르다김선생": (FRANCHISE, "분식"),
    "죠스떡볶이":  (FRANCHISE, "분식"),
    "명랑핫도그":  (FRANCHISE, "분식"),
    # 분식은 공정위 업종 분류를 따라 김밥·떡볶이·우동을 한 칸으로 묶는다.
    # 화면에서 '김밥' 을 따로 떼면 김가네·얌샘김밥처럼 김밥집이면서 밥·분식을
    # 같이 파는 곳이 두 칸에 걸쳐 앉는다.
    "얌샘김밥":    (FRANCHISE, "분식"),
    "김가네":      (FRANCHISE, "분식"),
    "스쿨푸드":    (FRANCHISE, "분식"),
    "토마토도시락": (FRANCHISE, "도시락"),
    "슬로우캘리":  (FRANCHISE, "샐러드"),
    "포케올데이":  (FRANCHISE, "샐러드"),
    "삼첩분식":    (FRANCHISE, "분식"),
    "국수나무":    (FRANCHISE, "분식"),
    "애플꼬마김밥": (FRANCHISE, "분식"),
    "싸다김밥":    (FRANCHISE, "분식"),
    "스시로":      (FRANCHISE, "일식"),
    # ── 더본코리아 외식 브랜드 ─────────────────────────────────────────
    # theborn.co.kr/brand/representation/ 의 '대표 브랜드' 20개 중 빽다방을 뺀
    # 19개다(빽다방은 cafe_paikdabang.py 담당). 2026-10-02 실측 목록이다.
    # 담당 어댑터는 둘로 갈린다.
    #   한신포차            collectors/hanshinpocha.py — 자기 사이트가 상품별
    #                       날짜를 준다(RSS pubDate). 메뉴 52건을 그대로 받는다.
    #   나머지 18개          collectors/theborn.py — **본사 보도자료에만** 나온다.
    # ⚠️ 그 18개는 브랜드 메뉴 사이트에 신제품 신호가 하나도 없어서 메뉴판을
    #    긁지 않는다(사유는 theborn.py docstring §2). 보도자료가 없는 브랜드는
    #    0건이 정상이다 — 등록은 해 두되 '수집 실패'로 읽지 마라.
    # ⚠️ 한 브랜드를 두 어댑터에 걸치지 마라. collect 는 어댑터 사이 중복 키를
    #    걸러주지 않아서 같은 상품이 두 줄로 들어간다.
    "빽보이피자":   (FRANCHISE, "피자"),
    "역전우동0410": (FRANCHISE, "일식"),
    "홍콩반점0410": (FRANCHISE, "중식"),
    "리춘시장":     (FRANCHISE, "중식"),
    "고투웍":       (FRANCHISE, "중식"),
    "홍콩분식":     (FRANCHISE, "분식"),
    "새마을식당":   (FRANCHISE, "한식"),
    "한신포차":     (FRANCHISE, "한식"),
    "백스비어":     (FRANCHISE, "한식"),
    "제순식당":     (FRANCHISE, "한식"),
    "원조쌈밥집":   (FRANCHISE, "한식"),
    "본가":         (FRANCHISE, "한식"),
    "인생설렁탕":   (FRANCHISE, "한식"),
    "막이오름":     (FRANCHISE, "한식"),
    "돌배기집":     (FRANCHISE, "한식"),
    "미정국수0410": (FRANCHISE, "한식"),
    "성성식당":     (FRANCHISE, "한식"),
    "연돈볼카츠":   (FRANCHISE, "도시락"),
    # 파스타다. taxonomy.SUBS 에 '양식' 칸을 새로 만들어 붙였다 —
    # 전에는 맞는 칸이 없어서 비워뒀고 그러면 2단 칩에서만 안 보였다.
    "롤링파스타":   (FRANCHISE, "양식"),
    "아웃백스테이크하우스": (FRANCHISE, "양식"),
    "빕스":        (FRANCHISE, "양식"),
    # ── 중식 (2026-10-02 공정위 가맹점수 전수조사로 합류) ────────────────
    # 공정위 `중식`(C1) 등록 313개 / 가맹점 5개 이상 99개를 가맹점 수 순으로
    # 전수 훑었다. 근거와 전체 순위표는 notes/CANDIDATES-CHINESE.md.
    # 더본코리아 계열(홍콩반점0410·리춘시장·고투웍)은 위 더본 블록에 이미 있다.
    #
    # ⚠️ **중식은 메뉴판을 긁으면 안 되는 업종이다.** 상위권 상당수가 마라탕
    #    브랜드인데 그쪽 '메뉴 페이지'는 상품이 아니라 **탕에 넣는 재료 목록**
    #    (청경채·분모자·팽이버섯…)이다. 긁으면 재료 70~80개가 전부 '신상'이
    #    된다. 그래서 대부분 **보도자료·공지 게시판**에서 날짜와 함께 뽑는다
    #    (GS25·오뚜기·오리온과 같은 방식).
    # ⚠️ 수집량이 브랜드당 **연 1~4건**으로 적다. 0건이 '수집 실패'가 아니다.
    "탕화쿵푸마라탕": (FRANCHISE, "중식"),   # 1위 492개
    "춘리마라탕":   (FRANCHISE, "중식"),   # 3위 202개
    "보배반점":     (FRANCHISE, "중식"),   # 4위 198개
    "소림마라":     (FRANCHISE, "중식"),   # 6위 137개
    "라홍방마라탕": (FRANCHISE, "중식"),   # 8위 129개
    "짬뽕관":       (FRANCHISE, "중식"),   # 15위 62개
    "홍짜장":       (FRANCHISE, "중식"),   # 18위 58개
    "미미관마라탕": (FRANCHISE, "중식"),   # 25위 40개
    "짬뽕10101":    (FRANCHISE, "중식"),   # 33위 29개
    "삼삼마라":     (FRANCHISE, "중식"),   # 94위 5개. 꼬리인데 신호가 깨끗하다
    "KFC":         (FRANCHISE, "치킨"),
    "에그드랍":    (FRANCHISE, "샌드위치"),
    "써브웨이":    (FRANCHISE, "샌드위치"),
    "퀴즈노스":    (FRANCHISE, "샌드위치"),
    "쉬즈베이글":  (FRANCHISE, "샌드위치"),
    "참토스트":    (FRANCHISE, "샌드위치"),
    "잇샌드":      (FRANCHISE, "샌드위치"),
    # 공정위 등록명은 SSOJA 지만 사이트 자신은 쏘자토스트/SSOJATOAST 로 쓴다.
    # 공정위 업종은 패스트푸드인데 실제로는 토스트·핫도그라 이삭토스트·참토스트와
    # 같은 칸에 둔다.
    "쏘자토스트":  (FRANCHISE, "샌드위치"),
    "지미존스":    (FRANCHISE, "샌드위치"),
    "샐러디":      (FRANCHISE, "샐러드"),
    # ── 돈까스 (2026-10-02 공정위 가맹점수 전수조사로 합류) ──────────────
    # 돈까스는 '일식' 으로 넣는다. 공정위 업종 분류에서도 돈까스 전문점 다수가
    # `일식` 에 등록돼 있고(백소정·하루엔소쿠·유미카츠·카츠백…), 나머지가
    # `서양식`·`기타 외식`·`분식` 으로 흩어져 있어 공정위 칸을 그대로 쓰면
    # 같은 업종이 네 칸으로 쪼개진다. 화면에서 찾는 자리는 한 곳이어야 한다.
    "백소정":      (FRANCHISE, "일식"),
    "미소야":      (FRANCHISE, "일식"),
    "긴자료코":    (FRANCHISE, "일식"),
    "하루엔소쿠":  (FRANCHISE, "일식"),
    "홍익돈까스":  (FRANCHISE, "일식"),
    "브라운돈까스": (FRANCHISE, "일식"),
    # ── 일식 (돈까스 외) ──────────────────────────────────────────────
    "쿠우쿠우":    (FRANCHISE, "일식"),
    "미카도스시":  (FRANCHISE, "일식"),
    "모토이시":    (FRANCHISE, "일식"),
    "동경에서먹었던규동": (FRANCHISE, "일식"),
    # ── 한식 ─────────────────────────────────────────────────────────
    # 한솥만 '도시락' 이다. 공정위 업종은 `한식` 이지만 파는 게 도시락이고
    # 본도시락·토마토도시락과 같은 칸에 있어야 사용자가 찾는다.
    "한솥":        (FRANCHISE, "도시락"),
    "두찜":        (FRANCHISE, "한식"),
    "담꾹":        (FRANCHISE, "한식"),
    "유가네":      (FRANCHISE, "한식"),
    "오봉집":      (FRANCHISE, "한식"),
    "큰맘할매순대국": (FRANCHISE, "한식"),
    "원할머니보쌈족발": (FRANCHISE, "한식"),
    "마왕족발":    (FRANCHISE, "한식"),
    "박가부대":    (FRANCHISE, "한식"),
    # 아래 셋은 robots.txt 는 허용하지만 이용약관이 수집·복제를 금지한다.
    # 운영자 판단으로 수집하되, 삭제 요청이 오면 다투지 말고 즉시 내린다.
    #   이마트24  — 약관 제8조 ⑧ "크롤러, 매크로 프로그램, 스파이더, 스크래퍼 등… 수집"
    #   도미노피자 — 푸터 "사전 서면동의 없이 정보·콘텐츠를 상업적 목적으로 스크래핑"
    #   폴바셋    — 약관 v9.0 "사전 승낙 없이 복제 또는 유통하거나 상업적으로 이용"
    #   동서식품   — 약관 제13조 ② "동서식품을 이용함으로써 얻은 정보를 사전승낙
    #               없이 복제·전송·출판·배포… 영리목적으로 이용하여서는 안 됩니다".
    #               크롤러·스크래퍼 금지 조항은 없다. 제2조가 '이용자' 를 회원으로
    #               정의하고 '영리목적' 단서가 붙어 그대로 걸리는지는 애매하다.
    #   가마치통닭 — 약관 제10호 "회사의 승인 없이 회사 인터넷 사이트의 서비스 정보
    #               또는 개인정보를 복제 또는 유통시키거나 상업적으로 이용". 단 그
    #               조항이 '회원의 의무' 절 안이라 비회원 크롤러에 걸리는지는 애매하다.
    #   샘표      — 같은 성격의 복제·배포 제한. 단 그 조항이 '새미네부엌 커뮤니티'
    #               절 안에 있어 보도자료실에 걸리는지 애매하다. 크롤러 금지 없음.
    #
    # 빕스·뚜레쥬르는 robots 가 Googlebot 외 전면 차단이지만 2026-10-02
    # 운영자 판단으로 무시하고 2026-10-08 에 등록했다(롯데리아와 같은 칸).
    # 재검토 기록은 notes/RECHECK-ROBOTS-DINING.md.
    #
    # GS25 는 2026-10-01 에 등록했다. 상품 목록은 여전히 수집 불가다 —
    # gs25.gsretail.com 이 전 경로 본사 SPA 로 리다이렉트되고, 앱(우리동네GS)의 웹 짝인
    # m.woodongs.com 에도 상품 라우트가 없다. 대신 본사 보도자료에서 오뚜기·오리온과
    # 같은 방식으로 신제품만 뽑는다. 자세한 근거는 collectors/gs25.py docstring 참고.
    # 롯데리아는 2026-10-02 에 등록했다. lotteeatz.com/robots.txt 는 여전히 알려진 봇
    # 티어 외 모든 UA 를 Disallow: / 로 막지만, **운영자 판단으로 robots 를 무시**하기로
    # 했다(UA 는 위장하지 않고 sinsang-note 그대로 밝힌다). 수집하는 곳은 주문 플로우가
    # 아니라 브랜드 메뉴 면 /brand/ria 다 — 매장코드·세트·할인·품절이 섞이지 않는다.
    # 근거는 collectors/burger_lotteria.py docstring 참고.
}


# 상품 상세 페이지가 없는 브랜드를 위한 폴백. 카드를 누르면 최소한 그 브랜드
# 메뉴 페이지로는 가야 한다. 트래픽을 브랜드로 돌려주는 게 이 링크의 목적이다.
SITES = {
    "메가MGC커피":  "https://www.mega-mgccoffee.com/menu/",
    "스타벅스":     "https://www.starbucks.co.kr/menu/drink_list.do",
    "이디야커피":   "https://www.ediya.com/contents/drink.html",
    "설빙":         "https://sulbing.com/menu/",
    "빽다방":       "https://paikdabang.com/menu/menu_new/",
    "커피빈":       "https://www.coffeebeankorea.com/menu/list.asp",
    "CU":          "https://cu.bgfretail.com/product/product.do",
    "세븐일레븐":   "https://www.7-eleven.co.kr/product/presentList.asp",
    # 상품 목록 페이지가 없는 브랜드다. 기사별 상세 주소가 Item.url 로 붙으므로
    # 이건 폴백일 뿐이다. 브랜드 소개(/brand/gs25)보다 보도자료 목록이 용건에 가깝다.
    "GS25":        "https://www.gsretail.com/news/press-releases",
    "맘스터치":     "https://www.momstouch.co.kr/menu/new.php",
    "버거킹":       "https://www.burgerking.co.kr/menu/main",   # 해시 라우팅 아님(history 모드)
    "프랭크버거":   "https://www.frankburger.co.kr/html/menu_1.html",
    "BBQ":         "https://bbq.co.kr/categories/17",   # /menu 는 404. Next.js 라 카테고리 경로를 쓴다
    "bhc치킨":      "https://www.bhc.co.kr/menu/chicken.asp",
    "교촌치킨":     "https://www.kyochon.com/menu/chicken.asp",
    # /menu/new_p 의 _p 는 AJAX 조각 경로라 사람이 열면 에러 JSON 이 뜬다.
    "굽네치킨":     "https://www.goobne.co.kr/menu/menu_list",
    # 상품 상세 페이지가 없는 브랜드다(카드에 <a> 자체가 없다). 이게 유일한 링크다.
    "처갓집양념치킨": "https://cheogajip.co.kr/bbs/board.php?bo_table=allmenu",
    # 상품별 주소(/menu/view.asp?idx=)가 Item.url 로 붙으므로 이건 폴백이다.
    "푸라닭":       "https://www.puradakchicken.com/menu/product.asp",
    # ⚠️ http 전용이다. 443 이 연결 리셋이라 https 로 못 바꾼다(chicken_boor.py 참고).
    "부어치킨":     "http://www.boor.co.kr/menu/default.aspx?menu=ALL",
    # 상품별 주소(board_view.php?board_seq=)가 Item.url 로 붙으므로 이건 폴백이다.
    "또래오래":     "https://www.toreore.com/board/menu/board_list.php",
    # 신메뉴 전용 페이지. 메뉴 게시판 3종은 Item.url 로 따로 붙는다.
    "자담치킨":     "https://www.ejadam.co.kr/bbs/content.php?co_id=new_menu",
    # /menu 가 302 로 가는 신메뉴 페이지. 번호(/menu01=추천메뉴)와 내비 순서가
    # 어긋나는 사이트라 경로를 짐작하면 틀린다(chicken_ttangttang.py 참고).
    "땅땅치킨":     "https://ttangttang.co.kr/menu",
    # 상품별 주소(/menu/detail?goodsNo=)가 Item.url 로 붙으므로 이건 폴백이다.
    "페리카나":     "https://www.pelicana.co.kr/menu/list",
    # 상품별 주소(/menu/view.php?board_id=)가 Item.url 로 붙으므로 이건 폴백이다.
    "바른치킨":     "https://barunchicken.com/menu/index.php",
    # 상품 팝업(/popup/product_view?wm_id=)이 Item.url 로 붙으므로 이건 폴백이다.
    "누구나홀딱반한닭": "https://www.nuguna-banhandak.co.kr/product/list?ca_id=01",
    "후라이드 참 잘하는집": "https://www.hoocham.com/menu/menu1?ca_id=01",
    # 최상위는 브랜드/창업 포털 스플래시라 메뉴 페이지를 직접 건다.
    "꾸브라꼬숯불치킨": "https://kkubeurakko.com/menu-1/",
    # 상품별 주소(?bmode=view&idx=)가 Item.url 로 붙으므로 이건 폴백이다.
    "치킨플러스":   "https://chickenplus.co.kr/CHICKEN",
    # 대문(mexicana.co.kr)은 /intro.asp 인트로로 떨어진다. 메뉴는 여기다.
    # 상품별 페이지가 없어(카드에 <a> 가 없다) 이게 유일한 링크다.
    "멕시카나":     "https://www.mexicana.co.kr/menu/product.asp",
    # ⚠️ 도메인이 대표번호다 — hosigi.co.kr 가 아니다. 수집은 /chicken·/parts·
    # /side 에서 하지만(/menu 는 3건이 빠져 있다) 사람이 여는 전체 면은 /menu 다.
    "호식이두마리치킨": "https://www.9922.co.kr/menu",
    # ⚠️ 60ke.co.kr 는 NXDOMAIN, 60ke.com 은 주차 페이지다.
    # 상세가 href 없는 JS 팝업이라 이게 유일한 링크다.
    "60계":        "https://60chicken.co.kr/bbs/content.php?co_id=menu",
    # 상품별 주소(/home_menu_detail.asp?no=)가 Item.url 로 붙으므로 이건 폴백이다.
    "네네치킨":     "https://nenechicken.com/home_menu.asp",
    # 상품별 주소(/b/menu/<wr_id>)가 Item.url 로 붙으므로 이건 폴백이다.
    "가마치통닭":   "https://www.gamachi.co.kr/b/menu",
    # ⚠️ .com 은 남의 빈 호스트다(collectors/chicken_norang.py 참고).
    # apex 는 브랜드/창업 두 장짜리 스플래시라 메뉴 첫 장을 쓴다.
    "노랑통닭":     "https://norangtongdak.co.kr/menu/chicken_list.html",
    "피자헛":       "https://www.pizzahut.co.kr/menu",
    "미스터피자":   "https://www.mrpizza.co.kr/bbs/board.php?bo_table=menu",
    "파파존스":     "https://pji.co.kr/menu/pizza",
    "배스킨라빈스": "https://www.baskinrobbins.co.kr/menu/fom.php",
    # 글별 주소가 Item.url 로 붙으므로 이건 폴백이다. 사람이 열 자리는
    # 공지 게시판이 아니라 메뉴·매장 면이다.
    "요아정":      "https://yoajung.co.kr/bbs/content.php?co_id=menustore",
    "던킨":         "https://www.dunkindonuts.co.kr/menu",
    "이삭토스트":   "https://www.isaac-toast.co.kr/menu/menu.php",
    "이마트24":     "https://emart24.co.kr/goods/pl",
    "도미노피자":   "https://www.dominos.co.kr/goods/list",
    # 피자스쿨은 https 가 자체서명이라 http 로 건다(스쿨푸드와 같은 칸).
    # collectors/pizza_pizzaschool.py 참고.
    "피자스쿨":     "http://pizzaschool.net/menu/",
    "피자마루":     "https://www.pizzamaru.co.kr/menu",
    "폴바셋":       "https://www.baristapaulbassett.co.kr/menu/List.pb",
    "파리바게뜨":   "https://www.paris.co.kr/products/",
    "뚜레쥬르":     "https://www.tlj.co.kr/product/result.asp",
    "나폴레옹과자점": "https://napoleonbakery.co.kr/h/b/napoleon/products",
    "브레댄코":     "https://www.breadnco.kr/portfolio-category/new/",
    "홍루이젠":     "https://www.hongruizhen.com/goods/goods_list.php?cateCd=001",
    "노티드":       "http://www.knottedstore.com/menu",   # TLS 2026-09-06 만료 → http
    "삼송빵집":     "https://ssbnc.kr/doc/menu0.php",
    "본죽":         "https://www.bonif.co.kr/brand/menu?brdCd=BF101",
    "본죽&비빔밥":   "https://www.bonif.co.kr/brand/menu?brdCd=BF102",
    "본도시락":     "https://www.bonif.co.kr/brand/menu?brdCd=BF104",
    "본설렁탕":     "https://www.bonif.co.kr/brand/menu?brdCd=BF105",
    "본우리반상":   "https://www.bonif.co.kr/brand/menu?brdCd=BF107",
    "멘지":         "https://www.bonif.co.kr/brand/menu?brdCd=BF111",
    "본흑염소·능이삼계탕": "https://www.bonif.co.kr/brand/menu?brdCd=BF113",
    "이지브루잉커피": "https://www.bonif.co.kr/brand/menu?brdCd=BF114",
    "요거프레소":   "https://yogerpresso.co.kr/menu/menu-new.html",
    "김밥천국":     "https://kimbab1009.com/31",
    "바르다김선생": "https://teacherkim.co.kr/menu/list.html?bs=004001",
    "죠스떡볶이":   "https://jawsfood.co.kr/menu/menu.html",
    "명랑핫도그":   "https://myungranghotdog.com/menu/new",
    # 상품별 주소(link 필드)가 Item.url 로 붙으므로 이건 폴백이다.
    "얌샘김밥":     "https://yumsem.com/yumsem-gimbap/yumsem-basic/",
    # 김가네는 상품 상세가 없다(카드가 href="#none" 인 JS 모달). 이게 유일한 링크다.
    "김가네":       "https://www.gimgane.co.kr/board/index.php?board=menu_01&sca=newmenu",
    # 스쿨푸드는 https 가 자체서명이라 http 로 건다. collectors/snack_schoolfood.py 참고.
    "스쿨푸드":     "http://www.schoolfood.co.kr/menu/menu.html",
    "토마토도시락": "https://www.tomatodosirak.co.kr/board/index.php?board=menu_01&sca=new",
    # 슬로우캘리는 글별 주소가 Item.url 로 붙는다. 이건 폴백이다.
    "슬로우캘리":   "https://www.slowcali.co.kr/bbs/board.php?bo_table=main_news",
    # 수집은 /protein_poke·/rice_bowl·/side·/drink 에서 하지만, 사람이 여는
    # 메뉴 첫 장은 /poke 다. 링크의 용건은 브랜드로 트래픽을 돌려주는 것이다.
    "포케올데이":   "https://pokeallday.co.kr/poke",
    # /bbs/board.php 쪽 게시판은 403 이다. content.php 가 열린 경로다.
    "삼첩분식":     "https://samcheop.com/bbs/content.php?co_id=menu&tab=1",
    # 글별 주소가 Item.url 로 붙는다. 이건 폴백이고, 메뉴 쪽을 건다.
    "국수나무":     "https://www.namuya.co.kr/food/food.php",
    # 글별 주소가 Item.url 로 붙는다. 이건 폴백이고 메뉴 쪽을 건다.
    "애플꼬마김밥": "https://apple-food.co.kr/bbs/board.php?bo_table=menu",
    # ssadagimbab.co.kr 은 NXDOMAIN 이다. 사는 건 ssadagb.com 쪽이다.
    "싸다김밥":     "https://www.ssadagb.com/menu/list?cate_no=23",
    "매머드커피":   "https://mmthcoffee.com/sub/menu/new_list.php",
    "더벤티":       "https://theventi.co.kr/new2022/menu/all.html",
    "컴포즈커피":   "https://composecoffee.com/index1",
    "투썸플레이스": "https://www.twosome.co.kr/mn/menuList.do",
    "엔제리너스":   "https://www.angelinus.com/menu/menu_list.asp",
    "할리스":       "https://www.hollys.co.kr/menu/espresso.do",
    # SPA 라 사람이 여는 주소는 /menu 다. 어댑터는 그 뒤의 내부 API 를 쓴다.
    "탐앤탐스":     "https://www.tomntoms.com/menu",
    "블루샥":       "https://www.blushaak.co.kr/menu",
    # ⚠️ gongcha.co.kr 이 아니라 **하이픈이 든** gong-cha.co.kr 이 본 사이트다.
    # 루트는 스플래시라 메뉴 카탈로그 경로를 폴백으로 둔다.
    "공차":         "https://gong-cha.co.kr/brand/menu/product",
    "카페051":      "https://cafe051.com/menu",
    # 상품별 주소(보도자료 글)가 Item.url 로 붙으므로 이건 폴백이다.
    "우지커피":     "https://oozycoffee.com/coffee",
    # 쿼리값이 한글 그대로다(menu=신메뉴). 퍼센트 인코딩해서 넣는다.
    "팔공티":       "https://palgongtea.co.kr/goods/newest.html?menu=%EC%8B%A0%EB%A9%94%EB%89%B4",
    # ⚠️ http 전용이다. https 는 ConnectTimeout 이라 이미지가 derive() 에서 지워진다.
    "카페베네":     "http://caffebene.co.kr/product",
    # 한글 도메인(읍천리382.com)의 퓨니코드다.
    "읍천리382":    "https://www.xn--382-v18me95c8ph.com/",
    "파스쿠찌":     "https://www.pascucci.co.kr/product/productList.asp",
    "텐퍼센트커피": "https://tenpercentcoffee.com/menu",
    "카페인중독":   "https://www.caffeine-addiction.co.kr/",
    "하삼동커피":   "https://www.hasamdongcoffee.com/",
    # ⚠️ 둘 다 http 전용이라 이미지가 derive() 에서 지워진다.
    "고망고":       "http://gomango.kr/menu",
    "차얌":         "http://chayam.co.kr/menu",
    "달리는커피":   "https://dalcu.co.kr/",
    # juicy.co.kr 은 443/80 둘 다 연결거부다. 본 사이트는 no1juicy.com 이고
    # ⚠️ http 전용이라 이미지가 derive() 에서 지워진다.
    "쥬씨":         "http://www.no1juicy.com/",
    "매스커피":     "https://mass-coffee.com/",
    "스시로":       "https://www.sushiro.co.kr/pm",
    "에그드랍":     "http://www.eggdrop.co.kr/menu/list.php?category=NEW",
    "써브웨이":     "https://www.subway.co.kr/menuList/sandwich",
    # https 가 자체서명이라 평문 http 뿐이다. 근거는 collectors/sandwich_quiznos.py docstring.
    "퀴즈노스":     "http://quiznos.co.kr/menu/menu.php",
    "쉬즈베이글":   "https://shesbagel.com/toastandbread",
    "참토스트":     "https://charmtoast.com/menu",
    # 상품별 주소(`?bo_table=menu&wr_id=`)가 Item.url 로 붙으므로 이건 폴백이다.
    "잇샌드":       "https://itsand.co.kr/board/bbs/board.php?bo_table=menu",
    # 상품별 주소(/<칸>/?idx=)가 Item.url 로 붙으므로 이건 폴백이다.
    "쏘자토스트":   "https://ssoja.co.kr/menu",
    "지미존스":     "https://www.jimmyjohns.co.kr/homepage/menu.php",
    "샐러디":       "https://salady.com/menu/list_1",
    # 돈까스 6곳. 상품별 주소가 Item.url 로 붙는 곳이 많아 대부분 폴백이다.
    "백소정":       "https://baeksojeong.com/35",
    "미소야":       "https://www.misoya.co.kr/menu",
    "긴자료코":     "https://ginzaryoko.co.kr/signature-menu-list/signature.view",
    "하루엔소쿠":   "https://haruensoku.co.kr/",
    "홍익돈까스":   "https://www.hongikdonkatsu.com/menu",
    "브라운돈까스": "https://browntonkatsu.com/sub/menu6.php",
    # 일식 4곳. 넷 다 글별 주소가 Item.url 로 붙으므로 이건 폴백이다.
    # 쿠우쿠우만 상품 목록 페이지가 없어 '신메뉴 소개' 페이지를 폴백으로 둔다(GS25 선례).
    "쿠우쿠우":     "https://www.qooqoo.co.kr/page/?pid=newMenu",
    "미카도스시":   "https://www.mikadosushi.co.kr/bbs/board.php?bo_table=menu",
    "모토이시":     "https://motoishi.co.kr/introduce-menu/main-menu.php",
    "동경에서먹었던규동": "https://tokyo-gyudong.com/menu",
    # 한식 4곳. 큰맘할매순대국·원앤원 둘은 상품 상세 페이지가 아예 없어 폴백이 본 링크다.
    "한솥":         "https://www.hsd.co.kr/menu/menu_list",
    "두찜":        "https://twozzim.com/bbs/content.php?co_id=menu",
    "담꾹":        "https://www.damgguk.com/recipe/menus/",
    "유가네":      "https://www.yoogane.co.kr/menu/menu.html",
    "오봉집":      "https://www.obongzip.com/mainmenu",
    "큰맘할매순대국": "https://www.keunmam.co.kr/html/menu.html",
    "원할머니보쌈족발": "https://wonandone.co.kr/bossam/menu.asp",
    # ⚠️ mawangjokbal.com 은 NXDOMAIN 이다. 공식은 mawangpork.com.
    "마왕족발":     "https://mawangpork.com/html/menu_1.html",
    "박가부대":     "https://wonandone.co.kr/parkga/menu.asp",
    "맥도날드":     "https://www.mcdonalds.co.kr/kor/menu/burger",
    # 롯데GRS 통합몰 안의 롯데리아 전용 브랜드 메뉴 면. /brand/lotteria 는 404 다.
    "롯데리아":     "https://www.lotteeatz.com/brand/ria",
    # www.nobrandburger.com 이 여기로 리다이렉트된다.
    "노브랜드버거": "https://www.shinsegaefood.com/nobrandburger/index.sf",
    # 상품별 주소(이벤트 글)가 Item.url 로 붙으므로 이건 폴백이다.
    "왓더버거":     "https://whattheburger.co.kr/page.php?p_id=menu",
    # ⚠️ http 전용이다. 443 이 Connection refused 라 https 로 못 바꾼다.
    "쉐이크쉑":     "http://shakeshack.kr/sub/menu.jsp",
    "파이브가이즈": "https://www.fiveguys.co.kr/menu/",
    # 카드에 <a> 가 없어 상품 상세가 없다. 이게 유일한 링크다.
    "버거운버거":   "https://www.burgerunburger.com/menu",
    "오뚜기":       "https://www.otoki.com/pr/news?searchNewsCategory=PRESS",
    "팔도":         "https://www.paldofood.co.kr/product/noodle",
    "오리온":       "https://www.orionworld.com/board/list/87",
    # 상품별 주소는 롯데칠성몰(mall.) 이라 Item.url 로 따로 붙는다. 이건 폴백이다.
    "롯데칠성음료": "https://company.lottechilsung.co.kr/kor/product/newprdt/list.do",
    # 상품별 주소(/product/detail?prdId=)가 Item.url 로 붙으므로 이건 폴백이다.
    "카페봄봄":     "https://cafebombom.co.kr",
    "커피베이":     "https://www.coffeebay.com",
    "하이오커피":   "https://hiocoffee.com",
    "카페만월경":   "https://cafewhale.com",
    "빙동댕":       "https://www.xn--hl1bno83x.kr",
    "달롱도르":     "https://dallondor.com",
    "에밀리아젤라또": "https://www.emiliagelato.co.kr",
    "타래퀸":       "https://www.taraequeen.com",
    # ⚠️ http 전용이다. https 는 안 열린다(collectors/dessert_palazzo.py 참고).
    "빨라쪼":       "http://www.ipalazzo.com",
    "33떡볶이":   "https://33success100.co.kr",
    "병아리김밥":   "https://chickgimbap.com",
    "김밥킹":       "https://xn--4k0bn7xt5p.com",
    "모락떡볶이":   "https://moraktteok.com/",
    "태리로제떡볶이": "https://terryroze.com",
    "떡군이네떡볶이": "https://xn--6e0b73ep0espx.com",
    "백억커피":     "https://10billioncoffee.co.kr",
    "디저트39":   "https://dessert39.com",
    "엽기떡볶이":  "https://www.yupdduk.com",
    "앤티앤스":     "https://www.auntieannes.co.kr",
    "송사부고로케": "https://songsabu.co.kr",
    # 모회사 보도자료 게시판이 아니라 자사몰이다. 여기가 url 이 빈 상품의
    # 폴백이라, 게시판을 적어두면 사람이 백화점 뉴스로 떨어진다.
    "벤슨":        "https://www.bensonicecream.com/product/new.php",
    "더플레이스":   "https://www.italiantheplace.co.kr/menu",
    "제일제면소":   "https://www.cheiljemyunso.co.kr/menu",
    "하이트진로":  "https://www.hitejinro.com/socialmedia/press_list.asp",
    "하림":         "https://www.harim.com/main/?menu=52",
    "하림산업":     "https://harimholdings.com/kr/sub/newsroom/newsroom.asp",
    # 아워홈·샘표는 상품 목록 페이지가 없어 보도자료를 폴백으로 쓴다(GS25 선례).
    # 동서식품은 상품 목록이 있고 어댑터도 그쪽을 읽는다.
    "아워홈":      "https://www.ourhome.co.kr/front/newsboardlist.do",
    "동서식품":    "https://www.dongsuh.co.kr/product/list/1",
    "샘표":        "https://www.sempio.com/news/press-release",
    # 상품별 주소가 Item.url 로 붙는 곳은 이게 폴백이다. 해태·삼양·하이트진로음료는
    # 상세가 SPA 셸이거나 사진이 없어 목록 주소를 그대로 쓴다.
    "해태제과식품": "https://www.ht.co.kr/sweet/news",
    "크라운제과":  "https://www.crown.co.kr/product/index?searchCateCd=1478063307",
    "롯데웰푸드":  "https://www.lottewellfood.com/prcenter/news",
    "삼양식품":    "https://www.samyangfoods.com/kor/publicity/press/list.do?searchCateCd=035002",
    "빙그레":      "https://www.bing.co.kr/news/news_announced",
    "매일유업":    "https://www.maeil.com/news/press.jsp",
    "하이트진로음료": "https://www.hitejinrobeverage.com/ko/community/news",
    # 동원F&B 만 진짜 상품 카탈로그가 SSR 로 살아 있다(101KB). robots 가
    # `/services/Product/` 를 명시 허용한다. 나머지 둘은 목록이 폴백이다.
    "풀무원":      "https://news.pulmuone.co.kr/pulmuone/newsroom/listPulmuone.do?menu=312",
    "동원F&B":     "https://www.dongwonfnb.com/services/Product/Product_List",
    "사조대림":    "https://www.sajo.co.kr/2026/product/new_product.asp",
    # 상품별 상세(/now/pr/{id})가 Item.url 로 붙으므로 이건 폴백이다.
    "SPC삼립":     "https://www.spcsamlip.co.kr/now/pr",
    # 농심만 진짜 신제품 면이라 어댑터가 읽는 주소를 그대로 쓴다. 나머지 둘은
    # 보도자료 목록이 폴백이다(기사별 주소는 Item.url 로 따로 붙는다).
    # ⚠️ 신세계푸드는 어댑터가 XHR(/company/pr/response/…)을 읽지만, 사람이 열
    #    주소는 그게 아니다 — 사람이 보는 면을 적는다.
    # 🔴 `brand.nongshim.com/new_product/index`(브랜드관 신제품 면)를 가리키고
    # 있었는데 **그 면은 2026-06 에서 갱신이 멈췄다.** 검수가 잡았다 —
    # 농심이 실제로 낸 8~10월 신제품 3건이 거기 없다. 어댑터도 뉴스룸으로
    # 옮겼으니 사람이 여는 주소도 같이 옮긴다(collectors/maker_nongshim.py 참고).
    "농심":        "https://www.nongshim.com/newsroom/news/list",
    "CJ제일제당":  "https://www.cj.co.kr/kr/newsroom/pressreleases",
    "신세계푸드":  "https://www.shinsegaefood.com/company/pr/news_list.sf",
    "면사랑":      "https://www.noodlelovers.com/site/main/archive/post/category/news",
    # 기사별 주소(newsView.do?idx=)가 Item.url 로 붙으므로 이건 폴백이다.
    "대상":        "https://www.daesang.com/kr/news/newsList.do",
    "라벨리":      "https://lavelee.co.kr/media-coverage/",
    # ── 더본코리아 외식 브랜드 ─────────────────────────────────────────
    # 상품별 주소(보도자료 기사)가 Item.url 로 붙으므로 이건 전부 폴백이다.
    # 자체 도메인이 있으면 그 브랜드의 **메뉴 페이지**를, 없으면 theborn.co.kr 의
    # 브랜드 소개 페이지를 쓴다. 주소에 한글이 그대로 들어가는 건 더본 쪽
    # WordPress 슬러그가 한글이기 때문이다(브라우저가 알아서 인코딩한다).
    "역전우동0410": "https://udon0410.com/menu/",
    "미정국수0410": "https://www.0410noodle.com/menu/",
    "롤링파스타":   "https://rolling-pasta.com/",
    # /menu/main.do 는 내비가 가리키지만 404 다. 목록 면을 직접 건다.
    "아웃백스테이크하우스": "https://www.outback.co.kr/menu/productList.do?cateIdx=26&menuIdx=43",
    # ⚠️ ?ssoLoginYN=N 이 없으면 210바이트 리다이렉트 셸만 온다.
    "빕스":         "https://www.ivips.co.kr/menu?ssoLoginYN=N",
    "한신포차":     "https://hanshinpocha.com/menu/",
    "백스비어":     "https://paiksbeer.com/menu/",
    "새마을식당":   "https://newmaul.com/sub/menu.php",
    "원조쌈밥집":   "https://ssambap.co.kr/menu/",
    "돌배기집":     "https://dolbaegi.com/",
    # bornga.kr 은 글로벌 라인 사이트라 메뉴가 영문이다. 국내 사람이 볼
    # 자리는 본사 브랜드 페이지 쪽이다(메뉴 20건이 한글로 실려 있다).
    "본가":         "https://www.theborn.co.kr/theborn_brand/본가/",
    # 아래는 자체 도메인이 없거나(빽보이피자·홍콩반점0410·연돈볼카츠·막이오름·
    # 제순식당·고투웍·홍콩분식·성성식당) 도메인이 살아 있지 않아
    # (인생설렁탕·리춘시장은 TLS 인증서가 호스트명과 안 맞고, licun8888.com 은
    # https 로 열면 paikdabang.com 으로 떨어진다) 본사 브랜드 페이지로 보낸다.
    "빽보이피자":   "https://www.theborn.co.kr/theborn_brand/빽보이피자/",
    "홍콩반점0410": "https://www.theborn.co.kr/theborn_brand/홍콩반점2/",
    "연돈볼카츠":   "https://www.theborn.co.kr/theborn_brand/연돈볼카츠/",
    "막이오름":     "https://www.theborn.co.kr/theborn_brand/막이오름/",
    "인생설렁탕":   "https://www.theborn.co.kr/theborn_brand/인생설렁탕/",
    "리춘시장":     "https://www.theborn.co.kr/theborn_brand/리춘시장/",
    "제순식당":     "https://www.theborn.co.kr/theborn_brand/제순식당/",
    "고투웍":       "https://www.theborn.co.kr/theborn_brand/고투웍/",
    "홍콩분식":     "https://www.theborn.co.kr/theborn_brand/홍콩분식/",
    "성성식당":     "https://www.theborn.co.kr/theborn_brand/성성식당/",
    # KFC 는 상품 카탈로그(/allmenu)가 클라이언트 렌더라 HTML 에 0건이다.
    # 어댑터가 읽는 '신메뉴' 면이 사람에게도 가장 쓸모 있는 폴백이다.
    "KFC":         "https://www.kfckorea.com/promotion/newMenu",
    # ── 중식 ─────────────────────────────────────────────────────────
    # 상품별 주소(보도자료·공지 상세)는 Item.url 로 붙으므로 이건 폴백이다.
    # 어댑터가 메뉴 페이지를 '안 읽는' 브랜드도 링크는 메뉴 쪽으로 보낸다 —
    # 사람이 누르면 재료 목록이라도 그 브랜드를 보는 자리가 맞다.
    "탕화쿵푸마라탕": "https://tanghuokungfu.co.kr/default/brand/menu/menu.php",
    "춘리마라탕":   "https://chunlimalatang.com/menu/",
    "보배반점":     "https://bobaebanjum.co.kr/menu/main.php",
    "소림마라":     "https://sorimmara.co.kr/html/menu.html",
    "라홍방마라탕": "https://www.lahongbang.com/page.php?p_id=menu",
    # 한글 도메인 짬뽕관.com. 신메뉴 글별 주소가 Item.url 로 붙으므로 폴백이다.
    # 사람이 열 자리는 공지 목록보다 메뉴판이다(NEW 배지가 거기 있다).
    "짬뽕관":       "https://www.xn--zb0bq16amwh.com/menu",
    # 한 장짜리 랜딩에 메뉴 28건이 박혀 있다. 메뉴 섹션 앵커가 없어 루트로 보낸다.
    "홍짜장":       "https://hongjjajang.com/",
    "미미관마라탕": "https://mimimara.co.kr/16",
    # 어댑터가 읽는 홍보자료(?c=184)는 2023-10 에 멈춰 글이 3건뿐이라,
    # 사람이 열 자리로는 메뉴 소개(?c=186)가 낫다.
    "짬뽕10101":    "https://goguryeofood.com/?c=186",
    # 한글 도메인 삼삼마라.com. 한 장짜리 사이트라 메뉴가 앵커(#doz_menu_19)다.
    "삼삼마라":     "https://xn--oi2bo7bt0ja.com/",
}


def site(brand: str) -> str:
    """브랜드 메뉴 페이지. 등록이 안 됐으면 빈 문자열(링크를 안 건다)."""
    return SITES.get(brand, "")


# 먹는 게 아닌 것들. 브랜드가 분류로 알려주는 경우가 가장 정확하고, 없으면 이름을 본다.
# 이름 단어는 좁게 잡는다 — '보틀'·'케이스' 를 넣었더니 '보틀캔디'·'빅보틀팝'·
# '드립백 커피 틴케이스' 같은 실제 식품이 걸렸다.
NONFOOD_CATEGORIES = {"MD상품", "생활용품"}
NONFOOD_WORDS = (
    "텀블러", "머그", "키링", "파우치", "볼펜", "피규어", "무드등",
    "에코백", "담요", "인형", "칫솔", "치약", "바디밤", "가그린", "스타킹", "양말",
    "립밤", "클렌징", "핸드크림", "샴푸", "앞치마", "쇼핑백", "보냉백", "보온병",
    "우산", "슬리퍼", "방향제", "콘돔", "마스크3", "손소독", "굿즈", "가방", "세제",
    # 편의점은 category 가 '신상품'·'행사 상품' 같은 판매채널이라 분류로는 못 가른다.
    # 아래는 전체 데이터에 대고 식품 오탐 0 을 확인하고 넣은 것들이다.
    "키친타올", "마스크팩", "폼클렌저", "클렌져", "면도기", "면도날",
    "화장지", "오버나이트", "간편유심", "토퍼", "립테라피", "로션", "위생",
    "브레스스프레이",
    # 생활용품 제조사명. 그 이름이 붙은 건 먹는 게 아니다.
    "리스테린", "페브리즈", "질레트", "센카", "니베아", "존슨", "다우니",
)
# 넣으면 안 되는 단어들. 한국어는 단어 경계가 없어서 우연히 걸린다.
#   보틀  → 빅보틀팝·보틀캔디 (과자)
#   모자  → 분모자 = 당면. 로제분모자볶이·분모자 로제 떡볶이
#   케이스 → 드립백 커피 틴케이스 세트
#   타올  → 롯데)로케타올리베라스750ml = 와인 ('로케타 올리베라스')
#   매트  → 패트와매트반반바 (아이스크림)
#   핸디  → 복숭아 가득 핸디 젤리 (스타벅스). 텀블러류는 '텀블러' 로 이미 잡힌다
#   티슈  → 던킨 '티슈 브레드'
#   렌즈  → '글로렌즈)골든고비라거', 이디야 '사과당근클렌즈주스'
#   피지  → 스타벅스 '리버 피치 피지오'·'쿨 라임 피지오' (음료)
#   가위  → 한가위보름달만찬·풍성한가위정찬도시락. '주방 가위' 로 붙여야 한다
#   빨대  → 메가 '빨대 텀블러'. 어차피 '텀블러' 가 잡는다
#   면도  → '짜장면도시락'·'라면도시락'. 편의점 이름은 띄어쓰기가 없어서 걸린다
#   찜기  → '소갈비찜기획상품'. 편의점이 '기획팩·기획상품' 을 아주 흔히 쓴다
#   스프레이 → '식용유 스프레이'·'휘핑 스프레이크림'. 먹는 스프레이가 실재한다
#   유심  → '두유심플'·'우유심쿵'
# 위 넷은 지금 데이터엔 오탐이 없지만 앞으로 날 자리다. 좁혀서 넣었고
# 좁히면서 잃은 건 0건이다(면도→면도기·면도날 4건 그대로).
#
# ⚠️ 리스테린·페브리즈 같은 브랜드명을 넣은 건 이 목록만의 예외다.
# ALCOHOL_WORDS 에서는 '하이트' 를 "제조사명이라 음료도 걸린다" 며 일부러 뺐다.
# 비식품 쪽은 이 회사들이 식품을 안 만들어서 안전한 것뿐이니, 한쪽 선례를
# 들고 다른 쪽에 적용하지 마라.
# 새 단어를 넣기 전에 전체 데이터에 대고 식품 오탐이 0인지 먼저 세라.


def is_nonfood(name: str, category: str = "") -> bool:
    """굿즈·생활용품인가. 카페 MD, 편의점 생활용품, 콜라보 굿즈가 여기 걸린다."""
    return category in NONFOOD_CATEGORIES or any(w in name for w in NONFOOD_WORDS)


# 주류는 본 목록에서 뺀다. 데이터에는 남겨둔다.
#
# 🔴 사유를 2026-10-02 에 정정했다. 전에 "청소년보호법상 연령 확인" 이라고
# 적었는데 **방향이 틀렸다.** 조사해 보니 직접 걸리는 건
#   국민건강증진법 제8조의2 제1항 — "주류 제조면허나 주류 판매업면허를 받은
#   자 및 주류를 수입하는 자를 **제외하고는** 주류에 관한 광고를 하여서는
#   아니 된다"
# 다. 이건 **광고 주체 제한**이지 접근 제한이 아니다. 우리는 면허자도
# 수입업자도 아니라서 **연령 확인을 붙여도 해소되지 않는다.**
# (청소년보호법 제19조의 '접근 제한 기능' 조항은 대상이 청소년유해매체물이라
#  유해약물인 주류에 바로 걸리지는 않는다.)
#
# 쟁점은 하나로 모인다 — "우리가 주류 신제품을 올리는 게 '광고' 인가".
# 광고라면 주체 제한·경고문구 의무가 따라오고 연령 게이트로는 못 푼다.
# 광고가 아니면 셋 다 요구되지 않는다. 우리는 그 판단을 할 자리가 아니다.
#
# 업계가 그어둔 선이 또렷하다(2026-10-01 21곳 실측) —
#   제품 소개 = 광고로 보고 연령 게이트 (제조사·수입사 7곳 전부)
#   출시 소식 = 소식으로 보고 공개      (같은 회사의 보도자료)
# 하이트진로·롯데칠성이 같은 사이트에서 경로별로 다르게 대한다.
# **롯데칠성은 자기 신제품 페이지에서 주류를 일부러 뺐다**(18건 전부 음료).
# 우리가 그 회사보다 느슨할 이유가 없다.
#
# 얻는 것도 작다. 지금 걸러지는 걸 전부 열어도 화면에 오르는 건 3건이고
# (나머지는 행사이거나 60일 창 밖), 제조사를 다 뒤져도 쓸 만한 곳이
# 하이트진로 보도자료 하나, 월 1~2건이다.
#
# 뒤집을 조건: 운영자가 면허를 얻거나, "출시 소식은 광고가 아니다" 는
# 유권해석·판례가 확인되거나, 복지부가 검토 중이라는 뉴미디어 기준이
# 나오면 다시 본다. 그때도 열려면 별도 분류 + 경고문구가 먼저다.
ALCOHOL_CATEGORIES = {"주류"}

# 이마트24 는 상품명 앞에 주종을 붙인다("레드)베어풋카베르네소비뇽750ml").
# 이름 단어보다 이게 정확하다. 세븐일레븐은 제조사를 붙여서("롯데)옐로우테일…")
# 접두로는 못 가르고, 그쪽은 아래 포도품종 단어로 잡는다.
# 실측해서 주종인 것만 넣었다 — '옐로우)' 는 과자, '포차24)' 는 안주다.
ALCOHOL_PREFIXES = ("레드", "화이트", "로제", "스파클링", "샴페인",
                    "위스키", "사케", "칵테일", "보드카", "럼", "리커")

ALCOHOL_WORDS = (
    "맥주", "비어", "라거", "에일", "IPA", "흑맥주", "발포주",
    "위스키", "하이볼", "칵테일", "소주", "보드카", "샴페인", "데낄라", "브랜디",
    "하이네켄", "기네스", "칭따오", "버드와이저",
    # 포도품종·와인용어. 와인은 이름에 '와인' 이 안 들어가는 게 보통이라
    # 품종으로 잡아야 한다(세븐일레븐 '롯데)옐로우테일오로라팩(쉬라)').
    # '와인' 은 뺐다 — 전체에서 잡은 게 나폴레옹과자점 '무화과와인바게트'·
    # '화이트와인애플파이' **빵 2건뿐**이고 진짜 와인은 0건이다. 와인은 이름에
    # '와인' 을 안 쓰고 품종·브랜드로 팔린다(아래). 요리용 와인을 넣은 빵·소스가
    # 계속 나오는 자리라 되살리지 마라.
    "까버네", "까베르네", "카베르네", "쇼비뇽", "소비뇽",
    "샤르도네", "샤도네이", "피노누아", "메를로", "모스카토", "쉬라", "시라즈",
    "리슬링", "산지오베제", "말벡",
    "까르미네르",
    # 주종도 품종도 이름에 없는 것들. 제품명으로 잡을 수밖에 없고 이 목록은
    # 늘어난다 — 구조적 한계다. '클라우드' 는 할리스 '미니저그 (클라우드크림)'
    # 이 걸려서 편의점 제조사 접두 뒤에 오는 경우로 좁혔다.
    "옐로우테일", ")클라우드", "한맥", "카스아이스", "칼스버그", "삿포로",
    "더드래프트", "크로넨버그", "쇼쿠사이", "효케츠", "파울라너",
    "바이젠", "츄하이", "필스너", "스타우트",
    "라들러", "에비스", "써머스비", "상그리아", "브룻", "스텔라퓨어", "크루저",
    ")페로니",   # '페로니' 로는 피자헛 '페페로니 러버' 를 문다
)

# 뒤에 무엇이 오느냐로 갈리는 것들. 단순 포함으로는 못 가른다.
# 중국 백주. 중식 브랜드가 자체 고량주를 낸다(보배반점 '보배고량주' 2026-02-26).
# ⚠️ 통짜 '고량주' 로 넣으면 안 된다 — 지금 데이터엔 0건이라 오탐이 안 보이지만
# '고량주스'·'고량주스바'·'청고량주먹밥' 을 전부 문다. 실제로 찍어 보고 확인했다.
# 카스 → 카스테라 28건과 같은 자리라 뒤에 한글이 안 오는 경우로 좁힌다.
# '백주' 는 아예 넣지 않았다 — 2글자라 '백주년' 같은 말을 문다.
_ALCOHOL_RE = re.compile(r"막걸리(?!향|맛|풍미)|고량주(?![가-힣])")
# 넣으면 안 되는 단어들. 전체 데이터에 대고 센 결과다.
#   막걸리 → 스타벅스 '막걸리향 크림 콜드 브루' = 커피. 2건 전부 오탐
#   사케  → '사케라또 아포가토'(스타벅스), 사케동. 접두 '사케)' 로만 잡는다
#   카스  → 카스테라 28건
#   테라  → 카스테라, 프론테라
#   럼    → 브라운쿠키크럼블, 블루베리플럼주스. 접두 '럼)' 로만 잡는다
#   사와  → 사사사와플크림샌드
#   청주  → 청주식돼지김치짜글이
#   하이트 → 제조사명이라 '하이트)무알콜레몬유자' 같은 음료도 걸린다
#   스텔라 → 카스텔라 19건 (빽다방 생크림 카스텔라·던킨 카스텔라 도넛)
#   코젤  → 츄파춥스게코젤리
#   기린  → 기린오후의차밀크티
#   몰트  → 스타벅스 '콜드 브루 몰트'
#   블랑  → 지금은 전건 술이지만 2글자라 언제든 식품을 문다. 크로넨버그로 잡는다
# 새 단어를 넣기 전에 전체 데이터에 대고 식품 오탐이 0인지 먼저 세라.

# 무알콜 표기가 있으면 주류가 아니다. '아사히스타일프리캔맥주' 처럼 이름에
# 맥주가 들어가도 술이 아닌 것들이 있다.
NONALCOHOL_MARKS = ("무알콜", "논알콜", "넌알콜", "비알콜",
                    "무알코올", "논알코올", "넌알코올")

# 도수 0.0 표기. 이 검사는 맨 앞에서 즉시 False 를 돌려주므로 오탐이 나면
# 술이 그대로 화면에 올라간다 — 방향이 반대인 유일한 규칙이다. 그냥 "0.0" 을
# 넣으면 '…10.0g' 같은 용량 표기에 걸려 주류 필터가 통째로 꺼진다.
_ZERO_ABV = re.compile(r"(?<!\d)0\.0(?!\d)")


# 제조사 자사 주류 브랜드. 이름만으로는 못 가르고 그 회사 상품일 때만 술이다.
# '클라우드' 를 전역 단어로 넣으면 노티드 '밀크 클라우드'·'티라미수 클라우드'
# 와 할리스 '미니저그 (클라우드크림)' 을 문다. 브랜드를 묶으면 그게 안 걸린다.
# 편의점이 파는 같은 제품은 제조사 접두가 붙어("롯데)클라우드…") 따로 잡힌다.
ALCOHOL_BY_BRAND = {
    # 값은 정규식이다. '새로' 는 2글자라 그냥 넣으면 '새로나온…' 을 문다
    # (브랜드 안으로 좁혀도 그렇다). 뒤에 한글이 붙으면 다른 말이므로 끊는다.
    "롯데칠성음료": (r"클라우드", r"처음처럼", r"새로(?![가-힣])", r"백화수복",
                 r"스카치블루", r"순하리", r"청하", r"설중매", r"마주앙",
                 r"충전소", r"별빛"),
}


def is_alcohol(name: str, category: str = "", brand: str = "") -> bool:
    """술인가. 무알콜 표기가 있으면 이름에 '맥주' 가 들어가도 술이 아니다."""
    if any(m in name for m in NONALCOHOL_MARKS) or _ZERO_ABV.search(name):
        return False
    if category in ALCOHOL_CATEGORIES:
        return True
    if any(re.search(w, name) for w in ALCOHOL_BY_BRAND.get(brand, ())):
        return True
    if _ALCOHOL_RE.search(name):
        return True
    head = name.split(")", 1)[0] if ")" in name else ""
    return head in ALCOHOL_PREFIXES or any(w in name for w in ALCOHOL_WORDS)


# 카드에 안 찍는 라벨. 정본은 여기다 — 홈(collect.card)과 하위 페이지
# (web/pages)가 각자 적어두면 한쪽만 고쳐진다. 실제로 그랬다: 홈만 고쳐져
# 상세·브랜드·유형 페이지 548장에 'NEW NEW' 중복이 1,024건 남아 있었다.
#
# 행사 라벨은 편의점이 신상품에 도입 행사를 거의 항상 붙여서(세븐일레븐
# 신상품 탭 91건 전부) 그대로 두면 신상 목록이 할인 목록처럼 읽힌다.
# 행사 정보 자체는 data/products.json 에 남는다.
PROMO_LABELS = {"1+1", "2+1", "3+1", "1 + 1", "2 + 1", "3 + 1",
                "할인", "증정", "세일", "특가"}

# NEW 배지를 이미 그리므로 같은 뜻의 라벨은 겹쳐 찍지 않는다.
#
# 목록으로 적지 않고 규칙으로 센다. 전에 {"NEW","신메뉴",…} 로 열거했다가
# 삼송빵집의 'NEW MENU' 를 놓쳐 'NEW NEW MENU' 가 나란히 떴다. 브랜드마다
# 띄어쓰기·대소문자·꼬리말이 제각각이라 열거하면 반드시 빠뜨린다.
_DUP_HEADS = ("NEW", "신메뉴", "신상품", "신제품", "출시")


def _is_dup(label: str) -> bool:
    """우리 NEW 배지와 같은 뜻인가. 'NEW MENU'·'new'·'신 메뉴' 를 다 잡는다."""
    flat = label.replace(" ", "").upper()
    return any(flat.startswith(h.replace(" ", "").upper()) for h in _DUP_HEADS)


def shown_labels(labels) -> list:
    """카드에 찍을 라벨만 남긴다. 홈·상세·브랜드·유형 전부 이걸 쓴다."""
    return [l for l in (labels or [])
            if l and l not in PROMO_LABELS and not _is_dup(l)]


# ── 표시용 이름 ────────────────────────────────────────────────────────
#
# 편의점 상품명은 POS 에 박힌 문자열 그대로다 — `CJ)얼큰우동221g(큰컵)`,
# `롯데)말랑카우밀크79g`. 사람이 읽기도 어렵고 유튜브에 검색도 안 된다.
#
# 🔴 **원본 name 은 절대 바꾸지 않는다.** make_key() 가 name 으로 키를 만들고
# 그 키에 first_seen 이력이 매달려 있다. 이름을 건드리면 전 상품의 키가 바뀌어
# "어제 없던 게 오늘 있다" 가 전건 참이 되고 이력이 통째로 끊긴다.
# 그래서 원본은 그대로 두고 **표시용 이름을 따로** 만든다(derive 가 d["display"]).

# 제조사·납품사 접두. 떼도 되는 것만 들어간다.
#
# 가르는 기준은 추측이 아니라 실측이다 — **둘 이상의 편의점 체인에 같은 접두가
# 나타나면 제조사**다. 제조사는 모든 체인에 납품하지만 PB·자체 라인은 그 체인에만
# 있다. data/products.json 7,005건으로 세어 32개가 나왔고 전건을 눈으로 확인했다.
# 반대로 한 체인에만 있는 접두(`포차24)` 이마트24 30건, `성수310)` 53건,
# `405)` CU 18건, `PBICK)` 22건)는 PB 브랜드라 떼면 상품명을 잃는다 — 안 뗀다.
#
# ⚠️ 정확히 일치할 때만 뗀다. 부분일치로 하면 `하이트진로)`·`롯데리아)` 가
# `하이트)`·`롯데)` 로 걸려서 회사가 다른데도 떨어진다.
# ⚠️ 새 접두를 넣기 전에 전체 데이터에 돌려 상품명이 깎이지 않는지 먼저 세라.
MAKER_PREFIXES = {
    "CJ", "HK", "그린", "널담", "농심", "대상", "동원", "롯데", "리뉴", "마즈",
    "매일", "바세린", "바프", "빙그레", "삼립", "샘표", "서주", "스위트", "엠즈",
    "오뚜기", "오비", "유한", "제니코", "카브루", "코카", "크라운", "티젠", "피지",
    "하겐", "하림", "하이트", "해태",
}

# 선두 대괄호. 숫자뿐이면(나폴레옹과자점 `[123] Love you more` 등 83건) 버리고,
# 말이 들어 있으면(`[파란라벨]`·`[프로틴]`·`[고기곱빼기]`) 괄호만 벗겨 남긴다.
# 통째로 버리면 `[프로틴]닭가슴살` 에서 라인 구분이 사라진다.
_LEAD_BRACKET = re.compile(r"^\[([^\[\]]*)\]\s*")

# `제조사)` 접두. 여는 괄호를 품으면 안 된다 — `디카페인카페모카(H)` 의 `(H)` 가
# 접두로 걸려 이름 앞 10글자가 통째로 날아간다(빽다방·브레댄코 349건이 그랬다).
_PREFIX = re.compile(r"^([^()\[\]\s]{1,10})\)\s*")

# 용량·규격 단위. 숫자가 **바로 앞에 붙어** 있을 때만 단위로 본다.
#   - 사이에 공백을 허용하면 `포차24 매콤껍데기` 의 `24 매` 가 걸린다.
#   - 맨 앞이면 이름 자체다 — `5G_국대급시너지도시락` 의 `5G`.
#   - 앞이 숫자·쉼표면 가격이다 — `롯데)3,900매콤닭껍질튀김` 의 `900매`.
#   - 뒤에 영문·숫자가 오면 단위가 아니다 — `자이언트X3_…`, `초BIG!…`.
# `개`·`구`·`포`는 뺐다. `8포션`·`6구`·`12개월` 처럼 말의 일부로 걸린다
# (`개입` 은 남긴다 — 그건 단위가 맞다).
_UNIT = r"(?:kg|개입|ml|인분|g|l|t|p|입|매)"
_SPEC = re.compile(r"(?<=.)(?<![\d,.])\d+(?:\.\d+)?" + _UNIT + r"(?![A-Za-z0-9])", re.I)

# `*6`·`*4입` 같은 묶음 표기. `x`·`X` 는 넣지 않는다 — `자이언트X3` 이 걸린다.
_MULT = re.compile(r"\s*[*×]\s*\d+\s*(?:개입|입|매|p)?(?![A-Za-z0-9가-힣])", re.I)

# 괄호 안이 규격뿐인 것. `(6입)`·`(355ml)` 과 POS 입수코드 `(12)`·`(36)`.
# 배송 방식 접두. 상품명이 아니라 주문 조건이다.
_SHIP = re.compile(r"^\s*[\[(]\s*(?:택배배송|택배|새벽배송|냉장|냉동)"
                   r"(?:\s*[/·,]\s*(?:택배배송|택배|새벽배송|냉장|냉동))*\s*[\])]")

# 규격을 떼고 남은 곱셈 꼬리. ' x 5개' · ' X 3' 처럼 앞에 수량이 사라진 것.
_ORPHAN_MULT = re.compile(r"\s+[xX×*]\s*\d+\s*(?:개입|개|입|매|p|P)?"
                          r"(?![A-Za-z0-9가-힣])")

_SPEC_PAREN = re.compile(r"\s*\(\s*(?:[*×]?\s*)?\d+(?:\.\d+)?\s*" + _UNIT + r"?\s*\)", re.I)

# 끝에 붙은 보조 괄호 앞에만 공백을 넣는다. `카스테라(초코)` → `카스테라 (초코)`.
# 이름 중간은 건드리지 않는다 — `소프트(모닝)롤` 을 쪼개면 더 읽기 나쁘다.
_TAIL_PAREN = re.compile(r"(?<=\S)\(([^()]*)\)\s*$")


def _sub_outside_parens(rx, s: str) -> str:
    """괄호 **밖**에서만 치환한다. 괄호 안은 통째로 두거나 통째로 버린다.

    괄호 안에서 용량만 빼면 껍데기가 남아 더 흉해진다 — hy프레딧
    `…도라지 캔디(1.2g x 50정) 2통` 이 `…캔디( x 50정) 2통` 이 됐었다.
    """
    spans = [m.span() for m in re.finditer(r"\([^()]*\)", s)]
    def rep(m):
        return m.group(0) if any(a <= m.start() < b for a, b in spans) else " "
    return rx.sub(rep, s)


def _drop_unmatched_parens(s: str) -> str:
    """짝 없는 괄호만 공백으로 바꾼다. 안의 글자는 안 버린다.

    편의점 이름은 괄호가 열리고 안 닫힌 게 흔하다(`…하몽맛45g(`,
    `바닐라라떼300ml(컵`). 여는 괄호에서 잘라버리면 `스키틀즈젤리(후르츠요거트`
    의 맛 이름이 사라진다 — 글자는 남기고 괄호만 없앤다.
    """
    depth, out = 0, []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            if depth == 0:
                out.append(" ")
                continue
            depth -= 1
        out.append(ch)
    if depth:                       # 안 닫힌 여는 괄호를 뒤에서부터 지운다
        left, rev = depth, []
        for ch in reversed(out):
            if ch == "(" and left:
                rev.append(" ")
                left -= 1
            else:
                rev.append(ch)
        out = list(reversed(rev))
    return "".join(out)


def display_name(name: str) -> str:
    """화면·검색어에 쓸 이름. 원본은 그대로 두고 읽을 수 있는 쪽만 만든다.

    `CJ)얼큰우동221g(큰컵)` → `얼큰우동 (큰컵)`
    `롯데)말랑카우밀크79g`   → `말랑카우밀크`
    `포차24)맥반석오징어`    → `포차24 맥반석오징어`   (PB 브랜드라 안 뗀다)

    ⚠️ 사이즈·온도 괄호(`(HOT)`·`(L)`·`(R)`)는 **남긴다.** 빽다방
    `아메리카노(HOT)`/`(ICED)` 와 이디야 `(L)`/`(EX)` 가 128건 있는데, 떼면
    목록에 같은 이름의 카드가 둘씩 뜬다. 변형을 접는 건 별개 작업이다.

    정리한 결과가 2글자 이하로 줄면 **원본을 그대로 돌려준다** — 복구 불가로
    보고 손대지 않는 쪽이 안전하다(`면)2`·`CJ)맛밤80g` 등 12건).
    """
    src = (name or "").strip()
    if not src:
        return name or ""
    s = src

    # 배송 방식은 상품명이 아니다. hy프레딧 39건이 '[택배배송]'·'[택배배송/냉동]'
    # 으로 시작한다. _LEAD_BRACKET 이 괄호만 벗겨서 '택배배송 실리만 …' 이 됐다.
    s = _SHIP.sub("", s).lstrip()

    m = _LEAD_BRACKET.match(s)
    if m:
        inner, rest = m.group(1).strip(), s[m.end():]
        s = rest if (not inner or inner.isdigit()) else f"{inner} {rest}"

    m = _PREFIX.match(s)
    if m:
        head, rest = m.group(1), s[m.end():]
        # 1글자 접두는 CU 의 분류 코드다 — `도)`=도시락 `김)`=김밥 `샌)`=샌드위치
        # `햄)`·`샐)`·`면)`·`삼)`·`주)`·`랩)`·`핫)`. 전건 확인했고 상품명이 아니다.
        # 나머지는 떼지 않고 괄호만 벗긴다. 글자를 하나도 안 잃는 쪽이다.
        s = rest if (head in MAKER_PREFIXES or len(head) == 1) else f"{head} {rest}"

    s = _SPEC_PAREN.sub(" ", s)        # 괄호 안이 규격뿐이면 괄호째 버린다
    s = _sub_outside_parens(_MULT, s)
    s = _sub_outside_parens(_SPEC, s)
    # 규격을 떼고 나면 곱셈 꼬리만 허공에 남는 경우가 있다 —
    # '두부흑임자스낵 50g x 5개' 에서 _SPEC 가 '50g' 을 지워 'x 5개' 가 남았다.
    # _MULT 는 'x' 를 일부러 안 보는데(자이언트X3 때문) _SPEC 는 그 사정을
    # 모른다. 두 규칙이 서로를 모르니 뒤에서 한 번 더 턴다.
    s = _sub_outside_parens(_ORPHAN_MULT, s)
    s = re.sub(r"\(\s*\)", " ", s)
    s = _drop_unmatched_parens(s)
    s = _TAIL_PAREN.sub(r" (\1)", s)
    s = re.sub(r"\s+", " ", s).strip(" ·,/")
    return s if len(s.replace(" ", "")) >= 3 else src


def derive(d: dict, *, stored: bool = False) -> dict:
    """레지스트리·판정에서 나오는 값들을 채운다. 제자리에서 고치고 그대로 돌려준다.

    여기가 정본이어야 한다. 수집한 상품은 Item.to_dict() 로 들어오지만, 수집이
    실패한 브랜드의 이전분은 그 경로를 안 거쳐서 collect 가 따로 채워야 한다.
    전에 그 두 자리에 같은 계산을 각자 적어뒀더니 한쪽에만 image 정규화가 빠져서,
    수집이 실패한 브랜드만 http 이미지를 들고 들어와 카드가 빈 네모가 됐다.
    필드를 하나 더 늘릴 때 여기만 고치면 되게 둔다.
    """
    d["brand_type"], d["brand_sub"] = kind(d["brand"])
    d["url"] = d.get("url") or site(d["brand"])
    # 표시용 이름. 원본 name 은 건드리지 않는다(위 display_name 주석 참고).
    # 위의 nonfood·alcohol 과 달리 **매번 다시 계산한다** — 규칙을 고치면
    # 수집이 실패해 이월된 행도 같이 따라오게 하려는 것이다. 재료가 name
    # 하나뿐이라 다시 계산해도 잃을 값이 없다.
    d["display"] = display_name(d["name"])
    # 어댑터가 따로 표시하지 않았으면 이름·분류로 판정한다.
    #
    # `or` 라서 한 방향으로만 움직인다 — 어댑터가 True 를 찍었으면 규칙이
    # 몰라도 존중해야 하기 때문이다(GS25 '손앤박 하티' 처럼 이름으로는 못
    # 가리는 화장품). 문제는 **이미 파생된 값**에 같은 함수를 돌릴 때다.
    # 그때는 저장된 True 가 어댑터 뜻인지 옛 규칙의 결과인지 구분이 안 되고,
    # 단어 목록에서 단어를 빼도 안 풀린다. 실제로 '와인' 을 뺐는데 나폴레옹
    # 와인바게트가 계속 술로 남았다.
    #
    # stored=True 로 부르면 저장값을 무시하고 처음부터 다시 센다. 수집 실패
    # 이월분과 일괄 재계산이 그 경로다 — 거기엔 어댑터 뜻이 섞여 있지 않다.
    cat = d.get("category", "")
    # 어댑터가 찍은 값은 따로 기억해 둔다. 안 그러면 다시 계산할 때 그 뜻이
    # 사라진다 — '와인' 을 빼려고 전체를 재계산했더니 GS25 '손앤박 하티'
    # (어댑터가 화장품이라고 찍은 것)가 같이 풀렸다.
    if not stored:
        for k in ("nonfood", "alcohol"):
            if d.get(k):
                d.setdefault("by_adapter", []).append(k) if k not in d.get(
                    "by_adapter", []) else None
    said = set(d.get("by_adapter") or ())
    # 업체가 준 분류가 제일 확실하다. 이름만 보는 is_nonfood 는 '실리만 양손
    # 주방 가위'·'폴프랜즈 양말' 처럼 식품 같은 말이 하나도 안 든 것을 놓친다
    # (hy프레딧 61건이 그랬다). 단어를 더 넣는 대신 업체 분류를 믿는다 —
    # 단어 목록은 늘릴수록 '카스' 가 '카스테라' 를 지우는 사고가 난다.
    d["nonfood"] = ("nonfood" in said
                    or taxonomy.vendor_nonfood(d["brand"], cat)
                    or is_nonfood(d["name"], cat))
    d["alcohol"] = "alcohol" in said or is_alcohol(d["name"], cat, d["brand"])
    # 글자 칸에 None 이 들어오면 아래 어딘가에서 터진다. 어댑터가 한 번
    # 터지면 그 브랜드가 통째로 빠지는데 건수가 0 이라 급감 가드에도 안
    # 걸린다. 실제로 태리로제떡볶이 56건이 그렇게 날아갔다 — selectolax 의
    # `.attributes.get(k, "")` 는 값 없는 속성을 "키는 있고 값은 None" 으로
    # 주기 때문에 기본값 ""가 안 먹는다. 어댑터마다 `or ""` 를 적게 하는
    # 대신 정본인 여기서 한 번 턴다.
    for k in ("name", "name_en", "desc", "image", "category",
              "url", "released_at", "uploaded_at"):
        if d.get(k) is None:
            d[k] = ""

    # 우리 페이지는 https 라 http 이미지는 브라우저가 막는다(혼합 콘텐츠).
    # 빈 네모가 뜨느니 사진 없는 카드로 그리는 게 낫다.
    #
    # ⚠️ 주소를 **버리지 말고 image_src 에 옮긴다.** 전에는 그냥 지웠는데,
    # 그러면 되살릴 길이 없어진다. 에그드랍 73·퀴즈노스 62·쉐이크쉑 52·
    # 스쿨푸드 81건이 그렇게 사진 없는 카드가 됐다 — 그 호스트들은 https 를
    # 아예 안 열어서(ConnectError) 주소만 바꿔선 안 되고, 받아서 우리 쪽에
    # 두는 수밖에 없다. rules.mirror_images 가 image_src 를 보고 그 일을 한다.
    if d["image"].startswith("http://"):
        d["image_src"], d["image"] = d["image"], ""
    return d


def kind(brand: str) -> tuple:
    """등록되지 않은 브랜드는 조용히 넘기지 않고 드러낸다."""
    if brand not in BRANDS:
        raise KeyError(f"BRANDS 에 없는 브랜드: {brand}")
    return BRANDS[brand]


@dataclass
class Item:
    """브랜드 어댑터가 공통으로 뱉는 상품 1건.

    이 서비스의 용건은 '신제품'이다. 전체 카탈로그가 아니다.
    어댑터는 아래 세 신호로 신제품 여부를 최대한 알려줘야 한다.
      released_at  브랜드가 출시일/등록일을 알려주면 채운다. 가장 강한 신호.
      is_new       브랜드가 NEW 배지 등으로 신제품이라 표시하면 True.
                   신제품이 아니라고 확인되면 False. 알 수 없으면 None.
      promo        1+1·2+1 같은 행사/할인 상품. 신제품이 아니므로 화면에서 뺀다.
                   세트·콤보는 여기 쓰지 마라. collect.drop_sets() 가 이름으로
                   거른다. 어댑터마다 세트 기준이 달라져 신메뉴 세트가 잘렸다.
    셋 다 비어 있으면 '어제 없던 게 오늘 있다'는 diff 로만 판정하게 되고,
    그 브랜드는 합류 첫날엔 신제품을 하나도 못 내놓는다. 그래도 그게 정직하다.
    """
    brand: str
    name: str
    name_en: str = ""
    desc: str = ""
    image: str = ""
    labels: list = field(default_factory=list)   # ICE / HOT 등
    category: str = ""
    uploaded_at: str = ""                        # 브랜드가 알려주면 채움 (YYYY-MM-DD)
    released_at: str = ""                        # 출시일/등록일. uploaded_at 보다 강한 신호
    is_new: bool | None = None                   # 브랜드가 신제품이라 표시했는가
    promo: bool = False                          # 행사/할인 상품 (신제품 아님)
    nonfood: bool = False                        # 굿즈·생활용품. 먹는 게 아니라 따로 관리한다
    alcohol: bool = False                        # 술. 연령 확인이 없으니 본 목록에서 뺀다
    url: str = ""                                # 브랜드 사이트의 이 상품 페이지.
                                                 # 없으면 SITES 의 브랜드 메뉴 URL 로 떨어진다
    brand_type: str = ""                         # 레지스트리에서 채운다. 어댑터는 비워둔다
    brand_sub: str = ""                          # 프랜차이즈 세부분류(햄버거/피자/치킨)

    @property
    def key(self) -> str:
        return make_key(self.brand, self.name)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["key"] = self.key
        return derive(d)


# 해외 러너에서 국내 사이트는 간헐적으로 연결 실패·타임아웃이 난다.
# 연결 단계 재시도는 transport 가 맡고, 읽기 타임아웃은 retry() 로 감싼다.
# 한국 안에서 요청을 내보내고 싶을 때 쓰는 구멍. 환경변수가 없으면 아무
# 일도 안 한다(지금 로컬은 그대로 직접 나간다).
#
# 왜 필요한가 — 2026-10-08 러너에서 직접 쟀다. GitHub 호스팅 러너는 **지역을
# 고를 수 없고**(라벨이 OS·아키텍처뿐이다) 바깥 IP 가 해외(Azure)다. 한국
# 사이트 여럿이 그걸 막는다: 컴포즈·투썸·하이트진로·써브웨이가 403 이고
# 봇UA 든 브라우저UA 든 똑같다(UA 문제가 아니다). 세븐일레븐은 아예
# ConnectTimeout 이다. 상품의 19%가 그렇게 매일 이월되고 있었다.
#
# 한국 IP 를 거치면 풀린다. 어떤 경로를 쓸지는 운영자가 정하고(자체 VPS
# 프록시·Tailscale 출구 노드·VPN 등) 여기는 주소만 받는다.
PROXY = os.environ.get("SINSANG_PROXY", "").strip()


def client(**kw) -> httpx.Client:
    # 어댑터가 Referer 같은 헤더를 더할 수 있게 UA 위에 덮어쓴다.
    headers = {"User-Agent": UA} | dict(kw.pop("headers", {}))
    if PROXY:
        kw.setdefault("proxy", PROXY)
    kw.setdefault("timeout", httpx.Timeout(30.0, connect=15.0))
    # verify 는 transport 에 넘겨야 한다. httpx.Client(transport=..., verify=...) 는
    # transport 가 있으면 verify 를 조용히 무시한다. 이걸 모르고 구형 TLS 사이트
    # 4곳(또래오래·노랑통닭·훌랄라·지코바)이 '연결 불가'로 잘못 판정됐다.
    verify = kw.pop("verify", True)
    return httpx.Client(headers=headers, follow_redirects=True,
                        transport=httpx.HTTPTransport(retries=3, verify=verify), **kw)


def retry(fn, tries: int = 3, delay: float = 2.0):
    """일시적 오류는 간격을 늘려가며 다시 시도한다. 끝까지 실패하면 그대로 올린다."""
    for i in range(tries):
        try:
            return fn()
        except (httpx.TransportError, httpx.HTTPStatusError):
            if i == tries - 1:
                raise
            time.sleep(delay * (i + 1))
