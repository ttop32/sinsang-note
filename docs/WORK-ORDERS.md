# 작업지시서 — FEATURE-PLAN-2 P0 · P1

작성 2026-10-01 · 근거 `docs/FEATURE-PLAN-2.md` · 기준 빌드 라이브 `10:59 · 300장 / 483건` · 데이터 `06:01 · 6,450건`

이 문서는 **다음 작업자가 질문 없이 착수할 수 있는 단위**로 쪼갠 것이다.
기능의 근거·대안 검토·반려 사유는 전부 `docs/FEATURE-PLAN-2.md` 에 있다. 여기서는 **무엇을 어떻게**만 적는다.

| 지시서 | 제목 | 우선 | 담당 역할 | 주 소유 파일 |
|---|---|---|---|---|
| **WO-1** | 홈 숫자를 그리는 수와 맞춘다 (483 → 300) | P0 | 웹 렌더 | `collect.py` |
| **WO-2** | 주류 제외 — 접두 기반 `is_alcohol()` | P0 | 수집 계약 | `collectors/base.py` |
| **WO-3** | 푸터 — 게시중단 창구 · "먹는 것만" · 분류/브랜드 링크 | P0 | 웹 렌더 | `collect.py` · `web/pages.py` |
| **WO-4** | 유튜브 리뷰 검색 링크 (상세 페이지) | P0 | 페이지 생성 | `web/youtube.py`(신규) · `web/pages.py` |
| **WO-5** | `/c/굿즈/` 비식품 전용 목록 | P1 | 페이지 생성 | `collect.py` · `web/pages.py` · `web/seo.py` |
| **WO-6** | 2단 칩 건수 내림차순 + 가로 스크롤 힌트 | P1 | 웹 렌더 | `collect.py` |
| **WO-7** | Atom 피드 타임스탬프·건수 + RSS 링크 | P1 | SEO·피드 | `web/seo.py` |
| **WO-8** | og:image 자체 생성 커버 | P1 | 자산 생성 | `web/assets.py` · `collect.py` |

### 🟢 2026-10-01 중간 실측 — 착수 전에 반드시 보라

이 문서를 쓰는 동안 **세 건이 이미 머지됐다.** 다시 구현하지 마라.
아래는 작업트리·`docs/` 산출물을 직접 대고 잰 것이다.

| 지시서 | 상태 | 실측 |
|---|---|---|
| **WO-2** 주류 | 🟢 **머지됨 — 검증만 하면 된다** | `collectors/base.py:213-262` 에 `ALCOHOL_CATEGORIES`/`ALCOHOL_PREFIXES`/`ALCOHOL_WORDS`/`NONALCOHOL_MARKS`/`is_alcohol()` 전부 있음. `collect.is_fresh()` 에서 차단. PM 이 202건 전수를 눈으로 훑어 **식품 오탐 0** 확인 |
| **WO-5** 굿즈 | 🟢 **머지됨 — 검증만** | `is_fresh(..., goods=True)` + `collect.pick()` + `pages.build(..., goods=)`. **`docs/c/굿즈/index.html` 에 카드 65장** — 내가 예측한 65 와 정확히 일치 |
| 고아 상세 페이지 정리 | 🟢 **머지됨** | `web/pages.py:374-387` 에 "생성 결과 바깥을 턴다" 프루너. 실측 **disk 548 = sitemap 548, 고아 0** |
| **WO-1** 숫자 | 🔴 미착수 | 푸터·리드 **483** vs 카드 **300** 그대로 |
| **WO-3** 푸터 | 🟡 절반 | `theme.CONTACT`/`NOTICE` 머지·게시중단 링크 1개·**`/c/` 링크 16개 있음.** 남은 것 = **`/b/` 브랜드 링크 0개 · RSS 링크 없음** |
| **WO-4** 유튜브 | 🔴 미착수 | 상세 548장 중 유튜브 링크 **0장** |
| **WO-6** 칩 | 🔴 미착수 | 2단 여전히 선언순(`라면41 햄버거3 피자12 치킨4 베이커리26 디저트6 분식1 일식40 샌드위치4 샐러드3`) |
| **WO-7** 피드 | 🔴 미착수 | `<entry>` 50 · `<published>` **0** |
| **WO-8** og | 🔴 미착수 | og:image 아직 파리바게뜨 CDN · `docs/og.png` 없음 |

🔴 **머지된 `is_alcohol()` 이 내 F6 초안보다 낫다.** 내가 못 본 축이 둘 있다 —
`NONALCOHOL_MARKS`(무알콜/논알콜/0.0 이면 '맥주'가 들어가도 술이 아니다)와
**포도품종 단어**(`까베르네`·`쇼비뇽`·`샤르도네`·`피노누아`…). 와인은 이름에 `와인` 이
안 들어가는 게 보통이라 품종으로 잡아야 한다는 지적이 맞다.
**FEATURE-PLAN-2 §3 F6 의 접두 표는 설계 근거로만 읽고, 코드는 머지된 쪽을 정본으로 삼아라.**

🟢 **고아 페이지 정리(PM B-06)는 WO-5 에 붙일 필요가 없어졌다.** 프루너가 이미 들어갔고
고아 0 을 확인했다. **대신 그 프루너가 계속 도는지를 WO-5 완료 기준 6번으로 검사해라**
(아래 WO-5 §완료 판정 6번을 "`docs/p` 디렉터리 수 == sitemap 의 `/p/` 수"로 읽어라).
BUG-REPORT C-2(세트 잔여 35장)·PRODUCT-PLAN S14 도 같은 결함이었고 이걸로 함께 닫힌다.

---

## 0. 전 지시서 공통 — 반드시 지킬 것

### 0-1. 🔴 선행조건 (전건 공통)

**PM 이 `docs/BACKLOG.md` B-01 / W0 으로 잡은 "작업트리 ↔ HEAD 분기 해소"가
이 문서의 모든 지시서보다 먼저다.** PM 실측 — HEAD 는 브랜드 46곳, 작업트리는 56곳,
`NONFOOD_WORDS`(비식품 분리) 자체가 HEAD 에 없고 어댑터 10개가 untracked 다.

이 문서의 모든 측정값은 **작업트리 기준**이다. HEAD 기준으로 보면 숫자가 다르다.
**W0 이 끝나기 전에 착수하면 머지 충돌이 아니라 "없는 코드를 고치는" 상황이 된다.**

### 0-2. 🔴 여러 줄 블록은 통째로 다시 써라

이 프로젝트는 **같은 증상으로 사이트가 두 번 죽었다.**
한 번은 CSS(`.c{display:flex}` 가 `[hidden]` 을 덮음), 한 번은 JS(`subnav`·`subBtns`·`syncSub` 미선언).
두 번 다 **여러 줄 블록에 부분 문자열 치환**을 한 결과다.

- `collect.py` 의 `CSS_EXTRA`, `render()` 안의 f-string HTML, `<script>` 블록
- `web/theme.py` 의 `CSS`, `head()` 반환 문자열
- `web/pages.py` 의 `EXTRA_CSS`, `_shell()`

→ **이 블록 안을 고칠 때는 블록 전체를 읽고 전체를 새로 써라.** `sed`·부분 `replace` 금지.

### 0-3. 🔴 한국어 단어 추가는 전수 검증 후에

한국어는 단어 경계가 없다. 과거 비식품 목록에 `핸디` 를 넣어 스타벅스 **`핸디 젤리`(식품)** 가 지워졌다.
이번 조사에서도 `카스`(→카스테라 54건), `막걸리`(→막걸리향 콜드브루 2건, 둘 다 식품),
`스위트)`(→`스위트)키캡모양젤리` 등 5건)가 같은 함정이었다.

→ **새 단어·접두를 넣기 전에 `data/products.json` 6,450건 전체에 대고 돌려
식품 오탐 0 을 세고, 그 출력을 완료 보고에 붙여라.**

### 0-4. 🟢 완료 전 반드시 돌릴 스모크 검사 (전건 공통)

빌드한 `docs/index.html` 에 대고 아래를 돌려 **전부 `OK`** 가 나와야 끝이다.
"탭·검색·정렬이 통째로 죽은" 사고를 잡는 최소한의 그물이다.

```bash
cd /Users/swkim72/source/sinsang-note && ./.venv/bin/python - <<'EOF'
import re, pathlib, sys
h = pathlib.Path('docs/index.html').read_text(encoding='utf-8')
fail = []
cards = re.findall(r'<a class="c"', h)
tabs  = dict((m[1], int(m[2])) for m in re.findall(r'data-f="([^"]*)"[^>]*>([^<]*)<span class="n">(\d+)', h))
subs  = [(m[0], int(m[1])) for m in re.findall(r'data-s="([^"]*)"[^>]*aria-pressed="false">[^<]*<span class="n">(\d+)', h)]
dp    = re.findall(r'<a class="c" data-p="([^"]*)"', h)
# 1 탭 숫자 = 실제 카드 수
import collections
c = collections.Counter(dp)
for label, n in tabs.items():
    want = len(cards) if label == '전체' else c.get(label, 0)
    if n != want: fail.append(f'탭 {label} 숫자 {n} != 카드 {want}')
# 2 푸터·리드 숫자 = 그린 카드 수
for m in re.findall(r'최근 \d+일 신제품 ([\d,]+)건', h):
    if int(m.replace(',','')) != len(cards): fail.append(f'푸터/리드 {m}건 != 카드 {len(cards)}장')
# 3 JS 가 참조하는 DOM id 가 전부 있는지
for i in ['g','q','cnt','sort','subnav','noresult']:
    if f'id="{i}"' not in h: fail.append(f'id={i} 없음')
# 4 JS 가 쓰는 전역이 선언돼 있는지 (2차 사고 재발 방지)
for v in ['subnav','subBtns','syncSub','priBtns','apply']:
    if f'{v} =' not in h and f'function {v}' not in h: fail.append(f'JS 심볼 {v} 미선언')
# 5 카드 hidden 이 CSS 로 먹는지 (1차 사고 재발 방지)
if '.c[hidden]{display:none}' not in h: fail.append('.c[hidden] 규칙 없음')
# 6 head 필수 태그
for t in ['rel="canonical"','property="og:image"','rel="manifest"','type="application/atom+xml"']:
    if t not in h: fail.append(f'head {t} 없음')
print('카드', len(cards), '| 탭', tabs, '| 2단', subs)
print('FAIL' if fail else 'OK'); [print(' -', f) for f in fail]
sys.exit(1 if fail else 0)
EOF
```

**그리고 브라우저로 라이브(또는 로컬 `docs/index.html`)를 열어 손으로 셋을 확인한다.**
자동 검사가 DOM 이벤트까지는 못 본다.

1. 1단 탭 하나를 눌러 **카드 수가 실제로 줄어드는가** (칩 숫자와 같은가)
2. 검색창에 `라떼` 를 넣어 **카드가 줄어드는가**
3. `최신순` 을 눌러 **`브랜드순` 으로 바뀌고 순서가 바뀌는가**

### 0-5. 파일 충돌 표 — 병렬 배정 전에 읽어라

`collect.py` 가 병목이다. **WO-1 · WO-3 · WO-5 · WO-6 · WO-8 이 전부 `collect.py` 를 건드리고,
그중 WO-1 · WO-3 · WO-6 은 `render()` 함수 **같은 영역**(f-string HTML / `CSS_EXTRA`)을 만진다.

| | `collect.py` | `collectors/base.py` | `web/pages.py` | `web/seo.py` | `web/assets.py` | `web/youtube.py` |
|---|---|---|---|---|---|---|
| WO-1 | 🔴 `render()` f-string | | | | | |
| WO-2 | 🟡 `is_fresh()` 1줄 | 🔴 단독 | | | | |
| WO-3 | 🔴 `render()` f-string | | 🟡 `_shell()` | | | |
| WO-4 | | | 🟡 `product_page()` | | | 🔴 신규 단독 |
| WO-5 | 🟡 `main()` | | 🟡 신규 함수 | 🟡 `build()` 인자 | | |
| WO-6 | 🔴 `CSS_EXTRA` + `render()` | | | | | |
| WO-7 | | | | 🔴 단독 | | |
| WO-8 | 🟡 `render()` 1줄 | | | | 🔴 단독 | |

🔴 = 주 소유(그 작업자만 만진다) · 🟡 = 작은 수정(충돌 가능)

**권고 배정**

| 트랙 | 지시서 | 비고 |
|---|---|---|
| **트랙 A (직렬 1명)** | WO-1 → WO-3 → WO-6 | 셋 다 `collect.py:render()` 를 통째로 다시 쓴다. **나눠 주면 반드시 충돌한다** |
| **트랙 B (병렬)** | WO-2 | `collectors/base.py` 단독. `collect.py` 는 `is_fresh()` 에 **1줄 추가**뿐이라 트랙 A 와 조율만 하면 된다 |
| **트랙 C (병렬)** | WO-4 | `web/youtube.py` 신규 + `web/pages.py:product_page()`. 트랙 A 와 안 겹친다 |
| **트랙 D (병렬)** | WO-7 | `web/seo.py` 단독 |
| **트랙 E (병렬)** | WO-8 | `web/assets.py` 단독 + `collect.py` 1줄 (트랙 A 가 끝난 뒤 얹는다) |
| **트랙 F (A·C·D 뒤)** | WO-5 | `collect.py`·`pages.py`·`seo.py` 셋을 다 건드린다. **마지막에 혼자 돌린다** |

---

## WO-1 — 홈 숫자를 그리는 수와 맞춘다 (483 → 300)

| | |
|---|---|
| **우선순위** | **P0** |
| **담당 역할** | 웹 렌더 (`.claude/agents/` 에 해당 역할 없음 — 메인 세션 또는 범용 에이전트) |
| **선행조건** | §0-1 (W0) |
| **근거** | FEATURE-PLAN-2 §1-2 ① · §3 F8 |

### 손댈 파일

- `/Users/swkim72/source/sinsang-note/collect.py` — `render()` 함수 **전체** (현재 약 455~560행)

### 지금 상태 (실측)

푸터·리드가 `최근 60일 신제품 483건` 이라 쓰는데 화면에는 `.c` 카드 **300장**뿐이다.
`SHOW = 300` 이 자르고, 푸터·리드는 `len(rows)` 를 쓴다. **183장(38%)이 숫자에만 있다.**

### 변경 내용

1. `render()` 의 `lead` 와 `<footer>` 에서 `len(rows)` → **`len(shown)`** 으로.
2. `new_today` 도 `shown` 기준으로 다시 센다. 지금은 `main()` 에서 `fresh`(483) 기준으로 계산해
   `render()` 로 넘어온다. `render()` 안에서 `[r for r in new_today if r in shown]` 상당의
   재계산을 하거나, `main()` 에서 자르는 순서를 바꾼다. **어느 쪽이든 리드의 "오늘 N건"이
   화면의 오늘자 카드 수와 같아야 한다.**
3. 잘린 분량을 숨기지 말고 **푸터에 한 줄로 밝힌다.**
   `최근 60일 신제품 483건 중 최신 300건` 형태. 문구는 WO-3 과 합의한 푸터 전체 문안을 따른다.
   (WO-1 → WO-3 순서라면 WO-1 은 숫자만 맞추고 문구는 WO-3 이 완성한다.)

🔴 `render()` 안의 `doc = f"""…"""` 는 100줄짜리 여러 줄 f-string 이다.
**`<footer>` 줄만 치환하지 말고 §0-2 대로 블록을 통째로 다시 써라.**

### 완료 판정 기준

```bash
cd /Users/swkim72/source/sinsang-note && ./.venv/bin/python collect.py
```
(네트워크가 막혀 수집이 실패하면 `data/products.json` 을 그대로 쓰는 경로로 렌더만 돌려라.)

1. **§0-4 스모크 검사가 `OK`.** 특히 `푸터/리드 N건 != 카드 M장` 항목이 안 떠야 한다.
2. 아래가 전부 같은 수여야 한다.
   ```bash
   grep -o 'class="c"' docs/index.html | wc -l          # 그린 카드
   grep -o '최근 60일 신제품 [0-9,]*건' docs/index.html   # 푸터·리드 (2회 등장, 둘 다 같아야)
   grep -o 'data-f=""[^>]*>전체<span class="n">[0-9]*' docs/index.html   # 전체 탭
   ```
3. 리드가 `오늘 N건` 일 때, `grep -c 'datetime="<오늘날짜>"' docs/index.html` 가 **N 과 같아야** 한다.
4. §0-4 의 손 확인 3종.

### 다른 지시서와 같은 파일을 건드리는가

🔴 **WO-3 · WO-6 과 `collect.py:render()` 를 공유한다.** 같은 사람이 WO-1 → WO-3 → WO-6 순으로
직렬 처리할 것(§0-5 트랙 A). WO-2 가 `is_fresh()` 에 1줄, WO-5 가 `main()` 에, WO-8 이 `render()` 에
1줄을 더하지만 영역이 다르다 — 그래도 **WO-1 머지 후에 얹어라.**

---

## WO-2 — 주류 제외 (접두 기반 `is_alcohol()`)

| | |
|---|---|
| **우선순위** | **P0** |
| **담당 역할** | 수집 계약 (`.claude/agents/adapter-reviewer.md` 의 리뷰 관점과 같은 영역) |
| **선행조건** | §0-1 (W0). `NONFOOD_WORDS` 가 HEAD 에 없으므로 **W0 전에는 붙일 자리 자체가 없다** |
| **근거** | FEATURE-PLAN-2 §3 F6 (실측표 포함) |

### 손댈 파일

- `/Users/swkim72/source/sinsang-note/collectors/base.py` — `NONFOOD_*` 블록 바로 아래 (현재 185~204행 주변)
- `/Users/swkim72/source/sinsang-note/collect.py` — `is_fresh()` 에 **1줄만** (현재 297~298행 바로 다음)

### 변경 내용

**① `collectors/base.py` 에 추가** — `NONFOOD_WORDS` 와 **같은 모양·같은 주석 톤**으로.
(`.claude/agents/adapter-builder.md` 가 요구하는 "주변 코드 스타일을 따른다" 그대로.)

```
ALCOHOL_PREFIXES = ("위스키)", "사케)", "칵테일)", "레드)", "화이트)", "스파클링)", "로제)")
ALCOHOL_WORDS    = ("맥주", "소주", "와인", "하이볼", "막걸리", "라거", "에일", "위스키")
# 🔴 단, 뒤에 '향'·'맛'·'풍미' 가 붙으면 주류가 아니라 '그 맛이 나는 식품'이다.
#    막걸리향 크림 콜드 브루 · 서울 막걸리향 콜드 브루 (스타벅스, 둘 다 식품)
#    → `막걸리(?!향|맛|풍미)` 처럼 뒤를 보고 거른다. 단어를 빼지 말고 예외를 달아라.
#      (GS25 보도자료에 햇반백미막걸리·햇반흑미막걸리 같은 진짜 주류가 있다)
# ⛔ 넣으면 안 되는 것 (전체 6,450건 실측)
#   스위트)  → 스위트)키캡모양젤리·스위트)토이스토리히퍼·스위트)메가팝토이스토리 (CU 과자류 5건)
#   카스     → 삼각카스테라·키키카스테라 (54건 중 대부분)
#   테라     → 카스테라·프론테라
#   막걸리   → 막걸리향 크림 콜드 브루 · 서울 막걸리향 콜드 브루 (2건 전부 식품)
#   청주     → 오뚜기)청주식돼지김치짜글이450G
#   기린     → 기린오후의차밀크티 · 기린효케츠레몬
#   클라우드 → 미니저그 (클라우드크림)
#   750ml   → 용량일 뿐. 식품에도 붙는다
```

🔴 위 `ALCOHOL_WORDS` 안의 `막걸리` 는 **금지 목록에도 있다.** 실측에서 적중 2건이
**둘 다 `막걸리향 콜드 브루`(식품)** 였다. **단어로는 넣지 마라.** 위 블록은 초안이고,
실제 목록은 아래 ③ 검증을 돌린 결과로 확정한다.

**② `is_alcohol(name, category) -> bool`** — `is_nonfood()` 바로 아래, 같은 모양.

🔴 **`category` 가 비어 있어도 동작해야 한다.** GS25 처럼 보도자료에서 이름만 뽑는 소스는
`category` 가 항상 빈 문자열이다(GS25 작업자 실측). **분류 축에만 의존하면 통째로 샌다.**

🔴 **`Item` 에 `alcohol: bool = False` 필드를 추가하고 `to_dict()` 에서 OR 로 합친다** —
`nonfood` 와 **똑같은 모양**이다.

```python
d["nonfood"] = self.nonfood or is_nonfood(self.name, self.category)
d["alcohol"] = self.alcohol or is_alcohol(self.name, self.category)
```

이유: 이름만으로는 판정이 불가능한 소스가 실제로 있다. GS25 보도자료의 **`한영석 청명주`**(전통 약주)는
`하이볼`·`라거`·`소주`·`막걸리`·`청주`·`사케` 어느 단어에도 안 걸린다(작업자 실측).
그런데 **기사 본문에는 도수가 적혀 있다.** 그건 그 어댑터만 볼 수 있는 정보다.
→ **원칙은 "base 가 이름으로 판정한다"이고, 어댑터는 자기만 아는 근거가 있을 때만 `alcohol=True` 로 덮는다.**
`청명주` 같은 단어를 `ALCOHOL_WORDS` 에 넣지 마라 — `명주`·`청주` 오탐이 따라온다
(`오뚜기)청주식돼지김치짜글이450G`).

🟠 **단어 기반 게이트의 구조적 한계를 기록해 둔다.** 전통주·수제맥주 신제품처럼
**이름에 주종이 안 들어가는 주류**는 이름만으로 못 잡는다. 받아들이고, 위 override 로 보완한다.

🔴 **`nonfood` 와 합치지 마라.** 굿즈는 WO-5 의 `/c/굿즈/` 에서 보여주고 **주류는 어디에도 안 보여준다.**
같은 플래그로 묶으면 굿즈 페이지에 와인이 올라간다.

**③ `collect.is_fresh()` 에 1줄** — `nonfood` 검사 **바로 다음**.

```python
if r.get("nonfood"):
    return False
if r.get("alcohol"):
    return False      # 주류. 연령 확인 없이 1면에 노출할 수 없다
```

**④ 무알콜 맥주 2건** (`병맥주(카스0.0 논알콜)` · `병맥주(카스레몬스퀴즈0.0)`) 도 **같이 뺀다.**
`맥주` 단어에 자연히 걸린다.

### 완료 판정 기준

**1. 전수 오탐 검증 — 출력을 완료 보고에 붙여라.**

```bash
cd /Users/swkim72/source/sinsang-note && ./.venv/bin/python - <<'EOF'
import json, sys; sys.path.insert(0,'.')
from collectors.base import is_alcohol
d = json.load(open('data/products.json'))['products']
hit = [r for r in d if is_alcohol(r['name'], r.get('category',''))]
print('적중', len(hit))
for r in hit: print(' ', r['brand'], '|', r['name'])
EOF
```
→ 출력된 전건이 **주류여야 한다. 식품이 한 건이라도 섞이면 미완료다.**
(전체 적중은 **150건 안팎**이 예상치다. 크게 벗어나면 규칙을 다시 봐라.)

**2. 현재 창에서 2건이 사라져야 한다.**

```bash
grep -c 'ml캔(6입)\|옐로우테일' docs/index.html      # 렌더 후 0 이어야 함
```
구체적으로 `롯데)옐로우테일오로라팩(까버)`(와인)·`롯데)클라우드468ml캔(6입)`(맥주).

**3. 식품이 줄지 않았는지.** 렌더 전후 `fresh` 건수 차이가 **정확히 주류 건수만큼**이어야 한다.
483 → 481 (±0). 더 줄었으면 오탐이다.

**4. 굿즈가 영향받지 않았는지.** `nonfood=True` 건수가 **178 그대로**여야 한다.

**5. §0-4 스모크 검사 `OK`.**

### 다른 지시서와 같은 파일을 건드리는가

🟡 `collect.py:is_fresh()` 1줄 — **WO-1/3/6 이 만지는 `render()` 와는 다른 함수**라 충돌 위험은 낮지만
같은 파일이다. **트랙 A 와 머지 순서를 맞춰라.**
🟢 `collectors/base.py` 는 WO-2 단독 소유.
⚠️ WO-5(굿즈 페이지)가 `alcohol` 플래그를 쓴다 — **WO-2 가 먼저다.**

---

## WO-3 — 푸터 (게시중단 창구 · "먹는 것만" · 분류/브랜드 링크)

| | |
|---|---|
| **우선순위** | **P0** |
| **담당 역할** | 웹 렌더 |
| **선행조건** | §0-1 (W0) · **WO-1**(같은 f-string) · 굿즈 링크는 **WO-5** 가 먼저여야 404 가 안 난다 |
| **근거** | FEATURE-PLAN-2 §1-2 ⑦ · §3 F3 · §3 F8 |

### ⚠️ 2026-10-01 작업 중 선반영된 부분 — 중복 작업하지 마라

이 지시서를 쓰는 동안 다른 작업자가 `web/theme.py` 에 **공용 상수 2개를 이미 넣었다.**

```python
CONTACT = "https://github.com/ttop32/sinsang-note/issues"
NOTICE  = ("먹는 것만 모읍니다 — 굿즈와 주류는 목록에서 뺍니다.<br>"
           "상품 정보와 이미지의 저작권은 각 브랜드에 있습니다. "
           f'브랜드 관계자께서 <a href="{CONTACT}" rel="nofollow">게시 중단을 요청</a>하시면 '
           "확인 후 바로 내리겠습니다.")
```

**이 위치가 내가 지정했던 것보다 낫다** — 푸터 문안이 세 곳에 복붙돼 있던 걸 정본 한 곳으로 모았다.
**`theme.NOTICE` / `theme.CONTACT` 를 쓰고, 문구를 다시 짓지 마라.**

남은 일은 셋이다.

1. `collect.py:render()` 와 `web/pages.py:_shell()` 이 **실제로 `theme.NOTICE` 를 쓰고 있는지** 확인.
   아직 각자 하드코딩돼 있으면 거기를 `theme.NOTICE` 로 바꾼다.
2. **`NOTICE` 에 굿즈 페이지 링크가 없다.** `"굿즈와 주류는 목록에서 뺍니다"` 라고만 돼 있다.
   WO-5 가 끝난 뒤 `굿즈는 <a href=".../c/굿즈/">굿즈</a>에서 따로 봅니다` 로 보강한다.
   🟢 **주류는 링크를 걸지 않는다** — 어디에도 안 보여준다(WO-2).
3. **분류·브랜드·RSS 링크는 아직 없다.** 아래가 그 작업이다.

### 손댈 파일

- `/Users/swkim72/source/sinsang-note/web/theme.py` — `NOTICE` 보강(위 2번). 🔴 **문구 정본은 여기 하나다**
- `/Users/swkim72/source/sinsang-note/collect.py` — `render()` 의 `<footer>` 블록 (홈 전용 링크 줄)
- `/Users/swkim72/source/sinsang-note/web/pages.py` — `_shell()` **133~134행** (`/p/`·`/b/`·`/c/`·404 공용)

🔴 **푸터 렌더가 두 곳에 각각 있다. 둘 다 `theme.NOTICE` 를 쓰게 하지 않으면 또 갈라진다.**

### 지금 상태 (실측, 홈)

```
마지막 갱신 2026-10-01 10:59 · 최근 60일 신제품 483건
상품 정보와 이미지의 저작권은 각 브랜드에 있습니다.
```

### 변경 내용 — 홈 푸터를 4줄로

```
신상노트 · 편의점·카페·프랜차이즈 신제품 모아보기
먹는 것만 모읍니다. 텀블러·굿즈는 [굿즈]에서 따로 봅니다.
상품 정보와 이미지의 저작권은 각 브랜드에 있습니다. 게시중단을 원하시면 [여기]로 알려주세요.
분류 전체 보기 · 브랜드 전체 보기 · RSS
마지막 갱신 2026-10-01 10:59 · 최근 60일 신제품 483건 중 최신 300건
```

| 링크 | 목적지 | 비고 |
|---|---|---|
| `[굿즈]` | `/sinsang-note/c/굿즈/` | **WO-5 선행.** 아직이면 이 줄 전체를 보류하고 나머지만 넣어라 |
| `[여기]` | `https://github.com/ttop32/sinsang-note/issues/new?labels=takedown&title=게시중단+요청` | 🔴 **메일 주소를 평문으로 박지 마라** (스팸 수집기) |
| `분류 전체 보기` | `/sinsang-note/c/편의점/` 등 15종 — 한 줄에 `·` 로 나열 | FEATURE-PLAN-2 §3 F8(c). **현재 홈에서 `/c/`·`/b/` 로 가는 링크가 0개다** |
| `브랜드 전체 보기` | `/sinsang-note/b/<브랜드>/` 나열 또는 상위 N + 더보기 | 브랜드 50곳이라 전부 나열하면 길다. **상위 12개 + `/c/` 로 유도**를 권한다 |
| `RSS` | `/sinsang-note/feed.xml` | 🔴 **WO-7 이 끝난 뒤에 노출해라.** 지금 노출하면 상위 50건이 전부 같은 타임스탬프인 피드를 구독시킨다 |

### `web/pages.py:_shell()` 쪽

공용 푸터는 짧게 유지한다. 홈 전체 목록을 상세·브랜드·유형 페이지 모두에 깔면 무겁다.

```
신상노트 · 편의점·카페·프랜차이즈 신제품 모아보기
상품 정보와 이미지의 저작권은 각 브랜드에 있습니다. 게시중단 요청
```

**"게시중단 요청" 링크는 모든 페이지에 있어야 한다** — 상품 상세에서 그 상품을 내려달라는 게
가장 흔한 요청이기 때문이다.

### 완료 판정 기준

1. **홈·상세·브랜드·유형·404 다섯 종류 전부**에 게시중단 링크가 있다.
   ```bash
   cd /Users/swkim72/source/sinsang-note
   for f in docs/index.html docs/404.html docs/c/편의점/index.html docs/b/스타벅스/index.html $(ls -d docs/p/*/ | head -1)index.html; do
     printf '%s: ' "$f"; grep -c 'issues/new' "$f"
   done
   ```
   → 전부 **1 이상**.
2. 홈에서 `/c/` 로 가는 링크가 **15개**, `/b/` 로 가는 링크가 **1개 이상**.
   ```bash
   grep -o 'href="/sinsang-note/c/[^"]*"' docs/index.html | sort -u | wc -l
   grep -o 'href="/sinsang-note/b/[^"]*"' docs/index.html | sort -u | wc -l
   ```
3. 푸터 링크 전부가 **실제로 존재하는 파일**을 가리킨다 (404 금지).
   ```bash
   ./.venv/bin/python - <<'EOF'
   import re,pathlib,urllib.parse
   h=pathlib.Path('docs/index.html').read_text(encoding='utf-8')
   bad=[]
   for u in set(re.findall(r'href="/sinsang-note/([^"]*)"',h)):
       p=pathlib.Path('docs')/urllib.parse.unquote(u)
       if p.suffix=='' : p=p/'index.html'
       if not p.exists(): bad.append(u)
   print('BROKEN',bad or 'none')
   EOF
   ```
   → `none`.
4. 브라우저로 **375px** 에서 홈 끝까지 내려 푸터가 가로로 넘치지 않는지 본다
   (분류 15개 나열이 가로 스크롤을 만들면 줄바꿈 처리).
5. §0-4 스모크 검사 `OK`.

### 다른 지시서와 같은 파일을 건드리는가

🔴 **WO-1 · WO-6 과 `collect.py:render()` 공유** (트랙 A 직렬).
🟡 **WO-4 와 `web/pages.py` 공유** — WO-4 는 `product_page()`, WO-3 은 `_shell()` 로 함수가 다르다.
   그래도 같은 파일이니 **머지 순서를 정해라** (WO-3 먼저 권장, `_shell()` 이 더 위에 있다).
🟡 **WO-5 선행**(굿즈 링크) · **WO-7 선행**(RSS 링크).

---

## WO-4 — 유튜브 리뷰 검색 링크 (상세 페이지)

| | |
|---|---|
| **우선순위** | **P0** — 운영자 지목 1순위 |
| **담당 역할** | 페이지 생성 |
| **선행조건** | §0-1 (W0). **PRODUCT-PLAN P0-3(상품명 정규화)이 있으면 그 결과를 쓴다. 없으면 이 지시서 안에서 최소 정규화를 자체 구현한다** |
| **근거** | FEATURE-PLAN-2 §2-2(검색 실측 3건) · §3 F1 |

### 범위 — 이것만 한다

> **상세 페이지(`/p/...`)에 유튜브 검색 링크 한 줄.
> 홈 카드에 넣지 않는다. YouTube Data API 를 쓰지 않는다. 임베드하지 않는다.**

🔴 **API·임베드로 확장하지 마라.** 사유는 FEATURE-PLAN-2 §3 F1-1·F1-4·F1-5 에 수치로 있다.
요약: 하루 `search.list` **100콜** 상한인데 창 안에 483건이 있고 하루 신규가 107건이던 날이 있었다.
그리고 홈 카드는 `<a class="c">` 가 카드 전체를 감싸서 **중첩 링크가 HTML 위반**이다.

### 손댈 파일

- `/Users/swkim72/source/sinsang-note/web/youtube.py` — **신규.** 공개 심볼은 **함수 2개만.**
  - `search_query(item: dict) -> str` — 검색어. 만들 수 없으면 빈 문자열
  - `search_url(item: dict) -> str` — 완성된 유튜브 검색 URL. 검색어가 없으면 빈 문자열
- `/Users/swkim72/source/sinsang-note/web/pages.py` — `product_page()` 안, `dl.f` 표 **아래**

### 변경 내용

**① `web/youtube.py`**

검색어 조립 규칙 (순서대로):

| 순서 | 규칙 | 예 |
|---|---|---|
| 1 | POS 접두 제거 — `^[^\s]{1,8}\)` | `CJ)얼티브프로틴초코250ml` → `얼티브프로틴초코250ml` |
| 2 | 대괄호 라벨 제거 — `^\[[^\]]+\]` | `[파란라벨]통곡물 호밀 깜빠뉴` → `통곡물 호밀 깜빠뉴` |
| 3 | 용량·규격 제거 — `\d+(ml|ML|g|G|L)\b`, `\(\d+입\)` | `뿌셔뿌셔불고기맛90g` → `뿌셔뿌셔불고기맛` |
| 4 | 사이즈·온도 코드 제거 — `\((R\|K\|S\|L\|HOT\|ICE[^)]*)\)` | `피치 아이스티 (R)` → `피치 아이스티` |
| 5 | 결과가 **3자 미만이면 빈 문자열** 반환 (링크를 안 단다) | |
| 6 | `f"{brand} {name}"` 로 합쳐 `urllib.parse.quote_plus` | |

🔴 **`신메뉴`·`신상`·`출시` 같은 말을 붙이지 마라.**
실측 — `메가커피 신메뉴` 검색 상위에 `[자막뉴스] "은퇴자금까지 부었는데" 날벼락...
잘 나가던 메가커피의 민낯 / YTN`(165만회)이 뜬다. 브랜드 평판 뉴스로 보내는 링크가 된다.

**날짜 게이트 — `search_url()` 에서 7일.**
`collect._when(item)` 이 오늘로부터 **7일 이내면 빈 문자열**을 돌려준다.
근거: 당일 출시 `파리바게트 크림치즈말랑` → **관련 영상 0건** (상위가 `프랑스 사람들을
혼란에 빠뜨린 바게트`). 1개월 된 `버거킹 몬스터 맥시멈` → **상위 6건 전부 정타**.
🟡 **일수는 상수 하나로 빼둬라** (`FRESH_DAYS = 7`). 운영하며 조정한다.
⚠️ `web/youtube.py` 가 `collect` 를 import 하면 순환 import 위험이 있다
(`collect` → `web.pages` → `web.youtube` → `collect`). **날짜는 인자로 받아라.**

**② `web/pages.py:product_page()`**

`dl.f` 표가 끝난 뒤, `h2.sec`("… 의 다른 신제품") **앞**에 한 줄.

```html
<p class="yt"><a href="{search_url}" target="_blank" rel="noopener nofollow">
🔎 유튜브에서 「{검색어}」 리뷰 찾기 →</a></p>
```

- `search_url` 이 빈 문자열이면 **이 블록을 통째로 출력하지 않는다.**
- **브랜드 링크가 먼저, 유튜브가 나중.** 이 서비스는 트래픽을 브랜드로 돌려주는 게 원칙이다.
- 🟢 **상세 페이지의 브랜드 링크 문구는 두 갈래다**(2026-10-01 결정, FEATURE-PLAN-2 §3 F1-3).
  상품별 URL 이 있으면 `브랜드에서 보기 →`, 브랜드 대표 URL 뿐이면 **`브랜드 메뉴판에서 보기 →`**.
  백필 작업자 실측으로 **62건은 브랜드 서버에 상품 주소가 아예 없다**(스시로 40·빽다방 11·메가 6·
  프랭크버거 3·할리스 1·파파존스 1). 영구히 그렇다. 없는 걸 있는 척하지 않는다.
  🔴 **판정은 `card()` 와 같은 조건을 쓴다 — `not url or url == base.site(brand)`.**
  새로 만들지 마라. 문자열 비교를 `base.site()` 호출로 해야 김밥천국처럼
  **대표 URL 에 해시만 붙은 딥링크**(`.../31#lg=…&slide=6` ≠ `.../31`)가
  "대표 URL 뿐"으로 오분류되지 않는다.
  ⚠️ 이 CTA 분기는 **WO-4 담당자가 같이 얹는다.** 백필 작업자는 `collect.py`·`web/` 접근 범위가
  없어 못 하고, 어차피 `product_page()` 라 WO-4 와 같은 함수다.
- 문구는 "리뷰 **보기**"가 아니라 "리뷰 **찾기**" — 영상이 있다고 약속하지 않는다.
- 검색어를 따옴표로 보여줘서 **무엇으로 검색하는지 먼저 알린다.**
- `.yt` 스타일은 `EXTRA_CSS` 에 한 규칙 추가. 🔴 §0-2 — `EXTRA_CSS` 블록 통째로 다시 쓰기.

**③ 브랜드 페이지(`/b/`)·유형 페이지(`/c/`)에는 넣지 않는다.** §2-2 의 `메가커피 신메뉴` 사례.

### 완료 판정 기준

**1. 검색어 조립 단위 확인 — 아래 6건이 그대로 나와야 한다.**

```bash
cd /Users/swkim72/source/sinsang-note && ./.venv/bin/python - <<'EOF'
import sys; sys.path.insert(0,'.')
from web.youtube import search_query
cases = [
  ({'brand':'버거킹','name':'몬스터 맥시멈'},            '버거킹 몬스터 맥시멈'),
  ({'brand':'세븐일레븐','name':'CJ)얼티브프로틴초코250ml'}, '세븐일레븐 얼티브프로틴초코'),
  ({'brand':'파리바게뜨','name':'[파란라벨]통곡물 호밀 깜빠뉴'}, '파리바게뜨 통곡물 호밀 깜빠뉴'),
  ({'brand':'던킨','name':'피치 아이스티 (R)'},          '던킨 피치 아이스티'),
  ({'brand':'오뚜기','name':'뿌셔뿌셔불고기맛90g'},       '오뚜기 뿌셔뿌셔불고기맛'),
  ({'brand':'CU','name':'면)2'},                        ''),      # 3자 미만 → 링크 없음
]
bad=0
for item, want in cases:
    got = search_query(item)
    ok = got == want
    bad += not ok
    print(('OK ' if ok else 'NG '), repr(item['name']), '->', repr(got), '' if ok else f'(기대 {want!r})')
print('FAIL' if bad else 'ALL OK')
EOF
```
→ `ALL OK`.

**2. 렌더 후 상세 페이지 실물 확인.**

```bash
./.venv/bin/python collect.py
grep -l 'youtube.com/results' docs/p/*/index.html | wc -l    # 링크가 붙은 상세 수
ls -d docs/p/*/ | wc -l                                      # 전체 상세 수
```
→ **0 < 붙은 수 < 전체 수.** 전건에 붙으면 날짜 게이트가 안 먹는 것이고,
0 이면 조립이 전부 실패한 것이다.

**3. 7일 이내 상품에 링크가 없는지.**
```bash
grep -L 'youtube.com/results' $(grep -rl '2026-10-01' docs/p/*/index.html | head -5)
```
→ 오늘자 상세 전부가 "링크 없음" 쪽에 나와야 한다.

**4. 🔴 브라우저로 직접 1건을 확인한다.** 링크가 붙은 상세를 열고 **실제로 눌러서**
유튜브 검색 결과에 **그 제품 영상이 나오는지** 본다. 안 나오면 날짜 게이트(7일)를 늘릴 근거다.

**5. 링크 속성.** `target="_blank"` + `rel="noopener nofollow"` 가 전부 붙어 있다.
```bash
grep -o '<a href="https://www.youtube.com/results[^>]*>' docs/p/*/index.html | head -3
```

**6. 순환 import 가 안 나는지.** `./.venv/bin/python -c "import collect"` 가 통과.

**7. §0-4 스모크 검사 `OK`** (홈은 안 바뀌어야 한다 — 바뀌었으면 범위를 넘은 것이다).

### 다른 지시서와 같은 파일을 건드리는가

🟢 `web/youtube.py` 는 WO-4 단독.
🟡 **WO-3 과 `web/pages.py` 공유** — WO-3 은 `_shell()`(133행), WO-4 는 `product_page()`(148~237행)
   + `EXTRA_CSS`. **함수는 다르지만 `EXTRA_CSS` 는 WO-4 만 만진다.**
🟡 **WO-5 도 `web/pages.py`** — WO-5 는 신규 함수 추가라 겹치지 않지만, **WO-5 를 마지막에** 돌린다.

---

## WO-5 — `/c/굿즈/` 비식품 전용 목록

| | |
|---|---|
| **우선순위** | **P1** |
| **담당 역할** | 페이지 생성 |
| **선행조건** | §0-1 (W0) · **WO-2**(`alcohol` 플래그로 주류를 굿즈에서도 뺀다) · **WO-1/3/6 머지 후**(`collect.py` 충돌 회피) |
| **근거** | FEATURE-PLAN-2 §3 F2 · PRODUCT-PLAN §7-9 |

### 🔴 건수를 먼저 바로잡는다

PRODUCT-PLAN §7-12 의 **178건은 전체 카탈로그 기준**이다. 화면에 올릴 건수가 아니다.

| 단계 | 건수 (2026-10-01 데이터 기준) |
|---|---:|
| `nonfood=True` 전체 | 178 |
| 60일 창 안 | 77 |
| `merge_variants` + `drop_sets` + `cap_per_brand` 후 | **65** |

브랜드: `CU 40 · 할리스 13 · 매머드커피 8 · 세븐일레븐 3 · 파파존스 1`
**완료 기준에 178 을 쓰지 마라. 그리고 이 숫자는 날마다 바뀐다.**

### 손댈 파일

- `/Users/swkim72/source/sinsang-note/collect.py` — `main()` (약 203~220행)
- `/Users/swkim72/source/sinsang-note/web/pages.py` — `goods_page()` 신규 + `build()` 시그니처
- `/Users/swkim72/source/sinsang-note/web/seo.py` — `build()` 가 받는 `page_paths` 에 합류

### 지금 상태 — 생성기를 그대로 못 쓴다

`collect.is_fresh()` 의 **첫 줄**이 `if r.get("nonfood"): return False` 다.
즉 **굿즈는 `fresh` 에 절대 안 들어가고**, `pages.build(fresh, ...)` 는 `fresh` 만 돈다.
`/c/굿즈/` 는 저절로 생기지 않는다.

### 변경 내용

**① `collect.main()`** — `fresh` 와 **나란히** `goods` 를 만든다.

```python
fresh = [r for r in rows if is_fresh(r, today)]
...
goods = [r for r in rows if r.get("nonfood") and not r.get("alcohol")
                         and is_fresh({**r, "nonfood": False}, today)]
goods.sort(key=lambda r: (_when(r), r["brand"]), reverse=True)
goods = cap_per_brand(drop_sets(merge_variants(goods)))
```

🔴 **`fresh` 와 똑같은 가공 3종을 반드시 적용해라.** 안 하면 할리스 텀블러 색상 변형이
페이지를 덮는다 (PRODUCT-PLAN §7-9 ②).
🔴 **`alcohol` 은 굿즈에서도 뺀다** (WO-2 선행 이유).

**② `web/pages.py:goods_page(rows, brands, today)`** — `kind_page()` 와 거의 같다.

- `_list_page()` 를 재사용. 경로는 `theme.kind_path("굿즈")` = `c/굿즈/`
- `title` = `굿즈 신상 — 2026년 10월 | 신상노트`, `h1` = `굿즈 신상`
- 리드 밑 한 줄: `먹는 것이 아니라 메인 목록에서는 빼고 여기 모읍니다.`
- 브랜드 링크 줄(`kind_page()` 의 `</header>` 치환)도 그대로

🔴 **카드가 `/p/` 로 가면 안 된다.** 굿즈 65건의 상세를 만들면
`"할리스 더 가벼운 텀블러 — 신제품"` 같은 비식품 페이지가 색인된다
(PRODUCT-PLAN S14 세트 잔여 페이지와 같은 사고).
→ `goods_page` 의 카드는 **브랜드 상품 URL(외부)로 직접** 나가게 한다.
   `_card()` 가 `/p/` 를 박고 있으면 **굿즈용 카드 함수를 따로 만들거나 `_card()` 에 플래그를 넘겨라.**

**③ `web/seo.py`** — 반환 경로를 `page_paths` 에 합쳐 **사이트맵에 넣는다.**
🔴 **`feed.xml` 에는 넣지 마라.** 먹는 것만 모으는 피드다.

**④ 1단·2단 칩에는 넣지 않는다.** PRODUCT-PLAN §7-9 ① 결론 유지.
진입은 **푸터 링크(WO-3)뿐**이다.

### 완료 판정 기준

1. **파일이 생기고 건수가 맞는다.**
   ```bash
   cd /Users/swkim72/source/sinsang-note && ./.venv/bin/python collect.py
   test -f docs/c/굿즈/index.html && echo EXISTS
   grep -o 'class="c"' docs/c/굿즈/index.html | wc -l       # 60 ~ 70 사이 (오늘 기준 65)
   ```
   🔴 **정확히 65 를 요구하지 마라.** 날마다 바뀐다. **60~70 범위 밖이면 가공 3종을 의심해라.**
2. **브랜드 구성이 맞는다.** CU · 할리스 · 매머드커피 · 세븐일레븐 · 파파존스 가 나오고
   **그 밖의 브랜드가 없다.**
3. **식품이 섞여 있지 않다.** 🔴 **65장을 눈으로 훑어라.** 13장짜리 할리스 텀블러가
   색상 변형으로 중복돼 있지 않은지도 같이 본다. (이번 조사에서 사람이 훑어 오탐 2건을 찾았다.)
   ```bash
   grep -o '<h2>[^<]*</h2>' docs/c/굿즈/index.html
   ```
4. **주류가 없다.** `grep -c '옐로우테일\|클라우드468' docs/c/굿즈/index.html` → `0`.
5. **카드가 외부로 나간다.** `/p/` 링크가 0개.
   ```bash
   grep -c 'href="/sinsang-note/p/' docs/c/굿즈/index.html   # 0
   ```
6. **굿즈 상세 페이지가 안 생겼다.** `ls -d docs/p/*/ | wc -l` 이 WO-5 전후로 **같아야** 한다.
7. **사이트맵에 있고 피드에 없다.**
   ```bash
   grep -c '굿즈' docs/sitemap.xml    # 1 이상
   grep -c '굿즈' docs/feed.xml       # 0
   ```
8. **메인 피드 건수가 안 변했다.** 홈 카드 수가 WO-5 전후로 같다.
9. §0-4 스모크 검사 `OK`.

### 다른 지시서와 같은 파일을 건드리는가

🔴 **`collect.py`(main) · `web/pages.py` · `web/seo.py` 셋 다 건드린다.
WO-1 · WO-3 · WO-4 · WO-6 · WO-7 이 전부 끝난 뒤 혼자 돌려라** (§0-5 트랙 F).
⚠️ WO-3 의 푸터 굿즈 링크는 **WO-5 가 끝나야 404 가 안 난다.**

---

## WO-6 — 2단 칩 건수 내림차순 + 가로 스크롤 힌트

| | |
|---|---|
| **우선순위** | **P1** |
| **담당 역할** | 웹 렌더 |
| **선행조건** | §0-1 (W0) · **WO-1 · WO-3**(같은 `render()`) |
| **근거** | FEATURE-PLAN-2 §1-2 ③④ · §3 F4 |

### 손댈 파일

- `/Users/swkim72/source/sinsang-note/collect.py` — `CSS_EXTRA` 문자열 + `render()` 의 `subs` 생성부

### 지금 상태 (실측, 375px)

2단 칩 순서 = `SUBS` 선언 순: `라면41 햄버거3 피자12 치킨4 베이커리26 디저트6 분식1 일식40 샌드위치4 샐러드3`
`scrollWidth 735px / clientWidth 375px` → **4.5칩만 보인다.** 2위인 **일식 40건이 8번째**라 화면 밖.
스크롤바·그라데이션 등 **밀린다는 표시가 전혀 없다**(`scrollbar-width:none` + `::-webkit-scrollbar{display:none}`).

### 변경 내용

**① 2단 칩 정렬을 건수 내림차순으로.** `render()` 의

```python
subs = "".join(... for k in SUBS if scount.get(k))
```

를 `sorted(…, key=lambda k: (-scount[k], SUBS.index(k)))` 상당으로.
동률이면 `SUBS` 선언 순. 적용 후 예상:
`라면41 · 일식40 · 베이커리26 · 피자12 · 디저트6 · 치킨4 · 샌드위치4 · 햄버거3 · 샐러드3 · 분식1`

🟡 **1단(`PRIMARY`)은 건드리지 마라.** `전체 / 편의점 / 카페 / 외식` 이라는 의미 순서가 있고,
375px 에 339px 로 들어간다(실측).

**② 가로 스크롤 힌트 — 오른쪽 끝 12~16px 그라데이션.**

🔴 **구현 함정.** `nav`/`.subnav` 자체가 `overflow-x:auto` 다. 거기에 `::after` 를 붙이면
**그라데이션이 칩과 같이 스크롤돼 오른쪽 끝으로 사라진다.**
→ 래퍼를 하나 더 두고(`position:relative`) 그 위에 얹어라.

```
.navwrap{position:relative}
.navwrap::after{content:"";position:absolute;top:0;right:0;bottom:0;width:16px;
  pointer-events:none;background:linear-gradient(to right,transparent,var(--bg))}
```

- 1단·2단 **둘 다** 적용. 1단은 지금 안 밀리지만 칩이 하나만 늘어도 밀린다.
- 🟠 **스크롤이 끝까지 간 상태에서도 그라데이션이 남는다.** JS 로 숨길 수도 있지만
  **JS 를 추가하지 마라** — 이 프로젝트에서 JS 변경이 두 번 사고를 냈다.
  항상 보이는 16px 그라데이션이 "밀 수 있다"는 신호로 충분하다.
- `mask-image` 대안은 🟠 미확인(사파리 접두 필요 여부를 확인하지 않았다). **`::after` 로 가라.**

**③ 🔴 칩을 두 줄로 wrap 하지 마라.** 375px 실측 — 지금 첫 카드 top 이 **355px**,
첫 화면에 카드 1.3장이다. wrap 하면 +45px 이고, 칩이 13개가 되면 3줄이 돼 +90px 다.
그리고 **칩 개수가 데이터에 따라 변해서 줄 수가 매일 바뀐다.**

**④ 🟡 2단 줄이 사라지는 점프는 이번 범위가 아니다.** 카페·편의점을 누르면
`syncSub()` 가 `subnav.hidden = true` 로 줄을 없애고 카드가 59px 점프한다(실측).
**고치지 말고 보고만 해라.** PRODUCT-PLAN §6-2 가 "카페 2단에 음료·디저트를 넣는다"로
이미 예약한 자리다. 콘텐츠가 먼저다.

🔴 **`CSS_EXTRA` 는 여러 줄 CSS 블록이다. §0-2 — `nav{…}` 와 `.subnav{…}` 규칙을 통째로 다시 써라.**

### 완료 판정 기준

1. **정렬이 맞는다.**
   ```bash
   cd /Users/swkim72/source/sinsang-note && ./.venv/bin/python collect.py
   ./.venv/bin/python - <<'EOF'
   import re,pathlib
   h=pathlib.Path('docs/index.html').read_text(encoding='utf-8')
   s=re.search(r'id="subnav".*?</div></div>',h,re.S).group(0)
   v=[(m[0],int(m[1])) for m in re.findall(r'data-s="([^"]*)"[^>]*>[^<]*<span class="n">(\d+)',s)]
   print(v); print('OK' if v==sorted(v,key=lambda x:-x[1]) else 'FAIL 내림차순 아님')
   EOF
   ```
   → `OK`.
2. **그라데이션이 스크롤과 함께 움직이지 않는다.** 🔴 브라우저 375px 에서
   2단 칩을 **끝까지 오른쪽으로 밀고** 오른쪽 가장자리에 그라데이션이 **그대로 있는지** 본다.
   (래퍼를 안 쓰면 여기서 사라진다.)
3. **375px 첫 화면에 라면·일식·베이커리가 보인다.** 스크린샷으로 확인.
4. **첫 카드 top 이 안 늘었다.** 변경 전 **355px** 이하 유지.
   ```js
   Math.round(document.querySelector('.c').getBoundingClientRect().top + scrollY)
   ```
5. **1단은 그대로다.** `전체 / 편의점 / 카페 / 외식` 순서·건수 불변, 375px 에서 **339px** 유지.
6. **필터가 여전히 동작한다.** 🔴 §0-4 의 손 확인 3종 전부.
   (2단 칩 순서를 바꾸면 `subBtns` 배열 순서가 바뀐다 — `data-s` 로 매칭하므로 괜찮아야 하지만
   **반드시 눌러서 확인해라.** 여기가 두 번 죽은 자리다.)
7. §0-4 스모크 검사 `OK`.

### 다른 지시서와 같은 파일을 건드리는가

🔴 **WO-1 · WO-3 과 `collect.py:render()` 공유** (트랙 A 직렬, 마지막).
`CSS_EXTRA` 는 WO-6 단독 소유.

---

## WO-7 — Atom 피드 타임스탬프·건수 + RSS 링크

| | |
|---|---|
| **우선순위** | **P1** |
| **담당 역할** | SEO·피드 |
| **선행조건** | §0-1 (W0) |
| **근거** | FEATURE-PLAN-2 §3 F7 |

### 🔴 PRODUCT-PLAN §3 P1-6 의 진단을 정정하고 들어가라

그 문서는 "`<updated>` 에 빌드 날짜가 들어간다 → 매일 50건 중복 알림"이라고 썼다. **틀렸다.**
`web/seo.py:145` 가 `when = _rfc3339(collect._when(r))` 로 **상품 날짜**를 쓴다.
`<id>` 가 상품 상세 URL 이라 고유하므로 **중복 알림은 안 난다.**

실제 문제는 셋이다.

| | 증상 | 실측 |
|---|---|---|
| ① | 피드 자체 `<updated>` 도 상품 날짜다 | `docs/feed.xml` 51개 `<updated>` 전부 `2026-09-30T00:00:00Z`. 11시에 빌드했는데 "어제 자정 갱신" |
| ② | 50건 전부 같은 타임스탬프 → 정렬이 리더 구현에 맡겨진다 | 〃 |
| ③ | 하루 신규가 50건 넘으면 조용히 잘린다 | `FEED_MAX=50`, 09-30 빌드 "오늘 **107건**" |

### 손댈 파일

- `/Users/swkim72/source/sinsang-note/web/seo.py` — `_feed()`(171~189행) · `_entry()`(140~168행) · `FEED_MAX`(상수)

### 변경 내용

1. **`_feed()` 의 피드 자체 `<updated>` 를 빌드 시각으로.**
   `updated = _rfc3339(collect._when(rows[0]))` → `updated = _now()`.
   **항목의 `<updated>` 는 그대로 상품 날짜를 유지한다.**
2. **`_entry()` 에 `<published>` 추가.** `<updated>` 와 같은 값. Atom 에서 "언제 나온 것"의 표준 자리.
3. **`FEED_MAX` 50 → 100.** 실측 피크 107건을 담으려면 그래야 한다.
   피드 용량 57KB → 약 114KB. 허용 범위.
4. 🔴 **타임스탬프를 지어내지 마라.** "같은 날이면 i번째를 `00:00:{i}Z`" 같은 방식 금지.
   없는 시각을 만드는 것이고, 이 프로젝트는 "모르면 None"을 계약으로 삼는다(ROADMAP §3-6).
5. **푸터 RSS 링크는 WO-3 이 넣는다.** WO-7 이 끝났다고 WO-3 에 알려라.

### 완료 판정 기준

1. **XML 이 깨지지 않았다.**
   ```bash
   cd /Users/swkim72/source/sinsang-note && ./.venv/bin/python collect.py
   ./.venv/bin/python -c "import xml.dom.minidom as m; m.parse('docs/feed.xml'); print('WELLFORMED')"
   ```
2. **피드 자체 `<updated>` 가 오늘이고 시각이 자정이 아니다.**
   ```bash
   head -20 docs/feed.xml | grep '<updated>'
   ```
   → `2026-10-01T##:##:##Z` 형태. `T00:00:00Z` 면 미완료.
3. **항목 수가 늘었다.**
   ```bash
   grep -c '<entry>' docs/feed.xml       # 100 (또는 fresh 가 100 미만이면 그 수)
   grep -c '<published>' docs/feed.xml   # <entry> 수와 같아야 함
   ```
4. **항목 `<updated>` 는 여전히 상품 날짜다.** 전부 같은 값이어도 괜찮다 — 그건 데이터가 그런 것이다.
   ```bash
   grep -o '<updated>[^<]*' docs/feed.xml | sort | uniq -c
   ```
   → 피드 자체의 1건만 오늘 시각, 나머지는 `T00:00:00Z`.
5. **🔴 실제 RSS 리더에 넣어 본다.** 브라우저로 `feed.xml` 을 열거나 무료 리더에 URL 을 넣고
   **항목 제목·이미지·링크가 제대로 나오는지** 본다. 링크를 눌러 `/p/...` 로 가는지도 확인.
6. **`<id>` 가 전부 고유하다.**
   ```bash
   grep -o '<id>[^<]*' docs/feed.xml | sort | uniq -d    # 출력 없어야 함
   ```
7. **용량.** `ls -la docs/feed.xml` → 150KB 미만.
8. §0-4 스모크 검사 `OK` (홈이 안 바뀌어야 한다).

### 다른 지시서와 같은 파일을 건드리는가

🟢 **`web/seo.py` 단독** — 단 **WO-5(굿즈)도 `web/seo.py:build()` 를 건드린다.**
WO-5 를 마지막에 돌리기로 했으므로(§0-5 트랙 F) WO-7 이 먼저다.
⚠️ **WO-3 의 RSS 링크 노출이 WO-7 완료에 종속**이다.

---

## WO-8 — og:image 자체 생성 커버

| | |
|---|---|
| **우선순위** | **P1** |
| **담당 역할** | 자산 생성 |
| **선행조건** | §0-1 (W0) · `collect.py` 1줄은 **트랙 A(WO-1/3/6) 머지 후** |
| **근거** | FEATURE-PLAN-2 §1-2 ⑥ · §3 F5 |

### 🔴 "콜라주" 로 만들지 마라 — 반려 사유

PRODUCT-PLAN §6-8 ② 가 "og:image 를 콜라주로"라고 썼지만, 콜라주는 브랜드 이미지를
받아 합성해 **우리 도메인에서 재배포**하는 것이다. 지금은 핫링크라 **브랜드 서버가 서빙**하고
푸터의 "저작권은 각 브랜드에 있습니다"가 성립한다. 콜라주는 **PRODUCT-PLAN §4 가
명시적으로 금지한 "브랜드 이미지 자체 호스팅"** 그 자체이고 `CRAWLING-POLICY §3` 과도 충돌한다.

→ **코드로 그린 커버를 만든다.**

### 손댈 파일

- `/Users/swkim72/source/sinsang-note/web/assets.py` — `cover()` 신규 + `build()` 에서 호출
- `/Users/swkim72/source/sinsang-note/collect.py` — `render()` 의 `theme.head(..., image=…)` **1줄**

### 지금 상태 (실측)

```
og:image = https://d2afncas1tel3t.cloudfront.net/wp-content/uploads/2026/09/크림치즈말랑.png
```
홈 링크를 카톡에 던지면 **파리바게뜨 빵 사진**이 신상노트의 얼굴이 된다.
그 브랜드가 이미지를 내리면 공유 카드가 깨진다.

### 변경 내용

**① `web/assets.py:cover(stats) -> bytes`** — 1200×630 PNG.

`assets.py` 가 **이미 `zlib`+`struct` 로 truecolor PNG 를 직접 인코딩하고 있다**(Pillow 없음·설치 금지).
그 인코더를 재사용한다. 색은 **`theme.CSS` 의 `:root` 에서 읽는다** — 이 파일의 원칙 2번.

디자인:
- 배경 `--bg`(또는 `--accent`), 중앙에 **기존 아이콘 마크**(`_sparkle_quads()` 재사용)
- 그 아래 숫자·로마자만 — 예: `2026-10-01` / `25 NEW` / `SINSANG`

🔴 **한글을 PNG 로 찍으려 하지 마라.** `.venv` 에 폰트 래스터라이저가 없다.
글자 모양을 좌표로 직접 그리는 건 획이 적은 숫자·로마자까지다.
**제목·설명은 `og:title`·`og:description` 이 글자로 말해준다. 이미지는 브랜드 식별만 하면 된다.**

**② `build()` 에서 `docs/og.png` 로 출력.** 아이콘 4종과 같은 자리.

**③ `collect.py:render()` 1줄.**
```python
top = next((r for r in rows if r.get("image")), None)
_head = theme.head(..., image=(top or {}).get("image", ""), ...)
```
→ `image=ROOT_PATH + "og.png"`.

🟡 **`/p/`·`/b/`·`/c/` 는 지금처럼 그 페이지의 상품 이미지를 쓴다.**
그건 그 페이지의 내용이고 핫링크라 자체 호스팅이 아니다. **홈만 바꾼다.**

🟠 **미확인 — SVG 를 og:image 로 쓰는 것.** 카카오톡·슬랙 스크래퍼가 SVG 를 렌더하는지
확인하지 않았다. `icon.svg` 가 이미 있으니 되면 공짜다. **확인 전에는 PNG 로 간다.**

### 완료 판정 기준

1. **파일이 생기고 열린다.**
   ```bash
   cd /Users/swkim72/source/sinsang-note && ./.venv/bin/python collect.py
   ls -la docs/og.png
   ./.venv/bin/python -c "
   import struct;d=open('docs/og.png','rb').read()
   assert d[:8]==b'\x89PNG\r\n\x1a\n','PNG 시그니처 아님'
   w,h=struct.unpack('>II',d[16:24]);print('크기',w,'x',h)
   assert (w,h)==(1200,630);print('OK')"
   ```
   → `1200 x 630` + `OK`. 용량 **200KB 미만**.
2. **홈 og:image 가 우리 것을 가리킨다.**
   ```bash
   grep -o 'property="og:image" content="[^"]*"' docs/index.html
   ```
   → `/sinsang-note/og.png`. 🔴 브랜드 CDN 도메인이 남아 있으면 미완료.
3. **상세·브랜드·유형 페이지의 og:image 는 안 바뀌었다.**
   ```bash
   grep -ho 'property="og:image" content="[^"]*"' docs/p/*/index.html | head -3
   ```
   → 여전히 브랜드 CDN.
4. **🔴 아이콘 4종이 그대로다.** PNG 인코더를 건드렸으니 회귀를 확인한다.
   ```bash
   ls -la docs/icon.svg docs/icon-180.png docs/icon-512.png docs/manifest.webmanifest
   ```
   크기가 변경 전과 **거의 같아야** 하고, `icon-180.png`·`icon-512.png` 를 **열어서 눈으로 본다.**
5. **🔴 실제 공유 카드를 확인한다.** 배포 후 홈 URL 을 슬랙·카톡에 붙여 **썸네일이 뜨는지** 본다.
   (배포 전이라면 `og.png` 를 직접 열어 눈으로 확인하고, 배포 후 재확인을 후속으로 남긴다.)
6. **빌드 시간이 안 늘었다.** 외부 요청이 0건이어야 한다 — 이미지를 **다운로드하지 않는다.**
7. §0-4 스모크 검사 `OK`.

### 다른 지시서와 같은 파일을 건드리는가

🟢 `web/assets.py` 는 WO-8 단독.
🟡 `collect.py:render()` 1줄 — **트랙 A(WO-1/3/6)가 끝난 뒤 얹어라.**

---

## 부록 — 이 문서에서 다루지 않은 것

| 항목 | 왜 |
|---|---|
| 카드 URL 백필 | 이미 다른 작업자가 진행 중. FEATURE-PLAN-2 §1-2 ⑨ 에 경계만 적었다 |
| GS25 어댑터 / 이미지 내장 NEW 배지 조사 / 비프랜차이즈 업체조사 | 진행 중 |
| `docs/BACKLOG.md` · `docs/ASSIGNMENTS.md` | PM 소유. 건드리지 않았다 |
| 편의점 상품명 정규화 (PRODUCT-PLAN P0-3) | 이미 기획돼 있다. **WO-4 의 선행 조건**이라 그 사실만 적었다 |
| `is_fresh` 의 `is_new` ↔ `baseline` 순서 (PM B-13) | PM 이 잡은 항목. 과거 한 번에 바꿔 빽다방 11건·설빙 14건이 사라진 전례가 있어 **WO 들과 섞으면 안 된다** |
| 배포 전 필터 회귀 검사 (PRODUCT-PLAN §8-2 0') | 재기획하지 않고 **§0-4 로 전 지시서의 완료 기준에 넣었다** |
| F9 `/d/` 일자 아카이브 · F10 날짜 구분선 | P2. 위 8건이 끝난 뒤 지시서를 쓴다 |
| 유튜브 Data API 승격 | 조건부. FEATURE-PLAN-2 §3 F1-5 의 전제 4개가 갖춰진 뒤 |
