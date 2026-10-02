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
- 🔴 **2026-10-02 정정: 없음이 아니었다.** `SITES` 주소를 httpx 로 다시 받아보니
  푸터에 라벨 붙은 SNS 목록이 있다 → `lottechilsung`. 아래 "2026-10-02 보강" 참고.

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

### 이삭토스트 — `isaactoast.official` ✅
- **출처**: `isaac-toast.co.kr` SNS 링크
- **열어본 결과**: 프로필명 **이삭토스트** / `Enjoy sweet day, isaac toast🥪` / **팔로워 2.7만**

### 파리바게뜨 — `parisbaguette_kr` ✅
- **출처**: `paris.co.kr` 푸터 SNS (`<footer>` 안 + 머리쪽 선언 양쪽)
- **열어본 결과**: 프로필명 **파리바게뜨** / `파리바게뜨의 다양한 소식을 만나보세요!💙` / **팔로워 18.2만**
- 기획 문서의 🟢`paris_baguette` 가 아니다. 공식 사이트는 `parisbaguette_kr` 를 가리킨다.

### 나폴레옹과자점 — `napoleon.bakery` ✅ (팔로워 적음 — 정상)
- **출처**: `napoleonbakery.co.kr` SNS 링크
- **열어본 결과**: 프로필명 **나폴레옹과자점** / `📍since 1968; 50년을 이어가는 베이커리 / 성북본점은 백년가게·서울미래유산` / **팔로워 5,846**
- 🟠 팔로워가 수천 명대지만 **의심 근거가 아니다** — 서울 소수 직영점 제과점이고,
  바이오가 창업연도·본점 위치·로고 식별법(`보라색 소문자 로고를 확인해주세요`)까지 밝힌다.
  공식 사이트가 직접 가리킨다. **확인 완료로 본다.**

### 브레댄코 — `breadnco_kr` ✅
- **출처**: `breadnco.kr` SNS 링크
- **열어본 결과**: 프로필명 **브레댄코 공식 인스타그램** / `"Feel light, alright"` / **팔로워 1.2만**

### 홍루이젠 — `hungruichenkorea` ✅
- **출처**: `hongruizhen.com` SNS 링크
- **열어본 결과**: 프로필명 **홍루이젠** / `낮은 칼로리에 든든한 풍성함! 홍루이젠` / **팔로워 1.7만**
- 🟠 **도메인 로마자(`hongruizhen`)와 핸들 로마자(`hungruichen`)가 다르다.**
  도메인에서 유추하면 틀린다.

### 노티드 — `cafeknotted_kr` ✅
- **출처**: `knottedstore.com` SNS 링크
- **열어본 결과**: 프로필명 **Knotted 노티드** / `달콤한 행복을 전하는 카페 노티드 / From Seoul to LA & Sydney` / **팔로워 12.7만**

### 삼송빵집 — `samsong_bakery` ✅ (계정 2개 중 선택)
- **출처**: `ssbnc.kr` 푸터 `<ul class="ft-sns">`. **푸터가 두 계정에 라벨을 붙여놨다:**
  - `<a href=".../samsong_bakery"><p>삼송빵집</p></a>` ← **브랜드 계정**
  - `<a href=".../samsong1957"><p>삼송1957</p></a>` ← 별개 매장(대구 수성못 카페)
- **열어본 결과(`samsong_bakery`)**: 프로필명 **삼송빵집** / `삼송빵집 공식 인스타그램입니다. #통옥수수빵 #마약빵` /
  **팔로워 9,137**, 바이오에 `www.ssbnc.kr` 를 걸어 **사이트↔계정 상호 확인**됨. 하이라이트 `🚨사칭 주의🚨`
- **열어본 결과(`samsong1957`)**: 프로필명 **𝕊𝔸𝕄𝕊𝕆ℕ𝔾 𝟙𝟡𝟝𝟟 수성못 카페** / 팔로워 2,584 →
  빵집 브랜드가 아니라 **대구 수성못 카페 지점 계정**이므로 `BRANDS["삼송빵집"]` 에는 쓰지 않는다.

---

## 본아이에프(bonif.co.kr) 8개 브랜드 — 푸터가 **브랜드↔핸들 대응표**를 직접 제공한다

`본죽`·`본죽&비빔밥`·`본도시락`·`본설렁탕`·`본우리반상`·`멘지`·`본흑염소·능이삼계탕`·`이지브루잉커피`
는 모두 같은 사이트(`bonif.co.kr`)를 쓴다. 이 사이트 푸터의 인스타 아이콘에 마우스를 올리면
**툴팁(`<div class="tooltip">`)이 브랜드명과 핸들을 한 줄씩 짝지어 보여준다** — 추측할 필요가 없다.

```
<li><a href=".../bonjukofficial/">본죽</a></li>
<li><a href=".../bonjukofficial/">본죽&비빔밥</a></li>      ← 본죽과 같은 계정
<li><a href=".../bondosirak_official/">본도시락</a></li>
<li><a href=".../bonseol_official/">본설렁탕</a></li>
<li><a href=".../bonwoori_official/">본우리반상 </a></li>
<li><a href=".../ramen_menji/">멘지</a></li>
<!-- 2026-07-10 추가 (s) -->
<li><a href=".../easybrewingcoffee/">이지브루잉커피</a></li>
<li><a href=".../easywhitebread_official/">이지화이트브레드</a></li>   ← 우리 BRANDS 에 없는 브랜드
<!-- 2026-07-10 (e) -->
```

**이 표에 `본흑염소·능이삼계탕` 은 없다.** 브랜드 페이지(`brdCd=BF113`)에도 전용 계정 링크가 없다.

### 본죽 — `bonjukofficial` ✅
- **출처**: 위 푸터 툴팁의 `본죽` 행
- **열어본 결과**: 프로필명 **본죽 공식 인스타그램** / `신메뉴부터 이벤트까지, 본죽의 다양한 소식` / **팔로워 3.5만**

### 본죽&비빔밥 — `bonjukofficial` 🟠 **본죽과 같은 계정**
- **출처**: 위 푸터 툴팁의 `본죽&비빔밥` 행 — **본사가 의도적으로 같은 계정을 가리킨다.**
- **열어본 결과**: 프로필명 **본죽 공식 인스타그램** / 팔로워 3.5만
- 🟠 `/b/본죽&비빔밥/` 에 달면 **"본죽" 계정**이 열린다. 전용 계정이 없는 게 맞지만,
  링크 텍스트에 계정명(`본죽 공식 인스타그램`)을 그대로 노출해야 어긋남이 없다.

### 본도시락 — `bondosirak_official` ✅
- **출처**: 위 푸터 툴팁의 `본도시락` 행
- **열어본 결과**: 프로필명 **본도시락** / `⤹본도시락 이벤트 모아보기🎉` / **팔로워 5.3만**, 하이라이트에 **`신메뉴`**

### 본설렁탕 — `bonseol_official` ✅
- **출처**: 위 푸터 툴팁의 `본설렁탕` 행
- **열어본 결과**: 프로필명 **본설렁탕(본가네국밥)** / `이열치열🔥삼계탕&콩국수 여름 특선 할인!` / **팔로워 6,479**
- 바이오 링크가 `www.bonif.co.kr/event/detail?...&brdCd=BF105` — **BF105 는 `SITES["본설렁탕"]` 의 코드와 일치.** 교차 확인됨.

### 본우리반상 — `bonwoori_official` ✅ (팔로워 321 — 근거는 확실)
- **출처**: 위 푸터 툴팁의 `본우리반상` 행
- **열어본 결과**: 프로필명 **본우리반상** / `본죽의 24년 노하우를 담은 프리미엄 한식 브랜드, 본우리반상` / **팔로워 321**
- 🟠 팔로워 321명. 다만 ① 본사 사이트가 라벨까지 붙여 가리키고 ② 프로필명·소개가 정확히 그 브랜드고
  ③ 바이오에 본사 이벤트 URL 이 걸려 있다 → **공식 맞다. 다만 링크해도 볼 게 거의 없다**(아래 "내 의견" 참고).

### 멘지 — `ramen_menji` ✅
- **출처**: 위 푸터 툴팁의 `멘지` 행
- **열어본 결과**: 프로필명 **멘지 MENJi** / `🍜토리파이탄 라멘으로 떠나는 미식 여행 🐓Since 2019` / **팔로워 2,572**

### 본흑염소·능이삼계탕 — **없음**
- **확인한 곳**: `bonif.co.kr` 푸터 브랜드↔핸들 대응표(위 8줄) 와 브랜드 페이지 `brdCd=BF113`.
- **결과**: 대응표에 **이 브랜드만 빠져 있다.** 다른 7개 브랜드는 전부 들어있는데 이것만 없다 →
  본사가 아직 계정을 안 만들었거나 사이트에 안 걸었다는 뜻. **없음.**

### 이지브루잉커피 — `easybrewingcoffee` ✅ (팔로워 155 — 근거는 확실)
- **출처**: 위 푸터 툴팁의 `이지브루잉커피` 행 (`<!-- 2026-07-10 추가 -->` 로 최근 등록됨)
- **열어본 결과**: 프로필명 **이지브루잉커피** / `Good Price, Special Barista / Easy Brewing Coffee` / **팔로워 155**
- 🟠 **팔로워 155명.** 본사가 2026-07-10 에 직접 추가한 링크라 계정 진위는 확실하지만,
  **사용자에게 보여줄 가치는 거의 없다.** 신생 브랜드라 게시물도 적다.

---

### 요거프레소 — `yogerpresso_official` ✅
- **출처**: `yogerpresso.co.kr` `<footer>` 안 SNS 아이콘
- **열어본 결과**: 프로필명 **요거프레소** / `𝘔𝘌𝘙𝘙𝘠 𝘈𝘜𝘛𝘜𝘔𝘕 🍂` / **팔로워 3만**, 하이라이트 `NEW`

### 매머드커피 — `mmthcoffee` ✅
- **출처**: `mmthcoffee.com` SNS 링크
- **열어본 결과**: 프로필명 **매머드커피 (MAMMOTH COFFEE)** / `TAKE MORE, PAY LESS` / **팔로워 3.5만**
- 하이라이트 `NEW🔔`·`⚠️사칭주의`

### 더벤티 — `theventi_official` ✅
- **출처**: `theventi.co.kr` 푸터 SNS (`<footer>` 안 + 머리쪽 선언 양쪽)
- **열어본 결과**: 프로필명 **더벤티 공식 계정(theVenti)** / `한 잔을 마셔도 알차게, 더벤티💜` / **팔로워 5.9만**
- 하이라이트 **`더벤티 신메뉴`**·`🚨사칭 계정 주의🚨`

### 컴포즈커피 — `compose_coffee` ✅ 🔴 **기획 문서가 틀렸던 자리**
- **출처**: `composecoffee.com/index1` 푸터·헤더 `<ul class="sns-ul">` 의
  `<a href=".../compose_coffee/"><i class="fa-brands fa-instagram"></i></a>` (**세 군데 전부 같은 값**)
- **열어본 결과**: 프로필명 **컴포즈커피** / `'커피를 커피답게' 컴포즈커피 공식 인스타그램` / **팔로워 28.5만**
- 🔴 **기획 문서(F11-3)가 🟢맞음으로 적은 `composecoffee`(언더바 없음)를 직접 열어봤더니
  팔로워 269명 / 팔로잉 762명의 별개 계정**이었다. 프로필명 `COMPOSE COFFEE`,
  소개는 `벤티사이즈, 대용량커피창업, 커피 프랜차이즈, 카페창업...` — **창업 홍보용 구 계정**으로 보인다.
  **"확인했다"고 적힌 6건 중에도 틀린 게 있었다**는 뜻이다. 전수 재확인이 필요했던 이유.

### 할리스 — `official_hollys` ✅
- **출처**: `hollys.co.kr` SNS 아이콘 `<a href=".../official_hollys/"><img alt="인스타그램"></a>`
- **열어본 결과**: 프로필명 **할리스 공식 인스타그램** / `일상의 즐거움을 만나보세요!` / **팔로워 9.2만**
- 기획 문서의 🟢`hollys_coffee` 가 아니라 **`official_hollys`**(접두사가 앞에 온다).

### 김밥천국 — **없음** (아이콘은 있는데 **주소가 비어 있다**)
- **확인한 곳**: `kimbab1009.com` 원본 HTML(677KB) + 브라우저 렌더 후 DOM.
- **결과**: 인스타 링크가 **`http://instagram.com/` 딱 이것뿐 — 핸들이 없다.**
  푸터에 아이콘은 달아놨는데 주소를 안 채운 상태다(imweb 템플릿 기본값으로 보인다).
- → **없음.** 핸들이 없으니 추측할 거리조차 없다.

### 바르다김선생 — **없음** (🔴 공식 사이트가 가리키는 계정이 **죽어 있다**)
- **확인한 곳**: `teacherkim.co.kr` 푸터 `<div class="sns">`
  `<a href="https://www.instagram.com/teacherkim_insta/"><img alt="인스타그램 바로가기"></a>`
  (브라우저 렌더 DOM 으로도 같은 주소 확인. 옆에 트위터 `teacherkim_t`·페이스북 `KimTeacher2013` 도 있다.)
- **열어본 결과**: **"Profile을(를) 이용할 수 없습니다 — 링크가 잘못되었거나 프로필이 삭제되었을 수 있습니다."**
  (시간 두고 2회 재시도, 동일)
- → **출처는 확실하지만 계정이 없어졌다. 링크를 달면 사용자가 깨진 페이지로 간다 → "없음" 처리.**
- 🟠 **이 사례가 "출처 확인만으로는 부족하다"는 증거다.** 공식 사이트가 가리켜도 **실제로 열어봐야** 안다.

### 죠스떡볶이 — `jaws__official` ✅
- **출처**: `jawsfood.co.kr` SNS 링크
- **열어본 결과**: 프로필명 **죠스떡볶이 공식 인스타그램** / `죠스는 언제나 즐겁습니다❤️` / **팔로워 8,506**
- **언더바 2개**(`jaws__official`). 굽네(`the___goobster`, 3개)와 같은 함정.

### 명랑핫도그 — `myungranghotdog_official` ✅
- **출처**: `myungranghotdog.com` 푸터 SNS (`<footer>` 안 + 머리쪽 선언 양쪽)
- **열어본 결과**: 프로필명 **명랑핫도그 공식 채널** / `🧀모짜렐라에 체다치즈를 더한... 명랑's 더블치즈스틱` / **팔로워 4.7만**

### 스시로 — `sushiro_korea` ✅
- **출처**: `sushiro.co.kr` 푸터 SNS (`<footer>` 안 + 머리쪽 선언 양쪽)
- **열어본 결과**: 프로필명 **스시로한국(Sushiro Korea)** / `🍣"맛있는 스시를 배부르게!"🍣` / **팔로워 3만**

### 에그드랍 — `eggdrop.official` ✅
- **출처**: `eggdrop.co.kr` `<footer>` 안 SNS 아이콘
- **열어본 결과**: 프로필명 **EGGDROP 에그드랍** / `Everyday Better 🥚 PREMIUM EGG SANDWICH 🥪` / **팔로워 4.1만**

### 써브웨이 — `subwaykorea` ✅
- **출처**: `subway.co.kr` SNS 링크
- **열어본 결과**: 프로필명 **써브웨이** / `맛있게 먹기만 해도, 단백질이 따라오는 프로틴 시리즈 3종💪` / **팔로워 6.7만**

### 샐러디 — `saladykorea` ✅
- **출처**: `salady.com` SNS 링크
- **열어본 결과**: 프로필명 **샐러디** / `내가 좋아지는 한 끼, 샐러디` / **팔로워 2.9만**

---

## 전체 표 (복붙용)

`collectors/base.py` 의 `BRANDS` 순서 그대로다. **핸들은 반드시 이 표에서 복붙할 것** —
언더바 개수(`the___goobster` 3개, `jaws__official` 2개)와 끝 언더바(`mrpizza_official_`,
`frankburger_official_`), 점/언더바 구분(`ediya.coffee` vs `ediya_coffee`)이 전부 함정이다.

| # | 브랜드 | 핸들 | 상태 | 프로필명 | 팔로워 |
|---:|---|---|:--:|---|---:|
| 1 | 메가MGC커피 | `mega.mgc.coffee_official` | ✅ | 메가MGC커피 | 8.8만 |
| 2 | 스타벅스 | `starbuckskorea` | ✅ | 스타벅스 코리아 | 101.7만 |
| 3 | 이디야커피 | `ediya.coffee` | ✅ | 이디야커피 EDIYA COFFEE | 21.1만 |
| 4 | 설빙 | — | ⚪ 없음 | | |
| 5 | 빽다방 | `paikscoffee_official` | ✅ | 빽다방 | 9.2만 |
| 6 | 커피빈 | `coffeebean_kr` | ✅ | 커피빈코리아 | 3.8만 |
| 7 | 폴바셋 | `paulbassettkorea` | ✅ | 폴 바셋 공식 인스타그램 | 6.9만 |
| 8 | CU | `cu_official` | ✅ | CU | 74.5만 |
| 9 | 세븐일레븐 | `7elevenkorea` | ✅ | 세븐일레븐ㅣ7-Eleven Korea | 66.9만 |
| 10 | 이마트24 | `emart24_official` | ✅ | 이마트24 \| emart24 | 36.2만 |
| 11 | GS25 | `gs25_official` | ✅ | 대한민국 대표 편의점 GS25 | 101.8만 |
| 12 | 맘스터치 | `momstouch.love` | ✅ | 맘스터치 | 9만 |
| 13 | 버거킹 | `burgerkingkorea` | ✅ | 버거킹코리아 공식 인스타그램 | 12.4만 |
| 14 | BBQ | `bbq_offi` | ✅ | 비비큐 (BBQ) | 9.6만 |
| 15 | bhc치킨 | `bhc_chicken_official` | ✅ | bhc치킨 공식 인스타그램 | 7.4만 |
| 16 | 교촌치킨 | `kyochon_official` | ✅ | 교촌치킨 | 6.9만 |
| 17 | 피자헛 | `pizzahutkorea` | ✅ | 피자헛 공식 인스타그램 | 6.7만 |
| 18 | 미스터피자 | `mrpizza_official_` | ✅ | 미스터피자 | 3.5만 |
| 19 | 파파존스 | `papajohnskr` | ✅ | 파파존스 | 3.2만 |
| 20 | 도미노피자 | `dominostory` | ✅ | 도미노피자 공식 인스타그램 | 34.5만 |
| 21 | 굽네치킨 | `the___goobster` | ✅ | 굽네 공식_THE 굽스터 | 35.5만 |
| 22 | 프랭크버거 | `frankburger_official_` | ✅ | 프랭크버거 공식 인스타그램 | 2.3만 |
| 23 | 맥도날드 | `mcdonalds_kr` | ✅ | 맥도날드(McDonald's) | 32.8만 |
| 24 | 오뚜기 | `otoki_daily` | ✅ | 오뚜기 | 16.5만 |
| 25 | 팔도 | `paldofood` | ✅ | 팔도 | 22만 |
| 26 | 오리온 | `orion_world` | ✅ | 오리온 | 13.7만 |
| 27 | 롯데칠성음료 | `lottechilsung` | 🔴 정정 | 롯데칠성음료 | 5.9만 |
| 28 | hy프레딧 | `hy.official.kr` | 🟠 조건부 | hy(한국야쿠르트) | 7.3만 |
| 29 | 배스킨라빈스 | `baskinrobbinskorea` | ✅ | 배스킨라빈스🍦 | 74.7만 |
| 30 | 던킨 | `dunkin_kr` | ✅ | 던킨 | 42.6만 |
| 31 | 이삭토스트 | `isaactoast.official` | ✅ | 이삭토스트 | 2.7만 |
| 32 | 파리바게뜨 | `parisbaguette_kr` | ✅ | 파리바게뜨 | 18.2만 |
| 33 | 나폴레옹과자점 | `napoleon.bakery` | ✅ | 나폴레옹과자점 | 5,846 |
| 34 | 브레댄코 | `breadnco_kr` | ✅ | 브레댄코 공식 인스타그램 | 1.2만 |
| 35 | 홍루이젠 | `hungruichenkorea` | ✅ | 홍루이젠 | 1.7만 |
| 36 | 노티드 | `cafeknotted_kr` | ✅ | Knotted 노티드 | 12.7만 |
| 37 | 삼송빵집 | `samsong_bakery` | ✅ | 삼송빵집 | 9,137 |
| 38 | 본죽 | `bonjukofficial` | ✅ | 본죽 공식 인스타그램 | 3.5만 |
| 39 | 본죽&비빔밥 | `bonjukofficial` | 🟠 조건부 | 본죽 공식 인스타그램 (본죽과 동일) | 3.5만 |
| 40 | 본도시락 | `bondosirak_official` | ✅ | 본도시락 | 5.3만 |
| 41 | 본설렁탕 | `bonseol_official` | ✅ | 본설렁탕(본가네국밥) | 6,479 |
| 42 | 본우리반상 | `bonwoori_official` | ✅ | 본우리반상 | 321 |
| 43 | 멘지 | `ramen_menji` | ✅ | 멘지 MENJi | 2,572 |
| 44 | 본흑염소·능이삼계탕 | — | ⚪ 없음 | | |
| 45 | 이지브루잉커피 | `easybrewingcoffee` | ✅ | 이지브루잉커피 | 155 |
| 46 | 요거프레소 | `yogerpresso_official` | ✅ | 요거프레소 | 3만 |
| 47 | 매머드커피 | `mmthcoffee` | ✅ | 매머드커피 (MAMMOTH COFFEE) | 3.5만 |
| 48 | 더벤티 | `theventi_official` | ✅ | 더벤티 공식 계정(theVenti) | 5.9만 |
| 49 | 컴포즈커피 | `compose_coffee` | ✅ | 컴포즈커피 | 28.5만 |
| 50 | 할리스 | `official_hollys` | ✅ | 할리스 공식 인스타그램 | 9.2만 |
| 51 | 김밥천국 | — | ⚪ 없음 | (푸터 주소가 빈 `instagram.com/`) | |
| 52 | 바르다김선생 | — | ⚪ 없음 | (`teacherkim_insta` 계정 삭제됨) | |
| 53 | 죠스떡볶이 | `jaws__official` | ✅ | 죠스떡볶이 공식 인스타그램 | 8,506 |
| 54 | 명랑핫도그 | `myungranghotdog_official` | ✅ | 명랑핫도그 공식 채널 | 4.7만 |
| 55 | 스시로 | `sushiro_korea` | ✅ | 스시로한국(Sushiro Korea) | 3만 |
| 56 | 에그드랍 | `eggdrop.official` | ✅ | EGGDROP 에그드랍 | 4.1만 |
| 57 | 써브웨이 | `subwaykorea` | ✅ | 써브웨이 | 6.7만 |
| 58 | 샐러디 | `saladykorea` | ✅ | 샐러디 | 2.9만 |

### 집계

| 상태 | 개수 | 브랜드 |
|---|---:|---|
| ✅ **확인 완료** | **51** | 위 표의 ✅ 전부 |
| 🟠 **확인됐으나 주의 필요** | **2** | `hy프레딧`(계정 주체가 hy 법인), `본죽&비빔밥`(본죽과 같은 계정) |
| ⚪ **없음** | **5** | 설빙 · 롯데칠성음료 · 본흑염소·능이삼계탕 · 김밥천국 · 바르다김선생 |
| ❓ **미확인** | **0** | — |

**추측으로 채운 칸은 한 곳도 없다.** 53건 모두 ① 공식 사이트가 가리키고 ② 실제로 열어
프로필명이 그 브랜드임을 확인했다. 5건은 공식 사이트가 안 가리키거나(4) 가리킨 계정이 삭제돼(1) 비웠다.

### 이번에 바로잡은 것 — 기획 문서 F11-3 의 20건 추측 중

| 기획 문서 추측 | 판정 | 실제 정답 |
|---|---|---|
| `ediya_coffee` → 🔴 윤소연(개인) | 맞는 지적 | **`ediya.coffee`** (점) |
| `bhc_chicken` → 🔴 임방환(개인) | 맞는 지적 | **`bhc_chicken_official`** |
| `bbq_chicken` → 🔴 Jazhari Johnson(개인) | 맞는 지적 | **`bbq_offi`** |
| `orionworld` → 🔴 Ajay Kaundal(개인) | 맞는 지적 | **`orion_world`** (언더바) |
| `emart24.official` → 🟠 "이마트" | 맞는 지적 | **`emart24_official`** (언더바). 점 버전은 이마트24 **페이스북** 주소다 |
| `7eleven_korea` → ⚪ 없음 | 맞는 지적 | **`7elevenkorea`** |
| `megamgccoffee` → ⚪ 없음 | 맞는 지적 | **`mega.mgc.coffee_official`** |
| `dunkinkorea` → ⚪ 없음 | 맞는 지적 | **`dunkin_kr`** |
| `dominos_korea` → ⚪ 없음 | 맞는 지적 | **`dominostory`** |
| `momstouch_official` → ⚪ 없음 | 맞는 지적 | **`momstouch.love`** |
| `ottogi_official` → ⚪ 없음 | 맞는 지적 | **`otoki_daily`** |
| `sulbing_official` → ⚪ 없음 | 맞는 지적 | **없음** (공식 사이트에 SNS 링크 자체가 없다) |
| `composecoffee` → 🟢 맞음 | 🔴 **틀렸다** | **`compose_coffee`**. 언더바 없는 쪽은 팔로워 269명 창업홍보 계정 |
| `paikdabang` → 🟢 맞음 | 🔴 **공식 사이트가 가리키는 건 다른 계정** | **`paikscoffee_official`** |
| `paris_baguette` → 🟢 맞음 | 🔴 **공식 사이트가 가리키는 건 다른 계정** | **`parisbaguette_kr`** |
| `hollys_coffee` → 🟢 맞음 | 🔴 **공식 사이트가 가리키는 건 다른 계정** | **`official_hollys`** |
| `cu_official` → 🟢 맞음 | ✅ 일치 | `cu_official` |
| `baskinrobbinskorea` → 🟢 맞음 | ✅ 일치 | `baskinrobbinskorea` |

**"🟢 맞음" 6건 중 4건이 공식 사이트가 가리키는 계정과 달랐다.**
눈으로 보고 "브랜드 같아 보인다"로 통과시킨 것과, **공식 사이트가 스스로 가리키는 것**은 다른 증거다.

### 조사 중 발견한 함정 (코드 넣을 때 주의)

1. 🔴 **HTML 주석 안의 죽은 링크** — 커피빈 `coffeebeankorea` 는 `<!-- -->` 안에 있었고 **실제로 없는 계정**이었다.
   정규식으로 `instagram.com/(\w+)` 만 긁으면 이걸 집는다.
2. 🔴 **공식 사이트가 가리켜도 계정이 죽어 있을 수 있다** — 바르다김선생 `teacherkim_insta`.
   **반드시 열어서 확인**해야 한다.
3. 🟠 **아이콘만 있고 주소가 빈 경우** — 김밥천국의 `http://instagram.com/`.
4. 🟠 **`<a href>` 가 아니라 `<button>`** — 버거킹은 Vue/Ionic SPA 라 HTML 긁기로 안 잡힌다. 눌러봐야 나온다.
5. 🟠 **본사 사이트 루트가 아니라 브랜드 페이지에만 있는 경우** — GS25 는 `gsretail.com/brand/gs25` 까지 들어가야 나온다.
6. 🟠 **한 사이트가 여러 브랜드 계정을 가리키는 경우** — 본아이에프(8개)·삼송빵집(2개).
   다행히 둘 다 **푸터가 라벨을 붙여놔서** 짝짓기가 가능했다.
7. 🟠 **도메인 로마자 ≠ 핸들 로마자** — `orionworld.com`→`orion_world`, `hongruizhen.com`→`hungruichenkorea`.

### 유지보수

핸들은 브랜드가 바꿀 수 있다(계정 통폐합·리브랜딩). **바르다김선생이 실제로 그렇게 죽었다.**
`base.py` 에 상수로 박는다면 **"언제 확인했는지"를 주석으로 남기고**(이 조사는 2026-10-01),
링크 클릭이 깨져도 사이트는 안 깨지도록 단순 `<a target="_blank">` 로만 둘 것.
재확인이 필요하면 이 문서의 "출처" 칸대로 공식 사이트 푸터만 다시 보면 된다.

---

## 이 기능이 사용자에게 값이 있나 — 내 의견

**솔직히: 값이 작다. P2 보다도 낮게 본다. 다만 "0" 은 아니다.**

### 1. 사용자가 원한 것과 줄 수 있는 것이 어긋나 있다

사용자가 요청한 건 **"그 제품의 인스타"** 였다. 줄 수 있는 건 **"그 브랜드 계정의 홈"** 이다.
이건 같은 것의 축소판이 아니라 **다른 물건**이다.
`도미노피자 무진장 슈림프 스테이크 피자` 를 보다가 인스타 링크를 누르면
도미노피자 계정 **첫 화면**이 열린다. 그 제품 게시물을 찾으려면 사용자가 직접 스크롤해야 하고,
**찾는다는 보장도 없다**(출시한 지 오래됐으면 한참 아래에 있다).

기획 문서가 이 어긋남을 알고 **브랜드 페이지(`/b/<브랜드>/`)에만 달기로** 한 건 옳은 판단이다.
그런데 그렇게 좁히고 나면 남는 값이 이만큼이다:

> 브랜드 페이지에 이미 와 있는 사용자에게, 그 브랜드 공식 홈페이지 링크 **옆에**,
> 그 브랜드 인스타 링크를 하나 더 주는 것.

이건 **"있으면 편한 북마크"** 지 **"이 사이트를 쓰는 이유"** 가 아니다.

### 2. 같은 자리에 더 나은 것이 이미 있거나 넣을 수 있다

브랜드 페이지에는 이미 `SITES` 의 공식 메뉴 페이지 링크가 있다. 신상을 **정확하게** 보여주는 건
그쪽이다. 인스타는 **같은 정보를 더 산만하게** 준다(이벤트·콜라보·채용·사칭주의 공지가 섞여 있다).
유튜브 검색 링크(F11 문서 기준 P0)는 **제품 단위로 간다** — 어긋남이 없다.
**제한된 화면에서 인스타 한 줄이 가져갈 자리값만큼 값을 내지 못한다.**

### 3. 그래도 0 은 아닌 이유 — 하이라이트

조사하면서 확인한 건데, **여러 브랜드가 "신상" 전용 하이라이트를 만들어놨다**:

- CU **`신상트렌드`** · GS25 **`신상앨범`** · 이마트24 **`신상 모아보기`**·**`신상 하이라이트`**
- 팔도 **`팔도신상`** · 던킨 **`던킨 신상`** · 더벤티 **`더벤티 신메뉴`** · 배스킨라빈스 **`이달의 맛`**·`NEW`
- 본도시락 `신메뉴` · 브레댄코 `New` · 매머드 `NEW🔔` · 할리스 `NEW` · 요거프레소 `NEW`

**이건 비로그인으로도 프로필 상단에 보인다.** 즉 "이 브랜드 최근 신상을 이미지로 쭉 보고 싶다" 는
용건에는 **실제로 쓸모가 있다.** 특히 편의점 3사는 팔로워 수십~백만에 신상 하이라이트가 또렷하다.

### 4. 그래서 추천

**하려면 이렇게, 아니면 안 하기.**

- 🟢 **한다면**: 브랜드 페이지에만, **계정명을 그대로 노출**해서
  (`📷 CU 인스타그램 @cu_official →`) **제품이 아니라 브랜드라는 걸 링크 텍스트가 말하게** 할 것.
  기획 문서 F11-4 방향 그대로다.
- 🔴 **상품 상세에는 절대 넣지 말 것.** 유튜브 검색 링크보다 기대 어긋남이 크다.
- 🟠 **팔로워 세 자릿수 계정은 빼는 걸 권한다** — 이지브루잉커피(155) · 본우리반상(321).
  **진짜 공식 계정이지만 볼 게 없다.** 눌렀는데 게시물 몇 개뿐이면 링크를 단 것이 손해다.
  기준을 정하자면 **1만 이상**이면 하이라이트·게시물이 충분히 쌓여 있다.
- 🟠 **hy프레딧은 빼는 쪽을 권한다.** 계정 주체가 "hy(한국야쿠르트)" 라 프레딧 상품을 보던 사용자에겐 엉뚱하다.
- 🟠 **본죽&비빔밥은 본죽과 같은 계정**이라, 두 브랜드 페이지에 같은 링크가 뜬다. 문제는 아니지만 알고 있을 것.

**우선순위에 대한 솔직한 의견**: 이 조사(수작업 58건)는 **이미 끝났으니** 넣는 비용은 이제 링크 한 줄이다.
하지만 **이 기능을 위해 이 조사를 또 하라면 말리겠다.** 들인 품 대비 사용자가 얻는 게 작다.
같은 품을 F12-1(`얼큰 우동` 띄어쓰기 검색 전멸, 🔴)에 쓰는 게 **사용자에게 훨씬 큰 값**이다.
검색이 0건 나오는 건 사이트를 못 쓰게 만들지만, 인스타 링크가 없는 건 아무도 모른다.

---

# 2026-10-02 보강 — 늘어난 브랜드 59곳

위 조사는 `BRANDS` 가 58곳이던 2026-10-01 기준이다. 그 뒤 브랜드가 **171곳**으로 늘어
(더본코리아 13곳·치킨 다수·중식·돈까스·일식·제과 대기업 등) 빠진 곳을 같은 방법으로 채웠다.
유튜브 조사(`notes/YOUTUBE.md`)와 같은 날 같은 경로로 했다 — 공식 사이트가 가리키는 것만,
전부 비로그인으로 열어 프로필명을 확인했다.

**인스타 128곳 / 171곳 확보.**

## 이번에 걸러낸 가짜·죽은 계정 — 전부 공식 사이트가 가리키던 것들

| 브랜드 | 공식 사이트가 가리킨 핸들 | 열어본 결과 | 실제 정답 |
|---|---|---|---|
| 치킨플러스 | `chickenplus` (**schema.org `sameAs`**) | 🔴 **`waranon` — 팔로워 12명 개인 계정** | `chickenplus__official` (푸터 아이콘 쪽) |
| 노랑통닭 | `norangtongdak486` (**schema.org `sameAs`**) | 🔴 삭제됨 | `norangtongdak_official` (퀵메뉴 쪽) |
| 땅땅치킨 | `ttangttangchicken_official` | 🔴 삭제됨 | `ttangttang.chicken_new` |
| 보배반점 | `bobae__official` (메뉴 nav) | 🔴 삭제됨 | `bobaebanjum_kr` (schema.org 쪽) |
| 모토이시 | `motoishi.official` | 🔴 삭제됨 | **없음** |

🔴 **`schema.org/sameAs` 가 푸터 아이콘보다 믿을 만한 게 아니다.** 치킨플러스와 노랑통닭은
`sameAs` 쪽이 틀렸고 아이콘 쪽이 맞았다. 보배반점은 반대였다.
**한쪽만 보고 끝내면 안 되고, 어차피 열어봐야 안다.**

## 브랜드 전용이 아닌데 넣은 것 (hy프레딧과 같은 판단)

| 브랜드 | 핸들 | 계정 주체 | 비고 |
|---|---|---|---|
| 동원F&B | `dongwonmall` | **동원몰**(자사몰) | 공식 사이트 인스타 아이콘이 가리키는 유일한 계정 |
| 사조대림 | `sajogroup` | **사조그룹**(모회사) | 사조 사이트가 가리키는 유일한 계정 |
| 짬뽕10101 | `goguryeofood_official` | **(주)고구려푸드**(운영사) | 소개에 `BRAND.1 고구려짬뽕10101` |
| 샘표 | `sempio.official` | 샘표우리맛연구중심 | 샘표 공식 계정 맞다 |

## 1차 조사 정정 — 롯데칠성음료는 "없음"이 아니었다

위 표에서 롯데칠성음료를 ⚪없음으로 적었는데, 그때 `SITES` 의
`/kor/product/newprdt/list.do` 가 TLS 체인 오류로 안 열려 브라우저로 **메인만** 봤던 탓이다.
이번에 그 주소를 직접 받아보니 **푸터에 라벨 붙은 SNS 목록이 있다**:
`음료 인스타그램`(`lottechilsung`)·`처음처럼`·`새로`·`크러시`·`청하`·`칠성레이블`.
`schema.org` 의 `sameAs` 도 `instagram.com/lottechilsung` 을 선언한다.
수집이 **음료 신제품**을 보므로 `lottechilsung`(롯데칠성음료 / 5.9만) 을 넣었다.

## 추가한 핸들 (2026-10-02)

| 브랜드 | 핸들 | 프로필명 | 팔로워 |
|---|---|---|---:|
| 60계 | `60chicken` | 60계치킨 | 3.6만 |
| CJ제일제당 | `cjcheiljedang` | CJ제일제당 | 21.5만 |
| KFC | `kfc_korea` | KFC Korea | 7만 |
| 가마치통닭 | `gamachi_official` | 가마치 | 1.7만 |
| 국수나무 | `noodletree_official` | 국수나무 공식 인스타그램 | 1.3만 |
| 김가네 | `gimgane_official` | 김가네 | 2.3만 |
| 꾸브라꼬숯불치킨 | `kkubeu_home` | 꾸브라꼬숯불치킨 | 1.2만 |
| 네네치킨 | `nenechicken_official` | 네네치킨 공식계정 | 2.2만 |
| 노랑통닭 | `norangtongdak_official` | 노랑통닭 공식 인스타그램 | 3.1만 |
| 노브랜드버거 | `nobrandburger.official` | 노브랜드 버거 | 17.3만 |
| 농심 | `nongshim` | 농심 | 20.2만 |
| 누구나홀딱반한닭 | `nuguna_banhandak` | 누구나홀딱반한닭 | 8,112 |
| 동경에서먹었던규동 | `tokyokyudong` | 동경규동 공식 인스타그램 | 5,850 |
| 동원F&B | `dongwonmall` | 동원몰 공식 인스타그램 | 3.8만 |
| 두찜 | `twozzim` | 두찜 공식 계정 | 1.6만 |
| 땅땅치킨 | `ttangttang.chicken_new` | 땅땅치킨 | 681 |
| 또래오래 | `toreore_official` | 또래오래 치킨 | 2.6만 |
| 라홍방마라탕 | `lahongbang_official` | 라홍방 마라탕 KOREAN MALATANG | 7,641 |
| 롯데리아 | `lotteria_kr` | 롯데리아 | 37.7만 |
| 롯데웰푸드 | `lottewellfood_food` | 롯데웰푸드 \| 푸드채널 | 17.2만 |
| 롯데칠성음료 | `lottechilsung` | 롯데칠성음료 | 5.9만 |
| 매일유업 | `freshmaeil` | 매일유업(Maeil) | 14.5만 |
| 멕시카나 | `mexicana_official` | 멕시카나 | 2.7만 |
| 면사랑 | `noodlelovers.com_` | 면사랑 \| 면요리•간편식•레시피 | 10.2만 |
| 미카도스시 | `mikadosushi_official` | 미카도스시 공식계정🍣 | 6,629 |
| 바른치킨 | `barunchicken_official` | 바른치킨 공식 인스타그램 | 2.5만 |
| 백소정 | `baeksojeong_official` | 백소정 공식 인스타그램 | 4,949 |
| 버거운버거 | `burgerunburger_official` | 한입먹기 버거운버거 (BUB) 🍔 | 263 |
| 보배반점 | `bobaebanjum_kr` | 보배반점 공식 인스타그램 | 1.2만 |
| 부어치킨 | `boor_chicken` | 부어치킨 | 8,459 |
| 브라운돈까스 | `browntonkatsu` | 브라운돈까스 | 1,139 |
| 빙그레 | `binggraekorea` | 빙그레 | 26.6만 |
| 사조대림 | `sajogroup` | 사조그룹 | 1.2만 |
| 삼양식품 | `samyangfoods` | 삼양식품 | 11.1만 |
| 삼첩분식 | `samcheop__official` | 삼첩분식 | 9,572 |
| 샘표 | `sempio.official` | 샘표우리맛연구중심 | 3.2만 |
| 소림마라 | `sorimmara_official` | 소림마라 | 729 |
| 쉐이크쉑 | `shakeshackkr` | Shake Shack Korea | 24.8만 |
| 쉬즈베이글 | `shes_bagel_official` | 쉬즈베이글 커피 | 993 |
| 스쿨푸드 | `schoolfood_official` | SCHOOLFOOD, 스쿨푸드 | 6,537 |
| 슬로우캘리 | `slowcali_official` | 슬로우캘리 Slow,Cali | 8,852 |
| 신세계푸드 | `shinsegaefood.official` | 신세계푸드 | 4.2만 |
| 싸다김밥 | `ssadagb_official` | 싸다김밥 공식 인스타그램 | 7,642 |
| 쏘자토스트 | `ssojatoast_official` | 쏘자토스트 | 967 |
| 아워홈 | `ourhome.delicious` | 아워홈 | 4.2만 |
| 얌샘김밥 | `yumsem_official` | 얌샘김밥 공식 인스타그램 | 2.3만 |
| 왓더버거 | `what_the_burger` | 왓더버거 WHAT THE BURGER \| 성공창업 | 1.2만 |
| 원할머니보쌈족발 | `wongrandma` | 원할머니 공식 인스타그램👵 | 1.3만 |
| 자담치킨 | `jadamchicken_official` | 자담치킨 | 2.4만 |
| 지미존스 | `jimmyjohns_korea` | 지미존스 코리아 | 3,073 |
| 짬뽕10101 | `goguryeofood_official` | (주)고구려푸드 | 691 |
| 짬뽕관 | `jjambbonggwan` | 짬뽕관 공식 계정 | 631 |
| 참토스트 | `charmtoast_official` | 참토스트 공식 인스타그램 | 333 |
| 처갓집양념치킨 | `cheogajip_go` | 처갓집양념치킨 공식 인스타그램 | 2,517 |
| 춘리마라탕 | `chunlimalatang_official` | 춘리마라탕 공식계정 | 1,885 |
| 치킨플러스 | `chickenplus__official` | 치킨플러스 | 3,192 |
| 쿠우쿠우 | `qooqoo_official` | 쿠우쿠우 | 2.6만 |
| 퀴즈노스 | `quiznoskorea` | 퀴즈노스 | 2.3만 |
| 크라운제과 | `crownsns` | 크라운제과 | 5.3만 |
| 탐앤탐스 | `tomntoms_coffee` | 탐앤탐스커피 | 2.7만 |
| 탕화쿵푸마라탕 | `tanghuokungfu_korea` | 탕화쿵푸마라탕 공식 인스타그램 | 6,793 |
| 토마토도시락 | `tomatodosirak_official` | 토마토도시락 공식 인스타그램 | 1만 |
| 투썸플레이스 | `atwosomeplace_official` | 투썸플레이스 | 36.9만 |
| 페리카나 | `pelicana1982` | 페리카나 | 2만 |
| 포케올데이 | `pokeallday_official` | 포케올데이 Poke all day | 1.5만 |
| 푸라닭 | `puradak_official` | 푸라닭 치킨 | 4.4만 |
| 풀무원 | `pulmuone` | 풀무원 Pulmuone 공식 인스타그램 | 37.5만 |
| 하림 | `harim_natural` | 하림자연실록 | 4.1만 |
| 하이트진로음료 | `hitejinrobeverage_official` | 하이트진로음료 \| HJB 매거진 | 1.7만 |
| 한솥 | `hansot_official` | 한솥도시락 | 15만 |
| 해태제과식품 | `haitai_co` | 해태제과식품(주) | 8.5만 |
| 호식이두마리치킨 | `hosigi1999` | 호식이두마리치킨 공식 인스타그램 | 5만 |
| 홍익돈까스 | `hongikdonkatsu_official` | (프로필명 비어 있음 / 소개 `정통 경양식 돈까스 전문`) | 2,305 |
| 홍짜장 | `2026_hongjjajang_official` | 홍짜장 | 23 |
| 후라이드 참 잘하는집 | `good__fried` | 후라이드참잘하는집_후참잘_Official | 1.2만 |

## 인스타 없음 (43곳)

- **더본코리아 13곳** — 브랜드 페이지에 SNS 링크 0건. 본사 홈페이지가 거는 건
  `theborn_tasty`(본사)와 `paikscoffee_official`(빽다방)뿐이라 `고투웍`·`홍콩반점0410` 같은
  개별 브랜드에 걸 수 없다. (고투웍·리춘시장·막이오름·본가·빽보이피자·성성식당·연돈볼카츠·
  인생설렁탕·제순식당·홍콩반점0410·홍콩분식·새마을식당·백스비어)
- **SNS 링크 자체가 없다** — 긴자료코·돌배기집·동서식품·롤링파스타·미미관마라탕·
  미정국수0410·삼삼마라·역전우동0410·오봉집·원조쌈밥집·유가네·한신포차·설빙·애플꼬마김밥·미소야
- **아이콘은 있는데 주소가 비어 있다** — 김밥천국(`instagram.com/`)·큰맘할매순대국(`href=""`)·
  하루엔소쿠(`href="javascript:;"`)
- **게시물 임베드만 있고 프로필 링크가 없다** — 담꾹
- **가리킨 계정이 삭제됨** — 바르다김선생(`teacherkim_insta`)·모토이시(`motoishi.official`)
- **자매 브랜드 계정만 있다** — 박가부대(wonandone.co.kr 공용 푸터가 `wongrandma`·`mori_shabu` 만 선언) ·
  엔제리너스(lotteeatz.com 공용 푸터가 롯데리아 계정만 선언)
- **브랜드별 계정만 있고 회사 계정이 없다** — 하이트진로(참이슬·테라·켈리… 8개 중
  어느 하나를 "하이트진로"로 걸 수 없다. 유튜브는 `하이트진로 SNS` 목록에 회사 채널이 있어 넣었다)
- **SPA 를 렌더해도 SNS 링크가 없다** — SPC삼립(장식용 Instagram 버튼만) · 블루샥
- **인스타 피드 위젯의 API 주소만 있다** — 잇샌드
- **글로벌(미국) 계정만 가리킨다** — 파이브가이즈(`instagram.com/fiveguys`). 한국 계정이 따로 없다
- **지주사 사이트가 껍데기다** — 하림산업(`harimholdings.com` 43바이트)
