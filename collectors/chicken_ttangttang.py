"""땅땅치킨.

공정위 등록 가맹점 177개, 치킨 업종 27위. ttangttang.co.kr 은 아임웹(imweb) 사이트고
메뉴가 전부 SSR 로 들어 있다. 쿠키·세션 없이 열리고 브라우저도 불필요하다.
다만 한 장이 640KB 안팎이라(테마 CSS·스크립트가 대부분) 받는 양에 비해 알맹이는 적다.

⚠️ **메뉴 번호와 내비 순서가 어긋나 있다.** 내비는 신메뉴·추천 메뉴·후라이드·오븐·세트·
피자·사이드·내점 순인데 경로는 `/menu02, /menu01, /menu03 … /menu08, /90` 이다.
`/menu01` 은 **추천메뉴**지 신메뉴가 아니다. 그래서 경로를 짐작하지 않고 내비
(`ul.clearfix li.depth-01 a[data-url]`)에서 **이름과 경로를 같이 읽는다** — 브랜드가
번호를 바꾸거나 탭을 늘려도 따라간다. `/menu` 는 `/menu02` 로 302 된다.

⚠️ **<title> 로 신메뉴 페이지를 찾으면 틀린다.** 내점 메뉴(`/90`)의 `<title>` 도
`신메뉴ㅣ땅땅치킨` 이다(복사 흔적, 2026-10-02 실측). 신메뉴 페이지는 내비 **라벨**이
'신메뉴' 인 쪽 하나뿐이다.
⚠️ imweb HTML 에는 `new_fixed_header`·`new_header_mode` 같은 테마 CSS 클래스 때문에
'new' 문자열이 수백 번 나온다. **정규식으로 NEW 를 세면 전건 오탐이다.** 쓰지 않는다.

신제품 신호:
  is_new  브랜드가 따로 운영하는 **신메뉴 페이지에 실렸는가** 하나다(굽네 선례).
          상품 카드에 NEW 배지 같은 건 없다. 2026-10-02 실측으로 신메뉴 6건인데
          전 메뉴를 합치면 35건이라, '전부 보여주는 페이지' 가 아니라 골라 담은 칸이
          맞다(후라이드 13건과는 2건만 겹치고, 추천메뉴 10건의 진부분집합이다).
          신메뉴에 없는 건 False 가 아니라 **None** 이다 — 탭 관리가 멈춘 경우와
          구분할 방법이 없어 '신제품이 아니다' 라고 단정하지 않는다.
  released_at  **없다.** 출시일·등록일을 적어주는 자리가 목록에도 상세 모달에도 없고,
          공지 게시판도 없다(브랜드 탭은 '브랜드/고객의 소리' 둘뿐). 비운다.
  uploaded_at  이미지 CDN 경로의 날짜다(`cdn.imweb.me/thumbnail/20260715/…`).

  🔴 선행 조사(notes/CANDIDATES-CHICKEN.md §7-5)가 "imweb 경로 날짜는 보통 일괄
     업로드 한 날짜라 쓰지 마라" 고 못박아 뒀다(호식이두마리치킨은 전 상품이
     `20200120` 하나였다). 그래서 **쓰기 전에 실측했다**(2026-10-02). 결과는
     호식이와 달랐다 — 수집한 49건의 날짜가 12개로 흩어진다:
       2024-01-11(1) · 2024-01-12(22, 사이트 구축 일괄) · 2024-01-23(1) ·
       2024-04-30(3) · 2024-12-18(1) · 2025-09-15(5) · 2025-12-10(1) ·
       2026-01-19(2) · 2026-04-14(2) · 2026-05-13(2) · 2026-05-19(6) · 2026-07-15(3)
     신메뉴 탭 6건도 한 덩어리가 아니라 2026-07-15 4건 / 2026-05-13 2건으로 갈린다.
     즉 이 브랜드에서는 경로 날짜가 제품별 업로드일로 살아 있다.
     경로 날짜가 진짜인지도 확인했다 — 추천메뉴를 뺀 7개 탭의 이미지 55장을 HEAD 해서
     Last-Modified 를 받아보니 **KST 로 환산하면 경로 날짜와 전건 일치**했다
     (예: `20260513` ↔ `Tue, 12 May 2026 16:27:14 GMT` = KST 05-13. GMT 날짜를 그대로
     쓰면 하루 어긋나는 건이 있다). 그래서 HEAD 를 매번 돌리지 않고 경로에서 읽는다 —
     요청이 목록 8회로 끝난다(굽네 `_uploaded_at` 과 같은 방식).
     어디까지나 업로드일이지 출시일이 아니므로 released_at 에는 넣지 않는다.

세트 처리. 이 브랜드는 **이름에 '세트'·'콤보' 가 없는 세트**가 있다 —
'5. 허브순살치킨+후왕', '2. 땅땅불갈비+불닭' 처럼 번호만 붙인 조합이고, 브랜드가
직접 **'세트 메뉴' 페이지**에 모아둔 것들이다. collect.drop_sets() 는 이름에
'세트|콤보' 가 있어야 움직이므로 이것들을 못 잡는다. 그렇다고 내가 이름 규칙을
새로 만들면 다른 어댑터와 기준이 어긋난다. 그래서 **상품은 그대로 싣되(커버리지),
브랜드가 세트 메뉴에 올린 것은 신메뉴 탭에 같이 걸려 있어도 is_new 를 주지 않는다.**
구성 조합은 신제품이 아니기 때문이고, 판단 근거가 내 이름 규칙이 아니라 브랜드
자신의 분류라서 이 선에서 멈춘다. 지금 해당되는 건 '5. 허브순살치킨+후왕',
'6. 허브순살치킨+매콤양념치킨' 2건이다(둘 다 세트 메뉴 1~6번 중 일부).

반대로 **`로'st치킨+슈트트링 감자` 는 끼워팔기가 아니라 단품으로 본다.** 세트 메뉴
페이지가 아니라 오븐 메뉴에 실려 있고, 무엇보다 `로'st치킨` 이 **전 메뉴 어디에도
단독으로 없다**(실측). 감자를 빼고는 아예 팔지 않는다는 뜻이라 '+슈트트링 감자' 는
상품명의 일부다. 세트 메뉴의 조합(허브순살치킨·후왕이 각각 후라이드 메뉴에 단품으로
존재)과는 성격이 다르다.

⚠️ `로'st치킨(HOT)+슈트트링 감자` 는 **수집 결과에 안 남는다.** base.make_key() 가
`(HOT)` 을 온도 표기로 보고 털어내서 `로'st치킨+슈트트링 감자` 와 같은 키가 되고,
먼저 들어온 쪽만 남는다. 어댑터가 거른 게 아니라 base 의 변형 합치기 규칙이고
(빽다방 HOT/ICED 와 같은 처분), 신메뉴 신호는 남는 쪽이 이미 들고 있다.

promo 는 전건 False 다. 메뉴에 할인·행사 표시가 없다(세트는 promo 가 아니다).

상품별 주소가 **없다.** 카드 링크가 `javascript:SITE.openModalMenu('m2026…','m2024…')`
라 같은 자리에서 모달이 뜰 뿐이다. 그래서 url 은 그 상품이 실린 **메뉴 페이지**까지만
채운다. 가격은 페이지에 없다.

robots.txt 는 `/site_join`·`/login`·`/shop_cart`·`/?mode*`·`/admin` 만 막고
`Allow: /` 다. 우리가 받는 `/menuNN` 은 허용 범위다. 다만 **이용약관이 하필
`/?mode=policy` 라 robots 가 막은 자리에 있어** 금지 조항을 확인하지 못했다.
운영자 판단으로 수집하되(UA 는 숨기지 않는다) 삭제 요청이 오면 즉시 내린다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "땅땅치킨"
SITE = "https://ttangttang.co.kr"
NEW_MENU = "신메뉴"       # 내비 라벨. 경로(/menu02)는 바뀔 수 있어 라벨로 찾는다
SET_MENU = "세트 메뉴"     # 브랜드가 구성 조합을 모아둔 칸. 위 docstring 참고

DELAY = 0.6        # 목록 요청 간격(초). 한 장이 640KB 라 넉넉히 둔다
MAX_PAGES = 20     # 폭주 방지. 현재 8개.

# 이미지 CDN 경로의 업로드일(`cdn.imweb.me/thumbnail/20260715/…`).
_CDN_DATE = re.compile(r"/thumbnail/(\d{4})(\d{2})(\d{2})/")


def _uploaded_at(img_url: str) -> str:
    """CDN 경로의 업로드일을 YYYY-MM-DD 로. 실측으로 Last-Modified(KST)와 일치한다."""
    m = _CDN_DATE.search(img_url or "")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def _text(node, sel: str) -> str:
    n = node.css_first(sel)
    return " ".join(n.text(separator=" ").split()) if n else ""


def _pages(html: str) -> list:
    """내비에서 (경로, 탭 이름) 을 순서대로. 번호가 어긋나 있어 경로를 짐작하지 않는다."""
    out, seen = [], set()
    for a in HTMLParser(html).css("ul.clearfix li.depth-01 a[data-url]"):
        url = (a.attributes.get("data-url") or "").strip()
        name = _text(a, "span.plain_name")
        if not url or not name or url in seen:
            continue
        seen.add(url)
        out.append((url, name))
    return out


def _cards(html: str) -> list:
    """갤러리 위젯의 상품 카드. 이름·설명은 숨은 caption 블록에 들어 있다."""
    return HTMLParser(html).css("div._item.item_gallary")


def _card(node) -> tuple:
    cap = node.css_first("div[id^=caption_]")
    if cap is None:
        return "", "", ""
    name = _text(cap, "h4")
    desc = _text(cap, "p")
    wrap = node.css_first("div.img_wrap")
    image = (wrap.attributes.get("data-src") or "") if wrap else ""
    return name, desc, image


def _get(client, path: str) -> tuple:
    """페이지 HTML 과 **최종 경로**. `/menu` 는 `/menu02` 로 302 되므로 둘이 다르다."""
    r = base.retry(lambda: client.get(f"{SITE}/{path}"))
    r.raise_for_status()
    return r.text, str(r.url).rstrip("/").rsplit("/", 1)[-1]


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        first, first_path = _get(c, "menu")   # /menu → /menu02 (신메뉴)
        pages = _pages(first)[:MAX_PAGES]
        if not pages:
            raise RuntimeError("메뉴 내비를 못 읽었다 — 셀렉터가 깨졌을 가능성")
        if not any(name == NEW_MENU for _, name in pages):
            raise RuntimeError(f"내비에 '{NEW_MENU}' 탭이 없다 — 구조가 바뀌었을 가능성")

        new_names, set_names = set(), set()
        sources = []
        for path, name in pages:
            # `/menu` 로 이미 받아둔 그 페이지는 다시 받지 않는다. 내비 순서가 아니라
            # **리다이렉트가 끝난 경로**로 맞춘다 — 순서는 언제든 바뀐다.
            if path == first_path:
                html = first
            else:
                time.sleep(DELAY)
                html, _ = _get(c, path)
            cards = _cards(html)
            sources.append((cards, path, name))
            # 같은 상품도 페이지마다 띄어쓰기가 다르다('2. 땅땅불갈비+불닭' vs
            # '2. 땅땅불갈비+ 불닭'). 비교는 공백을 턴 이름으로 한다.
            got = {n.replace(" ", "") for card in cards if (n := _card(card)[0])}
            if name == NEW_MENU:
                new_names = got
            elif name == SET_MENU:
                set_names = got

        # 비어 있으면 셀렉터나 탭이 깨진 것이다. 전체 건수는 그대로라 collect.py 의
        # 0건 가드도 FLOOR 도 발동하지 않아 "땅땅은 신제품이 없다"가 조용히 굳는다.
        if not new_names:
            raise RuntimeError("신메뉴 페이지가 비었다 — 셀렉터가 깨졌을 가능성")

        for cards, path, category in sources:
            for card in cards:
                name, desc, image = _card(card)
                if not name:
                    continue
                # 브랜드가 세트 메뉴에 올린 구성 조합은 신메뉴 탭에 걸려 있어도
                # 신제품으로 치지 않는다. 이름에 '세트' 가 없어 drop_sets 가 못 잡는다.
                flat = name.replace(" ", "")
                is_new = flat in new_names and flat not in set_names
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=desc,
                    image=image,
                    labels=["신메뉴"] if is_new else [],
                    category=category,
                    uploaded_at=_uploaded_at(image),
                    is_new=is_new or None,   # 신메뉴 탭 부재는 '아님'의 근거가 못 된다
                    # 상품별 주소가 없다(모달). 그 상품이 실린 메뉴 페이지까지만.
                    url=f"{SITE}/{path}",
                    # 세트는 promo 가 아니다. 메뉴에 할인·행사 표시도 없다.
                    promo=False,
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)

    # 🔴 신메뉴 탭(위 가드)과 별개로 **날짜만 조용히 사라지는** 경로가 있다.
    # imweb 이 CDN 경로를 바꾸면(`/thumbnail/<8자리>/` 가 아니게 되면)
    # `_uploaded_at` 이 전건 빈 문자열을 돌려주는데, 건수는 49 그대로고 is_new 도
    # 3건 남아서 collect.py 의 0건 가드도 FLOOR 도 통과한다. 그러면 신메뉴 탭
    # 밖의 46건은 신제품 판정 근거를 통째로 잃는다 — 2026-10-03 리뷰에서
    # 재현했다. 치킨플러스·호식이두마리치킨과 같은 가드다(실측 49/49).
    dated = sum(1 for it in items if it.uploaded_at)
    if dated * 2 < len(items):
        raise RuntimeError(
            f"땅땅치킨 업로드일 {len(items)}건 중 {dated}건만 붙었다 — "
            f"CDN 경로(cdn.imweb.me/thumbnail/<YYYYMMDD>/)가 바뀌었을 가능성")
    return items
