# 브랜드 후보 조사 — 일식 · 중식 · 아시안 · 샌드위치/샐러드

`docs/BRAND-CANDIDATES.md` 와 같은 형식이다. **어댑터는 쓰지 않았다.** 이 문서는 조사 결과일 뿐이다.

- 조사일: **2026-09-30**
- 조사 방법: 브랜드당 HTTP 5회 이내, 요청 간 2.2초 이상, `collectors/base.client()` (UA `sinsang-note/1.0`)
- 조사 범위: robots.txt + 홈 + 메뉴 페이지 + (가능하면) 이용약관. **전체 메뉴를 긁지 않았다.**
- 추측으로 채운 칸은 없다. 못 본 것은 "확인 못 함"이라고 적었다.
- 카테고리 밖(베이커리·한식·분식·카페·주점)은 건드리지 않았다.

> **요청 수 관련 고지.** 에그드랍은 TLS 핸드셰이크 실패 3회를 포함해 접속 시도가 6회다.
> 서버에 실제로 도달한 HTTP 요청은 3회(HTTP 평문)다. 실패한 3회는 TLS 단계에서 끊겨
> HTTP 요청이 전송되지 않았다. 나머지 브랜드는 전부 5회 이내다.

---

## 1. 요약 — 이 카테고리는 수확이 나쁘다

**23개 브랜드를 조사해 공식 사이트를 확정한 곳이 9곳뿐이다.** 절반 이상이 도메인 단계에서 죽었다.
일식·중식 프랜차이즈는 자체 웹사이트를 아예 운영하지 않거나(인스타·배달앱으로 대체),
도메인을 놓쳐 주차·매물 페이지가 된 곳이 유난히 많다.

신제품 신호가 확실한 곳은 **4곳**이고, 그중 **1곳(써브웨이)은 약관 때문에 붙이면 안 된다.**
결국 실제로 쓸 수 있는 건 **스시로 · 에그드랍 · 샐러디 3곳**이다.

---

## 2. 전체 표

| 브랜드 | 카테고리 | URL | 수집 난이도 | 신제품 신호 | robots | 약관 | 비고 |
|---|---|---|---|---|---|---|---|
| **스시로** | 일식 | `sushiro.co.kr/pm` | 쉬움 | **이달의 한정메뉴 전용 페이지** | **없음 (404, JSON 본문)** | **확인 못 함** | 카드마다 `data-menu-name-ko/ja/price/image`. 6페이지 ~48건 |
| **에그드랍** | 샌드위치 | `www.eggdrop.co.kr/menu/list.php?category=NEW` | 쉬움 | **NEW 전용 카테고리 + 홈 `NEW EGGDROP` 섹션** | 허용 (`Allow: /`) — **HTTP 로만** | **확인 못 함** (개인정보처리방침만 존재) | ⚠️ **HTTPS 인증서가 2025-05-27 만료.** 평문 HTTP 외에 길이 없다 |
| **샐러디** | 샐러드 | `salady.com/menu/list_1`, `/menu2/list_1?menu2=1` | 쉬움 | **NEW 배지 + "새로운 메뉴" 섹션** | 허용 (`Allow: /`) | ⚠️ **제12조 2항** — 폴바셋 제외 사유와 사실상 같은 문구 | 2개 라인 × 3목록. list_1 43건(NEW 6) / menu2 45건(NEW 4) |
| **써브웨이** | 샌드위치 | `www.subway.co.kr/menuList/sandwich` | 쉬움 | **신제품 탭 + 상품 class + NEW 배지 (3중)** | **없음 (404, JSON 본문)** | 🔴 **제5.2조 (b) 명시적 금지** | **신호는 이 조사 전체 1등인데 약관이 막는다.** §5 참조 |
| **니뽕내뽕** | 일식/퓨전 | `www.nipongnaepong.co.kr/menu/menu_list_wd.php?q_mcate=…` | — | **확인 못 함** | 🔴 **403 → `can_fetch()` 전 경로 False** | — | PHP SSR, 카테고리 5개. robots 403 은 404 와 다르다(§6-1) |
| **미소야** | 일식/돈까스 | `www.misoya.co.kr/menu` | **불가** | **없음** | 허용 (`/site_join`,`/login`,`/shop_cart`,`/?mode*`,`/admin` 제외) | **확인 못 함** — 약관이 `/?mode=policy`, robots 가 막는 경로 | 아임웹(imweb). `/menu` HTML 에 **상품명이 0건**, 카테고리명뿐 |
| **돈치킨** | 일식/돈까스 | `donchicken.co.kr/bbs/content.php?co_id=menu` | **불가** | **없음** | 허용 (`Allow: /`) | **확인 못 함** (개인정보취급방침만) | HTML 에 **`메뉴명 설명 최대 두 줄`** 플레이스홀더만. 상품 0건 |
| **아비꼬** | 일식/카레 | `abiko.kr` | **확인 못 함** | **확인 못 함** | **없음 (404, HTML 본문)** | **확인 못 함** | gnuboard. `/bbs/content.php?co_id=menu` 는 오류 페이지. 홈에 `#menu` 앵커뿐 |
| **더본코리아** | 포털 | `www.theborn.co.kr/brand/representation/` | — | **없음** | (다른 조사에서 `Allow: /` 확인됨) | — | 브랜드 페이지(`/theborn_brand/홍콩반점2` 등)는 **IR·회사소개 보일러플레이트고 메뉴가 없다** |
| **홍콩반점0410** | 중식 | — | **확인 못 함** | — | — | — | 도메인 3개 전부 오답. §6-2 참조 |
| **짬뽕지존** | 중식 | — | **확인 못 함** | — | — | — | `jjambbong.co.kr` = **"domain for sale"** 주차 페이지 |
| **초마** | 중식 | — | **확인 못 함** | — | — | — | `choma.co.kr` 443 **Connection refused**. 공유 호스팅 IP |
| **만다복** | 중식 | — | **확인 못 함** | — | — | — | `mandabok.co.kr`·`.com`·`.kr` 전부 NXDOMAIN |
| **차이나팩토리** | 중식 | — | **확인 못 함** | — | — | — | `chinafactory.co.kr` = **대전 관저 더샵3차 모델하우스**. 완전 무관 |
| **사보텐** | 일식/돈까스 | — | **확인 못 함** | — | — | — | `saboten.co.kr` = **Gabia 주차**(인증서 `*.gabia.com`) |
| **갓덴스시** | 일식 | — | **확인 못 함** | — | — | — | `gatten.co.kr` 타임아웃, `gattensushi.com` = **HugeDomains 매물** |
| **요시노야** | 일식 | — | **확인 못 함** | — | — | — | `yoshinoya.co.kr`·`.kr`·`yoshinoyakorea.co.kr` 전부 NXDOMAIN |
| **하남돼지집** | (한식) | — | **확인 못 함** | — | — | — | `hanam.co.kr` = **하남전자**. 무관. 한식 담당 범위라 더 안 팜 |
| **포메인** | 쌀국수 | — | **확인 못 함** | — | — | — | `phomein.co.kr` = **Gabia 주차**(인증서 `*.gabia.io`) |
| **미스사이공** | 쌀국수 | — | **확인 못 함** | — | — | — | `misssaigon.co.kr`·`.kr`·`mrsaigon`·`pho36` 전부 NXDOMAIN |
| **탕화쿵푸 / 라화쿵부** | 마라탕 | — | **확인 못 함** | — | — | — | `tanghwa`·`tanghwakungfu`·`rahwa`·`rahwakungbu` 전부 NXDOMAIN |
| **오니기리와이규동** | 일식 | — | **확인 못 함** | — | — | — | `onigiri.co.kr` = **hosting.kr 주차** |
| **미아옥 / 큐브치킨 / 포케 브랜드** | 기타 | — | **확인 못 함** | — | — | — | 공식 도메인을 특정하지 못했다 |

---

## 3. 근거 (실측 조각)

추측과 구분하기 위해 실제로 받은 마크업을 남긴다.

### 스시로 — 이 카테고리 최고 후보

홈(`sushiro.co.kr/`)에 `id="new-limited"` 섹션이 서버렌더로 들어있고, 전용 페이지 `/pm` 가 따로 있다.

```html
<section id="new-limited" class="new-section new-section--cream">
  <p class="new-section-kicker">LIMITED MENU</p>
  <h2 class="new-section-title">이달의<br>한정 메뉴</h2>
  <a class="new-button new-button--primary" href="/pm">전체 보기</a>
```

`/pm` 의 `<title>` 은 `이달의 한정메뉴 | 스시로한국`, 본문 첫 줄은 **"이달에만 즐길 수 있는 한정 메뉴"** 다.
상품 카드가 전부 data 속성으로 구조화돼 있다.

```html
<article class="new-menu-card menu-modal-trigger"
  data-menu-group="이달의 한정메뉴"
  data-menu-name-ko="금태 아부리 시오레몬"
  data-menu-name-ja="のどくろ炙り塩レモン"
  data-menu-price="5,000"
  data-menu-image="https://ssrkosupport.com/29990/002232.jpg">
```

1페이지 8건, `?page=1`~`6` 페이지네이션 → **총 ~48건**. 전부 이번 달 한정 메뉴다(과거 이력이 아니다).
푸터 실측: `스시로한국 / 사업자등록번호 214-88-75700 / 대표 TANAKA SHUNSAKU` — 공식 한국 법인 사이트가 맞다.

**유보.** `/pm` 은 "이 달에 한정 판매하는 메뉴"지 "이번 달에 처음 나온 메뉴"가 아니다.
매달 갈리는 건 확실하지만 재등장 품목이 섞일 수 있다. `is_new=True` 는 줄 수 있어도
`released_at` 은 못 채운다. 배스킨라빈스 "이달의 맛"과 같은 성격으로 다뤄라.

### 에그드랍 — NEW 가 URL 로 분리돼 있다

`/menu/list.php?category=NEW` 가 독립 카테고리다. 상품 7건이 서버렌더로 들어있다.

```html
<li>
  <a href="/menu/view.php?seq=338">
    <span class="title" style="background-image: url('/upload/menu/1767686689.png')"></span>
    <span class="text">케일 사과주스</span>
  </a>
</li>
```

카테고리 8개: `NEW / TOAST / SANDWICH / BAGEL / BRUNCH / SIDE / DRINK, COFFEE / SET MENU`.
홈 1요청에 `seq` 73건이 들어있고 `<section class="new"><h3>NEW EGGDROP</h3>` 슬라이더도 따로 있다.

⚠️ **HTTPS 가 죽어 있다.**
```
subject=CN=www.eggdrop.co.kr
SAN: DNS:www.eggdrop.co.kr, DNS:eggdrop.co.kr
notAfter=May 27 06:57:28 2025 GMT
```
인증서 자체는 이 브랜드 것이 맞는데(SAN 일치) **1년 4개월 전에 만료됐다.**
`base.client()` 는 `verify=True` 라 HTTPS 로는 접속이 안 된다. 평문 HTTP 는 정상 응답하고
robots.txt 도 HTTP 로만 받힌다(`User-agent: *\r\nAllow: /`).
평문 HTTP 수집을 허용할지는 `CRAWLING-POLICY.md` 에 방침이 없다. **사용자 판단이 필요하다.**

⚠️ **이미지 파일명을 날짜로 쓰지 마라.** `/upload/menu/1767686689.png` 를 유닉스 epoch 으로 읽으면
2026-01-06 이 나와 그럴듯하지만, 같은 사이트의 `1793690388.png` 는 **2026-11-03 — 미래 날짜**다.
epoch 해석이 성립하지 않는다. 할리스·노브랜드버거보다 더 나쁜 신호니 아예 쓰지 마라.

### 샐러디 — NEW 배지 + 전용 섹션

```html
<div class="title"><h5>새로운 메뉴</h5></div>
<!-- new -->
<ul><li>
  <a href="/menu/view_1?idx=124&ca_id="></a>
  <div class="info"><h6>고추장제육 들기름파스타 누들볼</h6>
    <p>Gochujang Bulgogi Perilla Oil Pasta
      <b class="tagbox"><span class="new">NEW</span></b>
```

한글명·영문명·태그가 다 들어있다. `LOW SUGAR` 같은 다른 태그도 같은 `tagbox` 안에 있다.
라인이 2개다 — `/menu/*`(43건, NEW 6) 와 `/menu2/*?menu2=1`(45건, NEW 4).
각 라인에 `list_1`(메인) / `list_2?type=topping` / `list_3?type=side` → **총 6요청**.

### 써브웨이 — 신호는 최고, 약관이 막는다

신호가 3중으로 겹쳐 이 조사에서 가장 좋다.

```html
<li><a href="ITEM_SANDWICH.NEW">신제품</a></li>   <!-- 필터 탭 이름이 그대로 "신제품" -->
...
<li data-menusubsort="1" data-menumainsort="1" class="ITEM_SANDWICH.NEW">   <!-- 상품 li 의 class -->
  <div class="label">
    <span class="new" style="background-color:secondary-01">NEW</span>      <!-- 배지 -->
```

`/menuList/sandwich` 한 페이지에 33건, 그중 `ITEM_SANDWICH.NEW` 4건 / NEW 배지 5건.
카테고리 7개(`sandwich/salad/grain_salad/morning/wrap/sidedrink/catering/unit`)라 7요청이면 전체가 온다.
**그런데 약관이 막는다. §5 참조.**

### 미소야 — robots 는 열려 있는데 상품이 HTML 에 없다

`/menu` 는 1.3MB 인데 렌더 텍스트에 상품명이 **하나도 없다.** 카테고리명뿐이다.

> MENU 미소야 메뉴 소개 since2000 KATSU UDON SOBA RICE BOWL HOT POT SUSHI ADD ON …
> 소비자는 맛있는 음식만을 선택합니다. … 리딩 브랜드는 … **신제품**을 개발합니다.

검색에 걸린 "신제품"은 **브랜드 철학 문구**고, "신메뉴"는 `/*팝업 순서 신메뉴*/` 라는 **CSS 주석**이다.
둘 다 상품 신호가 아니다. 아임웹 이미지 보드라 상품은 JS 렌더 이미지 안에 있다.
CDN 경로에 날짜가 있지만(`cdn.imweb.me/thumbnail/20260812/…`) 섹션 이미지지 상품 이미지가 아니다.

### 돈치킨 — 템플릿이 안 채워져 있다

`/bbs/content.php?co_id=menu` 렌더 텍스트 전문에 가까운 부분:

> 메뉴안내 menu 고민은 짧게 치킨 피자 세트 만족은 확실하게 치킨메뉴 피자메뉴 세트메뉴 안주&사이드메뉴
> 구운치킨 후라이드치킨 베이크치킨 닭강정 시카고피자 피자 치킨세트메뉴 안주 사이드
> **메뉴명 설명 최대 두 줄** 원산지표기

`메뉴명 설명 최대 두 줄` 은 디자인 플레이스홀더다. 실제 상품은 JS 로 채워지고 HTML 엔 없다.
아비꼬와 CSS 버전 문자열(`?ver=2303229`)이 같은 걸 보면 같은 제작사 템플릿이다.

---

## 4. robots.txt 실측

`urllib.robotparser.RobotFileParser.can_fetch("*", …)` 결과다.

| 브랜드 | 상태 | can_fetch |
|---|---|---|
| 미소야 | 200 `text/plain` | `/menu` → **True** |
| 돈치킨 | 200 `text/plain` | `/bbs/content.php?co_id=menu` → **True** |
| 샐러디 | 200 `text/plain` | `/menu/list_1` → **True**, `/menu2/list_1?menu2=1` → **True** |
| 에그드랍 (HTTP) | 200 `text/plain` | `/menu/list.php?category=NEW` → **True** |
| 스시로 | **404**, 본문이 JSON | 파일 없음 → 제한 없음 |
| 써브웨이 | **404**, 본문이 JSON | 파일 없음 → 제한 없음 |
| 아비꼬 | **404**, 본문이 HTML | 파일 없음 → 제한 없음 |
| **니뽕내뽕** | **403 Forbidden** | `/` `/main/index.php` `/menu/…` → **전부 False** |
| 갓덴스시(`gattensushi.com`) | 200 `Disallow:` (빈 값) | 주차 도메인이라 무의미 |

니뽕내뽕 실측:
```
rp.set_url("https://www.nipongnaepong.co.kr/robots.txt"); rp.read()
disallow_all: True   allow_all: False
can_fetch('*', /menu/menu_list_wd.php?q_mcate=PONG) -> False
```

---

## 5. 이용약관 조사

| 브랜드 | 근거 | 크롤링·재배포 금지 | 판정 |
|---|---|---|---|
| **써브웨이** | `www.subway.co.kr/agreement` 제5.2조 (b) | **있음 (명시적·광범위)** | 🔴 **수집하지 않는다** |
| **샐러디** | `salady.com/popup/location` 제12조 2항 | **있음** — 단 "영리목적" 한정 + 회원/앱 약관 | 🟠 **사용자 판단 필요** |
| 스시로 | 홈·`/pm` 어디에도 약관 링크 없음 | — | ⚪ **확인 못 함** |
| 에그드랍 | `/etc/privacy.php`(개인정보처리방침)만 존재 | — | ⚪ **확인 못 함** |
| 미소야 | 약관이 `/?mode=policy` 인데 **robots 가 `/?mode*` 를 Disallow** | — | ⚪ **확인 못 함 (받으면 안 됨)** |
| 돈치킨 | 개인정보취급방침만 존재 | — | ⚪ **확인 못 함** |
| 아비꼬 | 확인 못 함 | — | ⚪ **확인 못 함** |

### 써브웨이 — 이 조사에서 유일하게 확정적으로 막힌 브랜드

이용약관 제5조 제2항(제한):

> 이용자는 사이트에서 다음의 행위를 하거나, 제3자가 다음 행위를 하도록 허가할 수 없습니다.
> (a) 공개적으로 사용할 수 없는 회사 시스템, 프로그램 또는 데이터에 접근하거나 접근하려고 시도하는 행위
> **(b) 회사의 자료를 어떠한 방식으로든 복사, 복제, 재발행, 업로드, 게시, 전송, 재판매 또는 배포하는 행위**

**이마트24 제8조 ⑧ 보다 넓다.** 이마트24는 "크롤러·매크로·스파이더·스크래퍼"라는 *수단*을 막았는데,
써브웨이는 수단을 가리지 않고 **"어떠한 방식으로든 복사·복제·재발행·게시·배포"** 를 막는다.
우리 서비스는 메뉴 데이터를 복제해 재게시하는 게 본체다. 정면으로 걸린다.

robots.txt 가 없다는 건 방어가 되지 않는다. 이마트24·도미노·폴바셋과 같은 종류의 건이고,
셋 다 제외됐으니 **써브웨이도 같은 처분이 일관적이다.**

> 과제에서 "써브웨이 같은 글로벌 브랜드는 본사 약관이 더 엄격할 수 있으니 특히 봐라"고 했는데,
> 실제로 그랬다. 문구가 한국 프랜차이즈 약관 톤이 아니라 미국 본사 약관 번역체다
> ("이 합의서", "임대, 리스, 공동 임차, 서비스 업체", "디컴파일·디스어셈블·리버스 엔지니어링").

### 샐러디 — 폴바셋과 같은 문구다

서비스이용약관 제12조(저작권의 귀속 및 이용제한) 2항:

> 이용자는 '회사'의 서비스를 이용함으로써 얻은 정보를 '회사'의 사전 승낙 없이
> **복제, 송신, 출판, 배포, 방송 기타 방법에 의하여 영리목적으로 이용**하거나
> 제3자에게 이용하게 하여서는 안됩니다.

`collectors/base.py` 의 폴바셋 제외 사유와 비교해라:

> 폴바셋 — 약관 "정보를 회사의 사전 승낙 없이 복제 또는 유통하거나 상업적으로 이용하는 행위" 금지

**사실상 같은 조항이다.** 폴바셋을 뺐으면 샐러디도 빼는 게 일관적이다.

다만 두 가지 차이는 있다.
1. **"영리목적으로"** 라는 한정이 붙어 있다. 폴바셋도 "상업적으로"가 붙어 있었는데 제외됐으니
   이 차이로 결론이 갈리진 않을 것 같다.
2. 제1조·제2조를 보면 이 약관은 **'샐러디 모바일 Application' 회원**을 대상으로 한다
   (`'회원': … '앱'을 통해 이용약관과 … 동의하여 '회원'등록한 자`).
   이디야 케이스(🟡 회원 대상, 공개 사이트 적용 여부 불명)와 같은 구조다.
   비회원이 공개 웹페이지만 읽는 경우에 구속력이 있는지는 다툼의 여지가 있다.

**내 판단으로 결정하지 않았다.** 폴바셋 선례를 따르면 제외, 이디야 선례를 따르면 보류다.
`CRAWLING-POLICY.md` §4 표에 추가하고 사용자가 정해야 한다.

---

## 6. 어댑터를 쓸 사람에게 넘기는 주의사항

### 6-1. ⚠️ robots.txt 403 은 404 와 정반대다 (새 함정)

`BRAND-CANDIDATES.md` §6-2 는 "robots.txt 가 없는 것(404)은 금지가 아니다"라고 맞게 적었다.
**그런데 403·401 은 반대로 전면 금지다.** RFC 9309 §2.3.1.4 가 그렇게 정하고,
파이썬 `robotparser` 도 그대로 구현한다(`disallow_all = True`).

니뽕내뽕이 정확히 이 경우다. 홈은 200 으로 멀쩡히 열리는데 robots.txt 만 403 이라
**`can_fetch()` 가 전 경로 False** 다. 빕스와 같은 처분을 받아야 한다.

상태코드를 세 갈래로 나눠 처리해라.
- `200` → 파싱
- `404` / `410` → 제한 없음 (단 더 보수적인 간격)
- **`401` / `403` → 전면 금지**
- `5xx` → 일시 오류. 금지로 간주하고 재시도

투썸플레이스가 "403" 으로 이미 제외돼 있는데, 그 근거가 이것이다.

### 6-2. ⚠️ `can_fetch()` 가 쿼리스트링 와일드카드를 놓친다 (새 함정)

미소야 robots 는 `Disallow: /?mode*` 로 약관·마이페이지를 막고 있다.
그런데 파이썬 `robotparser` 는 이걸 **무시한다.**

```python
rp.parse("User-agent: *\nAllow: /\nDisallow: /?mode*\n".splitlines())
rp.can_fetch("*", "https://h/?mode=policy")   # -> True  (막혔어야 한다)
```

원인은 `RuleLine.__init__` 이 규칙 경로를 `urllib.parse.quote()` 로 감싸는 데 있다.

```python
urllib.parse.quote('/?mode*')   # -> '/%3Fmode%2A'
```

`?` 가 `%3F` 로, `*` 가 `%2A` 로 바뀌어 **실제 URL `/?mode=policy` 와 영원히 매칭되지 않는다.**

→ **`can_fetch()` 가 True 라고 끝내지 마라.** 규칙에 `?` 나 쿼리 와일드카드가 있으면
robots.txt 원문을 눈으로 읽고 브랜드 의도를 따로 판단해야 한다.
(그래서 이 조사에서 미소야 약관 `/?mode=policy` 는 `can_fetch` 가 True 였는데도 받지 않았다.)

### 6-3. 도메인 함정이 이 카테고리에 유독 많다 — 6건

`BRAND-CANDIDATES.md` 의 폴바셋 `pbkorea.co.kr` 건과 같은 종류가 이 카테고리에만 6건이다.
**페이지 제목과 푸터 사업자명을 눈으로 확인하기 전엔 어떤 도메인도 믿지 마라.**

| 찍은 도메인 | 실제 정체 | 어떻게 드러났나 |
|---|---|---|
| `chinafactory.co.kr` | **대전 관저 더샵3차 모델하우스** | `<title>` 이 아파트 분양 |
| `hanam.co.kr` | **하남전자** | 404 페이지 제목이 `하남전자 404 Error` |
| `hongkongbanjum.com` | **광고/팝언더 네트워크** | robots 가 `/cpx.php` `/check_popunder.php` 를 막는다 |
| `hongkongbanjum.co.kr` | **도메인 주차 랜더** | 본문 114바이트, `location.href="/lander"`. robots 에 `LLM-Policy:` |
| `gattensushi.com` | **HugeDomains 매물** | `<title>` 이 `GattenSushi.com is for sale` |
| `jjambbong.co.kr` | **도메인 매물** | `<title>` 이 `jjambbong.co.kr domain for sale!!!` |
| `onigiri.co.kr` | **hosting.kr 주차** | 유일한 링크가 `hosting.kr` 호스팅 안내 |
| `saboten.co.kr` / `phomein.co.kr` | **Gabia 주차** | 인증서가 `*.gabia.com` / `*.gabia.io` |

### 6-4. TLS 인증서를 먼저 읽으면 요청을 아낄 수 있다

`base.client()` 가 `CERTIFICATE_VERIFY_FAILED` 로 죽었을 때, **HTTP 요청을 더 쓰지 말고 인증서를 봐라.**
TLS 핸드셰이크만으로 정체가 드러난다. HTTP 요청이 아니니 브랜드당 5회에도 안 들어간다.

```
$ echo | openssl s_client -connect saboten.co.kr:443 -servername saboten.co.kr 2>/dev/null \
    | openssl x509 -noout -subject -dates -ext subjectAltName
subject=C=KR, O=Gabia,Inc., CN=*.gabia.com          ← 브랜드 것이 아니다 → 주차
SAN: DNS:*.gabia.com, DNS:bizgabia.com, DNS:gabia.com
```
```
$ ... -connect eggdrop.co.kr:443 ...
subject=CN=www.eggdrop.co.kr                        ← 브랜드 것이 맞다 → 만료일 뿐
SAN: DNS:www.eggdrop.co.kr, DNS:eggdrop.co.kr
notAfter=May 27 06:57:28 2025 GMT
```

**SAN 이 브랜드 도메인이면 "인증서만 만료", 제3자 도메인이면 "주차"** 다. 이 구분이 중요하다.
같은 이유로 DNS 조회(`dig`)도 HTTP 요청이 아니니, 후보 도메인은 DNS 로 먼저 훑어 NXDOMAIN 을
걸러낸 뒤 살아남은 것만 요청해라. 이 조사에서 그렇게 50여 개 도메인을 요청 0회로 정리했다.

### 6-5. robots 가 열려 있어도 상품이 없을 수 있다

미소야와 돈치킨은 robots 가 `Allow: /` 고 메뉴 페이지도 200 인데 **HTML 안에 상품이 0건**이다.
`BRAND-CANDIDATES.md` 가 네네치킨·컴포즈커피를 "불가"로 분류한 것과 같은 상황인데,
이쪽은 페이지가 커서(미소야 1.3MB) 얼핏 성공처럼 보인다.
**응답 크기나 상태코드가 아니라 상품명이 실제로 잡히는지로 판정해라.**

### 6-6. `BRANDS` 레지스트리에 세부분류를 먼저 등록해야 한다

기존에 없는 분류가 필요하다 — **일식**(스시로), **샌드위치**(에그드랍), **샐러드**(샐러디).
`base.py` 의 `BRANDS` 한 곳에서 정하는 원칙은 유지해라.

### 6-7. 더본코리아 산하 브랜드는 `theborn.co.kr` 로는 안 된다

`/brand/representation/` 에 브랜드 페이지 링크가 10개 있다 —
`홍콩반점2`(=홍콩반점0410), `홍콩분식`, `연돈볼카츠`, `고투웍`, `막이오름`, `본가`,
`빽보이피자`, `성성식당`, `인생설렁탕`, `제순식당`.
그런데 `/theborn_brand/홍콩반점2/` 를 실제로 받아 보면 **메뉴가 없고 회사 IR 보일러플레이트**만 나온다
(재무상태표·공시정보가 본문에 들어있다). WordPress 공통 템플릿이 브랜드 페이지에도 붙어 있는 구조다.
`BRAND-CANDIDATES.md` 가 "더본코리아는 메뉴가 없다"고 한 결론이 브랜드 개별 페이지에도 그대로 맞다.
**홍콩반점·연돈볼카츠는 자체 사이트를 찾지 못하면 붙일 수 없다.**

---

## 7. 추천 순위

기준 순서는 **(1) 신제품 신호 → (2) 수집 난이도 → (3) 브랜드 관심도** 다.

| # | 브랜드 | 근거 | 예상 요청 수 |
|---|---|---|---|
| 1 | **스시로** | **이달의 한정메뉴가 URL 로 분리돼 있고**(`/pm`), 카드마다 `data-menu-*` 로 한글명·일본어명·가격·이미지가 구조화돼 있다. 파싱 실패 위험이 이 조사에서 가장 낮다. 회전주기가 월 단위로 명확해 서비스 성격과도 맞는다 | 6 (`/pm?page=1…6`) |
| 2 | **에그드랍** | NEW 가 전용 카테고리(`category=NEW`)라 1요청이면 신제품만 받는다. robots 도 `Allow: /`. ⚠️ **HTTPS 인증서 만료로 평문 HTTP 외에 길이 없다** — 이 한 가지 때문에 1위를 못 준다. 방침 결정이 먼저다 | 1 (신제품만) / 8 (전체) |
| 3 | **샐러디** | NEW 배지 + "새로운 메뉴" 섹션이 명확하고 한글·영문명이 다 온다. ⚠️ **약관 제12조 2항이 폴바셋 제외 사유와 같은 문구** — 붙이기 전에 사용자 판단이 필요하다 | 6 (2라인 × 3목록) |
| 4 | **아비꼬** | 신호·메뉴 경로 **둘 다 확인 못 했다.** 홈에 `#menu` 앵커만 있고 gnuboard 경로는 오류 페이지였다. 순위라기보다 **다음 조사 대상**이다 | 미상 |
| 5 | — | **5위로 올릴 브랜드가 없다.** 나머지는 전부 도메인 실패·신호 없음·약관 금지 중 하나다 | — |

### 순위에 넣지 않은 이유

- **써브웨이** — 신호만 보면 **이 조사 1위**다(신제품 탭 + 상품 class + NEW 배지 3중, SSR, 7요청).
  하지만 약관 제5.2조 (b)가 복제·재게시를 어떠한 방식으로든 금지한다.
  **순위 문제가 아니라 붙이면 안 된다.** 이마트24·도미노·폴바셋과 같은 처분이다.
- **니뽕내뽕** — robots.txt 가 403 이라 `can_fetch()` 가 전 경로 False 다. 빕스와 같다. **붙이면 안 된다.**
- **미소야 · 돈치킨** — robots 는 열려 있지만 **HTML 에 상품이 0건**이다. 수집 자체가 불가다.
- **더본코리아 계열(홍콩반점·연돈볼카츠 등)** — 브랜드 페이지에 메뉴가 없다.
- **나머지 12개 브랜드** — 공식 도메인을 확정하지 못했다. §8 참조.

---

## 8. 확인 못 한 것

1. **공식 도메인을 찾지 못한 브랜드 (12개)** — 사보텐, 갓덴스시, 요시노야, 미아옥, 큐브치킨,
   홍콩반점0410, 짬뽕지존, 초마, 만다복, 차이나팩토리, 포메인, 미스사이공, 탕화쿵푸·라화쿵부,
   오니기리와이규동, 포케 브랜드.
   각각 3~6개 후보 도메인을 DNS 로 조회했고 전부 NXDOMAIN·주차·매물·무관 사이트였다.
   **이 브랜드들이 웹사이트를 아예 운영하지 않을 가능성이 높다**(인스타그램·배달앱 대체).
   브라우저로 검색엔진을 거쳐 찾으면 나올 수도 있으나, 이 조사는 HTTP 직접 확인만 했다.
2. **스시로 이용약관** — 홈과 `/pm` 어디에도 약관 링크가 없다. 다른 경로에 있을 수 있다.
   **추천 1위인데 약관을 못 봤다는 게 구멍이다.** 붙이기 전에 반드시 확인해라.
3. **에그드랍 이용약관** — `/etc/privacy.php`(개인정보처리방침)만 찾았다.
4. **미소야 이용약관** — `/?mode=policy` 인데 robots 가 `/?mode*` 를 막는다.
   `can_fetch()` 는 파서 버그로 True 를 주지만(§6-2) 브랜드 의도는 명백히 금지라 받지 않았다.
5. **아비꼬 메뉴 경로 전체** — `/bbs/content.php?co_id=menu` 는 오류 페이지였다. 다른 경로가 있을 것이다.
6. **스시로 `/pm` 6페이지 전부의 내용** — 1페이지(8건)만 받았다.
   2~6페이지가 같은 달 것인지 과거 달 것인지 **확인하지 않았다.**
   1페이지 본문에 "이달에만 즐길 수 있는 한정 메뉴"라고 적혀 있어 같은 달로 보이지만 실측은 안 했다.
7. **써브웨이 나머지 6개 카테고리의 NEW 배지 유무** — `sandwich` 만 확인했다.
   (어차피 약관 때문에 붙일 수 없어 더 받지 않았다.)
8. **에그드랍 `/menu/view.php?seq=` 상세 페이지** — 출시일 필드가 있는지 확인하지 않았다.
   있으면 `released_at` 을 채울 수 있어 순위가 올라간다. **다음 조사 1순위.**
9. **샐러디 `/menu/list_2`(토핑)·`/list_3`(사이드)** — `list_1` 만 확인했다.
