"""짬뽕10101 — 홍보자료 게시판에서 신메뉴와 출시일을 뽑는다.

공정위 `중식` 업종 가맹점 수 **33위**(29개, 2024년 말). (주)고구려푸드.
사이트·간판은 `고구려짬뽕10101` 로 쓰지만 공정위 등록 브랜드명은 `짬뽕10101` 이다.
BRANDS 에는 공정위 이름으로 올린다(등록표가 순위표와 같은 축이어야 한다).

**메뉴 소개 페이지는 쓸 수 없다.** `?c=186`(고구려짬뽕10101)과 `?c=191`
(고구려짬뽕10101MINI)에 상품이 이름+설명으로 나란히 있지만 2026-10-02 실측으로
**날짜도 NEW 배지도 하나도 없다.** 긁으면 옛날짬뽕·삼선짬뽕·냉짬뽕·차돌짬뽕…이
전부 '신상' 으로 올라간다. 그래서 메뉴 페이지는 안 본다.

남은 경로는 **홍보자료 게시판** 하나뿐이고, 이건 탕화쿵푸마라탕과 같은 종류의
소스다(보도자료형). 그 어댑터의 규칙을 가져오되 **교차검증 방향을 뒤집는다**
— 아래 §2 참고.

§1. 수집 경로. 2026-10-02 실측:
  - 홍보자료 목록 `/?c=184&gp=N`. 쿠키·토큰 없이 SSR 로 열린다. UTF-8 이다
    (탕화쿵푸와 달리 EUC-KR 이 아니다).
  - 목록 한 칸이 `.bbs-multi-info` 이고 그 안의
      `a[title]`           ← **온전한 제목**
      `.bbs-multi-tit`     ← 같은 제목(공백 범벅)
      `.bbs-multi-desc`    ← 본문 앞머리 300자쯤에서 `말...` 로 잘림
      `.bbs-multi-date`    ← `2023.09.04`
    로 구성된다. ⚠️ **제목이 `title` 속성에 온전히 들어 있다.** 탕화쿵푸는
    목록 제목이 30자에서 잘려 상세를 받아야 했는데 여기는 그럴 필요가 없다.
    그래도 상세를 받는다 — 교차검증에 쓸 **온전한 본문**이 목록엔 없다.
  - 상세는 `/?c=184&gbn=view&ix=NN`. `.bbs-view-tit`(제목) /
    `#bbsContents`(본문·기사 이미지) 다.
  - 페이징은 `gp` 다. `gp=2` 는 글이 **0건**으로 돌아오므로 빈 페이지에서 멈춘다.

§2. 상품명은 제목과 본문을 교차검증해서만 뽑는다. **방향이 탕화쿵푸의 반대다.**
  탕화쿵푸는 본문이 ‘…’ 로 상품을 부르고 제목은 안 불렀다. 여기는 거꾸로다 —
    제목 `… 일반 짬뽕과 불짬뽕 사이의 중간 매운맛 ‘고추 짬뽕’ 출시`
    본문 `… 신메뉴 고추짬뽕을 출시한다고 밝혔다` (따옴표 없이 맨 글자)
  그래서
    ① **제목**에서 ‘…’ 로 인용된 이름을 모으고
    ② 그중 **본문에도 공백 무시하고 들어 있는 것만** 상품으로 채택한다.
  (‘고추 짬뽕’ → 공백 턴 `고추짬뽕` 이 본문에 있다 → 채택.)
  한쪽에만 있는 건 버린다. 실측상 제목 인용에는 **브랜드명**이 섞인다 —
  `‘고구려짬뽕10101MINI’ 가맹영업 시작` 이 그것이고, 상품이 아니다.
  그래서 `10101`·`MINI` 가 든 인용은 _NOT_PRODUCT 로 떨군다.

§3. 🔴 **이 게시판은 멈춰 있다. 반드시 읽어라.**
   홍보자료 전체가 **3건**이고 마지막 글이 **2023-10-24** 다. 3건의 내역은
     2023-09-04  ‘고추 짬뽕’ 출시            ← 유일한 상품 기사
     2023-09-04  고구려짬뽕10101MINI 가맹영업 시작  ← 브랜드 런칭
     2023-10-24  고구려짬뽕10101MINI 가맹점주 모집!  ← 모집 공고
   즉 **이 어댑터가 지금 뽑는 건 3년 묵은 1건**이고, released_at 이 2023-09-04
   이라 60일 창 밖이다. **화면에는 0건이 오른다.** 그게 정상이고 의도다
   (소림마라 어댑터와 같은 사정). "건수가 0이니 고장났다"고 판단하지 마라 —
   고장이면 `fetch()` 가 예외를 던진다.

   그럼에도 만든 이유는 **신호의 종류가 진짜**이기 때문이다. 브랜드가 직접
   '신메뉴 … 출시한다' 고 썼고, 상품명이 제목·본문 양쪽에서 확인되며, 날짜가
   게시판에서 나온다. 중식 26~40위 15개 브랜드 중 이런 자리는 여기 하나뿐이다
   (나머지 14곳은 메뉴 카탈로그이거나 창업모집 랜딩이거나 도메인이 죽었다).
   본사가 글을 다시 올리면 그날부터 자동으로 잡힌다.

§4. 날짜는 게시판 등록일이라 `released_at` 에 넣는다. 기사가 '출시한다' 고
   말한 날이지 사진 올린 날이 아니다(소림마라의 `uploaded_at` 과 다른 자리).
   is_new 는 True 다 — 브랜드가 '신메뉴' 라고 직접 말한 글이라서다
   (탕화쿵푸·GS25·오뚜기와 같은 근거).

robots: `goguryeofood.com/robots.txt` → 200, text/plain. 본문이 두 줄뿐이다 —
        `User-agent: *` / `Allow:/`. 전면 허용이다.
약관: 푸터에도 내비에도 **이용약관 페이지가 없다.** 수집·복제를 금지하는 문구는
      찾지 못했다(소림마라·탕화쿵푸와 같은 칸).
TLS: 인증서 SAN 이 `goguryeofood.com, www.goguryeofood.com` 으로 브랜드 자기
     것이다(주차 도메인이 아니다). https 로 받는다.
⚠️ 기사 이미지는 본사 서버의 `/upload/184/...` 다. 언론사 CDN 이 아니라
   브랜드 서버라 탕화쿵푸보다 안정적이다. 그래도 https 인 것만 담는다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "짬뽕10101"
SITE = "https://goguryeofood.com"
BOARD = "184"        # 홍보자료. 184 는 내비의 '홍보자료' 링크에서 그대로 나온 번호다
MAX_PAGES = 5        # gp=2 가 이미 0건이다. 글이 늘어날 자리만 열어둔다
DELAY = 2.5          # robots 는 전면 허용이지만 간격은 길게 잡는다(탕화쿵푸 선례)

# 상품 기사인가. 이 말이 제목에 없으면 상세를 받지 않는다.
# '런칭' 은 일부러 뺐다 — 이 사이트에서 런칭은 **브랜드** 런칭을 가리킨다
# (고구려짬뽕10101MINI). 상품 출시는 '출시' 로만 쓴다.
_LAUNCH = re.compile(r"(출시|선봬|선보|신메뉴)")

# 위 동사를 쓰지만 상품 기사가 아닌 것들. 실측으로 걸린 말만 넣었다.
_SKIP = ("가맹영업", "가맹점주", "모집", "창업설명회", "박람회", "채용", "수상")

# 제목·본문의 홑따옴표. 한국 기사는 ‘ ’ 와 ' 를 섞어 쓴다.
_QUOTED = re.compile(r"[‘'`]([^’'`\n]{2,30})[’'`]")

# 따옴표 안이 상품이 아닌 것들. 이 사이트의 제목 인용에는 브랜드명이 섞인다.
#   ‘고구려짬뽕10101MINI’  → 브랜드. `10101`·`MINI` 로 잡는다
# 브랜드명을 글자 그대로 넣지 않고 토막으로 잡는 건 표기가 흔들리기 때문이다
# (`고구려짬뽕10101MINI`·`고구려짬뽕 10101 MINI` 가 같은 페이지에 섞여 있다).
_NOT_PRODUCT = ("10101", "MINI", "고구려푸드", "브랜드", "가맹", "창업",
                "프랜차이즈", "이벤트", "캠페인", "협약", "점")

# 지점명. `"점"` 을 _NOT_PRODUCT 에 넣으면 부분일치라 '점보마라탕'·'점보만두'
# 같은 실존 작명을 죽인다(라화쿵부가 실제로 '3KG 점보마라탕' 을 판다).
# 지점명은 항상 '…점' 으로 **끝나므로** 끝자리로만 본다.
_BRANCH = re.compile(r"점$")


def _text(node) -> str:
    return " ".join(node.text().split()) if node else ""


def _date(s: str) -> str:
    """'2023.09.04' → '2023-09-04'. 월·일 범위를 검증한다."""
    m = re.search(r"(20\d{2})[.\-/](\d{1,2})[.\-/](\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"{y:04d}-{mo:02d}-{d:02d}"


def _get(c, params: dict) -> str:
    r = base.retry(lambda: c.get(SITE + "/", params=params))
    r.raise_for_status()
    return r.text


def _rows(html: str) -> list:
    """목록 한 페이지 → [(등록일, 글번호, 온전한제목)].

    제목은 `.bbs-multi-tit` 가 아니라 **링크의 title 속성**에서 가져온다.
    둘 다 온전하지만 title 쪽이 공백이 깨끗하다.
    """
    out = []
    for info in HTMLParser(html).css(".bbs-multi-info"):
        a = info.css_first("a[title]")
        if not a:
            continue
        title = " ".join(a.attributes.get("title", "").split())
        when = _date(_text(info.css_first(".bbs-multi-date")))
        m = re.search(r"ix=(\d+)", a.attributes.get("href", ""))
        if title and when and m:
            out.append((when, m.group(1), title))
    return out


def _names(title: str, body: str) -> list:
    """제목과 본문을 교차검증해 상품명을 뽑는다. 못 고르면 빈 목록.

    **제목**이 ‘…’ 로 부른 이름 중 **본문에도 (공백 무시) 있는 것**만 남긴다.
    탕화쿵푸와 방향이 반대다 — 사유는 docstring §2.
    """
    t = " ".join(title.split())
    if any(w in t for w in _SKIP) or not _LAUNCH.search(t):
        return []
    flat_body = body.replace(" ", "")
    out, seen = [], set()
    for m in _QUOTED.finditer(t):
        name = m.group(1).strip(" ,·∙")
        # 두 상품을 '·' 로 묶은 한 덩어리는 버린다(보배반점에서 실제로 터진 오집).
        if len(name) < 2 or any(ch in name for ch in "·∙&?"):
            continue
        if any(w in name for w in _NOT_PRODUCT) or _BRANCH.search(name):
            continue
        if name.replace(" ", "") not in flat_body:   # 본문이 안 부르면 버린다
            continue
        if name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out


def _image(doc) -> str:
    """기사 본문 이미지. 사이트 UI 이미지(/upload/site/, /upload/banner/)는 뺀다."""
    cont = doc.css_first("#bbsContents")
    for n in (cont.css("img") if cont else []):
        src = n.attributes.get("src", "")
        if not src or "/upload/site/" in src or "/upload/banner/" in src:
            continue
        if src.startswith("/"):
            src = SITE + src
        if src.startswith("https://"):
            return src
    return ""


def fetch() -> list[Item]:
    cand, posts = [], 0
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            if page > 1:
                time.sleep(DELAY)
            rows = _rows(_get(c, {"c": BOARD, "gp": page}))
            if not rows:
                break
            posts += len(rows)
            for when, ix, title in rows:
                if any(w in title for w in _SKIP) or not _LAUNCH.search(title):
                    continue
                cand.append((when, ix, title))
        else:
            # MAX_PAGES 를 다 돌고도 빈 페이지를 못 만났다 — 글이 늘었다는 뜻이다.
            # 조용히 뒷페이지를 버리지 않고 드러낸다.
            raise RuntimeError(
                f"{SITE}/?c={BOARD} 목록이 {MAX_PAGES}페이지를 넘는다. MAX_PAGES 를 올려라")

        # 상품 기사가 0건인 건 정상이다(§3). 하지만 **글 자체가 0건이면** 마크업이
        # 바뀐 것이다. 그 둘을 가르려고 cand 가 아니라 posts 를 센다.
        if not posts:
            raise RuntimeError(
                f"{SITE}/?c={BOARD} 에서 글을 하나도 못 찾았다. 마크업을 확인해라")

        items: list[Item] = []
        seen = set()
        for when, ix, title in cand:
            time.sleep(DELAY)
            doc = HTMLParser(_get(c, {"c": BOARD, "gbn": "view", "ix": ix}))
            cont = doc.css_first("#bbsContents")
            body = _text(cont) if cont else ""
            img = _image(doc)
            url = f"{SITE}/?c={BOARD}&gbn=view&ix={ix}"
            for name in _names(title, body):
                it = Item(brand=BRAND, name=name, image=img,
                          released_at=when, is_new=True, url=url)
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
    return items
