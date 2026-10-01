# 버그 전수조사 (BUG-SCAN)

- 조사일: **2026-10-01 11:20 ~ 11:55 (KST)**
- 대상 ①: **배포본** https://ttop32.github.io/sinsang-note/ — 조사 시점 배포는 `마지막 갱신 2026-10-01 11:23` 빌드(= commit `3d406a6` 무렵)
- 대상 ②: **작업 트리** `/Users/swkim72/source/sinsang-note` — HEAD `ca10085` + 미커밋 변경
- 방법: 소스 통독 → `data/products.json` 전수 계산(6,988행) → 빌드 산출물 651장 전수 파싱 → 실제 브라우저 조작(375px·데스크톱, 탭/칩/검색/정렬/404/상세/브랜드/유형) → 외부 링크 56개 HTTP 확인

> ⚠️ **조사 중에 다른 에이전트(main)가 `collect.py`·`collectors/base.py`·`web/pages.py` 와 `docs/` 를
> 계속 다시 만들었다.** 11:39·11:41·11:46·11:51 에 빌드가 바뀌었다. 항목마다 **어느 시점·어느 대상에서
> 쟀는지** 적었다. "현재 상태" 는 **11:54 작업 트리** 기준이다.
> `git status` 에 보이는 다른 에이전트 변경(`collect.py`, `collectors/base.py`, `collectors/cafe_hollys.py`,
> `docs/*.md`)은 내 것이 아니다. 이 파일(`docs/BUG-SCAN.md`) 외에는 아무것도 건드리지 않았다.

---

## 요약

| 구분 | 건수 |
|---|---|
| A. 심각 — 사용자가 바로 본다 | 2 |
| B. 같은 규칙이 두 군데 이상 (한 곳만 고친 것) | 9 |
| C. 조용한 실패 · 상태 오염 | 4 |
| D. 데이터·분류 | 3 |
| E. 공개 노출 | 1 |

**재현 못 한 것(= 버그로 올리지 않음)**: CSS·JS 부분치환 잔해(§G-1), 단어목록 한국어 오탐(§F),
주류·비식품 누출(§G-3), 탭·칩·검색·정렬 동작(§G-2), 깨진 내부링크(11:51 빌드 기준 0건, §B-2 참고).

---

## A. 심각 — 사용자가 바로 본다

### A-1. 하위 **647장 전부**에서 카드 이미지가 세로 400px 로 늘어난다 — `.c img{height:auto}` 가 홈에만 있다

**증상**
카드 이미지가 정사각형이 아니라 **폭 무관 높이 400px 고정**. 375px 2열에서 164×400 (2.44:1),
데스크톱 3열에서 226×400 (1.77:1). 제품이 세로로 길게 잘려 화면 밖으로 나간다.
홈(`/`)만 정상(164×164).

**재현 (브라우저)**
1. `https://ttop32.github.io/sinsang-note/` 를 열고 콘솔:
   `getComputedStyle(document.querySelector('.c img')).height` → `164px` (정상)
2. `https://ttop32.github.io/sinsang-note/b/설빙/` 로 이동해 같은 줄 실행 → **`400px`**
3. 아무 상세 페이지(`/p/설빙-흑절미설빙/`)로 가서 "설빙의 다른 신제품" 추천 카드에 같은 줄 실행 → **`400px`**
   (히어로 이미지만 341×341 로 정상)

**재현 (로컬, 네트워크 없이)**
```
grep -n "\.c img" collect.py web/pages.py web/theme.py
# collect.py:394  .c img{height:auto}        ← 홈만
# web/theme.py:48 .c img,.ph{width:100%;aspect-ratio:1;object-fit:cover;...}  ← height 선언 없음
# web/pages.py    없음                        ← 하위 페이지 전부 누락
```

**파일:줄**
- `collect.py:394` — `.c img{height:auto}` (홈 전용 `CSS_EXTRA`)
- `web/theme.py:48` — `.c img,.ph{...}` 에 `height` 선언 없음
- `web/pages.py:40~57` `EXTRA_CSS` — `.hero img` 에만 `height:auto` 가 있고 `.c img` 는 없음
- `web/pages.py:115` / `collect.py:426` — `<img width="400" height="400">` 속성이 UA presentational hint 로
  `height:400px` 를 만들고, 저자 CSS 가 `height` 를 안 덮어서 `aspect-ratio:1` 이 무시된다

**영향 범위** 하위 **647 페이지 / 카드 이미지 4,748장** (상세 548 + 브랜드 42 + 유형 21 중 이미지 있는 647장).
상세 페이지가 검색 유입의 본체인데, 그 페이지 하단 추천 그리드가 전부 깨진 모양이다.

**심각도 — 높음.** 배포본·작업 트리 **둘 다 현재 깨져 있다**(11:54 재확인).

> 🔴 **기존 `docs/BUG-REPORT.md` A-1 의 기술이 틀렸다.**
> 거기서 "같은 레포의 상세 페이지 CSS(`web/pages.py:38`)에는 `height:auto` 가 들어 있어 상세 페이지만
> 정상이다" 라고 썼는데, 그 줄은 `.hero img` 규칙이다(현재 `web/pages.py:46`). 카드(`.c img`)에는 없다.
> 그래서 "홈만 고치면 끝" 으로 처리됐고, **A-1 은 닫힌 게 아니라 647장에 그대로 남아 있다.**
> A-2(NEW 중복)·C-3 에 이어 **세 번째 "홈에서만 고쳐진" 항목**이다.

---

### A-2. 에그드랍 상품 사진이 깨진다 — `http://` 이미지 + 만료된 인증서

**증상** 카드 자리가 빈 회색 네모로 남는다. 콘솔에 Mixed Content 경고 + `net::ERR_CERT_DATE_INVALID`.

**재현**
1. 배포본 홈을 열고 콘솔:
   `[...document.querySelectorAll('.c img')].filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.src)`
   → `http://www.eggdrop.co.kr/upload/menu/...png` **4장**
2. 원인 확인:
   ```
   echo | openssl s_client -servername www.eggdrop.co.kr -connect www.eggdrop.co.kr:443 2>/dev/null \
     | openssl x509 -noout -dates
   # notAfter=May 27 06:57:28 2025 GMT   ← 1년 4개월 전 만료
   ```
   브라우저가 mixed content 를 https 로 자동 승격 → 인증서 오류 → 로드 실패.

**파일:줄** 데이터 쪽 문제. `data/products.json` 의 에그드랍 `image` 73건이 전부 `http://`.
`collectors/sandwich_eggdrop.py` 가 사이트가 주는 http URL 을 그대로 쓴다.
(`collectors/base.py` SITES 의 `에그드랍`·`노티드` 도 http 지만, 그건 **최상위 이동**이라 깨지지 않는다 —
깨지는 건 **이미지 서브리소스**뿐이다.)

**영향 범위** 현재 빌드에서 **9개 문서**(홈 + 상세·브랜드·유형 8장), 홈에서 눈에 보이는 건 4장.
덧붙여 그 상품들의 `og:image`·JSON-LD `image` 도 http 라 공유 카드·구조화 데이터에서도 이미지가 안 뜬다.

**심각도 — 중간.** (건수는 적지만 "사진 보러 오는 사이트" 에서 빈 네모다)

---

## B. 같은 규칙이 두 군데 이상 — 한 곳만 고치면 조용히 어긋난다

### B-1. 라벨 필터 (PROMO/DUP) — **조사 중 main 이 고쳤다. 배포본에는 남아 있다**

**측정 (11:38, 수정 직전 빌드)**
```
NEW 배지 바로 뒤 NEW계열 칩 :  1,024건 / 148페이지   (홈 0건)
행사 라벨 칩(1+1·2+1·증정·할인): 378건 /  49페이지   (홈 0건)
  내역: 2+1 177, 증정 90, 1+1 80, 할인 31
  상위: b/cu 40, c/편의점 40, c/굿즈 38, c/햄버거 19, c/치킨 13
```
**11:39 에 main 이 `base.shown_labels()` 로 정본화**(`collectors/base.py:290`, `web/pages.py:121,170`,
`collect.py:431`). 11:41 이후 빌드에서 0건 재측정 확인.
**배포본(11:23 빌드)에는 아직 그대로 있다** — 다음 배포 전까지는 사용자가 본다.

**심각도 — (수정됨) / 배포본 기준 높음**

---

### B-2. "유형" 의 정의가 `collect.render` 와 `web/pages` 에서 다르다 → 홈 푸터가 404 로 링크

**증상** 홈 푸터의 분류 링크 중 일부가 생성되지 않은 유형 페이지를 가리킨다.

**재현 (11:46~11:48 빌드에서 실제 재현)**
```
$ grep -o 'href="/sinsang-note/c/[^"]*"' docs/index.html | sort -u
  ... href="/sinsang-note/c/카페/" ...
$ test -d docs/c/카페 && echo 있음 || echo 없음
없음                      ← 홈 푸터 링크가 404
$ grep -c "c/카페" docs/sitemap.xml
0                         ← sitemap 은 안 넣었다(두 경로가 서로 다르게 판단한다는 증거)
```
같은 메커니즘으로 **11:38~11:48 사이 `/c/디저트/` 가 8개 페이지(홈 + 던킨·배스킨라빈스 상세 6장 + 1)에서
404** 였다. (`docs/c/디저트/index.html` 이 `_sweep` 에 삭제된 상태 = `git status` 의 `D` 표시)

**파일:줄**
- `collect.py:494` — 푸터 링크는 **3중 or**:
  `primary_of(r)==k or r.get("brand_sub")==k or r.get("brand_type")==k`
- `web/pages.py:67` `_kind(r)` — 페이지 생성은 **2중 or**: `brand_sub or brand_type`
- `web/pages.py:23` `_kinds()` 는 `collect.SECTIONS` 를 정본으로 쓰지만, **행이 어느 유형에 속하는지**를
  판정하는 쪽은 공유하지 않는다. `SECTIONS` 에 있지만 어떤 행의 `_kind` 도 아닌 값(예: `카페`, `외식`),
  반대로 어떤 행의 `_kind` 이지만 `SECTIONS` 에 없는 값(예: `디저트`) 둘 다 링크 깨짐을 만든다.

**현재 상태** 11:51 빌드에서 main 이 `web/pages.py:295 RETIRED` 로 "비워진 유형은 안내 페이지를 남긴다"
는 땜질을 넣어 **지금은 깨진 링크 0건**이다. 다만 **두 곳의 판정 규칙이 여전히 다르다** — 분류 축을 또
바꾸면 같은 방식으로 재발한다.

**영향 범위** 재현 시점 기준 홈 1장 + 상세 6장. **홈 푸터라 전 사용자 노출.**

**심각도 — 높음(재현 시점) / 현재는 땜질됨, 구조는 남음**

---

### B-3. 사이트 루트 `/sinsang-note/` 가 네 군데에 따로 적혀 있다

| 위치 | 방식 |
|---|---|
| `web/theme.py:11` `BASE_URL` | 정본 |
| `web/theme.py:84~87` | **하드코딩** `/sinsang-note/icon.svg`, `icon-180.png`, `manifest.webmanifest`, `feed.xml` |
| `collect.py:94` `ROOT_PATH = "/sinsang-note/"` | **하드코딩** |
| `web/pages.py:36` | `BASE_URL` 에서 유도 |
| `web/assets.py:209` `_root()` | `BASE_URL` 에서 유도 |

`BASE_URL` 을 바꾸면 유도하는 두 곳만 따라가고, **하드코딩된 다섯 줄은 조용히 틀린 주소를 가리킨다**
(파비콘·터치아이콘·매니페스트·피드·홈의 모든 내부 링크).
`web/theme.py:94` 주석이 "페이지 생성기와 sitemap 이 각자 경로를 만들면 반드시 어긋난다. 여기서만 만든다"
라고 못박아 놓고, 바로 열 줄 아래에서 스스로 하드코딩한다.

**심각도 — 낮음(지금은 값이 일치)** / 리네임·도메인 변경 시 전면 붕괴

---

### B-4. 방문자 분석 스크립트가 **404 페이지에만** 들어간다

`web/assets.py:269 analytics_snippet()` 의 유일한 호출처는 `web/assets.py:297`, 즉 `_404()` 안이다.
```
$ grep -rn "analytics_snippet()" collect.py web/*.py
web/assets.py:297:{analytics_snippet()}
```
`ANALYTICS["enabled"]=True` 로 켜면 **홈·상세 548장·브랜드 42장·유형 21장 어디에도 안 붙고 404 만 계측된다.**
`theme.head()` 가 아니라 404 전용 템플릿에 끼워 넣은 탓이다.

**심각도 — 낮음(현재 off)** / 켜는 순간 조용히 무용지물

---

### B-5. `web/seo.py` 의 JSON-LD 빌더 3종이 **아무 데서도 안 쓰인다** (죽은 중복 구현)

```
$ grep -rn "product_jsonld\|itemlist_jsonld\|website_jsonld" collect.py web/*.py collectors/*.py
web/seo.py:214:def product_jsonld(...)
web/seo.py:235:def itemlist_jsonld(...)
web/seo.py:252:def website_jsonld(...)
# 정의뿐, 호출 0
```
`web/pages.py:97 _ld()` 가 Product/BreadcrumbList/ItemList 를 **따로** 만든다. 이스케이프 규칙도 다르다
(pages 는 `<`→`<`, seo 는 `</`→`<\/` + `<!--`).
덤으로 **홈(`/`)에는 JSON-LD 가 하나도 없다** — `website_jsonld()` 가 준비돼 있는데 `collect.render` 가
`theme.head(...)` 를 `jsonld=` 없이 부른다(`collect.py:500` 부근).

**심각도 — 낮음 (SEO 기회손실 + 다음 수정자가 틀린 쪽을 고칠 위험)**

---

### B-6. 보도자료 어댑터 4종이 같은 단어목록을 복붙했고 **이미 갈라졌다**

| 모듈 | `_VERB` | `_SKIP` |
|---|---|---|
| `collectors/maker_ottogi.py:43,51` | `출시\|선봬\|선보여\|선보인다\|론칭` | 38개 |
| `collectors/maker_orion.py:51,57` | 〃 (동일) | 〃 (동일) |
| `collectors/maker_lottewellfood.py:58,64` | 〃 (동일) | 〃 (동일) |
| `collectors/gs25.py:110,123` | **+ `상품화\|제안\|첫 선`** | **+16개** |

gs25 에만 있는 16개: `구독 로봇 매장 배달 서비스 수출 시리즈 앱 오픈 이벤트 점포 창업 택배 플랫폼 할인 혜택`.
즉 **같은 성격의 기사를 네 어댑터가 서로 다른 기준으로 거른다.** `_SINGLE`·`_HEAD`·`_MULTI`·`_TRAIL_SEP`·
`_BETWEEN`·`_TAIL` 도 같은 식으로 네 벌이다.

⚠️ 그중 `"앱"` 은 **한 글자**다. 한국어는 단어 경계가 없어서 기사 제목 아무 데나 걸린다
(이 목록이 이미 겪은 `카스`→카스테라, `럼`→쿠키크럼블 과 같은 종류의 위험).
gs25 보도자료 제목을 받아올 수 없어 오탐 수는 **실측 못 했다 — 미확인**.

**덤: `collectors/maker_lottewellfood.py` 는 배선돼 있지 않다.**
`collect.ADAPTERS`(`collect.py:40~56`)에 없고 `base.BRANDS` 에 `롯데웰푸드` 도 없다
(넣으면 `base.kind()` 가 `KeyError`). 175줄짜리 죽은 어댑터다.

**심각도 — 낮음 (지금 수집 결과에 영향 없음) / `maker_lottewellfood` 는 死코드**

---

### B-7. `_uploaded_at()` (이미지 Last-Modified → 날짜) 가 두 어댑터에 복붙돼 있다

`collectors/chicken_bbq.py:35` 와 `collectors/chicken_kyochon.py:80`. 로직·주석("실패하면 조용히 비운다")까지 동일.
한쪽만 고치면 치킨 두 브랜드의 날짜 판정이 갈라진다.

**심각도 — 낮음**

---

### B-8. 푸터가 **세 벌** 로 구현돼 있다

- `collect.py:527~529` (홈): `마지막 갱신 … · {count}` + 분류링크 + `theme.NOTICE`
- `web/pages.py:133~135` (`_shell`): 사이트명 링크 + 태그라인 + `theme.NOTICE`
- `web/assets.py:307` (`_404`): `theme.NOTICE` 만

문구 자체(`theme.NOTICE`)는 정본화됐지만 **구조는 세 군데에 흩어져 있다.**
그 결과 404 페이지에는 홈으로 가는 푸터 링크도, 태그라인 줄도 없다.

**심각도 — 낮음**

---

### B-9. `_when()` 이 두 벌 (`collect.py:289`, `web/pages.py:62`)

주석이 "순환 import 때문에 사본" 이라고 인정하고 있다. `web/seo.py` 는 `collect._when` 을 import 해 쓴다
(즉 **세 모듈이 두 가지 구현을 섞어 쓴다**). 지금은 내용이 같다.
같은 식으로 `_img_url`(`pages.py:77`) ↔ `_ext_url`(`seo.py:44`), `_kind`(`pages.py:67`) ↔
`_kind_of`(`seo.py:71`) 도 쌍으로 존재한다.

**심각도 — 낮음(현재 동일) / §B-2 가 실제로 이 쌍에서 터졌다**

---

## C. 조용한 실패 · 상태 오염

### C-1. 수집 실패한 브랜드의 이전분(`carried`)은 **`brand_type`·`brand_sub` 만 갱신**된다 — 나머지 필드는 영구 stale

**코드**
```python
# collect.py:158~161
carried = [p for p in prev.values() if p["brand"] in failed_brands]
for c in carried:
    c["brand_type"], c["brand_sub"] = base.kind(c["brand"])   # ← 이 두 개만
rows += carried
```
`nonfood`·`alcohol` 은 `Item.to_dict()`(`collectors/base.py:311~319`)에서만 계산된다.
**carried 행은 `to_dict()` 를 안 거치므로, 단어목록을 아무리 고쳐도 그 브랜드는 옛 판정을 유지한다.**
필드 자체가 없으면 `is_fresh` 의 `bool(r.get("nonfood")) != goods` 가 `None`→거짓으로 읽어 **식품 목록으로 샌다.**

**재현 (git 으로 실측 — 현재 파일이 아니라 커밋된 스냅샷)**
```
$ git show 200445c:data/products.json | ./.venv/bin/python -c "
import json,sys,collections
ps=json.load(sys.stdin)['products']
m=[p for p in ps if 'nonfood' not in p]
print(len(ps),'행 중',len(m),'행에 nonfood 키가 아예 없음',
      collections.Counter(p['brand'] for p in m).most_common(4))"
6835 행 중 385 행에 nonfood 키가 아예 없음
[('이마트24',357),('CU',14),('파리바게뜨',9),('배스킨라빈스',2)]
```
그중 실제 오분류 1건을 확인했다:
`이마트24 | 엘라스틴)아이스스칼프클리닉샴푸480ml` — 저장값 `nonfood` 없음(=식품 취급),
현행 규칙으로 다시 계산하면 `nonfood=True`.

**현재 상태** 11:51 재수집 뒤 `data/products.json` 6,988행은 **깨끗하다**(키 누락 0, 레지스트리 불일치 0).
즉 **지금 터져 있지는 않지만, 어댑터가 하나라도 실패하는 날 바로 재발한다.**
(같은 메커니즘으로 2026-10-01 오전에는 `brand_type`/`brand_sub` 가 **2,851행(41.7%)** 어긋나 있었고,
그 결과 11:41 빌드에서 "카페" 탭의 2단 칩이 통째로 비고 파리바게뜨가 "외식 > 베이커리" 로 들어가 있었다.)

**심각도 — 중간 (잠복)**

---

### C-2. `STALE = 90` 은 **어디서도 쓰이지 않는다** — 그런데 주석 세 군데가 쓰인다고 말한다

```
$ grep -rn "STALE" collect.py web collectors
collect.py:72:STALE = 90
collectors/snack_kimbabcheonguk.py:23:  ... collect 의 STALE
collectors/cafe_coffeebean.py:19:  ... collect.py 의 STALE 가지치기가
```
`collect.py:69~72` 주석은 "배지를 믿되 날짜가 이만큼(90일) 지났으면 신제품이 아니라고 본다" 고 적었지만,
`is_fresh()`(`collect.py:298~`)에는 그 분기가 없다. 날짜가 있으면 `WINDOW`(60) 로, 날짜가 없으면 **무조건 배지를 믿는다**.

**현재 영향 측정** 화면에 올라간 525건 중 **날짜 근거 없이 배지만으로 통과한 것 279건**
(세븐일레븐 40, CU 40, 팔도 40, 스시로 40, 커피빈 28 …).
다만 그중 `first_seen` 이 60일보다 오래된 건 **0건**이라, **지금은 눈에 보이는 피해가 없다**.
(주석이 근거로 든 "이디야 2017년 상품" 은 현재 데이터에 남아 있지 않아 **재현 못 함 — 미확인**.)

**심각도 — 낮음 / 문서와 코드 불일치**

---

### C-3. 실패를 빈 값으로 삼키는 자리

| 위치 | 삼키는 것 | 결과 |
|---|---|---|
| `collectors/chicken_bbq.py:39~50`, `chicken_kyochon.py:84~88` | 이미지 HEAD 전부(`except Exception`) | `uploaded_at=""` → 날짜 근거 상실, 전건이 "오늘 처음 봄" 으로 흐른다 |
| `collectors/pizza_pizzahut.py:95~100` | 이미지 후보 HEAD | `image=""` → 사진 없는 카드 |
| `collectors/cu.py:116~120` | 상세 HTTP 오류 | `desc=""` |

전부 "부가 정보" 라 예외를 안 올리는 건 설계상 맞지만, **대량 실패해도 `FLOOR` 가드에 안 걸린다**
(건수는 그대로고 날짜·사진만 비니까). 조용한 품질 저하 경로다.

**심각도 — 낮음 (잠복) / 실측 불가 — 미확인**

---

### C-4. `FLOOR` 급감 가드가 다중 브랜드 어댑터에서는 **합계** 로만 돈다

`collect.py:141~144` 의 `before` 는 `names`(어댑터가 담당하는 브랜드 전부)의 합이다.
`bon_if` 는 브랜드 8종을 한 어댑터가 가져온다 — 그중 7종이 0건이 돼도 1종이 충분히 많으면
`len(items) >= before*0.7` 을 통과한다. "셀렉터 하나 깨지면 조용한 부분수집" 이라는 바로 그 시나리오를
8브랜드 어댑터에서는 못 잡는다.

**심각도 — 낮음 (잠복)**

---

## D. 데이터·분류

### D-1. `drop_sets()` 가 **진짜 신제품 24건** 을 떨어뜨린다 (그중 ~9건은 명백한 오탐)

`collect.py:276` `_SET = re.compile(r"세트|콤보")` 는 **이름에 '세트'/'콤보' 가 들어가기만 하면** 떨군다.
docstring 은 "본품이 없는 조합 상품(구성·할인)" 만 거른다고 하지만, 실제로는
**본품이 따로 없는 모든 '세트' 상품** — 즉 세트로만 파는 정상 신제품까지 사라진다.

**재현**
```
./.venv/bin/python - <<'PY'
import json,sys,datetime; sys.path.insert(0,'.')
import collect
ps=json.load(open('data/products.json',encoding='utf-8'))['products']
t=datetime.date.today().isoformat()
sel=[r for r in ps if collect.is_fresh(r,t)]
sel.sort(key=lambda r:(collect._when(r),r['brand']),reverse=True)
m=collect.merge_variants(sel); d=collect.drop_sets(m)
print(len(sel),'→',len(m),'→',len(d))
for r in m:
    if r not in d: print('  ',r['brand'],'|',r['name'])
PY
# 1449 → 1429 → 1405   (24건 소멸)
```

**명백한 오탐 (조합·할인이 아니라 그 자체가 상품)**
- 던킨 `학화 호도 먼치킨 세트(5개입)`
- 브레댄코 `더치팩쿠키선물세트(중)`
- 스타벅스 `러스크 어소트먼트 세트`, `풀문 잼 쿠키 세트`
- 파리바게뜨 `행복만주 세트`
- 맥도날드 `진주 고추 크림치즈 머핀 세트`, `맥크리스피™ 고추장 버터 세트`, `맥스파이시® 고추장 버터 세트`
- 굿즈 쪽에서도 1건: CU `애경)실속형여행용세트`

(의도대로 걸린 것: 맘스터치 `싱글피자N버거세트`, BBQ `황올한마리+버거세트`, 미스터피자 `피치 세트 M(배달)` 등)

**영향 범위** 화면 목록에서 사라질 뿐 아니라 **상세 페이지 자체가 생성되지 않는다**
(`pages.build()` 가 `pick()` 결과만 받는다) → 그 상품들은 검색 유입 경로가 없다.
전체 데이터 기준으로는 **140건**이 "본품 없는 세트" 로 분류돼 같은 운명이다(맥도날드 세트 라인업 전체 포함).

**심각도 — 중간**

---

### D-2. `ICE` 와 `ICED` 칩이 섞여 나온다

현재 빌드 전수:
```
$ cat docs/index.html docs/p/*/index.html docs/b/*/index.html docs/c/*/index.html \
  | grep -o '<span class="lb lb2">[^<]*</span>' | sed 's/<[^>]*>//g' | sort | uniq -c | sort -rn
 177 ICE
 130 시즌메뉴
  96 ICED
  40 HOT
  ...
```
같은 뜻인데 브랜드별 표기를 그대로 내보낸다. `collectors/base.py:_SIZE` 는 **키 계산** 할 때만
`ICE|ICED` 를 동일 취급하고, **화면 표기** 는 정규화하지 않는다.

**심각도 — 낮음 (미관)**

---

### D-3. 굿즈 유형 페이지가 식품 문구를 그대로 쓴다

`/c/굿즈/` 의 제목·리드·메타가 `kind_page()`(`web/pages.py:275~288`) 공용 문구다:
- `<title>` "**굿즈 신상** — 2026년 10월 | 신상노트"
- 리드 "최근 **신제품** 56건"
- meta description "굿즈 **신제품** … CU, 매머드커피, 세븐일레븐, 파파존스, 할리스 **신메뉴** 를 한 곳에서 봅니다."

텀블러·키링 목록에 "신메뉴" 라고 쓴다. 56장짜리 페이지 하나.

**심각도 — 낮음**

---

## E. 공개 노출

### E-1. 내부 기획·검수 문서 24개(1.1MB)가 공개 웹에 200 으로 서빙된다

`docs/` 가 GitHub Pages 의 퍼블리시 디렉터리인데 기획 문서가 같은 자리에 있다.
`robots.txt` 는 `Allow: /` 로 전부 허용한다(`web/seo.py:132 _robots()`).

```
$ for u in BACKLOG.md ASSIGNMENTS.md BUG-REPORT.md CRAWLING-POLICY.md QA-REPORT.md; do
    printf "%-22s " $u; curl -s -o /dev/null -w "%{http_code} %{size_download}\n" \
      "https://ttop32.github.io/sinsang-note/$u"; done
BACKLOG.md             200 56907
ASSIGNMENTS.md         200 46188
BUG-REPORT.md          200 23361
CRAWLING-POLICY.md     200 35702
QA-REPORT.md           200 74324
```
`CRAWLING-POLICY.md` 에는 **"이용약관이 수집을 금지하지만 운영자 판단으로 수집한다"** 는 판단 근거가
브랜드명과 함께 적혀 있다(`collectors/base.py:98~102` 와 같은 내용). 공개 읽기 가능 상태다.
sitemap 에는 없어서 크롤 유입 가능성은 낮지만, 주소를 알면 누구나 받는다.

**심각도 — 중간 (평판·법무 쪽)**

---

## F. 단어 목록 전수 검사 — **현행 목록에 한국어 오탐 0건**

전체 `data/products.json`(6,988행)에 대고 돌린 결과. (`collectors/base.py` 는 조사 중 main 이 갱신했다 —
11:44 시점 버전 기준)

| 목록 | 적중 | 식품 오탐 | 비고 |
|---|---|---|---|
| `NONFOOD_WORDS` (30단어) | 136행 | **0** | 전부 진짜 굿즈·생활용품 |
| `ALCOHOL_WORDS` (54단어) | 216행 | **0** | 전부 진짜 주류 |
| `ALCOHOL_PREFIXES` (10개, `X)` 접두) | 118행 | **0** | |
| `PROMO_LABELS` / `DUP_LABELS` | — | **0** | 완전일치 집합이라 부분일치 위험 없음 |

과거 사고(`핸디`→스타벅스 핸디 젤리, `카스`→카스테라 28건, `럼`→쿠키크럼블)는 **전부 해소돼 있다.**
`is_nonfood`/`is_alcohol` 을 전 데이터에 다시 돌려 저장값과 비교했을 때 불일치 **0건**(11:54 기준).

**죽은 단어 (한 건도 안 걸림)** — 지우면 목록이 짧아진다
- `NONFOOD_WORDS`: `에코백 칫솔 치약 핸드크림 앞치마 쇼핑백 보온병 방향제 손소독` (9개)
- `ALCOHOL_WORDS`: `흑맥주 발포주 데낄라 브랜디 와인 시라즈 리슬링 산지오베제 스타우트` (9개)
  — `와인` 이 0건인 건 이마트24 가 `레드)`/`화이트)` 접두를 쓰기 때문

**측정 못 한 것**: 보도자료 어댑터의 `_SKIP`/`_VERB`(§B-6). 대상이 상품명이 아니라 기사 제목이라
`products.json` 으로는 대리측정만 된다. `gs25._SKIP` 의 한 글자 `"앱"` 은 위험하지만 **미확인**.

---

## G. 재현 안 된 것 (버그 아님 — 기록용)

### G-1. 부분치환 잔해 — **없다**
- CSS 4블록(`theme.CSS`, `collect.CSS_EXTRA`, `pages.EXTRA_CSS`, `assets._404_CSS`) 전부
  **중괄호 균형 0, 블록 밖에 떠 있는 선언 0개**. 같은 셀렉터가 두 블록에 겹쳐 적힌 것도 0개.
  (단 `.c img` 는 `theme.CSS` 의 `.c img,.ph` 와 `collect.CSS_EXTRA` 의 `.c img` 로 **셀렉터 문자열이 달라**
  이 검사에 안 걸렸다 → §A-1)
- JS: 홈에서 탭·칩·검색·정렬 전부 동작하고 **콘솔 JS 에러 0건**(이미지 에러만). 선언 없는 심볼 없음.

### G-2. 브라우저 조작 전수 — 정상
| 조작 | 결과 |
|---|---|
| 1단 탭 4개 | 배지 숫자 = 실제 표시 카드 수 (300/121/80/99), `cnt` 일치 |
| 2단 칩 10개 | 전부 `allMatch=true`(보이는 카드가 전부 그 `data-s`), 배지 숫자 일치 |
| 칩 재클릭 | 해제돼 전체 복귀(300) |
| 1단 전환 | 2단 선택 자동 초기화(`subOn=0`), 검색어는 유지(의도대로 보임) |
| 조합 (외식+피자+"치즈") | 12 → 1건, 정상 |
| 검색 `라떼`/`Latte`/`스타벅스` | 28 / 13 / 3건 |
| 검색 `브랜드에서 보기`·`자세히 보기`·`NEW` | **0건** — UI 문구·배지가 색인에 안 들어간다(의도대로) |
| 검색 지움 | 300건 복귀, `cnt` 비움, `#noresult` 숨김 |
| 정렬 토글 ×2 | 최신순↔브랜드순 왕복, 원래 순서 완전 복원 |
| 375px | 가로 스크롤 **없음**(`scrollWidth==innerWidth==375`), 1단 탭 4개 다 보임, 2단만 가로 스크롤 |
| 404 (`/c/없는주소/`) | GitHub Pages 가 404.html 서빙, `noindex,follow`, canonical=홈, 홈 버튼 정상 |
| 상세 `/p/…` | 히어로 정사각, 빵부스러기 4단, dl 4행, JSON-LD 존재, canonical 정상 |
| sitemap / feed | XML 파싱 OK, sitemap 647 URL **전부 실제 파일 존재**, 빌드됐는데 누락된 페이지 0, feed entry 50 |
| 외부 "브랜드에서 보기" 폴백 56개 | **전부 200** (BBQ·굽네 포함 — BUG-REPORT A-4/A-5 는 해소됨) |

사소한 관찰 하나: 정렬을 한 번 누르면 `#noresult` 문단이 `main.g` 의 **첫 자식** 으로 밀린다
(모든 카드를 `appendChild` 로 뒤에 붙이기 때문, `collect.py:609~611`). 숨김 상태라 **화면 영향 0**.

### G-3. 주류·비식품 누출 — **0건**
화면에 올라간 식품 525건 + 굿즈 56건 전수를 현행 `is_alcohol`/`is_nonfood` 로 다시 판정 → 섞인 것 0.
`category == "주류"` 인데 `alcohol=False` 인 행도 0.

### G-4. 키 충돌·슬러그 충돌 — **0건**
6,988행 전부 고유 `make_key`(`load_previous()` 가 조용히 덮어쓰는 행 0).
`fresh` 안 상세 슬러그 충돌 0, 60자 절단 0.

---

## H. 미확인 (재현 못 함 — 추측으로 올리지 않음)

1. `gs25._SKIP` 의 한 글자 `"앱"` 이 기사 제목에서 만드는 오탐 수 — 제목 코퍼스 없음
2. `STALE` 주석이 근거로 든 "이디야 2017년 상품 / 버거킹 31%" — 현재 데이터에 없음
3. `_uploaded_at`·`_image` 의 대량 실패 시나리오 — 외부 서버 상태 의존
4. `FLOOR` 가드가 `bon_if` 8브랜드에서 뚫리는 실제 사례 — 어댑터 실패를 만들어내야 함
5. 배포본과 작업 트리의 차이로 생기는 항목(§B-1, §B-2)은 **다음 배포 뒤 재확인 필요**

---

## 우선순위 제안

| 순위 | 항목 | 근거 |
|---|---|---|
| 1 | **A-1** `.c img{height:auto}` 를 `web/theme.py:48` 로 올린다 | 647페이지 4,748장, 지금 깨져 있다. `collect.CSS_EXTRA`·`pages.EXTRA_CSS` 둘 다에서 빼고 정본 한 곳으로 |
| 2 | **B-2** 유형 판정을 한 함수로 합친다 | 홈 푸터 404 가 이미 두 번 났다. `RETIRED` 는 땜질 |
| 3 | **C-1** `carried` 행도 `nonfood`/`alcohol` 재계산 | 어댑터 실패일마다 재발하는 잠복 폭탄 |
| 4 | **D-1** `drop_sets` 를 "본품 없는 **조합**"(`N+M`, `A와 B`) 로 좁힌다 | 신제품 9건이 상세 페이지도 없이 사라진다 |
| 5 | **E-1** 기획 문서를 `docs/` 밖으로 빼거나 `robots.txt` 에 `Disallow` | 법무·평판 |
| 6 | **A-2** 에그드랍 이미지 URL `http:`→`https:` 변환(또는 이미지 없음 처리) | 빈 네모 4장 |
