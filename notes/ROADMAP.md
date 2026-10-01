# 로드맵 · 에이전트 배정안

이 프로젝트는 하루 만에 브랜드 46곳까지 커졌고, 그 대부분을 병렬 에이전트가 만들었다.
빠른 만큼 **결정과 미해결 항목이 흩어졌다.** 이 문서는 그걸 한곳에 모아 다음 작업을
지휘 가능한 상태로 만든다.

- 작성일: **2026-09-30**
- 근거: `collect.py` · `collectors/base.py` · `docs/CRAWLING-POLICY.md` ·
  `docs/CANDIDATES-*.md` 6종 · `git log` · GitHub Issues 실측
- 추측으로 채운 칸은 없다. 확인 못 한 건 그렇게 적었다.

---

## 1. 지금 상태

| 항목 | 값 | 근거 |
|---|---|---|
| 등록 브랜드 | **46곳** | `base.BRANDS` |
| 어댑터 모듈 | **39개** | `collect.ADAPTERS` (`bon_if` 하나가 8브랜드) |
| 수집 건수 | 4,390건 | `data/products.json` |
| 화면 노출 | 신제품만, 최대 300건 / 브랜드당 40건 | `collect.SHOW` · `PER_BRAND` |
| 페이지 무게 | 208KB | `docs/index.html` |
| 조사 문서 | 7종 (마스터 1 + 카테고리 6) | `docs/` |
| 공정위 등록 전수 | 9,449개 중 468개 문서화 | `docs/FRANCHISE-MASTER.md` |

**조사는 사실상 포화 상태다.** 카테고리 6종(치킨 / 한식·분식·도시락 / 일식·중식·아시안·샌드위치 /
베이커리·디저트 / 카페·주점 / 피자·햄버거·패스트푸드 / 고기·족발·찜탕)이 전부 훑렸고,
각 문서가 추천 순위와 "확인 못 한 것"을 남겼다. **다음 병목은 조사가 아니라 구현과 준법 확인이다.**

---

## 2. 지금 가장 중요한 작업 3개

### ① `base.client(verify=…)` 버그 — [#12](https://github.com/ttop32/sinsang-note/issues/12)

`client()` 가 `transport=` 를 같이 넘기기 때문에 httpx 가 `verify` 를 **조용히 무시한다.**
예외도 경고도 없다. 한 줄짜리 수정인데 **어댑터 4개가 여기서 멈춰 있다** —
또래오래(치킨 추천 1위·가맹 527), 노랑통닭(751), 가마치통닭(788), 훌랄라·지코바.

한 곳을 고치면 네 곳이 풀리는 건 이 백로그에서 이것뿐이다. 그래서 1순위다.

### ② 이미 수집 중인데 약관을 못 본 브랜드 — [#13](https://github.com/ttop32/sinsang-note/issues/13)

`CRAWLING-POLICY.md` §5.1 이 **"코드가 먼저 나가는 순서를 금지한다"** 고 명문화했는데,
브랜드가 하루 만에 46곳이 되면서 그 순서가 깨졌다. 메가MGC커피(JS 모달)·CU·세븐일레븐·
죠스떡볶이·김밥천국·에그드랍·스시로·본아이에프 8브랜드가 **약관 미확인 상태로 공개 사이트에 실려 있다.**

기술 부채가 아니라 **운영 리스크**다. 뒤늦게 금지 조항이 나오면 내리는 비용이 훨씬 크고,
지금은 우리가 만든 정책을 우리가 어기고 있는 상태다.

### ③ 맥도날드 어댑터 — [#16](https://github.com/ttop32/sinsang-note/issues/16)

조사가 끝났고 막힌 데가 없는 것 중 **가치가 가장 크다.**
`regDate` 가 진짜 출시일이라 `Item.released_at` 을 바로 채운다 — `Item` docstring 이
"가장 강한 신호"라고 부르는 값이고, 지금 이걸 주는 브랜드가 손에 꼽는다.
게다가 JSON API·인증 없음·robots `Allow: /`·**웹 약관 자체가 없음**이라 ②의 리스크도 없다.
햄버거 카테고리 관심도 1위이기도 하다.

> ①②는 막힌 것을 뚫는 일이고 ③은 가치를 더하는 일이다. ①은 다른 작업을 풀어주므로 먼저,
> ②는 시간이 갈수록 노출이 커지므로 병행, ③은 그 둘과 파일이 겹치지 않아 동시에 돌려도 된다.

---

## 3. 배정 패턴 — 무엇이 되고 무엇이 깨졌나

### 3-1. ✅ 파일 소유권이 병렬성을 결정한다

**에이전트 하나에 파일 하나.** 이게 이 프로젝트에서 제일 잘 먹힌 규칙이다.
`collectors/<브랜드>.py` 는 `BRAND` 상수와 `fetch() -> list[Item]` 만 있으면 성립하는
독립 모듈이라, 20여 명이 동시에 작업해도 충돌이 나지 않았다.

**공유 파일은 메인 세션이 독점한다.**

| 파일 | 소유 | 왜 |
|---|---|---|
| `collectors/base.py` | **메인 세션만** | `Item`·`BRANDS`·`SITES`·`client()`. 모든 어댑터가 읽는다 |
| `collect.py` | **메인 세션만** | `ADAPTERS` 등록, 신제품 판정, 렌더 |
| `web/*.py` | **메인 세션만** | 페이지·sitemap·feed 생성기가 서로 경로를 주고받는다 |
| `docs/CRAWLING-POLICY.md` | **메인 세션만** | 정책 정본 |
| `collectors/<브랜드>.py` | 에이전트 1명 | 이게 병렬 단위다 |
| `docs/CANDIDATES-<카테고리>.md` | 에이전트 1명 | 조사 에이전트의 출력 파일 |

**어댑터 에이전트에게 등록을 시키지 마라.** `BRANDS`·`SITES`·`ADAPTERS` 세 곳을 동시에
여러 명이 고치면 반드시 깨진다. 에이전트는 필요한 값(브랜드 표기·유형·세부분류·메뉴 URL)을
보고만 하고, 등록은 메인 세션이 모아서 한 번에 한다.

> 이 세션 중에도 실제로 그 순서로 돌아갔다. 완성된 어댑터 8개(매머드커피·더벤티·컴포즈커피·
> 할리스·스시로·에그드랍·써브웨이·샐러디)가 파일로만 존재하다가 메인 세션이 `BRANDS`·`SITES`·
> `ADAPTERS` 에 한 번에 등록해 46브랜드가 됐다.

### 3-2. ⚠️ 스크래치패드가 공용이라 파일명이 충돌했다 — 3번

임시 파일을 같은 디렉터리에 같은 이름으로 쓰다가 서로 덮어쓴 사고가 **세 번** 있었다.

→ **에이전트마다 하위 폴더를 지정해라.** 브리프에 경로를 박아서 준다.
```
스크래치 파일은 <스크래치패드>/<브랜드영문명>/ 아래에만 써라.
그 폴더 밖에 임시 파일을 만들지 마라.
```

### 3-3. ⚠️ 조사 결과가 틀린 경우가 반복됐다 — 최소 4번

이게 이 프로젝트에서 **가장 비싼 실패 패턴**이다. 구현 에이전트가 조사 문서를 사양서로 읽고,
실측이 다른데도 문서에 맞추려다 시간을 버렸다.

| 조사가 적은 것 | 실제 | 어디서 드러났나 |
|---|---|---|
| 바르다김선생 "SSR 라벨이 있다" | **주석처리된 죽은 마크업** | 구현 단계 |
| 컴포즈커피 "JS 렌더라 수집 불가" | 첫 페이지가 **스플래시**였을 뿐. 본체는 `/index1` | 재조사 |
| 미스터피자 "NEW 배지 없음" | 실제로 **15건 있었다** | 구현 단계 |
| 본아이에프 브랜드 코드 | `BF101`↔`BF102` 가 **뒤바뀌어 있었다** | 구현 단계 |
| 더벤티 "`/menu/new.html` 이 신메뉴 180건" | **상품이 아니라 홍보 포스터**였다 | 구현 단계 |
| 에그드랍 "홈의 NEW 슬라이더가 신제품 소스" | 고정 배너 한 장. 거기 걸린 상품은 `category=NEW` 에 있지도 않았다 | 구현 단계 |
| 스시로 "카드가 `<article class=new-menu-card>`" | 실제는 `<div class="card … menu-card">` | 구현 단계 |
| 죠스떡볶이 "`/menu/setmenu.html` 배지 미확인" | 그 페이지엔 **상품 카드가 아예 없다** | 구현 단계 |

**반대 방향 사고도 있다** — 원할머니 보쌈족발은 배지 마크업이 있는데 **전량 주석처리**였다.
CSS 나 마크업이 있다고 배지가 켜져 있는 게 아니다.

→ **모든 구현 에이전트 브리프에 "조사와 다르면 그대로 보고하라"를 넣는다.** §5 에 복붙용 문구가 있다.
→ 실측이 조사와 다르면 **조사 문서를 고치는 것도 그 에이전트의 일**이다. 안 그러면 다음 사람이 또 걸린다.

### 3-4. ✅ 조사 에이전트에 요청 예산을 준 게 잘 먹혔다

"브랜드당 HTTP 5회" 같은 상한이 있어서 조사가 폭주하지 않았고, 예산을 넘긴 경우는
문서에 이유가 남았다(파리바게뜨 7요청 — 1순위 추천이라 약관 확인까지 했다).
남의 서버를 치는 작업이라 이 상한은 예의 문제이기도 하다.

→ **계속 유지한다.** 넘길 거면 이유를 적게 한다.

### 3-5. ⚠️ 요청 범위 밖은 보고만 하게 한 건 옳았다 — 다만 후속이 안 붙었다

치킨 조사 에이전트가 `client()` 의 `verify` 버그를 정확히 진단하고도
**"요청 범위 밖이라 고치지 않았다"** 고 적고 끝냈다. 범위를 지킨 건 맞다
(공유 파일이라 건드렸으면 충돌했다). 문제는 그 보고가 **이슈로 승격되지 않아** 묻혔다는 것이다.

→ **범위 밖 발견은 보고하되, 메인 세션이 그 자리에서 이슈로 만든다.** 이번에 #12 로 올렸다.

### 3-6. ✅ "모르면 None" 계약이 데이터를 지켰다

`Item` 의 `is_new` 가 True / False / None 삼상 값이고, docstring 이 "알 수 없으면 None" 을
명시한다. 어댑터들이 이걸 지켜서 **배지가 없다고 False 를 찍지 않았다.**
덕분에 `is_fresh()` 가 "브랜드가 아니라고 말한 것"과 "우리가 모르는 것"을 구분할 수 있다.

같은 정신이 조사 문서에도 있다 — "확인 불가"를 추정으로 채우지 않는다(`CRAWLING-POLICY.md` §5.6).
**이 계약을 새 에이전트에게도 반드시 전달해라.** 채우고 싶은 유혹이 제일 큰 자리다.

---

## 4. 다음에 띄울 에이전트

파일이 겹치지 않는 것끼리 묶었다. 같은 묶음 안은 동시 실행해도 된다.

### 웨이브 1 — 막힌 것을 뚫는다 (메인 세션 직접)

| # | 범위 | 파일 | 이슈 |
|---|---|---|---|
| M1 | `client()` 가 `verify` 를 transport 로 흘리게 고친다. `verify=False` 는 예외로 막는다 | `collectors/base.py` | [#12](https://github.com/ttop32/sinsang-note/issues/12) |
| M2 | `Item.price` 도입 여부 결정 (미착수 어댑터 9개가 들어오기 전에) | `collectors/base.py` | [#4](https://github.com/ttop32/sinsang-note/issues/4) |

**에이전트에게 주지 마라.** 둘 다 `base.py` 고, 이 파일은 39개 어댑터가 전부 읽는다.
M1 이 끝나기 전에는 웨이브 2 의 A4(또래오래)를 착수시키지 않는다.

### 웨이브 2 — 조사가 끝난 어댑터 (에이전트 1명 = 파일 1개)

| # | 브랜드 | 새로 만들 파일 | 신호 | 선행 | 이슈 |
|---|---|---|---|---|---|
| A1 | 맥도날드 | `collectors/burger_mcdonalds.py` | **`regDate` = 출시일** | — | [#16](https://github.com/ttop32/sinsang-note/issues/16) |
| A2 | 피자스쿨 | `collectors/pizza_pizzaschool.py` | WP REST 1요청 63건 + ISO 날짜 | — | [#17](https://github.com/ttop32/sinsang-note/issues/17) |
| A3 | 퀴즈노스서브 | `collectors/sandwich_quiznos.py` | 1요청에 전체 + New Menu 섹션 | — | [#17](https://github.com/ttop32/sinsang-note/issues/17) |
| A4 | 노브랜드버거 | `collectors/burger_nobrand.py` | 업로드일뿐 | — | [#17](https://github.com/ttop32/sinsang-note/issues/17) |
| A5 | 피자마루 | `collectors/pizza_pizzamaru.py` | 신메뉴 전용 페이지 + 신제품순 정렬 | **약관 제9조 확인** | [#17](https://github.com/ttop32/sinsang-note/issues/17) |
| A6 | 자담치킨 | `collectors/chicken_jadam.py` | 신메뉴 전용 페이지 | — | [#18](https://github.com/ttop32/sinsang-note/issues/18) |
| A7 | 부어치킨 | `collectors/chicken_booa.py` | NEW 탭 | 약관이 JS 모달 — 사람이 봐야 함 | [#18](https://github.com/ttop32/sinsang-note/issues/18) |
| A8 | 땅땅치킨 | `collectors/chicken_ttangttang.py` | 메뉴 번호 | robots 가 약관 경로를 막음 | [#18](https://github.com/ttop32/sinsang-note/issues/18) |
| A9 | 또래오래 | `collectors/chicken_ttoraeore.py` | **항목별 등록일자** | **M1 필수** | [#18](https://github.com/ttop32/sinsang-note/issues/18) |

가맹점 수로는 또래오래(527)·자담(708)·부어(260)·땅땅(177)·피자스쿨(628)·피자마루(498) 순이지만,
**A1 맥도날드를 먼저 띄운다** — `released_at` 을 주는 브랜드가 희소해서다.

### 웨이브 3 — 조사 (에이전트 1명 = 문서 1개)

| # | 범위 | 건드릴 파일 | 이슈 |
|---|---|---|---|
| R1 | 페리카나 `_nuxt` 청크 해독 (치킨 가맹 1위) | `docs/CANDIDATES-CHICKEN.md` | [#15](https://github.com/ttop32/sinsang-note/issues/15) |
| R2 | 치킨 잔여 7곳 경로 조사 (또봉이 RSC 페이로드·보드람·노랑통닭·꾸브라꼬 외) | `docs/CANDIDATES-CHICKEN.md` | [#20](https://github.com/ttop32/sinsang-note/issues/20) |
| R3 | 공식 도메인 미확정 ~50곳 — 공정위 정보공개서로 법인명부터 | `docs/CANDIDATES-*.md` 전부 | [#21](https://github.com/ttop32/sinsang-note/issues/21) |

⚠️ **R1 과 R2 는 같은 파일을 쓴다.** 동시에 띄우지 마라. R1 을 먼저 하고 R2 는 그다음이거나,
R2 에게 별도 파일에 쓰게 한 뒤 메인 세션이 병합한다.

### 웨이브 4 — 준법·운영 (메인 세션 또는 전담 1명)

| # | 범위 | 파일 | 이슈 |
|---|---|---|---|
| C1 | 약관 미확인 브랜드 일괄 확인 + 정책 표 갱신 | `docs/CRAWLING-POLICY.md` | [#13](https://github.com/ttop32/sinsang-note/issues/13) |
| C2 | 사람 판단 3건 (죠스떡볶이 NEW·스타벅스 `new_SDATE`·배스킨 연도) | 각 어댑터 docstring | [#19](https://github.com/ttop32/sinsang-note/issues/19) |
| I1 | 실패 브랜드 이월 만료 + 실패 알림 (같이 설계) | `collect.py`, 워크플로 | [#14](https://github.com/ttop32/sinsang-note/issues/14) · [#6](https://github.com/ttop32/sinsang-note/issues/6) |
| I2 | 이미지 R2 이전 — **브랜드별로 갈라야 한다** | 신규 | [#5](https://github.com/ttop32/sinsang-note/issues/5) |

C1 은 브라우저가 필요한 항목(메가 JS 모달, 부어치킨 `javascript:void(0)`)이 있어
자동화로 끝나지 않는다. **사람이 붙어야 하는 일이라고 처음부터 잡아라.**

---

## 5. 모든 에이전트 브리프에 넣을 공통 문구

복붙해서 쓴다. §3 의 실패 패턴을 그대로 막는 문장들이다.

```
[소유권] 너는 <파일 경로> 하나만 수정한다. collect.py 와 collectors/base.py 는
공유 파일이라 메인 세션 소유다. BRANDS·SITES·ADAPTERS 에 등록이 필요하면
직접 하지 말고 필요한 값을 보고만 해라.

[스크래치] 임시 파일은 <스크래치패드>/<네 작업 이름>/ 아래에만 써라.
그 폴더 밖에 파일을 만들지 마라. 공용 경로에 쓰면 다른 에이전트와 충돌한다.

[조사와 다르면] 조사 문서(docs/CANDIDATES-*.md)는 사양서가 아니라 참고자료다.
실측이 문서와 다르면 문서를 따르지 말고 실측을 그대로 보고해라.
문서에 맞추려고 코드를 억지로 쓰지 마라. 실제로 여러 번 틀렸다 —
바르다김선생 "SSR 라벨"은 주석처리된 죽은 마크업이었고, 컴포즈 "JS 렌더 불가"는
첫 페이지가 스플래시였던 것이고, 미스터피자 "배지 없음"은 실제로 15건 있었고,
본아이에프 브랜드 코드 2개는 뒤바뀌어 있었다.
반대로 원할머니 보쌈족발은 배지 마크업이 있는데 전량 주석처리였다 —
마크업이 있다고 배지가 켜져 있는 게 아니다.
다른 점을 찾으면 해당 조사 문서도 같이 고쳐라.

[모르면 None] Item.is_new 는 True / False / None 삼상 값이다.
브랜드가 신제품이라고 표시했으면 True, 아니라고 확인됐으면 False,
알 수 없으면 None 이다. 배지가 없다는 이유로 False 를 찍지 마라.
날짜도 마찬가지다 — 추정한 값을 released_at 에 넣지 마라.
브랜드가 "출시일"이라고 말해준 게 아니면 uploaded_at 까지다.

[예의] docs/CRAWLING-POLICY.md 를 따른다. 특히:
- 착수 전 robots.txt 실측 + 이용약관 확인이 코드보다 먼저다 (§5.1)
- robots.txt 상태코드를 네 갈래로 본다: 200 / 404·410(제한 없음) /
  401·403(전면 금지) / 5xx(금지로 간주) (§6-2)
- can_fetch() 결과만 믿지 마라. 쿼리스트링 와일드카드를 놓친다.
  robots 원문을 눈으로 읽어라 (§6-2)
- verify=False 금지 (§6-1). TLS 로 막히면 그대로 "막혔다"로 적는다
- HTTP 요청 전에 dig 와 openssl s_client 로 도메인을 먼저 검증해라 (§6-5).
  가짜·파킹·매물 도메인이 20건 넘게 나왔다. 둘 다 부하를 만들지 않는다
- 요청 간 최소 1초 지연. 브랜드당 요청 상한을 지키고, 넘길 거면 이유를 적어라
- 브랜드 내 요청은 순차. 병렬 금지

[범위 밖] 범위 밖 문제를 발견하면 고치지 말고 보고해라.
보고를 안 하면 묻힌다 — 실제로 base.client() 의 verify 버그가
"요청 범위 밖이라 고치지 않았다"로만 남아 한동안 묻혀 있었다.

[근거를 남겨라] 모듈 docstring 에 실측 근거를 적어라 —
요청 수, 건수, 신호 필드가 무엇인지, robots 상태, 약관 확인 여부.
다음 사람이 네 판단을 재현할 수 있어야 한다.
```

---

## 6. 이슈 지도

| 우선순위 | 이슈 | 성격 |
|---|---|---|
| **P0** | [#12](https://github.com/ttop32/sinsang-note/issues/12) `client(verify=)` 버그 | 한 줄이 어댑터 4개를 막고 있다 |
| **P0** | [#13](https://github.com/ttop32/sinsang-note/issues/13) 약관 미확인 브랜드 | 운영 리스크. 이미 공개 중 |
| P1 | [#16](https://github.com/ttop32/sinsang-note/issues/16) 맥도날드 | 막힌 데 없는 최고 가치 |
| P1 | [#17](https://github.com/ttop32/sinsang-note/issues/17) 피자·패스트푸드 4종 | 조사 완료, 착수만 |
| P1 | [#18](https://github.com/ttop32/sinsang-note/issues/18) 치킨 4종 | 또래오래는 #12 선행 |
| P1 | [#15](https://github.com/ttop32/sinsang-note/issues/15) 페리카나 `_nuxt` | 가맹 1위, 기술 하나로 막힘 |
| P1 | [#14](https://github.com/ttop32/sinsang-note/issues/14) 이월 만료 | 스타벅스가 지금 그 상태 |
| P1 | [#6](https://github.com/ttop32/sinsang-note/issues/6) 실패 알림 | 감지는 됐고 알림만 남음. #14 와 같이 |
| P1 | [#19](https://github.com/ttop32/sinsang-note/issues/19) 사람 판단 3건 | 기계로 답이 안 나온다 |
| P1 | [#4](https://github.com/ttop32/sinsang-note/issues/4) 가격 필드 | 미착수 어댑터 9개 들어오기 전에 |
| P1 | [#5](https://github.com/ttop32/sinsang-note/issues/5) 이미지 R2 | 브랜드별로 갈라야 함 (robots) |
| P2 | [#8](https://github.com/ttop32/sinsang-note/issues/8) 카테고리 체계 | 범위 재정의 필요 |
| P2 | [#20](https://github.com/ttop32/sinsang-note/issues/20) 치킨 잔여 7곳 | 조사 |
| P2 | [#21](https://github.com/ttop32/sinsang-note/issues/21) 도메인 미확정 ~50곳 | 조사 |
| P2 | [#10](https://github.com/ttop32/sinsang-note/issues/10) 소셜 소스 | 사용자 지정 최하위 |

**2026-09-30 에 닫은 것:** [#1](https://github.com/ttop32/sinsang-note/issues/1) first_seen 오염(브랜드별 최초 등장 + `baseline` + `SURGE` 로 해결) ·
[#2](https://github.com/ttop32/sinsang-note/issues/2) 개별 페이지·sitemap(`web/` 패키지) ·
[#3](https://github.com/ttop32/sinsang-note/issues/3) 필터·페이지 무게(자동 생성 탭 + `SHOW`/`PER_BRAND`) ·
[#7](https://github.com/ttop32/sinsang-note/issues/7) 신규 구분(전체 목록을 없애고 신제품만 렌더) ·
[#9](https://github.com/ttop32/sinsang-note/issues/9) GS25(카탈로그가 앱 전용으로 이관 — 수집 안 함)

---

## 7. 착수 금지 목록

되돌아오는 질문이라 한 곳에 모은다. 근거는 `CRAWLING-POLICY.md` §6-4.

| 사유 | 브랜드 |
|---|---|
| robots.txt 가 우리 UA 를 차단 | 롯데리아, 빕스, 뚜레쥬르, 엽기떡볶이, 니뽕내뽕 |
| WAF 가 검색봇 UA 만 통과 | 투썸플레이스 |
| 사이트 폐쇄(앱 이관) | GS25 |
| 메뉴가 이미지뿐 (OCR 은 범위 밖) | 주점 전반(투다리·청담동말자싸롱), 가장맛있는족발 |
| HTTPS 만 있고 인증서가 깨짐 | 탐앤탐스, 커피스미스, 크리스피크림 |
| 상품이 HTML 에 없음 | 미소야, 돈치킨, 스트릿츄러스, KFC |

**UA 를 위장해 뚫지 않는다.** 대법원 2021도1533 이 정보통신망 침입죄 근거로 든 행위다.

`docs/CANDIDATES-MEAT.md` 는 카테고리 전체에 **"신상노트에 값어치가 없다"** 는 판정을 내렸다.
`released_at` 을 줄 수 있는 브랜드가 한 곳도 없고 `is_new` 를 양쪽으로 확정할 수 있는 곳도
마왕족발 하나뿐이다. 다른 카테고리가 다 떨어지기 전에는 손대지 않는다.
