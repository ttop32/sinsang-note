"""부어치킨.

공정위 등록 가맹점 260개, 치킨 업종 22위. boor.co.kr 은 ASP.NET(WebForms) 사이트고
메뉴 목록이 서버에서 그대로 렌더돼 나온다. 쿠키·세션 없이 열리고 브라우저도 불필요하다.
응답은 UTF-8.

⚠️ **이 브랜드는 평문 HTTP 로만 받는다.** `https://www.boor.co.kr` 은 TLS 핸드셰이크가
아니라 **연결 자체가 리셋된다**(`ConnectError: [Errno 54] Connection reset by peer`,
2026-10-02 재확인). 인증서가 틀린 게 아니라 443 이 서비스되지 않는 것이다. 그래서
verify=False 같은 우회가 성립하지 않고 http 말고는 길이 없다. 에그드랍과 같은 처분이다 —
받는 건 공개 메뉴 정보뿐이고 자격증명·개인정보를 보내지 않으므로 남는 위험은
"받은 데이터가 변조될 수 있음" 하나다. 운영자 방침으로 허용한다.
apex `/` 는 렌더 텍스트 8자짜리 껍데기고 **진짜 홈은 `/default.aspx`** 다.

목록은 `/menu/default.aspx?menu=<분류>` 한 장씩이다. 분류 목록은 페이지 안의 스크립트에
박혀 있다 — `var arrMenuCategory = ["ALL","NEW","그릴후라이드","후라이드","버거","사이드"];`.
하드코딩하지 않고 정규식으로 읽어서 브랜드가 분류를 늘리면 따라가게 했다.
내비 링크는 `menu=%uADF8%uB9B4…` 같은 JS escape(%uXXXX)로 적혀 있지만, 서버는 보통의
UTF-8 퍼센트 인코딩도 그대로 받는다(실측). httpx params 로 그냥 넘긴다.

신제품 신호:
  is_new  **NEW 탭이 진짜 서버측 필터다.** 2026-10-02 실측으로 ALL 57건, NEW 12건이고
          NEW 는 ALL 의 진부분집합이다(맵쇼킹·콘소메치킨·바삭허니 4종·크리스피킹 4종·
          흥부/놀부강정). 후라이드 13건은 NEW 와 교집합이 없다. 즉 브랜드가 직접 골라
          담는 칸이다. 그래서 전 분류를 훑어 커버리지를 잡고, NEW 탭에서 돌아온
          **이름**에만 True 를 준다(교촌 new_names 와 같은 구조).
          나머지는 False 가 아니라 **None** 이다 — NEW 탭에 없다는 게 "신제품이 아니다"의
          근거는 되지만, 브랜드가 탭 관리를 멈춘 경우와 구분되지 않아 단정하지 않는다.
  released_at  공지 게시판 `/customer/news.aspx` 에 "신메뉴 출시 <맵쇼킹>" 형태의 글이
          **등록일과 함께** 올라온다. 이미지 Last-Modified 보다 강한 신호라 이쪽을 쓴다.
          2026-10-02 실측: 맵쇼킹 2026-04-24, 콘소메치킨 2026-04-24, 크리스피킹 2025-12-01.
          제목의 홑화살괄호 안 이름을 상품명에 부분일치시킨다 — `<크리스피킹>` 하나가
          '오리지널/더블치즈/블랙페퍼/타코마요 크리스피킹' 4건에 걸리기 때문이다.
          오매칭을 줄이려고 공백을 턴 토큰이 3글자 이상일 때만 본다('<치킨>' 같은 글이
          오면 전건이 걸린다). 같은 이름의 글이 여럿이면 **가장 이른 날짜**를 쓴다.
          ⚠️ BoardID 파라미터는 글 번호처럼 보이지만 실제로는 **무시된다** — 1698·1706·
          1707 중 무엇을 넣어도 같은 목록 1페이지(10건)가 온다. 그래서 1회만 받는다.
          10건이면 2024-04 까지 거슬러 가므로 신제품 창(60일)에는 차고 넘친다.
  uploaded_at  이미지의 Last-Modified. 43/57 이 2024-05-13 한 날짜에 몰려 있는데
          이건 사이트 이관 일괄 업로드고, 나머지는 2025-08-25/26·2025-12-03·2026-04-28 로
          제품별로 흩어져 있다. 그 흩어진 쪽이 NEW 탭 12건과 정확히 겹친다.
          어디까지나 파일 업로드 시각이지 출시일이 아니라서 released_at 이 비었을 때만 쓴다.

  🔴 함정 — **썸네일 URL 로는 날짜를 못 받는다.** 카드의 `<img src>` 는 리사이저다
     (`/includes/thumbnail.ashx?image=/uploads/products/맵쇼킹.png&w=300&h=300`).
     이 리사이저는 **Last-Modified 헤더를 아예 안 준다**(전건 None). 그래서 `image=`
     쿼리 파라미터를 풀어 **원본** `/uploads/products/<이름>.png` 를 HEAD 해야 한다.
     파일명이 한글이라 unquote 후 다시 quote 한다. 이걸 모르면 uploaded_at 이 전건
     빈 값으로 조용히 떨어진다.

⚠️ **image 는 전건 빈 문자열이다.** 이미지 호스트가 같은 http 전용 서버라 https 로는
못 받는다(이미지 경로만 https 로 HEAD 해도 똑같이 connection reset). 우리 페이지는
https 라 http 이미지는 브라우저가 혼합 콘텐츠로 막고, base.derive() 도 `http://` 로
시작하는 image 를 버린다. 그래서 http URL 을 넣어봐야 중간에 사라질 뿐이라
**처음부터 빈 값으로 둔다**(에그드랍 선례, base.derive() 주석 참고). 443 이 열리면
`image=_origin(src)` 한 줄만 되살리면 된다.

상품별 상세 페이지가 **없다.** 카드 링크가 `href="javascript:void(0)"` 이고 눌러도
같은 자리에서 사진만 커진다. 그래서 url 은 그 상품이 실린 **분류 탭 주소**까지만 채운다.
base.SITES 폴백(ALL 탭)보다는 가깝다.

`10_살로만매니아세트`·`12_내맘대로세트`·`13_내맘대로반반세트` 는 후라이드 분류에 들어 있는
진짜 세트 상품이다. 손으로 거르지 않고 promo=False 로 그대로 넣어 collect.drop_sets()
가 이름으로 판단하게 둔다. promo 는 할인·행사 전용인데 메뉴 페이지에는 그런 표시가 없다.

가격은 메뉴 페이지에 없다. 이용약관은 `javascript:void(0)` 모달이라 URL 로 못 받았고
금지 조항을 확인하지 못했다(없다는 뜻이 아니다). robots.txt 는 `/member/`·`/uploads/`
등을 Disallow 하는데 우리가 HEAD 하는 원본 이미지가 `/uploads/products/` 라 거기 걸린다.
운영자 판단으로 무시하고 받는다(UA 는 숨기지 않는다).
"""
import re
import time
import urllib.parse
from email.utils import parsedate_to_datetime

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "부어치킨"
SITE = "http://www.boor.co.kr"          # https 는 연결 리셋. 위 docstring 참고
MENU = SITE + "/menu/default.aspx"
NEWS = SITE + "/customer/news.aspx"
NEW_CATEGORY = "NEW"                    # 브랜드가 직접 고르는 신메뉴 탭
ALL_CATEGORY = "ALL"                    # 전체 목록. 분류명을 못 주므로 커버리지용으로만

DELAY = 0.4        # 목록 요청 간격(초)
IMG_DELAY = 0.15   # 이미지 HEAD 간격(초)
MAX_CATEGORIES = 20   # 폭주 방지. 현재 6개.
MAX_ITEMS = 300       # 폭주 방지. 현재 57건(= HEAD 57회).

# 공지 제목 "신메뉴 출시 <맵쇼킹>" 에서 상품명만. '신제품 출시' 표기도 섞여 있다.
_NOTICE = re.compile(r"신(?:메뉴|제품)\s*출시.*?<\s*([^<>]+?)\s*>")


def _text(node, sel: str) -> str:
    """선택자 하나의 텍스트. <br/> 로 끊긴 설명문이 붙어버리지 않게 공백으로 잇는다."""
    n = node.css_first(sel)
    return " ".join(n.text(separator=" ").split()) if n else ""


def _name_en(node) -> str:
    """영문명. 비어 있는 자리에 '0' 을 박아둔 항목이 있어(콘크러치 오징어) 걸러낸다."""
    en = _text(node, "li.mn1_con")
    return "" if en.strip("0 ") == "" else en


def _categories(html: str) -> list:
    """페이지 스크립트의 arrMenuCategory 를 그대로 읽는다. 분류가 늘면 따라간다."""
    m = re.search(r"arrMenuCategory\s*=\s*\[(.*?)\]", html, re.S)
    return re.findall(r"[\"']([^\"']+)[\"']", m.group(1)) if m else []


def _origin(src: str) -> str:
    """썸네일 리사이저 URL 을 원본 이미지 URL 로. 리사이저는 Last-Modified 를 안 준다.

    `/includes/thumbnail.ashx?image=/uploads/products/맵쇼킹.png&w=300&h=300`
      → `http://www.boor.co.kr/uploads/products/%EB%A7%B5%EC%87%BC%ED%82%B9.png`
    """
    if not src:
        return ""
    q = urllib.parse.parse_qs(urllib.parse.urlparse(src).query).get("image", [""])[0]
    if not q:
        return ""
    return SITE + urllib.parse.quote(urllib.parse.unquote(q))


def _uploaded_at(client, img_url: str) -> str:
    """원본 이미지의 Last-Modified 를 날짜로. 실패하면 조용히 비운다."""
    if not img_url:
        return ""
    try:
        lm = client.head(img_url).headers.get("last-modified", "")
        return parsedate_to_datetime(lm).date().isoformat() if lm else ""
    except Exception:
        return ""


def _page(client, category: str) -> list:
    r = base.retry(lambda: client.get(MENU, params={"menu": category}))
    r.raise_for_status()
    return r.text, HTMLParser(r.text).css("div.mn1")


def _released(client) -> dict:
    """공지 목록의 '신메뉴 출시 <이름>' → 등록일. 같은 이름이면 가장 이른 날짜."""
    out: dict = {}
    try:
        r = base.retry(lambda: client.get(NEWS, params={"BoardID": 1707}))
        r.raise_for_status()
    except Exception:
        return out          # 공지는 보조 신호다. 못 받아도 수집은 계속한다
    for tr in HTMLParser(r.text).css("tr.ntc_tr"):
        subject = _text(tr, "td.c_subject")
        day = _text(tr, "td.c_day")
        m = _NOTICE.search(subject)
        if not m or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
            continue
        token = m.group(1).replace(" ", "")
        # 2글자 토큰은 '<치킨>' 처럼 전건을 물 수 있다. 짧으면 쓰지 않는다.
        if len(token) < 3:
            continue
        if token not in out or day < out[token]:
            out[token] = day
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    # Item.image 를 비워 두므로(위 ⚠️) 날짜를 뽑을 원본 이미지 주소는 따로 들고 있는다.
    origins: dict = {}
    with base.client() as c:
        # ALL 을 먼저 받는 건 분류 목록(arrMenuCategory)이 페이지 안에 있어서다.
        # 정작 카드는 분류명을 못 주므로 ALL 은 커버리지용으로 맨 뒤에서 거둔다.
        all_html, all_nodes = _page(c, ALL_CATEGORY)
        if not all_nodes:
            raise RuntimeError("전체 메뉴가 비었다 — 셀렉터가 깨졌을 가능성")

        categories = [x for x in _categories(all_html) if x != ALL_CATEGORY]
        if not categories:
            raise RuntimeError("arrMenuCategory 를 못 읽었다 — 스크립트가 바뀌었을 가능성")

        sources = []
        new_names = set()
        for category in categories[:MAX_CATEGORIES]:
            time.sleep(DELAY)
            _, nodes = _page(c, category)
            sources.append((nodes, category))
            if category == NEW_CATEGORY:
                new_names = {n for node in nodes
                             if (n := _text(node, "p.mn1_tit"))}

        # 비어 있으면 셀렉터나 탭이 깨진 것이다. 전체 건수는 57 그대로라 collect.py 의
        # 0건 가드도 FLOOR 도 발동하지 않아 "부어는 신제품이 없다"가 조용히 굳는다.
        if not new_names:
            raise RuntimeError("NEW 탭이 비었다 — 셀렉터가 깨졌을 가능성")

        sources.append((all_nodes, ""))      # 분류 탭에서 빠진 상품을 마지막에 거둔다
        released = _released(c)

        for nodes, category in sources:
            for node in nodes:
                name = _text(node, "p.mn1_tit")
                if not name:
                    continue
                is_new = name in new_names
                flat = name.replace(" ", "")
                it = Item(
                    brand=BRAND,
                    name=name,
                    name_en=_name_en(node),
                    desc=_text(node, "p.menu_screen"),
                    # http 전용 호스트라 base.derive() 가 어차피 버린다. 위 ⚠️ 참고.
                    image="",
                    labels=["NEW"] if is_new else [],
                    category=category,
                    # 같은 상품에 글이 여럿이면 가장 이른 날짜가 출시 공지다.
                    released_at=min((d for t, d in released.items() if t in flat),
                                    default=""),
                    is_new=is_new or None,   # NEW 탭 부재는 '아님'의 근거가 못 된다
                    # 상품별 페이지가 없다. 그 상품이 실린 분류 탭까지만.
                    url=f"{MENU}?menu={urllib.parse.quote(category or ALL_CATEGORY)}",
                    # 세트는 promo 가 아니다(collect.drop_sets() 담당). 메뉴 페이지에
                    # 할인·행사 표시는 없다.
                    promo=False,
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                img = node.css_first("img.thumbMenu")
                origins[it.key] = _origin(img.attributes.get("src", "") if img else "")
                items.append(it)
                if len(items) >= MAX_ITEMS:
                    break

        # 출시일을 공지에서 못 받은 것만 이미지 업로드 시각으로 메운다.
        for it in items:
            if it.released_at:
                continue
            time.sleep(IMG_DELAY)
            it.uploaded_at = _uploaded_at(c, origins.get(it.key, ""))
    return items
