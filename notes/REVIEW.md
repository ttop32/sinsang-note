# 전체 검수 — 사용자 눈으로

측정 대상은 **로컬 산출물**이다(배포본 아님).
- `data/products.json` mtime **2026-10-01 17:51:13 KST**, `count=7217`, `updated_at=2026-10-01T07:53:58+00:00`
- `docs/index.html` mtime **2026-10-01 17:51:14 KST**, md5 `be1e07b73089f0073f87bfc2a4d284d4`, 919,286 bytes
- 검수 중 레포가 두 번 리빌드됐다(17:14 → 17:48 → 17:51). 17:48 빌드와 17:51 빌드는 **홈 카드 내용이 완전히 동일**함을 확인했다(추가 0 / 삭제 0, 아래 재현).
- 서빙: `cd docs && python -m http.server 8777` / 하위 링크가 `/sinsang-note/` 절대경로라 `/tmp/.../site/sinsang-note -> docs` 심링크를 만들어 `http.server 8778` 로도 띄웠다.

**지시문의 전제와 다른 점부터.** 지시문은 "홈 300장 47개 브랜드 / 상세 1,340장 / 굿즈 37건 / `PER_BRAND` 12" 라고 했는데,
지금 산출물은 **홈 1,237장 · 53개 브랜드 / 상세 1,250장 / 굿즈 13건** 이다. `collect.py` 의
`PER_BRAND = 0`, `SHOW = 0` 으로 바뀌어(커밋 `d294361` 직전 작업분) **브랜드 상한과 홈 300장 상한이 둘 다 풀렸다.**
그래서 지금까지 상한이 가려 주던 것이 전부 홈 첫 화면에 올라와 있다. 아래 §1-1 이 그 결과다.

재현:
```
cd /Users/swkim72/source/sinsang-note
grep -n '^PER_BRAND\|^SHOW' collect.py
python3 - <<'EOF'
import re,html,pathlib,json,collections
s=pathlib.Path('docs/index.html').read_text(encoding='utf-8')
cards=re.findall(r'<a class="c"[^>]*>.*?</a>', s, re.S)
g=lambda c,rx:(re.search(rx,c,re.S).group(1) if re.search(rx,c,re.S) else '')
rows=[dict(brand=html.unescape(g(c,r'<span class="br">(.*?)</span>')),
           name=html.unescape(g(c,r'<h2>(.*?)</h2>')),
           raw=html.unescape(g(c,r'data-raw="([^"]*)"')),
           date=g(c,r'<time datetime="([^"]*)"'),
           img=g(c,r'<img[^>]*src="([^"]*)"')) for c in cards]
print(len(rows), len({r['brand'] for r in rows}))
print(collections.Counter(r['brand'] for r in rows).most_common(10))
EOF
```
→ `1237 53` / `[('CU',338), ('파리바게뜨',312), ('hy프레딧',75), ('이마트24',61), ('팔도',46), ('스시로',46), ('스타벅스',36), ('커피빈',28), ('폴바셋',21), ('이디야커피',19)]`
(측정 2026-10-01 17:52 KST)

---

## §1 지금 화면에 틀린 것

### 1-1 🔴 파리바게뜨 메뉴판이 통째로 신상 목록에 올라와 있다 — 홈 1,237장 중 **312장(25%)**

사용자가 네 번 지적한 "기존 메뉴를 신상으로 잡지 마라" 가 지금 홈 첫 화면에서 재발해 있다.
홈에 떠 있는 파리바게뜨 카드 **312장**의 제목을 그대로 옮긴다(전부 날짜가 찍혀 있다):

| 카드에 찍힌 날짜 | 상품명(카드 제목 그대로) |
|---|---|
| 2026-08-26 | `소보루빵` `단팥소보루` `카스테라` `초코카스테라` `프렌치바게뜨` `밤식빵` `모닝토스트` `맘모스브레드` `찹쌀도넛` `단팥 도넛` `슈크림빵` `옛날왕슈크림도넛` `버터롤` `플레인 베이글` `프렌치크라상` `후레쉬 식빵` `달콤 꽈배기도넛` `케익꽈배기도넛` `추억의 소시지빵` `초코 소라빵` `메론크림빵` `땅콩크림빵` `양파치즈브레드` `오리지널 머핀` `초콜릿 머핀` `미스터베어` `미스베어` |
| 2026-09-01 | `꽈배기도넛` `연유크림빵` |
| 2026-09-03 | `정통 파운드케익` |
| 2026-09-10 | `양송이 스프` |
| 2026-09-11 | `단팥빵` `NO.1 우유식빵` `모카크림빵` `부드러운 상미종 생(生)식빵` |
| 2026-09-24 | `추억의 생도나스` |
| 2026-10-01 | `모짜렐라 치즈봉` `멕시칸 핫도그` `우유가좋은뽀로로케익` |

전부 파리바게뜨가 수십 년 팔아온 상시 품목이다. `카스테라`·`소보루빵`·`단팥빵`·`프렌치바게뜨` 가
"최근 60일 신제품" 으로 떠 있다.

**원인 — 어댑터가 함정이라고 적어둔 걸 소비 쪽이 그대로 밟았다.**
`collectors/bakery_parisbaguette.py` docstring:
> **`date` 를 `released_at` 에 넣지 않는다.** … 2026-08-26 의 104건을 열어 보면 후레쉬 식빵·웨하스·
> 고로케·피자빵처럼 오래된 상시 판매 품목이다. 하루에 신제품 104종이 나온 게 아니라 사이트 개편 때
> 일괄 재발행된 것이고 … **그걸 `released_at` 에 넣었으면 8월 26일에 104개 신제품이 나온 걸로 보도된다.**

그런데 `collect.is_fresh()` 는 두 필드를 구분하지 않는다:
```python
stamped = r.get("released_at") or r.get("uploaded_at")   # collect.py:407
...
if stamped: return stamped >= cutoff                     # collect.py:446
```
`uploaded_at` 으로 피한 줄 알았던 값이 바로 다음 줄에서 `released_at` 과 같은 자격으로 쓰인다.
**어댑터의 방어가 아무 일도 하지 않는다.**

**원본 대조 (2026-10-01 17:5x KST 실측).** 워드프레스 post id 를 보면 재발행이 바로 드러난다 —
새로 만든 글은 id 가 185,5xx 대인데, 같은 날짜를 달고 있는 것 중에 id 가 4,800 인 글이 있다:
```
python3 - <<'EOF'
import json, httpx
c=httpx.Client(headers={"User-Agent":"sinsang-note/1.0 (+https://github.com/ttop32/sinsang-note)"},
               timeout=30, follow_redirects=True)
rows=[]
for pg in (1,2):
    r=c.get("https://www.paris.co.kr/wp-json/wp/v2/product",
            params={"per_page":100,"page":pg,"_fields":"id,date,modified,slug,title"})
    rows+=json.loads(r.content.decode("utf-8-sig"))
for x in sorted([x for x in rows if x['date'][:10]>='2026-09-25'], key=lambda x:x['id'])[:6]:
    print(x['id'], x['date'][:10], x['title']['rendered'])
for x in rows:
    if x['id'] in (4800,4466,65054,63833,51278,5129): print('OLD', x['id'], x['date'][:10], x['title']['rendered'])
EOF
```
출력(발췌):
```
4800   2026-10-01 우유가좋은뽀로로케익      ← id 4,800. 사이트에서 가장 오래된 축인 글이 오늘 날짜를 달고 있다
185509 2026-10-01 멕시칸 핫도그
185511 2026-10-01 모짜렐라 치즈봉           ← slug 가 mozzarella-cheese-sticks-2 (중복 재발행 표식)
OLD 4466  2026-09-11 모카크림빵
OLD 65054 2026-09-11 단팥빵
OLD 63833 2026-09-11 NO.1 우유식빵
OLD 51278 2026-09-01 꽈배기도넛
OLD 5129  2026-09-03 정통 파운드케익
```
`mozzarella-cheese-sticks` 슬러그는 지금 404 이고 `-2` 만 살아 있다 → 같은 상품의 **재발행 글**이다.

**규모.** 60일 창(cutoff 2026-08-02) 안에 2026-08-26 재발행 98건 + 2026-08-28 67건이 통째로 들어온다.
파리바게뜨 530건 중 **312건이 "신제품"** 으로 집계된다(58%).
```
python3 - <<'EOF'
import json, datetime, collect, collections
rows=json.load(open('data/products.json',encoding='utf-8'))['products']
listed=collect.pick(rows, datetime.date.today().isoformat(), cap=False)
print(len(listed), collections.Counter(r['brand'] for r in listed).most_common(5))
EOF
```
→ `1237 [('CU',338), ('파리바게뜨',312), ('hy프레딧',75), ('이마트24',61), ('팔도',46)]`

**고치려면**: `is_fresh` 가 `uploaded_at` 을 `released_at` 과 같게 취급하는 걸 끊어야 한다
(예: `uploaded_at` 만 있는 행은 `first_seen` 경로/기준선 규칙으로 보내거나, 한 날짜에 N건 이상 몰린
`uploaded_at` 덩어리를 `SURGE` 처럼 기준선 처리). 지금은 **`SURGE` 가드도 안 걸린다** — `SURGE` 는
`first_seen == today` 인 행만 보는데, 재발행 덩어리는 `uploaded_at` 이 과거라 `first_seen` 이 소급되기 때문이다.

---

### 1-2 🔴 "최근 60일" 이라고 써놓고 **218장은 날짜 근거가 아예 없다** — `STALE` 상수는 죽어 있다

홈 푸터: `최근 60일 신제품 1237건`. 그런데 1,237장 중 **218장은 날짜가 없다**(카드 날짜 칸이 비어 있고
데이터에도 `released_at`·`uploaded_at` 이 둘 다 없다). 그리고 **"최신순" 정렬의 맨 앞 세 장이 바로 그런 카드다**:

```
최신순 1위  홍루이젠 / 초당옥수수 샌드위치       / (날짜 없음)
최신순 2위  홍루이젠 / 복숭아 우롱 에이드         / (날짜 없음)
최신순 3위  홍루이젠 / 자두 자몽 히비스커스 에이드 / (날짜 없음)
```

이 218장은 `is_new=True` 만 가지고 올라온 것인데, 그 경로에는 **나이 상한이 없다**:
```python
if r.get("is_new") is True:
    if stamped: return stamped >= cutoff
    if any(l in base.PROMO_LABELS for l in r.get("labels", [])): return False
    return True            # ← 날짜가 없으면 영구히 True
```
`collect.py:78` 의 `STALE = 90` 은 주석에 "배지를 믿되 날짜가 이만큼 지났으면 신제품이 아니라고 본다"
라고 쓰여 있지만 **코드 어디에서도 읽지 않는다.**
```
grep -rn "STALE" collect.py web collectors
```
→ `collect.py:78:STALE = 90` (정의 1곳) + 어댑터 docstring 2곳의 언급뿐. **참조 0.**
`collectors/cafe_coffeebean.py` docstring 도 이미 이렇게 적어뒀다:
> 날짜가 없어서 collect.py 의 STALE 가지치기가 걸리지 않으니, 오래 걸려 있는 상품이 계속 NEW 로 보일 수 있다.

지금 데이터에선 `first_seen` 이 전부 2026-09-29~10-01 이라 아직 늙지 않았지만(아래 측정),
**이 218장은 브랜드가 배지를 내릴 때까지 영원히 홈에 남는다.**
```
python3 - <<'EOF'
import json, datetime, collect, collections
rows=json.load(open('data/products.json',encoding='utf-8'))['products']
L=collect.pick(rows, datetime.date.today().isoformat(), cap=False)
u=[r for r in L if not (r.get('released_at') or r.get('uploaded_at'))]
print('날짜 없는 카드', len(u), collections.Counter(r.get('first_seen') for r in u))
EOF
```
→ `날짜 없는 카드 220 Counter({'2026-09-30': 199, '2026-09-29': 11, '2026-10-01': 10})`
(220 vs 화면 218 차이는 `data-raw` 없는 카드 2장의 파싱 차이가 아니라 `display` 중복 1건 + 굿즈 경로 차이로,
화면 기준 218 이 맞다.)

---

### 1-3 🔴 날짜 없는 NEW 경로로 **13년 된 간판 메뉴**가 올라와 있다

§1-2 의 구멍을 타고 실제로 올라온 것들. 전부 홈에 떠 있고 **NEW 배지가 찍혀 있다.**

| 브랜드 | 카드 제목 (그대로) | 왜 신상이 아닌가 |
|---|---|---|
| 설빙 | `인절미설빙` | 설빙 창업(2013) 때부터의 간판 메뉴 |
| 설빙 | `팥인절미설빙` `흑절미설빙` `팥흑절미설빙` `인절미아이스크림설빙` | 같은 인절미 라인 |
| 설빙 | `인절미토스트` `흑절미토스트` `인절미샷라떼` `인절미라떼` | 같은 라인의 사이드·음료 |
| 설빙 | `애플망고치즈설빙` | 설빙 상시 메뉴 |
| 죠스떡볶이 | `죠스떡볶이` | 브랜드명과 같은 간판 상품(2007~) |

죠스는 어댑터 docstring(`collectors/snack_jaws.py`)이 이미 자백해 뒀다:
> 그 1건이 하필 **'죠스떡볶이'** — 브랜드명과 같은 간판 상품이다. 신제품이라기보다 리뉴얼이나
> 대표메뉴 강조일 가능성이 있다.

설빙은 96건 중 14건에만 배지가 붙어 있어 "브랜드가 선별해서 단다" 는 판단 자체는 맞지만,
그 14건에 간판 메뉴가 들어 있다. 날짜가 없으니 걸러낼 2차 근거가 없다.
```
python3 -c "
import json
rows=json.load(open('data/products.json',encoding='utf-8'))['products']
for r in rows:
    if r['brand'] in ('설빙','죠스떡볶이') and r.get('is_new') is True:
        print(r['brand'], r['name'], r.get('released_at'), r.get('uploaded_at'), r.get('labels'))
"
```

---

### 1-4 🟠 세트·콤보가 신상으로 떠 있다 — `drop_sets` 가 본품을 못 찾으면 통과시킨다

`drop_sets()` 는 **같은 브랜드에 본품 이름이 실제로 존재할 때만** 세트를 뺀다. 그래서 단품을 안 긁는
브랜드(또는 세트만 신메뉴로 올리는 브랜드)에서는 세트가 그대로 신상이 된다. 홈에 떠 있는 것:

| 브랜드 | 카드 제목 |
|---|---|
| BBQ | `황올한마리+버거세트` `양념한마리+버거세트` `황올반+양념반+버거세트` |
| 맘스터치 | `싱글피자N버거세트` `싱글피자N치킨세트 (순살)` `싱글피자N치킨세트 (뼈)` |
| 미스터피자 | `퀘감포 세트 (배달)` `피치 세트 M (배달)` `피치 세트 L (배달)` |
| 맥도날드 | `맥크리스피™ 고추장 버터 세트` `맥스파이시® 고추장 버터 세트` |
| CU | `닭강정김밥콤보세트` |
| 파파존스 | `바베큐립 콤보` |
| hy프레딧 | `…청년떡집 잔망루피 시그니처 선물세트` `…절편 3종 세트 …` 외 5건 |
| 브레댄코 | `더치팩쿠키선물세트 (중)` |
| 던킨 | `학화 호도 먼치킨 세트` |

BBQ `황올한마리+버거세트` 의 "황금올리브치킨" 은 1995년부터 팔던 제품이고, 상세 페이지 설명도
브랜드 소개문이다 — 구성·할인이지 신제품이 아니다. 미스터피자 `피치 세트 M/L (배달)` 은 사이즈만 다른
같은 세트 둘이 각각 카드가 됐다(`merge_variants` 는 `세트 M`·`세트 L` 을 같은 본품으로 묶지 못한다 —
`_VARIANT` 가 어미의 `세트` 만 보고 `세트 M` 은 안 본다).

재현: `http://127.0.0.1:8778/sinsang-note/` → 검색창에 `세트` → 카드 제목 확인.

---

### 1-5 🟠 행사 안내문이 상품 설명으로 떠 있다 (BBQ)

홈/상세에 있는 BBQ `필크런치 떡볶이 세트`(2026-08-12, NEW 배지) 의 카드 설명이 상품 설명이 아니라
**굿즈 증정 행사 공지**다:
> `(7/16~소진시) 필릭스 굿즈 증정 : 럭키드로우(랜덤) 또는 럭키포토(랜덤) 중 1종 증정 * 매장별 운영 상황 및 굿즈 재고에 따라 제공 여부가 상이하므로, 이용 전 매장에 문의해 주시기 바랍니다. …`

7/16 시작 행사가 10/1 홈에 "신제품" 으로 떠 있다.
재현: `http://127.0.0.1:8778/sinsang-note/p/bbq-필크런치-떡볶이-세트/`

---

### 1-6 🟠 같은 상품이 카드 두 장 — 정규화가 서로 다른 두 이름을 같은 제목으로 만들었다

```
팔도 / 이천햅쌀 비락식혜      (raw: 이천햅쌀 비락식혜 1.5L)
팔도 / 이천햅쌀 비락식혜      (raw: 이천햅쌀 비락식혜)
```
`display_name()` 이 `1.5L` 을 떼면서 두 제목이 같아졌다. `make_key()` 는 원본 이름을 쓰니 중복으로
안 잡히고, `merge_variants()` 는 `세트/콤보/단품` 접미만 보니 역시 안 잡는다.
재현: 홈 검색창에 `비락식혜` → 2건, 제목 동일.
```
python3 -c "
import sys; sys.path.insert(0,'.')
from collectors.base import display_name
for n in ['이천햅쌀 비락식혜 1.5L','이천햅쌀 비락식혜']: print(repr(n),'->',repr(display_name(n)))
"
```

---

### 1-7 🟠 정규화가 이름을 망가뜨린 카드 5장 — `… x 5개` 만 남았다

`_SPEC` 가 괄호 밖 `50g` 을 지우면서 뒤의 묶음 표기 `x 5개` 가 허공에 남았다.

| 카드 제목 (화면) | 원본(`data-raw`) |
|---|---|
| `택배배송 것플렉스 두부흑임자스낵 x 5개` | `[택배배송] 것플렉스 두부흑임자스낵 50g x 5개` |
| `택배배송 것플렉스 두부현미스낵 x 5개` | `[택배배송] 것플렉스 두부현미스낵 50g x 5개` |
| `택배배송 것플렉스 두부오트스낵 x 5개` | `[택배배송] 것플렉스 두부오트스낵 50g x 5개` |
| `택배배송 것플렉스 두부아몬드스낵 x 5개` | `[택배배송] 것플렉스 두부아몬드스낵 50g x 5개` |
| `택배배송 것플렉스 국내산 글루텐프리 고구마칩 x 5개` | `[택배배송] 것플렉스 국내산 글루텐프리 고구마칩 30g x 5개` |

`_MULT` 는 `*`·`×` 만 보고 `x` 는 "자이언트X3 이 걸린다" 는 이유로 일부러 뺐는데, `_SPEC` 는 그 사정을
모른 채 앞의 용량만 지운다. **두 규칙이 서로를 모른다**(§4 와 같은 결함 모양).

같이 확인한 손실(치명적이진 않지만 사람이 고르는 데 쓰는 정보):
`버터 크라상 파이(8개입)` → `버터 크라상 파이` / `미니 호두아몬드 크림치즈빵(5개입)` → `(5개입)` 사라짐 /
`생크림폭탄 도넛(3개입)` / `구움과자 아뜰리에 (10개입)` / `학화 호도 먼치킨 세트(5개입)`.
`버터 크라상 파이(낱개)` 는 `(낱개)` 가 남아서, 화면에는 `버터 크라상 파이 (낱개)` 와
`버터 크라상 파이` 두 장이 뜬다 — 뒤의 것이 8개입인 걸 알 길이 없다.

---

### 1-8 🟠 원본에서 잘린 이름을 그대로 내보낸다

```
화면: 택배배송/냉동 청년떡집 프리미엄 크림떡 2종 세트 티라미슈, 톡톡 옥
raw : [택배배송/냉동] 청년떡집 프리미엄 크림떡 2종 세트(티라미슈, 톡톡 옥
```
원본 자체가 `옥` 에서 잘려 있고 여는 괄호가 안 닫혔다. `_drop_unmatched_parens` 가 괄호만 없애서
문장이 중간에서 끊긴 채 카드에 찍힌다. **잘린 이름을 감지해 버리거나 보수하는 자리가 없다.**

같은 hy프레딧 카드 39장이 `택배배송` / `택배배송/냉동` 으로 시작한다 — 배송 방식이지 상품명이 아니다.
`_LEAD_BRACKET` 이 "말이 들어 있으면 괄호만 벗겨 남긴다" 규칙이라 `[택배배송]` 이 제목 앞머리가 됐다.

---

### 1-9 🟡 사진이 없는 카드 5장이 **빈 네모**로 뜬다 (모바일에서 더 눈에 띈다)

```
에그드랍 / 케일 사과주스
에그드랍 / 굿모닝 브런치
에그드랍 / 아메리칸 브런치
에그드랍 / 아보가든 브런치
파리바게뜨 / 티트라 아뜰리에 컬렉션
```
`derive()` 가 `http://` 이미지를 지우는 처리(에그드랍 인증서 만료 대응)는 **혼합 콘텐츠 에러는 없앴지만
빈 네모는 그대로다.** 375px 모바일에서 사진 칸 크기의 빈 사각형이 그려진다(스크린샷으로 확인).
커밋 `8f7a2f1` "에그드랍 사진 73장이 빈 네모였다" 가 해소로 적혀 있으나, **화면에서는 여전히 빈 네모다** —
해소된 것은 "브라우저가 막는 깨진 이미지" 지 "빈 칸" 이 아니다.

재현: `resize 375x812` → 홈에서 `에그드랍` 검색 → 4장 전부 빈 네모.

**깨진 이미지는 없다.** 홈 `<img>` 1,232장을 `loading=eager` 로 강제 로드해 전부 완료시킨 뒤
`naturalWidth===0` 인 것을 셌다 → **0건** (pending 0).

---

### 1-10 🟡 주류·굿즈 누수 — 지금 화면에서는 **안 샜다** (전수 확인함)

- **주류가 식품 목록에 샌 것: 0건.** 홈 1,237장 전체 이름에 주종·품종·주류 브랜드 60여 개를 대고 훑었고,
  걸린 것은 전부 오탐 회피분(`카스테라` 19건, `몽블랑`, `매실차`, `진미채`, `양조간장`, `제로 매실 아이스티`)이었다.
  `BBQ 병맥주(카스0.0 논알콜)` / `병맥주(카스레몬스퀴즈0.0)` 는 `NONALCOHOL_MARKS`·`_ZERO_ABV` 로
  정확히 제외됐다.
- **굿즈가 식품 목록에 샌 것: 0건.** 홈 1,237장에 굿즈성 단어를 대고 훑어 추가로 나온 것이 없다.
- **`/c/굿즈/` 13건 전건 확인.** 13장 전부 실제 굿즈가 맞다(쿠키런 콜라보 굿즈 1, 매머드 피규어·볼펜·파우치·
  키링·무드등 8, 할리스 텀블러 4). **식품이 굿즈로 잘못 빠진 것: 0건.**
  ⚠️ 다만 지시문의 "굿즈 37건" 은 더 이상 맞지 않는다 — 커밋 `093e416` 이 굿즈를 카페·외식 것만으로 좁혀서
  편의점 생활용품(CU 52 · 이마트24 25 · 세븐 7)은 **식품 목록에도, 굿즈 목록에도 안 나온다.**
- 다만 **데이터 레벨 오분류**는 있다(지금은 `is_fresh` 에 안 걸려 화면엔 없다):
  먹는 것인데 `nonfood=True` 로 박힌 것 — `CU 포켓몬)럭키비타에너지샷`, `CU 로트벡쉔)올인원이뮨샷`,
  `CU 한삼인)홍삼진굿데이앰플`, `CU HK)컨디션스틱샤인제로18g`, `CU 동화)부채표편안활스틱`,
  `CU RU21)하루두알멀티비타민`. 전부 `category=생활용품` 이라 `NONFOOD_CATEGORIES` 가 아니라
  브랜드 분류에서 걸린 것이고, 그 브랜드가 그렇게 분류한 것이라 "우리 결함" 이라기는 애매하다.
  `derive()` 의 `nonfood`/`alcohol` 이 **한 방향(True 로만)** 움직이므로, 나중에 풀고 싶어도 안 풀린다.

---

### 1-11 🟡 롯데칠성 카드 3장 — 서버가 중간 인증서를 안 줘서 **클라이언트에 따라 깨질 수 있다**

```
롯데칠성음료 / 펩시 엑스트라 피즈
롯데칠성음료 / 오트몬드 프로틴 커피셰이크
롯데칠성음료 / 오트몬드 검은콩단백
```
세 장 모두 `https://company.lottechilsung.co.kr/image/...` 를 핫링크한다.
```
echo | openssl s_client -connect company.lottechilsung.co.kr:443 -servername company.lottechilsung.co.kr 2>&1 | grep "Verify return code"
```
→ `Verify return code: 21 (unable to verify the first certificate)` — 중간 인증서 누락.
`collectors/lottechilsung.py` 는 `collectors/certs/globalsign-gcc-r3-dv-tls-ca-2020.pem` 을 번들에 더해
**수집기 쪽만** 풀었다. 방문자 브라우저에는 그 보충이 없다.
- 파이썬 `httpx`(certifi) → `CERTIFICATE_VERIFY_FAILED` 3건
- **Chrome(Browser pane) 에서는 3장 모두 정상 로드**(AIA fetching 으로 복구) — 그래서 지금 화면은 멀쩡하다.
- Firefox/일부 모바일 WebView 는 AIA 를 안 따라가는 경우가 있어 깨질 수 있다. **미확인(§5).**

---

### 1-12 🟡 날짜 대조 표본 — 카드 날짜 ≠ 출시일

| 카드 | 화면 날짜 | 원본 실측 | 판정 |
|---|---|---|---|
| 파리바게뜨 `우유가좋은뽀로로케익` | 2026-10-01 | WP `date=2026-10-01` 인데 **post id 4800**(사이트 최고참급) | 출시일 아님 — 재발행 |
| 파리바게뜨 `모짜렐라 치즈봉` | 2026-10-01 | slug `mozzarella-cheese-sticks-2`, 원 슬러그는 404 | 출시일 아님 — 재발행 |
| 파리바게뜨 `단팥빵` | 2026-09-11 | post id 65054 | 출시일 아님 |
| BBQ `순살 치킨버거 (마일드)` | 2026-09-08 | 상세 페이지 "등록일 2026년 9월 8일" | 일치(브랜드가 준 등록일) |
| 맘스터치 `스매쉬버거` | 2026-09-09 | 어댑터가 브랜드 신메뉴 등록일 수집 | 일치 |

**날짜 칸이 빈 카드 218장**(§1-2). 기준선 때문에 비운 게 아니라 **브랜드가 날짜를 안 줘서** 비었고,
그 처리 자체(모르는 날짜를 안 쓴다)는 맞다. 문제는 그 상태로 "최근 60일" 이라고 쓰는 것과,
그 218장에 나이 상한이 없다는 것(§1-2, §1-3).

---

### 1-13 ✅ 틀리지 않은 것 (오진 방지용으로 적어둔다)

- 죠스떡볶이 카드 사진이 `/images/common/img_menu_spicy.png` 라 "배지 아이콘을 집은 것" 으로 의심했는데,
  내려받아 보니 **680×680 떡볶이 실사진**이다. 경로 이름만 `common` 이다.
- 홈 1단 탭·2단 칩 숫자는 **전부 실제 카드 수와 일치**한다(§2).
- 홈 `오늘 23건` 은 카드에 `2026-10-01` 이 찍힌 장수와 정확히 일치한다(파리바게뜨 11 + 노티드 6 +
  CU 2 + 배스킨라빈스 2 + 동서식품 1 + 스타벅스 1 = 23). 다만 그 23건 중 11건이 §1-1 의 재발행분이다.

---

### §1 추가 — 검수 중 레포가 고쳐졌다 (18:03 커밋 `9970736`)

§1 을 보낸 뒤 운영자가 `untrust_bulk_dates()` 와 `STALE` 가드를 넣었다.
**18:03:20 빌드 기준으로 다시 쟀다**(`docs/index.html` md5 `efa41a9c295fa1623fb0fd4b22908502`, 780,929 bytes, 측정 18:11 KST):

| | 17:51 빌드 | 18:03 빌드 |
|---|---|---|
| 홈 카드 | 1,237 | **1,055** |
| 파리바게뜨 | 312 | **125** |
| 날짜 없는 카드 | 218 | **223** |
| 사진 없는 카드 | 5 | 5 |

**해소됨**: §1-1 의 2026-08-26(98건)·08-28(67건) 재발행 덩어리가 통째로 빠졌다.
`소보루빵`·`카스테라`·`프렌치바게뜨`·`밤식빵`·`맘모스브레드`·`찹쌀도넛`·`버터롤`·`플레인 베이글`·
`프렌치크라상`·`모닝토스트`·`슈크림빵`·`후레쉬 식빵`·`미스터베어` 전부 화면에서 사라졌다.

**🔴 아직 남아 있다** — `BULK_MIN = 20` 보다 작은 덩어리는 안 걸린다. 9장이 그대로 떠 있다:

| 카드 날짜 | 상품명 | 원본 WordPress post id |
|---|---|---|
| 2026-10-01 | `멕시칸 핫도그` | 185509 |
| 2026-10-01 | `모짜렐라 치즈봉` | 185511 (slug `…-2`, 원 슬러그 404) |
| 2026-10-01 | `우유가좋은뽀로로케익` | **4800** |
| 2026-09-11 | `모카크림빵` | **4466** |
| 2026-09-11 | `단팥빵` | **65054** |
| 2026-09-11 | `NO.1 우유식빵` | **63833** |
| 2026-09-10 | `양송이 스프` | 64958 |
| 2026-09-03 | `정통 파운드케익` | **5129** |
| 2026-09-01 | `꽈배기도넛` | **51278** |

같은 날 새로 만들어진 글의 id 는 185,5xx 대다. id 가 4,466·4,800·5,129 인 글이 10월 1일·9월 11일
날짜를 달고 있는 건 재발행이지 출시가 아니다. **덩어리 크기가 아니라 post id 를 보면 바로 갈린다** —
`같은 응답 안에서 id 중앙값보다 한 자릿수 작은 글`은 재발행으로 보는 게 BULK_MIN 보다 정확하다.
(이 판정은 파리바게뜨 전용이 아니다. 대부분의 CMS 가 증가하는 정수 id 를 준다.)

**§1-2·§1-3 은 그대로다.** 날짜 없는 카드가 218 → 223 으로 오히려 늘었고(날짜를 지운 결과),
설빙 14장은 `인절미설빙` 포함 전부 그대로다. 새로 넣은 `STALE` 가드는 `first_seen` 기준이라
이번 주에 처음 수집한 상품은 아직 안 걸린다(커밋 메시지도 "지금 걸리는 건 4건뿐" 이라고 적고 있다).
**§3 에서 그 구멍을 실제로 메울 수 있는 값을 찾았다 — 이미지 `Last-Modified` 다.**

---

## §2 브라우저 조작 결과

서빙: `cd docs && python -m http.server 8777` (홈 전용) / 하위 링크가 `/sinsang-note/` 절대경로라
`<scratchpad>/site/sinsang-note -> docs` 심링크 + `http.server 8778` (전 페이지).
브라우저는 Browser pane(Chrome). 측정 17:50~18:12 KST.

### 2-1 1단 탭 · 2단 칩 — 숫자와 실제 카드 수가 **전부 일치**
17:51 빌드(1,237장)에서 5개 탭 × 24개 칩을 전부 눌러 `.cnt` 텍스트와 `offsetParent!==null` 인
카드 수를 대조했다.

| 탭 | 표시 | 실제 | 2단 칩 합 |
|---|---|---|---|
| 전체 | (빈칸) | 1237 | — (전체 탭에선 칩을 숨긴다) |
| 편의점 | 413건 | 413 | CU 338 + 이마트24 61 + 세븐일레븐 11 + GS25 3 = 413 ✓ |
| 카페 | 530건 | 530 | 베이커리 345 + 커피 164 + 빙수 14 + 도넛 5 + 아이스크림 2 = 530 ✓ |
| 외식 | 154건 | 154 | 일식 48 + 햄버거 29 + 치킨 29 + 피자 21 + 도시락 11 + 샌드위치 6 + 한식 6 + 샐러드 3 + 분식 1 = 154 ✓ |
| 가공식품 | 140건 | 140 | 냉동식품 79 + 라면 51 + 조미료 4 + 음료 3 + 과자 2 + 커피 1 = 140 ✓ |

2단 칩 개별 클릭도 대조했다(외식 → 일식 48/48, 치킨 29/29, 피자 21/21, 분식 1/1, 한식 6/6, 전체 154/154).
**숫자가 거짓말하는 자리는 없었다.** 커밋 `093e416` 가 고친 "2단 숫자가 전체 기준이라 가공식품>커피 95라고
써놓고 1건" 문제는 실제로 해소돼 있다(전체 탭 커피 165 = 카페 164 + 가공식품 1).

재현:
```js
// http://127.0.0.1:8778/sinsang-note/ 콘솔
const vis=()=>[...document.querySelectorAll('a.c')].filter(e=>e.offsetParent!==null).length;
for(const t of document.querySelectorAll('nav button[data-f]')){t.click();await new Promise(r=>setTimeout(r,120));
  console.log(t.textContent, document.querySelector('.cnt').textContent, vis());}
```

### 2-2 검색 — 대체로 좋다. 걸린 것 셋
낱말 단위 AND 매칭이라 `촉촉 몽블랑` 처럼 띄어 쳐도 `촉촉한 몽블랑` 이 걸린다. 영문(`latte` 22건,
`americano`·`Americano` 동일), 대소문자 무시, 앞뒤 공백 trim(`  단팥  ` 14건) 다 정상.
`data-raw` 색인도 작동한다 — `도)돈까스쏘야더블정식`·`유라가)생초코모찌`·`삼립)` 전부 걸린다.

걸린 것:
1. **`소보로빵` 0건 / `소보루빵` 5건.** 한국어 표기 흔들림(소보로·소보루)을 흡수하지 않는다.
   사람이 더 많이 치는 쪽은 `소보로` 다.
2. **`비락식혜` 2건인데 제목이 똑같다**(§1-6).
3. `CJ)얼큰우동` 0건 — 이건 **정상**이다. `얼큰우동` 이라는 상품이 데이터 7,217건 어디에도 없다
   (docstring 의 예시일 뿐이다). 같은 이유로 `말랑카우` 0건도 정상이다 — 데이터엔 2건 있지만
   둘 다 신제품 목록 밖이고, 홈 검색은 홈 카드만 색인한다.
```
python3 -c "
import json;rows=json.load(open('data/products.json',encoding='utf-8'))['products']
for t in ('얼큰우동','말랑카우'): print(t, [(r['brand'],r['name']) for r in rows if t in r['name']])"
```

### 2-3 정렬 토글 · 조건 지우기 — 정상
- `최신순 ↔ 브랜드순` 왕복 2회, 상태·라벨·순서 모두 정상 복귀.
  브랜드순 1위 `교촌치킨/간장윙콤비`, 최신순 1위 `홍루이젠/초당옥수수 샌드위치`.
- **"조건 모두 지우기"는 0건일 때만 나타난다.** 결과가 1건이라도 있으면 DOM 에 버튼이 없다
  (`showEmpty()` 가 `#noresult` 안에 그릴 때만 생긴다). 눌러 보니 탭·칩·검색어가 전부 초기화되고
  전건이 다시 보인다(1,055/1,055). **동작은 맞다.** 다만 "카페 + 빙수 + 설빙" 처럼 14건이 걸러진
  상태에서는 되돌릴 버튼이 없어 탭을 직접 '전체'로 눌러야 한다.
- 0건 메시지가 조건을 짚어 준다: `카페 + 빙수 + '설빙' 에 해당하는 제품이 없습니다.`

### 2-4 모바일 375px — 가로 스크롤 없음
`resize_window(mobile)` → `document.documentElement.scrollWidth` 375 = `innerWidth` 375.
2열 그리드, 탭 가로 스크롤 정상. **사진 없는 카드가 모바일에서 특히 크게 비어 보인다**(§1-9, 스크린샷 확인).

### 2-5 하위 페이지
| 페이지 | 결과 |
|---|---|
| `/c/굿즈/` | 13장, 제목 `굿즈 신상 — 2026년 10월`, lead `최근 신제품 13건` — 숫자 일치 |
| `/p/bbq-순살-치킨버거-마일드/` | 빵부스러기 `신상노트›치킨›BBQ›…`, 등록일·브랜드·유형·카테고리·유튜브·형제 상품 5장 정상 |
| `/b/bbq/` · `/c/치킨/` | 200, 카드 렌더 정상 |
| `/404.html` | `페이지를 찾을 수 없습니다 — 신상노트`, 목록으로 돌아가는 링크 1개 |
| 없는 주소 | 로컬 `http.server` 는 자체 404 를 준다(GitHub Pages 가 `404.html` 을 쓰므로 **로컬에선 검증 불가, §5**) |

⚠️ 상세·브랜드·유형 페이지에는 검색창·정렬·탭이 **없다**. 홈에만 있다.

### 2-6 콘솔 에러 · 깨진 이미지 — 0건
- 콘솔 로그 0건(`read_console_messages`).
- 홈 `<img>` 1,232장을 `loading='eager'` 로 바꿔 전부 로드 완료시킨 뒤 `naturalWidth===0` 을 셌다 → **0건**.
  `pending 0`. 롯데칠성 3장도 Chrome 에서는 정상 로드된다(§1-11).

### 2-7 유튜브 링크 — 홈에는 **없다.** 상세 페이지 1,250장 중 889장에만 있다
```
grep -c 'youtube' docs/index.html            → 0
grep -rl "youtube" docs/p | wc -l            → 889
```
형태는 영상 직링크가 아니라 **검색 결과 링크**다:
`https://www.youtube.com/results?search_query=BBQ+순살+치킨버거`.
`_yt_query()` 가 `display`(정규화된 이름)를 쓰므로 `CU 삼립)프로H옥수수크림빵` 상세의 링크는
`CU 프로H옥수수크림빵` 으로 나간다 — **링크 쪽은 정규화가 적용돼 있다**(같은 페이지 제목은 아니다, §4-1).
실제로 눌러서 그 상품이 나오는지는 **미확인**(§5).


---

## §3 수집기 — 업체 전수조사 (어댑터 54개 / 브랜드 61곳)

*(§3-0 스윕 결과는 아래 §3-4. 먼저 지목된 27곳을 하나씩 본 결과를 적는다.)*

**이 절의 가장 큰 발견부터.** B군의 질문 "브랜드가 날짜를 안 주는 건지, 우리가 안 받는 건지" 의 답은
**대부분 우리가 안 받는 것**이다. 그리고 그 결과가 §1-2·§1-3 이다.

### 3-1 🔴 날짜 0% 브랜드 — **이미지 `Last-Modified` 가 전건 나온다. 안 받고 있을 뿐이다**

이마트24가 쓴 바로 그 수다. 이미 네 어댑터가 쓰고 있다:
`collectors/cu.py` · `collectors/emart24.py` · `collectors/chicken_bbq.py` · `collectors/chicken_kyochon.py`.
날짜 0% 인 18곳에 같은 걸 대 봤다(2026-10-01 18:0x KST 실측, 전건 HEAD):

| 브랜드 | 이미지 | Last-Modified 획득 | 분포 | 쓸 만한가 |
|---|---|---|---|---|
| 설빙 | 96 | **96/96** | 2025-02(54) … 2026-09(4) | ✅ 흩어져 있다 |
| 커피빈 | 166 | **166/166** | 2026-02(68)·2026-03(39)·2026-09(10) … | ✅ |
| 던킨 | 215 | **215/215** | 2025-02(75)·2026-08(25)·2026-09(11) … | ✅ |
| 빽다방 | 299 | **299/299** | 2021-05(82)·2026-07(30)·2026-09(12) … | ✅ (경로에도 `/2026/09/` 가 299건 전건) |
| 매머드커피 | 24 | **24/24** | 2026-06(13)·07(6)·09(5) | ✅ |
| 스시로 | 46 | **46/46** | 2026-09(46) 한 덩어리 | △ 월 단위로만 |
| 팔도 | 102 | 전건 | 2025-01 ~ 2026-06 | ✅ |
| 미스터피자 | 78 | 전건 | 2025-12 ~ 2026-07 | ✅ |
| 파파존스 · 샐러디 · 프랭크버거 · 컴포즈커피 | 전건 | 전건 | 흩어짐 | ✅ |
| 세븐일레븐 | 154 | 전건 | **2014-09** 같은 값이 나온다 | ❌ 서버 mtime 이 아니다 |
| 홍루이젠 | 43 | 전건 | 2024-03 ~ 2024-07 | △ 쓸 수는 있으나 상품 등록일보다 이르다 |
| 삼송빵집 | 37 | 전건 | 2023-05 (공용 `/images/sub/` 경로) | ❌ 상품별 파일이 아니다 |
| 죠스떡볶이 | 14 | 전건 | 2018-06 | △ |
| 나폴레옹과자점 | 354 | **0** | imagekit CDN 이 헤더를 안 준다 | ❌ |
| 에그드랍 | 0 | — | 이미지 자체가 없다(§1-9) | ❌ |

**이게 왜 중요한가 — 지금 화면의 날짜 없는 NEW 카드 대부분이 실은 낡았다.**
`Last-Modified` 는 "그 뒤로 파일이 안 바뀌었다" 는 뜻이라 **나이의 하한**이다. 그 값으로 60일 창
(cutoff 2026-08-02)을 재면:

| 브랜드 | 화면에 NEW 로 떠 있는 수 | 이미지가 창 밖 | 최악 사례 |
|---|---|---|---|
| 팔도 | 46 | **39** | `팔도 비빔국수` 2025-01-31, `뽀로로 과일맛 젤리 쁘띠` 2025-01-31, `아리 모던누들` 12종 2026-06-01 |
| 커피빈 | 28 | **20** | `달고나 크림 라떼`·`에스프레소 달고나 크림 라떼` **2021-05-17** |
| 매머드커피 | 24 | **19** | `몰티즈 자망코 컵빙수` 2026-06-16 |
| 미스터피자 | 17 | **16** | `콤비네이션 샌드`·`치킨텐더 샌드`·`소세지 샌드` 2025-12-05 |
| 설빙 | 14 | **10** | `인절미설빙` **2025-02-18**, `인절미토스트`·`인절미라떼` 2025-02-17 |
| 홍루이젠 | 5 | **5** | `프레시 파 베이컨 크림치즈` **2024-03-01** (= 최신순 1페이지 카드) |
| 삼송빵집 | 5 | **5** | `콘짜렐라` 4종 **2024-04-24** |
| 파파존스 | 5 | **5** | `메가 초코칩 쿠키`·`바베큐립 콤보` 2026-01-27 |
| 프랭크버거 | 3 | **3** | 3건 모두 2026-07-14 |
| 던킨 | 5 | 2 | `허니 바이츠` 2026-03-31 |
| 죠스떡볶이 | 1 | **1** | `죠스떡볶이` **2018-06-05** |
| 빽다방 | 11 | 1 | `고메버터소금빵` 2022-10-27 |
| 샐러디 3 · 세븐일레븐 11 | — | 0 | 전부 창 안 |

합계 **126장**. §1-3 에서 "13년 된 간판 메뉴" 라고 쓴 `인절미설빙`·`죠스떡볶이` 가
각각 2025-02-18 · 2018-06-05 로 수치가 붙는다.

재현:
```
python3 - <<'EOF'
import json, httpx, email.utils, concurrent.futures as cf, datetime
rows=json.load(open('data/products.json',encoding='utf-8'))['products']
UA={"User-Agent":"sinsang-note/1.0 (+https://github.com/ttop32/sinsang-note)"}
def lm(u):
    try:
        with httpx.Client(headers=UA,timeout=20,follow_redirects=True) as c:
            r=c.head(u)
            if r.status_code>=400: r=c.get(u,headers={**UA,'Range':'bytes=0-1'})
        t=email.utils.parsedate(r.headers.get('last-modified') or '')
        return datetime.date(*t[:3]).isoformat() if t else ''
    except Exception: return ''
for b in ['설빙','커피빈','팔도','미스터피자','삼송빵집','홍루이젠','파파존스','죠스떡볶이','매머드커피','던킨','빽다방','프랭크버거']:
    rs=[r for r in rows if r['brand']==b and r.get('is_new') is True and r.get('image')]
    with cf.ThreadPoolExecutor(12) as ex: res=list(ex.map(lm,[r['image'] for r in rs]))
    old=[(d,r['name']) for r,d in zip(rs,res) if d and d<'2026-08-02']
    print(f'{b}: NEW {len(rs)}건 중 창 밖 {len(old)}건', sorted(old)[:3])
EOF
```

**고치려면**: `base` 에 `uploaded_at_from_image(client, url)` 를 한 벌 두고
(지금 `chicken_bbq._uploaded_at` 과 `chicken_kyochon._uploaded_at` 이 **글자까지 같은 함수를
각자 복사해 갖고 있다**), 위 ✅ 표시 브랜드에서 호출한다. 세븐일레븐·삼송빵집처럼 값이 엉뚱한 곳은
쓰지 않는다 — **브랜드별로 실측해 보고 넣어야 한다**(이마트24가 그렇게 했다).
요청 수는 브랜드당 상품 수만큼 늘어나지만, CU 가 이미 666건에 쓰고 있고 캐시 경로(`known=prev`)도 있다.

⚠️ 반대 위험도 같이 적는다. `Last-Modified` 는 **일괄 재업로드에 똑같이 속는다** — 설빙 54건이
2025-02 한 달에, 빽다방 82건이 2021-05 에 몰려 있다. 그래서 §1-1 의 `untrust_bulk_dates()` 를
**반드시 같이 통과시켜야** 하고, 날짜가 새로 붙는 쪽이 아니라 **낡은 걸 떨구는 쪽으로만** 써야 안전하다.

### 3-2 🔴 컴포즈커피 — **NEW 배지는 있다. 이미지 안에 그려져 있어서 HTML 로는 안 보였다**

A군에서 유일한 "진짜 결함"이다.

`collectors/cafe_compose.py` docstring:
> 신제품 신호가 **하나도 없다.** 2026-09-30 실측으로 확인한 내용:
>   - NEW 배지 없음. 페이지의 NEW 는 전부 'NEWS' 메뉴 이름이다.

**이 문장이 틀렸다.** 배지는 상품 사진 JPEG 안에 합성돼 있다 — 오른쪽 아래 노란 별모양에
흰 글씨 `NEW`(#FFD800). HTML 에는 흔적이 없으니 텍스트만 훑으면 절대 안 보인다.
목록 HTML 을 눈으로 확인했다 — 카드는 `<img src>` + `<div class="cafemenu-menu-name">` 뿐이고
`data-*`·배지 요소가 0개다.

**200건 중 16건에 배지가 있다**(색 비율로 셈):
```
빅포즈 솔티드 쿨리치 · 논산에서 온 수박주스 · H-비스코프 라떼 · I-비스코프 라떼 ·
H-딸기 자스민 밀크 티브리즈 · I-딸기 자스민 밀크 티브리즈 · 솔티드 쿨리치 ·
명란 소프트 바게트 · 초코 바게트 · 생크림 시나몬 크루아상 · 아이스크림 크루아상 ·
요거폼 포도자스민 티브리즈 · 밤 티라미수 · 헨젤과 프레첼 · 쫀득카노 · 커피엔 역시 커피빵
```
재현:
```
python3 - <<'EOF'
import sys, io, httpx, concurrent.futures as cf; sys.path.insert(0,'.')
from PIL import Image
from collectors import cafe_compose as cc
UA={"User-Agent":"sinsang-note/1.0 (+https://github.com/ttop32/sinsang-note)"}
def badge(it):
    with httpx.Client(headers=UA,timeout=25,follow_redirects=True) as c: r=c.get(it.image)
    im=Image.open(io.BytesIO(r.content)).convert("RGB"); w,h=im.size
    px=list(im.crop((int(w*.5),int(h*.65),w,h)).getdata())
    n=sum(1 for p in px if abs(p[0]-255)<12 and abs(p[1]-216)<18 and p[2]<40)
    return it.name, n/len(px)
items=cc.fetch()
with cf.ThreadPoolExecutor(12) as ex:
    hits=[(n,f) for n,f in ex.map(badge,items) if f>0.02]
print(len(items),'건 중 배지',len(hits)); [print('  ',n) for n,_ in hits]
EOF
```
→ `200 건 중 배지 16`

**고치려면**: 썸네일을 받아 오른쪽 아래 사분면의 `#FFD800` 비율을 보는 검사를 넣는다
(요청 200회. `Last-Modified` 수집과 같은 HEAD/GET 패스에 얹으면 추가 비용이 거의 없다).
그리고 **docstring 의 "NEW 배지 없음" 문장을 고쳐야 한다** — 안 고치면 다음 사람이 또
"신호 없음" 으로 결론 내고 같은 자리를 다시 판다.

### 3-3 A군 나머지 7곳 — 전부 **"그 브랜드의 사실"** 이다 (어댑터 직접 실행해 확인)

| 브랜드 | 실행 결과 | 왜 화면 0장인가 | docstring 에 적혀 있나 |
|---|---|---|---|
| 김밥천국 62 | `62건 is_new=True 62` / 날짜 2024-12(36)·2017-04(26) | `/31 신메뉴` 가 **8년치 누적 아카이브**다. 썸네일 날짜 두 덩어리뿐이라 60일 창에서 전건 탈락. | ✅ 적혀 있다. ⚠️ 다만 "collect 의 STALE 판정에서 대부분 걸러진다" 는 **틀린 설명**이었다(STALE 은 18:03 전까지 참조 0). 실제로 거른 건 `WINDOW` 다. |
| 나폴레옹 354 | `354건 is_new=False 354` | `day8until_newarrival` 가 **신상품 배지 만료일**이고 354건 전부 만료(최신 20260831). 사이트 자신의 신상품 필터도 0건. | ✅ 매우 상세히 적혀 있다 |
| 바르다김선생 46 | `46건 True 4 / None 42` / 날짜 2018-07(20)·2023-11(4) | NEW 태그 4건의 썸네일 날짜가 **2023-11-22**. 창 밖. | ✅ |
| 본우리반상 37 | `True 17` / 최신 `2026-07-01` | 최신 신메뉴가 7월 1일. cutoff 8월 2일. | △ bon_if docstring 은 `newYn` 과 날짜 부재를 적었지만 "그래서 지금 0장이 정상" 은 없다 |
| 요거프레소 27 | `True 25 / False 2` / 최신 `released_at 2026-07-01` | **"신상 93%인데 화면 0" 의 답**: 브랜드 신메뉴 아카이브에 **7월 이후 새 글이 없다**. `released_at` 은 캡션의 '2026년 7월' 에서 온 진짜 값이다. | △ 월 1일 규칙은 상세히 적혀 있으나 "현재 0장" 설명은 없다 |
| 본흑염소 13 | `True 2` / 최신 `2025-12-15` | 작년 12월이 마지막 | △ |
| 명랑핫도그 7 | `True 7` / 최신 `2026-05-27` | 5월이 마지막. FLOOR_MIN=10 미만이라 급감 가드도 꺼져 있다. | ✅ |

세 곳(본우리반상·본흑염소·요거프레소)만 **docstring 에 "지금 화면 0장인 이유" 가 없다.**
다음 사람이 또 조사한다 — 한 줄씩 적어두는 게 맞다.

부수 발견: 나폴레옹 354건에 **`교환권 (3만원)`·`교환권 (2만원)`·`교환권 (1만원)`** 이 상품으로 들어 있다.
지금은 `is_new=False` 라 화면에 안 나오지만 식품이 아니다.

### 3-4 C군 전건 NEW — **5곳 중 1곳만 "어댑터가 무조건 True"**

| 브랜드 | 실측 | 판정 |
|---|---|---|
| CU 666 | 원본 1,200건 중 667건만 NEW (운영자 확인) | **브랜드의 사실.** 착시 아님 |
| 스시로 46 | `/pm` 이 '이달의 한정메뉴' 전용 페이지. `data-menu-group` 전건 '이달의 한정메뉴' → **대조군 0** | **브랜드의 사실.** docstring 에 ⚠️ 유보까지 적혀 있다("'이 달에 파는 것'이지 '이 달에 처음 나온 것'이 아니다") |
| 김밥천국 62 | `/31 신메뉴` 한 장만 받는다 → 대조군 0 | **구조상 전건 True.** docstring 에 적혀 있다 |
| hy프레딧 159 | '신제품' 탭만 받는다. 약 3개월 롤링 창 | **구조상 전건 True.** docstring 에 적혀 있다 |
| **버거킹 54** | 전문 응답에 228건이 오는데 `if NEW_FLAG not in labels: continue` (`burger_burgerking.py:82`) 로 **NEW 없는 건 버린다** | **어댑터가 거른다.** docstring 은 "전체 228건 중 71건" 이라고 수치만 적고 **"나머지는 저장하지 않는다" 를 안 적었다** |

버거킹은 "무조건 True 를 넣는" 건 아니고 "True 인 것만 남기는" 쪽이지만, 결과적으로
`/b/버거킹/` 이 "버거킹 신메뉴 전체" 가 아니라 "오늘 NEW 배지가 붙은 것" 이라는 걸
데이터만 봐서는 알 수 없다.

### 3-5 🔴 NEW 전용 어댑터 + `FLOOR` 가드 = **배지를 떼면 수집 실패로 읽힌다**

`collect.FLOOR = 0.7`, `FLOOR_MIN = 10` 은 "전일 대비 70% 밑으로 떨어지면 부분수집" 으로 보고
`RuntimeError` 를 올려 **이전 수집분을 그대로 이월**한다(`carried`).

NEW 가 붙은 것만 저장하는 브랜드에서는 **이 가드가 재는 것이 수집 성공률이 아니라 배지 개수**다.
브랜드가 지난 시즌 배지를 한 번에 떼면 그날 수집이 "실패" 로 기록되고 어제 데이터가 하루 더 남는다.

지금 노출된 브랜드(저장 건수 ≥ FLOOR_MIN 10, 전건 is_new=True):
```
CU 666 · hy프레딧 159 · 김밥천국 62 · 버거킹 54 · 스시로 46 · 요거프레소 27 ·
브레댄코 26 · 더벤티 25 · 매머드커피 24 · 샘표 21 · 롯데칠성음료 18 · 맘스터치 17 ·
오뚜기 15 · 아워홈 12 · GS25 11
```
버거킹은 **이미 아슬아슬하다** — docstring 실측(2026-09-30)이 71건인데 오늘 54건이다(−24%).
한 번만 더 떼면 `54 × 0.7 = 37.8` 선에 걸린다.

### 3-6 🟠 같은 기법, 가드는 절반만 — 조용한 실패 자리

이미지 `Last-Modified` 를 쓰는 어댑터 4곳 중 **CU·이마트24에만** "날짜를 못 받으면 예외" 가드가 있다.

```python
# collectors/cu.py:299
if want and not dated:
    raise ValueError("CU 비행사 … 전부 이미지 Last-Modified 를 못 받았다 …")
# collectors/emart24.py:224
#   "이마트24 이미지 Last-Modified 가 {len(items)}건 중 {dated}건뿐이다."
```
```python
# collectors/chicken_bbq.py:36  / collectors/chicken_kyochon.py:80  — 글자까지 같은 함수 두 벌
def _uploaded_at(client, img_url: str) -> str:
    """이미지의 Last-Modified 를 날짜로. 실패하면 조용히 비운다."""
    ...
    except Exception:
        return ""          # ← 가드 없음
```
BBQ(110건·날짜 100%)와 교촌(116건·날짜 100%)은 CDN 이 헤더를 끊으면 **예외 없이 전건 날짜가 비고**,
`is_new is False` 분기가 `bool(released_at)` 을 보므로 조용히 대부분이 화면에서 사라진다.
남는 건 `is_new=True` 인 것들뿐인데 그건 날짜가 없어 §1-2 경로로 **영구 체류**한다.
수집은 "성공" 으로 찍히고 아무도 모른다.


---

## §4 구조 — 같은 규칙이 두 곳에 있고 한쪽만 고쳐진 자리

### 4-1 🔴 **상품명 정규화가 홈에서만 적용됐다** (이 레포 최빈 결함의 4번째 사례)

커밋 `c2109db` "상품명 정규화·유튜브 링크·og 커버·피드 정렬" 이 홈 카드에만 들어갔다.

```python
# collect.py:card()            ← 홈
f'<h2>{e(r.get("display") or r["name"])}</h2>'
# web/pages.py:_card()         ← 브랜드·유형·굿즈 페이지, 상세의 '다른 신제품'
f'<h2>{E(r["name"])}</h2>'
```
`web/pages.py:_card()` 의 docstring 은 `"""목록용 카드. collect.card() 와 같은 모양이되 통째로 링크가 된다."""`
라고 적혀 있다 — **모양은 같은데 제목이 다르다.**

실측:
```
python3 -c "
import re,html,pathlib
s=pathlib.Path('docs/b/cu/index.html').read_text(encoding='utf-8')
print([html.unescape(x) for x in re.findall(r'<h2>(.*?)</h2>',s)][:5])
print('data-raw:', s.count('data-raw'))"
```
→ `['유라가)생초코말차모찌', '유라가)생초코모찌', '도)돈까스쏘야더블정식', '김)한돈불고기마늘쫑김밥', '주)너비아니전주비빔밥바']`
→ `data-raw: 0`

같은 상품이 홈에서는 `유라가 생초코말차모찌`, `/b/cu/` 에서는 `유라가)생초코말차모찌` 다.

**상세 페이지는 더 나쁘다 — `<h1>` 과 `<title>`·`og:title` 까지 원본이다:**
```
docs/p/cu-도-튀김순대떡볶이트리플/index.html
   <title> CU 도)튀김순대떡볶이트리플 — 신제품 | 신상노트
   <h1>    도)튀김순대떡볶이트리플
   유튜브   CU 튀김순대떡볶이트리플      ← 같은 페이지 안에서 링크만 정규화돼 있다
```
`web/pages.py:_yt_query()` 는 주석에 `정본은 base.derive() 가 채우는 d["display"] 다` 라고 쓰고
display 를 쓴다. **같은 파일이 display 의 존재를 알면서 제목에는 안 쓴다.**

규모:
```
python3 - <<'EOF'
import re,html,pathlib,glob,json
rows=json.load(open('data/products.json',encoding='utf-8'))['products']
byname={r['name']:r for r in rows}
tot=diff=0
for p in glob.glob('docs/p/*/index.html'):
    m=re.search(r'<h1[^>]*>(.*?)</h1>', pathlib.Path(p).read_text(encoding='utf-8'), re.S)
    if not m: continue
    tot+=1; h=html.unescape(m.group(1)).strip()
    r=byname.get(h)
    if r and (r.get('display') or h)!=h: diff+=1
print(tot, diff)
EOF
```
→ `1068 475` — **상세 475장의 제목·`<title>`·`og:title` 이 POS 문자열 그대로다.**
공유 카드에 나가는 제목이고 검색 색인에 들어가는 제목이다.
브랜드 페이지 53장·유형 페이지 25장의 카드 제목도 전부 원본이다.

**고치려면**: `web/pages.py` 에서 제목을 그리는 자리 전부(`_card`, `product_page` 의 h1,
`theme.head()` 에 넘기는 title/og:title, 빵부스러기)를 `r.get("display") or r["name"]` 로 바꾸고,
`_card` 에 `data-raw` 도 같이 심는다(지금 하위 페이지에는 검색이 없지만, 붙이면 바로 필요해진다).
더 나은 쪽은 **카드 HTML 을 한 함수로 합치는 것**이다 — 두 벌로 두는 한 또 갈린다.

### 4-2 🟠 `_when()` 이 두 벌 — 바로 옆 함수는 정본을 부르는데 이것만 복사본이다

```python
# web/pages.py:69
def _when(r: dict) -> str:
    """정렬용. '언제 것'인가 — 브랜드 날짜 우선, 없으면 처음 본 날."""
    return r.get("released_at") or r.get("uploaded_at") or r.get("first_seen", "")

# web/pages.py:74  ← 바로 다음 함수
def _shown_date(r: dict) -> str:
    """화면에 찍을 날짜. 정본은 collect.shown_date 다 — 두 벌로 두면 어긋난다."""
    import collect
    return collect.shown_date(r)
```
`web/seo.py` 는 `collect._when(r)` 을 직접 부른다(`seo.py:112,154,213,294`).
**세 모듈 중 둘은 정본을 쓰고 pages.py 만 복사본을 쓴다.** 지금 내용은 같다 — 그래서 더 위험하다.
정렬 기준을 한 번 손대면 홈·피드·사이트맵만 바뀌고 브랜드·유형 페이지는 옛 순서로 남는다.

### 4-3 🟠 `_SPEC` 와 `_MULT` 가 서로를 모른다 (§1-7 의 원인)

```python
# collectors/base.py:423
_UNIT = r"(?:kg|개입|ml|인분|g|l|t|p|입|매)"
_SPEC = re.compile(r"(?<=.)(?<![\d,.])\d+(?:\.\d+)?" + _UNIT + r"(?![A-Za-z0-9])", re.I)
# collectors/base.py:427
# `*6`·`*4입` 같은 묶음 표기. `x`·`X` 는 넣지 않는다 — `자이언트X3` 이 걸린다.
_MULT = re.compile(r"\s*[*×]\s*\d+\s*(?:개입|입|매|p)?(?![A-Za-z0-9가-힣])", re.I)
```
`_MULT` 가 `x` 를 **일부러** 제외한 사정을 `_SPEC` 는 모른 채 앞의 `50g` 만 지운다 →
`두부흑임자스낵 50g x 5개` → `두부흑임자스낵 x 5개`. 5장이 그 모양이다.

### 4-4 🟠 세트 표기 정규식이 **세 벌**, 단위 목록이 **두 벌**

```python
collect.py:325  _VARIANT  = (라지\s*세트|L\s*세트|더블\s*PICK\s*세트|세트|콤보|단품)$   # merge_variants
collect.py:384  _SET      = 세트|콤보                                                  # drop_sets 의 게이트
collect.py:387  _SET_TAIL = (?:라지\s*)?(?:세트|콤보)$                                 # 본품 이름 후보 만들기
```
셋이 같은 개념("세트 표기")을 세 가지 목록으로 들고 있다. `_VARIANT` 에만 `단품`·`L 세트`·
`더블 PICK 세트` 가 있고 `_SET_TAIL` 에는 없다. §1-4 의 `피치 세트 M (배달)`·`피치 세트 L (배달)` 이
합쳐지지 않는 게 정확히 이 틈이다 — 어느 정규식도 `세트 M` 꼴을 모른다.

```python
collectors/base.py:16  _SIZE = ^(L|M|S|XL|EX|대|중|소|Mini|Regular|Large|HOT|ICE|ICED|아이스|핫|\d+\s*(ml|mL|L|g|G|kg|인분|개입|P|입))$   # make_key
collectors/base.py:423 _UNIT = (?:kg|개입|ml|인분|g|l|t|p|입|매)                                                                      # display_name
```
`_SIZE` 에는 `매` 가 없고 `_UNIT` 에는 `P` 가 소문자뿐이다. 한쪽에 단위를 보태도 다른 쪽은 모른다.
**§1-6 의 `이천햅쌀 비락식혜 1.5L` 중복이 이 틈이다** — `display_name` 은 `1.5L` 을 떼는데
`make_key` 는 `1.5L` 이 괄호 밖이라 안 뗀다. 두 이름이 서로 다른 키로 살아남아 같은 제목으로 그려진다.

### 4-5 🟡 푸터 숫자 문구가 `PER_BRAND` 를 들먹인다 — 지금 값이 0 이다

```python
# collect.py:741
count = (f"최근 {WINDOW}일 신제품 {whole}건 · "
         f"브랜드마다 최신 {PER_BRAND}장씩 {len(shown)}장"
         if whole > len(shown) else f"최근 {WINDOW}일 신제품 {len(shown)}건")
```
`PER_BRAND = 0` 이면 `cap_per_brand` 가 그대로 돌려주므로 `whole == len(shown)` 이라 지금은
죽은 분기다. 하지만 **`SHOW` 만 다시 켜면** (`SHOW=300`, `PER_BRAND=0`)
`"… 1055건 · 브랜드마다 최신 0장씩 300장"` 이라고 쓴다. 두 개의 다른 상한(`PER_BRAND`·`SHOW`)을
한 문장이 하나인 것처럼 설명한다.

### 4-6 🟡 docstring 이 코드보다 앞서가거나 뒤처진 자리

- `collectors/cafe_compose.py` — "NEW 배지 없음" (§3-2). **사실과 다르다.**
- `collectors/snack_kimbabcheonguk.py` — "collect 의 STALE 판정에서 대부분 걸러진다".
  STALE 은 18:03 커밋 전까지 **참조 0** 이었다. 실제로 거른 건 `WINDOW` 다.
  (`cafe_coffeebean.py` 는 반대로 "STALE 가지치기가 걸리지 않으니 …" 라고 정확히 적어뒀다.
  **두 어댑터가 같은 상수에 대해 정반대로 적고 있었다.**)
- `collectors/burger_burgerking.py` — NEW 없는 건 버린다는 사실을 안 적었다 (§3-4).
- `collectors/fredit.py` — "⚠️ 화면 40칸 경고. `collect.PER_BRAND` 가 40인데 …". 지금 0 이다.
- `collectors/cafe_paikdabang.py` — 이미지 경로의 `/2026/09/` 를 "일이 없으니 안 쓴다" 며 버리는데,
  `collectors/cafe_yogerpresso.py` 와 `dessert_baskinrobbins.py` 는 **같은 월 정밀도 정보를 '그 달 1일'로
  released_at 에 넣는다.** 세 어댑터가 같은 상황에 정반대 정책을 쓴다.
  빽다방은 `Last-Modified` 로 **일 단위까지** 받을 수 있는데(§3-1) 그것도 안 본다.

### 4-7 🟡 조용한 실패 — 깨져도 예외 없이 빈 값을 내는 자리

`except Exception` 은 레포 전체에 7곳뿐이고 대부분 호스트 순회(스타벅스·설빙·폴바셋)나
브랜드 격리(`collect.py:163`)라 의도된 것이다. 문제는 아래 셋:

| 자리 | 조용히 비는 값 | 결과 |
|---|---|---|
| `chicken_bbq.py:42` `except Exception: return ""` | BBQ 110건의 날짜 전부 | §3-6 |
| `chicken_kyochon.py:87` 같은 코드 | 교촌 116건의 날짜 전부 | §3-6 |
| `pizza_pizzahut.py:99` `except Exception: … pass` | — | 미확인(§5) |

그리고 어댑터 54개 중 **24개가 자체 가드(`raise`)가 없다** — 전적으로 `collect` 의 0건 가드와
`FLOOR` 에 기댄다. 그 둘은 **"건수" 만 본다.** 이름이 통째로 바뀌어도(§지시문이 경고한 모양)
건수만 맞으면 통과한다.
```
for f in collectors/*.py; do b=$(basename $f .py); case $b in base|__init__) continue;; esac;
  grep -q "raise " $f || echo "  $b"; done
```
→ `bakery_knotted bakery_napoleon bakery_parisbaguette burger_frankburger burger_momstouch
cafe_coffeebean cafe_yogerpresso chicken_bbq chicken_bhc chicken_goobne dessert_baskinrobbins
ediya maker_lottewellfood maker_orion maker_ottogi mega pizza_mrpizza pizza_papajohns
pizza_pizzahut snack_barunkim snack_jaws snack_kimbabcheonguk snack_myungrang toast_isaac`

### 3-7 🟠 이마트24 — 전수 실행 중 **가드가 터졌다** (간헐적)

54개 어댑터 전건 실행(§3-8) 중 이마트24만 예외로 끝났다. 2026-10-01 18:0x KST:
```
ValueError: 이마트24 /goods/event 의 분류 메뉴가 달라졌다.
  기대 {'1': '간편식사', '2': '과자', '3': '생활용품', '5': '음료'}
  실제 {'1': '골라담기', '2': '과자', '5': '음료', '3': '생활용품'}
  — 어긋난 것 {'1': '간편식사'}
```
이건 `collectors/emart24.py:213 _check_nav()` 가 의도대로 동작한 것이다. 문제는 **재현이 안 된다**는 것:
그 뒤 같은 URL·같은 파라미터로 **28회 재요청했는데 28회 모두 `'1': '간편식사'`** 가 나왔다
(seq 1·2·3·5 각 1회 + seq=1 로 24회).
```
python3 - <<'EOF'
import sys,time,collections; sys.path.insert(0,'.')
import httpx; from collectors import emart24 as e
UA={"User-Agent":"sinsang-note/1.0 (+https://github.com/ttop32/sinsang-note)"}
bad=0
with httpx.Client(headers=UA,timeout=30,follow_redirects=True) as c:
    for i in range(24):
        r=c.get(e.URL.format(section="event"), params={"search":"","page":1,
                 "category_seq":"","base_category_seq":"1","align":"RECENT"})
        nav=e._nav_categories(r.text)
        if nav.get('1')!='간편식사': bad+=1; print(i,nav)
        time.sleep(0.4)
print('24회 중 어긋남', bad)
EOF
```
→ `24회 중 어긋남 0`

즉 사이트가 **가끔** 다른 내비게이션을 내려준다(어댑터 docstring 이 이미 적어둔
"분류를 고른 상태로 열면 혜택 링크가 base_category_seq 를 그대로 물고 온다" 상황이
간헐적으로 재발하는 모양이다). 터지면 **이마트24 981건이 통째로 이월분으로 떨어지고**
`collect.main()` 이 `SystemExit` 으로 끝나 Actions 가 빨개진다.
`_nav_categories` 가 `category_seq=` 가 **빈 값**인 링크만 고르게 돼 있는데,
그 조건이 간헐적으로 안 먹는다는 뜻이다. 터진 응답 본문을 안 남겨서 **원인은 미확인(§5)** —
`_check_nav` 가 실패할 때 HTML 을 덤프하도록 해두면 다음에 잡을 수 있다.

### 4-1 보강 — 정규화가 빠진 면이 **네 군데 더** 있다 (RSS 포함)

`web/seo.py:_entry()` 도 `r.get("name","")` 를 쓴다.
```
python3 -c "
import re,pathlib,html,json
rows=json.load(open('data/products.json',encoding='utf-8'))['products']
bn={r['name']:r for r in rows}
ts=[html.unescape(t) for t in re.findall(r'<entry>\s*<title>(.*?)</title>',
      pathlib.Path('docs/feed.xml').read_text(encoding='utf-8'), re.S)]
print(len(ts), sum(1 for t in ts if t in bn and (bn[t].get('display') or t)!=t))"
```
→ `1051 470` — **Atom 피드 제목 470건이 POS 문자열 그대로다**(`햄)스파이시마요치킨버거`).

정리하면 `display` 를 쓰는 곳은 **홈 카드와 상세의 유튜브 링크 둘뿐**이고,
안 쓰는 곳은 상세 `<h1>`·`<title>`·`og:title`(475장) · 브랜드 페이지 53장 · 유형 페이지 25장 ·
굿즈 페이지 · `feed.xml` 470건 · `alt` 텍스트다.

---

## §5 미확인 — 못 본 것 (본 표본을 숫자로)

### 본 것 (숫자)
| 대상 | 본 양 |
|---|---|
| 홈 카드 제목 | **1,237장 전건**(17:51 빌드) + **1,055장 전건**(18:03 빌드) — 둘 다 브랜드별로 나눠 눈으로 읽었다 |
| 홈 카드 이미지 | **1,232장 전건** 로드 검증(강제 eager → `naturalWidth` 확인) + **292개 고유 URL** HTTP 상태 확인 |
| `/c/굿즈/` | **13건 전건** |
| 데이터 전체 | `data/products.json` **7,217건** 전건에 대해 주류·굿즈 단어 스캔, `nonfood=True` **276건 전건** 이름 확인 |
| 이미지 `Last-Modified` 실측 | **18개 브랜드** 샘플 + 설빙 96 · 커피빈 166 · 던킨 215 · 빽다방 299 · 매머드 24 · 스시로 46 **전건** HEAD |
| 어댑터 직접 실행 | 전수 스윕 54개(§3-8) + 개별 재실행 7개(버거킹·컴포즈·요거프레소·나폴레옹·김밥천국·바르다김선생·본아이에프) |
| docstring 통독 | 12개 어댑터 |
| 브라우저 조작 | 탭 5 × 칩 24, 검색어 **29개**, 정렬 왕복 2회, 리셋 1회, 375px 1회, 하위 페이지 6장 |
| 상세 페이지 | **1,068장**의 `<h1>` 자동 대조 + 5장 수동 열람 |
| 유튜브 링크 | **2건 실제 클릭**(버거킹 트러플 머쉬룸 와퍼 / CU 튀김순대떡볶이트리플) — 둘 다 그 상품 영상이 상단에 나왔다 |

### 못 본 것
1. **배포본(`ttop32.github.io`)을 안 봤다.** 지시대로 로컬 산출물만 봤다. 배포본과 로컬이 같은지는 미확인.
2. **없는 주소의 404 처리.** 로컬 `http.server` 는 자기 404 를 준다. GitHub Pages 가 `docs/404.html` 을
   실제로 내주는지는 배포본에서만 확인된다. (`404.html` 자체는 정상 렌더된다.)
3. **Firefox·Safari·모바일 WebView.** §1-11 의 롯데칠성 인증서 문제는 Chrome 에서만 확인했다.
   Chrome 은 AIA fetching 으로 복구한다. 다른 엔진에서 깨지는지 **미확인**.
4. **유튜브 링크 889개 중 887개.** 2건만 눌러 봤다. 상품명이 짧고 일반적인 것
   (`죠스떡볶이`·`티라미수`·`몽블랑`)은 엉뚱한 영상이 나올 수 있는데 확인 안 했다.
5. **시즌 재출시 판정.** 이디야 `씨앗호떡`·`팥붕어빵`·`슈크림붕어빵`·`반반붕어빵`·`잡채호떡`·
   `피자호떡`·`햄치즈계란빵` 7종이 2026-09-01 한 날에 들어왔다(SURGE 8 · BULK_MIN 20 둘 다 미달).
   해마다 가을에 돌아오는 품목으로 보이는데, 이미지가 **2026-09-01 에 새로 올라가** 있어서
   `Last-Modified` 로는 재출시인지 신규인지 **못 가린다.** 버거킹 `트러플 머쉬룸 와퍼`도 같다 —
   유튜브에 "1년 전" 리뷰와 "재출시 트머와" 영상이 있지만, 브랜드가 "올가을 뉴~해진 트머와" 라고
   광고하고 있어 리뉴얼인지 재출시인지 판단을 유보한다.
6. **이마트24 가드가 왜 터졌는지(§3-7).** 터진 응답 HTML 을 안 남겨서 재현 못 했다. 28회 재시도 전부 정상.
7. **상세 페이지 1,250장 중 1,068장만** `<h1>` 을 대조했다(나머지는 상품명 매칭이 안 돼 셈에서 빠졌다).
8. **CU 338건·hy프레딧 75건의 개별 신제품 여부.** 이름은 전건 읽었고 명백한 상시품목은 없었지만,
   `데일리)파프리카2입`·`도드람)한돈삼겹살300g`·`데일리)캠벨포도500g(팩)`·`데일리)제수용햇사과3입`
   같은 **농축산물·상시 SKU** 가 "신상품" 으로 올라오는 게 맞는지는 판단하지 않았다
   (브랜드가 자기 신상품 피드에 넣은 것이라 "거짓" 이라고 단정할 근거가 없다).
9. **`pizza_pizzahut.py:99` 의 `except … pass`** 가 무엇을 삼키는지 안 봤다.
10. **성능·접근성.** 홈 1,055장이 한 문서(781KB)다. 저사양 기기에서의 렌더 비용과 스크린리더 동작은 미확인.

### 3-8 ✅ 어댑터 54개 전건 실행 — **53개 정상, 저장분과 건수 완전 일치. 1개 실패**

2026-10-01 18:08~18:30 KST, `collect.ADAPTERS` 전건을 실제 네트워크로 돌려
`data/products.json`(17:51 스냅샷)과 대조했다.
```
# 전체 스크립트: 아래를 파일로 저장해 실행
import sys, json, collections, inspect, time
sys.path.insert(0, '/Users/swkim72/source/sinsang-note')
import collect
from collectors import base
stored = json.load(open('data/products.json', encoding='utf-8'))['products']
scount = collections.Counter(p['brand'] for p in stored)
prev = {base.make_key(p['brand'], p['name']): p for p in stored}
for mod in collect.ADAPTERS:
    names = collect.brands_of(mod)
    try:
        items = mod.fetch(known=prev) if 'known' in inspect.signature(mod.fetch).parameters else mod.fetch()
        print(mod.__name__, sum(scount[n] for n in names), len(items),
              sum(1 for i in items if i.is_new is True),
              sum(1 for i in items if i.released_at or i.uploaded_at))
    except Exception as e:
        print(mod.__name__, 'ERR', e)
```

| | 수 |
|---|---|
| 돌린 어댑터 | **54** |
| 실행 성공 | **53** |
| **저장 건수와 실행 건수가 다른 것** | **0** |
| 실패 | **1** (emart24, §3-7) |

**"조용히 0건이 된 어댑터는 없다."** 54개 중 0건을 낸 곳도 없다.
가장 적은 곳이 배스킨라빈스 2건인데 `/menu/fom.php`('이달의 맛') 한 장만 받도록 설계된 것이고
docstring 에 근거가 적혀 있다(전체 메뉴는 "신제품 신호가 없어서 긁어봐야 카탈로그만 불어난다").
굽네 8건·명랑핫도그 7건도 각각 NEW 전용 경로다.

실행 시간이 긴 곳(이미지 HEAD·페이지 순회): 동서식품 129초 · 오리온 65초 · 매머드 61초 ·
더벤티 51초 · 커피빈 45초 · 폴바셋 44초.

전수표에서 **새로 눈에 띈 것 하나**:

**파리바게뜨 — 사이트 545건인데 어댑터는 530건. 사라지는 15건 중 9건이 서로 다른 SKU다.**
```
python3 - <<'EOF'
import sys, json, collections, httpx, html; sys.path.insert(0,'.')
from collectors import base
UA={"User-Agent":"sinsang-note/1.0 (+https://github.com/ttop32/sinsang-note)"}
c=httpx.Client(headers=UA,timeout=30,follow_redirects=True); rows=[]
for pg in range(1,7):
    r=c.get("https://www.paris.co.kr/wp-json/wp/v2/product",params={"per_page":100,"page":pg,"_fields":"id,title"})
    d=json.loads(r.content.decode("utf-8-sig"));  rows += d
    if not d: break
names=[html.unescape(" ".join((x['title']['rendered'] or '').split())) for x in rows]
k=collections.Counter(base.make_key("파리바게뜨",n) for n in names)
print(len(rows), '건 중 키 중복으로 접히는 것', sum(v-1 for v in k.values() if v>1))
for key,v in [(a,b) for a,b in k.items() if b>1][:12]:
    print('  ', [n for n in names if base.make_key("파리바게뜨",n)==key])
EOF
```
→ `545 건 중 키 중복으로 접히는 것 15`
```
['모짜렐라 치즈봉', '모짜렐라 치즈봉(2개입)']
['감자쫀떡(1개입)', '감자쫀떡(2개입)']          ← 다른 SKU 인데 한 건으로 접힌다
['구움과자 아뜰리에 (10개입)', '구움과자 아뜰리에 (15개입)']   ← 같음
['화과자 오감(소)', '화과자 오감(대)']            ← 같음
['마늘빵', '마늘빵 (5개입)'] / ['딸기롤페스츄리', '딸기롤페스츄리(3개입)']
['우유 듬뿍 연유브레드', '우유 듬뿍 연유브레드(대)'] / ['감자 크로켓(2개입)', '감자 크로켓']
['멕시칸소시지페스츄리(2개입)', '멕시칸소시지페스츄리']
['단팥빵', '단팥빵'] / ['슈크림빵', '슈크림빵'] / ['소보루빵', '소보루빵']   ← 진짜 중복 글(재발행)
```
`base.make_key()` 의 `_SIZE` 가 `대|중|소` 와 `\d+개입` 을 "같은 상품의 사이즈 표기" 로 보고 턴다.
`(소)`/`(대)` 는 그 설계가 맞지만 **`(1개입)` vs `(2개입)`, `(10개입)` vs `(15개입)` 은 다른 상품이다.**
접힌 쪽은 어댑터의 `seen` 에서 **통째로 버려져** 상세 페이지도 안 생기고 검색으로도 못 닿는다.
`drop_sets` 가 "조용히 지워지는 쪽이 더 나쁘다" 며 피하려던 바로 그 모양인데, 여기서는 일어나고 있다.
거짓양성(아닌데 걸린 것)이 아니라 **거짓음성(맞는데 안 걸린 것)** 이다.

### 3-9 지목된 27곳 최종 판정표

| 브랜드 | 판정 | 비고 |
|---|---|---|
| **컴포즈커피** | 🔴 **진짜 결함** | NEW 배지가 이미지 안에 있다. 200건 중 16건. docstring 이 "배지 없음" 으로 틀리게 적혀 있다 (§3-2) |
| **팔도·커피빈·미스터피자·설빙·홍루이젠·삼송빵집·파파존스·매머드·프랭크버거·죠스떡볶이·던킨** | 🔴 **진짜 결함** | 이미지 `Last-Modified` 를 안 받아서 낡은 배지가 영구히 올라와 있다. 합 126장 (§3-1) |
| **빽다방** | 🟠 개선 여지 | 날짜를 받을 수 있는데(`/2026/09/` 경로 + `Last-Modified` 전건) 안 받는다. 지금 피해는 1장 |
| **스시로** | ✅ 브랜드의 사실 | `/pm` 이 '이달의 한정메뉴' 전용. 대조군 0. docstring 에 ⚠️ 유보까지 적혀 있다 |
| **CU** | ✅ 브랜드의 사실 | 원본 1,200건 중 667건만 NEW |
| **hy프레딧** | ✅ 브랜드의 사실 | '신제품' 탭만 받는다. 약 3개월 롤링 |
| **김밥천국** | ✅ 브랜드의 사실 | `/31` 이 8년치 아카이브. ⚠️ docstring 의 "STALE 로 걸러진다" 는 **틀린 설명** |
| **버거킹** | 🟠 문서 결함 | 어댑터가 NEW 없는 건 버린다(`:82`). docstring 에 안 적혀 있다 |
| **나폴레옹** | ✅ 브랜드의 사실 | `day8until_newarrival` 전건 만료. 사이트 자체 신상품 필터도 0건 |
| **바르다김선생** | ✅ 브랜드의 사실 | NEW 태그 4건의 썸네일이 2023-11 |
| **본우리반상 · 본흑염소 · 요거프레소** | ✅ 브랜드의 사실 / 🟠 문서 미비 | 각각 7월·작년 12월·7월이 마지막 신메뉴. **docstring 에 "그래서 지금 0장" 이 없다** |
| **명랑핫도그** | ✅ 브랜드의 사실 | 5월이 마지막. FLOOR_MIN 미만이라 급감 가드도 꺼져 있다 |
| **세븐일레븐** | ✅ 사실 | 날짜 0% 지만 `Last-Modified` 가 2014년 값이라 못 쓴다. 지금 올라온 11건은 전부 창 안 |
| **에그드랍** | 🟠 | 이미지 자체가 없다(인증서 만료, §1-9). 날짜도 없다 |
| **이마트24** | 🟠 간헐 실패 | §3-7 |
| **샐러디** | ✅ | NEW 3건 전부 창 안 |

---

## §1 재측정 — 18:18 커밋 `7ad0d1e` 반영 후 (측정 18:24 KST)

`docs/index.html` mtime 18:18:39, md5 `76df0c9c5e64bbdf9ed73d631307405b`, 777,163 bytes, 카드 **1,051장**.

| 항목 | 상태 |
|---|---|
| §1-6 `이천햅쌀 비락식혜` 중복 카드 | ✅ **해소** (동일 제목 중복 0건) |
| §1-7 `것플렉스 … x 5개` | ✅ **해소** (`것플렉스 두부흑임자스낵`) |
| §1-4 세트/콤보 | 🟠 35 → **31장**. 미스터피자 `(포장)` 2장·맘스터치 `(순살)` 1장이 묶였다. **BBQ 황올 세트 3종, 맘스터치 싱글피자N세트 2종, 맥도날드 세트 3종, 파파존스 콤보, hy프레딧 선물세트 6종은 그대로** |
| §1-1 파리바게뜨 상시품목 | 🔴 **9장 그대로** (`단팥빵`·`NO.1 우유식빵`·`모카크림빵`·`양송이 스프`·`정통 파운드케익`·`꽈배기도넛`·`멕시칸 핫도그`·`모짜렐라 치즈봉`·`우유가좋은뽀로로케익`) |
| §1-3 설빙 14장 | 🔴 **그대로** (`인절미설빙` 포함) |
| §1-8 잘린 이름 | 🔴 **그대로** (`청년떡집 프리미엄 크림떡 2종 세트 티라미슈, 톡톡 옥`) |
| §1-9 빈 네모 5장 | 🔴 **그대로** |
| §1-2 날짜 없는 카드 | 🔴 222장 (1,051 중 21%) |

### 🔴 1-14 **새로 생긴 깨짐** — §1-7 고치면서 괄호 **안**을 건드렸다

```
화면:  파오리 락토프리 포션버터 (12.5g ) x 2팩
원본:  [택배배송] 파오리 락토프리 포션버터 (12.5g x 10개) x 2팩
```
3장(`락토프리`·`그란본따 무염`·`가염` 포션버터).

새로 들어온 `_ORPHAN_MULT`(`collectors/base.py:433`)가 **`_sub_outside_parens()` 를 안 거치고
문자열 전체에 걸린다**:
```python
s = _sub_outside_parens(_MULT, s)     # 괄호 밖만
s = _sub_outside_parens(_SPEC, s)     # 괄호 밖만
s = _ORPHAN_MULT.sub(" ", s)          # ← 괄호 안까지 (새로 추가된 줄)
```
`_sub_outside_parens` 의 docstring 이 바로 이 사고를 적어 두고 있다:
> 괄호 안에서 용량만 빼면 껍데기가 남아 더 흉해진다 — hy프레딧
> `…도라지 캔디(1.2g x 50정) 2통` 이 `…캔디( x 50정) 2통` 이 됐었다.

**고치려면** `s = _sub_outside_parens(_ORPHAN_MULT, s)` 로 바꾸면 된다.
재현:
```
python3 -c "
import sys;sys.path.insert(0,'.')
from collectors.base import display_name
print(display_name('[택배배송] 파오리 락토프리 포션버터 (12.5g x 10개) x 2팩'))"
```
→ `파오리 락토프리 포션버터 (12.5g ) x 2팩`
