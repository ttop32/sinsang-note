"""사조대림 — 사조그룹 '신제품' 전용 페이지에서 신제품과 출시일을 뽑는다.

보도자료 제목을 파싱하는 오리온·삼양 계보가 **아니다.** 사조는 그룹 사이트에
**신제품 전용 게시판**을 따로 두고 제목 형식까지 통일해 둬서, 팔도의 `신제품`
배지와 같은 '브랜드가 직접 켜고 끄는 신호' 로 읽는 쪽이 정확하다.
(보도자료 역필터는 쓸 데가 없다 — 게시판 자체가 신제품만 담는다.)

2차 조사가 "사조대림 — `www` 가 DNS 로는 풀리는데 80·443 둘 다 타임아웃. 대체
도메인을 추측하지 않았다" 로 남긴 구멍이다. 3차가 실측으로 메웠다:
**계열사 도메인(`sajodaerim.co.kr`)이 아니라 그룹 사이트 `www.sajo.co.kr` 이 정답**이고,
거기가 계열사 신제품을 전부 모아 준다. (notes/CANDIDATES-MAKER.md §⑧)

수집 경로. 2026-10-02 실측:
  GET https://www.sajo.co.kr/2026/product/new_product.asp?page=1   200 / 23,725B
    <div class="col_wrap">
     <div>
      <a class="img_area" href="./new_product_view.asp?idx=3800&page=1&searchstr=">
        <img src='https://www.sajo.co.kr/upload_data/board/thumbnail/20260802_TOP.png'></a>
      <div class="img_area_s"><img src="/upload_data/board/thumbnail/nt_ci_dr.png" alt="사조대림"></div>
      <a href="./new_product_view.asp?idx=3800&searchstr=">
        <strong class="img_tit">[사조대림] ‘해표 더 고소한 김’ 2종 출시</strong></a>
      <p class="date">2026.08.03</p>
     </div>
  페이지당 6건, `?page=N`. 2026-10-02 현재 **총 7건**(2페이지).
  썸네일이 **절대 URL(https)** 로 와서 그대로 쓸 수 있다.

**제목 형식이 통일돼 있다 — 이게 이 어댑터의 전부다.**
    [계열사] ‘상품명’ N종 출시          ← 따옴표가 있는 쪽
    [사조대림] 해표 순창궁 태양초 고추장 3종 출시   ← 따옴표가 없기도 하다
따옴표가 있으면 그 안을, 없으면 `[계열사]` 와 동사 사이를 상품명으로 본다.

**⚠️⚠️ 계열사는 `[...]` 제목 접두로 가른다. `img_area_s` 의 `alt` 를 믿지 마라.**
3차 조사 문서가 "계열사를 `alt` 로도 중복 제공한다" 고 적었는데 **틀렸다.**
2026-10-02 실측에서 **첫 행이 어긋난다**:
    제목 `[사조펫] '벤티 케어 오메가3' 신제품 출시`  ↔  alt `사조동아원`
CI 이미지가 밀려 붙은 것으로 보인다. alt 를 믿었으면 **펫푸드가 식품으로 올라간다.**
제목 접두는 7건 전부 정확했다.

**쓰는 계열사 (`_AFFILIATES`).** 그룹에 8개가 섞여 있다:
    사조대림 · 사조오양 · 사조씨푸드 ← ✅ 소비자 식품(어묵·수산가공·햄·간편식)
    사조산업 · 사조원                ← ✅ 축산·수산 원물
    사조동아원                       ← ❌ 제분. B2B 밀가루
    사조푸디스트                     ← ❌ 급식·휴게소. 편의점 상품이 아니다
    사조펫                           ← ❌ 펫푸드. 사람이 먹는 게 아니다
브랜드 이름은 **'사조대림'** 하나로 등록한다. 신제품 게시판 7건 중 6건이
사조대림이고, 나머지 계열사는 붙었다 말았다 해서 따로 칸을 내면 대부분 0건이 된다.

**거르는 것.**
  `[사조대림] ‘한알레시피’ 4종 **리뉴얼** 출시!`   ← 신제품이 아니다
  `[사조펫] …`                                    ← 펫푸드
  `… 선물세트 / 기획전 / 한정 …`                   ← 상품이 아니거나 신상이 아니다

**일괄 등록 흔적 — 없다.** 7건 날짜가 전부 다르다
(09.01 · 08.03 · 07.27 · 07.20 · 07.13 · 07.01 · 06.23). 썸네일 파일명의
`20260802` 도 보도일 08.03 과 하루 차로 맞는다 — 다만 **날짜는 `p.date` 를 쓴다**
(크라운 사례: 파일명 날짜는 재업로드로 덮인다).

**SAJO 뉴스(`/2026/product/sajo_news.asp`, 총 56건)는 쓰지 않는다.**
갱신은 더 빠르지만(최신 09.17 vs 신제품 09.01) CSR·안전점검·추석 선물세트·
휴게소 신메뉴가 섞여 있어 역필터를 또 얹어야 한다. 신제품 전용 게시판이 이미
있는데 그걸 두고 뉴스를 긁는 건 이 프로젝트가 경계하는 쪽이다. 신제품 게시판이
말라붙으면 그때 다시 본다.

robots: https://www.sajo.co.kr/robots.txt → ⚠️ **판정 불가.** 200 / 3,861B 인데
        `<title>서비스 오류 안내</title>` HTML 이고, 없는 경로(`/zzz-nope-12345`)에도
        **바이트 단위로 같은 응답**을 준다. robots.txt 가 없고 모든 미지정 경로에
        공용 오류 셸을 주는 유형이다(해태 ht.co.kr 과 같다).
약관:   확인하지 않았다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "사조대림"
SITE = "https://www.sajo.co.kr"
LIST = SITE + "/2026/product/new_product.asp"
VIEW = SITE + "/2026/product/new_product_view.asp"
MAX_PAGES = 4        # 한 페이지 6건. 2026-10-02 현재 총 7건(2페이지). 상한.
DELAY = 2.2

# 소비자 식품을 내는 계열사만. 제목의 `[...]` 접두로 가른다(alt 는 못 믿는다).
_AFFILIATES = {"사조대림", "사조오양", "사조씨푸드", "사조산업", "사조원"}

_PREFIX = re.compile(r"^\s*\[([^\]]{2,12})\]\s*")
_QUOTED = re.compile(r"[‘'`]([^’'`]{2,40})[’'`]")
_QUOTE_CHARS = re.compile(r"[‘’'`“”\"]")
_VERB = re.compile(r"(출시|선봬|선보여|선보인다|론칭|런칭)")
# 상품명 뒤에 붙는 수량 표기. `2종`·`3종 출시` 의 그 부분이다.
_COUNT_TAIL = re.compile(r"\s*\d+\s*종\s*$")
_NEW_TAIL = re.compile(r"\s*신제품\s*$")

# 신제품 게시판이지만 신상이 아닌 것들이 섞인다.
# ⚠️ 2026-10-03 검수에서 `한정` → `한정판` 으로 **좁혔다.** 두 글자 `한정` 은
#    **`한정식` 을 문다**(`[사조대림] ‘한정식 도시락’ 출시` 로 실증). 사조는
#    어묵·햄·간편식을 내는 한식 제조사라 실제로 물릴 자리다. 이 레포가
#    `카스`→`카스테라` 28건으로 데인 것과 같은 모양이다. 다른 어댑터
#    (maker_orion·maker_cj 의 `_REPACK_NAME`)도 전부 `한정판` 을 쓴다 —
#    그쪽 표기에 맞췄다. 실측 7건에서 `한정` 으로 걸리던 기사는 0건이다.
_SKIP = ("리뉴얼", "선물세트", "기획세트", "기획전", "한정판", "프로모션",
         "이벤트", "캠페인", "에디션")


def _pick(title: str) -> str:
    """'[사조대림] ‘해표 더 고소한 김’ 2종 출시' → '해표 더 고소한 김'.

    따옴표가 없는 제목도 있다('[사조대림] 해표 순창궁 태양초 고추장 3종 출시').
    그때는 `[계열사]` 와 동사 사이를 상품명으로 본다.
    """
    t = " ".join(title.split())
    body = _PREFIX.sub("", t)
    if any(w in body for w in _SKIP):
        return ""
    verb = None
    for m in _VERB.finditer(body):
        verb = m
    if not verb:
        return ""
    head = body[:verb.start()]
    # 따옴표 **안**만 쓰면 수식어가 달린 상품명이 깎인다 —
    # `‘하우스&펍’ 소시지 3종 출시` 가 '하우스&펍'(브랜드)로 줄어든다.
    # 그래서 **첫 따옴표부터 동사 앞까지**를 통째로 잡고 따옴표 기호만 턴다.
    # 따옴표가 없으면 머리 전체를 쓴다(`해표 순창궁 태양초 고추장 3종 출시`).
    q = list(_QUOTED.finditer(head))
    seg = head[q[0].start():] if q else head
    name = _QUOTE_CHARS.sub("", seg)
    name = _NEW_TAIL.sub("", _COUNT_TAIL.sub("", name.strip())).strip(" ,·∙!")
    # 따옴표 없는 제목에서 통째로 잡은 머리는 수식어가 길게 붙어 있을 수 있다.
    # 2~40자 밖이면 상품을 특정 못 한 것으로 본다.
    if not (2 <= len(name) <= 40):
        return ""
    return name


def _affiliate(title: str) -> str:
    """제목 접두의 계열사명. 없으면 빈 문자열."""
    m = _PREFIX.match(" ".join(title.split()))
    return m.group(1).strip() if m else ""


def _date(s: str) -> str:
    """'2026.08.03' → '2026-08-03'. 월·일 범위를 검증한다."""
    m = re.match(r"^\s*(20\d{2})[-.](\d{1,2})[-.](\d{1,2})\s*$", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _rows(html: str) -> list[tuple]:
    """목록 HTML → (날짜, 제목, idx, 이미지) 목록."""
    out = []
    for div in HTMLParser(html).css(".col_wrap > div"):
        tit = div.css_first("strong.img_tit")
        if not tit:
            continue
        dt = div.css_first("p.date")
        a = div.css_first("a.img_area")
        img = a.css_first("img") if a else None
        src = (img.attributes.get("src") or "").strip() if img else ""
        m = re.search(r"idx=(\d+)", (a.attributes.get("href") or "") if a else "")
        out.append((_date(dt.text(strip=True) if dt else ""),
                    " ".join(tit.text().split()),
                    m.group(1) if m else "",
                    src if src.startswith("http") else (SITE + src if src.startswith("/") else "")))
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    affiliates: set = set()      # 아래 가드의 진단용. 실제로 읽힌 계열사들.
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            r = base.retry(lambda: c.get(LIST, params={"page": page}))
            r.raise_for_status()
            rows = _rows(r.text)

            # 셀렉터가 바뀌면 조용히 0건이 되는 게 제일 나쁘다.
            if page == 1 and not rows:
                raise ValueError(
                    f"사조 신제품 1페이지가 비었다. {r.url} → {len(r.content)}B — "
                    f"목록 셀렉터(.col_wrap > div / strong.img_tit / p.date)가 "
                    f"바뀌었는지 확인하라")
            if not rows:
                break

            for released, title, idx, img in rows:
                aff = _affiliate(title)
                affiliates.add(aff)
                if aff not in _AFFILIATES:
                    continue
                name = _pick(title)
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=_PREFIX.sub("", " ".join(title.split())),
                    image=img,
                    released_at=released,
                    # 신제품 전용 게시판이다. 브랜드가 직접 켜고 끄는 신호다.
                    is_new=True,
                    url=f"{VIEW}?idx={idx}" if idx else LIST,
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

            if len(rows) < 6:        # 마지막 페이지
                break

    # 제목 접두가 사라지면 계열사를 못 가르게 되고, 그러면 전건이 조용히
    # 떨어져 0건이 된다. 펫푸드가 식품으로 올라가는 반대 사고보다 낫지만
    # 둘 다 조용하면 안 된다 — 터뜨린다.
    if not items and not (affiliates & _AFFILIATES):
        raise ValueError(
            f"사조 신제품에서 쓸 수 있는 계열사가 하나도 없다. "
            f"읽힌 계열사={sorted(affiliates)} — 제목의 '[계열사]' 접두 형식이 "
            f"바뀌었는지 확인하라")
    return items
