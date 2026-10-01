# 브랜드 후보 조사 — 피자 · 햄버거 · 패스트푸드

`docs/BRAND-CANDIDATES.md` · `docs/CANDIDATES-KOREAN.md` 와 같은 형식이다. **어댑터는 없다.** 조사 결과일 뿐이다.

- 조사일: **2026-09-30**
- 조사 대상: `docs/FRANCHISE-MASTER.md` 의 공정위 업종 **`피자`(I1) TOP29 + `패스트푸드`(G1) TOP30**, 그리고 TOP30 밖으로 밀린 **KFC**.
  총 **45개 브랜드**(중복 제외)에서 이미 수집 중·제외 확정된 브랜드를 뺀 전부.
- 조사 방법: 브랜드당 HTTP 5회 이내, 요청 간 2초 이상, `collectors/base.client()` (UA `sinsang-note/1.0`)
  - ⚠️ **맥도날드만 16회 썼다.** 허용치는 10회였다. Nuxt 번들이 `entry.*.js` 가 아니라 해시 이름 9개로 쪼개져 있어
    어느 게 엔트리인지 HTML 을 다시 안 받고는 알 수 없었고, 9개를 전부 받아 grep 하는 쪽을 택했다.
    초과분은 전부 정적 JS 번들이고, 결과적으로 **API 를 찾았다**(§2). 판단은 다음 사람이 해라.
- robots 는 전부 `urllib.robotparser.can_fetch("sinsang-note/1.0", …)` 으로 실측했다. **상태코드와 Content-Type 을 같이 봤다.**
- 추측으로 채운 칸은 없다. 못 본 것은 "확인 못 함"이라고 적었다.

이미 처리된 브랜드는 제외했다 — 수집 중(피자헛·미스터피자·파파존스·도미노피자·맘스터치·버거킹·프랭크버거),
제외 확정(롯데리아), 앞선 조사에서 불가(피자알볼로).
다른 에이전트가 맡은 치킨·족발보쌈·양식·중식·돈까스·초밥·베이커리·카페는 건드리지 않았다.

**공정위 업종 분류가 우리 카테고리와 어긋난다.** `패스트푸드` 업종에 피자 4종(맘스피자·비스트로피자·지정환피자·맘스터치 피자앤치킨)과
호떡 1종(점순이 호떡)이 들어 있다. 원본 업종 기준으로 전부 조사 범위에 넣었고, 표의 `업종` 칸에 공정위 원본을 그대로 실었다.

---

## 1. 전체 표

가맹점 수는 공정위 2025년도 정보공개서(2024년 말 기준). 업종은 공정위 원본 분류다.

### 1-1. 사이트를 확인한 브랜드

| 브랜드 | 가맹점수 | 업종 | URL | 수집 난이도 | 신제품 신호 | robots | 약관 | 비고 |
|---|---:|---|---|---|---|---|---|---|
| **맥도날드** | 55 | 패스트푸드 | `www.mcdonalds.co.kr/api/v1/kor/product/product/list` | **쉬움** | **`regDate` 실제 등록일 + `newIcon` 배지 필드** | 허용 (`Allow: /`, 200 text/plain) | **이용약관 페이지 자체가 없다** (개인정보처리방침만) | **내부 JSON API 찾음.** 카테고리 1회 + 카테고리당 1회. §2 |
| **피자스쿨** | 628 | 피자 | `pizzaschool.net/wp-json/wp/v2/portfolio` | **쉬움** | **`date`/`modified` 실제 등록일** | 허용 (`/wp-admin/` 만 Disallow) | 확인 못 함 (약관 페이지 없음) | **워드프레스 REST API 가 열려 있다.** 63건, 1요청. https 는 자체서명 인증서라 **http 만 동작** |
| **피자마루** | 498 | 피자 | `pizzamaru.co.kr/menu/10/` | **쉬움** | **신메뉴 전용 페이지 + "신제품순" 정렬** | 허용 (`/inday_fileinfo/`,`/admin_zone/` 제외) | ⚠️ **제9조 복제·상업적 이용 금지** | 완전 SSR. 상품명+설명+가격. 카테고리 10개 |
| **퀴즈노스서브** | 66 | 패스트푸드 | `quiznos.co.kr/menu/menu.php` | **쉬움** | **"New Menu 신메뉴" 섹션 (4건)** | 허용 (`Allow:/`) — ⚠️ https 자체서명, **http 만** | 회원약관에 스크래핑 금지 **없음** (멤버십·기프트카드 약관) | **1요청에 전체 메뉴 + 신메뉴 구분.** 이 조사 최고의 가성비 |
| **잇샌드** | 23 | 패스트푸드 | `itsand.co.kr/board/bbs/board.php?bo_table=menu` | **쉬움** | **신메뉴 카테고리 + 연번 내림차순(148→134…)** | ⚠️ **robots 자리에 HTML** | 확인 못 함 | gnuboard. 이삭토스트와 같은 연번 패턴. 10페이지 |
| **노브랜드버거** | 189 | 패스트푸드 | `shinsegaefood.com/nobrandburger/index.sf` | **쉬움** | 이미지 경로 업로드일만 (`uploaded_at`) | ⚠️ **404 (HTML 반환)** | 법적고지에 스크래핑 금지 **없음** (링크 사이트 면책만) | 앞선 조사 재확인. **홈 1요청 = 647KB / 렌더 43,505자**, 전체 메뉴 |
| **노모어피자** | 174 | 피자 | `nomorepizza.co.kr/menu` | 쉬움 | **없음** (뉴스에 "출시" 기사만) | 허용 (`/admin`,`/api/` 제외) | 확인 못 함 | Next.js SSR. 상품명+가격이 HTML 에 있다 |
| **난타5000피자** | 86 | 피자 | `nanta5000.co.kr/bbs/content.php?co_id=menu` | 쉬움 | **없음** | 허용 (`Allow: /`) | 확인 못 함 | gnuboard 단일 페이지. 1요청에 전체 메뉴 |
| **반올림피자** | 365 | 피자 | `order.banolimpizza.com/menu/list?categoryId=1` | 보통 | **신메뉴 카테고리 있음** | 허용 — ⚠️ **`/api/` Disallow** | 확인 못 함 | 주문 도메인으로 리다이렉트. SSR 은 카테고리+상품 일부만. **내부 API 는 robots 위반** |
| **피자에땅** | 138 | 피자 | `pizzaetang.com/etang/etang_menu.html` | 보통 | **없음** | 허용 (cafe24 표준 규칙) | cafe24 기본 전자상거래 약관, 스크래핑 조항 **없음** | cafe24 쇼핑몰. `/product/*` 표준 경로 존재 |
| **프레드피자** | 168 | 피자 | `fredpizza.co.kr/menu/pizza.php` | 보통 | **확인 못 함** | ⚠️ **robots 자리에 HTML** (피자알볼로와 같은 패턴) | 확인 못 함 | 상세정보(영양성분·원산지·알레르기)는 있는데 목록은 렌더 570자. ajax 의심 |
| **스테프핫도그** | 41 | 패스트푸드 | `steffhotdog.com/frcsteff/product/list/1` | 보통 | **"등록일순/등록일역순" 정렬 옵션** | ⚠️ **robots 자리에 HTML** | 확인 못 함 | 목록 자체는 렌더 489자 — 상품이 HTML 에 없다. 정렬 옵션만 확인 |
| **PC토랑** | 676 | 패스트푸드 | `pctorang.com/menu` | 보통 | **없음** | 허용 (아임웹 표준) | 확인 못 함 | 아임웹. 820KB 받아 렌더 1,671자지만 **상품명은 SSR 로 들어 있다** |
| **왓더버거** | 71 | 패스트푸드 | `whattheburger.co.kr/page.php?p_id=menu` | 보통 | **없음** | 허용 (`/adm/`,`/install/` 제외) | 확인 못 함 | 홈은 창업 모집 사이트. 메뉴 페이지는 렌더 6,892자로 실재 |
| **스크린토랑** | 37 | 패스트푸드 | `screentorang.com/menu/` | 보통 | **없음** | 허용 (아임웹 표준) | 확인 못 함 | 아임웹. 2.2MB 받아 렌더 4,466자. 스크린골프장 납품형 |
| **SSOJA(쏘자)** | 33 | 패스트푸드 | `ssoja.co.kr/menu` | 보통 | **없음** | 허용 (아임웹 표준, 규칙 블록이 **중복 기재**됨) | 확인 못 함 | 아임웹. 토스트 브랜드 |
| **호텔토랑** | 31 | 패스트푸드 | `hoteltorang.com/menu` | 보통 | **없음** (`/new` 는 "입점소식" 게시판) | 허용 (아임웹 표준) | 확인 못 함 | 아임웹. PC토랑·스크린토랑과 **같은 운영사**(대표 설로몬) |
| **버거운버거** | 25 | 패스트푸드 | `burgerunburger.com/menu` | 보통 | **없음** | 허용 (아임웹 표준) | 확인 못 함 | 아임웹. 렌더 3,914자 |
| **비스트로피자** | 68 | 패스트푸드 | `bistropizza.co.kr` | 보통 | **없음** (`/new` 는 "새소식") | 허용 (아임웹 표준) | 확인 못 함 | 아임웹. 731KB 받아 렌더 586자 — **메뉴 하위 경로 확인 못 함** |
| **KFC** | 미확인 | 패스트푸드 | `kfckorea.com/allmenu` | **불가** (현재) | `/promotion/newMenu` — 프로모션 글, 상품 목록 아님 | ⚠️ **404 (HTML 반환)** | 확인 못 함 (`/siteClause` 도 SPA) | Vue SSR 인데 **상품이 `__INITIAL_VUEX_STATE__` 에 없다.** §3 |
| **빽보이피자** | 243 | 피자 | `theborn.co.kr` | **불가** | 보도자료에 "출시" 기사 | 허용 (`Allow: /`) | 확인 못 함 | 앞선 조사와 동일 — **개별 브랜드 사이트가 없다.** 더본코리아 기업 사이트뿐 |
| **고피자** | 95 | 피자 | `gopizza.kr` | **불가** | 인스타 피드 JSON 에 "신메뉴" 캡션 | 허용 (`/admin/` 제외) | 확인 못 함 | Vercel SPA. `<title>` 조차 없다. 메뉴 목록이 HTML 에 없다 |
| **7번가피자** | 191 | 피자 | `7thpizza.com` | **불가** | — | 허용 (`Allow:/`) | 확인 못 함 | 29KB 받아 **렌더 336자.** 링크도 없다 |
| **빅스타피자** | 114 | 피자 | `bigstarpizza.co.kr` | **불가** | — | 허용 — 단 `Googlebot-Image`·`bingbot`·`AhrefsBot` 등 **선별 차단** | 확인 못 함 | `<title>` 이 "소자본창업 : 빅스타피자". **창업 모집 사이트**, 렌더 131자 |
| **피자스톰** | 94 | 피자 | `pizzastorm.co.kr` | **불가** | — | 허용 (`/html/fran.html` 만 제외) | 확인 못 함 | 7KB 받아 **렌더 44자.** 스플래시 |
| **힘난다버거** | 26 | 패스트푸드 | `himnanda.co.kr` | **불가** | — | 허용 (`Disallow:` 빈 값 = 전면 허용) | 확인 못 함 | "K 푸드테크 대표기업". 렌더 512자, 메뉴 링크 없음 |
| **에그셀런트** | 21 | 패스트푸드 | `eggcellent.co.kr` | **불가** | — | ⚠️ 자체서명 인증서 (https 실패, http 만) | 확인 못 함 | 렌더 **37자**. 스플래시 |
| **오지버거** | 25 | 패스트푸드 | `ogburger.co.kr` | **불가** | — | 허용 (`Allow: /`) | 확인 못 함 | **841바이트, 렌더 0자.** 빈 페이지 |
| **선명희피자** | 87 | 피자 | `smhpizza.co.kr` | **불가** | — | 확인 못 함 (https 연결 거부) | 확인 못 함 | http 로 469바이트 **렌더 0자.** 사이트가 사실상 없다 |
| **PJ피자** | 57 | 피자 | `pjpizza.co.kr` | **확인 못 함** | — | 허용 (아임웹 표준) | 확인 못 함 | 아임웹. 홈 938KB / 렌더 1,236자. **메뉴 경로 확인 못 함** |
| **버거리** | 86 | 패스트푸드 | `burgerry.co.kr` | **확인 못 함** | — | 허용 (`/php_/`,`/w/manual_html/` 제외) | 확인 못 함 | EUC-KR 계열인데 인코딩이 깨져 있다(`占쏙옙`). **메뉴 경로 확인 못 함** |
| **코브라독스** | 28 | 패스트푸드 | `cobradogs.co.kr` / `.com` | **확인 못 함** | — | 확인 못 함 | 확인 못 함 | `.co.kr` 인증서 호스트명 불일치, `.com` 은 TLS `UNEXPECTED_EOF`. **양쪽 다 못 받았다** |

### 1-2. 공식 도메인을 찾지 못한 브랜드

DNS 후보 **100여 개를 조회**해 응답하는 호스트만 HTTP 로 확인했다. 아래는 응답하는 후보가 없었거나, 응답한 게 다른 사이트였던 브랜드다.

| 브랜드 | 가맹점수 | 업종 | 가맹본부 | 확인한 것 |
|---|---:|---|---|---|
| **오구피자** | 360 | 피자 | (주)피자앤컴퍼니 | `ogu.co.kr` 은 **hosting.kr 파킹 페이지**(도메인 함정). 반올림피자와 같은 본부다 |
| **청년피자** | 312 | 피자 | (주)비에스비푸드 | 후보 5종 전부 NXDOMAIN |
| **피자먹다** | 102 | 피자 | (주)피자이노베이션 | 후보 3종 NXDOMAIN |
| **맘스피자** | 104 | 패스트푸드 | (주)맘스터치앤컴퍼니 | `momstouch.co.kr` 은 **맘스터치**(렌더 87자 스플래시). `momspizza.com` 은 AWS 미국 IP — 한국 브랜드가 아닐 가능성 |
| **맘스터치 피자앤치킨** | 37 | 패스트푸드 | (주)맘스터치앤컴퍼니 | 위와 동일 |
| **지정환피자** | 59 | 패스트푸드 | (주)정담에프에스 | 후보 3종 NXDOMAIN |
| **죠샌드위치** | 48 | 패스트푸드 | (주)제이에스앤씨 | 후보 4종 NXDOMAIN |
| **아띠몽** | 38 | 패스트푸드 | (주)솔푸드 | 후보 3종 NXDOMAIN |
| **석봉토스트** | 36 | 패스트푸드 | (주)석봉토스트 | 후보 3종 NXDOMAIN |
| **점순이 호떡** | 33 | 패스트푸드 | 떡메식품 | 후보 2종 NXDOMAIN. (호떡이라 우리 카테고리와도 안 맞는다) |
| **BT버거앤타코** | 30 | 패스트푸드 | (주)해냄 | 후보 4종 NXDOMAIN |
| **밀플랜비** | 19 | 패스트푸드 | (주)웨이브 | 후보 4종 NXDOMAIN |
| **서오릉피자** | 64 | 피자 | (주)서오릉에프앤비 | 후보 4종 NXDOMAIN |
| **유로코피자** | 63 | 피자 | (주)유로코푸드 | 후보 3종 NXDOMAIN |
| **피자파는집** | 61 | 피자 | 피자파는집(주) | `pizzaparty.com` 은 **유럽 IP 의 무관한 사이트**(도메인 함정) |
| **피자와썹** | 59 | 피자 | (주)와썹브로 | 후보 4종 NXDOMAIN |
| **번쩍피자** | 58 | 피자 | (주)번쩍코리아 | 후보 4종 NXDOMAIN |
| **피자는 치즈빨** | 55 | 피자 | (주)위대한사람들 | 후보 3종 NXDOMAIN |
| **피굽남피자** | 53 | 피자 | 피굽남앤유떡가맹본부 | 후보 3종 NXDOMAIN |

> **이 19개는 "사이트가 없다"가 아니라 "내가 못 찾았다"다.** 소규모 프랜차이즈는 자체 도메인 없이
> 인스타그램·네이버 플레이스·창업 포털(`myfranchise.kr` 등)만 쓰는 경우가 흔하다.
> 공정위 정보공개서 원문(가맹본부 홈페이지 항목)을 보면 바로 풀릴 가능성이 높다. §5 참고.

---

## 2. 맥도날드 — API 를 찾았다

이 조사의 핵심 과제였다. **결론부터: 풀렸다.** 상품이 JSON 으로 오고, **실제 등록일까지 온다.**

### 2-1. 어떻게 찾았나

`/kor/menu/burger` HTML 에 `apiBase:"https://www.mcdonalds.co.kr/api/v1"` 가 있는 것까지는 앞선 조사가 확인한 그대로다.
문제는 Nuxt3 번들이 `entry.*.js` 가 아니라 **해시 이름 9개**(`BNH_uf3h.js` 등)로 쪼개져 있었다는 점이다.
9개를 전부 받아 grep 했다. 엔드포인트는 **백틱 템플릿 리터럴**이라 따옴표 문자열 grep 으로는 안 잡힌다.

`BNH_uf3h.js` (247KB, 엔트리):
```js
Eu=()=>{const t=Wn().public.apiBase, r=Mt().path.includes("/kor"), o=r?"kor":"eng", …
  const c=(await $fetch(`${t}/${o}/category/list`)).resultObject.list.map(…)
```

`DMFGWSLn.js` (메뉴 `[slug]` 페이지):
```js
const U=se().public.apiBase, …
ae(()=>`${U}/${z}/product/product/list`,
   {query:{page:s, view_rows:B, mainCategory:T, subCategory:o, searchWord:w}, …})   // z="kor", B=6
```

`CRX-Smj4.js` (추천 슬라이더):
```js
q(`${$}/${a}/product/recommend/list`, …)
```

### 2-2. 실측 — 엔드포인트 3종 전부 200 JSON

```
GET https://www.mcdonalds.co.kr/api/v1/kor/category/list                 → 200 application/json, 7건
GET https://www.mcdonalds.co.kr/api/v1/kor/product/product/list
      ?page=1&view_rows=100&mainCategory=1                               → 200, totalCount 22, list 22건
GET https://www.mcdonalds.co.kr/api/v1/kor/product/recommend/list        → 200, 17건
```

인증·토큰·Referer 없이 그냥 GET 이다. `/kor` 을 `/eng` 로 바꾸면 영문이 온다.

카테고리 7개 (`category/list` 의 `seq`/`slug`):

| seq | slug | 이름 |
|---:|---|---|
| 1 | `burger` | 버거 |
| 7 | `mc-lunch` | 맥런치 |
| 8 | `happy-snack` | 해피 스낵 |
| 4 | `side-dessert` 계열 | 사이드&디저트 |
| 2 | `mc-morning` | 맥모닝 |
| 3 | `happy-meal` | 해피밀 |
| (1개 더) | | (응답 잘림 — 확인 못 함) |

`mainCategory=1` 응답의 `subCategory` 는 `16 버거전체 / 1 비프버거 / 2 치킨버거 / 17 기타`.
**`subCategory` 를 빼고 `view_rows` 를 키우면 카테고리 전체가 1요청에 온다.**

### 2-3. 신제품 신호 — `regDate` 가 진짜 등록일이다

상품 객체에 **필드가 68개** 있다. 그중 우리가 쓸 것:

```
regDate, modDate      ← 등록일 / 수정일
newIcon               ← NEW 배지 (bundle: class="ico_new new-${newIcon}")
korName, engName, korContent, engContent
pcImageUrl, moImageUrl, pcListImageUrl, …  (imgUrl 프리픽스와 결합)
calorie, protein, fat, sodium, …  + allergyList, materialList
menuStatus("단품,세트,런치"), menuStatusYN, exposureStatus("menu,recommend")
```

`recommend/list` 17건의 `regDate` 를 그대로 옮기면 이렇다:

```
2026-September-15th  맥크리스피™ 고추장 버터 세트
2026-September-15th  맥스파이시® 고추장 버터 세트
2026-August-12th     제주 풋귤 맥피즈 Medium
2026-August-4th      진주 고추 크림치즈 머핀 세트
2026-July-22nd       홍천 우리쌀 칩
2026-June-10th       그릴드 치킨 모닝 버거 세트
2026-May-13th        게살 크림 크로켓 스낵랩
2026-January-23rd    맥윙™ 2조각 콤보
2024-June-4th        맥스파이시® 상하이 버거 세트
2019-October-8th     맥치킨® 세트
2019-May-30th        빅맥® 세트
```

**신메뉴는 2026년, 클래식은 2019년.** 이미지 업로드일 같은 대용품이 아니라 **진짜 `released_at` 이다.**
이 조사에서 나온 신호 중 가장 강하다 — 피자헛 `saleStartDate` 와 같은 급이고, 본아이에프 `newYn`(Y/N)보다 위다.

⚠️ **두 가지 주의.**
1. 날짜 포맷이 `2026-September-15th` 라는 **영문 서수 로컬라이즈 문자열**이다. ISO 가 아니다. 파서를 따로 써야 한다.
   (`/eng` 응답도 같은 포맷인지는 **확인 못 함.**)
2. `newIcon` 은 필드가 있고 번들에 렌더 코드도 있는데, **지금 조회한 39건 전부 빈 문자열(`""`)이다.**
   기능은 살아 있으나 운영에서 안 쓰고 있다. `is_new` 는 `newIcon` 이 아니라 **`regDate` 로 판정해라.**

또 `korName` 에 `맥크리스피<sub class=reg>™</sub>` 처럼 **HTML 태그가 박혀 있다.** 상품명 정제가 필요하다.

### 2-4. robots · 약관

```
GET https://www.mcdonalds.co.kr/robots.txt   → 200 text/plain
User-agent: *
Allow: /
```
`can_fetch()` 전부 True. API 경로도 막혀 있지 않다.

**약관은 페이지 자체가 없다.** 홈(`/kor/main.do`) 푸터의 법적 링크는 `/kor/private` (개인정보처리방침) **하나뿐**이고,
Nuxt 번들 9개 전부에서 `이용약관`·`terms`·`clause` 문자열이 **0건**이다.
글로벌 브랜드라 본사 약관이 더 엄격할 거라 봤는데, 한국 사이트에는 웹 이용약관이 걸려 있지 않다.
(앱 약관은 별도로 있을 수 있다. **확인 못 함.**)

---

## 3. KFC — 못 풀었다. 어디까지 갔는지

프론트는 **Vue SSR**(`/assets/vendor.js` + `/assets/client.js`)이다.

`/allmenu` 를 받으면 SSR 초기 상태가 들어 있긴 한데 **상품이 없다**:
```json
__INITIAL_VUEX_STATE__ = {"count":0,"pageTitle":null,"orderInfo":null,"user":null,
  "sessionInfo":{"cartCnt":"0","csrf":{"token":"…","headerName":"X-CSRF-TOKEN"}, …},
  "host":"http://www.kfckorea.com"}
__INITIAL_COMPONENTS_STATE__ = [null,null]
```
렌더 텍스트는 1,148자, 전부 네비게이션이다.

`client.js`(589KB)를 받아 grep 했다. **라우트 테이블은 나왔지만 API 베이스는 안 나왔다.**
```js
{path:"/allmenu", component:f("allmenulist/Template"), children:p.a}
{path:":cate(recommend|chicken|burger|snack|drink)", component:r("allmenulist/ItemList")}
{path:"detail/:merchantShortYn/:id", component:r("allmenulist/allmenuDetail")}
{path:"newMenu", component:r("promotion/NewMenu"), meta:{title:["EVENT","새소식","신메뉴"]}}
{path:"newMenu/detail/:sq", component:r("promotion/PromotionView")}
```
그리고 페이지 경로 맵(`categories.menu`, `event.newMenu` 등)이 통째로 있는데 **전부 화면 라우트이지 API 가 아니다.**
`apiUrl`·`/api/` 문자열은 `client.js` 안에 **0건**이다.

**다음 사람이 이어서 할 것 (요청 3~4회면 된다):**
1. `/assets/vendor.js` 를 받아라. axios 인스턴스의 `baseURL` 이 거기 있을 가능성이 크다.
   (`client.js` 안에 axios 유틸 코드는 있는데 설정은 없었다.)
2. 그래도 없으면 `/allmenu/burger` 를 직접 받아 SSR 상태가 채워지는지 봐라. `/allmenu` 는 셸 라우트라 비었을 수 있다.
3. `sessionInfo.csrf` 가 있는 걸로 봐서 **일부 API 는 `X-CSRF-TOKEN` 헤더를 요구할 수 있다.** GET 목록도 그런지 확인해라.

**robots.txt 는 404 인데 HTML 을 준다** (SPA catch-all). 피자알볼로·GS25 와 같은 패턴이다.
```
GET https://www.kfckorea.com/robots.txt → 404, 2021바이트, '<!doctype html> <html> …'
```
상태코드만 보고 "허용"으로도, 본문만 보고 "규칙 없음"으로도 판단하면 안 된다. **부재로 취급하고 보수적 간격을 써라.**

약관은 `/siteClause` 라우트가 존재하는 걸 번들에서 확인했지만 **SPA 라 원문을 못 받았다. 확인 못 함.**

신제품 신호는 앞선 조사 그대로 `/promotion/newMenu` 뿐이고, 홈에 `/promotion/newMenu/detail/1126` 링크가 있다.
**`sq` 가 순증 번호**라 신규 판정에는 쓸 수 있으나, **프로모션 글이지 상품 레코드가 아니다.**

---

## 4. 근거 (실측 조각)

추측과 구분하기 위해 실제로 받은 것을 남긴다.

### 피자스쿨 — 워드프레스 REST API 가 열려 있다

`pizzaschool.net` 은 **워드프레스**다. 상품이 `/menu/{상품명}/` 퍼머링크로 하나씩 있다.
`/wp-json/wp/v2/menu` 는 404 인데, `/wp-json/wp/v2/types` 를 보면 **커스텀 포스트 타입 이름이 `portfolio`** 다.

```json
"portfolio": {"rest_base": "portfolio", "rest_namespace": "wp/v2", "name": "메뉴관리"}
```

```
GET http://pizzaschool.net/wp-json/wp/v2/portfolio?per_page=8&_fields=id,date,modified,slug,title,link
→ 200, X-WP-Total: 63
```
```
7210  2026-07-23T22:57:56 | 2026-07-23T22:58:44(mod) | 치킨타코피자
7206  2026-07-23T22:45:32 | …                        | 비프타코피자
6864  2026-01-01T22:59:39 | 2026-07-24T14:14:51      | 콘치즈피자
6386  2025-03-14T01:12:57 | 2026-01-07T14:02:02      | 프리미엄스테이크피자
4796  2023-06-08T13:26:13 | …                        | 불닭고구마피자
4442  2022-06-23T23:41:41 | …                        | 오지치즈포테이토피자
4179  2021-08-12T18:38:43 | …                        | 트러플포테이토피자
```

**`date` 가 ISO8601 이고 기본 정렬이 최신순이다.** 맥도날드와 달리 파서도 필요 없다.
63건 전체가 `per_page=100` 한 방에 온다. `_fields` 로 필요한 것만 받을 수도 있다.

⚠️ **https 는 자체서명 인증서라 실패한다.** `http://` 로만 받힌다. `verify=False` 가 아니라 **http 를 써야** 한다.

robots 는 워드프레스 기본이다.
```
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php
Sitemap: http://pizzaschool.net/wp-sitemap.xml
```
`/wp-json/` 은 막혀 있지 않다. `can_fetch()` True.

### 피자마루 — 신메뉴가 카테고리로 분리돼 있다

`/menu/10/` 이 **신메뉴** 전용 페이지다. 네비게이션이 카테고리 ID 를 그대로 노출한다.

```
/menu/10/  신메뉴          /menu/11/  클래식        /menu/32/  1인피자(8인치)
/menu/13/  몬스터          /menu/26/  골드&바이트    /menu/12/  프리미엄
/menu/27/  시카고&치즈폭탄  /menu/31/  퍼스널(마루업)  /menu/14/  투탑박스
/menu/15/  사이드 및 기타
```

완전 SSR 이고 상품명·설명·가격이 전부 들어 있다.

> BBQ치폴레 피자 — 불향 가득한 돈육 불고기와 담백한 포테이토 위에 바삭콘 시즈닝과 치폴레 소스를 듬뿍 뿌려,
> 스모키한 매콤함과 감칠맛이 폭발하는 특별한 피자! … **14,900원**

정렬 옵션에 **"신제품순"**이 있다(`메뉴정렬 신제품순 / 인기 제품순 / 가격 낮은순 / 가격 높은순`).
쿼리 파라미터로 노출되는지는 **확인 못 함**이지만, `/menu/10/` 만으로도 `is_new` 는 확정할 수 있다.

⚠️ **약관에 제약 조항이 있다.** `/terms/` **제9조 ("회원"의 의무)**:

> "회사가 제공하는 서비스를 통하여 얻은 정보를 회사의 사전 승낙 없이 허가용도 이외의 목적으로 사용하거나
> **복제, 유통, 상업적으로 이용하려는 행위**"

문언상 **"회원"의 의무**라 비회원 수집에 그대로 걸리는지는 다툼의 여지가 있다. 붙이기 전에 판단이 필요하다.

### 퀴즈노스서브 — 1요청에 전체 메뉴 + 신메뉴 구분

`/menu/menu.php` 한 페이지에 전 카테고리가 SSR 로 들어 있고, **맨 앞이 "New Menu 신메뉴" 섹션**이다.

> **New Menu 신메뉴** — 숯불치킨 샌드위치 / 터키 더블 아보카도 Turkey Double Avocado /
> 치폴레 터키 Chipotle Turkey / 한우 불고기 Hanwoo Bulgogi Sandwich
> **샌드위치** — 숯불치킨 샌드위치 / 트레디셔널 / B.L.T. / 이탈리안 / 햄 & 치즈 / 에그 마요 칠리 /
> 바질 카프레제 / 코리안 트레디셔널 / 크레이지 핫 치킨 / … (20종)
> **Salad & Pizza** — 치킨 샐러드 …

신메뉴 4건이 전체 목록에도 다시 나오므로 **교집합으로 `is_new` 를 True/False 양쪽 다 확정할 수 있다.**
가맹점 66개짜리 브랜드치고 신호 품질이 이 조사 상위권이다.

⚠️ **https 가 자체서명 인증서다.** `http://www.quiznos.co.kr` 로만 받힌다.
robots 는 `Allow:/` 이고 `can_fetch()` True.

회원약관(`/other/member.php`, 11,688자)은 **멤버십·기프트카드 약관**이다. 운영사는 (주)유썸.
크롤링·스크래핑·자동화 수집 금지 조항은 **없다.**

### 잇샌드 — 연번이 곧 신제품 순서다

`itsand.co.kr/board/bbs/board.php?bo_table=menu` 는 gnuboard 게시판이고 상품이 **연번 내림차순**으로 나온다.

```
148 자두라떼            - 권장소비자가격 : …
147 현미주먹밥 …
146 현미주먹밥 전주식비빔밥 샐러드 - 8,500원
145 그래놀라그릭요거트   - 6,900원
…
134 플레인 휘낭시에      - 2,900원
```

카테고리에 **`mn_new`(신메뉴)** 가 따로 있다. 이삭토스트의 상품코드 패턴과 같은 성격인데,
이쪽은 **6자리 날짜가 아니라 단순 연번**이라 `released_at` 은 못 채운다. `is_new` 판정용이다. 10페이지.

⚠️ robots.txt 자리에 **HTML** 이 온다 (200 text/html). 피자알볼로 패턴.

### 노브랜드버거 — 앞선 조사 재확인

`shinsegaefood.com/nobrandburger/index.sf` 홈 **1요청이 647,463바이트 / 렌더 43,505자**다.
전체 메뉴가 그 안에 다 있다. 수집 효율은 이 조사 전체에서 맥도날드 다음이다.

robots 는 **404 인데 HTML** 을 준다(2,268바이트).
법적 고지(`/terms/terms.sf`, 렌더 1,766자)는 **링크 사이트 면책 조항**이 전부고,
크롤링·스크래핑·복제 금지 조항은 **없다.**

신호는 여전히 **이미지 경로 업로드일뿐**이다. `BRAND-CANDIDATES.md` §6-5 대로
**`released_at` 에 넣지 마라. `uploaded_at` 까지다.**

### 반올림피자 — robots 가 내부 API 를 막는다

`banolimpizza.com` 은 `order.banolimpizza.com` 으로 리다이렉트된다. 사업자 298-86-00407, 대구 북구.

```
User-Agent: *
Allow: /
Disallow: /cart   /order/   /my/   /login   /sign-up/   /account/   /callback
Disallow: /address-setting/   /find-store/select   /event/participation/   /franchise/inquiry
Disallow: /api/                      ← ⚠️
Sitemap: https://order.banolimpizza.com/sitemap.xml
```

`/menu/list?categoryId=1` 은 허용이고 SSR 로 카테고리와 상품 일부가 나온다.
카테고리에 **신메뉴**가 있다.

> 메뉴 / **신메뉴** / 추천 / 베스트 메뉴 / 시그니처 / 클래식 / 스페셜 / 버라이어티 / 세트 메뉴 / 사이드 메뉴 / 음료&기타
> 버터갈릭 통마늘치킨 25,900원 · 버터베어 갈릭세트 32,400원

**하지만 `/api/` 가 Disallow 다.** 다른 브랜드에서 통했던 "번들 까서 내부 API 찾기"를 여기서 쓰면
**robots 위반**이다. HTML 만 긁어야 한다.

### 아임웹 6종 — robots 가 글자 하나까지 같다

PC토랑 · 스크린토랑 · 호텔토랑 · SSOJA · 버거운버거 · 비스트로피자 · PJ피자가 전부 **아임웹**이고
robots.txt 가 동일 템플릿이다.

```
User-agent: *
Allow: /
Disallow: /site_join   /site_join_agree   /login   /logout.cm   /shop_cart   /?mode*   /admin
Sitemap: https://<도메인>/sitemap.xml
```

`Disallow: /?mode*` 는 **김밥천국에서 약관 원문을 못 받게 만들었던 그 규칙**이다(`CANDIDATES-KOREAN.md`).
이 6곳도 약관이 `/?mode=policy` 류 경로면 같은 문제가 난다. **약관을 전부 "확인 못 함"으로 둔 이유다.**

SSOJA 는 규칙 블록이 **두 번 기재**돼 있다(`User-agent: *` 가 2회). 파싱은 되지만 관리가 안 된 흔적이다.

PC토랑·스크린토랑·호텔토랑은 **사업자가 같은 계열**이다 — 대표 설로몬, 주소 전부 `서울 강남구 선릉로 94길 14, 7층`.
어댑터를 하나 쓰면 셋을 커버할 수 있다. (호텔토랑 668-86-01982, 스크린토랑 114-86-84206)

아임웹은 수백 KB~2MB 를 받아 렌더 텍스트가 1~4천 자다. **상품명은 SSR 로 들어 있지만 배지·날짜는 없다.**

### 도메인 함정 — 이번에도 나왔다

`BRAND-CANDIDATES.md` §6-1 의 경고가 그대로 재현됐다.

| 브랜드 | 후보 도메인 | 실제 |
|---|---|---|
| 오구피자 | `ogu.co.kr` | **hosting.kr 파킹 페이지.** 본문에 `hosting.kr/servlet/html?pgm_id=HOSTING000006` 링크뿐 |
| 피자파는집 | `pizzaparty.com` | **유럽 IP(188.214.128.77)** 의 무관한 사이트 |
| 맘스피자 | `momspizza.com` | **AWS 미국 IP(44.195.229.203).** (주)맘스터치앤컴퍼니와 무관할 가능성 |
| 맘스피자 | `momstouch.co.kr` | **맘스터치** 스플래시(렌더 87자). 맘스피자가 아니다 |

**푸터 사업자명·사업자등록번호를 확인하고 시작해라.** 확인이 된 것만 표 1-1 에 넣었다.

---

## 5. 다음 사람에게

1. **맥도날드 어댑터를 먼저 붙여라.** 이 조사에서 나온 유일한 "관심도 1위 + 진짜 `released_at`" 조합이다.
   `category/list` 1회로 카테고리를 받고, 카테고리당 `product/product/list?view_rows=100&mainCategory={seq}` 1회.
   **총 8요청에 전체 메뉴 + 등록일**이 온다. 날짜 파서(`2026-September-15th`)와 상품명 HTML 태그 제거만 새로 써야 한다.
2. **피자스쿨은 그 다음이다.** 워드프레스 REST 라 **1요청에 63건 + ISO 날짜**다. 구현 난이도는 맥도날드보다 낮다.
   다만 **http 강제**라 `base.client()` 의 https 기본 가정과 충돌한다. 스타벅스 `_live_host()` 같은 처리가 필요하다.
3. **KFC 는 `vendor.js` 한 번만 더 받아보면 결론이 난다.** §3 에 남긴 3단계를 그대로 따라가라.
   여기서 안 나오면 "SPA + API 비공개"로 확정하고 접어라.
4. **robots 자리에 HTML 을 주는 곳이 이 카테고리에만 5곳**이다 — KFC, 노브랜드버거(신세계푸드), 프레드피자, 스테프핫도그, 잇샌드.
   피자알볼로·GS25 를 합치면 패턴이 굳어졌다. `CRAWLING-POLICY.md` 에 **"robots 응답의 Content-Type 을 검사한다"**를
   명문화할 때가 됐다. 상태코드만 보는 코드는 전부 오판한다.
5. **자체서명 인증서로 https 가 죽은 곳이 3곳**이다 — 피자스쿨, 퀴즈노스, 에그셀런트.
   `verify=False` 로 우회하지 마라. **http 로 붙는 게 맞다**(어차피 평문이라 보안 이득이 없고, verify=False 는 다른 사이트까지 위험하게 만든다).
6. **아임웹 어댑터를 하나 만들면 6개 브랜드가 붙는다.** 대신 전부 **신제품 신호가 없다.** 우선순위는 낮다.
   PC토랑·스크린토랑·호텔토랑은 사업자가 같으니 어댑터 1개로 3개다.
7. **도메인을 못 찾은 19개는 공정위 정보공개서 원문으로 풀어라.** `FRANCHISE-MASTER.md` §2 의
   `franchise.ftc.go.kr` 목록에서 각 브랜드 상세로 들어가면 **가맹본부 홈페이지 항목**이 있다.
   내가 쓴 DNS 후보 추측보다 훨씬 확실하다. 나는 요청 한도 때문에 거기까지 못 갔다.
8. **가맹점 수와 수집 가치가 심하게 어긋나는 카테고리다.**
   피자 1위 피자스쿨(628개)은 최상급 신호인데, 2~6위인 피자마루·반올림·오구·청년·빽보이(합계 1,780개) 중
   신호가 확실한 건 피자마루 하나뿐이다. 반대로 66개짜리 퀴즈노스가 신호 품질 3위다.

---

## 6. 추천 순위

기준은 지시받은 대로 **(1) 신제품 신호 → (2) 수집 난이도 → (3) 가맹점 수·인지도** 순이다.

| 순위 | 브랜드 | 가맹점수 | 왜 |
|---:|---|---:|---|
| **1** | **맥도날드** | 55 | **`regDate` 가 진짜 출시일**이다. JSON API, 인증 없음, robots `Allow: /`, 약관 자체가 없음. 관심도 1위. 카테고리 전체가 8요청 |
| **2** | **피자스쿨** | 628 | 워드프레스 REST **1요청에 63건 + ISO 날짜.** 구현 난이도 최저. 피자 업종 가맹점 1위. 감점 요인은 http 강제뿐 |
| **3** | **피자마루** | 498 | **신메뉴 전용 페이지 + "신제품순" 정렬.** 완전 SSR(이름·설명·가격). 피자 2위. ⚠️ 약관 제9조는 붙이기 전에 판단 필요 |
| **4** | **퀴즈노스서브** | 66 | **1요청에 전체 메뉴 + "New Menu" 섹션.** `is_new` 를 True/False 양쪽 확정 가능. 가맹점은 적지만 신호·효율이 최상위 |
| **5** | **노브랜드버거** | 189 | **홈 1요청에 전체 메뉴**(렌더 43,505자). 신세계푸드 약관에 금지 조항 없음. 단 **신호가 업로드일뿐**이라 4위 아래 |

**차순위(신호 없음 · 수집은 쉬움):** 노모어피자(174) · 난타5000피자(86) · 잇샌드(23, 연번 신호는 있으나 날짜 없음)
**보류:** 반올림피자(365) — 신메뉴 카테고리는 있으나 `/api/` 가 robots Disallow라 HTML 파싱만 가능
**착수 금지:** KFC · 빽보이피자 · 고피자 · 7번가피자 · 빅스타피자 · 피자스톰 · 힘난다버거 · 에그셀런트 · 오지버거 · 선명희피자 (상품이 HTML 에 없거나 사이트가 비어 있다)

---

## 7. 확인 못 한 것

- **KFC 메뉴 API 엔드포인트** — `client.js` 에 라우트만 있고 `apiUrl`·`/api/` 문자열이 0건. `vendor.js` 미확인
- **KFC 이용약관 원문** — `/siteClause` 라우트는 있으나 SPA
- **맥도날드 카테고리 7개 중 1개** — `category/list` 응답을 900자만 찍어서 마지막 항목이 잘렸다
- **맥도날드 `/eng` 응답의 날짜 포맷** — `/kor` 만 확인했다
- **맥도날드 앱 약관** — 웹에는 이용약관이 없다는 것만 확인했다
- **피자마루 "신제품순" 정렬의 쿼리 파라미터** — UI 에 옵션이 있는 것만 봤다
- **비스트로피자 메뉴 하위 경로** — 홈에서 `/new`(새소식)만 찾았고 메뉴 경로는 못 찾았다
- **PJ피자 · 버거리 메뉴 경로**
- **프레드피자 상품 목록의 로딩 방식** — 상세정보는 HTML 에 있는데 목록이 없다. ajax 로 추정만 했다
- **스테프핫도그 "등록일역순" 정렬 결과** — 옵션 존재만 확인, 상품이 HTML 에 없다
- **코브라독스** — `.co.kr` 인증서 호스트명 불일치, `.com` TLS `UNEXPECTED_EOF`. 양쪽 다 한 바이트도 못 받았다
- **아임웹 6종(PC토랑·스크린토랑·호텔토랑·SSOJA·버거운버거·비스트로피자·PJ피자) 약관** — `Disallow: /?mode*` 때문에 접근 보류
- **표 1-1 대부분의 약관** — robots 만 본 곳이 많다. 실제로 붙일 브랜드는 약관을 따로 확인해야 한다
- **1-2 의 19개 브랜드 공식 도메인** — DNS 후보 추측으로만 찾아봤다. 공정위 정보공개서 원문 미확인 (§5-7)
