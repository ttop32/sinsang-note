# 신상노트

편의점·카페·프랜차이즈·식품 제조사의 **신제품만** 모아 보여주는 정적 사이트.
<https://ttop32.github.io/sinsang-note/>

서버도 DB도 없다. GitHub Actions 가 매일 06:00(KST) 수집해 결과를 커밋하고,
GitHub Pages 가 `docs/` 를 그대로 서빙한다.

현재 **어댑터 189 · 브랜드 217 · 상품 14,031건**.

## 제1 규칙 — 기존 메뉴는 신상이 아니다

이 레포에서 제일 나쁜 결함은 **메뉴판을 통째로 긁어 전부 신상으로 만드는 것**이다.
2+1 행사 상품도, 세트 할인도, 리뉴얼도 신상이 아니다. 어댑터를 쓸 때 가장 먼저
확인할 것은 "이 소스가 신제품이라고 말하는 근거가 무엇인가" 하나다.

실제로 막은 사고가 여럿이다 — 설빙 `span.flag` 에 섞인 시그니처 배지로 2013년
메뉴가 신상이 됐고, 퀴즈노스는 전건(66/66)에 NEW 가 붙어 있었고, 하이오커피의
'신메뉴 40건'은 1년치 바구니라 10월에 쌍화차와 컵빙수가 공존했다. 새 어댑터를
붙이기 전에 `collectors/` 의 기존 모듈 두어 개를 열어 읽어 보면 함정이 다 적혀 있다.

## 구조

```
collect.py        수집 오케스트레이션 + 배선 가드 + --doctor
doctor.py         실패 원인 판정(DNS·TLS·해외차단·열림)과 사전 점검
rules.py          신선도 판정(60일 창)·중복 정리·이미지 검증·미러
taxonomy.py       우리가 관리하는 분류 26종과 업체 분류 → 우리 분류 맵핑
social.py         브랜드별 인스타·유튜브 링크
web/              페이지 생성 (home·pages·seo·theme·assets)
collectors/
  base.py         Item · BRANDS(217) · SITES · client() · 파생값
  <브랜드>.py       BRAND(또는 BRANDS) + fetch() -> list[Item]
  certs/          중간 인증서가 빠진 사이트용. verify=False 는 쓰지 않는다
data/products.json  수집 결과. git 이력이 곧 스냅샷 아카이브다
docs/               Pages 가 서빙하는 결과물 (b=브랜드, c=분류, p=상품, i=이미지 미러)
notes/              업종별 순위 조사·불가 사유·경계 기록
```

의존 방향은 한쪽이다 — `collect → web → rules/taxonomy`. 거꾸로 부르지 않는다.

## 로컬 실행

```bash
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./.venv/bin/python collect.py
open docs/index.html
```

## 수집 전 점검

```bash
./.venv/bin/python collect.py --doctor
```

수집 없이 주소만 1~2분에 훑는다. **수집 주소**(어댑터가 실제로 긁는 곳)와
**사이트 링크**(`base.SITES`, 막히면 카드 링크가 죽는다)를 따로 센다.

⚠️ **돌리는 곳의 IP 에 따라 답이 달라진다. 그게 맞는 동작이다.** 한국에서는
189곳 전부 열리는데 GitHub 러너(해외)에서는 여덟 곳이 `해외차단` 으로 찍힌다.
러너 쪽 답은 `doctor` 워크플로가 매주 화요일 새벽에 찍어 Actions 요약에 남긴다.

⚠️ `열림` 은 '수집이 된다'가 아니라 '못 닿은 건 아니다'까지다. 이 레포는 200 에
여러 번 속았다(탕화쿵푸의 차단 안내 200, 모리샤브의 soft-404).

## 브랜드 추가 — 고칠 곳이 **네 군데**다

```
collect.py   ① import   ② ADAPTERS 목록
base.py      ③ BRANDS(유형·세부분류)   ④ SITES(카드 링크)
```

하나만 빠뜨리면 파일이 멀쩡히 있는데 아무 일도 안 일어나고 아무도 모른다.
그래서 `collect.orphans()` 가 매 수집마다 찾아 찍는다. 자동으로 배선하지는
않는다 — 어느 어댑터를 켤지는 사람이 정하는 게 맞아서다(일부러 내려둔 것이 있다).

유형은 `CVS·CAFE·FRANCHISE·MAKER` 넷이고 **1단 탭은 `brand_type` 으로 갈린다.**
카페에서 파는 것(커피·디저트·빙수·도넛·아이스크림·베이커리)을 `FRANCHISE` 로
넣으면 '외식' 탭으로 샌다 — 실제로 11곳이 그랬다. `collect.miscast()` 가 본다.

### 어댑터가 지켜야 할 것

- **조용한 빈 리스트 금지.** 0건·급감·배지 0건·날짜 전건 실패에 전부 `raise`.
  소스가 신제품 글 게시판뿐이라 0건이 정상이면 `ALLOW_EMPTY = True`.
- **`is_new` 의 `False` 는 "브랜드가 신상이 아니라고 말했다"일 때만.** 배지가
  아무 말도 안 하면 `None` 이다. `False` 로 두면 `released_at` 이 요구돼
  그 브랜드가 영원히 화면에서 사라진다(더플레이스 41건이 그럴 뻔했다).
- **일괄 입력 날짜는 `uploaded_at` 에만.** `rules.untrust_bulk_dates()` 가
  그 자리만 본다. `released_at` 에 넣으면 무방비다.
- **`endDate` 가 있으면 반드시 읽는다.** 기간 한정은 `startDate` 가 최근이라
  가장 신상으로 보이는 자리가 가장 먼저 썩는다.
- robots·약관은 운영자 판단으로 무시하되 **UA 위장은 하지 않는다.**
  `verify=False` 도 쓰지 않는다 — 인증서가 빠졌으면 `certs/` 에 넣어 certifi 에
  **더한다**(교체가 아니다).
- 주류·비식품은 범위 밖이다.

## 신제품 판정

브랜드가 알려주는 `released_at` → `uploaded_at` → 우리가 처음 본 `first_seen`
순으로 믿고, 최근 60일 안이면 신상으로 본다. 브랜드마다 노출 수에 상한이 있고,
수집량이 갑자기 줄면(`FLOOR`) 부분수집으로 보고 이전 결과를 유지한다.

## 이미지

브랜드 서버를 직접 참조하면 핫링크 차단에 걸리므로 `docs/i/` 로 미러한다.
`rules.verify_images()` 가 **매직 바이트로** 판정한다 — Content-Type 으로
거르면 octet-stream 으로 오는 진짜 PNG 가 통째로 사라진다.
