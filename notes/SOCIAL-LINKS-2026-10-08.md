# 브랜드 SNS 링크 보강 (2026-10-08)

**조사 전용 문서. 고친 코드는 `social.py` 한 파일뿐이다.**
직전 조사(`notes/INSTAGRAM.md` 2026-10-01, `notes/YOUTUBE.md` 2026-10-02)는 브랜드가
171곳이던 때 것이다. 그 뒤 브랜드가 **217곳**으로 늘면서 인스타 90곳·유튜브 116곳이
비어 있었다. 이번에 그 빈칸(둘을 합치면 121개 브랜드)을 전부 다시 훑었다.

## 조사 방법 — 앞선 두 문서와 같은 경로

1. `base.SITES` 의 주소 **와 그 도메인 루트**를 `base.client()` 로 받는다
   (UA 위장·`verify=False` 안 씀).
2. 원본 HTML 에서 `instagram.com/…` · `youtube.com/@|channel|user|c/…` 만 딴다.
   **HTML 주석(`<!-- -->`) 안의 링크는 따로 표시해서 걸러냈다** — 커피빈 때 밟은 함정이다.
   `/p/` · `/reel/` · `/embed/` · `youtu.be/<id>` 는 게시물·영상이라 계정 증거가 아니다.
3. 나온 계정·채널을 **전부 열어서** 프로필명·소개·팔로워/구독자를 확인했다.
   유튜브는 `channel/UC…` · `user/…` 를 `@핸들`로 변환한 뒤 그 핸들로 다시 열었다.
4. 마지막에 **`social.links()` 가 만드는 실제 주소 47개를 전부 GET** 해서
   200 + 그 브랜드가 맞는지 확인했다(실패 0건).

검색해서 찾은 것, 이름이 그럴듯한 것은 **한 건도 넣지 않았다.**

---

## 채운 것 — 인스타 32곳

| 브랜드 | 핸들 | 근거 (어느 주소의 어디) | 열어본 결과 |
|---|---|---|---|
| 33떡볶이 | `33tteokbokki` | `33success100.co.kr` 푸터 SNS 아이콘 | 33떡볶이 / 1,529 |
| 공차 | `gongcha_korea` | `gong-cha.co.kr` 헤더 `div.sns-wrap > a.insta` | 공차코리아 / Gong cha Korea Official / 18.6만 |
| 김밥킹 | `gimbapking_official` | `김밥킹.com`(`xn--4k0bn7xt5p.com`) SNS 링크 | 김밥킹 / 1,396 |
| 달롱도르 | `dallondor_official` | `dallondor.com` SNS 링크 | 달롱도르 공식 계정 / 503 |
| 달리는커피 | `dalcu_korea` | `dalcu.co.kr` SNS 링크 | 달리는커피 / 1.1만 |
| 대상 | `daesang_news` | `daesang.com` 루트 `schema.org/Organization` 의 `sameAs` | **대상그룹** 공식 인스타그램 / 1.6만 |
| 디저트39 | `dessert39_official` | `dessert39.com` SNS 링크 | 디저트39 DESSERT39 / 76.5만 |
| 떡군이네떡볶이 | `tteokgoonene` | `떡군이네떡볶이.com`(`xn--6e0b73ep0espx.com`) SNS 링크 | 떡군이네 떡볶이 / 3,614 |
| 뚜레쥬르 | `touslesjours_kr` | `tlj.co.kr` 푸터 `a.instagram` (옆 블로그 링크는 주석 처리됨) | 뚜레쥬르 / 35.6만 |
| 마왕족발 | `mawang_official` | `mawangpork.com` SNS 링크 | 마왕족발 공식 계정 / 2.1만 |
| 매스커피 | `masscoffee_` | `mass-coffee.com` SNS 링크 | 매스커피 / 1,574 |
| 백억커피 | `10billioncoffee` | `10billioncoffee.co.kr` SNS 링크 | 백억커피 공식 인스타그램 / 1.2만 |
| 빙동댕 | `bing_dong_daeng` | `빙동댕.kr`(`xn--hl1bno83x.kr`) SNS 링크 | 빙동댕 / 2,196 |
| 빨라쪼 | `palazzo_kr` | `ipalazzo.com` SNS 링크 | 빨라쪼 / 4,474 |
| 아웃백스테이크하우스 | `outbackkorea` | `outback.co.kr` 푸터 `ul.sns-menu` + `schema.org` `sameAs` **두 곳 일치** | 아웃백 스테이크하우스 / 24.8만 |
| 에밀리아젤라또 | `emiliagelato_official` | `emiliagelato.co.kr` SNS 링크 | 에밀리아젤라또 / **15** (게시물 3) |
| 엽기떡볶이 | `yupdduk_official` | `yupdduk.com` SNS 링크 + 공식 유튜브 소개가 되건다 | 엽기떡볶이 공식 인스타그램 / 5.1만 |
| 우지커피 | `oozy.coffee_official` | `oozycoffee.com` SNS 링크 | 우지커피 공식계정 / 1.8만 |
| 읍천리382 | `eupcheonri_official` | ⚠️ 아래 "한 다리 건넌 것" 참고 | 도심 속 시골농촌카페 읍천리382 공식 인스타그램 / 2.3만 |
| 쥬씨 | `newjuicy_kr` | `no1juicy.com` 푸터 SNS 버튼 (⚠️ `schema.org` 쪽은 함정, 아래 참고) | 쥬씨 Juicy / 4,544 |
| 차얌 | `chayamkr` | `chayam.co.kr` `schema.org/Organization` 의 `sameAs` | 차얌 / 5,031 |
| 카페051 | `cafe_051_official` | `cafe051.com` SNS 링크 | 카페051 CAFE051 / 4,094 |
| 카페만월경 | `manwolgyung_official` | `cafewhale.com` SNS 링크 + 공식 유튜브 소개가 되건다 | 카페 만월경 \| 24시 카페 / 4,399 |
| 카페베네 | `caffebene_official` | `caffebene.co.kr` SNS 링크 | 카페베네 공식 인스타그램 / 2.4만 |
| 카페인중독 | `caffeinism_company` | `카페인중독.com`(`xn--iq1bo78ac9at1k9mh.com`) 본문 SNS 버튼 (⚠️ `schema.org` 쪽은 함정) | 카페인중독 공식인스타그램 / 1.5만 |
| 커피베이 | `coffeebay_official` | `coffeebay.com` SNS 링크 | 커피베이 공식 계정 / 9,849 |
| 태리로제떡볶이 | `terryroze_official` | `terryroze.com` SNS 링크 | 태리로제떡볶이 \| 이태리를 입다 / 8,230 |
| 텐퍼센트커피 | `tenpercent.coffee` | `tenpercentcoffee.com` SNS 링크 | 텐퍼센트커피 / 2.1만 |
| 파스쿠찌 | `pascucci_kr` | `pascucci.co.kr` 푸터 `li.insta` (헤더·푸터 두 군데, **주석 아님**) | 파스쿠찌 공식 인스타그램 / 15.8만 |
| 팔공티 | `palgongtea.official` | `palgongtea.co.kr` 푸터 `a.instagram` — ⚠️ **https 인증서가 깨져 http 로만 열린다** | 팔공티 공식 계정 / 8,212 |
| 피자마루 | `pizzamaru_official` | `pizzamaru.co.kr` SNS 링크 | 피자마루 공식 인스타그램 / 2.4만 |
| 피자스쿨 | `pizzaschool_official` | `pizzaschool.net` SNS 링크 | 피자스쿨 공식 인스타그램 / 2.6만 |

## 채운 것 — 유튜브 15곳

사이트가 **채널 주소**를 직접 건 것만 넣었다. 영상 임베드·`youtu.be/<id>` 만 있는 곳은 전부 버렸다.

| 브랜드 | 핸들 | 사이트가 건 주소 | 채널명 / 구독자 |
|---|---|---|---|
| 33떡볶이 | `33tteokbokki` | `channel/UC1WqzWW1XerKqcpYRGRoSzA` | 33 떡볶이 / 188 |
| 대상 | `DTUBE` | `channel/UCfv1dkNKCFUtZouvp3DhS3g` (푸터 `li.sns-yt` + `schema.org`) | **대상그룹 DAESANG 디튜브** / 1.39만 |
| 디저트39 | `dessert39_official` | `channel/UC0ykSSGK7ik4_qIlyA-jpcg` | 디저트39 / 8.23천 |
| 백억커피 | `10billioncoffee` | `@10billioncoffee` | 백억커피 / 1.61천 |
| 빙동댕 | `빙동댕빙수` | `@%EB%B9%99%EB%8F%99%EB%8C%95%EB%B9%99%EC%88%98` (한글 핸들) | 빙동댕 / 671 |
| 아웃백스테이크하우스 | `outbackkorea` | `user/outbackkorea` (푸터 + `schema.org`) | 아웃백 스테이크하우스 / 7.92만 |
| 엽기떡볶이 | `yupdduk_official` | `channel/UC6n3KHZx7bs5dK1fSVqWLvw` | **동대문엽기떡볶이** / 6.04천. 소개가 `yupdduk.com` 과 공식 인스타를 되건다 |
| 우지커피 | `oozycoffee` | `@oozycoffee` + `channel/UCu7JJS68DTLspQmVT9ikmNw` (같은 채널) | 우지커피 / 681 |
| 읍천리382 | `eupcheonri_official` | `@eupcheonri_official` | 읍천리382 / 925. 소개가 공식 도메인을 되건다 |
| 쥬씨 | `juicy_kr_official` | `channel/UC2e5U1W0eITo9l3R5hdLK-Q` | 쥬씨 / 421. 소개 `쥬씨 유튜브 공식계정 입니다` |
| 카페051 | `cafe051_official` | `@cafe051_official` | **공오일** / 101. 소개 `카페051 공식 유튜브 채널입니다` |
| 카페만월경 | `manwolgyung` | `@manwolgyung` | 카페 만월경 / 1.79천. 소개가 `cafewhale.com` 을 되건다 |
| 카페베네 | `caffebene4373` | `channel/UCQ7MW5IpWOL9LwQqr_AWQ9A` | 카페베네 Caffebene / 400. 소개 `카페베네(Caffebene)의 공식 유투브 채널` |
| 파스쿠찌 | `pascucci_kr` | `channel/UCHKRIWTWjq0uzJOAm6KFHOg` (푸터 `li.youtube`) | **파스쿠찌_유튜브점** / 2.06천 |
| 피자마루 | `공식채널피자마루` | `user/pizzamaru` (한글 핸들) | 공식채널피자마루 / 7.74천 |

> 인스타 핸들과 유튜브 핸들이 **다른** 브랜드가 셋이다 — 우지커피(`oozy.coffee_official` ≠ `oozycoffee`) ·
> 카페051(`cafe_051_official` ≠ `cafe051_official`, 언더바 위치가 다르다) · 카페베네(`caffebene_official` ≠ `caffebene4373`).
> 한쪽을 복사해 다른 쪽에 쓰면 안 된다.

---

## 🔴 사이트가 가리켰지만 버린 것

| 브랜드 | 사이트가 가리킨 것 | 열어보니 | 처리 |
|---|---|---|---|
| 쥬씨 | `schema.org` `sameAs` → `juicyjuice_official` | `100% Homemade Orange Jucie` / **팔로워 6** — 남의 계정 | 푸터가 거는 `newjuicy_kr` 사용 |
| 카페인중독 | `schema.org` `sameAs` → IG `caffeine_addiction` | `coffee` / **팔로워 2, 게시물 1** — 빈 계정 | 본문 버튼의 `caffeinism_company` 사용 |
| 카페인중독 | `schema.org` `sameAs` → YT `@caffeine_addiction` | 채널명 **`lose`**, 소개·링크 없음 | **유튜브 없음** |
| 모락떡볶이 | `@user-zi8qb7ci5y` | **404 — 없는 채널** | 유튜브 없음 |
| 타래퀸 | `taraequeen.com` → `tarae_queen_official` | **없는 계정**(프로필 메타 안 나옴) | 인스타 없음 |
| 바르다김선생 | `teacherkim_insta` | **여전히 죽어 있다**(2026-10-01 확인과 같음) | 인스타 없음 |
| 고망고 | `gomango.kr` 푸터 `ul.sns` → `gigicoffee_kr` | **없는 계정** + 애초에 자매 브랜드(지지커피) 계정 | 인스타 없음 |
| 차얌 | 푸터 → `juicychayam_official` | `쥬씨&차얌` — 두 브랜드 공용 계정 | 브랜드 전용 `chayamkr` 사용 |
| 읍천리382 | `schema.org` → `dakdonggari_official` | `수성못 술집 닭동가리 본점` — 다른 브랜드 | 버림 |
| 읍천리382 | 본문 → `eupcheonri_catering` | `읍천리382 케이터링` — 케이터링 전용 부계정 | 본계정 사용(아래) |
| 하림산업 | `harim.com` → `harim_natural` / `@하림TV` | **하림(본사)** 것. `하림` 브랜드에 이미 들어가 있다 | 하림산업은 없음 |
| 노브랜드버거 | `channel/UC9D4PXxFPeFphOT5a_MQm0w` | **스프TV = 신세계푸드**(별도 브랜드로 등재됨) | 없음 (직전 판단 유지) |
| 엔제리너스 | `channel/UCN728nR9XbzXICnHXUAvbbA` | **리아버거가게 = 롯데리아** | 없음 (직전 판단 유지) |
| 박가부대 | `channel/UCoAvbI-Z0Rw68q4NLbefGTA` | **원할머니 보쌈족발** | 없음 (직전 판단 유지) |
| 왓더버거 | `@ahn_teacher1` | **장사꾼안선생** 개인 채널 | 없음 (직전 판단 유지) |
| 더본코리아 13곳 | `channel/UCyn-K7rZLXjGl7VXGweIlcA` + `theborn_tasty`·`paikscoffee_official` | 창업자 개인 채널 / 본사·빽다방 계정 | 전부 없음 (직전 판단 유지) |

### ⚠️ 한 다리 건넌 것 — 읍천리382 인스타 (`eupcheonri_official`)

이 한 건만 "공식 사이트가 직접 건다"에 해당하지 않는다. 근거 사슬은 이렇다.

1. 공식 사이트 `읍천리382.com` 이 유튜브 `@eupcheonri_official` 을 건다.
2. 그 채널 소개가 **공식 도메인 `www.xn--382-v18me95c8ph.com` 을 되건다**(상호 확인 완료 → 공식 채널 확정).
3. 그 확정된 공식 채널이 소개에 `instagram.com/eupcheonri_official` 을 적어둔다.
4. 열어보니 `도심 속 시골농촌카페 읍천리382 공식 인스타그램` / 2.3만.

사이트가 직접 거는 건 케이터링 부계정(`eupcheonri_catering`)뿐이라 그쪽은 본계정이 아니다.
**기준을 넓힌 것이 마음에 걸리면 이 한 줄만 지우면 된다.** 나머지 46개는 전부 사이트 직접 링크다.
(`notes/YOUTUBE.md` 가 같은 이유로 보류한 **컴포즈커피**는 이번에도 손대지 않았다 — 거기는
공식 **인스타 소개**가 출처라 도메인 상호 확인이 없다.)

---

## 못 찾은 것 — 전부

**인스타 58곳 · 유튜브 101곳이 아직 비어 있다.** 사유별로 묶었다.
`(직전)` 은 2026-10-01·10-02 조사가 이미 같은 결론을 낸 곳이고, 이번에 다시 받아 **그대로임을 확인**했다.

### 공식 사이트에 SNS 링크가 아예 없다 — 인스타·유튜브 둘 다 없음
긴자료코`(직전)` · 돌배기집`(직전)` · 동서식품`(직전)` · 롤링파스타`(직전)` · 미미관마라탕`(직전)` ·
미정국수0410`(직전)` · 삼삼마라`(직전)` · 설빙`(직전)` · 역전우동0410`(직전)` · 오봉집`(직전)` ·
원조쌈밥집`(직전)` · 한신포차`(직전)` · 블루샥`(직전)` ·
**더플레이스 · 라벨리 · 빕스 · 송사부고로케 · 앤티앤스 · 요아정 · 제일제면소 · 카페봄봄 · 하이오커피** (이번 신규 확인)

> 더플레이스(`italiantheplace.co.kr`)·빕스(`ivips.co.kr`)·제일제면소(`cheiljemyunso.co.kr`) 는
> 루트가 200~230바이트짜리 빈 셸이다. `/menu` 쪽 본문(2.2만 바이트)까지 받아도 SNS 링크가 0건.

### 영상·게시물 임베드만 있고 계정 주소가 없다
- **김밥천국**`(직전)` — `youtu.be/<id>` 171개, 프로필 링크 0
- **미소야**`(직전)` — `youtube.com/watch?v=…` 다수, 채널 주소 없음
- **애플꼬마김밥**`(직전)` — `youtube.com/embed/…` 2개 (유튜브는 이미 들어가 있다)
- **담꾹**`(직전)` — 인스타 `/p/`·`/reel/` 게시물만
- **병아리김밥** (신규) — `youtube.com/embed/…` 3개 + 인스타 피드 위젯(`ul.instagram` 을 JS 로 채움)
- **하루엔소쿠**`(직전)` — 푸터 SNS 아이콘이 `href="#none"`, 본문 임베드는 JTBC 클립

### 아이콘은 있는데 주소가 비어 있다
김밥천국(`instagram.com/` 뿐)`(직전)` · 큰맘할매순대국(`href=""`)`(직전)` · 하루엔소쿠(`href="#none"`)`(직전)`

### 인스타 피드 API 주소만 있다
잇샌드`(직전)` — `graph.instagram.com/me/media` 호출 코드뿐, 핸들이 안 나온다

### JS 셸이라 원본 HTML 에 링크가 없다
- **SPC삼립**`(직전)` — Next.js. `Instagram`·`Youtube` 라는 **글자만** 있는 장식 버튼이고 `href` 가 없다
- **블루샥**`(직전)` — 루트 16만 바이트를 받아도 SNS 문자열 0건

### 사이트에 연결이 안 된다 (이번에 새로 막힌 곳 포함)
| 브랜드 | 증상 |
|---|---|
| 탐앤탐스 | `tomntoms.com` **인증서 검증 실패**. 직전 조사 때는 열렸다(인스타는 이미 등재) — 사이트 쪽 문제 |
| 모토이시 | `motoishi.co.kr` 인증서 검증 실패 (직전엔 열렸고 가리킨 계정이 삭제돼 있었다) |
| 벤슨 | `bensonicecream.com` 인증서 검증 실패 (http 도 https 로 리다이렉트) |
| 하삼동커피 | `hasamdongcoffee.com` **`DH_KEY_TOO_SMALL`** — 구형 TLS |
| 유가네 | `yoogane.co.kr` 서버가 응답 없이 연결을 끊는다 (http 는 reset) |
| 하림산업 | `harimholdings.com` 루트가 **43바이트 껍데기**, `SITES` 경로는 404 |

> ⚠️ 전부 `base.client()` 기본값(`verify=True`, UA 위장 없음) 기준이다.
> `verify=False` 를 쓰면 열릴 수 있지만 지시대로 쓰지 않았다. 다음에 볼 때는 사이트가
> 고쳐졌는지부터 확인하는 게 맞다.

### 모회사·자매 브랜드 계정뿐 — 걸면 틀린 링크가 된다
노브랜드버거(신세계푸드)`(직전)` · 엔제리너스(롯데리아)`(직전)` · 박가부대(원할머니)`(직전)` ·
고망고(지지커피 — 게다가 그 계정도 죽어 있다) · 하림산업(하림)

### 더본코리아 13곳 — 브랜드 페이지에 SNS 0건`(직전)`
고투웍 · 리춘시장 · 막이오름 · 백스비어 · 본가 · 빽보이피자 · 새마을식당 · 성성식당 ·
연돈볼카츠 · 인생설렁탕 · 제순식당 · 홍콩반점0410 · 홍콩분식
→ 본사 푸터가 거는 유튜브는 **백종원 개인 채널**, 인스타는 `theborn_tasty`(본사)·`paikscoffee_official`(빽다방).
브랜드 단위로 걸 수 있는 게 없다.

### 글로벌 계정만 가리킨다
파이브가이즈`(직전)` — `fiveguys.co.kr` 가 `instagram.com/fiveguys`·`@FiveGuysBurgersFries`(미국) 만 건다

### 브랜드별 계정만 있고 회사 계정이 없다
하이트진로`(직전)` — 참이슬·테라·켈리·진로·필라이트·일품진로·이슬톡톡·하이트 8개 계정뿐

### 본아이에프 브랜드
본흑염소·능이삼계탕 — `bonif.co.kr` 가 형제 브랜드 7개 인스타만 걸고 이 브랜드 전용 계정은 없다`(직전)`

### 인스타는 있는데 유튜브 링크만 없는 곳 (48곳)
공차 · 김밥킹 · 꾸브라꼬숯불치킨 · 나폴레옹과자점 · 노브랜드버거 · 노티드 · 달롱도르 · 달리는커피 ·
떡군이네떡볶이 · 뚜레쥬르 · 롯데웰푸드 · 마왕족발 · 매머드커피 · 매스커피 · 맥도날드 · 멕시카나 ·
미카도스시 · 버거운버거 · 브레댄코 · 빨라쪼 · 빽다방 · 사조대림 · 삼첩분식 · 소림마라 · 쉬즈베이글 ·
스쿨푸드 · 쏘자토스트 · 에밀리아젤라또 · 왓더버거 · 이삭토스트 · 죠스떡볶이 · 차얌 · 참토스트 ·
처갓집양념치킨 · 춘리마라탕 · 치킨플러스 · 카페인중독 · 커피베이 · 컴포즈커피 · 크라운제과 ·
탐앤탐스 · 태리로제떡볶이 · 텐퍼센트커피 · 팔공티 · 피자스쿨 · 할리스 · 홍익돈까스 · 홍짜장

→ 전부 공식 사이트에 유튜브 **채널** 링크가 없다. 맥도날드는 한국 사이트가 유튜브를 아예 안 건다
(글로벌 채널을 대신 넣지 않았다). 이 중 16곳(공차·김밥킹·달롱도르·달리는커피·떡군이네떡볶이·
뚜레쥬르·마왕족발·매스커피·빨라쪼·에밀리아젤라또·차얌·카페인중독·커피베이·태리로제떡볶이·
텐퍼센트커피·팔공티·피자스쿨)은 **이번에 인스타만 새로 채운 곳**이다.

### 유튜브는 있는데 인스타 링크만 없는 곳 (5곳)
모토이시`(직전, 계정 삭제)` · 미소야`(직전)` · 본흑염소·능이삼계탕`(직전)` · 애플꼬마김밥`(직전)` · 하이트진로`(직전)`

---

## 집계

| 항목 | 조사 전 | 조사 후 | 증감 |
|---|---:|---:|---:|
| 브랜드 전체 | 217 | 217 | — |
| ✅ 인스타 확보 | 127 | **159** | **+32** |
| ⚪ 인스타 없음 | 90 | 58 | −32 |
| ✅ 유튜브 확보 | 101 | **116** | **+15** |
| ⚪ 유튜브 없음 | 116 | 101 | −15 |
| 둘 다 없어 링크 줄이 안 나오는 브랜드 | 85 | **53** | −32 |
| SNS 줄이 하나라도 나오는 브랜드 | 132 | **164** | +32 |

**새로 넣은 47개 주소를 `social.links()` 가 만드는 형태 그대로 전부 GET 해서 200 + 브랜드 일치를 확인했다(실패 0건).**
인스타는 비로그인에서도 `og:description` 에 프로필명·팔로워 수가 그대로 나와 계정 주인을 확인할 수 있었다.

### 다음에 다시 볼 거리

- **사이트가 막힌 6곳**(탐앤탐스·모토이시·벤슨·하삼동커피·유가네·하림산업) — 인증서/TLS 문제라
  사이트가 고쳐지면 바로 다시 보면 된다. 특히 탐앤탐스는 직전 조사 때 열리던 곳이다.
- **컴포즈커피 기준 문제** — `notes/YOUTUBE.md` 가 남긴 숙제 그대로다. "공식 인스타 소개에 적힌
  유튜브"를 인정할지 정해지면 인스타만 있는 34곳을 한 번에 훑으면 된다.
- **읍천리382 인스타** — 위 "한 다리 건넌 것". 기준을 좁히기로 하면 이 줄만 지운다.
- **팔로워·구독자가 아주 적은 신규분** — 에밀리아젤라또 인스타 15명(게시물 3) · 33떡볶이 유튜브 188명 ·
  카페051 유튜브 101명 · 쥬씨 유튜브 421명 · 카페베네 유튜브 400명.
  전부 근거는 확실하지만 볼 게 거의 없다. 문턱을 둘지는 기존 방침(`근거가 있으면 넣는다`)대로 두었다.
