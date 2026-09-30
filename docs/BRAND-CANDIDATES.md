# 브랜드 후보 조사

다음에 붙일 프랜차이즈 브랜드 후보를 조사한 결과다. **어댑터는 아직 없다.** 이 문서는 조사 결과일 뿐이다.

- 조사일: **2026-09-30**
- 조사 방법: 브랜드당 HTTP 5회 이내, 요청 간 2초 이상, `collectors/base.client()` (UA `sinsang-note/1.0`)
- 조사 범위: robots.txt + 홈 + 메뉴 페이지 구조 파악. **전체 메뉴를 긁지 않았다.**
- 추측으로 채운 칸은 없다. 못 본 것은 "확인 못 함"이라고 적었다.

이미 붙어 있는 9곳(메가MGC커피·스타벅스·이디야·CU·세븐일레븐·이마트24·맘스터치·롯데리아·버거킹)과
다른 에이전트가 작업 중인 5곳(BBQ·BHC·교촌·도미노·피자헛), 그리고 이미 조사가 끝난 GS25는 제외했다.

---

## 1. 판단 기준

`collectors/base.py` 의 `Item` docstring 그대로다. 우리는 카탈로그가 아니라 **신제품**을 모은다.

| 신호 | 강도 | 예 |
|---|---|---|
| `released_at` (브랜드가 알려주는 출시일/등록일) | **가장 강함** | 스타벅스 `new_SDATE`, 이삭토스트 `prdcode` |
| `is_new` (NEW 배지) | 강함 | 스타벅스 `newicon`, 폴바셋 `newIcon` |
| 신메뉴 전용 페이지·카테고리 | 강함 | 빽다방 `/menu/menu_new/`, 던킨 `sub=1` |
| 이미지 파일명 타임스탬프 | 약함 (`uploaded_at` 만) | 메가 `_uploaded_at()`, 할리스, 노브랜드버거 |
| 아무것도 없음 | 없음 | diff 로만 판정 → 합류 첫날 신제품 0건 |

**신호가 없는 브랜드는 아무리 유명해도 후순위다.** 메가MGC커피가 이미 그 처지다.

---

## 2. 전체 표

| 브랜드 | 카테고리 | URL | 수집 난이도 | 신제품 신호 | robots | 비고 |
|---|---|---|---|---|---|---|
| **이삭토스트** | 분식 | `isaac-toast.co.kr/menu/menu.php?ptype=list&catcode=…` | 쉬움 | **released_at + NEW 배지** | 허용 (`/admin/`,`/img/`,`/upload/` 제외) | `prdcode` 앞 6자리가 출시일. 상품 이미지는 `/admin/` 아래라 **핫링크는 robots 위반** |
| **파파존스** | 피자 | `pji.co.kr/menu/pizza` | 쉬움 | **NEW 배지 + NEW 필터 탭** | **robots.txt 없음 (404)** | `papajohns.co.kr` → `pji.co.kr` 리다이렉트. Next.js SSR, 가격까지 나옴 |
| **던킨** | 디저트 | `dunkindonuts.co.kr/menu?cat=1&sub=1` | 쉬움 | **신제품 전용 서브카테고리** | 허용 (`Allow: /`) | `sub=1` 이름이 "신제품". 대분류 5개(cat=1,2,3,5,6) |
| **설빙** | 디저트 | `sulbing.com/menu/` | 쉬움 | **NEW 배지** | 허용 (`/bbs/`,`/data/` 제외) | `www` 는 HTTPS 리셋. **apex 만 동작** |
| **폴바셋** | 카페 | `baristapaulbassett.co.kr/menu/List.pb?cid1=A…E` | 쉬움 | **NEW 배지 + NEW 전용 탭** | 허용 (`/common/coupon/` 제외) | `paulbassett.co.kr` 은 NXDOMAIN, `pbkorea.co.kr` 은 **무관한 풍선 쇼핑몰** |
| **빽다방** | 카페 | `paikdabang.com/menu/menu_new/` | 쉬움 | **신메뉴 전용 카테고리** | 허용 (`/wp-admin/` 제외) | WordPress SSR. 설명·영양정보까지 한 페이지에 |
| **굽네치킨** | 치킨 | `goobne.co.kr/menu/new_p?gubun=new_menu_list` | 쉬움 | **신제품 전용 페이지** | 허용 — 단 아래 ⚠️ | robots 가 `/menu/new.jsp` 를 **Disallow**. 우리 경로(`/menu/new_p`)는 허용이나 의도를 오해할 여지 |
| **커피빈** | 카페 | `coffeebeankorea.com/menu/list.asp?category=32` | 쉬움 | **"신음료" 카테고리** | 허용 (`Allow: /`) | ASP SSR. 메뉴 카테고리 14개 |
| **배스킨라빈스** | 디저트 | `baskinrobbins.co.kr/menu/fom.php` | 쉬움 | **이달의 맛 전용 페이지** | **robots.txt 없음 (404)** | 월 1~2건으로 적지만 정확. 전체는 `/menu/list.php?category=A…F` |
| **프랭크버거** | 햄버거 | `frankburger.co.kr/index_brand.html` | 쉬움 | **NEW 배지** (홈 슬라이더 15개 중 8개) | 허용 (`Allow:/`) | 전체 메뉴 페이지(`/html/menu_1.html`)의 배지 유무는 **확인 못 함** |
| **할리스** | 카페 | `hollys.co.kr/menu/espresso.do` 외 8개 | 쉬움 | 이미지 타임스탬프만 | 허용 (`/membership`,`/myHollys` 제외) | `menuEtc_202608200959255100.png` → `uploaded_at`. 메가와 같은 함정 주의 |
| **노브랜드버거** | 햄버거 | `shinsegaefood.com/nobrandburger/index.sf` | 쉬움 | 이미지 경로 날짜만 | **robots.txt 없음 (404)** | **홈 1요청에 전체 메뉴가 다 들어있다.** `/uimages/2026/04/30/…` 업로드일 |
| **파스쿠찌** | 카페 | `pascucci.co.kr/product/productList.asp?typeCode=…` | 쉬움 | **없음** | 허용 (`/cucciman/`,`/upload/` 제외) | 카테고리 ~15개 SSR. "시즌음료" 분류는 있으나 신제품 분류는 아님 |
| **미스터피자** | 피자 | `mrpizza.co.kr/bbs/board.php?bo_table=menu&sca=…` | 쉬움 | **없음** | 허용 (`/adm*/`,`/skin/` 제외) | gnuboard. 카테고리 11개. `wr_id` 오름차순이 등록순인지는 확인 못 함 |
| **처갓집양념치킨** | 치킨 | `cheogajip.co.kr/bbs/board.php?bo_table=allmenu` | 쉬움 | **없음** | 허용 (`Allow: /`) | gnuboard. "이달의 추천치킨"은 추천이지 신제품이 아니다 |
| **60계치킨** | 치킨 | `60chicken.co.kr/bbs/content.php?co_id=menu` | 쉬움 | **없음** | 허용 (`/adm/`,`/data/` 등 제외) | `60ke.co.kr`·`60ke.com` 은 **오답**(NXDOMAIN / 파킹). 전체 메뉴가 1페이지 |
| **더벤티** | 카페 | `theventi.co.kr` (신메뉴 경로 미확정) | 보통 | 신메뉴 전용 페이지 있음 | 허용 (`Allow: /`) | nav 에 "신메뉴"가 있으나 상대경로라 절대 URL **확인 못 함**(`/menu/new.html` 은 404) |
| **맥도날드** | 햄버거 | `mcdonalds.co.kr/kor/menu/burger` | 보통 | **확인 못 함** | 허용 (`Allow: /`) | Nuxt3. HTML·SSR 페이로드 어디에도 상품 없음. 내부 API base `…/api/v1` 만 확인, **엔드포인트 확인 못 함** |
| **KFC** | 햄버거 | `kfckorea.com/allmenu` | 보통 | 신메뉴 탭 있으나 상품목록 아님 | **robots.txt 없음 (404)** | `/promotion/newMenu` 는 SSR 이고 행사기간(9/8~11/9)도 나오지만 **프로모션 글**이지 상품 목록이 아니다 |
| **네네치킨** | 치킨 | `nenechicken.com` | 불가 | — | 허용 (`/manager/`,`/Program/` 제외) | 주문 SPA. 메뉴가 매장 선택에 종속(`/process/*.fuse`). HTML 에 상품 0건 |
| **컴포즈커피** | 카페 | `composecoffee.com` | 불가 | — | 허용 (게시판 일부 제외) | Rhymix + JS 렌더. `<body>` 가 스크립트 변수뿐. 내부 엔드포인트 **못 찾음** |
| **피자알볼로** | 피자 | `pizzaalvolo.co.kr` | 불가 | — | **robots.txt 가 HTML 반환** | `app.pizzaalvolo.co.kr` SPA 로 리다이렉트 |
| **투썸플레이스** | 카페 | `twosome.co.kr` | 불가 | — | **403** | CloudFront 가 robots.txt 조차 403. 봇 차단이 명시적 |
| **빕스** | 패밀리레스토랑 | `ivips.co.kr` | **금지** | — | **`User-agent: * / Disallow: /`** | Googlebot·NaverBot 만 허용. 우리는 명시적 차단 대상. 홈도 CJ ONE SSO 리다이렉트 |
| **푸라닭** | 치킨 | — | **확인 못 함** | — | — | `puradak.com` NXDOMAIN (`www` 가 죽은 apex 로 CNAME). 공식 도메인 못 찾음 |
| **김밥천국** | 분식 | — | **확인 못 함** | — | — | 상표를 공유하는 법인이 여럿이라 공식 도메인을 특정 못 했다 |
| **더본코리아(빽다방 외)** | 기타 | `theborn.co.kr` | — | — | 허용 (`Allow: /`) | 브랜드 소개 포털이고 메뉴가 없다. 홍콩반점·새마을식당 등 개별 사이트는 조사 안 함 |

---

## 3. 근거 (실측 조각)

추측과 구분하기 위해 실제로 받은 마크업을 남긴다.

**이삭토스트** — 신호가 가장 좋다. NEW 배지와 날짜가 둘 다 있다.
```html
<a href="/menu/menu.php?ptype=view&prdcode=2602230003&page=1&catcode=10101000">
  <dt><div class="icon"><img src="/img/new.svg" alt="NEW"/></div>
```
`prdcode` 는 `YYMMDD` + 순번이다. `2607100002` → 2026-07-10, `2609140001` → 2026-09-14,
`2306210007` → 2023-06-21. 목록도 이 값 기준 최신순으로 나온다.
**다만 스타벅스 `new_SDATE` 때와 같은 유보가 필요하다.** 이 6자리가 출시일인지 등록일인지는
브랜드가 명시하지 않았다. 어댑터를 쓸 때 여러 카테고리에서 실측해 분포를 확인하고 판단해라.

**폴바셋**
```html
<div class="menuList"><ul class="listStyleB"><li>
  <div class="iconArea"><span class="newIcon">New</span></div>
```
`cid1=A`(COFFEE) 한 페이지에 상품 61건, 그중 `newIcon` 5건 / `bestIcon` 10건.
`MENU > NEW` 전용 탭도 따로 있다.

**설빙**
```html
<ul class="menuList"><li><a href="menu_view.php?menu=166" class="item">
  <span class="flag"><img src="/new/images/icon_new.png" alt="new"></span>
```
`/menu/?type=설빙|사이드|음료` 3탭, 합쳐 31건.

**파파존스**
```html
불닭 까르보 치킨<span …><span class="… text-primary-red border-primary-red">NEW</span></span>
```
`/menu/pizza` 한 페이지에 "총 24개" + `ALL / NEW / BEST / SPECIALTY&THIN / CLASSIC / GREEN EAT` 필터 탭.
가격(L/F)까지 서버렌더로 들어있다.

**던킨** — 탭 이름이 그대로 "신제품"이다.
```html
<a … data-gtm-click="메뉴-신제품" href="https://www.dunkindonuts.co.kr/menu?cat=1&sub=1">신제품</a>
```

**빽다방** — `/menu/menu_new/` 렌더 텍스트 일부.
> 신메뉴 / 지금 바로 가까운 매장에서 빽다방 신메뉴를 만나 보실 수 있습니다. / 챔피언스 블랙 벨벳 라떼 HOT …

**굽네치킨** — `/menu/new_p?gubun=new_menu_list` 렌더 텍스트.
> 신제품 / 전체 치킨 피자 사이드 / 남해마늘바사삭 고추바사삭 마라천왕 갈비천왕

**커피빈** — `category=32` 가 "신음료". 상품이 서버렌더로 다 들어있다.
> Sparkling Apple Spice 스파클링 애플 스파이스 … Apple Pie Cream Latte 애플파이 크림라떼 …

**할리스 / 노브랜드버거** — NEW 배지는 없고 날짜만 있다.
```
//admin.hollys.co.kr/upload/menu/etc/menuEtc_202608200959255100.png
/uimages/2026/04/30/신메뉴_06.홈페이지_주스_(1).png
```
노브랜드버거 이미지 55건의 날짜 분포는 `2025-05-07` 24건이 최다다.
**메가MGC커피에서 81건이 2024-06 한 달에 몰렸던 것과 같은 일괄 재업로드 흔적**이다.
그대로 `released_at` 에 넣으면 오보가 된다. `uploaded_at` 까지만 써야 한다.

**빕스** — 우리를 명시적으로 막는 유일한 브랜드다.
```
# Robots.txt for https://www.ivips.co.kr
User-agent: *
Disallow: /

User-agent: Googlebot
…
Allow: /menu
```
`urllib.robotparser.can_fetch("*", "https://www.ivips.co.kr/menu")` → **False**.
붙이면 안 된다.

**굽네치킨 robots** — 이름이 비슷한 경로가 막혀 있다.
```
User-agent: *
Disallow: /menu/new.jsp
Disallow: /brd/notice/list
Allow:/
```
`can_fetch("*", ".../menu/new.jsp")` → False, `can_fetch("*", ".../menu/new_p?…")` → **True**.
경로가 다르니 규칙상 허용이지만, 브랜드가 "신메뉴 페이지를 크롤러에 보이기 싫다"는 뜻으로
막았을 가능성이 있다. 어댑터를 붙이기 전에 robots 를 다시 받아 확인하고,
`Disallow` 가 `/menu/new` 접두어로 넓어지면 즉시 빼야 한다.

---

## 4. 추천 순위 TOP 10

기준 순서는 **(1) 신제품 신호 → (2) 수집 난이도 → (3) 브랜드 관심도** 다.
신호가 없으면 아무리 유명해도 올리지 않았다.

| # | 브랜드 | 근거 | 예상 요청 수 |
|---|---|---|---|
| 1 | **이삭토스트** | 후보 중 **유일하게 `released_at` 을 실제로 채울 수 있다**(`prdcode` 날짜). NEW 배지도 별도로 있어 두 신호가 교차 검증된다. 붙는 날부터 신제품을 내놓는다 | 7 (카테고리 수) |
| 2 | **파파존스** | 상품별 NEW 배지 + NEW 필터 탭. Next.js SSR 이라 파싱이 안정적이고 가격까지 온다. 피자 카테고리는 지금 도미노·피자헛뿐이라 보강 효과도 크다 | 3~4 |
| 3 | **던킨** | 신제품이 **URL 로 분리돼 있다**(`sub=1`). 파싱 실패 위험이 가장 낮은 형태다. 인지도도 높다 | 5~6 |
| 4 | **설빙** | NEW 배지가 명확하고 전체가 3요청이면 끝난다. 디저트/빙수는 계절 신메뉴 회전이 빨라 서비스 성격에 잘 맞는다 | 3 |
| 5 | **폴바셋** | `newIcon` 배지 + NEW 전용 탭. SSR 안정. 다만 매장 수가 위 넷보다 적어 관심도는 한 단계 아래 | 5 |
| 6 | **빽다방** | 신메뉴 전용 카테고리가 통째로 있고 설명·영양정보까지 한 번에 온다. **매장 수 기준 국내 최상위권**이라 관심도는 이 목록 최고 | 5 |
| 7 | **굽네치킨** | 신제품 전용 페이지가 SSR 로 깔끔하다. ⚠️ robots 의 `/menu/new.jsp` Disallow 때문에 한 단계 내렸다. 붙이기 전 robots 재확인 필수 | 2 |
| 8 | **커피빈** | "신음료" 카테고리가 신호 역할을 한다. 배지가 아니라 카테고리라 `is_new=True` 는 줄 수 있어도 `False` 는 확인 못 하는 게 한계 | 14 (전 카테고리) |
| 9 | **배스킨라빈스** | "이달의 맛" 전용 페이지가 곧 신제품이다. 월 1~2건이라 양은 적지만 **오보 위험이 거의 없다.** robots.txt 가 없어 보수적 간격 필요 | 7 |
| 10 | **프랭크버거** | NEW 배지 확인(15개 중 8개). 전체 메뉴 페이지의 배지 유무를 확인 못 해서 10위. 확인되면 5위권 | 2~3 |

### TOP 10 에 넣지 않은 이유

- **맥도날드** — 관심도만 보면 1위 후보다. 하지만 상품이 HTML 에 없고 내부 API 엔드포인트를
  **확인 못 했다**(요청 5회 소진). 신제품 신호 유무도 모른다. **다음 조사 1순위**로 남긴다.
  `/_nuxt/entry.*.js` 를 받아 `api/v1` 하위 경로를 찾으면 바로 판정된다.
- **노브랜드버거** — 1요청에 전체 메뉴가 오는 최고의 수집 효율인데, **신호가 이미지 업로드일뿐**이다.
  메가와 같은 일괄 재업로드 흔적이 이미 보여서 `released_at` 로 못 쓴다. 11~12위권.
- **할리스** — 같은 이유. 이미지 타임스탬프만 있다.
- **파스쿠찌·미스터피자·처갓집·60계치킨** — 수집은 전부 쉽지만 **신호가 하나도 없다.**
  붙이면 합류 첫날 신제품 0건이고, 이후에도 diff 에만 의존한다. 카테고리 채우기용으로는
  쓸 수 있으나 우선순위는 뒤다.
- **KFC** — `/promotion/newMenu` 가 유일한 신호인데 상품 목록이 아니라 프로모션 글이다.
  글 제목을 상품에 끼워맞추는 건 `mega.py` 가 게시판을 쓰지 않기로 한 것과 같은 이유로 안 된다.
- **빕스** — robots 가 우리를 명시적으로 막는다. 순위 문제가 아니라 **붙이면 안 된다.**

---

## 5. 신제품 신호가 확실한 브랜드 (요약)

붙이는 날부터 신제품을 내놓을 수 있는 곳이다.

| 신호 종류 | 브랜드 |
|---|---|
| **출시일 (`released_at`)** | 이삭토스트 (`prdcode` 앞 6자리) |
| **NEW 배지 (`is_new`)** | 이삭토스트, 폴바셋, 설빙, 파파존스, 프랭크버거 |
| **신제품 전용 페이지·카테고리** | 빽다방, 던킨, 굽네치킨, 커피빈, 배스킨라빈스(이달의 맛), 파파존스(NEW 탭), 폴바셋(NEW 탭), 더벤티(경로 미확정) |
| 업로드일만 (`uploaded_at`) | 할리스, 노브랜드버거 |
| 없음 | 파스쿠찌, 미스터피자, 처갓집양념치킨, 60계치킨 |

---

## 6. 어댑터를 쓸 사람에게 넘기는 주의사항

1. **도메인부터 틀리기 쉽다.** 조사 중 실제로 틀린 것들:
   - 폴바셋 → `paulbassett.co.kr` 은 NXDOMAIN, `pbkorea.co.kr` 은 **풍선 쇼핑몰**(완전 무관).
     정답은 `baristapaulbassett.co.kr`
   - 파파존스 → `papajohns.co.kr` 은 `pji.co.kr` 로 리다이렉트
   - 60계치킨 → `60ke.co.kr` NXDOMAIN, `60ke.com` 은 파킹 IP. 정답은 `60chicken.co.kr`
   - 설빙 → `www.sulbing.com` 은 HTTPS 연결 리셋. apex `sulbing.com` 만 동작
     (스타벅스 `_live_host()` 같은 호스트 순회가 필요하다)
2. **robots.txt 가 없는 브랜드가 4곳이다** — 파파존스, 배스킨라빈스, KFC, 노브랜드버거(신세계푸드).
   부재는 금지가 아니지만 허용도 아니다. `CRAWLING-POLICY.md` 기준대로 **더 보수적인 간격**을 잡아라.
3. **피자알볼로는 robots.txt 자리에 HTML 을 돌려준다.** GS25 와 같은 패턴이니
   상태코드만 보고 "허용"으로 오판하지 마라.
4. **이삭토스트 상품 이미지는 `/admin/data/product2/` 아래**인데 robots 가 `/admin/` 을 Disallow 한다.
   HTML 파싱은 허용이지만 **이미지 직접 요청·핫링크는 robots 위반**이다.
   `img.79plus.co.kr` 핫링크 건(`CRAWLING-POLICY.md` §3)과 함께 처리 방침을 정해야 한다.
5. **이미지 파일명 날짜를 `released_at` 에 넣지 마라.** 할리스·노브랜드버거 둘 다
   메가와 같은 일괄 재업로드 흔적이 이미 보인다. `uploaded_at` 까지만이다.
6. **`BRANDS` 레지스트리에 세부분류를 먼저 등록해야 한다.** 이 후보들은 기존 3종(햄버거/피자/치킨)에
   없는 분류가 많다 — 디저트(던킨·배스킨라빈스·설빙), 분식(이삭토스트), 패밀리레스토랑 등.
   `base.py` 의 `BRANDS` 한 곳에서 정하는 원칙은 유지해라.

---

## 7. 확인 못 한 것

- **맥도날드 메뉴 API 엔드포인트** — `apiBase = https://www.mcdonalds.co.kr/api/v1` 까지만 확인.
  하위 경로와 신제품 필드 유무는 모른다.
- **더벤티 신메뉴 절대 URL** — nav 에 `../menu/new.html` 상대 링크가 있으나
  `/menu/new.html` 은 404. 실제 경로 못 찾음.
- **프랭크버거 전체 메뉴 페이지(`/html/menu_1.html`)의 NEW 배지 유무**
- **미스터피자 `wr_id` 가 등록순인지 여부** — gnuboard 관례상 그럴 가능성이 높지만 실측 안 함
- **푸라닭 공식 도메인** — `puradak.com` DNS 가 죽어 있다
- **김밥천국 공식 도메인** — 동일 상표 법인이 여럿이라 특정 못 함
- **더본코리아 산하 개별 브랜드**(홍콩반점·새마을식당·연돈볼카츠 등) — 빽다방만 조사했다
- **각 브랜드의 이용약관** — robots.txt 만 봤다. 이마트24처럼 **약관이 robots 와 어긋나는 사례**가
  이미 있으므로(`CRAWLING-POLICY.md` §4), 실제로 붙일 브랜드는 약관도 따로 확인해야 한다
