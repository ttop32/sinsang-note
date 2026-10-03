"""농심 — 뉴스룸 보도자료에서 신제품과 출시일을 뽑는다. 라면 점유율 1위사다.

오뚜기·오리온·샘표·삼양식품과 같은 계보다(보도자료 제목 → 상품명).
상품명 추출만 `collectors/maker_sajo.py`·`collectors/maker_myunsarang.py` 쪽을
따랐다 — 농심도 **따옴표 없는 제목이 섞인다**(아래 §제목 형식).

## 🔴 2026-10-03 검수에서 소스를 통째로 바꿨다 (여기를 먼저 읽어라)

앞 판(2026-10-02)은 **브랜드관 신제품 면** `brand.nongshim.com/new_product/index`
를 읽고 사진 파일명의 epoch 를 `uploaded_at` 에 넣었다. 그게 **두 가지로 틀렸다.**

**① 브랜드관이 4개월째 멈춰 있다.** 2026-10-03 실측 — 브랜드관 신제품 면의 최신
항목이 `신라면 로제`(2026-06)이고 그 뒤로 갱신이 없다. 그 사이 농심이 실제로 낸
국내 신제품 **3건을 통째로 놓치고 있었다**(외부 기사로 교차검증):
```
2026-08-10  포테토칩 4종 (편의점 4사 한정)      보도자료 id=195
2026-09-21  생생신툼바떡볶이면                 보도자료 id=208   ← 9/28 출시
2026-09-30  너구링 (너구리 × 양파링)           보도자료 id=212   ← 10/12 출시
```
검수 실측에서 **농심 8건이 전부 60일 창 밖이라 화면 0건**이었는데, 그게
'농심이 신제품을 안 냈다' 가 아니라 **우리가 늙은 경로를 보고 있었다**는 뜻이었다.
라면 점유율 55.5% 1위사가 조용히 화면에서 빠져 있던 것이다.

**② epoch 는 출시일이 아니다 — 그리고 일 단위로 안 맞는다.** 8건을 외부 기사와
대조하니 사진 업로드가 실제 출시보다 **0~13일 앞선다**(사전 에셋 업로드):
```
빵부장 말차빵     업로드 2025-12-15  출시 2025-12-15   0일
누룽지팝 매콤한맛  업로드 2026-05-15  출시 2026-05-18  -3일
망고킥           업로드 2026-05-13  출시 2026-05-18  -5일
바삭츄리 고튀     업로드 2026-01-16  출시 2026-01-22  -6일
누들핏 새우탕맛    업로드 2025-11-13  출시 2025-11-24  -11일
라뽁구리 큰사발면  업로드 2026-01-13  출시 2026-01-26  -13일
```
월초·월말 제품은 **월이 통째로 틀어진다.** 보도자료가 날짜를 주는데 추정값을
쓸 이유가 없다.

**③ 브랜드관은 상품명 띄어쓰기도 임의로 지운다.** `신라면로제`·`라뽁구리큰사발면`
— 전 매체·공식 보도자료는 `신라면 로제`·`라뽁구리 큰사발면` 이다. 보도자료 제목이
정본이다.

→ **쓰지 않게 된 경로를 지우지 말고 남겨 둔다**(다음 사람이 또 거기서 시작한다):
  `brand.nongshim.com/new_product/index` 200 / 436,603B, 완전 SSR, 9건.
  `.newProductList li` → `h1`(상품명)·`h2`(설명)·`.img img`·`.btn a`. 날짜 없음.
  **지금은 늙었다.** 농심이 다시 돌리기 시작하면 사진 축으로 다시 볼 만하다.

## 쓸 수 없는 경로 (여기서 시간 버리지 마라)

  GET https://www.nongshim.com/promotion/list_news   (보도자료)   200 / 103,120B
  GET https://www.nongshim.com/promotion/news_list   (같은 면)    200 / 103,031B
    **날짜 토큰 0개 · '출시' 0개.** 103KB 가 전부 내비·사이트맵이다. 브라우저로
    열어도 목록 자리가 **비어 있다** — JS 가 늦게 붙는 게 아니라 렌더된 화면에도
    글이 한 줄도 없다. XHR 도 안 뜬다. 사이트맵엔 '보도자료'로 남아 있는데
    **내용이 newsroom 으로 옮겨 갔다.**
  GET https://www.nongshim.com/product/productNewList                404 / 197B
  레거시 상세는 아직 살아 있다(`/promotion/notice/press_view?groupCode=003&groupId=925`
  → 바삭츄리 고튀). 목록이 없어서 못 쓴다. newsroom 과 번호 체계가 다르다.

## 쓰는 경로

  GET https://www.nongshim.com/newsroom/news/list?category=all&page=9
                                                  200 / 598,906B  **완전 SSR**
    <article class="news-card" data-category="product">
      <a class="news-card__link" href="view?id=212&category=all&page=1">
        <span class="news-card__media"><img
            src="https://image.nongshim.com/newsroom/news/1790724261676.jpg" …></span>
        <span class="news-card__tag"> 신제품 </span>
        <h3 class="news-card__title">농심, 모디슈머 레시피 담은 스낵 ‘너구링’ 출시</h3>
        <p class="news-card__content">…기사 본문 전체…</p>
        <time class="news-card__date">2026/10/01</time>
      </a></article>
  선택자: `article.news-card` → `h3.news-card__title` · `time.news-card__date` ·
  `a.news-card__link`(상세) · `img`(사진, **절대 https URL**).
  **제목이 안 잘린다** — 상세를 열 필요가 없다. 날짜는 `2026/10/01` 꼴.

  ⚠️⚠️ **`page=N` 은 '그 페이지'가 아니라 '처음부터 N페이지까지 누적'이다.**
     실측: page=1 → 12행 / page=4 → 48행 / page=9 → 108행 / page=20 → 213행(전건).
     12 × N 이다. **그래서 요청을 한 번만 한다** — 반복문을 돌리면 같은 걸 몇 번씩
     다시 받는다. robots 가 `Crawl-delay: 10` 이라 더더욱 한 번이어야 한다.
  ⚠️ `category=product` 로 좁히면 신제품만 40건이 온다(202KB). 그걸 안 쓰고
     `category=all` 을 받는 이유는 **아래 비율 가드의 분모**가 필요해서다.
     한 번의 요청으로 신호와 분모를 같이 받는다.

## 날짜 — 보도자료 게시일이다 (출시일과 며칠 차이가 난다)

`time.news-card__date` 를 `released_at` 에 넣는다. ⚠️ 엄밀히는 **보도일**이고
본문에는 보통 `오는 N월 N일 출시` 라고 며칠 뒤가 적힌다(너구링: 보도 09/30,
출시 10/12). 본문을 파싱해 출시일을 뽑는 길은 가지 않았다 — 문장 표현이
제각각이고(`오는`·`부터`·`정식`) 틀리면 조용히 어긋난다. **보도일은 출시보다
늦지 않으므로 신상 창을 놓치는 쪽으로만 틀린다**(안전한 방향이다).

## 제목 형식 — 따옴표가 **없는 제목이 섞인다**

40건 전수에서 본 두 꼴:
    농심, 모디슈머 레시피 담은 스낵 ‘너구링’ 출시     ← 따옴표 있음
    농심, 생생신툼바떡볶이면 출시                    ← **따옴표 없음**
    농심, 누룽지팝 출시 / 농심, 메론킥 출시 / 농심, 배홍동칼빔면 출시
오리온 계열(따옴표 안만 쓰는 규칙)을 그대로 쓰면 뒤쪽이 통째로 날아간다.
→ 사조·면사랑 방식. **주어(`^.*?농심…,`)를 떼고, 따옴표가 있으면 첫 따옴표부터,
없으면 머리 전체를 동사 앞까지 잡아** 따옴표 기호와 `N종` 꼬리를 턴다.
  ⚠️ 주어에 쉼표가 없는 제목이 있다 — `농심과 엽떡의 콜라보! '포테토칩 엽떡로제맛' 출시`.
     따옴표가 있어서 그쪽 경로로 제대로 풀린다(`포테토칩 엽떡로제맛`).
     ⚠️ 콜라보 제품을 '협업' 이라고 버리면 안 된다 — GS25 선례(사워레몬요거트 등
        2건)대로 **협업으로 만든 신제품은 진짜 신제품**이다.

## ⚠️ 섞이는 것 — 전부 걸러야 한다 (40건 전수 실측)

  **건강기능식품**  `농심 라이필, ‘더마콜라겐 바이탈리포좀C’ 출시`(2026-06-15) ·
      `농심, ‘라이필 더마콜라겐 시그니처RN’ 출시`(2025-09-26). `라이필` 이 농심의
      건기식 브랜드다. **주어 화이트리스트로는 뒤엣것을 못 막는다**(주어가 그냥
      '농심' 이다) → `_NOT_OUR_LINE` 으로 이름·제목에서 본다.
      ⚠️ `콜라겐` 한 단어로 줄이지 마라 — 콜라겐을 넣은 식품이 실재한다.
  **해외 전용**     `농심, ‘신라면 김치볶음면’ 글로벌 출시`(2025-11-04)
  **한정·굿즈 협업** `‘케이팝 데몬 헌터스’ 속 신라면 3종 한정 출시` ·
      `<케이팝 데몬 헌터스> 스페셜 제품 한정 출시` — 기존 제품의 한정 패키지다
  **상품 특정 불가** `편의점 4사와 손잡고 포테토칩 4종 동시 출시`(2026-08-10) —
      편의점별로 **서로 다른 4개**라 하나로 특정할 수 없다(**아는 손실**).
      `_BETWEEN` 의 `손잡고` 가 막는다.
  **캠페인**        `올리브영·산리오와 손잡고 ‘농심 K-스낵’ 알린다` — 동사가 없다

## 🔴 신제품 태그 비율 가드

브랜드가 기사에 직접 붙이는 분류다(`data-category` ↔ `news-card__tag`).
2026-10-03 실측 — `category=all&page=9` 108건의 분포:
```
domestic 국내 ~38%  ·  global 글로벌 ~35%  ·  product 신제품 ~19%  ·  esg ESG ~8%
```
`0%` 도 `100%` 도 아니다. 이 레포가 배지로 세 번 데였기 때문에(설빙 14→4 ·
퀴즈노스 66건 전부 NEW · 컴포즈 배지가 그림 안에 합성돼 0건) **존재가 아니라
비율로 믿는다.** 어느 쪽이든 깨지면 조용히 넘기지 않고 터뜨린다.

robots: https://www.nongshim.com/robots.txt → 200 / 1,037B.
        `User-agent: * → Disallow: /` 이고 Googlebot·Bingbot·Yeti·Naverbot·Daumoa 와
        GPTBot·**ClaudeBot**·anthropic-ai·PerplexityBot·CCBot 등 명명된 봇만 `Allow: /`.
        우리 UA 는 어느 그룹에도 없어 `*` 가 적용된다 = **형식상 전면 금지.**
        운영자 판단으로 수집하되 삭제 요청이 오면 다투지 말고 즉시 내린다
        (base.BRANDS 의 이마트24·도미노피자와 같은 칸).
        ⚠️ **`Crawl-delay: 10` 을 선언한다.** 이 어댑터는 요청이 **1회뿐**이라 사실상
           걸릴 일이 없지만, 경로를 늘리게 되면 10초를 지켜라(`DELAY`).
        `brand.nongshim.com/robots.txt` 도 200 / 724B 로 따로 있다.
약관:   확인하지 않았다.
"""
import re
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "농심"
SITE = "https://www.nongshim.com"
LIST = SITE + "/newsroom/news/list"
# ⚠️ page=N 은 누적이다(12 × N). 한 번만 요청한다 — 위 docstring 참고.
# 9 = 108건 ≈ 11개월. DAYS(300일)를 덮는다.
PAGE = 9
DAYS = 300
DELAY = 10.0        # robots 가 Crawl-delay: 10 을 선언한다. 경로를 늘리면 지켜라.

# 브랜드가 기사에 직접 붙이는 분류. `data-category` 와 `.news-card__tag` 가 짝이다.
NEW_CAT = "product"      # 화면 표기 '신제품'
# 비율 가드의 상한. 전체 기사의 이만큼을 넘게 '신제품' 이라고 하면 그건
# 신호가 아니라 장식이다 — 아래 fetch() 의 가드 주석 참고.
MAX_NEW_RATIO = 0.6

# --- 제목 → 상품명 (추출은 maker_sajo·maker_myunsarang, 역필터는 maker_orion) ---
_SUBJECT = re.compile(r"^.*?농심[^,]{0,8},\s*")   # `농심,` · `농심 라이필,`
_QUOTED = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_QUOTE_CHARS = re.compile(r"[‘’'`“”\"]")
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭|런칭)")
_COUNT_TAIL = re.compile(r"\s*\d+\s*종\s*$")
_NEW_TAIL = re.compile(r"\s*신제품\s*$")

_SKIP = ("돌파", "완판", "누적", "성료", "수상", "선정", "채용", "매출", "영업이익",
         "협약", "체결", "주주총회", "후원", "기부", "추모", "공모", "발대식",
         "심포지엄", "박람회", "팝업", "캠페인", "발탁", "앰배서더", "재단",
         "경연", "시상", "간담회", "개최", "스폰서", "리뉴얼", "실적",
         "매진", "진행", "참가", "참여", "전개", "지원", "프로젝트",
         "이벤트", "광고", "조회수", "할인", "선물세트", "프로모션",
         # 기존 제품의 한정 패키지다. 실측 2건 다 '케이팝 데몬 헌터스' 협업.
         # ⚠️ `한정` 한 단어로 줄이지 마라 — `한정식` 이 물린다(사조 선례).
         "한정 출시", "한정판",
         # 국내 출시가 아닌 건 화면에 올리면 거짓이 된다.
         "日", "美", "글로벌", "수출", "해외")

# ⚠️ **주어로는 못 막는 구멍 — 농심이 내는 건강기능식품.** 실측 2건:
#     농심 라이필, ‘더마콜라겐 바이탈리포좀C’ 출시     (2026-06-15)
#     농심, ‘라이필 더마콜라겐 시그니처RN’ 출시         (2025-09-26)
#   `라이필` 이 농심의 건기식 브랜드다. 뒤엣것은 주어가 그냥 '농심' 이라
#   주어 화이트리스트로는 못 막는다(풀무원 `아미오` 와 같은 모양).
#   `base.is_nonfood()` 도 모른다 — 먹는 것이긴 하다.
#   ⚠️ `콜라겐` 한 단어로 줄이지 마라 — 콜라겐을 넣은 식품이 실재한다.
_NOT_OUR_LINE = ("라이필", "더마콜라겐", "건강기능식품", "건기식")

# 따옴표와 동사 **사이**에 있으면 따옴표 안이 상품명이 아니라는 신호(maker_orion).
# `손잡고` 는 농심 실측 추가분이다 — `편의점 4사와 손잡고 포테토칩 4종 동시 출시`
# 는 편의점별로 서로 다른 4개라 하나로 특정할 수 없다(아는 손실).
_BETWEEN = ("협업", "컬래버", "콜라보", "브랜드", "메뉴", "에디션", "테마",
            "전용 앱", "손잡고")
# '출시가 아니라 성과' 기사를 거르는 꼬리말. 동사 **뒤**에서만 본다(maker_orion).
# ⚠️ `오픈` 은 `_SKIP`(제목 전체)이 아니라 여기 둔다 — 농심은 베이커리 스낵
#    라인(`빵부장`)이 있어서 `오픈샌드위치…` 류 상품명이 물릴 자리다. 실측
#    40건에서 `_SKIP` 의 `오픈` 이 거르던 기사는 0건이었다(팝업 기사는 `팝업`
#    이 이미 잡는다). 신세계푸드에도 같은 이유로 같은 조치를 했다.
_TAIL = ("돌파", "만에", "만인", "판매", "인기", "완판", "누적", "기록", "연다",
         "쏜다", "오픈")


def _pick(title: str) -> str:
    """'농심, 모디슈머 레시피 담은 스낵 ‘너구링’ 출시' → '너구링'.

    따옴표가 없는 제목도 있다('농심, 생생신툼바떡볶이면 출시'). 그때는
    주어를 뗀 머리 전체를 상품명으로 본다. 상품을 특정 못 하면 빈 문자열.
    """
    t = " ".join(title.split())
    if any(w in t for w in _SKIP) or any(w in t for w in _NOT_OUR_LINE):
        return ""
    verb = None
    for m in _VERB.finditer(t):
        verb = m
    if not verb:
        return ""
    if any(w in t[verb.end():] for w in _TAIL):
        return ""
    head = _SUBJECT.sub("", t[:verb.start()])
    q = list(_QUOTED.finditer(head))
    if q and any(w in head[q[-1].end():] for w in _BETWEEN):
        return ""
    if not q and any(w in head for w in _BETWEEN):
        return ""
    seg = head[q[0].start():] if q else head
    name = _QUOTE_CHARS.sub("", seg)
    name = _NEW_TAIL.sub("", _COUNT_TAIL.sub("", name.strip())).strip(" ,·∙!…")
    # 따옴표 없는 제목에서 통째로 잡은 머리는 수식어가 길게 붙어 있을 수 있다.
    if not (2 <= len(name) <= 40):
        return ""
    return name


def _date(s: str) -> str:
    """'2026/10/01' → '2026-10-01'. 월·일 범위를 검증한다."""
    m = re.match(r"^\s*(20\d{2})[/.-](\d{1,2})[/.-](\d{1,2})\s*$", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _rows(html: str) -> list[tuple]:
    """목록 HTML → (분류, 날짜, 제목, href, 이미지) 목록."""
    out = []
    for art in HTMLParser(html).css("article.news-card"):
        tit = art.css_first("h3.news-card__title")
        if not tit:
            continue
        dt = art.css_first("time.news-card__date")
        a = art.css_first("a.news-card__link")
        img = art.css_first("img")
        href = (a.attributes.get("href") or "").strip() if a else ""
        src = (img.attributes.get("src") or "").strip() if img else ""
        out.append((art.attributes.get("data-category") or "",
                    _date(dt.text(strip=True) if dt else ""),
                    " ".join(tit.text().split()),
                    href,
                    src if src.startswith("http") else (SITE + src if src.startswith("/") else "")))
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    with base.client() as c:
        # ⚠️ 요청은 한 번뿐이다. page=N 이 누적이라 반복문은 같은 걸 다시 받는다.
        r = base.retry(lambda: c.get(LIST, params={"category": "all", "page": PAGE}))
        r.raise_for_status()
        rows = _rows(r.text)

    # 셀렉터가 바뀌면 조용히 0건이 된다. 하루 한 건꼴로 쌓이는 뉴스룸이라
    # '목록 0행'은 고장이다.
    if not rows:
        raise ValueError(
            f"농심 뉴스룸 목록이 비었다. {r.url} → {len(r.content)}B — "
            f"목록 셀렉터(article.news-card / h3.news-card__title / "
            f"time.news-card__date)가 바뀌었는지 확인하라")

    # ── 신제품 분류 비율 가드 ──────────────────────────────────────
    # **분류는 존재가 아니라 비율로 믿어야 한다.** 이 레포가 같은 종류로 세 번 데였다:
    #   설빙     `span.flag` 에 시그니처 배지가 섞여 와서 2013년부터 팔던
    #            인절미설빙이 신상이 됐다(14 → 4건)
    #   퀴즈노스  NEW 가 66건 **전부**에 붙어 있었다 = 신호가 아니라 장식
    #   컴포즈    배지가 썸네일 **그림 안에 합성**돼 HTML 엔 0건(0 → 16건)
    # 2026-10-03 실측: 108건 중 product 20건 = **18.5%**(국내 38% · 글로벌 35% ·
    # ESG 8%). 0% 도 과반도 아니다.
    fresh = [x for x in rows if x[0] == NEW_CAT]
    if not fresh:
        raise ValueError(
            f"농심 뉴스룸 {len(rows)}건 중 '{NEW_CAT}' 분류가 0건이다. "
            f"읽힌 분류={sorted({x[0] for x in rows})} — data-category 값이나 "
            f"분류 체계가 바뀌었는지 확인하라(컴포즈 선례)")
    if len(fresh) > len(rows) * MAX_NEW_RATIO:
        raise ValueError(
            f"농심 뉴스룸 {len(rows)}건 중 '{NEW_CAT}' 분류가 {len(fresh)}건"
            f"({len(fresh) / len(rows):.0%})다. 과반이 신제품일 수는 없다 — "
            f"분류가 장식으로 바뀌었는지 확인하라(퀴즈노스 선례: 66건 전부)")

    for _cat, released, title, href, img in fresh:
        if released and released < floor:
            continue
        name = _pick(title)
        if not name:
            continue
        it = Item(
            brand=BRAND,
            name=name,
            desc=_SUBJECT.sub("", title),
            image=img,
            # 엄밀히는 보도일이다. 본문의 '오는 N월 N일 출시' 보다 며칠 이르다 —
            # 즉 신상 창을 **놓치는 쪽으로만** 틀린다(위 docstring §날짜).
            released_at=released,
            # 브랜드가 기사에 직접 '신제품' 분류를 붙였고 제목이 '출시'라고 한다.
            is_new=True,
            # 목록의 href 가 `view?id=212&…` 꼴 상대주소다.
            url=(f"{SITE}/newsroom/news/{href}" if href.startswith("view?")
                 else (href or LIST)),
        )
        if it.key not in seen:
            seen.add(it.key)
            items.append(it)
    return items
