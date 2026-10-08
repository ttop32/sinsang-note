# robots·약관 사유 재검토 — 외식 · 베이커리 · 분식 10곳

`COVERAGE-SUMMARY.md` §C-정책(robots·약관·AI봇 차단) 18곳 중 **외식·베이커리·분식 10곳**을
다시 연 기록이다. **2026-10-02 운영자가 robots·약관 무시를 명시 승인**했고, 같은 사유로
농심·CJ제일제당·하림·써브웨이·롯데리아·도미노피자·이마트24·폴바셋이 이미 뒤집혀 수집 중이다.

- 조사일: **2026-10-08**
- 조사 방법: `collectors/base.client()` (UA `sinsang-note/1.0`), 요청 간 1.3~2.0초
- **robots·약관은 판정 사유에서 뺐다.** 남은 질문은 **"신상 신호가 실제로 있느냐"** 하나다.
- 신호 없는 곳에는 어댑터를 만들지 않았다. 메뉴판 전체를 긁어 '전부 신상'으로 만드는 건
  안 만드느니만 못하다(`CANDIDATES-*.md` 의 퀴즈노스 66/66 · 얌샘김밥 41/41 선례).
- 브랜드 하나 끝날 때마다 이 파일에 append 한다.

**대상 10곳**: 뚜레쥬르 · 앤티앤스 · 송사부고로케 · 호밀호두 · 아웃백스테이크하우스 ·
애슐리 · 빕스 · CJ푸드빌 · 엽기떡볶이 · 니뽕내뽕

> ⚠️ **CJ푸드빌은 뚜레쥬르·빕스의 모회사다.** 셋을 따로 긁으면 같은 상품이 두세 번 올라간다.
> §CJ푸드빌 에서 소스가 실제로 겹치는지 실측해 정리한다.

---

## 1. 결과 표

| 브랜드 | 가맹점수 | 공식 사이트 | 원래 접은 사유 | 재검토 결과 | 신상 신호 | 배지 비율 실측 | 날짜 출처 | 수집 건수 | 만든 파일 | (유형, 세부분류) |
|---|---:|---|---|---|---|---|---:|---|---|
| **아웃백스테이크하우스** | 미등록(직영) | `www.outback.co.kr` | 이용약관 제10조 ④ (robots 는 원래 허용) | ✅ **수집** | `icon_new.png` 배지 | **110건 중 17건 (15.5%)** — 중복 턴 뒤 62건 중 12건 | 썸네일 경로 `/upload/product/YYYYMMDD/` → `uploaded_at` | **62** | `collectors/western_outback.py` | (`FRANCHISE`, `양식`) |

---

## 2. 브랜드별 기록

### ✅ 아웃백스테이크하우스 — 62건 (NEW 12). `collectors/western_outback.py`

**원래 사유**: robots 가 아니라 **이용약관**이었다. `CANDIDATES-WESTERN.md` §4 에
"이 카테고리 기술적으로 최고인데 약관이 막는다"로 적혀 있다. robots 는 처음부터 열려 있었고
난독화된 `.do` 두 개(`/qkO3DtBJHg0se.do`, `/A0RG7SrkDWpB.do`)만 막는다.

**당시 실측과 달라진 점** — 1차는 `cateIdx=26`(DELIVERY) 한 장만 봤다(46건 중 NEW 3건).
이번에 내비를 풀어 **13칸 전수**를 돌았다.

```
cate=24 LUNCH SET                      19건 NEW=5
cate=26 DELIVERY                       46건 NEW=3
cate=52 BLACK LABEL AUTUMN EDITION      1건 NEW=0
cate=54 APPETIZERS & SALADS             7건 NEW=1
cate=57 SPECIAL STEAKS & BACK RIBS      7건 NEW=2
cate=59 PASTA & RICE                    9건 NEW=3
cate=64 EASY PICK                       3건 NEW=3
cate=69 BLACK LABEL SIZZLING EDITION    1건 NEW=0
                                      110건 NEW=17 → 15.5%
```

**배지 비율 15.5%.** 분모가 '신제품 전용 목록'이 아니라 **메뉴판 전체**인데 배지가 1/6 에만
붙는다 — 켜고 끄는 배지다. 퀴즈노스(66/66)·얌샘김밥(41/41) 과 반대 경우고, 하이오커피처럼
'1년치가 쌓인 신메뉴 탭'도 아니다. 배지 판정은 `.p-icon` **존재**가 아니라
**`src` 파일명이 `icon_new`** 인지로 한다(설빙 `icon_signature.png` 사고 회피).

**나머지 4칸은 상품 목록이 아니다.** `productList.do` 가 아닌 데로 떨어진다 —
`BEVERAGES & ALCOHOL`·`SIDES & ADD ON MATES`·`DESSERTS` 는 `productContents.do`
(편집기로 올린 포스터 `.webp` 두 장뿐), `SIZZLING BONE-IN STEAK` 는 `productView.do`
(단일 상품 상세). 넷 다 0건이 정상이라 칸별 raise 를 걸지 않고 합계로만 가드한다.

`WINES` 17건은 **전부 술**이라 요청 자체를 보내지 않는다.

**날짜 — 썸네일 경로에 업로드 일자가 박혀 있다.** `/upload/product/20260901/2026090100….png`.
110건 전건에서 뽑힌다. 그런데 **일괄 재업로드 덩어리**가 있다:

```
20250422 28건 · 20250616 15건 · 20260308 10건 · 20240714 9건 · 20260901 9건
```

하루에 신제품 28종이 나온 게 아니라 사진을 한꺼번에 다시 올린 것이다. 파리바게뜨 312장과
같은 함정이라 **`uploaded_at` 에만 넣는다**(`rules.untrust_bulk_dates()` 가 `uploaded_at`
만 보기 때문에 여기 넣어야 걸린다). `released_at` 은 끝까지 비웠다.

**⚠️ 이번에 실제로 밟은 함정 두 개** — 다음 사람이 또 밟지 않게 적는다.

1. **내비는 '지금 보고 있는 칸'의 번호를 안 준다.** 활성 항목만
   `<li class='actived'><a href="#">` 라서 정규식에 안 걸린다. SEED 로 쓴
   `cateIdx=26`(DELIVERY, 46건) 이 통째로 빠져 **110 → 31건**이 됐다.
   SEED 의 cateIdx 를 손으로 넣어 해결.
2. **같은 상품이 여러 칸에 걸려 있고 칸마다 배지가 다르다.** `트리플 갈릭 스트립` 은
   LUNCH SET·SPECIAL STEAKS 에서 NEW 인데 DELIVERY 에서는 아니고, `마라 투움바 파스타` 는
   PASTA & RICE 에서만 NEW 다. 먼저 본 것만 남기는 `seen` 집합이면 DELIVERY 를 먼저 도는
   탓에 **둘 다 신상에서 빠진다.** 한 칸이라도 NEW 면 그쪽으로 교체하게 고쳤다(10 → 12건).

`EASY PICK` 3건(`듀얼 PICK (2인)` 등)은 사실상 세트지만 **어댑터에서 거르지 않았다** —
세트 판정은 `collect.drop_sets()` 가 이름으로 한다.
