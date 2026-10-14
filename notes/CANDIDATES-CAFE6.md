# 카페(공정위 `커피`) 6차 — CAFE5 "다음 후보 5곳" 마무리 + 110위 아래 긴 꼬리

`CANDIDATES-CAFE5.md`(2026-10-08) 의 후속이다. 조사일 **2026-10-14**.
**등록(`base.BRANDS`·`SITES`·`collect.ADAPTERS`)·커밋은 하지 않았다.**

## 1. CAFE5 §6 "다음 후보 순서" 5곳 — 결과

| 순위 | 브랜드 | 가맹점 | 결과 | 파일 / 사유 |
|---:|---|---:|---|---|
| 47 | **발도스커피** | 91 | ✅ **어댑터** — 28건 / 첫날 **4건** | `collectors/cafe_valdos.py` |
| 98 | **카페16온스** | 31 | ✅ **어댑터** — 4건 / 첫날 0건 | `collectors/cafe_cafe16oz.py` |
| 94 | **쿼드커피** | 33 | ✅ **어댑터** — 11건 / 첫날 0건 | `collectors/cafe_quad.py` |
| 52 | 달.콤(dal.komm) | 76 | ⛔ **보도자료가 끊겼고, 메뉴 날짜는 시즌 재업로드로 오염** | 아래 §1-4 |
| 62 | 핸즈커피 | 58 | ⛔ **상품명이 이미지 안에만 있다** | 아래 §1-5 |

등록 제안은 셋 다 **`(CAFE, "커피")`**. 셋 다 검수 서브에이전트를 붙였고 지적은 전부 반영했다.

### 1-1. ✅ 발도스커피 — `collectors/cafe_valdos.py`

- SITES `http://valdos.co.kr/bbs/bbs/board.php?bo_table=m31` (⚠️ http 만).
- 소스: `New & season` 그누보드 갤러리 **앞 2쪽(16글)**. 글 본문 = 상품명을 `&` 로 이은 것 → 쪼갠다.
  제목(`2026 가을 신메뉴`)은 묶음 이름이라 안 쓴다. 본문이 빈 글(`제로슈가`·`디카페인` = 옵션 공지)은 버린다.
- 날짜: 목록·글 보기·RSS 어디에도 제대로 없다(글 보기 작성일이 `-0001-11-30`, RSS 는 8글 중 4글만).
  **원본 이미지 `HEAD` 의 `Last-Modified`** 를 쓴다 — RSS 가 날짜를 준 4글과 **초 단위까지** 일치.
  `uploaded_at` 에만 넣고, 목록 순서 보정(나보다 새 글들의 가장 이른 날짜로 깎기)을 한다.
- 🔴 게시판에 **일괄 재업로드 이력**이 있다(9쪽 67글 전수: 2024-02-13 24글·2024-02-05 18글·2025-06-11 6글).
  그래서 창 안에서 **같은 날 글이 3개 이상**이면 터뜨린다(검수 재현: 맨 위 5글 재업로드 시 옛 메뉴 7건이 신상이 됐다).
- 🔴 **매년 돌아오는 시즌 글**(`2023~2026 컵빙수`): 제목이 연도로 시작하고 `신메뉴` 가 없으면 글째 버린다.
- `is_new` 는 주지 않는다(9쪽짜리 아카이브라 배지로 쓰면 하이오커피 사고).
- 첫날 4건: `초당옥수수라떼` · `초당옥수수크림커피` · `리얼알밤빵`(09-16) · `바질토마토치아바타샌드위치`(09-07).

### 1-2. ✅ 카페16온스 — `collectors/cafe_cafe16oz.py`

- SITES `https://cafe16oz.com/bbs/m01.php`. 손으로 짠 정적 HTML 의 `신메뉴` 칸 카드 4장(상품 단위).
- 날짜: 이미지 정적 파일의 `Last-Modified`(리치 3종 2026-01-15 13분 간격으로 하나씩, 블랙시크릿라떼 2025-11-27).
- 🔴 검수 지적으로 고쳤다 — 처음엔 `logo.png` 하나와 대조했는데 **이 사이트는 2025-09-10 에 전메뉴 사진 21장을
  한꺼번에 올렸고 그날 로고는 안 바뀌었다.** 지금은 **전메뉴의 `/img` 파일 23장 + 로고**를 대조 묶음으로 받아,
  카드 사진 ±2시간 안에 대조 파일이 3개 이상이면 일괄 업로드로 보고 날짜를 버린다.
- ⚠️ 남는 구멍: `coffee23.png`(블랙시크릿라떼)는 전메뉴와 같은 파일이라 **그 한 장만** 교체하면 1건이 60일간 뜬다.
- 배지 4/4(칸 전체가 신메뉴). 날짜가 판정한다. 첫날 0건(최근 2026-01-15).

### 1-3. ✅ 쿼드커피 — `collectors/cafe_quad.py`

- SITES `https://www.quadcoffee.co.kr/board/notice`. 공지사항의 **`[신메뉴]` 말머리 글**(현재 5글, 2026-04-01~07-21).
- 상품명 = 본문(인스타 캡션)의 **"이모지 + 이름" 한 줄**(`🥑🍌 아보카도바나나스무디`). 캠페인 줄(`🍉⚡쿼드 스낵클럽 개장⚡🌭`)은
  이름 뒤에 이모지가 또 와서 걸러진다. 미끼 줄(`📍전국 쿼드커피 매장`·`🎁 증정 이벤트`)은 제외 단어로 거른다.
- 🔴 **'[신메뉴]' 인데 작년 메뉴 복귀 글**이 있다(컵빙수 "작년에 핫했던 … COME BACK!"). `COME BACK·컴백·재출시·재판매·
  돌아왔/온·다시 찾아·작년·올해도·앵콜` 이 본문에 있으면 글째 버린다(검수가 "올해도 돌아온" 을 놓치는 걸 재현해서 넓혔다).
- 같은 상품이 여러 글에 나오면 **가장 이른 글 날짜**를 남긴다('모음' 글 대비).
- 날짜: 글 작성일 → `released_at`(본문 "7/21 공식 출시" 와 일치). 첫날 0건(최근 2026-07-21).
- ⚠️ 놓치는 꼴: 상품 하나뿐인 글은 이름을 문장 속에 쓴다(버터떡) — 안 잡는다(빠지는 방향).
- 검수 교차검증: `MENU > 푸드` 32개 중 `핫도그`·`국물떡볶이` 만 썸네일 날짜가 글 작성일(2026-06-23)과 같다 →
  썸머스낵클럽의 핫도그·떡볶이는 진짜 새 메뉴. 나머지 메뉴판은 2026-04-02 사이트 개편 일괄이라 날짜로 못 쓴다.

### 1-4. ⛔ 달.콤 — 보도자료형으로 열 수 있다던 자리. **2026년엔 달콤커피 자체 출시 기사가 없다**

- `/news?page=1..11` 55건 전수: 2026년 출시 기사는 **전부 자매 브랜드 `달콤.N`**(숙성라떼·반반 베이글·우베 3종…).
  달콤커피 자신의 마지막 출시 기사는 **2026-01-14 딸기 3종**, 2026-04-07 은 「인기 메뉴 **재출시**」.
- 기사 본문의 인용부호 이름 ∩ 현재 메뉴판(10칸 133개)으로 걸러 보면 **5건, 전부 2025년 빙수·수박주스**뿐이다.
- 메뉴판 썸네일 경로에 날짜가 있지만(`/menu/thumbnail/20260528140337_…png`) **시즌 재업로드로 오염**됐다 —
  2025-05 에 출시한 전통팥빙수·망고요거트빙수·1인 빙수 2종·리얼수박주스가 **2026-05-28** 날짜를 달고 있고,
  2026-01-09 에는 기존 베이글 12종이 한꺼번에 재업로드됐다. 교차검증 축이 없다 → ⛔.
- 🟡 **다음 수**: `달콤.N` 은 별도 메뉴(`/menu?brand_cd=DALKOMM_N`)·별도 보도자료 흐름이 살아 있다(가맹 10곳).
  카페 저가 브랜드로 따로 붙일지는 등록 담당 판단. 지금 달콤 어댑터를 만들면 0건짜리다.

### 1-5. ⛔ 핸즈커피 — 상품명이 이미지 안에만 있다

- 신메뉴 게시판은 `…/new_hands/board/new_board.php?bo_table=menu_new`(⚠️ `bbs/board.php` 는 PHP Warning 범벅 껍데기).
  글 날짜(2026.09.08 등)는 진짜인데 **본문이 이미지뿐**이다. `alt` 가 파일명이라 글마다 다르다 —
  최신 글은 `2026_가을시즌_홈페이지_게시판용_야플시나몬핫.png`, 바로 전 글은 `게시판1.png`(**NFD 한글**이라 grep 도 안 걸린다).
  상품명을 뽑을 텍스트가 없다 → ⛔.

---

## 2. 110위 아래 긴 꼬리 (182곳) + 30~109위 도메인 미확정 5곳 = 187곳

스크리닝은 하위 에이전트(지시서: 판정만, 브랜드당 3~5요청)가 했고 🟢 은 내가 직접 열어 판정했다. 조사일 2026-10-14.

**진행: 187/187곳 판정.** 집계: ⬜ 117 · ⛔ 61 · ⚠️ 4 · ✅ 2 · 🟡 1 · 🔴 1 · ✅🟡 1

⚠️ **검색 예산 소진** — 스크리너가 100번째 무렵부터 WebSearch 세션 한도(200회)를 다 썼다. 그 뒤 67곳은 **프차몰 링크 + 로마자/한글
도메인 추측만**으로 판정했다. 그 구간의 ⬜·🔴 는 `·확정아님` 을 붙였다 — "사이트가 없다" 가 아니라 "못 찾았다" 다.

> **이 업종 긴 꼬리의 모양** — 가맹점 5~25개 카페의 ⬜(사이트 못 찾음)가 절반을 넘는다. 사이트가 있어도 아임웹 원페이지·창업 모객
> 랜딩이 대부분이고, 아임웹 CDN 날짜만 있고 교차축이 없는 곳(⛔)이 많다. 쓸 만한 건 **출시 글 게시판에 상품명이 텍스트로 있는 곳**
> (비엔나커피하우스) 하나였다.

### 2-1. ✅ 비엔나커피하우스 — `collectors/cafe_vienna.py` (16건 / 첫날 1건, 886c9491 배선)
- 공지 제목 `"… (상품명)" 출시 안내` 에서 이름, 글 날짜 → `released_at`. 괄호가 한글이면 안쪽, 영문이면 바깥. `N종`·`시리즈`·`컬렉션`·`시즌` 묶음은 버린다.
- 🔴 `고창 수박 주스` 가 2025-07-17·2026-06-18 두 번 출시 안내로 올라왔다 → 4쪽을 다 읽고 **같은 이름은 가장 이른 날짜**.
- 2025-07-17 에 글 7개가 같은 날(사이트 이전 재게시) → 창 안 같은 날 글 4개 이상이면 raise.
- 첫날 1건: 솔티카라멜 팝 아이스크림(2026-09-09).

### 2-1b. ✅ 템포커피 — `collectors/cafe_tempo.py` (4건 / 첫날 0건)
- 등록 제안 `(CAFE, "커피")` · SITES `http://tempocoffee.co.kr/web/cop/bbsWeb/selectBoardList.do?bbsId=BBSMSTR_000000000191` (http, https 거부)
- NEWS 게시판 `ul.list_news` 6글 중 신메뉴 2글(2026-05-14). 제목 괄호 안 `(진미숫가루라떼, 겐마이현미 녹차)` 를 `,` 로 쪼갠다.
  EVENT 게시판의 같은 날 글은 제목에 이름이 없어 안 쓴다. 신메뉴 글이 해에 한 번 남짓이라 `ALLOW_EMPTY = True`·`DAYS = 540`.

### 2-1c. ✅(🟡 배선 보류 권고) STACKBEAN — `collectors/cafe_stackbean.py` (98건 / 첫날 0건)
- 등록 제안 `(CAFE, "커피")` · SITES `http://stackbean.co.kr/product/list.php?ca_id=10` (http, https 자체서명)
- 상위 칸 10·20·30·40 × 페이징(홈 링크의 하위 탭만 따라가면 105개 중 49개만 받는다 — 검수 지적으로 바꿨다). `30` 의 대용량 변형(`1.1L …`·`MAX …` 8건) 제외.
- 상품 이미지 `/product/data/item/<10자리>/` 의 번호 = 상품 레코드 생성 시각. 검수가 이미지 Last-Modified 49/49 로 확인(번호 ≤ 파일, 15초~34분),
  사진 일괄 교체(2025-01-15 23장)에도 번호는 그대로.
- 🔴 **재등록 — 막는 것과 못 막는 것**
  - 막는다: 최근 번호인데 `NEW / HEALTHY`(10) 칸에 없으면 날짜를 버린다(2025년 새 상품 26건이 전부 10 칸). 시뮬: 일반 칸 13건을 오늘 재등록 → 노출 0.
  - **못 막는다**: 겨울 메뉴를 지웠다가 다음 겨울에 **10 칸으로** 다시 만들면 진짜 신상과 구별할 축이 사이트에 없다. 시뮬: 2025-11-18 5종을 오늘 번호로 → **노출 5건**(뱅쇼·샹그리아 스파클링 등).
  - 하루 묶음(2025-08-21 프로틴 12 + 시트러스 7)이 진짜 라인인지 재등록인지도 사이트 안에서는 10 칸 여부 말고 **가를 축이 없다.**
  → 등록 담당 판단: 이 구멍 때문에 **안 붙이는 게 맞을 수 있다**(조정자 기준 "못 막으면 안 붙인다").

### 2-2. 순위표 — 판정한 곳 전부 (스크리닝 결과. 내가 직접 열어 뒤집거나 만든 곳 — 소미담·아이캔커피·라떼킹·비엔나·템포·STACKBEAN — 만 보정)

| # | 브랜드 | 가맹점 | 공식 사이트 | 판정 | 신상 신호 / 근거 | 불가 사유 · 다음 할 일 |
|---:|---|---:|---|---|---|---|
| 1 | 랑데자뷰(RENDEJAVOUS) | 25 | https://rendejavous.com/default/ | ⛔ | 메뉴 게시판(sub03, idx≤104) 배지 요소0·날짜0, EUC-KR. 뉴스 게시판 글1건(2022-03) | 메뉴 목록은 idx 순서뿐, 날짜·배지 없음. 루트는 meta refresh→/default/ |
| 2 | 커피볶는시골커피 | 25 | https://sigolcoffee.com | ⛔ | 창업 모객 원페이지(내부링크 2개), '신메뉴' 1회는 마케팅 문구 | 빌더형 1페이지 |
| 3 | 커피무카24 | 25 |  | ⬜ | WebSearch 1회 무소득, mooka24.com/coffeemooka.com NXDOMAIN | 도메인 못 찾음 |
| 4 | 소미담 | 25 | https://somidam.com/80 (아임웹, 떡카페) | ⛔ | 공지 게시판 4쪽에 [신메뉴]/[신제품] 말머리 글+작성일: 1쪽 9건 중 [신메뉴] 7건(2026-03-17~2026-09-30), 2쪽 2025-10-28~2026-02-25, 4쪽 2024-10-16~17(일괄 등록). 최신 2026-09-30 '시그니처 크림라떼 5종' | **뒤집음 🟢→⛔**: 게시판 [신메뉴] 말머리+작성일은 실재하나 본문이 이미지 1장(3글 확인: 텍스트 0줄), 메뉴 4칸도 이름 텍스트 0. 최근 2글 제목이 `시그니처 크림라떼 5종`(N종)·`올가을, ‘감’이 제대로 잡았다!`(이름 없음) → 60일 창에서 뽑을 이름 0 |
| 5 | 고품격커피공장 | 24 |  | ⬜ | WebSearch 1회 무소득, 고품격커피공장.com NXDOMAIN | 도메인 못 찾음 |
| 6 | 뜰커피 | 24 |  | ⬜ | WebSearch 1회 무소득, ddeulcoffee.com·뜰커피.com NXDOMAIN | 도메인 못 찾음 |
| 7 | 스몰굿 | 24 |  | ⬜ | WebSearch: 매장 리뷰만(부산 기원). smallgood.co.kr 은 whoisdomain.kr/forward 프레임 469B(주차), smallgoodcoffee.com NXDOMAIN | 도메인 못 찾음 |
| 8 | 샬로우커피 | 24 |  | ⬜ | WebSearch: 울산 매장 리뷰만. shallowcoffee.com 은 'Virtual Coffee Dates'(무관 해외), .co.kr NXDOMAIN | 도메인 못 찾음 |
| 9 | 점프(JUMP) | 23 |  | ⬜ | WebSearch: 오송점 예약페이지만. jumpcoffee.com 200인데 114B 빈 껍데기(브랜드 확인 불가), jumpcoffee.co.kr NXDOMAIN | 도메인 못 찾음 |
| 10 | 미남커피(MINAM COFFEE) | 23 |  | ⬜ | WebSearch 무소득, minamcoffee.com/.co.kr·미남커피.com NXDOMAIN | 도메인 못 찾음 |
| 11 | 무무커피 | 22 | https://mumucoffee.co.kr | ⛔ | 아임웹. /notice 공지 최신 2023-11(본문 날짜 2023-11~2024-03), 신메뉴·출시 단어 0, 배지 요소 0. (mumucoffee.com 은 별개 'Mumu Coffee') | 공지 멈춤, 메뉴에 날짜·배지 없음 |
| 12 | 카페동네 | 22 |  | ⬜ | WebSearch 무소득(부천 개인매장만), cafedongne.com/카페동네.com NXDOMAIN | 도메인 못 찾음 |
| 13 | 카페CCD | 22 |  | ⬜ | WebSearch 무소득(인도 CCD만), cafeccd.com/.co.kr NXDOMAIN | 도메인 못 찾음 |
| 14 | 아이캔커피 | 21 | https://icancoffee.co.kr/newmenu | ⛔ | 아임웹 전용 /newmenu 칸에 상품 단위 캡션 8건(한손피자 4종 CDN 20260929 · 빙수 4종 CDN 20260813), 'NEW' 는 섹션 제목 텍스트(요소 아님). 교차축: 공지 /49 에 '20xx 신메뉴 출시' 글 23건(2025-11-20~2026-04-14)이나 피자·빙수 출시글은 없음 | **뒤집음 🟢→⛔**: `/newmenu` 캡션 8건의 날짜가 아임웹 CDN 뿐인데, 공지 「2026 요구르트시리즈 출시」(2026-04-14) 상품 코코요구르트 3종이 `/drinks` 에서 **CDN 20260929**(피자와 같은 날)를 달고 있다 = 5개월 뒤 재업로드. CDN 날짜가 출시일이 아님을 확인 |
| 15 | 플루800 | 21 |  | ⬜ | WebSearch 무소득, flu800.com/.co.kr·플루800.com NXDOMAIN | 도메인 못 찾음 |
| 16 | 매머드커피(Mammoth coffee) | 21 | (mmthcoffee.com, 프차몰) | 🟡 이미 등록 | base.BRANDS['매머드커피'] 존재 | skip |
| 17 | 아몽즈커피(A Mong Z) | 21 |  | ⬜ | WebSearch 무소득, amongzcoffee.com/amongz.co.kr NXDOMAIN | 도메인 못 찾음 |
| 18 | 어랏커피스탠드 | 21 | https://alotcoffee.com | ⛔ | addblock 빌더 원페이지(메뉴 'A LOT SIGNATURE'·'ALL NEW'·공지사항 전부 #앵커), sitemap 404, 날짜·배지 요소 0 | 빌더형 1페이지. (61위 A LOT TO GO 와 같은 회사로 추정) |
| 19 | 디디커피 | 21 |  | ⬜ | WebSearch 무소득. ⚠️didicoffee.com 은 http 200 이지만 title '365bet…' 도박 스팸(만료도메인 탈취), .co.kr NXDOMAIN | 도메인 못 찾음(didicoffee.com 은 브랜드 아님) |
| 20 | 커피왕 | 20 |  | ⬜ | WebSearch: 왜관점 알바몬만. coffeeking.co.kr http 469B whoisdomain 포워드 프레임(주차), 커피왕.com NXDOMAIN | 도메인 못 찾음 |
| 21 | 피에스타7커피 | 20 |  | ⬜ | WebSearch 무소득, fiesta7coffee.com/fiesta7.co.kr NXDOMAIN | 도메인 못 찾음 |
| 22 | 무인다방 | 20 |  | ⬜ | WebSearch 무소득(일반명사), 무인다방.com/muindabang.com NXDOMAIN | 도메인 못 찾음 |
| 23 | 왓커피 | 20 |  | ⬜ | WebSearch 무소득, whatcoffee.co.kr/.kr NXDOMAIN | 도메인 못 찾음 |
| 24 | 오슬랑 | 20 |  | ⬜ | WebSearch 무소득, oslang.co.kr/오슬랑.com NXDOMAIN, oslang.com 403 '2026wordcup.com' 무관 | 도메인 못 찾음 |
| 25 | 그라츠커피랩(GRAZ COFFEE LAB) | 20 | https://grazcoffeelab.com/menu | ⛔ | 메뉴판 텍스트 29품목(가격만), 배지 요소·날짜 0, 소식 게시판 없음(링크 5개: 소개/메뉴/카페/제품/가맹) | 신상 구분 수단 없음 |
| 26 | 카페달링 | 20 | https://cafedarling.com | ⛔ | 그누보드. bo_table=news 글 1건이 'test 25.04.04'(더미), beverage 게시판 배지·날짜 0. 본문 '신메뉴' 3회는 메인 문구 | 소식 게시판 사실상 빈 더미 |
| 27 | 소디스 | 19 | https://sodiscoffee.com | ⛔ | 소디스커피&에스프레소바. /notice/ 최신 2024-01(1건), /menu/ 배지·날짜 0. (sodis.co.kr 은 'This store is unavailable' 무관) | 공지 멈춤 |
| 28 | 화채업자 | 19 | https://화채업자.com (xn--5h5bw6af5gnsm.com) | ⛔ | 창업 모객 원페이지(내부링크 전부 #앵커), 화채·빙수 메뉴 나열뿐 | 빌더형 1페이지 |
| 29 | 커피스토어 | 19 | http://커피스토어.com (xn--9t4b29ctzlbyc75f.com, https 자체서명 인증서) | ⛔ | 창업 모객 원페이지(/#con02 등 앵커), 신메뉴 단어 0 | 빌더형 1페이지 |
| 30 | 이공커피 | 18 |  | ⬜ | WebSearch 무소득, egongcoffee.com/20coffee.co.kr/이공커피.com NXDOMAIN | 도메인 못 찾음 |
| 31 | 블레스롤(Bless Roll) | 18 | https://blessroll.com | ⛔ | 아임웹. '새로운 메뉴'(/30)·'Bless News'(/23) 칸 본문 텍스트가 사실상 없음(667·724자, 네비·푸터뿐 — 이미지 포스터만), 날짜 0. CDN 202608/202609 각 4장(교차축 없음) | 포스터만, 상품명 텍스트 없음 |
| 32 | Every Coffee(에브리커피) | 18 | https://www.everycoffee.co.kr | ⛔ | 아임웹 창업 모객 페이지(리브랜딩·월매출 홍보), 내부 링크 6개(페이지네이션뿐), 신메뉴 단어 0 | 빌더형 1페이지 |
| 33 | 봄바스타커피 | 18 |  | ⬜ | WebSearch 무소득, bombastacoffee.com/bombasta.co.kr NXDOMAIN | 도메인 못 찾음 |
| 34 | 커피101스트릿(COFFEE 101 STREET) | 18 |  | ⬜ | WebSearch 무소득. coffee101street.com 200 이지만 'This store is unavailable'(1,516B, Shopify 폐점 껍데기 — 브랜드 확인 불가) | 도메인 못 찾음 |
| 35 | 조선다방 | 18 |  | ⬜ | WebSearch 무소득, chosundabang.com/joseondabang.com/조선다방.com NXDOMAIN | 도메인 못 찾음 |
| 36 | 아마떼 | 17 |  | ⬜ | WebSearch: 2012·2015 기사뿐. amate.co.kr 은 가비아 '사이트 준비 중' 주차(1,154B), cafeamate.com/.co.kr NXDOMAIN | 도메인 못 찾음 |
| 37 | 비엔나커피하우스 | 17 | https://viennacoffeehouse.co.kr/notice | ✅ | 공지 게시판 1쪽 8건 전부 출시 안내(상품명이 「」 안에 텍스트로, 작성일 'YYYY년 MM월 DD일'): 2026-01-07 비엔나 베리노 ~ 2026-09-09 솔티카라멜 팝 아이스크림. 출시글 8/8(100%), 3쪽까지 있음. 배지 요소 없음(게시판형) | **어댑터 제작** — `collectors/cafe_vienna.py` (§2-1, 886c9491 배선) |
| 38 | 이륜당 | 17 |  | ⬜ | WebSearch 무소득(바이크카페 무관 결과), iryundang.com/이륜당.com NXDOMAIN | 도메인 못 찾음 |
| 39 | 커피기업 | 16 |  | ⬜ | WebSearch 무소득(일반명사), coffeegiup.com/커피기업.com NXDOMAIN | 도메인 못 찾음 |
| 40 | 또리커피 | 16 |  | ⬜ | WebSearch 무소득, ddoricoffee.com/ttoricoffee.com NXDOMAIN | 도메인 못 찾음 |
| 41 | 카페코지 | 16 |  | ⬜ | WebSearch 무소득. cafecozy.com→cafecozy.dk(덴마크 식당, 무관), cafecozy.co.kr NXDOMAIN | 도메인 못 찾음 |
| 42 | 요거 피플 | 16 |  | ⬜ | WebSearch 무소득, yogurpeople.com/yogerpeople.com NXDOMAIN | 도메인 못 찾음 |
| 43 | 아리스타 | 16 | http://aristacoffee.co.kr (https 인증서 호스트 불일치) | ⛔ | 앱스토어 앱 소개에 공식 홈페이지로 기재. 공지(iBrdNo=3) 최신 2019-11, 신메뉴 글은 2018~2019뿐 | 게시판 멈춤(2019) |
| 44 | 모캄보 | 16 | https://mokambo.co.kr/52 | ⛔ | 아임웹 CAFFE MOKAMBO. '신메뉴' 칸(/52) 본문에 상품명 텍스트 없음(포스터 이미지), CDN 최신 202412, 교차축 없음 | 포스터만·멈춤 |
| 45 | 킹프레소 | 16 | https://kingpresso.co.kr/menu.php | ⛔ | 킹프레소 와플. menu.php 배지 요소·날짜 0, 게시판 링크 없음(내부 링크 5개). kingpresso.com 은 114B 빈 껍데기 | 신상 구분 수단 없음 |
| 46 | 남영댁 커피24 | 16 |  | ⬜ | WebSearch 무소득, 남영댁.com/namyoungdaek.com NXDOMAIN | 도메인 못 찾음 |
| 47 | 스윗앤샷 | 16 |  | ⬜ | WebSearch 무소득, sweetnshot.com/sweetandshot.co.kr NXDOMAIN | 도메인 못 찾음 |
| 48 | 요거팡 YogurPang | 15 | http://yogurpang.com (https TLS 오류) | ⛔ | 그누보드 창업 모객형('0원창업'), /bbs/new.php '게시물이 없습니다' | 게시판 비어 있음 |
| 49 | 커피홀(coffee hole) | 15 | https://coffeehole.co.kr/sub02/sub01.php | ⛔ | '신메뉴' 면은 포스터 16장(2024bingsu·2025딸기_포스터 등 파일명, 상품명 텍스트 없음·1~2년치). 언론보도(bo_table=news, 14쪽) 제목에 상품명 있으나 목록에 날짜 없고 최신 글(wr_id=225) 본문 날짜 24-04-12 | 포스터 아카이브 + 보도자료 2024-04 멈춤 |
| 50 | 아토커피 | 15 |  | ⬜ | WebSearch 무소득. atocoffee.com 은 'Launching Soon' 빈 페이지(브랜드 확인 불가), .co.kr NXDOMAIN | 도메인 못 찾음 |
| 51 | 카페보니또 | 15 | https://www.espressokorea.com (프차몰 링크) | ⛔ | 링크된 곳은 모회사 에스프레소코리아 B2B 사이트(생두수입·OEM·원두 제품), 카페보니또 메뉴·소식 면 없음, 게시판 링크 0 | 브랜드 매장 메뉴 면 없음 |
| 52 | 아틀리에빈 | 15 |  | ⬜ | WebSearch: 경산 옥산점 트립닷컴만. atelierbean.com/.co.kr·ateliervin.com NXDOMAIN | 도메인 못 찾음 |
| 53 | 펠어커피초코 | 15 | https://fellacoffeechoco.com/NOTICE | ⛔ | NOTICE 게시판은 HTTP 404 상태로 본문을 줌(60건). 내용이 점주용 공지(사업자서류·공동구매·쇼핑백 발주), [신메뉴] 글은 2026-02-20 1건, 최신 글 2026-02-28 이후 없음 | 점주 공지·7개월 멈춤 |
| 54 | 하이테이블 | 15 |  | ⬜ | WebSearch: 동암점·구래점(24시) 매장 페이지만. hightablecoffee.com 은 'The High Table' 영문 사이트(미국 추정, 무관), hightable.co.kr NXDOMAIN | 도메인 못 찾음 |
| 55 | 베스트빈 | 14 |  | ⬜ | WebSearch 무소득. bestbean.com 은 atom.com 도메인 매물, bestbean.co.kr NXDOMAIN | 도메인 못 찾음 |
| 56 | 커피브라더 | 14 |  | ⬜ | WebSearch 무소득. coffeebrother.co.kr → '웹호스팅 만료 안내'(webmaker21), coffeebrother.com 114B 빈 껍데기 | 도메인 못 찾음(유력 도메인 호스팅 만료) |
| 57 | 마린커피 | 14 |  | ⬜ | WebSearch: 삼척 커피마린협동조합만(별개). marinecoffee.co.kr 은 http 403(198B)·https 인증서 불일치라 브랜드 확인 불가 | 도메인 못 찾음 |
| 58 | 빈타이(BEAN TIE) | 14 | https://beantie.co.kr | ⛔ | 그누보드. NOTICE 게시판 글 최신 2018-07, 신메뉴 단어 0, 메뉴 배지 0 | 게시판 2018 멈춤 |
| 59 | 헤이키 커피 | 14 |  | ⬜ | WebSearch: 앱스토어 '헤이키커피 스마트주문' 앱만(홈페이지 미기재, 가맹문의 1533-3047). heykeycoffee.com/.co.kr·heykicoffee.com NXDOMAIN | 도메인 못 찾음 |
| 60 | 히즈빈스(HISBEANS) | 14 | https://www.hisbeans.com | ⛔ | 사회적기업 '향기내는사람들'. /notice 15건(2020-08~2025-10) 중 신메뉴·출시 0, 배지 요소 0 | 공지에 상품 글 없음 |
| 61 | A LOT TO GO(어랏투고) | 14 | (alotcoffee.com 추정) | ⛔ | alottogo.com/.co.kr NXDOMAIN. 18위 어랏커피스탠드 사이트(alotcoffee.com)가 같은 회사 브랜드로 보이며 그 사이트는 원페이지(#앵커)라 ⛔ | 자체 도메인 없음·모회사 원페이지 |
| 62 | 카페홈즈(Cafe Homes) | 14 | http://cafehomes.co.kr (https 자체서명) | ⛔ | 그누보드. co_id=news/menu 는 정적 content 페이지(날짜 0·신메뉴 0), /bbs/new.php 새글 0 | 게시판 비어 있음 |
| 63 | 카페그란데 | 13 |  | ⬜ | WebSearch 무소득. cafegrande.co.kr http 403(209B)·https 자체서명이라 브랜드 확인 불가 | 도메인 못 찾음 |
| 64 | 일리터맥스 | 13 |  | ⬜ | WebSearch 무소득(illy 결과만), 1litermax.com/.co.kr·ilitermax.com NXDOMAIN | 도메인 못 찾음 |
| 65 | 전광수커피 | 13 |  | ⬜ | WebSearch: 정동·분당 매장 리뷰만. jkscoffee.com 은 대만 '傑克森咖啡'(무관), jeonkwangsoo.com NXDOMAIN | 도메인 못 찾음 |
| 66 | COFFEE PUCK | 13 |  | ⬜ | WebSearch 무소득(Wolfgang Puck 등), coffeepuck.com/.co.kr NXDOMAIN | 도메인 못 찾음 |
| 67 | 와커피 (WA’ COFFEE) | 13 | https://wacoffee.co.kr/news | ⛔ | 소식 게시판 글 3건뿐(딸기 '겨울 시즌 메뉴 출시'·16호점 오픈·홈페이지 새단장), 목록·본문에 날짜 없음, 메뉴 배지 0. ©2023 | 게시판 사실상 정지·날짜 없음 |
| 68 | 커피온리 | 13 | https://www.coffeeonly.co.kr | ⛔ | 창업 모객 원페이지(내부 링크 2개). thevc.kr 기준 (주)커피온리 2025-12-31 폐업 표시 | 빌더형 1페이지·본사 폐업 추정 |
| 69 | THE BLUE COFFEE | 13 | https://thebluecoffee.co.kr | ⛔ | 아임웹. /Menu→/Coffee 배지 요소 0, 신메뉴·출시 0, CDN 202409 일괄(184장)·최신 202503. 소식 게시판 없음(_NEW 는 페이지명 접미사) | CDN 일괄 업로드뿐 |
| 70 | PLAN(플랜) | 13 |  | ⬜ | WebSearch: 플랜즈커피·플랜지스테이션 등 별개만. plancoffee.com 은 HugeDomains 매물, cafeplan.co.kr NXDOMAIN | 도메인 못 찾음 |
| 71 | 더드림커피 | 13 |  | ⬜ | WebSearch: 북부정류장점 예약페이지만. thedreamcoffee.com 114B 빈 껍데기, .co.kr/.kr NXDOMAIN | 도메인 못 찾음 |
| 72 | 콜프로스터스 | 13 |  | ⬜ | WebSearch 무소득, kolproasters/colproasters/callroasters.com NXDOMAIN | 도메인 못 찾음 |
| 73 | COFFEE ROMAN(커피로만) | 12 | https://coffeeroman.com | ⛔ | Cafe24. 공지(board_no=1) 최신 2024-06-21, NEWS(board_no=2) 글 날짜 0·신메뉴 0, 메뉴 배지 0 | 게시판 멈춤 |
| 74 | 그레이핍플커피 | 12 | https://graypipple.com | ⛔ | NEWS 6건 중 상품 출시는 2026-06-18 '컵빙수쉐이크 3종' 1건(묶음)뿐, 나머지는 창업박람회·매출 기사. 메뉴 NEW 탭(/menu/) 본문 비어 있음(JS) | 보도자료가 창업 위주·상품글 드묾 |
| 75 | 카페 우드진 | 12 | http://www.woodjean.com (WordPress, https 자체서명) | ⛔ | 공지사항 최신 2022-08-01, 메뉴 페이지(시그니처/커피/논커피) 배지·날짜 0 | 공지 2022 멈춤 |
| 76 | TOP LITER | 12 | https://topliter.com/info/menu.php | ⛔ | '신메뉴' 칸 5품목(식혜·미식혜·박사·박카리·수정과) 이미지 menu_new1~5.png 고정 파일명, 날짜 0. 공지 본문 305자(사실상 빈 게시판) | 날짜 없는 고정 칸 |
| 77 | PRESENT(프레전트) | 12 |  | ⬜ | WebSearch 무소득, presentcoffee.co.kr/cafepresent.co.kr NXDOMAIN | 도메인 못 찾음 |
| 78 | 국민우유집 | 11 |  | ⬜ | WebSearch: 서대문 본점·용인흥덕점 매장 페이지만. 국민우유집.com/kookminmilk.com NXDOMAIN | 도메인 못 찾음 |
| 79 | 욤카페 | 11 | https://yomcafe.co.kr | ⛔ | 아임웹 '샵인샵 창업 초기자금 0원' 창업 랜딩(내부 링크 6개), CDN 202506 일괄 559장, 신메뉴 0 | 빌더형 1페이지 |
| 80 | 프롬하츠(FROM HEARTS) | 11 | https://www.fromheartscoffee.com/NewMenu | ⛔ | 아임웹 '신메뉴' 칸 본문에 상품명 텍스트 없음(네비뿐 812자 — 포스터 이미지), CDN 202303~202604 혼재. 다른 게시판은 점주용(/Notice_storemanager) | 포스터만 |
| 81 | 이십센치 | 11 | http://www.20cm.co.kr (커피이십센치) | ⛔ | 아임웹. /NOTICE→/team 공지 본문 783자, 신메뉴·출시 0, CDN 최신 202406 | 게시판 멈춤·신상 신호 없음 |
| 82 | P휴게소입니다 | 11 |  | ⬜ | WebSearch 무소득(고속도로 휴게소 일반 결과), p휴게소.com/phugeso.com NXDOMAIN | 도메인 못 찾음 |
| 83 | 엑스엑스 커피메이커 | 11 |  | ⬜ | WebSearch 무소득(OXX·Xpresso Delight 등 해외), xxcoffeemaker.com/.co.kr·xxcoffee.co.kr NXDOMAIN | 도메인 못 찾음 |
| 84 | 위너스커피 | 11 |  | ⬜ | WebSearch: 당근 업체 페이지만(창업상담 1599-8756). winnerscoffee.com 은 HugeDomains 매물, .co.kr/.kr NXDOMAIN | 도메인 못 찾음 |
| 85 | 옐로우캔 | 11 | https://yellowcan.co.kr/home/c/News | ⛔ | 새소식 게시판 글이 전부 가맹점 오픈·계약체결(2025-05~2026-10-10), 메뉴 배지 0 | 게시판=가맹 오픈 소식뿐 |
| 86 | 오크레페(OH!CREPE) | 11 | http://ohcrepe.co.kr (https TLS 오류) | ⛔ | 그누보드 크레페 전문점. 메인 badge 클래스는 창업 프로모션 장식, menu.php 배지·날짜 0, /bbs/new.php 새글 0. '신메뉴'는 창업경쟁력 문구 | 게시판 비어 있음 |
| 87 | 테이큰커피 | 11 |  | ⬜ | WebSearch 무소득, takencoffee.com/.co.kr NXDOMAIN | 도메인 못 찾음 |
| 88 | 커피나무 | 11 |  | ⬜ | WebSearch: 서래마을점 기사만. coffeenamu.com 은 EggDomain 매물, coffeenamu.co.kr NXDOMAIN | 도메인 못 찾음 |
| 89 | 사운즈커피미니(SOUNDSCOFFEE mini) | 10 |  | ⬜ | WebSearch: 대구 매장 리뷰만. soundscoffee.com 은 가비아 '홈페이지 준비중' 주차(2,730B), soundscoffee.co.kr 은 네이버 스마트스토어 로그인으로 리다이렉트 | 도메인 못 찾음(135위 사운즈커피와 공통) |
| 90 | 라떼떼 | 10 |  | ⬜·확정아님 | WebSearch 예산 소진(세션 200회 한도)으로 미실시; lattete.com/.co.kr·라떼떼.com NXDOMAIN | 도메인 못 찾음 |
| 91 | 에센스커피 | 10 |  | ⬜ | WebSearch 무소득. essencecoffee.com 은 HugeDomains 매물, essencecoffee.co.kr 은 인증서 만료(http 도 https 로 튕김) | 도메인 못 찾음 |
| 92 | 손커피연구소 | 10 |  | ⬜·확정아님 | WebSearch 예산 소진(세션 200회 한도)으로 미실시; soncoffeelab.com/soncoffee.co.kr NXDOMAIN | 도메인 못 찾음 |
| 93 | #힘이나는커피생활 | 10 |  | ⬜ | WebSearch: 무교점 리뷰만. himnaneun.com/힘이나는커피생활.com NXDOMAIN | 도메인 못 찾음 |
| 94 | 라떼킹(Latteking) | 10 | https://latteking.co.kr/news | ⛔ | 아임웹. NEWS 게시판(전체/이벤트/신메뉴/보도자료 카테고리) 목록에 날짜 없음, 제목이 기사형('라떼킹, 성수LAB에서 크로와상과 크루키 단독 출시…'). CDN 최신 202606, 교차축 없음 | 재확인(10-14): NEWS 는 아임웹 게시판(카테고리 공지·보도자료·카사노바)인데 글 대부분이 **창업 마케팅**(「카페 창업 망하는 이유」 등)이고 상품 글은 「라떼킹, 성수LAB에서 크로와상과 크루키 단독 출시」 1건(상세 날짜 2026-05-15)뿐 — 이름이 문장 속이라 못 뽑는다 |
| 95 | 몬도커피츄러스 | 10 |  | ⬜·확정아님 | WebSearch 예산 소진(세션 200회 한도)으로 미실시; mondocoffee.co.kr/mondochurros.com NXDOMAIN | 도메인 못 찾음 |
| 96 | 진심커피 | 10 | http://jinsimcoffee.com (https 자체서명) | ⛔ | 그누보드. /bbs/new.php 새글 0, bo_table=season 배지·날짜 0, 메뉴 게시판 배지 0 | 게시판 비어 있음 |
| 97 | 슈퍼커피 | 10 |  | ⬜·확정아님 | WebSearch 예산 소진(세션 200회 한도)으로 미실시; supercoffee.co.kr NXDOMAIN | 도메인 못 찾음 |
| 98 | 커피다스1리터 | 10 |  | ⬜·확정아님 | WebSearch 예산 소진(세션 200회 한도)으로 미실시; coffeedas.com/.co.kr NXDOMAIN | 도메인 못 찾음 |
| 99 | OPPA COFFEE(오피피에이 커피) | 10 |  | ⬜·확정아님 | WebSearch 예산 소진(세션 200회 한도)으로 미실시; oppacoffee.com/.co.kr NXDOMAIN | 도메인 못 찾음 |
| 100 | 떼루와 | 10 |  | ⬜·확정아님 | WebSearch 예산 소진(세션 200회 한도)으로 미실시; 떼루와.com NXDOMAIN, terroir.co.kr 은 '제주로부터'(무관) | 도메인 못 찾음 |
| 101 | 킨크커피 | 10 |  | ⬜·확정아님 | WebSearch 예산 소진(세션 200회 한도)으로 미실시; kinkcoffee.com 은 HugeDomains 매물, .co.kr NXDOMAIN | 도메인 못 찾음 |
| 102 | 폴러스타커피 | 10 |  | ⬜·확정아님 | WebSearch 예산 소진(세션 200회 한도)으로 미실시; polestarcoffee.co.kr NXDOMAIN, polarstarcoffee.com 은 'Porlar Star Coffee' 해외 커피용품 Shopify(무관) | 도메인 못 찾음 |
| 103 | 꿀스커피GGUL'S COFFEE | 10 | http://ggulscoffee.com (https 인증서 불일치) | ⛔ | 그누보드. 공지 최신 2021-03, 메뉴(tl_product_new) 배지 요소 0·날짜 0 | 공지 2021 멈춤 |
| 104 | 헬리빈커피(HELIBEAN COFFEE) | 9 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; helibean.com/.co.kr·helibeancoffee.com NXDOMAIN | 도메인 못 찾음 |
| 105 | 1L 커피특별시 | 9 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; 1lcoffee.co.kr NXDOMAIN | 도메인 못 찾음 |
| 106 | 투달러커피(2Dollars Coffee) | 9 | https://2dollarscoffee.com | ⛔ | 그누보드 기반 창업 모객 원페이지('더 싸게 더 맛있게 더 잘 되게'), 내부 링크 2개(회원가입·비번찾기) | 빌더형 1페이지 |
| 107 | 부바스 | 9 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; buvas.co.kr/bubas.co.kr NXDOMAIN | 도메인 못 찾음 |
| 108 | 카페 꽃이피다 | 9 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; 카페꽃이피다.com NXDOMAIN | 도메인 못 찾음 |
| 109 | 아덴블랑제리 시그니쳐 | 9 | http://aden-cafe.com (https 자체서명) | ⛔ | 74위 아덴블랑제리와 같은 사이트. /bbs/new.php 새글 날짜 0(사실상 빈 게시판), 지난번 실측: bo_table=menu 583자·notice 435자 | 게시판 비어 있음 |
| 110 | 보니또 | 9 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; bonito.co.kr 은 '경주 보니또펜션'(무관). (프차몰 finfo 는 카페보니또 슬러그로 오매칭) | 도메인 못 찾음 |
| 111 | EVZZUCKER COFFEE | 9 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; evzzucker.com/.co.kr NXDOMAIN | 도메인 못 찾음 |
| 112 | 히얼이즈커피 | 9 | https://hereiscoffee.com | ⛔ | 메뉴(/product/list) 배지·날짜 0, 게시판 링크 없음. '시즌 신메뉴'는 팝업 문구 | 신상 구분 수단 없음 |
| 113 | 페이브커피 | 9 | favecoffee.co.kr (추정) | ⚠️ 접속 불가 | WebSearch 예산 소진으로 미실시. http 89B 가 https://favecoffee.co.kr 로 JS 리다이렉트, https 는 인증서 체인 오류(unable to get local issuer) — 브랜드 사이트인지도 확인 불가. favecoffee.com 은 buydomains 매물 | 인증서 오류 |
| 114 | 바리스텔라 | 9 | (프차몰 링크 = caffebene.co.kr) | ⚠️ 접속 불가 | 프차몰이 카페베네 도메인을 링크(카페베네 계열 추정, '카페베네'는 BRANDS 등록). caffebene.co.kr·baristella.co.kr 둘 다 ConnectTimeout | 타임아웃 — 카페베네 계열이면 기존 어댑터 쪽에서 확인 |
| 115 | 카페마타마타 | 9 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; matamata.co.kr/cafematamata.com NXDOMAIN | 도메인 못 찾음 |
| 116 | 카페락온 | 9 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; rockon.co.kr 은 hosting.kr 'Coming Soon' 주차(2026-10-14 등록), cafelockon.com NXDOMAIN | 도메인 못 찾음 |
| 117 | 투빅커피(TOOBIG COFFEE) | 9 | https://toobigcoffee.com | ⛔ | 아임웹. NOTICE 본문 703자·날짜 2023-07~08 뿐, CDN 최신 202308, 배지 0 | 2023 멈춤 |
| 118 | 픽셀커피 | 9 | https://pixelcoffee.co.kr | ⛔ | 아임웹. 날짜는 매장 등록일뿐(/shop, 2024-07~2026-09), 메뉴(/drink) 배지·날짜 0, 소식 게시판 없음 | 신상 구분 수단 없음 |
| 119 | 배달의카페 | 8 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; baedalcafe.co.kr NXDOMAIN | 도메인 못 찾음 |
| 120 | 별난커피 | 8 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; byulnancoffee.com/별난커피.com NXDOMAIN | 도메인 못 찾음 |
| 121 | 디저트 참 잘하는 집 | 8 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; dessertcham.co.kr NXDOMAIN | 도메인 못 찾음 |
| 122 | 몰타 | 8 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; maltacafe.co.kr NXDOMAIN | 도메인 못 찾음 |
| 123 | 밀크컨셉 | 8 | https://milkconcept.co.kr | ⛔ | 아임웹. 메뉴(/fullmenu·/signaturemenu)뿐, 소식 게시판 없음, 신메뉴·출시 0, 배지 요소 0(아임웹 공통 클래스만). CDN 202604~202608 교차축 없음 | 신상 구분 수단 없음 |
| 124 | 셀프 바리스타 | 8 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; selfbarista.co.kr NXDOMAIN, selfbarista.com 은 튀르키예 'Self Kahve' 유통사(무관) | 도메인 못 찾음 |
| 125 | 루고 | 8 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; rugo.co.kr 은 스키·스노보드 쇼핑몰(무관), cafelugo.com NXDOMAIN | 도메인 못 찾음 |
| 126 | 빈스빈스 | 8 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; beansbeans.com 114B 빈 껍데기, .co.kr NXDOMAIN | 도메인 못 찾음 |
| 127 | 라스베이글 | 8 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; lasbagel.com/.co.kr NXDOMAIN | 도메인 못 찾음 |
| 128 | 파운드커피 | 8 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; poundcoffee.com 은 영문 제휴 리뷰 블로그(무관), .co.kr NXDOMAIN | 도메인 못 찾음 |
| 129 | 카페리빈 | 8 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; caferebean.co.kr/cafelibean.com NXDOMAIN | 도메인 못 찾음 |
| 130 | 히든오아시스(HIDDENOASIS) | 7 | https://www.hiddenoasis.co.kr | ⛔ | 창업 모객 사이트('좋은 말보다, 판단할 근거'), 내부 링크 9개(브랜드·창업·가맹·메뉴), 게시판 없음, 신메뉴 0 | 창업 모객 |
| 131 | HayCOFFEE | 7 | http://www.haycoffee.co.kr (https 인증서 불일치) | ⛔ | 해이커피. 공지(/bbs/rwdboard) 본문 672자·날짜 0, 메뉴(/myboard/menu_list4) 배지·날짜 0 | 신상 구분 수단 없음 |
| 132 | 바리스트로 | 7 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; baristro.co.kr NXDOMAIN, baristro.com 은 Cloudflare 'DNS resolution error'(409) | 도메인 못 찾음 |
| 133 | 트러스트 스페셜티 커피 | 7 | http://trustcoffee.co.kr/default/ (https 인증서 불일치) | ⛔ | 루트 543B meta refresh 껍데기→/default/ (TRUST COFFEE). 제품 sub01~04 페이지뿐, 게시판·날짜·신메뉴 0 | 신상 구분 수단 없음 |
| 134 | 스트렝스커피 | 7 | https://strengthcoffee.co.kr | ⛔ | WordPress+KBoard. 공지 RSS pubDate 전부 2022-12-21(8건 일괄), 신메뉴 0 | 2022 멈춤 |
| 135 | 사운즈커피(SOUNDS COFFEE) | 7 |  | ⬜ | 89위 사운즈커피미니와 동일: soundscoffee.com 가비아 주차, soundscoffee.co.kr 네이버 스마트스토어 로그인 리다이렉트 | 도메인 못 찾음 |
| 136 | 카페율하온 | 7 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; yulhaon.com/율하온.com NXDOMAIN | 도메인 못 찾음 |
| 137 | 루머팡 | 7 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; rumorpang.com/루머팡.com NXDOMAIN | 도메인 못 찾음 |
| 138 | 토리스타특별한커피 | 7 | http://toristar.co.kr (https 자체서명) | ⛔ | 그누보드 bo_table=newmenu(신메뉴안내) 6건 있으나 작성일 전부 2020-02-05(일괄, 흑당라떼·한방쌍화차 등) — 이후 0건 | 신메뉴 게시판 2020 멈춤 |
| 139 | 고바슨 | 7 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; gobasun.com/.co.kr NXDOMAIN | 도메인 못 찾음 |
| 140 | 올선데이 | 7 | http://allsunday.co.kr (https TLS 오류) | ⛔ | 그누보드 베이글 카페. notice 목록 날짜 0·신메뉴 0, bo_table=menu 카테고리(Bagel/Coffee…) 배지 0 | 신상 구분 수단 없음 |
| 141 | SPACE COFFEE(스페이스커피) | 7 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; spacecoffee.co.kr NXDOMAIN | 도메인 못 찾음 |
| 142 | 스트릿캔 | 7 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; streetcan.co.kr NXDOMAIN, streetcan.com 은 무관 사이트로 리다이렉트(봇 체크) | 도메인 못 찾음 |
| 143 | 템포커피(tempo coffee) | 6 | http://tempocoffee.co.kr/web/main/mainPage.do (https 거부) | ✅ | eGov 게시판 NEWS(bbsId=…191) 6건 중 신메뉴 2건, 제목에 상품명 텍스트+작성일: 2026-05-14 '여름신메뉴 (진미숫가루라떼, 겐마이현미 녹차)출시'·2026-05-14 '(블루베리 셔벗 에이드, 블루베리 셔벗 라떼)'. 나머지 4건은 매장 오픈(2024-10~2025-05). 배지 요소 0 | **어댑터 제작** — `collectors/cafe_tempo.py` (§2-1b). NEWS 제목 괄호 안 상품명+글 날짜, ALLOW_EMPTY 게시판형 |
| 144 | PRABEAN(프라빈) | 6 | http://prabean.com (https 자체서명) | ⛔ | 공지(board_Bkse24) 최신 2020-05, 이벤트 게시판 본문 750자, 신메뉴 0 | 공지 2020 멈춤 |
| 145 | 그녀의 커피잔 | 6 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; 그녀의커피잔.com NXDOMAIN | 도메인 못 찾음 |
| 146 | 카페유어프레즌트 | 6 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; cafeyourpresent.com NXDOMAIN | 도메인 못 찾음 |
| 147 | 레인커피(RAIN COFFEE) | 6 | (프차몰 링크 = www.glowseoul.co.kr) | 🔴 도메인 오인·확정아님 | 프차몰 링크가 인테리어·브랜딩 디자인 회사 GLOW SEOUL 사이트(브랜드 사이트 아님). raincoffee.co.kr NXDOMAIN, WebSearch 예산 소진으로 미실시 | 공식 도메인 없음 |
| 148 | 빡벳(VAC VIET) | 6 | https://www.vacviet.com | ⚠️ 접속 불가 | 200 이지만 'Site is undergoing maintenance'(5,319B) 점검 페이지. 브랜드 사이트인지 확인 불가 | 점검 중 |
| 149 | 옵션스페셜티커피 | 6 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; optionspecialty.com/optioncoffee.co.kr NXDOMAIN | 도메인 못 찾음 |
| 150 | 우주곰커피 | 6 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; woojugom.com/woojugomcoffee.com NXDOMAIN | 도메인 못 찾음 |
| 151 | 이수페 | 6 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; isupe.co.kr NXDOMAIN | 도메인 못 찾음 |
| 152 | 킹사이즈커피 | 6 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; kingsizecoffee.com/.co.kr NXDOMAIN | 도메인 못 찾음 |
| 153 | ALI★KENYA★STAR(알리케냐스타)커피 | 6 |  | ⬜·확정아님 | 프차몰 링크는 공정위 정보공개서 뷰어뿐(홈페이지 아님). alikenyastar.com NXDOMAIN, WebSearch 예산 소진으로 미실시 | 도메인 못 찾음 |
| 154 | 더플롯커피(THE PLOT COFFEE) | 6 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; theplotcoffee.com/.co.kr NXDOMAIN | 도메인 못 찾음 |
| 155 | 지니프레쉬 | 6 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; geniefresh.co.kr NXDOMAIN | 도메인 못 찾음 |
| 156 | 리터킹 | 6 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; literking.com/.co.kr NXDOMAIN | 도메인 못 찾음 |
| 157 | 롤스커피 | 6 | http://rollscoffee.co.kr (https 연결 리셋) | ⛔ | 본문 469자 창업 모객형(인사말·인테리어·오픈현황·창업상담), 내부 링크 2개, 게시판·날짜 0. (rollscoffee.com 은 스페인어 'Inicio' 무관) | 빌더형 1페이지 |
| 158 | 셀렉커피랩(SELECT) | 5 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; selectcoffeelab.com/selectcoffee.co.kr NXDOMAIN | 도메인 못 찾음 |
| 159 | 브루잉토트 | 5 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; brewingtote.com/.co.kr NXDOMAIN | 도메인 못 찾음 |
| 160 | STACKBEAN | 5 | http://stackbean.co.kr (https 자체서명) | ✅🟡 | 메뉴 'NEW / HEALTHY' 카테고리(ca_id=10) 26품목, 상품 이미지 경로 /product/data/item/<유닉스타임>/ 이 등록시각: 2025-05-14 ~ 2025-11-18(뱅쇼·샹그리아·고구마라떼·달밤라떼·밤구마 5종 2025-11-18). 대조군 일반 카테고리(2010/3020/4010)는 2022-05~2024-07 → 날짜 축이 실제로 갈림 | **어댑터 제작(배선 보류 권고)** — `collectors/cafe_stackbean.py` (§2-1c). 상품 번호(=등록 유닉스 시각)를 상품별 날짜로. 시즌 메뉴를 NEW 칸으로 재등록하면 못 막는다 |
| 161 | 커피라빈트 | 5 | https://coffeelabint.com (추정, title 'coffeelanbint') | ⛔ | WebSearch 예산 소진. 유력 도메인은 Cafe24 원두·커피용품 쇼핑몰(싱글오리진·드립필터·구독), 매장 메뉴 면 없음, 신메뉴 0. 브랜드명과 철자 일치 여부 미확정 | 원두 쇼핑몰 — 매장 메뉴 면 없음 |
| 162 | 더노벰버 라운지 | 5 | https://www.thenovemberlounge.com | ⛔ | 인천 24시 커피. /board 본문 769자·날짜 0, 신메뉴 0 | 신상 구분 수단 없음 |
| 163 | INEAT(인잇) | 5 | https://www.lighnm.kr (프차몰 링크) | ⛔ | 링크는 모회사 LIG홈앤밀 기업 사이트. /news 언론보도는 서포터즈·업무협약(2025-03~12), 인잇 메뉴·신상 언급 0 | 기업 사이트·상품 소식 없음 |
| 164 | 지티(GT)커피 | 5 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; gtcoffee.co.kr NXDOMAIN, gtcoffee.com 은 싱가포르 Group Therapy Coffee(무관) | 도메인 못 찾음 |
| 165 | 달꽃다방 | 5 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; dalkkotdabang.com/달꽃다방.com NXDOMAIN | 도메인 못 찾음 |
| 166 | 빅웨이브(BIG WAVE) | 5 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; bigwavecoffee.co.kr NXDOMAIN, bigwave.co.kr ConnectTimeout(브랜드 여부 미확인) | 도메인 못 찾음 |
| 167 | COFFLIX(커플릭스) | 5 | cofflix.com (추정) | ⚠️ 접속 불가 | WebSearch 예산 소진으로 미실시; cofflix.com https 자체서명 인증서, http 도 https 로 튕겨 같은 오류 — 브랜드 사이트 여부 확인 불가. cofflix.co.kr NXDOMAIN | 인증서 오류 |
| 168 | 제이엠티(JMT) | 5 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; jmtcoffee.co.kr NXDOMAIN | 도메인 못 찾음 |
| 169 | 밀화당 | 5 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; milhwadang.com/밀화당.com NXDOMAIN | 도메인 못 찾음 |
| 170 | 우아한과일 | 5 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; woohanfruit.com/우아한과일.com NXDOMAIN | 도메인 못 찾음 |
| 171 | 커피코트 | 5 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; coffeecourt.co.kr/coffeecoat.co.kr NXDOMAIN | 도메인 못 찾음 |
| 172 | 지브릭커피(G,BRICK COFFEE) | 5 | https://www.fobee.co.kr/#gbrick (프차몰 링크 fobee.co.kr) | ⛔ | 링크된 곳은 공간디자인 회사 DesignFOBEE 사이트, GBRICK Coffee 는 그 안의 #앵커 섹션 하나(가맹상담 유도). 메뉴·소식 면 없음 | 모회사 원페이지 섹션 |
| 173 | 옐로우팜(YELLOW FARM) | 5 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; yellowfarm.co.kr/.kr NXDOMAIN | 도메인 못 찾음 |
| 174 | 스윗디저트카페루시카토 | 5 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; lucicato.co.kr/cafelucicato.com NXDOMAIN | 도메인 못 찾음 |
| 175 | 달다구니(DALDAGUNI) | 5 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; daldaguni.co.kr NXDOMAIN, daldaguni.com 은 budmin.net(디자인 에이전시)로 리다이렉트 — 무관 | 도메인 못 찾음 |
| 176 | 피카커피 | 5 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; fikacoffee.co.kr/.kr 은 whoisdomain 포워드 프레임 469B(주차) | 도메인 못 찾음 |
| 177 | 아이에떼커피 | 5 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; ieteecoffee.com NXDOMAIN | 도메인 못 찾음 |
| 178 | 파머스빈 | 5 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; farmersbean.com 은 HugeDomains 매물, .co.kr NXDOMAIN | 도메인 못 찾음 |
| 179 | 데일리에스프레소(Daily espresso) | 5 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; dailyespresso.co.kr/.kr NXDOMAIN | 도메인 못 찾음 |
| 180 | 컬러인커피 | 5 | https://colorincoffee.com | ⛔ | Cafe24 원두·티 쇼핑몰 겸 브랜드 사이트. NOTICE(board_no=1) 최신 2019-04, 신메뉴 0, 상품 배지 0 | 공지 2019 멈춤·쇼핑몰 |
| 181 | 코페아커피(COFFEA COFFEE) | 5 | https://www.coffea.co.kr (프차몰 링크) | ⛔ | 로스팅 전문 기업 사이트. /menu 본문 402자(이미지 메뉴판), 게시판·날짜·신메뉴 0 | 신상 구분 수단 없음 |
| 182 | 더원커피 | 5 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시; theonecoffee.co.kr NXDOMAIN, theonecoffee.com 114B 빈 껍데기 | 도메인 못 찾음 |
| 183 | CAFE CANBUS(카페캔버스) | 36 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시. 프차몰 링크 없음, 법인명 ㈜명진푸드(프차몰). cafecanbus.co.kr·canbus.co.kr·cafecanvas.co.kr·myungjinfood.co.kr NXDOMAIN | 도메인 못 찾음(재시도) |
| 184 | 스트릿 1988 | 31 | https://street1988.com | ⛔ | 법인 키스톤에프앤비. 붕어빵·호두과자·계란빵 간식 브랜드(커피 부속). '스트릿소식'(sub06_01) 본문 685자·날짜 2022-11 뿐, 메뉴 sub04_01~06 배지·날짜 0 | 소식 2022 멈춤 |
| 185 | 헤리턴스Cafe | 31 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시. 법인 (주)헤리턴스(무인카페, 구름라떼). heritance.co.kr·heritancecafe.com NXDOMAIN | 도메인 못 찾음(재시도) |
| 186 | 휴게소 | 30 |  | ⬜·확정아님 | WebSearch 예산 소진으로 미실시. 법인 (주)레스트아레아 → restarea.co.kr 은 봇 체크 403('Checking your browser', 5,768B)이라 브랜드 확인 불가(UA 위장 안 함). hugeso.co.kr 은 '두성유통'(무관). (82위 P휴게소입니다는 법인 '휴게소입니다'로 별개) | 도메인 못 찾음(유력 후보 봇 차단) |
| 187 | 달다곰이 | 25 | http://daldagomi.co.kr (https 인증서 불일치) | ⛔ | 법인 (주)달다곰이, 베이커리 카페('1,500종 베이커리'). 그누보드 f_notice·f_press·f_bread 등 게시판 정적 HTML 본문 499~575자로 목록 비어 있음(JS 렌더 추정), /bbs/new.php 새글 날짜 0. 달다곰이.com 은 http 403 | 게시판 정적 응답 비어 있음 — JS 렌더면 재확인 여지 |

### 2-3. 이번 구간에서 새로 확인한 함정

1. **WebSearch 는 소형 한국 카페 공식 도메인을 거의 못 준다** — 약 120회 중 1건(아리스타, 앱스토어 경유). 대신 **프차몰 상세의 '법인명'**
   (키스톤에프앤비·(주)달다곰이 등)으로 로마자 도메인을 짧게 추측하는 쪽이 맞았다.
2. **200 인데 브랜드가 아닌 곳** — 도박 스팸(`didicoffee.com`), 도메인 매물(HugeDomains·atom·EggDomain·buydomains), 가비아 '준비중',
   whoisdomain 포워드 프레임 469B, 해외 동명 업체(The High Table·대만 jkscoffee·싱가포르 gtcoffee), 업종 무관(스노보드몰·펜션).
3. **프차몰 링크가 모회사·제작사** — 에스프레소코리아·LIG홈앤밀·DesignFOBEE·GLOW SEOUL(레인커피 🔴).
4. **finfo 부분일치 오매칭** — `보니또` → `카페보니또`, `사운즈커피` → `사운즈커피미니`. 정확한 슬러그로 다시 봐야 한다.
5. **신메뉴 면이 포스터 아카이브** — 커피홀(`2024bingsu`·`2025딸기_포스터`), 탑리터(`menu_new1~5.png` 고정 파일명), 모캄보·프롬하츠·블레스롤(본문 텍스트 0).
   **멈춘 신메뉴 게시판** — 토리스타 6건 전부 2020-02-05 일괄, 스트렝스 RSS 전부 2022-12-21 일괄.
6. 30~109위 도메인 미확정 5곳: 스트릿1988(붕어빵)·달다곰이(베이커리)는 사이트를 찾아 ⛔, 카페캔버스·헤리턴스는 ⬜,
   휴게소는 유력 후보 `restarea.co.kr` 이 봇 체크 403(UA 위장 안 함)이라 ⬜.
