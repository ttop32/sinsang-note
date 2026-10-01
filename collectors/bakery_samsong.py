"""삼송빵집.

정답 도메인은 `ssbnc.kr` 이다. `ssbnc.co.kr` 은 인증서가 CN=*.mailplug.com 인
메일 호스팅이라 웹사이트가 아니다.

내비게이션 링크가 전부 `javascript:GoPage('menu1')` 이라 href 가 없다. 같은 HTML 안의
GoPage 함수 정의가 코드 → 경로를 그대로 들고 있어서 추가 요청 없이 뽑아 쓴다.
2026-09-30 실측.

  /doc/menu1.php  통옥수수빵          5종
  /doc/menu2.php  오븐에 구운 고로케   5종
  /doc/menu3.php  베이커리            19종
  /doc/menu4.php  커피/음료/디저트     8종

**menu5.php 는 404 다.** 조사 메모에는 menu1~5 다섯 요청으로 적혀 있었는데 실제로는
menu0~4 다. menu0 은 '제품소개' 전체 묶음인데 menu1~3 의 합(29종)일 뿐 menu4 가 빠져
있어서 menu0 을 받으면 음료를 놓친다. 그래서 menu1~4 를 개별로 받는다. 분류 이름도
그렇게 해야 붙는다.

**NEW 배지가 있다.** 조사에는 '신호 없음'으로 적혀 있었지만 상세 모달의 p.eng 에
NEW MENU / BEST MENU / HIT MENU 세 가지가 실제로 들어 있다(2026-09-30 기준 NEW 5건,
BEST 4건, HIT 2건). 배지 체계가 살아 움직이므로 NEW 가 없는 상품은 브랜드가 신제품이
아니라고 본 것으로 읽고 is_new=False 로 둔다.

**단, 문자열을 세면 안 된다.** menu3 의 raw HTML 에 NEW 가 7회 나오는데 그중 2회
(콘짜렐라 맵떡·먹물마카롱)는 통째로 주석 처리된 카드 안에 있다. 이 파일은 주석이
90개나 되는 편집 흔적 투성이다. 아래처럼 파서가 만든 .modal 노드에서만 읽는다.
덤으로 `<p class="eng">NEW MENU</h4>` 같이 닫는 태그가 어긋난 자리도 있는데
카드 수와 모달 수는 페이지마다 정확히 같게 파싱된다.

날짜는 없다. 목록에도 모달에도 등록일·출시일이 안 찍혀서 released_at·uploaded_at
둘 다 비운다. 공지·이벤트 게시판(그누보드, /pg/bbs/board.php?bo_table=comm1)에는
날짜가 있지만 글 제목을 상품에 끼워맞추는 건 추측이라 하지 않는다.

url 은 비운다. 상세가 같은 페이지의 모달이라 상품별 주소가 없다. base.SITES 의
브랜드 메뉴 URL 로 떨어진다.

robots.txt: 200 text/plain 21B, 본문 첫 글자 'U'. `User-agent: *` / `Allow:/` 뿐이라
막힌 경로가 없다. 이용약관 문서는 사이트에서 찾지 못했다.

소비자가격과 알레르기 정보가 모달에 있지만 Item 에 해당 필드가 없어 담지 않는다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "삼송빵집"
SITE = "https://ssbnc.kr"
MENUS = ("menu1", "menu2", "menu3", "menu4")
DELAY = 2.0

# <a href="javascript:GoPage('menu1')">통옥수수빵</a>
_GOPAGE = re.compile(r"GoPage\('([^']+)'\)")


def _text(node, sel):
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _nav_names(doc) -> dict:
    """내비게이션에서 menu 코드 → 분류 이름. 페이지마다 같은 nav 가 들어있다."""
    out = {}
    for a in doc.css(".smenu a"):
        m = _GOPAGE.search(a.attributes.get("href", ""))
        if m:
            out.setdefault(m.group(1), " ".join(a.text().split()))
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    names = {}
    with base.client() as c:
        for code in MENUS:
            r = base.retry(lambda: c.get(f"{SITE}/doc/{code}.php"))
            r.raise_for_status()
            doc = HTMLParser(r.text)
            names = names or _nav_names(doc)

            cards = doc.css(".thecard")
            modals = doc.css(".modal")
            # 앞면 카드의 영문명은 모달에 없다. 수가 같을 때만 순서로 짝짓는다.
            eng = [_text(x, ".front dd.eng") for x in cards] if len(cards) == len(modals) else []

            for i, modal in enumerate(modals):
                name = _text(modal, ".info h4")
                it = Item(brand=BRAND, name=name)
                if not name or it.key in seen:
                    continue
                seen.add(it.key)

                label = _text(modal, ".info p.eng")
                it.name_en = eng[i] if i < len(eng) else ""
                it.desc = _text(modal, ".info p.t1")
                img = modal.css_first(".img img")
                it.image = SITE + img.attributes.get("src", "") if img else ""
                it.labels = [label] if label else []
                it.category = names.get(code, "")
                it.is_new = "NEW" in label
                items.append(it)
            time.sleep(DELAY)

    # 배지가 깨져도 상품 건수는 그대로라 collect.py 의 0건 가드도 FLOOR 도 안 걸린다.
    # 신호만 조용히 사라진다. gs25.py 가 '1페이지가 비었다'에 넣은 가드를 여기로 옮긴다.
    # ⚠️ NEW 가 0건인 것 자체는 고장이 아니다 — 지금 5건뿐이라 브랜드가 다 내릴 수
    #    있다. 깨짐의 신호는 NEW·BEST·HIT 를 통틀어 라벨이 0건인 것이다
    #    (실측 2026-10-01: NEW 5 · BEST 4 · HIT 2 = 37건 중 11건).
    if items and not any(it.labels for it in items):
        raise ValueError(
            f"삼송빵집 배지 라벨(.info p.eng)이 {len(items)}건 중 0건이다. "
            f"실측 기준 NEW 5 · BEST 4 · HIT 2 가 붙어 있어야 한다 — "
            f"모달 셀렉터가 바뀌었는지 확인하라")
    return items
