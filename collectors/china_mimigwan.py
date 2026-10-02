"""미미관마라탕 — '미미관 소식' 게시판의 등록일과 신메뉴 글을 쓴다.

공정위 `중식` 업종 가맹점 수 **25위**(40개, 2024년 말). (주)아침빛바다.

**메뉴 페이지는 쓸 수 없다.** 아임웹(imweb)으로 만든 사이트고 `/16`(메뉴소개)·
`/21`(미미관 이야기)은 2026-10-02 실측으로 **본문이 통째로 이미지**다
(`cdn.imweb.me/thumbnail/…` 32장·8장, 게시판 행 0개). 상품명이 HTML 에 글자로
없으니 파싱할 것 자체가 없다. NEW 배지도 날짜도 없다.

쓸 수 있는 건 `/19`(미미관 소식) 하나다. 아임웹 게시판 위젯이고 **등록일이 붙는다.**

수집 경로. 2026-10-02 실측:
  - 목록 `https://mimimara.co.kr/19/` 가 SSR 이다. 쿠키·토큰 없이 열린다.
  - 한 행이 `ul.li_body` 고 `a.list_text_title`(제목) / `li.time`(등록일)이다.
    날짜는 `li.time` 의 **title 속성**(`2024-10-29 12:06`)이 더 정확하다 —
    보이는 글자는 날짜뿐이다.
  - ⚠️ **페이지는 1장뿐이고 `?page=2` 가 1페이지와 똑같은 10건을 돌려준다.**
    페이지 파라미터를 못 찾았다는 뜻이라 **목록을 한 번만 받는다.** 돌리면
    같은 글이 두 번 들어온다.
  - 상세는 `?bmode=view&idx=NN&t=board`. `div.view_tit`(제목)·
    `div.board_txt_area`(본문)·그 안의 `img`(사진, https cdn.imweb.me)다.

🔴 **게시판이 2024-10-29 에서 멈춰 있다.** 10건 전부 2024-03~2024-10 이다.
   그래서 날짜를 그대로 `released_at` 에 넣으면 **화면에는 0건이 오른다**(collect 의
   60일 창 밖). 그게 정상이고 의도다 — 소림마라와 같은 상황이고 같은 처리다.
   "건수가 0이니 고장났다"고 판단하지 마라. 고장이면 `fetch()` 가 예외를 던진다.
   ⚠️ 그래서 **날짜 하한(DAYS)을 두지 않는다.** 목록이 한 장 10건뿐이라 더 받을
   것도 없고, 하한을 두면 어댑터가 늘 빈 목록을 돌려줘 추출 규칙이 고장나도
   아무도 모른다. 화면 노출은 collect 의 60일 창이 거르게 둔다.

10건 중 상품 글은 **5건**이고 전건 본문을 눈으로 읽어 확인했다:
  신메뉴 - [크림마요새우] 출시!!                      2024-10-29
  간편 한끼 '미미관 컵누들 해물맛' 제품 출시!!!        2024-10-11  (HMR)
  신메뉴 - [통살새우해물링]이 새롭게 출시!             2024-05-31
  간편 한끼, '미미관 컵누들마라탕' - 온/오프라인 판매 중!! 2024-03-25  (HMR)
  신메뉴 - 유린기 출시!!                              2024-03-20
나머지 5건은 매장 오픈 2건·수상 1건·쇼츠 영상 1건·토핑 소개 1건('마라탕에는
눈꽃치즈가 내린다' — 출시 동사가 없어 _LAUNCH 에서 떨어진다)이다.
⚠️ 컵누들 2종은 매장 메뉴가 아니라 간편식(HMR)이다. 보배반점 '크림짬뽕'·라홍방
   '마라탕 한그릇'과 같은 성격이고 같은 이유로 담는다(그쪽 docstring 참고).

**상품명은 제목에서 뽑고 본문으로 교차검증한다 — 탕화쿵푸·보배반점과 방향이
반대다.** 그 둘은 본문의 ‘…’ 인용을 모아 제목에 있는 것만 남겼는데, 여기서는
그게 안 된다. 이 게시판은 **본문이 비어 있는 글이 있다** — 2024-10-29
'크림마요새우' 는 `board_txt_area` 안이 `<img>` 한 장뿐이고 글자가 0자다.
본문을 기준 축으로 삼으면 그 글의 상품을 통째로 잃는다. 대신 **제목이 상품명을
직접 묶어서 알려준다**(`[크림마요새우]`·`'미미관 컵누들 해물맛'`). 그래서
  ① 제목에서 `[…]`·‘…’ 로 묶인 이름과 `신메뉴 - … 출시` 꼴을 후보로 모으고
  ② **본문에 글자가 있으면 거기에도 나와야** 채택한다
는 2중 검증을 쓴다. 본문이 이미지뿐이면(위 1건) 제목 표식만으로 받는다 —
근거가 한쪽뿐이라는 뜻이니, 오집이 생기면 여기부터 의심해라.
⚠️ 본문은 띄어쓰기가 제목과 다르다(제목 '미미관 컵누들 해물맛' / 본문 '미미관
   컵누들해물맛'). 그래서 대조는 **공백을 턴 뒤**에 한다.
⚠️ 브랜드명이 따옴표 안에 들어와 상품으로 둔갑하는 사고가 있었다(라홍방 선례).
   후보에서 앞머리 '미미관'·'미미관마라탕'을 떼고, 떼고 나서 2글자가 안 되면
   버린다. 그래서 '미미관마라탕' 만 인용된 글은 아무것도 안 남긴다.

robots: `mimimara.co.kr/robots.txt` → 200, text/plain.
        `User-agent: *` / `Allow: /` 에 `Disallow:` 가 `/site_join`·`/login`·
        `/logout.cm`·`/shop_cart`·`/?mode*`·`/admin` 뿐이다. 우리가 읽는
        `/19/` 와 `/19/?bmode=view…` 는 **허용**이다(`/?mode*` 는 루트 기준
        패턴이라 `/19/?bmode=` 에 걸리지 않는다).
약관: 푸터에 이용약관·개인정보처리방침이 있다. 이용약관은 아임웹 기본 문안이고
      수집·복제·크롤러를 금지하는 조항은 찾지 못했다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "미미관마라탕"
SITE = "https://mimimara.co.kr"
LIST = SITE + "/19/"
DELAY = 2.2

# 상품 글인가. 이 말이 없으면 상세를 받지 않는다.
_LAUNCH = re.compile(r"(출시|선봬|선보|론칭|신메뉴|신제품|판매 ?중)")

# 상품 글이 아닌데 위 동사를 쓰는 것들. 실측 제목 10건으로 뽑았다.
_SKIP = ("호점", "OPEN", "오픈", "선정", "수상", "대상", "쾌거", "영상", "shorts",
         "이벤트", "프로모션", "창업", "채용", "박람회", "정보공개서", "휴무")

# 제목이 상품명을 묶는 세 가지 꼴. 실측:
#   신메뉴 - [크림마요새우] 출시!!
#   간편 한끼 '미미관 컵누들 해물맛' 제품 출시!!!
#   신메뉴 - 유린기 출시!!
_MARKED = re.compile(r"\[([^\[\]\n]{2,30})\]|[‘'`\"]([^’'`\"\n]{2,30})[’'`\"]")
_BARE = re.compile(r"신메뉴\s*[-–—]\s*(.{2,30}?)\s*(?:이|가)?\s*(?:새롭게\s*)?출시")

# 묶인 글자가 상품이 아닌 것들.
_NOT_PRODUCT = ("브랜드", "프랜차이즈", "이벤트", "캠페인", "협약", "점", "기념",
                "서비스", "인스타", "채널", "대상", "상위", "축제", "영상")

# 브랜드명 앞머리. 떼고 나서 남는 게 상품명이다('미미관 컵누들마라탕' → '컵누들마라탕').
_BRAND_HEAD = re.compile(r"^미미관(?:\s*마라탕)?\s*")


def _text(node) -> str:
    return " ".join(node.text().split()) if node else ""


def _date(s: str) -> str:
    m = re.search(r"(20\d{2})-(\d{1,2})-(\d{1,2})", s or "")
    if not m:
        return ""
    y, mo, d = (int(x) for x in m.groups())
    return f"{y:04d}-{mo:02d}-{d:02d}" if 1 <= mo <= 12 and 1 <= d <= 31 else ""


def _rows(html: str) -> list:
    """목록 → [(등록일, 상세URL, 제목)]."""
    out = []
    for ul in HTMLParser(html).css("ul.li_body"):
        a = ul.css_first("a.list_text_title")
        t = ul.css_first("li.time")
        if not a or not t:
            continue
        href = a.attributes.get("href", "")
        when = _date(t.attributes.get("title") or t.text())
        title = _text(a)
        idx = re.search(r"idx=(\d+)", href)
        if title and when and idx:
            # 목록 href 는 base64 검색조건(`?q=…`)이 붙어 길다. 글번호만 쓰면
            # 같은 글로 가고 주소도 짧다.
            out.append((when, f"{LIST}?bmode=view&idx={idx.group(1)}&t=board", title))
    return out


def _names(title: str, body: str) -> list:
    """제목에서 묶인 상품명을 뽑고 본문으로 교차검증한다. 못 고르면 빈 목록.

    본문에 글자가 없는 글(사진만 올린 글)은 제목 표식만으로 받는다 —
    docstring 의 ⚠️ 참고.
    """
    t = " ".join(title.split())
    if any(w in t for w in _SKIP) or not _LAUNCH.search(t):
        return []
    flat_body = (body or "").replace(" ", "")
    cand = [g for m in _MARKED.finditer(t) for g in m.groups() if g]
    cand += _BARE.findall(t)
    out, seen = [], set()
    for raw in cand:
        # `신메뉴 - [크림마요새우] 출시` 는 _MARKED 와 _BARE 에 둘 다 걸리고
        # _BARE 쪽은 대괄호를 품은 채로 잡힌다. 표식 문자를 털어 같은 이름으로
        # 모은다 — 안 털면 '[크림마요새우]' 가 따로 한 줄 더 들어간다.
        name = _BRAND_HEAD.sub("", raw.strip(" ,·∙[]‘’'\"`")).strip()
        if len(name) < 2 or any(w in name for w in _NOT_PRODUCT):
            continue
        # 제목이 두 상품을 '·' 로 묶어 한 표식 안에 넣는 경우는 버린다
        # (보배반점 선례). 개별 상품은 각자 따로 불릴 때 잡힌다.
        if any(ch in name for ch in "·∙&?"):
            continue
        # 본문에 글자가 있으면 거기에도 있어야 한다. 띄어쓰기가 제목과 달라서
        # 공백을 턴 뒤에 본다.
        if flat_body and name.replace(" ", "") not in flat_body:
            continue
        if name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out


def _image(doc) -> str:
    """글 본문 사진. 아임웹 CDN 이라 https 다."""
    for n in doc.css(".board_txt_area img"):
        src = n.attributes.get("src", "")
        if src.startswith("https://"):
            return src
    return ""


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST))
        r.raise_for_status()
        rows = _rows(r.text)
        # 목록이 비면 마크업이 바뀐 것이다. 조용히 빈 목록을 돌려주지 않는다.
        if not rows:
            raise RuntimeError(f"{LIST} 에서 글을 하나도 못 찾았다. 마크업을 확인해라")

        items: list[Item] = []
        seen = set()
        for when, url, title in rows:
            if any(w in title for w in _SKIP) or not _LAUNCH.search(title):
                continue
            time.sleep(DELAY)
            d = base.retry(lambda: c.get(url))
            d.raise_for_status()
            doc = HTMLParser(d.text)
            for s in doc.css("script,style"):
                s.decompose()
            full = _text(doc.css_first(".view_tit")) or title
            body = _text(doc.css_first(".board_txt_area"))
            img = _image(doc)
            for name in _names(full, body):
                it = Item(brand=BRAND, name=name, image=img,
                          released_at=when, is_new=True, url=url)
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
    return items
