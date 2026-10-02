"""SPC삼립 — 보도자료 JSON API 에서 신제품과 출시일을 뽑는다.

오뚜기·오리온·샘표·해태제과식품·크라운제과와 같은 계보다(보도자료 제목 →
상품명). 조인 규칙은 `collectors/maker_orion.py` 것을 가져오고, 크라운이 보탠
두 가지(`_REPACK_NAME`·따옴표 앞 검사)를 그대로 쓴 뒤 삼립에서 실측한 함정
네 개를 더 보탰다(아래 §조인 규칙).

**2차 조사의 "신제품 신호 없음" 을 뒤집는다.**
`notes/CANDIDATES-DIRECT2.md` §1-3 은 SPC삼립을 **"상품 카탈로그 자체가 없다.
제품은 brand.naver.com/samlip = 네이버 스마트스토어(범위 밖)"** 로 적고 신제품
신호를 **없음**으로 판정했다. 그 판정은 `spcsamlip.co.kr/brand/bakery`
**한 경로만** 보고 내린 것이다. 카탈로그가 없다는 말은 맞다 — 그런데
**보도자료가 깨끗한 JSON API 로 열려 있고, 이 레포에서 출시 밀도가 가장 높다.**
("카탈로그가 없다" ≠ "보도자료도 없다" — 1차가 크라운·해태·삼양에서 낸 것과
같은 종류의 오판이다. notes/CANDIDATES-MAKER.md §0 참고.)

수집 경로. 2026-10-02 실측:
  GET https://www.spcsamlip.co.kr/api/public/press-releases?page=1&size=30
  {"success": true, "message": null,
   "data": {"items": [
      {"id": "371",
       "title": "삼립, 세계 3대 식품박람회 ‘SIAL 파리’ 참가…K-호떡 선보인다",
       "content": "<p class=\\"ed-pc-body1\\">…기사 전문 HTML…</p>",
       "thumbnailUrl": "/uploads/images/eff6692a-…-b05be553c47c.jpg",
       "publishedDate": "2026-10-01",
       "createdAt": "2026-10-01T11:33:27", "updatedAt": "2026-10-02T11:21:25",
       "viewCount": "16", "isActive": "True",
       "categories": [{"id": 6, "name": "글로벌", "type": "press_release", …}]}, …],
     "page": 1, "size": 30, "totalCount": 364, "totalPages": 13}}

**이 API 를 어떻게 찾았나** (다음 사람이 같은 함정에 빠지지 않게 적어 둔다).
페이지(`/now/pr`)는 Next.js 정적 export 라 원본 HTML 에 기사가 하나도 없다 —
`__NEXT_DATA__` 조차 `{"props":{"pageProps":{}}}` 로 비어 있다. 날짜 토큰 0개,
'출시' 0개. 여기서 접으면 "CSR 이라 불가" 가 된다. 실제로는 **빌드된 JS 청크
안에 경로 문자열이 그대로 박혀 있었다** — `_buildManifest.js` 와 페이지 청크를
받아 `/[A-Za-z0-9/_-]+/` 중 board·news·press 를 품은 것만 추려 내니
`/public/press-releases` 가 나왔고, 앞에 `/api` 를 붙이니 바로 열렸다.
  GET /public/press-releases      → 404 + Next.js 셸 17,600B
  GET /api/public/press-releases  → 200 + JSON 17,414B      ← 이것
⚠️ **404 를 Next.js 셸(17,600B)로 준다.** `/now/news`·`/now/press` 같은 없는
   경로도 200 처럼 보이는 HTML 이 온다. 길이·md5 로 가려야 한다.

| 키 | 쓸 곳 |
|---|---|
| `title` | 제목 → `_pick` 이 상품명을 뽑는다 |
| **`publishedDate`** | **`released_at`.** `YYYY-MM-DD` |
| `createdAt` | **`publishedDate` 가 null 일 때의 대체값**(아래) |
| `thumbnailUrl` | 사진. 상대경로라 SITE 를 붙인다 |
| `id` | 상세 주소 `/now/pr/{id}` (200 확인) |
| `updatedAt` | ⚠️ **쓰지 마라**(아래) |

⚠️ **`publishedDate` 가 옛 기사에선 null 이다.** 120건을 전수로 받아 세어 보니
   최근 **57건만** 값이 있고(2025-12-04 이후) 그 앞은 전부 null 이다. 대신
   그 기사들의 `createdAt` 이 **`2025-09-22T00:00:00` 처럼 시각이 정각 0시**다
   — 사이트를 옮기면서 **보도일을 날짜만 채워 넣은 값**이고 실제 보도일과
   맞는다(`‘파삭칩 버터갈릭맛’ 출시` = 2025-09-22, 기사 본문과 일치).
   최근 기사의 `createdAt` 은 반대로 `2026-10-01T11:33:27` 처럼 진짜 등록 시각이다.
   → **`publishedDate or createdAt[:10]`** 으로 쓴다. 둘 다 보도일 축이다.
⚠️ **`updatedAt` 은 절대 쓰지 마라.** 2025-09~11 기사들의 `updatedAt` 이
   `2026-07-20`·`2026-08-26`·`2026-09-30`·`2026-10-02` 로 흩어져 있다 —
   콘텐츠 일괄 재저장이다. 동서식품 `regDt`·해태 `createdDttm` 과 같은 함정인데,
   여기선 **`createdAt` 이 아니라 `updatedAt` 쪽이 오염됐다**는 게 다르다.

**일괄 등록 흔적 — 거의 없다.** 120건의 날짜에서 같은 날 2건이 세 쌍뿐이다
(2026-01-30 · 2026-01-27 · 2026-01-09). 롯데칠성·롯데웰푸드가 쓰는 `BULK`
임계(같은 날 4건)에 못 미친다. 그중 2026-01-30 한 쌍은 **같은 기사를 두 번
올린 것**이다(`SPC삼립, 두바이 스타일 파이∙케이크 출시` / `삼립, 두바이 스타일
파이·케이크 출시`) — 이름이 같아서 `Item.key` 중복으로 저절로 걸러진다.

**출시 밀도 — 이번 조사 1위다.** 4페이지 120건(2024-07 ~ 2026-10-01)을 전수로
세었다: 제목에 `출시|론칭|런칭|선봬|선보` 가 든 기사가 **81건(68%)** 이다.
나머지 39건은 IR·주총·수상(레드닷·iF)·HACCP 인증·코스트코 입점·상생펀드·기부다.
빙그레(30건 중 6건)·동아오츠카(45건 중 1건)와 비교가 안 된다.

⚠️ **과자 전업이 아니다.** 삼립은 빵·호빵·떡·디저트가 중심이고 과자(파삭칩·
   약과자·젤리뽀·누네띠네)는 그중 일부다. 샐러드(피그인더가든)·간편식
   (시티델리)·면(하이면)·육가공(그릭슈바인)도 한 피드에 섞인다. 그래서
   `BRANDS` 세부분류를 '과자' 가 아니라 **'베이커리'** 로 적는다.
⚠️ **계열·B2B 가 섞인다.** `SPC GFS`(식자재 B2B)·`얌/Yaam`(B2B 솔루션)·
   `레디비`(생지)·`휴면생지`는 소비자 상품이 아니다. 주어가 `SPC GFS` 면
   `_HOLDING` 이 잡고, 나머지는 `_LAUNCH_BEFORE`('브랜드'·'솔루션'…)가 잡는다.
⚠️ **주류가 섞인다.** `삼립, 식빵으로 완성한 오리지널 밀맥주 ‘크러스트’ 출시`
   — 운영자가 주류를 따로 처리하므로 여기선 넣으면 안 된다. `_BOOZE` 로 막았다.
   ⚠️ `base.py`·`taxonomy.py` 의 판정 단어 목록은 건드리지 않았다(지시 사항).
      이 어댑터 안에서만 제목 단위로 거른다.
⚠️ **해외 전용·수출 기사가 많다.** 美 코스트코 입점, 캐나다 T&T 입점, SIAL 파리,
   꿀떡 수출 — 120건 중 10건 넘는다. 국내 화면에 올리면 거짓이 된다.
   크라운이 쓰는 `日`·`美`·`글로벌`·`수출`·`해외` 역필터를 그대로 가져왔다.

**조인 규칙 — 삼립에서 보탠 네 가지** (120건 제목을 전수로 눈에 대고 맞췄다).
  ① **따옴표와 `출시` 사이가 비어 있지 않으면 버린다.** 계보는 구분자(`·`,`,`)만
     봤는데 삼립은 따옴표 뒤에 **진짜 상품명이 따로 온다**:
       `빵도 이제 상황별 ‘맞춤 시대’ 비스포크빵 출시`   ← 상품은 '비스포크빵'
       `‘FTO 기술’ 휴면생지 출시`                      ← 상품은 '휴면생지'
       `‘포켓몬빵’ 1,000만 봉 판매…신제품 추가 출시`     ← 기존 제품 판매 기사
       `삐약이 ‘신유빈’ 모델로 2024 신제품 출시`         ← 따옴표 안은 사람 이름
     네 건 다 따옴표 안을 상품명으로 쓰면 **틀린 이름이 화면에 오른다.**
     → 따옴표 끝과 동사 사이에 공백 말고 뭔가 있으면 버린다. 이 규칙 하나가
       오탐 7건을 지웠고, 참 양성은 한 건도 안 줄었다(전수 대조).
  ② **이름에 쉼표가 있으면 상품이 둘이다.** `‘시루파이, 단팥 떠롤’ 출시`.
     계보의 `·∙` 금지에 `,` 를 더했다.
  ③ **따옴표 앞이 '브랜드'·'솔루션'·'플랫폼'·'베이커리' 면 브랜드 출범이다.**
       `온라인 전용 키즈 베이커리 ‘키키오븐’ 출시`      ← 브랜드다
       `B2B 푸드 토탈 솔루션 브랜드 ‘Yaam(얌)’ 론칭`    ← 브랜드다
     따옴표 **바로 앞 14자**만 본다. 넓히면 `프리미엄 베이커리 선물세트` 처럼
     멀리 떨어진 단어까지 물어 참 양성이 죽는다.
  ④ **앞 따옴표와 뒤 따옴표 사이가 구분자뿐이면 상품이 둘이다.**
       `‘샌드위치’, ‘햄버거’ 출시` · `‘함박 스테이크’, ‘미트볼’ 출시`
     계보(크라운)는 "사이가 **완전히 비었을** 때"만 봤다. 쉼표 하나가 끼면
     뒤엣것만 올라간다 — 실제로 `햄버거`·`미트볼` 두 건이 그렇게 샜다.

전수 대조로 **120건 중 22건**이 남는다(아래 §검증). 눈으로 세어 본 손실도
적어 둔다 — 버리는 진짜 신제품:
  · `‘치즈인더가든’ 샐러드 출시` · `‘크래프트 크림치즈 딸기’ 베이커리 출시`
    → 규칙 ①. 따옴표 안이 이름의 일부일 뿐이라 그대로 쓰면 반쪽 이름이 된다.
  · `‘탕종 또띠아 3종’ 출시` · `‘간편식 3종’ 출시` 류 **`N종` 전부**
    → 계보의 `_MULTI`. 한 기사에 상품이 여럿이라 이름을 하나로 못 적는다.
  · `‘주종발효’ 시리즈 출시` · `‘미식 안주 시리즈’ 출시`
    → 시리즈는 묶음이다(`_REPACK_NAME`).
  계보 방침대로 **틀린 이름을 올리느니 놓치는 쪽**을 골랐다.

robots: `https://www.spcsamlip.co.kr/robots.txt` → **200, 150바이트, text/plain.**
        원문 전체:
            User-agent: *
            Allow: /
            Disallow: /admin
            Disallow: /admin/
            Disallow: /now/promise
            Disallow: /now/promise/
            Sitemap: https://spcsamlip.co.kr/sitemap.xml
        ⚠️ `Allow: /` 가 `Disallow` **앞**에 있다(2차 §5 가 적은 '선행' 배치).
        금지는 `/admin`·`/now/promise` 뿐이고 우리가 쓰는 `/api/public/...`·
        `/now/pr` 은 어느 규칙에도 안 걸린다. **이번 조사에서 가장 깨끗한 축.**
        (`www.` 는 apex 로 301 리다이렉트되고 robots 는 apex 것 하나다.)
약관:   확인하지 않았다.

⚠️ **`www.samlip.co.kr` 는 삼립이 아니다.** 조사 중 실제로 열어 봤는데
   `/tech/lamp_product.php`·`/tech/mirror_product.php` 가 나오는 **자동차 램프
   회사 ㈜에스엘(SL)** 이다. 이름이 겹칠 뿐이다. 삼립은 `spcsamlip.co.kr` 다.
"""
import re
import time
from datetime import date, timedelta

from . import base
from .base import Item

BRAND = "SPC삼립"
SITE = "https://www.spcsamlip.co.kr"
NEWS = SITE + "/api/public/press-releases"     # 보도자료 JSON API
VIEW = SITE + "/now/pr"                        # 상세 (/now/pr/{id}, 200 확인)
SIZE = 30            # ⚠️ 상한이다. size=100 을 보내도 응답 `size` 가 30 으로 온다.
MAX_PAGES = 3        # 30건 × 3 ≈ 14개월. 한 페이지 약 94KB(본문 HTML 포함).
DAYS = 300
DELAY = 2.2

# 소비자 상품이 아닌 계열. 제목 머리가 이거면 B2B·지주 기사다.
_HOLDING = re.compile(r"^\s*SPC\s*GFS")
# 주류는 운영자가 따로 처리한다. 제목에 술이 보이면 통째로 버린다.
# 🔴 2026-10-02 검수 지적으로 좁혔다. **여긴 베이커리 전업이라 술 이름이 빵
# 이름에 그대로 들어온다** — 이 레포가 이미 `와인` 으로 한 번 데였다
# (나폴레옹과자점 `무화과와인바게트`·`화이트와인애플파이`. base.py ALCOHOL_WORDS
#  주석 참고 — 거기서도 `와인` 은 **빼는 쪽**으로 결론났다).
#   · `와인`  → 뺐다. 삼립은 와인을 안 판다. 걸릴 건 `와인바게트` 류 빵뿐이다.
#   · `막걸리` → base.py `_ALCOHOL_RE` 와 같은 꼬리 가드 + 빵/식빵/케이크를 더했다.
#   · `맥주`  → `맥주빵`·`맥주안주`·`맥주효모` 를 피한다. `밀맥주 ‘크러스트’` 는
#               뒤가 공백이라 그대로 걸린다(실측).
#   · `사케`  → `사케라또`(스타벅스 음료) 같은 말을 피한다.
# 150건 전수에서 히트는 `식빵으로 완성한 오리지널 밀맥주 ‘크러스트’ 출시` 1건,
# 오탐 0 — 좁힌 뒤에도 같다(아래 fetch 주석의 실측).
_BOOZE_RE = re.compile(
    r"소주|위스키|하이볼|주류"
    r"|맥주(?!빵|안주|효모|빵집)"
    r"|막걸리(?!향|맛|풍미|빵|식빵|케이크)"
    r"|사케(?!라)")

# --- 제목 → 상품명 (maker_orion 계보 + 크라운 보강 + 삼립 보강 4개) -----------
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭|런칭)")
_SINGLE = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_HEAD = re.compile(r"[“\"]([^”\"]*)[”\"]")
_MULTI = re.compile(r"\d+\s*종")
_SEP_ONLY = re.compile(r"^[\s,·∙、/]*$")        # 삼립 보강 ④

_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "협약", "체결", "주주총회", "후원", "기부", "추모", "공모", "발대식",
         "심포지엄", "박람회", "팝업", "캠페인", "발탁", "앰배서더", "재단",
         "경연", "시상", "간담회", "개최", "스폰서", "리뉴얼", "실적",
         "매진", "진행", "참가", "참여", "전개", "지원", "프로젝트",
         "인증", "입점", "합병", "증설", "개편", "기념",
         # 국내 출시가 아닌 건 화면에 올리면 거짓이 된다(크라운과 같은 축).
         "日", "美", "글로벌", "수출", "해외")
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마", "전용 앱")
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다", "쏜다")
_REPACK_HEAD = ("에디션", "라벨")
_REPACK_MID = ("테마", "에디션", "라벨", "컬래버", "콜라보")
_REPACK_NAME = ("에디션", "컬렉션", "한정판", "선물세트", "기획팩", "시리즈")
# 삼립 보강 ③ — 따옴표 '바로 앞' 에 오면 상품이 아니라 브랜드·사업의 출범이다.
_LAUNCH_BEFORE = ("브랜드", "솔루션", "플랫폼", "베이커리", "레이블")
_LAUNCH_WINDOW = 14          # 바로 앞 몇 글자만 보나. 넓히면 참 양성이 죽는다.


def _pick(title: str) -> str:
    """보도자료 제목에서 상품명을 뽑는다. 상품을 특정 못 하면 빈 문자열."""
    t = " ".join(title.split())
    if _HOLDING.match(t) or _BOOZE_RE.search(t):
        return ""
    if any(w in m.group(1) for m in _HEAD.finditer(t) for w in _REPACK_HEAD):
        return ""
    body = _HEAD.sub(" ", t)
    if any(w in body for w in _SKIP) or _MULTI.search(body):
        return ""
    qs = list(_SINGLE.finditer(body))
    if len(qs) >= 2 and any(w in body[qs[-2].end():qs[-1].start()] for w in _REPACK_MID):
        return ""
    verb = None
    for m in _VERB.finditer(body):
        verb = m
    if not verb or any(w in body[verb.end():] for w in _TAIL):
        return ""
    head = body[:verb.start()]
    quoted = None
    for m in _SINGLE.finditer(head):
        quoted = m
    if not quoted or any(w in head[quoted.end():] for w in _BETWEEN):
        return ""
    before = head[:quoted.start()]
    # 크라운 보강 — 따옴표 앞에 에디션/한정판이 있으면 기존 라인의 변형이다.
    if any(w in before for w in _REPACK_MID):
        return ""
    # 삼립 보강 ③ — 따옴표 바로 앞이 '브랜드'·'솔루션'이면 브랜드 출범 기사다.
    if any(w in before[-_LAUNCH_WINDOW:] for w in _LAUNCH_BEFORE):
        return ""
    # 삼립 보강 ① — 따옴표와 동사 사이에 뭔가 있으면 따옴표 안은 상품명이 아니다.
    if head[quoted.end():].strip():
        return ""
    # 삼립 보강 ④ — 앞 따옴표와 사이가 구분자뿐이면 한 기사에 상품이 둘이다.
    hq = list(_SINGLE.finditer(head))
    if len(hq) >= 2 and _SEP_ONLY.match(head[hq[-2].end():hq[-1].start()]):
        return ""
    name = quoted.group(1).strip(" ,·∙")
    # 삼립 보강 ② — 쉼표가 남아 있으면 상품이 둘이다(‘시루파이, 단팥 떠롤’).
    if len(name) < 2 or any(c in name for c in "·∙&?!,"):
        return ""
    if any(w in name for w in _REPACK_NAME):
        return ""
    return name


def _date(row: dict) -> str:
    """보도일. `publishedDate` 가 없으면 `createdAt` 의 날짜 부분을 쓴다.

    옛 기사는 `publishedDate` 가 null 이고 `createdAt` 이 `…T00:00:00` 으로
    보도일만 채워져 있다(docstring 참고). `updatedAt` 은 일괄 재저장이라 안 쓴다.
    """
    s = (row.get("publishedDate") or row.get("createdAt") or "")[:10]
    m = re.match(r"^(20\d{2})-(\d{2})-(\d{2})$", s)
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _image(row: dict) -> str:
    """썸네일. 상대경로(`/uploads/images/…`)라 SITE 를 붙인다.

    ⚠️ 원본이 1MB 가 넘는 것도 있다. 주소만 담고 어댑터는 요청하지 않는다.
    """
    src = (row.get("thumbnailUrl") or "").strip()
    if not src or src.startswith("data:"):
        return ""
    if src.startswith("http"):
        return src if src.startswith("https://") else ""
    return SITE + ("" if src.startswith("/") else "/") + src


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(NEWS, params={"page": page, "size": SIZE}))
            r.raise_for_status()
            # ⚠️ 없는 경로에 Next.js 셸(HTML 17,600B)을 200 처럼 주는 사이트다.
            #    상태코드가 아니라 JSON 모양으로 판정한다.
            try:
                data = r.json()["data"]
                rows = data["items"]
            except Exception as e:
                raise ValueError(
                    f"SPC삼립 보도자료 API 가 JSON 을 안 준다. {r.url} → "
                    f"{len(r.content)}B, content-type="
                    f"{r.headers.get('content-type')} — Next.js 404 셸로 "
                    f"떨어졌는지(= /api/public/press-releases 가 바뀌었는지) 확인하라"
                ) from e
            if page == 1 and not rows:
                raise ValueError(
                    f"SPC삼립 보도자료 1페이지가 비었다. {r.url} → totalCount="
                    f"{data.get('totalCount')} — 364건짜리 아카이브라 비어 있을 수 없다")
            if not rows:
                break

            for row in rows:
                title = " ".join((row.get("title") or "").split())
                released = _date(row)
                if released and released < floor:
                    continue
                name = _pick(title)
                if not name:
                    continue
                rid = str(row.get("id") or "").strip()
                it = Item(
                    brand=BRAND,
                    name=name,
                    # 기사 제목이 그대로 설명이 된다. 앞의 회사명만 턴다.
                    desc=re.sub(r"^\s*(SPC\s*)?삼립[^,]{0,12},\s*", "", title),
                    image=_image(row),
                    released_at=released,
                    is_new=True,     # 브랜드가 '출시'라고 낸 기사다
                    url=f"{VIEW}/{rid}" if rid.isdigit() else "",
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

            fresh = [d for d in (_date(x) for x in rows) if d]
            if fresh and max(fresh) < floor:
                break
            if len(rows) < SIZE:
                break
    return items
