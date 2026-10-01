# 인스타그램 공식 계정 조사 (F11)

**조사 전용 문서. 코드는 건드리지 않았다.**
`collectors/base.py` 의 `BRANDS` 58곳 전부에 대해 공식 인스타 핸들을 근거와 함께 적는다.

## 왜 이 문서가 있나

`notes/FEATURE-PLAN-2.md` F11-3 이 이미 증명했다 — **브랜드명에서 핸들을 유추하면 30%만 맞는다.**
20개를 찍어봤더니 8개는 없는 계정, 4개는 **남의 개인 계정**(`ediya_coffee`→윤소연,
`bhc_chicken`→임방환, `bbq_chicken`→Jazhari Johnson, `orionworld`→Ajay Kaundal),
1개는 다른 법인(`emart24.official`→"이마트")이었다.
남의 개인 계정을 브랜드 공식인 양 링크하면 그 사람에게 실제 피해가 간다.

## 조사 방법 — 이 경로만 썼다

1. **브랜드 공식 홈페이지를 연다** (`base.SITES` 의 URL + 그 도메인 루트).
2. **그 사이트가 스스로 가리키는 instagram.com 링크만 딴다.** 푸터·헤더 SNS 아이콘,
   `schema.org/Organization` 의 `sameAs`, 푸터 SNS 버튼의 이동 결과.
   JS 로 그려지는 사이트(설빙·버거킹·GS리테일·롯데칠성)는 브라우저로 렌더해서 DOM 을 봤다.
3. **그 핸들을 실제로 비로그인으로 열어 확인한다** — 프로필명·소개·팔로워 수를 기록.

**구글 검색으로 찾은 것, 이름이 그럴듯한 것은 쓰지 않았다.**
공식 사이트가 안 가리키면 **"없음"** 이다. 추측은 한 건도 없다.

> ⚠️ 아래 "직접 열어본 결과" 의 팔로워 수는 2026-10-01 비로그인 조회 기준이다.

---

## 브랜드별 결과

### 메가MGC커피 — `mega.mgc.coffee_official` ✅
- **출처**: `mega-mgccoffee.com/menu/` 상단 SNS 아이콘 리스트.
  `<a href=".../mega.mgc.coffee_official/"><img src=".../sns_instagram.png"></a>`
  (같은 줄에 네이버블로그·페이스북·스마트스토어 아이콘)
- **열어본 결과**: 프로필명 **메가MGC커피** / `메가MGC커피 공식 인스타그램☕ 💛MEGA Taste MEGA Smile💛` / **팔로워 8.8만**
- 하이라이트 `DRAW_TODAY`·`PLAY_TODAY`·`MGC X 127`

### 스타벅스 — `starbuckskorea` ✅
- **출처**: `starbucks.co.kr` 푸터 `<footer>` 안 SNS 메뉴 `<a ...>인스타그램</a>` +
  `<span itemscope itemtype="schema.org/Organization">` 의 `sameAs` (연관채널 선언). **두 곳 일치.**
- **열어본 결과**: 프로필명 **스타벅스 코리아** / `The Starbucks Coffee Company` / **팔로워 101.7만**
- 하이라이트 `What's New`·`Promotion`·`RESERVE`

### 이디야커피 — `ediya.coffee` ✅
- **출처**: `ediya.com` 의 `schema.org/Organization` 연관채널 블록(주석 `<!-- 이디야 연관채널 2022.05.03-->`)
  안 `<a itemprop="sameAs" href=".../ediya.coffee/">`
- **열어본 결과**: 프로필명 **이디야커피 EDIYA COFFEE** / `대한민국 대표 커피 브랜드 ☕️ 언제나 당신 곁에` / **팔로워 21.1만**
- 🔴 **기획 문서가 찍었던 `ediya_coffee`(언더바)는 남의 개인 계정이었다. 정답은 점(`.`) 이다.**
  한 글자 차이로 일반인에게 피해가 가는 사례 — 이 조사의 존재 이유.

### 설빙 — **없음**
- **확인한 곳**: `sulbing.com/` (3,009 bytes) 와 `sulbing.com/menu/` (14,203 bytes) 원본 HTML,
  그리고 브라우저 렌더 후 DOM(`scrollHeight 4134`) 까지.
- **결과**: `instagram`·`facebook`·`youtube`·`blog.naver` **어느 SNS 링크도 한 건도 없다.**
  외부 링크는 `brand.naver.com/sulbing`(스마트스토어)·`mgift.coopnc.com`(기프티콘) 둘뿐.
- → 공식 사이트가 가리키지 않으므로 **없음**. 링크를 달지 않는다.

### 빽다방 — `paikscoffee_official` ✅
- **출처**: `paikdabang.com` 헤더 유틸 메뉴의 SNS 아이콘 `<li class="sns i"><a href=".../paikscoffee_official/">instagram</a></li>`
  (바로 옆 `<li class="sns f">` 는 페이스북 `ipaikscoffee`)
- **열어본 결과**: 프로필명 **빽다방** / `🎊축💥빽다방 20주년🎊 스페셜한 신메뉴 6종 출시` / **팔로워 9.2만**
- 하이라이트에 **`⚠️사칭주의⚠️`** 가 있다 — 사칭 계정이 실제로 돌아다닌다는 뜻이고, 추측 금지 원칙을 뒷받침한다.
- 참고: 기획 문서가 🟢로 적었던 `paikdabang` 이 아니다. 공식 사이트는 `paikscoffee_official` 을 가리킨다.

### 커피빈 — `coffeebean_kr` ✅ (🟠 함정 있었음)
- **출처**: `coffeebeankorea.com/menu/list.asp` 푸터 SNS 아이콘
  `<a href=".../coffeebean_kr/" class="ico_instagram">INSTAGRAM</a>`
- **열어본 결과**: 프로필명 **커피빈코리아** / `☕️대한민국에선 커피빈 커피가 가장 맛있습니다.` / **팔로워 3.8만**
- 🟠 **같은 HTML 안에 `coffeebeankorea` 도 있는데 `<!-- -->` 주석 처리된 죽은 블록이다.**
  실제로 열어보니 **"Profile을(를) 이용할 수 없습니다"** — 존재하지 않는 계정이었다.
  **주석 안 링크를 쓰면 안 된다**는 사례. 살아있는 아이콘 쪽(`coffeebean_kr`)이 정답.

### 폴바셋 — `paulbassettkorea` ✅
- **출처**: `baristapaulbassett.co.kr` 푸터 `<div class="footSns">` 의
  `<a ... class="instagram"><span>인스타그램</span></a>`
- **열어본 결과**: 프로필명 **폴 바셋 공식 인스타그램** / `취향을 담는 시간, 폴 바셋☕` / **팔로워 6.9만**

### CU — `cu_official` ✅
- **출처**: `cu.bgfretail.com` `<footer>` 안 SNS 아이콘 리스트
  `<a href=".../cu_official"><img src="/images/common/new/footer_instagram.png" alt="Instagram"></a>`
- **열어본 결과**: 프로필명 **CU** / `Daily Variety, CU — 제일 먼저 만나는 편의점 트렌드💜` / **팔로워 74.5만**
- 하이라이트 `CU소식`·`CU로운혜택`·**`신상트렌드`** — 이 프로젝트 용건과 정확히 겹친다.

### 세븐일레븐 — `7elevenkorea` ✅
- **출처**: `7-eleven.co.kr` 의 SNS 블록 `<a href=".../7elevenkorea/" class="social insta">인스타그램</a>`
- 🟠 **주의**: 이 블록은 `<!-- ... -->` 로 감싸진 자리에도 같은 핸들이 있다(지금은 화면에 안 보이는 구 마크업).
  다만 **주석 밖 살아있는 자리에도 같은 `7elevenkorea`** 가 있어 값 자체는 흔들리지 않는다.
- **열어본 결과**: 프로필명 **세븐일레븐ㅣ7-Eleven Korea** / `Taste the world at 7eleven🌏 전 세계 맛있는 유행은 세븐에서` / **팔로워 66.9만**
- 기획 문서가 ⚪없는 계정으로 적었던 `7eleven_korea`(언더바)와 다르다. 언더바가 없는 쪽이 정답.

### 이마트24 — `emart24_official` ✅
- **출처**: `emart24.co.kr` 푸터 `<div class="instaIcon"><a href=".../emart24_official/"><img alt="인스타"></a></div>`
  \+ 같은 페이지 `schema.org/Organization` 의 `sameAs`. **두 곳 일치.**
- **열어본 결과**: 프로필명 **이마트24 | emart24** / `퀄리티 있는 라이프는 여기서 🏠✨ #ALLDAYHIGHLIGHT` / **팔로워 36.2만**
- 🔴 기획 문서가 🟠"다른 법인(이마트)"로 적었던 `emart24.official`(점)과 **다른 계정**이다.
  공식 사이트가 가리키는 건 언더바 `emart24_official` 이고, 이쪽이 진짜 이마트24다.
  참고로 점 버전 `emart24.official` 은 이마트24 **페이스북** 주소로 사이트에 적혀 있다 — 플랫폼이 다르다.

### GS25 — `gs25_official` ✅
- **출처**: `gsretail.com/brand/gs25` (본사 사이트의 GS25 브랜드 페이지) 의 외부 링크.
  `https://www.instagram.com/gs25_official` 이 `https://www.youtube.com/@official_GS25` 와 나란히 있다.
- 🟠 `base.SITES` 에 등록된 `gsretail.com/news/press-releases` 와 사이트 루트에는 **SNS 링크가 없다.**
  브랜드 페이지까지 들어가야 나온다(브라우저 렌더 필요 — Nuxt SPA 라 원본 HTML 은 906 bytes 껍데기).
- **열어본 결과**: 프로필명 **대한민국 대표 편의점 GS25** / `더 재미있게 더 실속있게 #25매거진` / **팔로워 101.8만**
- 하이라이트 **`신상앨범`**·`이벤트`·`카페25`

### 맘스터치 — `momstouch.love` ✅
- **출처**: `momstouch.co.kr` 푸터 SNS (`<footer>` 안쪽 + 머리쪽 선언 양쪽)
- **열어본 결과**: 프로필명 **맘스터치** / `대한민국 No.1 치킨&버거 맘스터치🍔` / **팔로워 9만**
- 기획 문서의 ⚪`momstouch_official` 이 아니라 **점 + `love`** 다. 절대 못 유추할 핸들.

### 버거킹 — `burgerkingkorea` ✅
- **출처**: `burgerking.co.kr` 푸터 SNS 버튼. 🟠 **`<a href>` 가 아니라 `<button class="btn_sns_insta">`**
  (Vue/Ionic SPA) 라서 HTML 긁기로는 안 잡힌다. **푸터의 그 버튼을 실제로 눌러서** 이동한 주소로 확인했다.
- **열어본 결과**: 프로필명 **버거킹코리아 공식 인스타그램** / `올가을 뉴~해진 트머와 🍂🍁` / **팔로워 12.4만**
- 하이라이트 `New`·`Menu`·`Promotion`

### BBQ — `bbq_offi` ✅
- **출처**: `bbq.co.kr` SNS 링크
- **열어본 결과**: 프로필명 **비비큐 (BBQ)** / `🍗세상에 없던 단짠! 바삭! 필크런치🍗` / **팔로워 9.6만**
- 🔴 기획 문서에서 **`bbq_chicken` → Jazhari Johnson(남의 개인 계정)** 이었던 바로 그 자리다.
  정답은 `bbq_offi` — `_official` 도 아니고 중간에서 잘린 `offi` 다. **유추 불가의 교과서.**

### bhc치킨 — `bhc_chicken_official` ✅
- **출처**: `bhc.co.kr` `<footer>` 안 SNS 아이콘
- **열어본 결과**: 프로필명 **bhc치킨 공식 인스타그램** / `bhc 치킨 주문하러 가기🍗` / **팔로워 7.4만**
- 🔴 기획 문서의 **`bhc_chicken` → 임방환(개인)** 과 `_official` 하나 차이다.

### 교촌치킨 — `kyochon_official` ✅
- **출처**: `kyochon.com` SNS 링크
- **열어본 결과**: 프로필명 **교촌치킨** / `월간우석 디지털 포토카드 다운받기⬇️` / **팔로워 6.9만**

### 피자헛 — `pizzahutkorea` ✅
- **출처**: `pizzahut.co.kr` SNS 링크
- **열어본 결과**: 프로필명 **피자헛 공식 인스타그램** / `함께 즐겨요 피자헛 ;)` / **팔로워 6.7만**

### 미스터피자 — `mrpizza_official_` ✅ (🟠 팔로잉 수가 특이)
- **출처**: `mrpizza.co.kr` `<footer>` 안 SNS 아이콘
- **열어본 결과**: 프로필명 **미스터피자** / `🚫미스터피자 계정 사칭주의🚫` / **팔로워 3.5만**
- 🟠 **팔로잉이 4,759** 로 브랜드 계정치고 비정상적으로 많다(보통 한 자릿수). 다만
  ① 공식 사이트 푸터가 이 계정을 가리키고 ② 프로필명이 미스터피자이며
  ③ 바이오·하이라이트가 **사칭 주의**를 직접 공지한다 → **공식으로 판정.**
  핸들 끝의 **언더바(`_`)가 붙는다**는 점이 함정 — 빼면 다른 계정이 된다.

### 파파존스 — `papajohnskr` ✅
- **출처**: `pji.co.kr` SNS 링크
- **열어본 결과**: 프로필명 **파파존스** / `Better Ingredients, Better Pizza🍕` / **팔로워 3.2만**

### 도미노피자 — `dominostory` ✅
- **출처**: `dominos.co.kr` 푸터 SNS (`<footer>` 안 + 머리쪽 선언 양쪽)
- **열어본 결과**: 프로필명 **도미노피자 공식 인스타그램** / `❗사칭 계정에 주의하세요❗` / **팔로워 34.5만**
- 기획 문서의 ⚪`dominos_korea` 가 아니다. **브랜드명이 전혀 안 들어간 `dominostory`.**

### 굽네치킨 — `the___goobster` ✅
- **출처**: `goobne.co.kr` 푸터 SNS (`<footer>` 안 + 머리쪽 선언 양쪽)
- **열어본 결과**: 프로필명 **굽네 공식_THE 굽스터** / `Goobne, Korea's No.1 Oven-Roasted Chicken Brand` / **팔로워 35.5만**
- **언더바 3개** 짜리 핸들. 사람이 손으로 옮겨 적다가 틀리기 딱 좋다 — 복붙만 할 것.

### 프랭크버거 — `frankburger_official_` ✅
- **출처**: `frankburger.co.kr` SNS 링크
- **열어본 결과**: 프로필명 **프랭크버거 공식 인스타그램** / `🇰🇷 대한민국 No.1 수제 버거 브랜드` / **팔로워 2.3만**
- 끝에 **언더바가 붙는다**(`..._official_`). 미스터피자와 같은 함정.

### 맥도날드 — `mcdonalds_kr` ✅
- **출처**: `mcdonalds.co.kr` SNS 링크
- **열어본 결과**: 프로필명 **맥도날드(McDonald's)** / `매니저 채용 진행 중(~10/11)` / **팔로워 32.8만**

### 오뚜기 — `otoki_daily` ✅
- **출처**: `otoki.com` 푸터 SNS (`<footer>` 안 + 머리쪽 선언 양쪽)
- **열어본 결과**: 프로필명 **오뚜기** / `💛오뚜기 공식 인스타그램` / **팔로워 16.5만**
- 바이오가 **공식 계정 목록을 직접 밝힌다**: `@otoki_daily @otoki_plate @otoki.noodle.zip
  @okitchen_studio @otoki_global (사칭 계정 주의)`. 대표 계정은 `otoki_daily`.
- 기획 문서의 ⚪`ottogi_official` 이 아니다. 로마자 표기부터(`otoki`) 다르다.

### 팔도 — `paldofood` ✅
- **출처**: `paldofood.co.kr` 푸터 SNS (`<footer>` 안 + 머리쪽 선언 양쪽)
- **열어본 결과**: 프로필명 **팔도** / `💙2026 PALDO FOOD💙 #PALDO official account` / **팔로워 22만**
- 하이라이트에 **`팔도신상`**·`사칭계정` 이 있다.

### 오리온 — `orion_world` ✅
- **출처**: `orionworld.com` `<footer>` 안 SNS 아이콘
- **열어본 결과**: 프로필명 **오리온** / `맛있는 선물이 가득한 오리온💝` / **팔로워 13.7만**
- 🔴 기획 문서의 **`orionworld` → Ajay Kaundal(남의 개인 계정)**.
  **언더바 하나 차이**(`orion_world`)로 갈린다. 홈페이지 도메인이 `orionworld.com` 이라
  도메인에서 핸들을 유추하면 정확히 그 개인 계정으로 간다 — 가장 위험한 케이스.

### 롯데칠성음료 — **없음**
- **확인한 곳**: `company.lottechilsung.co.kr` (브라우저 렌더, `<a>` **277개 전부 확인**).
  `SITES` 의 `/kor/product/newprdt/list.do` 는 httpx 로는 TLS 체인 오류라 브라우저로 봤고,
  `/kor/main.do` 는 404 이며 실제 메인은 `/kor/main/index.do` 다.
- **결과**: **instagram 링크 0건.** 외부 SNS 는 `blog.naver.com/ilovemirim`(네이버 블로그) 하나뿐.
  나머지 외부 링크는 롯데칠성몰·채용·IR·ISMS 인증 확인 등.
- → **없음.** (소비자 브랜드 계정이 따로 있을 수는 있으나 **공식 사이트가 가리키지 않으므로 쓰지 않는다.**)

### hy프레딧 — `hy.official.kr` 🟠 **확인됐지만 브랜드 전용 계정이 아니다**
- **출처**: `m.fredit.co.kr` 의 SNS 링크
- **열어본 결과**: 프로필명 **hy(한국야쿠르트)** / `대한민국 대표 프로바이오틱스 기업 hy` / **팔로워 7.3만**
- 🟠 **계정 주체가 "hy 법인"이지 "프레딧(쇼핑몰 브랜드)"이 아니다.**
  프로필 링크가 `litt.ly/hy.fredit_official` 인 걸 보면 프레딧 전용 채널이 따로 있을 가능성이 있지만,
  **공식 사이트가 가리키는 건 이 계정뿐**이라 이것만 근거가 있다.
  → 쓰려면 **계정명(`hy(한국야쿠르트)`)을 그대로 노출**해서 사용자가 "프레딧 계정"으로 오해하지 않게 해야 한다.
  오해 소지가 걸리면 **안 다는 쪽**을 권한다.

### 배스킨라빈스 — `baskinrobbinskorea` ✅
- **출처**: `baskinrobbins.co.kr` `<footer>` 안 SNS 아이콘
- **열어본 결과**: 프로필명 **배스킨라빈스🍦** / `배라의 행복한 이야기를 맛보세요!` / **팔로워 74.7만**
- 하이라이트 **`이달의 맛`**·**`NEW`** — 신상 용건과 맞는다.

### 던킨 — `dunkin_kr` ✅
- **출처**: `dunkindonuts.co.kr` `<footer>` 안 SNS 아이콘
- **열어본 결과**: 프로필명 **던킨** / `잠깐의 여유와 달콤한 행복! Welcome to Dunkin' Korea Instagram!` / **팔로워 42.6만**
- 하이라이트 **`던킨 신상`**. 기획 문서의 ⚪`dunkinkorea` 가 아니라 `dunkin_kr`.
