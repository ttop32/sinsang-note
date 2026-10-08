"""대상(청정원·종가) — 뉴스 게시판 JSON **+ 대상홀딩스 그룹소식** 에서 신제품을 뽑는다.

## 🔴 2026-10-08 소스 보강 — 자사 게시판이 그룹 보드의 **8분의 1** 이었다

아래 원래 조사는 `daesang.com` 자사 뉴스 게시판만 보고 "3개월에 1건, 이 레포에서
가장 낮은 축" 이라고 적었다. **그 판정이 소스 탓이었다.** 같은 날 받은 두 보드:

| 보드 | 1페이지 | 300일 안 행 수 | 최신 글 | 창 안 출시 기사 |
|---|---:|---:|---|---:|
| `daesang.com` 자사 뉴스 (`boardListJson.jsp`) | 6건 | 30 | **2026-09-08** | **3** |
| `daesangholdings.com` 그룹소식 (`news.php`) | 20건 | 110 | **2026-10-06** | **22** |

자사 게시판은 **한 달 멈춰 있고**, 들어 있는 30건의 성격도 기부·협약·박람회·
기획전으로 치우쳐 있다. 그룹 보드에는 같은 기간의 청정원·종가 출시 기사가
그대로 다 있다(아래 §그룹 보드). 신세계그룹 뉴스룸으로 신세계푸드를 5→12 로
올린 것과 **같은 수법**이고, 효과는 더 크다 — **보강 전 3건 → 후 20건.**

**회귀 확인 (2026-10-08)**: `_fetch_own()` 단독 = **3건 그대로**
(알룰로스·피클링소스·화이트식초). 아래 🔴 의 `_pick` 수정 2건이 원래 3건을
건드리지 않는다는 뜻이다. 이 모듈은 브랜드가 `대상` 하나뿐이라(`BRANDS` 없음)
같이 담긴 다른 브랜드가 줄어들 자리도 없다.

⚠️ **자사 보드를 떼지 않았다.** 두 보드는 같은 기사에 **다른 날짜**를 붙인다
   (실측: `알룰로스 3종 출시` 가 자사 2026-08-10 / 그룹 2026-07-28, 13일 차).
   그룹 쪽이 늘 더 이르다(그쪽이 원 배포일로 보인다). 그래도 **자사 보드를 먼저
   돌리고 그룹 보드를 뒤에 더한다** — 원래 어댑터가 내보내던 3건의 날짜·사진·URL 이
   그대로 유지돼야 회귀가 없기 때문이다. 겹치는 기사는 `make_key` 로 걸러진다.

## 그룹 보드 — `daesangholdings.com` 그룹소식 (2026-10-08 실측)

    GET https://www.daesangholdings.com/child/sub/bbs/news.php?page=N&code=news
        200 / 약 37KB / **한 페이지 20건**. 완전 SSR, 쿠키·토큰 없음.
    <li class="photo_b grid-8">
      <a href="/child/sub/bbs/news.php?ptype=view&idx=6728&page=1&code=news">
        <div class="photo_image" style="background-image:url(/adm/data/bbs/news/S2610060307527_1.png);"></div></a>
      <div class="photo_body">
        <div class="writer">대상주식회사</div>          ← ★ 계열사를 서버가 준다
        <div class="name"><a href="…">대상 종가, … '볶음깍두기' 신제품 출시</a></div>
        <div class="date">2026-10-06</div>
      </div></li>
    robots.txt → 200 / 21B / `User-agent: * / Allow:/` — 규칙 없음.

**이 보드의 핵심은 `div.writer` 다.** 제목 주어로만 가르던 것을 서버가 준 계열사
이름으로 한 번 더 받친다. 6페이지 120건 실측 분포 —

    대상주식회사 52  ← ✅ 우리가 쓰는 쪽(청정원·종가·호밍스·그레인보우)
    대상웰라이프 38  ← ❌ 뉴케어·것시스. 환자식·건기식이고 회사가 다르다
    대상펫라이프  8  ← ❌ 펫푸드. 사람이 먹는 게 아니다
    대상그룹      7  ← ❌ ESG·사회공헌
    대상다이브스  5  ← ❌ 복음자리(잼·커피). 회사가 다르다
    혜성프로비젼  5  ← ❌ 육가공. 회사가 다르다
    대상홀딩스    2  ← ❌ 지주
    (그 밖에 `대상주식회`·`대상웰라이` 처럼 **끝 글자가 잘려 오는 행이 3건** 있다.
     그래서 완전 일치가 아니라 **접두 일치**로 받는다. 잘린 글자를 못 보고
     `== "대상주식회사"` 로 짰으면 2건이 조용히 샜다.)

⚠️ **`writer` 만 믿지 않는다.** 원래 어댑터의 `_subject_ok`(제목 주어 접두)를
   그대로 한 번 더 통과시킨다 — `대상주식회사` 가 쓴 글에도 `대상 정원e샵`
   (자사몰 할인 기획전)이 섞여 있다(실측 3건). 사조가 `img_area_s` 의 `alt` 를
   믿었다가 펫푸드를 식품으로 올릴 뻔한 것과 같은 자리다.

## 배지·날짜 실측 (2026-10-08. 숫자로 박아 둔다 — "그 배지가 진짜냐" 를 받는 자리다)

**배지 = 100% (20/20 `is_new=True`). 이건 정상이다.**
여기는 카탈로그가 아니라 **'출시' 라고 쓴 보도자료만 골라내는 추출**이다. 에밀리아젤라또
7/7, 뚜레쥬르 11/442 와 같은 칸이다. 카탈로그를 전부 신상으로 만든 것과 구분하려면
**배지 비율이 아니라 '집히는 비율'** 을 봐야 한다 —

    그룹 보드 6페이지 120행 → 창(300일) 안 110행
      그중 writer=대상주식회… …… 52행   ← 분모
      그중 제목이 상품으로 집힘 … 20건   ← 분자. **38.5%**
      (자사 보드와 겹치는 3건은 `make_key` 로 병합 → 합계 **20건**)
    나머지 32행이 왜 떨어졌나(전수로 읽음): 사회공헌·기부 6 · 박람회/전시 5 ·
    수상/인증 5 · 캠페인/광고 영상 4 · 할인 기획전 3(`대상 정원e샵`) ·
    선물세트 3 · 실적/투자 2 · 패키지 리뉴얼 1 · 브랜드 엠블럼 1 ·
    **상품명에 `·`/`&` 가 들어 아래 '아는 손실' 로 버려진 2건**
    → `fetch()` 가 이 38.5% 를 `HOLD_MAX_PICK_RATIO=0.65` 로 지킨다.

### ⚠️ 아는 손실 — `_pick` 의 `·`/`&` 문자 금지가 진짜 신제품 2건을 버린다

2026-10-08 검수가 실측으로 잡았다. `_pick` 끝의
`if any(c in name for c in "·∙&?"): return ""` 에 걸리는 창 안 기사 2건 —

    2026-06-25 대상 청정원, 여름철 입맛 돋우는 ‘콩담백면 열무비빔국수·열무물냉면’ 출시
    2026-01-13 대상 청정원, 저당 곡물 식단 ‘그레인보우’ 신제품 ‘치킨&바질’ 출시

앞엣것은 **따옴표 하나에 상품 둘**이라 버리는 게 옳다(이름을 하나로 못 고른다).
뒤엣것(`치킨&바질`)은 **단일 상품**이라 진짜 손실이다.
→ **이번에 고치지 않았다.** 이 금지는 `maker_orion`·`maker_cj`·`hanwhagalleria_press`
  가 **똑같이** 들고 있는 레포 공통 규칙이고(오리온 `‘칡냉면’·’쫄냉면’ 출시` 에서
  닫는 따옴표가 `’` 로 와 정규식이 뒤쪽을 못 잡은 사고가 출처다), 여기서만 풀면
  계보가 갈라진다. **소스 보강 범위 밖**이라 기록만 남긴다.
  고치려면 세 파일을 같이 보고 `·` 는 '따옴표 안에 상품이 둘' 신호로, `&` 는
  단일 상품명의 일부로 갈라야 한다.

### ⚠️ 알고 감수하는 날짜 오차 — 최대 13일

두 보드가 같은 기사에 다른 날짜를 주고(아래 §그룹 보드) **그룹 쪽이 진짜 배포일**이다.
2026-10-08 검수가 상세 페이지로 확인했다 — 그룹 `idx=6680` 본문에 `작성일 : 2026-07-28`
이 박혀 있고, 자사 JSON 은 같은 기사를 `reg_dt 2026-08-10` 으로 준다.
그런데 `fetch()` 는 **자사 보드를 먼저 넣으므로 덜 정확한 08-10 이 남는다.**
회귀(원래 3건의 값 유지)를 택한 결과이고, **신선도 판단에 최대 13일 오차**를 안는다.
60일 창 기준으로는 안전한 폭이라 그대로 둔다.

**날짜 = 100% (20/20 `released_at`). 일괄 등록 흔적이 없다.**
120건 중 서로 다른 날짜가 **99개**고 하루 최대가 **4건**(2025-12-19)이다.
→ `released_at` 에 넣는다(자사 보드와 같은 판단). `HOLD_MAX_PER_DAY=8` 가 지킨다.
⚠️ **여기는 워드프레스가 아니다.** `modified` 에 해당하는 필드가 아예 없고
   `div.date` 하나뿐이라 신세계(200건 중 122건이 `date`≠`modified`, 최대 541일)·
   피자스쿨(`modified` 안에 2015년 치즈피자) 류의 함정이 생길 자리가 없다.

**상품명이 안 뽑히는 기사는 접는다.** 달콤왕가탕후루 선례(따옴표 안이 '여름시즌한정'
이라 상품명이 시즌 표기가 됐다)와 같은 자리를 22건 전수로 확인했고, 그래서 나온 게
아래 🔴 의 버그 2건이다. 둘 다 막았다.

⚠️ **`search=` 로 거르지 않았다.** 신세계 뉴스룸에서 `search=신세계푸드` 300일 113건이
   전부 본문 어딘가에 그 말을 담고 있던 사고와 같은 이유다. 여기는 **`div.writer`
   (서버가 준 계열사) + 제목 주어 접두** 두 관문으로 가른다. 본문은 보지 않는다 —
   목록만으로 둘 다 되기 때문에 상세를 받을 일이 없다(요청 6회로 끝난다).

**사진 — 자사 보드와 달리 진짜 `image/png` 로 온다.** 실측
`/adm/data/bbs/news/S2610060307527_1.png` → 200 / `image/png` / 431,089B.
자사 보드의 `download.jsp`(octet-stream, `verify_images()` 가 지움)와 달리
**화면에 실제로 뜬다.**

## 🔴 보강하며 고친 `_pick` 버그 2건 (둘 다 그룹 보드 22건 전수에서 잡혔다)

① `대상 청정원, 브랜드 론칭 30주년 기념 엠블럼 공개` → 상품명이 **`브랜드`** 로
   나왔다. 따옴표가 없어 머리 전체를 쓰는 분기인데 `_LEAD` 를 떼고 나면
   `브랜드` 한 낱말만 남는다. → **`maker_cj.py` 의 규칙을 가져왔다** —
   `론칭/런칭` + 머리에 `브랜드` 면 브랜드 출범이지 상품이 아니다. 거기에
   더해 `_GENERIC`(브랜드·신제품·제품·라인업…)을 상품명으로 못 쓰게 막았다.
   ⚠️ `출시` 는 건드리지 않았다 — `청정원 호밍스 브랜드 신제품 ‘X’ 출시` 꼴은
      진짜 신제품이다(삼양·CJ 가 같은 이유로 동사로 갈랐다).
② `대상, 메가박스와 협업 2탄 ‘복음자리 스페셜 딸기 메뉴 4종’ 출시` →
   **극장에서 파는 메뉴**지 대상이 내는 상품이 아니다. `협업` 이 따옴표
   **앞**에 있어서 `_BETWEEN`(따옴표와 동사 **사이**만 본다)에 안 걸린다.
   → `_REPACK_NAME` 에 **`메뉴`** 를 넣었다. 제조사 상품 이름이 `…메뉴` 로
     끝나는 일은 없다. (자사 보드 3건에는 영향이 없다 — 재실행으로 확인.)

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

from selectolax.parser import HTMLParser

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

# --- 그룹 보드(대상홀딩스 그룹소식). 사유는 docstring 🔴 ----------------------
HOLD_SITE = "https://www.daesangholdings.com"
HOLD_LIST = HOLD_SITE + "/child/sub/bbs/news.php"
HOLD_PER_PAGE = 20   # 2026-10-08 실측
HOLD_MAX_PAGES = 8   # 20건×8 = 160건 ≈ 15개월. 폭주 방지 상한(창은 DAYS 가 끊는다).
# `div.writer` 가 주는 계열사. **접두**로 본다 — 끝 글자가 잘려 오는 행이 있다.
HOLD_WRITER_LEAD = "대상주식회"
# 창 안 `대상주식회사` 행 가운데 상품으로 집히는 비율의 상한. 2026-10-08 실측
# 22/52 = 42.3%. 제목 역필터가 통째로 풀리면 ESG·기획전까지 상품이 된다.
HOLD_MAX_PICK_RATIO = 0.65
# 같은 날짜에 이만큼 몰리면 일괄 등록으로 보고 터뜨린다. 실측 최대 4건(2025-12-19).
HOLD_MAX_PER_DAY = 8
_HOLD_BG = re.compile(r"url\(\s*['\"]?([^'\")]+)")

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
_REPACK_NAME = ("에디션", "컬렉션", "한정판", "선물세트", "기획팩", "시리즈",
                # 극장·식당에서 파는 '메뉴' 는 제조사 상품이 아니다. 실측:
                # `대상, 메가박스와 협업 2탄 ‘복음자리 스페셜 딸기 메뉴 4종’ 출시`
                # (docstring 🔴②). 제조사 상품명이 '메뉴' 로 끝나는 일은 없다.
                "메뉴")
# 따옴표가 없어 머리 전체를 상품명으로 쓰는 분기에서 남는 껍데기 말.
# 실측: `대상 청정원, 브랜드 론칭 30주년 기념 엠블럼 공개` → '브랜드'.
_GENERIC = {"브랜드", "신제품", "제품", "신상품", "라인업", "시리즈", "패키지"}
# 브랜드 출범에 쓰이는 동사. `론칭/런칭` + 머리에 '브랜드' 면 상품이 아니다
# (maker_cj.py·maker_samyang.py 와 같은 규칙).
_LAUNCH_ONLY = re.compile(r"(론칭|런칭)")


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
    # `브랜드 … 론칭` 은 브랜드 출범이지 상품 출시가 아니다(docstring 🔴①).
    if _LAUNCH_ONLY.match(verb.group(1)) and "브랜드" in head:
        return ""
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
    # 껍데기 말만 남은 경우. 따옴표 없는 제목에서 머리 전체를 쓸 때 난다.
    if name in _GENERIC:
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


def _hold_rows(html: str) -> list[tuple]:
    """그룹소식 목록 HTML → (날짜, 계열사, 제목, idx, 이미지) 목록."""
    out = []
    for li in HTMLParser(html).css("li"):
        a = li.css_first("div.name a")
        if a is None:
            continue
        # ⚠️ selectolax 는 값 없는 속성에 None 을 준다. 기본값이 안 먹는다.
        href = a.attributes.get("href") or ""
        m = re.search(r"idx=(\d+)", href)
        w = li.css_first("div.writer")
        d = li.css_first("div.date")
        ph = li.css_first("div.photo_image")
        style = (ph.attributes.get("style") or "") if ph is not None else ""
        bg = _HOLD_BG.search(style)
        src = (bg.group(1).strip() if bg else "")
        out.append((
            _date((" ".join(d.text().split()) if d is not None else "").replace("-", ".")),
            " ".join(w.text().split()) if w is not None else "",
            " ".join(a.text().split()),
            m.group(1) if m else "",
            (HOLD_SITE + src) if src.startswith("/") else src,
        ))
    return out


def _fetch_holdings(floor: str) -> tuple[list[Item], dict]:
    """대상홀딩스 그룹소식에서 대상(식품) 신제품을 뽑는다. (상품, 진단) 로 돌려준다.

    자사 게시판(`daesang.com`)이 한 달씩 멈추는 동안에도 여기는 돈다.
    사유·실측은 docstring 🔴 참고.
    """
    items: list[Item] = []
    rows_seen = 0                  # 읽은 행 수 전체
    ours = 0                       # 창 안 `대상주식회사` 행 수
    writers: set = set()           # 가드 진단용
    per_day: dict = {}
    stop = False
    with base.client() as c:
        for page in range(1, HOLD_MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(HOLD_LIST, params={"page": page,
                                                            "code": "news"}))
            r.raise_for_status()
            rows = _hold_rows(r.text)
            # 목록 0행은 고장이다. 상품 0건은 정상일 수 있어도 이건 아니다.
            if page == 1 and not rows:
                raise ValueError(
                    f"대상홀딩스 그룹소식 1페이지가 비었다. {r.url} → "
                    f"{len(r.content)}B — 목록 셀렉터(li / div.name a / "
                    f"div.writer / div.date)가 바뀌었는지 확인하라")
            if not rows:
                break
            rows_seen += len(rows)

            for released, writer, title, idx, img in rows:
                writers.add(writer)
                if not released:
                    # 날짜 없는 is_new=True 는 90일 동안 화면에 눌러앉는다.
                    continue
                if released < floor:
                    stop = True
                    continue
                if not writer.startswith(HOLD_WRITER_LEAD):
                    continue
                ours += 1
                per_day[released] = per_day.get(released, 0) + 1
                # ⚠️ writer 만 믿지 않는다. `대상 정원e샵`(자사몰 기획전)이
                #    같은 writer 로 올라온다. 제목 주어도 함께 본다.
                if not _subject_ok(title):
                    continue
                name = _pick(title)
                if not name:
                    continue
                items.append(Item(
                    brand=BRAND,
                    name=name,
                    desc=_LEAD.sub("", title),
                    image=img,          # 진짜 image/png 다(docstring §사진)
                    category="조미료",
                    released_at=released,
                    is_new=True,        # 브랜드가 '출시' 라고 낸 기사다
                    url=(f"{HOLD_LIST}?ptype=view&idx={idx}&code=news"
                         if idx else HOLD_LIST),
                ))
            if stop:
                break

    return items, {"rows": rows_seen, "ours": ours,
                   "writers": writers, "per_day": per_day}


def _fetch_own() -> list[Item]:
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


def fetch() -> list[Item]:
    """자사 보드를 먼저 돌리고 그룹 보드를 뒤에 더한다.

    순서가 뜻이 있다 — 두 보드가 같은 기사에 **다른 날짜**를 붙이기 때문에
    (실측 13일 차), 먼저 넣은 쪽이 남아야 원래 3건의 날짜·사진·URL 이
    그대로 유지된다. 겹치는 기사는 `make_key` 로 걸러진다.
    """
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    items = _fetch_own()
    keys = {i.key for i in items}
    own = len(items)

    extra, diag = _fetch_holdings(floor)
    for it in extra:
        if it.key not in keys:
            keys.add(it.key)
            items.append(it)

    # --- 그룹 보드 가드. 조용한 빈 리스트·조용한 폭주를 둘 다 막는다 ---------
    # ① 계열사 칸이 사라지면 전건이 조용히 떨어져 보강분이 0 이 된다.
    if not diag["ours"]:
        raise ValueError(
            f"대상홀딩스 그룹소식에서 '{HOLD_WRITER_LEAD}…' 계열사 행이 0건이다"
            f"(읽은 행 {diag['rows']}). 읽힌 계열사={sorted(diag['writers'])} — "
            f"div.writer 표기가 바뀌었는지 확인하라 "
            f"(2026-10-08 실측 120행 중 대상주식회사 52행)")
    # ② 반대쪽. 제목 역필터가 풀리면 ESG·기획전까지 상품이 된다.
    ratio = (len(extra) / diag["ours"]) if diag["ours"] else 0.0
    if ratio > HOLD_MAX_PICK_RATIO:
        raise ValueError(
            f"대상홀딩스 그룹소식: 대상주식회사 {diag['ours']}행 중 "
            f"{len(extra)}건({ratio:.0%})이 상품으로 집혔다 — 기대 "
            f"{HOLD_MAX_PICK_RATIO:.0%} 이하(2026-10-08 실측 22/52=42%). "
            f"_SKIP·_subject_ok 가 풀렸는지 확인하라")
    # ③ 일괄 등록. 실측은 하루 최대 4건이다. 날짜를 한꺼번에 갈면 메뉴판이
    #    통째로 신상이 되는데 released_at 이라 60일 창에 그대로 걸린다.
    if diag["per_day"]:
        day, n = max(diag["per_day"].items(), key=lambda kv: kv[1])
        if n >= HOLD_MAX_PER_DAY:
            raise ValueError(
                f"대상홀딩스 그룹소식: {day} 하루에 대상주식회사 글이 {n}건이다"
                f"(2026-10-08 실측 최대 4건). 일괄 재등록이면 released_at 을 "
                f"그대로 쓰면 안 된다 — uploaded_at 으로 내려야 한다")
    # ④ 보강이 통째로 죽으면 원래 3건만 남는데 그건 '정상'처럼 보인다.
    #    그룹 보드가 자사 보드보다 3배 이상 두꺼운 게 이 브랜드의 전제다.
    if len(items) <= own:
        raise ValueError(
            f"대상: 그룹 보드가 보탠 상품이 0건이다(자사 {own}건 그대로). "
            f"대상주식회사 행 {diag['ours']}건은 읽혔다 — _pick 이 전부 "
            f"버렸는지 확인하라 (2026-10-08 실측 보강 후 20건)")
    return items
