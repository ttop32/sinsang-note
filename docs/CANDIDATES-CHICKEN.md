# 브랜드 후보 조사 — 치킨 (잔여 전수)

`docs/BRAND-CANDIDATES.md` 와 같은 형식이다. **어댑터는 없다.** 조사 결과일 뿐이다.

- 조사일: **2026-09-30**
- 조사 방법: 브랜드당 HTTP 5회 이내, 요청 간 2.2초, `collectors/base.py` 의 UA (`sinsang-note/1.0`)
- 조사 범위: robots.txt + 홈 + 메뉴/신메뉴 페이지 구조. **전체 메뉴를 긁지 않았다.**
- robots 는 전부 `urllib.robotparser.can_fetch()` 로 실측했다. **상태코드와 본문이 HTML 인지도 같이 봤다.**
- 추측으로 채운 칸은 없다. 못 본 것은 "확인 못 함"이라고 적었다.

대상은 `docs/FRANCHISE-MASTER.md` 치킨 업종 TOP30 에서 이미 수집 중인 4종(BBQ·bhc·교촌·굽네)과
앞서 판정이 끝난 3종(네네·처갓집·60계)을 뺀 **23개**다. 푸라닭은 "도메인 사망" 이었으나 다시 시도해 **살렸다**(§5).
피자·패스트푸드·족발보쌈·양식·중식·돈까스·초밥·베이커리·카페는 다른 에이전트 담당이라 건드리지 않았다.

---

## 1. 전체 표

| 브랜드 | 가맹점수 | URL | 수집 난이도 | 신제품 신호 | robots | 약관 | 비고 |
|---|---:|---|---|---|---|---|---|
| **또래오래** | 527 | `www.toreore.com/board/menu/board_list.php` | **쉬움** | **항목별 등록일자 + 신메뉴 카테고리 + `new` 클래스** | 허용 (`*: Allow: /` + sitemap) | 이용약관 **페이지 없음**, 개인정보처리방침에 수집 금지 조항 **없음** | **1요청에 전 메뉴 + 날짜.** ⚠️인증서 체인 불완전 |
| **자담치킨** | 708 | `www.ejadam.co.kr/bbs/content.php?co_id=new_menu` | **쉬움** | **신메뉴 전용 페이지** (SSR) | 허용 (`menuBurger` 보드만 차단) | 약관 링크 **없음** (푸터·사이트맵 모두) | gnuboard. 상품명+장문 설명 SSR |
| **부어치킨** | 260 | `www.boor.co.kr/menu/default.aspx?menu=NEW` | **쉬움** | **NEW 카테고리 탭** + 공지 "신메뉴 출시" | 허용 (`/member/`,`/uploads/` 등 제외) | ⚠️ **확인 못 함** (약관이 `javascript:void(0)` 모달) | ASP.NET. **http 전용**(https 는 연결 리셋) |
| **땅땅치킨** | 177 | `ttangttang.co.kr/menu` → `/menu02` | **쉬움** | **신메뉴 전용 페이지** (SSR) | 허용 (`/?mode*`,`/admin` 등 제외) | ⚠️ **확인 못 함 (robots 가 약관 경로를 막음)** | imweb. ⚠️`/menu01`은 **추천메뉴** — 번호가 어긋난다 |
| **가마치통닭** | 788 | `www.gamachi.co.kr/b/menu` | **쉬움** | **없음** (설명문 안 '신메뉴' 1건뿐) | 허용 (**200 이지만 본문이 빈 파일**) | 🚫 **금지 조항 있음** (약관 제10호) | gnuboard. **1요청에 47건** 전량 SSR |
| **호식이두마리치킨** | 722 | `www.9922.co.kr/menu` | **쉬움** | **없음** | 허용 (`*: Allow: /`, `/admin` 등 제외) | 확인 못 함 | imweb. **1요청에 전 메뉴** SSR |
| **멕시카나** | 738 | `www.mexicana.co.kr/menu/product.asp` | 쉬움 | **없음** | 허용 (**`Yeti` 그룹만 존재**, `*` 없음) | 확인 못 함 | 3페이지. 이름+설명+**권장소비자가격** |
| **푸라닭** | 715 | `www.puradakchicken.com/menu/product.asp` | 쉬움 | **없음** | 허용 (`*: Allow:/`) | 확인 못 함 | **도메인 사망 판정 정정**(§5). 8페이지 |
| **훌랄라** | 298 | `www.hoolala.co.kr/renewal/menu/*.php` (7종) | 쉬움 | **없음** | 허용 (`/adm/` 만 제외) | 확인 못 함 | **http 전용**(https 자체서명). ⚠️"신메뉴 교육 동영상"은 **점주용 게시판** |
| **바른치킨** | 185 | `barunchicken.com/menu/view.php?board_id=..&shca=M00N` | 보통 | **없음** | 허용 (`/js/`,`/common/`,`/itboard/` 등 제외) | 확인 못 함 | 목록 `/menu/index.php` 는 JS 렌더. **홈에 개별 링크가 SSR** |
| **치킨플러스** | 279 | `chickenplus.co.kr/CHICKEN`,`/PLUS-MENU`,`/SIDE-MENU` | 보통 | **없음** | 허용 (블록이 2번 중복 기재) | 확인 못 함 | imweb **게시판형**. 렌더 텍스트가 항목명뿐 |
| **누구나홀딱반한닭** | 260 | `www.nuguna-banhandak.co.kr/product/list` | 보통 | **신메뉴 카테고리 (내비에 존재)** — URL 확인 못 함 | 허용 (**`*` 그룹 없음**, 봇 8종만 개별 지정) | 확인 못 함 | 4페이지 + `/popup/product_view?wm_id=N`. 상품명 SSR 여부 확인 못 함 |
| **노랑통닭** | 751 | `www.norangtongdak.co.kr/main.html` → `/menu/chicken.html` | 보통 | **확인 못 함** | 허용 (`*: Allow: /`) | 확인 못 함 | ⚠️**구형 TLS (DH_KEY_TOO_SMALL)**. apex 는 스플래시. ⚠️`/store/new.html`은 **신규매장** |
| **동근이숯불두마리치킨** | 172 | `geunzzang.com/bbs/board.php?bo_table=main_menu` | **확인 못 함** | **없음** (gnuboard `icon_new` 필드가 **전부 빈 값**) | 허용 (`*: Allow: /`) | 확인 못 함 | 홈 723KB 대부분 창업 마케팅. 메뉴 게시판은 미확인 |
| **후라이드 참 잘하는집** | 280 | `www.hoocham.com/menu/menu1?ca_id=01` 외 2 | 보통 | **확인 못 함** | 허용 (**`*` 그룹 없음**, 봇 6종 차단·Yeti/NaverBot 허용) | 확인 못 함 | 홈은 SSR. `/story/news` 게시판 존재 |
| **보드람치킨** | 202 | `bodram.com` | **확인 못 함** | 홈에 `#신메뉴출시 #블랙페퍼순살치킨` 해시태그 + "WHAT'S NEW" 섹션 | ⚠️ **robots.txt 가 깨져 있다** (§4) | 확인 못 함 | Makeshop. `/menu` 는 **makeshop 403 페이지** → 메뉴 경로 확인 못 함 |
| **또봉이통닭** | 462 | `ttobongee.com` | **확인 못 함** | **확인 못 함** | 허용 (`*: Allow:/`) | 확인 못 함 | Next.js. `/menu`·`/skin3/menu.php` 둘 다 **404**. 홈 링크가 `/menu/undefined` |
| **꾸브라꼬숯불치킨** | 250 | `kkubeurakko.com` | **확인 못 함** | **확인 못 함** | 허용 (WordPress 기본 + `/wp-admin` 등 제외) | 확인 못 함 | **포털 스플래시**(렌더 489자). 브랜드 메뉴 사이트 확인 못 함 |
| **페리카나** | 995 | `www.pelicana.co.kr/menu/list` | **불가** | **신제품 전용 탭 + NEW 배지 (CSS 로 확인)** | **robots.txt 404 (본문 빈 파일)** | 확인 못 함 | Nuxt SPA. 907KB 받아 **렌더 텍스트 517자**. 번들에서 내부 API 못 찾음 |
| **지코바** | 743 | `www.gcova.co.kr` | **불가에 가까움** | **없음** | **404 (HTML)** | 확인 못 함 | EUC-KR **프레임셋**. 상품 1개 = 정적 `.htm` 1장. https 자체서명 |
| **치킨신드롬** | 175 | `chickensyndrome.co.kr` | **해당 없음** | — | 허용 (`*: Allow: /`) | — | **창업 모집 랜딩만 있다.** 메뉴 페이지 자체가 없다 (청년다방형) |
| **기영이숯불두마리치킨** | 248 | `kiyoung2.com` | **해당 없음** | — | 허용 (`*: Allow: /`) | — | **창업 모집 전용.** 소비자 메뉴 없음. "신메뉴 출시로"는 창업 홍보 문구 |
| **화락바베큐치킨** | 159 | `bbqchicken-sample.imweb.me` | **해당 없음** | — | 허용 (imweb 기본) | — | ⚠️**자체 도메인이 없다**(아임웹 샘플 서브도메인). 내용도 창업 모집뿐 |

---

## 2. 추천 순위

우선순위 기준은 (1) 신제품 신호가 명확한가 → (2) 수집이 쉬운가 → (3) 가맹점 수·인지도 순이다.

### 1위 — 또래오래 (527호점) ★ 이 카테고리 최고

**`released_at` 을 채울 수 있는 유일한 브랜드다.** 지금까지 나온 어떤 신호보다 강하다.
본아이에프의 `newYn` 은 Y/N 만 있고 날짜가 없었는데, 여기는 **항목별 날짜가 그대로 나온다.**

`GET /board/menu/board_list.php` **1요청**에 전 메뉴(이름+해시태그 설명+분류) + 날짜가 전부 SSR 로 온다.
분류 탭에 **신메뉴**가 따로 있고, HTML 에 `class='menu-intro__item new'` 가 붙는다.

### 2위 — 자담치킨 (708호점)

`/bbs/content.php?co_id=new_menu` 가 **신메뉴 전용 페이지**다. SSR 이고 상품명+장문 설명이 들어 있다.
가맹점 수도 708 로 이 목록에서 세 번째다. robots 는 `Allow: /` 이고 차단 대상은 `menuBurger` 보드 하나뿐이다.

### 3위 — 부어치킨 (260호점)

`/menu/default.aspx?menu=NEW` 라는 **NEW 카테고리 탭**이 있다. 페이지 스크립트에
`arrMenuCategory = ["ALL", "NEW", "그릴후라이드", "후라이드", "버거", "사이드"]` 가 박혀 있어 분류가 고정이다.
공지 게시판에도 "신메뉴 출시 …" 글이 여러 건이라 교차검증이 된다. 가맹점 수는 적은 편이다.

### 4위 — 땅땅치킨 (177호점)

`/menu` 가 `/menu02` 로 가고 그게 **신메뉴 전용 페이지**다. SSR 로 이름+설명이 나온다.
가맹점 수가 177 로 작고, robots 가 약관 경로(`/?mode*`)를 막아 약관을 확인할 수 없다는 점이 걸린다.

### 5위 — 가마치통닭 (788호점)

**신제품 신호는 없다.** 그런데 `GET /b/menu` **1요청에 47건이 전부** 이름·설명·이미지까지 SSR 로 온다.
난이도로만 보면 이 목록 최고고 가맹점 수도 788 로 두 번째다.

⚠️ 다만 **이용약관에 금지 조항이 있다.** 현재 방침("robots 가 명시 차단하면 제외, 약관만 금지면 수집하되 기록")
상 제외 대상은 아니지만, 붙인다면 `base.py` 의 이마트24·도미노피자·폴바셋 주석과 같은 자리에 기록해야 한다.

> 신호 없이 붙이면 합류 첫날 신제품을 하나도 못 내놓고 diff 로만 판정하게 된다.
> 그게 싫으면 5위 대신 **호식이두마리치킨(722호점)** 이 있다. 역시 1요청 전량 SSR 이고
> robots 가 `Allow: /` 로 명시 허용이며, 약관 금지 조항은 발견되지 않았다. 신호가 없는 건 똑같다.

---

## 3. 근거 (실측 조각)

추측과 구분하기 위해 실제로 받은 것을 남긴다.

### 또래오래 — 항목별 등록일자

`/board/menu/board_list.php` 렌더 텍스트 끝에 **상품마다 날짜가 붙은 목록**이 이어진다.

> 뿌레카치킨 한마리, 순살, 윙봉, 스틱, 콤보 **2026.09.29**
> 김말이튀김 사이드메뉴 **2026.09.16**
> 왕새우튀김 사이드메뉴 **2026.07.16**
> 미니핫도그 사이드메뉴 **2026.03.01**
> 말랑피자볼 사이드메뉴 **2026.01.29**
> … 카레마요 순살 **2025.10.27** / 오곡후라이드 **2025.05.01**

내림차순이고 값이 서로 다르다. 일괄 재업로드 흔적(할리스·노브랜드버거형)이 아니다.
같은 페이지의 분류 탭이 `전체 / 신메뉴 / 오곡시리즈 / 시그니처 / 순살&콤보 / 바베큐 / 사이드메뉴` 이고,
HTML 에 배지 클래스가 있다.

```html
<li class='menu-intro__item new'>
```

홈 상단에도 SSR 배너가 있다.

> [NEW] 찐~한 바베큐 풍미의 신메뉴 뿌레카치킨 출시! 지금 바로 만나보세요♥

상품 상세는 `/board/menu/board_view.php?board_seq=<번호>&category_seq=<분류>` 다.
`board_seq` 는 1167~1909 범위에서 증가하니 목록만으로 최신순 정렬도 된다.

**⚠️ 인증서 체인이 불완전하다.** 기본 설정으로는 붙지 않는다.

```
ConnectError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed:
              unable to get local issuer certificate
```

`base.client()` 는 `verify=` 를 넘겨도 듣지 않는다. **`transport` 를 같이 넘기기 때문에 `verify` 가 무시된다.**
`httpx.HTTPTransport(retries=3, verify=<ctx>)` 처럼 **transport 쪽에 넣어야** 통한다.
이건 노랑통닭·훌랄라·지코바에도 똑같이 걸리는 문제다.

### 자담치킨 — 신메뉴 전용 페이지

`/bbs/content.php?co_id=new_menu` 는 `<title>신메뉴 | 자담치킨</title>` 이고 SSR 이다.

> **뿌슐랭 치킨** — '뿌슐랭 치킨'은 부드럽고 촉촉한 닭다리 순살을 바삭한 라면 튀김옷으로 요리해
> 식감과 풍미를 살린 자담치킨의 **신메뉴**입니다. …
> **치즈핑 치킨** — 모짜렐라치즈의 풍미가 핑~하게 터지는 치즈치킨!

전체 메뉴는 별도 게시판이다. `menuChicken` / `menuPizza` / `menuEtc`.
robots 가 딱 하나를 막는데 그게 **메뉴 보드 중 하나**라 주의해야 한다.

```
User-agent: *
Allow: /
Disallow: /bbs/board.php?bo_table=menuBurger
```

`co_id=new_menu` 와 `co_id=newmenu` 두 링크가 홈에 같이 있다. 실제로 연 건 `new_menu` 쪽이다.

### 부어치킨 — NEW 탭이 실재한다

`/menu/default.aspx?menu=NEW` 가 200 이고 상품이 SSR 로 들어 있다.

> **맵쇼킹** Spicy Shocking — 맛있게 즐기는 기분 좋은 매운맛! 매운맛 마니아를 위한 중독성 강한 화끈한 맵쇼킹 치킨
> **콘소메치킨** Corn Consomme Chicken — 바삭함에 고소함을 더한 콘소메 시즈닝!

분류가 코드에 하드코딩돼 있다.

```js
var arrMenuCategory = ["ALL", "NEW", "그릴후라이드", "후라이드", "버거", "사이드"];
```

공지 게시판에도 교차검증이 된다. `href='/customer/news.aspx?BoardID=1707' title='신메뉴 출시 …'` 형태로
`BoardID` 1698·1706·1707 세 건이 홈에 노출돼 있다.

**https 는 연결이 리셋된다.** `ConnectError: [Errno 54] Connection reset by peer`. http 로만 붙는다.
apex 홈(`/`)은 렌더 텍스트 8자짜리 껍데기고 **실제 홈은 `/default.aspx`** 다.

### 땅땅치킨 — 메뉴 번호가 어긋나 있다

이게 이 브랜드의 함정이다. 내비 순서는 `신메뉴 / 추천 메뉴 / 후라이드 / 오븐 / 세트 / 피자 / 사이드 / 내점` 인데
경로는 `/menu, /menu01 … /menu06, /menu08` 이다. 순서대로 대응하지 않는다.

| 받은 URL | 최종 URL | `<title>` |
|---|---|---|
| `/menu01` | `/menu01` | **추천메뉴**ㅣ땅땅치킨 |
| `/menu` | `/menu02` | **신메뉴**ㅣ땅땅치킨 |

`/menu` 가 `/menu02` 로 리다이렉트되고 그게 신메뉴다. `/menu01` 을 신메뉴로 찍으면 틀린다.
신메뉴 페이지는 SSR 이다.

> **짭콤찹스** 매콤찹스의 매콤한 매력에 허브순살치킨의 깊은 간장소스를 더한, 짭조름하고 중독적인 새로운 맛의 만남
> **로'st치킨+슈트트링 감자** 바삭하게 튀겨내고속은 촉촉하게 살린, 로스트 스타일의 담백한 치킨

### 가마치통닭 — 1요청 47건, 대신 약관

`GET /b/menu` 가 `Total 47건 1 페이지` 로 전량을 준다. 이름·짧은설명·긴설명·이미지가 다 있다.

> 47 청양맵간장치킨 화끈한 청양고추와 간장소스의 조합으로 깊은 풍미의 치킨 …
> 46 사천치킨 맛있게 맵다! 가마치 히든 메뉴 …
> 45 두마리통닭 바삭하고 촉촉한 가마치 대표메뉴!! …

앞의 번호가 게시물 번호라 **내림차순이 대략 최신순**이지만, 출시일이 아니라 등록 순서일 뿐이다.
`released_at` 에 넣을 근거는 못 된다. 설명문 안에 "달콤 고소한 가마치 **신메뉴**" 가 한 건 있는데
이건 문구일 뿐 배지가 아니다.

**robots.txt 는 200 인데 본문이 빈 파일이다.** 상태코드만 보면 규칙이 있는 줄 알기 쉽다. 규칙이 없으니 전체 허용이다.

이용약관은 `https://www.gamachi.co.kr/site-service` 에 있고 **금지 조항이 있다.**

> 10. 회사의 승인 없이 회사 인터넷 사이트의 서비스 정보 또는 개인정보를 **복제 또는 유통**시키거나
> **상업적으로 이용** 또는 타인에게 제공하는 행위

폴바셋 약관 v9.0("사전 승낙 없이 복제 또는 유통하거나 상업적으로 이용")과 같은 유형이다.

### 페리카나 — 신호는 최상급인데 못 받는다

가맹점 995 로 이 목록 1위인데 Nuxt SPA 라 907KB 를 받아도 **렌더 텍스트가 517자**다.
상품이 하나도 없다. 그런데 인라인 CSS 가 배지 구조를 다 알려준다.

```css
.menu_list li .menu_item.new::after { background-image:url(/_nuxt/img/ico_n… }
.menu_list li i.new { background:url(/_nuxt/img/ico_new_w.b0d6089.…
.new_menu_wrap { margin-bottom:13rem }
.new_cont .ico_new { margin:0 auto 2.8rem; background-size:contain }
```

내비에도 `MENU > 신제품 / 치킨류 / 사이드 / 알레르기 정보` 로 **신제품 탭이 따로 있다.**

**피자헛·버거킹·BBQ·본아이에프처럼 번들에서 API 가 나오는지 확인했지만 못 찾았다.**
`/menu/list` HTML 전체에서 `/api`·`baseURL`·`apiUrl` 패턴이 **0건**이다. 스크립트는 이것뿐이다.

```
/_nuxt/1fb53df.js  /_nuxt/2137068.js  /_nuxt/3f63ed3.js  /_nuxt/5bccf12.js
/_nuxt/6048c0c.js  /_nuxt/7eb9d03.js  /_nuxt/b45ce60.js
```

**7개 청크를 하나씩 까보지 못했다.** 브랜드당 5요청 한도를 이미 썼다.
가맹점 995 에 신제품 탭까지 있으니 **다음 사람은 여기부터 파는 게 이득이다.** §6 참고.

### 후라이드 참 잘하는집 · 누구나홀딱반한닭 — robots 에 `*` 그룹이 없다

둘 다 같은 형태다. 봇을 개별로만 지정하고 **`User-agent: *` 블록이 아예 없다.**

```
# hoocham.com
User-agent: Googlebot-Image
Disallow: /
User-agent: bingbot
Disallow: /
… (ZoominfoBot, SemrushBot, DotBot, AhrefsBot 동일)
User-agent: Yeti
Allow: /
User-agent: NaverBot
Allow: /
```

우리 UA 는 어느 그룹에도 안 걸리므로 `can_fetch()` 가 `True` 를 돌려준다. **차단 대상이 아니다.**
다만 롯데리아처럼 "알려진 봇만 허용" 하려는 의도로 읽을 여지는 있다. 롯데리아와 결정적으로 다른 점은
**`Disallow: /` 를 우리에게 적용하는 `*` 그룹이 없다**는 것이다. 멕시카나(`User-agent: Yeti` / `Allow:/` 두 줄이 전부)도 같은 경우다.

### 보드람치킨 — robots.txt 가 깨져 있다

첫 줄에 Daum 웹마스터도구 인증 토큰이 **개행 없이 붙어** 있다.

```
DaumWebMasterTool:0b43b8028985bd60476be76e60cd6ba486041f248b02997a0488fb1f71605bf0:lQcmlAoiinIhMK/D14lLUA==User-agent: Yeti

Allow: /
```

`User-agent: Yeti` 가 토큰 끝에 이어 붙어 파서가 그 줄을 UA 선언으로 읽지 못한다.
결과적으로 유효한 그룹이 하나도 없어 전체 허용으로 판정된다. **의도가 무엇이든 실측은 허용이다.**

홈에는 신제품 신호로 쓸 만한 게 있다.

> #이것이치킨의오리지널리티 #얇튀속촉 #오리지널후라이드치킨 #진짜후라이드 **#신메뉴출시 #블랙페퍼순살치킨** #단짠매콤

"WHAT'S NEW" 섹션도 있다. 그런데 **메뉴 페이지 경로를 못 찾았다.** `/menu` 는 Makeshop 의 403 안내 페이지를 준다.

### 동근이숯불두마리치킨 — gnuboard 배지 필드가 비어 있다

홈의 최신글 JSON 에 gnuboard 기본 아이콘 필드가 그대로 노출된다.

```json
{"…/g5_write_main_shop.php?204", "icon_new":"", "icon_hot":"", "icon_secret":""}
```

**기능은 있는데 값이 전부 빈 문자열이다.** 브랜드가 배지를 안 쓴다는 뜻이라 `is_new` 로 못 쓴다.
메뉴 게시판(`/bbs/board.php?bo_table=main_menu`)은 열어보지 못했다.

---

## 4. 도메인 함정 (이번에 실제로 걸린 것)

`BRAND-CANDIDATES.md` §6-1 에 이어 붙일 것들이다. **추측했으면 전부 틀렸다.**

| 브랜드 | 틀리기 쉬운 추측 | 실제 |
|---|---|---|
| **지코바** | `zikoba.co.kr` | **`gcova.co.kr`** — 발음과 철자가 다르다 |
| **호식이두마리치킨** | `hosigi.co.kr` | **`9922.co.kr`** — 대표번호가 도메인이다 |
| **푸라닭** | `puradak.com` (앞선 조사의 "도메인 사망") | **`puradakchicken.com`** — 살아 있다 |
| **자담치킨** | `jadam.co.kr` | **`ejadam.co.kr`** |
| **부어치킨** | `booer.co.kr` | **`boor.co.kr`**, 게다가 **`/default.aspx`** 가 진짜 홈 |
| **동근이숯불두마리치킨** | `donggeuni.co.kr` | **`geunzzang.com`** |
| **기영이숯불두마리치킨** | `kiyoungi.co.kr` | **`kiyoung2.com`** |
| **꾸브라꼬** | `kkubrakko.com` | **`kkubeurakko.com`** |
| **화락바베큐치킨** | 자체 도메인 | **없다.** `bbqchicken-sample.imweb.me` (아임웹 샘플 서브도메인) |

**스플래시/포털이 apex 를 차지한 곳이 셋이다.** 홈을 받고 "JS 렌더라 불가" 로 넘기면 안 된다.

| 브랜드 | apex 응답 | 진짜 사이트 |
|---|---|---|
| 노랑통닭 | 렌더 121자, 브랜드/창업 두 칸짜리 포털 | `/main.html` |
| 꾸브라꼬 | 렌더 489자, 같은 형태 | 확인 못 함 |
| 부어치킨 | 렌더 8자 | `/default.aspx` |
| 멕시카나 | `/intro.asp` 로 가서 렌더 101자 | `/main/index.asp` |
| 푸라닭 | 렌더 6자 | `/menu/product.asp` |

**TLS 로 끊기는 곳이 넷이다.** 한촌설렁탕(`BRAND-CANDIDATES.md` §6) 과 같은 계열이다.

| 브랜드 | 증상 | 대응 |
|---|---|---|
| 노랑통닭 | `[SSL: DH_KEY_TOO_SMALL] dh key too small` | `ctx.set_ciphers("DEFAULT@SECLEVEL=0")` |
| 또래오래 | `unable to get local issuer certificate` (체인 불완전) | 컨텍스트 조정 |
| 훌랄라 | `self-signed certificate` | **http 로 붙는다** |
| 지코바 | `self-signed certificate` | **http 로 붙는다** |

⚠️ **`base.client(verify=ctx)` 는 듣지 않는다.** `client()` 가 `transport=httpx.HTTPTransport(retries=3)` 을
같이 넘기는데, httpx 는 transport 가 주어지면 `verify` 를 **조용히 무시한다.** 처음에 이걸 몰라서
또래오래·노랑통닭을 "연결 불가"로 잘못 판정할 뻔했다. `HTTPTransport(retries=3, verify=ctx)` 로 넣어야 한다.

**"new" 가 신메뉴가 아닌 곳이 셋이다.**

- 노랑통닭 `/store/new.html` → **신규매장**
- 훌랄라 "신메뉴 교육 동영상" (`bbs/board.php?bo_table=education`) → **점주용 교육 게시판**
- 치킨플러스·호식이 등 imweb 사이트의 `.new_fixed_header`, `.new_header_mode` → **테마 CSS 클래스**

imweb 사이트는 HTML 에 `new` 문자열이 수백 건 나온다. 정규식으로 `NEW` 만 세면 전부 오탐이다.

**창업 모집 사이트를 공식 사이트로 착각하기 쉬운 곳이 셋이다.** (`CANDIDATES-KOREAN.md` 의 청년다방과 같은 건)

- 치킨신드롬 `chickensyndrome.co.kr` — "창업혜택 1,800만원", "선착순 10호점" 뿐. 메뉴 페이지 없음
- 기영이숯불두마리치킨 `kiyoung2.com` — `<title>` 부터 "창업정보 | 가맹비,교육비,로열티 전액 면제"
- 화락바베큐치킨 — 화락이야기/선서문/메뉴구성/경쟁력/**진행절차**/**상담하기**

---

## 5. 앞선 판정 정정

### 푸라닭 — "도메인 사망" 이 아니다

`BRAND-CANDIDATES.md` 의 판정을 뒤집는다. **`www.puradakchicken.com` 이 정상 동작한다.**

```
GET https://www.puradakchicken.com/robots.txt  → 200
User-agent:*
Allow:/
```

`/menu/product.asp` 는 200 이고 상품이 SSR 로 들어 있다. 이름이 한/영 2개씩 나온다.

> 씬 후라이드 쿼터레그 (4조각) Thin Fried Quarter Leg / 마불로 악마 쿼터레그 (4조각) Mabulro Devil Quarter Leg
> 마마치 Garlic Bomb Chicken / 마요피뇨 Mayo-peno Chicken / 블랙알리오 BLACK AGLIO CHICKEN

8페이지(`?page=2..8`)로 나뉘고 페이지당 12건이라 약 96건이다. 푸터가 신원을 확인해 준다.

> 법인명 (상호) : (주)아이더스에프앤비 · 대표자 : 장성식 · 사업자등록번호 : 112-88-00179

`FRANCHISE-MASTER.md` 의 가맹본부 "(주)아이더스에프앤비" 와 일치한다.

**다만 신제품 신호는 없다.** 분류가 `전체메뉴 / 치킨 메뉴 / 사이드 메뉴 / 베스트 메뉴 / 나만의 레시피 / 메뉴별 정보`
로 신메뉴 칸이 없고, 1페이지 HTML 에 NEW 배지 마크업이 없다. 이미지에 `img_hot01.png`·`img_hot03.png` 가
있는데 이건 HOT 이지 NEW 가 아니다. **수집은 쉽지만 합류 첫날 신제품은 못 낸다.**

### 처갓집·60계 — 정정 없음

"신호 없음" 판정을 뒤집을 새 소스를 찾지 못했다. 이번 조사에서 다시 요청하지 않았다.

---

## 6. 확인 못 한 것

정직하게 남긴다. 다음 사람이 여기부터 하면 된다.

1. **페리카나 `_nuxt` 청크 7개.** 이 카테고리에서 **가장 가치가 높은 미완 건**이다.
   가맹점 995(목록 1위)에 신제품 전용 탭과 NEW 배지 CSS 까지 확인됐는데 데이터만 못 받았다.
   HTML 본문에는 API 흔적이 0건이니 **청크를 직접 까야 한다.** 요청 한도로 못 했다.
2. **또봉이통닭(462)의 메뉴 경로.** Next.js 인데 `/menu`, `/skin3/menu.php` 둘 다 404 다.
   홈 링크가 `/menu/undefined` 로 깨져 있고 실재 경로는 `/brands/story`, `/daily` 뿐이었다.
   **홈 HTML 92KB 안의 `self.__next_f` RSC 페이로드를 안 봤다.** 거기 메뉴 데이터가 있을 가능성이 높다.
3. **보드람치킨(202)의 메뉴 경로.** 홈에 `#신메뉴출시` 해시태그가 있어 신호는 있을 것 같은데
   `/menu` 가 Makeshop 403 이라 못 찾았다. Makeshop 기본 경로(`/shop/`, `/board/`)를 안 훑었다.
4. **꾸브라꼬(250)의 브랜드 사이트.** apex 가 포털이고 링크가 `/franchise`, `/index` 뿐이었다.
   `/index` 를 안 열어봤다. WordPress 라 `wp-json/wp/v2/` REST API 가 열려 있을 수 있다.
5. **노랑통닭(751)의 메뉴 페이지 신호.** `/menu/best.html`, `/menu/chicken.html` 까지 찾았지만
   구형 TLS 우회에 요청을 써서 **메뉴 페이지 자체를 못 열었다.** 가맹점 751 이라 값어치가 있다.
6. **누구나홀딱반한닭의 신메뉴 URL.** 내비에 `메뉴 > 신메뉴 / 세트메뉴 / 베이크치킨 …` 이 분명히 있는데
   목록 페이지 HTML 에서 그 링크가 `ca_id` 파라미터로 안 잡혔다. 상품명이 SSR 인지 이미지인지도 확인 못 했다.
7. **후라이드 참 잘하는집(280)의 메뉴 페이지.** `/menu/menu1?ca_id=01` 외 2개 경로까지만 확인하고
   내용을 못 봤다. `/story/news` 게시판이 신메뉴 출시를 다룰 수 있다.
8. **동근이숯불두마리치킨의 메뉴 게시판** `/bbs/board.php?bo_table=main_menu`.
9. **이용약관 대부분.** 원문을 확보한 건 **가마치통닭(금지 조항 있음)** 하나뿐이다.
   - **또래오래·자담치킨**은 이용약관 페이지 자체를 찾지 못했다(푸터에 개인정보처리방침·쿠키정책만).
     또래오래 개인정보처리방침 전문을 읽었고 수집·복제 금지 조항은 **없었다.**
   - **부어치킨**은 이용약관 링크가 `javascript:void(0)` 모달이라 URL 로 못 받는다. 사람이 브라우저로 봐야 한다.
   - **땅땅치킨·호식이·치킨플러스**는 imweb 공통으로 약관이 `/?mode=policy` 인데
     robots 가 `Disallow: /?mode*` 다. **robots 를 지키면 약관을 못 읽는다.**
     `CANDIDATES-KOREAN.md` 의 김밥천국과 똑같은 구조다.
10. **마스터 목록 밖 브랜드.** 이름은 아는데 **이번에 조사하지 않았다.** TOP30 밖이라 가맹점 수 근거가 없다.
    깐부치킨 · 티바두마리치킨 · 오븐에빠진닭(오빠닭) · 청년치킨.
    붙일 값어치가 있는지는 공정위 등록 여부와 가맹점 수부터 확인해야 한다.

---

## 7. 어댑터를 쓸 사람에게

1. **`BRANDS` 레지스트리는 손댈 게 없다.** 여기 후보는 전부 기존 세부분류 `치킨` 에 들어간다.
   `base.py` 의 `BRANDS` 한 곳에서 정하는 원칙만 지키면 된다.
2. **또래오래를 붙일 때 `released_at` 을 반드시 채워라.** `Item` 주석이 말하는 "가장 강한 신호"를
   실제로 줄 수 있는 첫 치킨 브랜드다. 날짜가 있으니 `is_new` 는 날짜에서 유도하면 된다.
3. **`base.client()` 로는 또래오래·노랑통닭에 못 붙는다.** §4 마지막 문단의 transport/verify 문제다.
   설빙 `_live_host()` 처럼 브랜드별 우회가 필요하다. 이 건은 `client()` 에 `verify` 를
   transport 로 흘려주는 한 줄로 공통 해결할 수도 있다 — 다만 **요청 범위 밖이라 고치지 않았다.**
4. **가마치통닭을 붙이면 약관 금지 조항을 `base.py` 주석에 기록해라.** 이마트24·도미노피자·폴바셋과 같은 자리다.
5. **imweb 사이트(호식이·땅땅·치킨플러스)의 이미지 경로 날짜를 `released_at` 에 넣지 마라.**
   `cdn.imweb.me/thumbnail/20200120/…` 처럼 날짜가 경로에 있는데, 호식이는 **전 상품이 `20200120` 하나**다.
   일괄 업로드 흔적이다. `BRAND-CANDIDATES.md` §6-5 와 같은 건이고, `uploaded_at` 까지만이다.
