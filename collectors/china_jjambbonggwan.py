"""짬뽕관 — 공지사항 게시판에서 신메뉴와 출시일을 뽑는다.

공정위 `중식` 업종 가맹점 수 **15위**(62개, 2024년 말). (주)짬뽕관.

공식 도메인은 **한글도메인 `짬뽕관.com`**(퓨니코드 `xn--zb0bq16amwh.com`)이다.
검색으로는 `jjkk.winko.net` 이 먼저 뜨는데 같은 IP(203.245.24.50)의 **구 주소**이고
https 가 안 열린다(443 연결 실패). 한글도메인 쪽은 https 가 멀쩡하니 그쪽을 쓴다.
`www.` 를 붙인 쪽이 사이트가 자기 링크에 쓰는 표기라 그대로 따랐다.

이 브랜드는 **중식 상위권에서 드물게 날짜가 붙은 신메뉴 글을 낸다.** 탕화쿵푸·
라홍방처럼 보도자료형이지만 사정이 더 낫다 — 자사 공지사항이라 매장 오픈·수상
기사에 섞인 남의 기사가 아니고, 날짜가 `2025-11-04` 처럼 **연도까지 온전**하다
(그누보드처럼 월·일만 주지 않는다).

수집 경로. 2026-10-02 실측:
  - 공지사항 목록 `/notice`, 2페이지 `/notice?page=2`. 쿠키·토큰 없이 SSR 로 열린다.
    1페이지 15건 + 2페이지 7건 = **전체 22건**(3페이지는 0건). 2022-11 이후 전부다.
  - 🔴 **목록 한 장에 필요한 게 다 들어 있다.** 한 줄이 `<li>` 이고
    `strong.title`(제목, 안 잘림) / `p.content`(**본문 전문**) / `span.date`(날짜) /
    `img`(썸네일) / `a[href]`(상세 주소)다. 탕화쿵푸·라홍방은 제목이 잘리거나
    날짜가 월·일뿐이라 상세를 일일이 받아야 했는데 **여기는 상세를 안 받아도 된다.**
    요청이 2회로 끝나서 상세 22번을 더 때리지 않는다.
  - 보도자료 게시판 `/press` 도 있는데 **상세 링크가 없는 목록 전용 보드**다
    (`/press/N` 같은 주소가 아예 안 나온다). 내용은 공지사항과 겹치고 신메뉴 글은
    `/notice` 쪽이 먼저·더 자세하다. 그래서 `/press` 는 안 본다.

신제품 판정 근거는 **글 자체**다. 브랜드가 자기 공지에 '신메뉴 … 출시' 라고 쓴
글이라 is_new=True 로 둔다(탕화쿵푸·라홍방·GS25 와 같은 근거).

상품명은 제목·본문을 **교차검증**해서만 뽑는다(탕화쿵푸·라홍방과 같은 규칙).
  ① 본문에서 따옴표로 인용된 이름을 모으고
  ② 그중 **제목에도 글자 그대로 있는 것만** 채택한다.
⚠️ 이 사이트는 따옴표를 **홑·겹 섞어 쓴다.** 실측:
     /notice/20 본문 `“돌판간짬뽕”이 출시되었습니다`   ← 겹따옴표
     /notice/17 본문 `'초계냉짬뽕' 과 '초계비빔짬뽕'`   ← 홑따옴표
   탕화쿵푸·라홍방은 홑따옴표만 봤는데 그 규칙을 그대로 가져오면 돌판간짬뽕을
   통째로 놓친다. 그래서 _QUOTED 가 홑·겹을 다 받는다.
⚠️ **행사 세트명이 따옴표 안에 들어온다.** /notice/20 본문에
   `‘돌판간짬뽕 + 연태고량주 세트’ 주문 시 5,000원 할인` 이 있다. 제목에는 없어서
   교차검증으로 떨어지지만, `+`·`·` 묶음 기호와 '세트' 로 한 번 더 막는다
   (라홍방의 협업 표기 방어와 같은 취지).
⚠️ **브랜드명이 따옴표 안에 들어온다.** `'짬뽕관' 청결한 오픈주방으로 …` 처럼
   제목에도 본문에도 브랜드명이 들어가는 글이 있어 교차검증을 그대로 통과한다.
   라홍방에서 실제로 터진 사고라 _NOT_PRODUCT 에 브랜드명을 넣어 막는다.

판정이 맞는지 **메뉴 페이지로 교차확인했다.** `/menu` 의 '짬뽕관 메뉴' 16종에
아래 글에서 뽑은 이름이 그대로 들어 있다 — 돌판간짬뽕·초계냉짬뽕·초계비빔짬뽕·
마라짬뽕·해물쟁반짜장. 즉 뽑힌 건 실재하는 상품이다(오집 0건).
그리고 `/menu` 의 '짬뽕관 신메뉴' 칸에는 **NEW 가 딱 1건, 돌판간짬뽕**이다.
공지사항이 준 가장 최근 신메뉴와 정확히 일치한다.

   ⚠️ 그런데도 **메뉴 페이지는 수집원으로 안 쓴다.** 그쪽 NEW 배지에는 날짜가
   없어서, 그걸 담으면 2025-11 에 나온 돌판간짬뽕이 `first_seen`=오늘로 떨어져
   '오늘의 신상'으로 올라간다(소림마라 docstring 이 경고하는 그 사고다).
   날짜를 주는 공지사항 하나만 읽고, 메뉴 페이지는 검증용으로만 썼다.

🔴 **이 브랜드는 신메뉴를 1년에 한두 번 낸다. 0건이 흔하다.**
   22건 중 상품 글은 5건이다 — 돌판간짬뽕(2025-11-04), 초계냉·초계비빔짬뽕
   (2025-06-18), 마라짬뽕·마라볶음면(2024-01-05), 해물쟁반짜장(2023-07-11),
   황태·차슈짬뽕(2022-12-02). 나머지 17건은 수상·매장 오픈·방송 출연·은행 협약이다.
   그래서 탕화쿵푸·라홍방의 `DAYS=300` 을 그대로 쓰면 **수집 0건**이다(가장 최근
   상품 글이 332일 전이다). 게시판이 22건짜리 2페이지뿐이라 더 봐도 비용이 0 이므로
   `DAYS=540` 으로 넓혀 최근 두 건의 상품 글까지 닿게 했다.
   ⚠️ 그래도 **화면에는 0건이 오른다.** 전부 60일 창 밖이다. 그게 정상이고 의도다
   (소림마라와 같다). 고장이면 `fetch()` 가 예외를 던진다.

robots: `www.xn--zb0bq16amwh.com/robots.txt` → 200, text/plain. 본문이 두 줄뿐이다 —
        `User-agent: *` / `Allow: /`. 전면 허용이다.
약관: 푸터에 개인정보처리방침·이메일무단수집거부만 있고 **이용약관 페이지가 없다**
      (`#!` 로 뜨는 레이어다). 수집·복제를 금지하는 문구는 찾지 못했다.
"""
import re
import time
from datetime import date, timedelta

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "짬뽕관"
# 한글도메인 `짬뽕관.com` 의 퓨니코드. 사이트가 자기 링크에 쓰는 표기 그대로다.
SITE = "https://www.xn--zb0bq16amwh.com"
NOTICE = SITE + "/notice"
MAX_PAGES = 2        # 2026-10-02 실측 22건(15+7). 3페이지는 0건이다
DAYS = 540           # 신메뉴가 연 1~2건이라 300일이면 0건이다(docstring 참고)
DELAY = 2.2

# 상품 글인가. 이 말이 없으면 이름을 뽑지 않는다.
_LAUNCH = re.compile(r"(출시|선봬|선보|론칭|신메뉴|신제품)")

# 상품 글이 아닌데 위 동사를 쓸 자리들. 실측 제목 22건에는 아직 충돌이 없지만
# (전부 _LAUNCH 로 갈린다) 수상 글이 '수상 기념 신메뉴' 식으로 쓰이면 걸린다.
_SKIP = ("수상", "선정", "오픈", "OPEN", "인증", "체결", "박람회",
         "인터뷰", "성료", "미팅", "설립")

# 홑·겹따옴표를 다 받는다. 이 사이트는 글마다 섞어 쓴다(docstring 참고).
_QUOTE = "‘’'“”\"`"
_QUOTED = re.compile(f"[{_QUOTE}]([^{_QUOTE}\n]{{2,30}})[{_QUOTE}]")

# 따옴표 안이 상품이 아닌 것들. '점' 이 지점명을 잡는다.
#
# 🔴 **'세트' 를 뺐다.** base.Item docstring 이 명시적으로 금지한다 —
#    "세트·콤보는 여기 쓰지 마라. collect.drop_sets() 가 이름으로 거른다.
#     어댑터마다 세트 기준이 달라져 신메뉴 세트가 잘렸다."
#    행사 묶음('돌판간짬뽕 + 연태고량주 세트')은 바로 아래 '+' 기호 필터가
#    이미 잡으므로 '세트' 를 따로 둘 이유가 없다.
_NOT_PRODUCT = ("짬뽕관", "브랜드", "프랜차이즈", "어워즈", "대상",
                "이벤트", "캠페인", "협약", "박람회", "매장", "주방")

# 지점명. `"점"` 을 _NOT_PRODUCT 에 넣으면 부분일치라 '점보마라탕'·'점보만두'
# 같은 실존 작명을 죽인다(라화쿵부가 실제로 '3KG 점보마라탕' 을 판다).
# 지점명은 항상 '…점' 으로 **끝나므로** 끝자리로만 본다.
_BRANCH = re.compile(r"점$")


def _text(node) -> str:
    return " ".join(node.text().split()) if node else ""


def _date(s: str) -> str:
    """'2025-11-04' → 같은 문자열. 월·일 범위를 검증한다."""
    m = re.search(r"(20\d{2})-(\d{1,2})-(\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _rows(html: str) -> list:
    """목록 한 페이지 → [(날짜, 제목, 본문, 이미지, 주소)].

    목록이 본문 전문을 들고 있어서 상세를 안 받는다(docstring 참고).
    """
    out = []
    for li in HTMLParser(html).css("li"):
        title = _text(li.css_first("strong.title"))
        when = _date(_text(li.css_first("span.date")))
        if not title or not when:
            continue
        body = _text(li.css_first("p.content"))
        a = li.css_first("a")
        url = (a.attributes.get("href") or "") if a else ""
        img = li.css_first("img")
        src = (img.attributes.get("src") or "") if img else ""
        out.append((when, title, body, src if src.startswith("https://") else "", url))
    return out


def _names(title: str, body: str) -> list:
    """제목과 본문을 교차검증해 상품명을 뽑는다. 못 고르면 빈 목록.

    본문이 따옴표로 부른 이름 중 **제목에도 글자 그대로 있는 것**만 남긴다.
    한쪽에만 있는 건 행사 세트명·수상명이라 버린다(docstring 참고).
    """
    t = " ".join(title.split())
    if any(w in t for w in _SKIP) or not _LAUNCH.search(t):
        return []
    flat = t.replace(" ", "")
    out, seen = [], set()
    for m in _QUOTED.finditer(body):
        name = m.group(1).strip(" ,·∙")
        # 묶음 기호가 들어가면 상품 하나가 아니다 — '돌판간짬뽕 + 연태고량주 세트'.
        if len(name) < 2 or any(c in name for c in "+·∙&?"):
            continue
        if any(w in name for w in _NOT_PRODUCT) or _BRANCH.search(name):
            continue
        if name.replace(" ", "") not in flat or name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out


def fetch() -> list[Item]:
    floor = (date.today() - timedelta(days=DAYS)).isoformat()
    rows = []
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            params = {"page": page} if page > 1 else None
            r = base.retry(lambda: c.get(NOTICE, params=params))
            r.raise_for_status()
            got = _rows(r.text)
            # 1페이지가 비면 마크업이 바뀐 것이다. 조용히 빈 목록을 돌려주지 않는다.
            if not got:
                if page == 1:
                    raise RuntimeError(f"{NOTICE} 1페이지에서 글을 못 찾았다. 마크업을 확인해라")
                break
            rows += got

    # ⚠️ 목록이 날짜순이 아니다. 2페이지 실측 순서가 2023-10-19 → 2023-07-26 →
    #    2023-07-11 → 2022-12-02 → 2023-02-20 이다. 오래된 걸 만났다고 멈추면
    #    뒤에 오는 최신 글을 잃는다. 끊지 말고 전부 받아 날짜로 거른다.
    #    오래된 쪽부터 담아 같은 이름이 겹치면 첫 출시일이 남게 한다(라홍방 선례).
    rows.sort(key=lambda x: x[0])

    items: list[Item] = []
    seen = set()
    for when, title, body, img, url in rows:
        if when < floor:
            continue
        for name in _names(title, body):
            it = Item(brand=BRAND, name=name, image=img,
                      released_at=when, is_new=True, url=url or NOTICE)
            if it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)
    return items
