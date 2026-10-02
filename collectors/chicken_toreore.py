"""또래오래.

공정위 가맹점 527개(치킨 업종 16위). toreore.com 은 구형 PHP 사이트라 메뉴 목록이
서버에서 통째로 렌더돼 나온다. 쿠키·세션 없이 열리고 브라우저도 불필요하다.

**요청 1번으로 끝난다.** /board/menu/board_list.php 한 장(53KB)에 전 메뉴 39건이
들어 있고, 상품별 추가 요청도 이미지 HEAD 도 없다. 치킨 브랜드 중 가장 싸다.

────────────────────────────────────────────────────────────────────────
이 어댑터가 치킨 중 유일하게 released_at 을 채운다
────────────────────────────────────────────────────────────────────────
BBQ·bhc·교촌·굽네는 넷 다 '브랜드가 말해준 출시일'이 없어서 이미지 파일명이나
Last-Modified 로 uploaded_at 까지만 쓴다. 또래오래는 다르다 — **상품마다 등록일이
문자열로 박혀 있다.** Item docstring 이 released_at 을 "가장 강한 신호"라고 부르는
그 자리에 그대로 들어간다.

다만 그게 **사람에게 보이는 목록이 아니라 HTML 주석 안**에 있다. 같은 페이지에
구버전 목록이 한 벌 더 생성되는데 `<!-- ... -->` 로 감싸져 브라우저엔 안 보인다.
죽은 하드코딩이 아니라 **매 요청마다 라이브 데이터로 다시 찍힌다** — 최신 상품
뿌레카치킨(2026.09.29)이 거기 들어 있고 사이트가 직접 붙인 [NEW] 배지와 맞는다.
주석 블록 안의 한 건은 이렇게 생겼다:

    <a href="board_view.php?&page=1&num=1909">
      <div class="tit">뿌레카치킨</div>
      <div class="txt">한마리, 순살, 윙봉, 스틱, 콤보</div>
      <div class="date">2026.09.29</div>

39건이 날짜 내림차순(2026.09.29 … 2024.04.02)으로 들어 있다. selectolax 는 주석
안을 안 파주니 정규식으로 주석을 먼저 꺼내고(`class="date"` 가 든 블록만) 그
조각을 다시 파싱한다.

🔴 **주석이라 템플릿을 정리하는 날 통째로 사라진다.** 그래서 날짜 블록이 0건이면
RuntimeError 로 터뜨린다. 날짜 없는 39건으로 조용히 떨어지면 이 브랜드가 가진
유일한 강한 신호를 잃고도 아무도 모른다 — 이 레포 최대 리스크가 그 경로다.

보이는 목록(board_seq=N)과 주석 목록(num=N)은 같은 번호다. 2026-10-02 실측
39/39 전건 조인됐다. 조인율이 떨어져도 터뜨린다 — 번호 체계가 갈라졌다는 뜻이다.

────────────────────────────────────────────────────────────────────────
신제품 신호가 셋이고 서로 독립이다
────────────────────────────────────────────────────────────────────────
  1. released_at  위의 주석 등록일. `2026.09.29` → `2026-09-29` 로만 바꾼다.
  2. NEW 배지     보이는 목록의 `<li>` class 다. 2026-10-02 실측 39건 중
                  case_X 33 / case_best 4 / case_new 2(뿌레카치킨 1909,
                  말랑삼색볼 1689). case_new 면 is_new=True, 라벨에 NEW/BEST 를
                  넣는다. **case_X 는 is_new=None 이다** — 배지가 없다는 게
                  '옛날 것'이라는 증거는 못 된다.
  3. 신메뉴 탭    category_seq=4 가 '신메뉴'다. 거기 담긴 상품도 is_new=True.
                  지금은 1건(뿌레카치킨)이라 2번의 부분집합이지만, 브랜드가 배지를
                  떼고 탭만 쓰는 날을 대비해 따로 본다.
탭 이름은 마크업(`div.tabMenu ul li a`)에서 읽는다. 하드코딩하면 탭이 늘 때
분류가 빈다 — chicken_goobne.py 가 `.maintab li span` 으로 하는 것과 같다.
오늘 읽히는 건 4=신메뉴 / 1=오곡시리즈 / 2=시그니처 / 3=순살&콤보 / 23=바베큐 /
5=사이드메뉴 이고, '신메뉴' 만 신호로 쓰고 나머지는 Item.category 로 들어간다.

────────────────────────────────────────────────────────────────────────
TLS — 서버가 중간인증서를 빠뜨린다. 검증을 끄지 않고 **보충**한다.
────────────────────────────────────────────────────────────────────────
2026-10-02 실측:

    리프  CN=www.toreore.com  (2025-09-22 ~ 2026-10-24, 유효)
          issuer = GlobalSign GCC R6 AlphaSSL CA 2025
    서버가 보낸 체인 = 리프 한 장뿐. 중간인증서가 없다.
    → certifi 로도 `unable to get local issuer certificate`

인증서는 멀쩡하고 소유자도 진짜인데 서버가 조각을 빠뜨린 것뿐이다. 리프의 AIA 가
가리키는 중간 인증서를 받아 `collectors/certs/globalsign-gcc-r6-alphassl-ca-2025.pem`
에 넣고 certifi 루트에 `load_verify_locations()` 로 **더해서** 쓴다.
`verify=False`(= `CERT_NONE`)는 쓰지 않는다 — notes/CRAWLING-POLICY.md §6-1 이
명시적으로 금지하고, 같은 사유·같은 처리의 선례가 lottechilsung.py 다.

보충한 컨텍스트로 실측했고 검증은 켜진 채 돈다:
    www.toreore.com          200    (보충 전에는 CERTIFICATE_VERIFY_FAILED)
    wrong.host.badssl.com    실패   Hostname mismatch
    self-signed.badssl.com   실패   self-signed certificate
http 우회는 쓰지 않는다 — 보충으로 https 가 정상 검증되므로 그럴 이유가 없다.
컨텍스트는 `base.client(verify=...)` 로 넘긴다(httpx 는 transport 가 있으면
Client(verify=) 를 조용히 무시한다. base.client 가 그 처리를 들고 있다).

────────────────────────────────────────────────────────────────────────
나머지 판단
────────────────────────────────────────────────────────────────────────
desc  `div.hashtag`(#고소바삭 #국내산오곡)와 `div.menu_des`(한마리, 순살, 윙봉,
      스틱, 콤보)를 ' · ' 로 이어 붙인다. 해시태그는 맛 설명이고 menu_des 는
      주문 가능한 **부위·단위**라 둘 다 사람에게 쓸모가 있다.
⚠️ `menu_des` 의 "한마리, 순살, 윙봉, 스틱, 콤보" 는 **세트가 아니라 한 상품을
   어떤 형태로 시킬 수 있는지**다. 이걸 세트로 읽고 버리면 치킨 본메뉴가 통째로
   날아간다. 그래서 여기서는 아무것도 안 거른다. 세트 판정은 collect.drop_sets()
   가 이름으로 한다.
promo 할인·행사 표시가 사이트에 없다. 전건 False 다. 세트에 promo 를 찍지 않는다.
url   카드가 이미 달고 있는 `/board/menu/board_view.php?board_seq=…&category_seq=…`
      다. 루트 기준 상대경로라 origin 만 앞에 붙인다. 추가 요청 없다.
image `/upload_files/board/MENU/o_….png` 도 같은 방식으로 origin 을 붙인다. 전부
      https 라 base.derive() 의 http 폐기에 걸리지 않는다.
가격은 페이지에 없다. 알레르기·열량 정보도 없다.
robots: https://www.toreore.com/robots.txt 는 404(규칙 없음)다. 운영자 판단으로
        수집하되 삭제 요청이 오면 다투지 않고 즉시 내린다.
"""
import pathlib
import re
import ssl

import certifi
from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "또래오래"
SITE = "https://www.toreore.com"
LIST = SITE + "/board/menu/board_list.php"

# 서버가 빠뜨린 중간 인증서. 출처·만료일은 파일 머리말 참고.
CA_EXTRA = (pathlib.Path(__file__).parent / "certs"
            / "globalsign-gcc-r6-alphassl-ca-2025.pem")

DELAY = 0.0      # 요청이 1번뿐이라 간격을 둘 자리가 없다. 상수는 다른 어댑터와 맞춰 남긴다.
MAX_ITEMS = 200  # 폭주 방지. 현재 39건.

# 브랜드가 '신메뉴' 라고 이름 붙인 탭. 분류명으로 맞춘다(번호는 바뀔 수 있다).
NEW_TAB = "신메뉴"

# 주석 목록의 `board_view.php?&page=1&num=1909` 와 보이는 목록의
# `board_view.php?board_seq=1167&category_seq=1` 를 잇는 번호.
_NUM = re.compile(r"[?&]num=(\d+)")
_SEQ = re.compile(r"[?&]board_seq=(\d+)")
_CAT = re.compile(r"[?&]category_seq=(\d+)")
# `2026.09.29` 만 받는다. 형식이 바뀌면 조용히 틀린 날짜를 쓰느니 비우는 게 낫다.
_DATE = re.compile(r"^(\d{4})\.(\d{2})\.(\d{2})$")


def _text(node, sel: str) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _abs(path: str) -> str:
    """루트 기준 상대경로에 origin 을 붙인다. 이미 절대면 그대로 둔다."""
    path = (path or "").strip()
    if not path:
        return ""
    return SITE + path if path.startswith("/") else path


def _ssl_context() -> ssl.SSLContext:
    """certifi 루트에 서버가 빠뜨린 중간 인증서 한 장을 **더한** 컨텍스트.

    검증을 끄는 게 아니다. check_hostname·verify_mode 는 기본값 그대로다.
    """
    ctx = ssl.create_default_context(cafile=certifi.where())
    if not CA_EXTRA.exists():
        raise FileNotFoundError(
            f"중간 인증서가 없다: {CA_EXTRA} — 이게 없으면 이 사이트는 "
            f"unable to get local issuer certificate 로 붙지 않는다")
    ctx.load_verify_locations(cafile=str(CA_EXTRA))
    return ctx


def _tabs(tree) -> dict:
    """category_seq → 탭 이름. 마크업에서 읽어 탭이 늘어나도 따라가게 한다."""
    out = {}
    for a in tree.css("div.tabMenu ul li a"):
        m = _CAT.search(a.attributes.get("href", ""))
        name = " ".join(a.text().split())
        if m and name:
            out[m.group(1)] = name
    return out


def _dates(html: str) -> dict:
    """HTML 주석 안의 구버전 목록에서 num → 'YYYY-MM-DD' 를 뽑는다.

    브라우저엔 안 보이지만 서버가 매 요청마다 라이브 데이터로 찍는다(docstring 참고).
    selectolax 는 주석 내부를 파싱하지 않으므로 먼저 정규식으로 꺼내 온다.
    """
    blocks = [b for b in re.findall(r"<!--(.*?)-->", html, re.S)
              if 'class="date"' in b]
    out = {}
    for block in blocks:
        for a in HTMLParser(block).css("a[href*='board_view.php']"):
            m = _NUM.search(a.attributes.get("href", ""))
            if not m:
                continue
            d = _DATE.match(_text(a, "div.date"))
            if d:
                out[m.group(1)] = f"{d.group(1)}-{d.group(2)}-{d.group(3)}"
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client(verify=_ssl_context()) as c:
        r = base.retry(lambda: c.get(LIST))
        r.raise_for_status()

    tree = HTMLParser(r.text)
    tabs = _tabs(tree)
    dates = _dates(r.text)
    cards = tree.css("li[class^=case]")

    # 아래 셋은 전부 '조용한 부분수집' 을 막기 위한 가드다. 하나라도 비면
    # 건수는 멀쩡한 채로 신호만 사라져서 collect.py 의 0건 가드·FLOOR 를
    # 둘 다 통과한다. 그 상태가 굳는 게 제일 나쁘다.
    if not cards:
        raise RuntimeError(
            "또래오래 메뉴 카드 0건 — 'li[class^=case]' 가 안 걸린다. "
            "셀렉터가 깨졌을 가능성")
    if not tabs:
        raise RuntimeError(
            "또래오래 탭 목록이 비었다 — 'div.tabMenu ul li a' 가 안 걸린다. "
            "셀렉터가 깨졌을 가능성")
    if not dates:
        raise RuntimeError(
            "또래오래 등록일 목록이 비었다 — 주석 안의 구버전 목록이 사라졌거나 "
            "셀렉터가 깨졌을 가능성. 날짜 없이 수집하면 이 브랜드의 유일한 "
            "출시일 신호를 잃고도 건수가 그대로라 아무도 못 알아챈다")

    for li in cards[:MAX_ITEMS]:
        a = li.css_first("a[href*='board_view.php']")
        href = a.attributes.get("href", "") if a else ""
        name = _text(li, "div.menu_name")
        if not name:
            continue

        cls = li.attributes.get("class", "")
        seq = _SEQ.search(href)
        cat = _CAT.search(href)
        category = tabs.get(cat.group(1), "") if cat else ""

        labels = []
        if cls == "case_new":
            labels.append("NEW")
        elif cls == "case_best":
            labels.append("BEST")

        # 배지와 '신메뉴' 탭은 서로 독립이다. 둘 중 하나라도 걸리면 신제품으로 본다.
        # 둘 다 아니면 None — 배지가 없다는 건 옛 상품이라는 증거가 못 된다.
        is_new = True if (cls == "case_new" or category == NEW_TAB) else None

        img = li.css_first("div.menu_img .imgBx img")
        # 해시태그(맛)와 menu_des(주문 단위)를 같이 보여준다. menu_des 는
        # 세트 구성이 아니라 부위·단위 안내다 — docstring ⚠️ 참고.
        desc = " · ".join(t for t in (_text(li, "div.hashtag"),
                                      _text(li, "div.menu_des")) if t)

        it = Item(
            brand=BRAND,
            name=name,
            desc=desc,
            image=_abs(img.attributes.get("src", "") if img else ""),
            labels=labels,
            category=category,
            # 브랜드가 직접 적어둔 등록일이다. uploaded_at 이 아니라 released_at.
            released_at=dates.get(seq.group(1), "") if seq else "",
            is_new=is_new,
            # 할인·행사 표시가 사이트에 없다. 세트에는 promo 를 찍지 않는다
            # (collect.drop_sets() 가 이름으로 거른다).
            promo=False,
            url=_abs(href),
        )
        if it.key in seen:
            continue
        seen.add(it.key)
        items.append(it)

    # 보이는 목록과 주석 목록은 같은 번호 체계여야 한다(2026-10-02 실측 39/39).
    # 조인율이 무너지면 번호가 갈라진 것이고, 그대로 두면 날짜 없는 상품이
    # 조용히 늘어난다. 절반 밑으로 떨어지면 터뜨린다.
    dated = sum(1 for it in items if it.released_at)
    if items and dated * 2 < len(items):
        raise RuntimeError(
            f"또래오래 등록일 조인 실패 — {len(items)}건 중 {dated}건만 날짜가 붙었다. "
            f"board_seq ↔ num 번호 체계가 갈라졌을 가능성")
    return items
