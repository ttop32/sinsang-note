"""에그드랍.

⚠️ 이 브랜드만 평문 HTTP 로 받는다. 우회가 아니라 그 길밖에 없다.
`eggdrop.co.kr` 의 TLS 인증서는 브랜드 본인 것이 맞는데(CN/SAN 이 www.eggdrop.co.kr)
**2025-05-27 에 만료됐다.** 2026-09-30 현재 갱신되지 않았다.
그래서 `base.client()`(verify=True) 로는 HTTPS 접속 자체가 안 된다.
`verify=False` 로 검증을 끄지 않는다 — 그러면 만료를 몰래 덮어 쓰는 셈이고,
중간자가 인증서를 갈아끼워도 우리가 알 수 없다. 대신 `http://` 로 명시해
"이 연결은 처음부터 암호화되지 않았다"는 사실을 코드에 드러낸다.
받는 건 공개 메뉴 정보뿐이고 자격증명·개인정보를 보내지 않으므로,
남는 위험은 "받은 데이터가 변조될 수 있음" 한 가지다. 운영자 방침으로 허용한다.
robots.txt 도 HTTP 로만 받히고 `User-agent: * / Allow: /` 다(200, text/plain).

목록은 `/menu/list.php?category=…` 8장이 전부다. SSR 이고 브라우저 불필요.
카테고리: NEW / SET MENU / SANDWICH / TOAST / BAGEL / BRUNCH / SIDE / DRINK, COFFEE.

신제품 신호:
  is_new  `category=NEW` 가 독립 카테고리다. 여기 실린 것만 True, 나머지는 False.
          브랜드가 따로 골라 담는 칸이라 '안 담긴 건 신제품이 아니다'로 본다
          (폴바셋 newIcon 과 같은 처분).
  released_at  **없다.** 목록에도 상세에도 날짜 필드가 하나도 없다.
          조사 문서가 "다음 조사 1순위"로 남긴 `/menu/view.php?seq=` 상세를
          2026-09-30 에 실제로 받아 확인했다. 상세에 있는 건 영문명·한글명·설명·
          이미지 슬라이드뿐이고 출시일·등록일 항목이 없다. 이 카테고리에서
          released_at 을 채울 수 있는 브랜드는 없다는 뜻이다.
  uploaded_at  비운다. 이미지 파일명(`/upload/menu/1767686689.png`)이 유닉스 epoch
          처럼 보이지만 같은 사이트에 `1793690388.png`(→ 2026-11-03, 미래)가 있다.
          epoch 해석이 성립하지 않으므로 uploaded_at 으로도 쓰지 않는다.

홈(`/`)의 `<section class="new"><h3>NEW EGGDROP</h3>` 슬라이더는 쓰지 않는다.
상품 목록이 아니라 고정 배너 한 장이고(`/assets/images/main/img_new_1.png`),
2026-09-30 현재 거기 걸린 '클럽 샌드위치'는 `category=NEW` 에 들어 있지도 않다.
조사 문서는 이걸 신제품 소스로 적었는데 실측으로는 아니다.

name_en·desc 는 목록에 없고 상세에만 있다. 전건 상세를 받으면 요청이 수십 회라
NEW 로 잡힌 것만 상한을 두고 받는다.

이용약관: 찾지 못했다. 푸터에 '개인정보취급방침'(`/etc/privacy.php`)만 있고
이용약관 링크가 없다. 금지 조항을 확인하지 못했다는 뜻이지 없다는 뜻은 아니다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "에그드랍"
HOST = "http://www.eggdrop.co.kr"     # ↑ docstring 참조. https 는 인증서 만료로 불가.
LIST_PATH = "/menu/list.php"
VIEW_PATH = "/menu/view.php"
DELAY = 2.0          # 요청 간격(초)
MAX_DETAILS = 30     # 폭주 방지. 현재 NEW 는 7건.

NEW_CATEGORY = "NEW"
CATEGORIES = [NEW_CATEGORY, "SET MENU", "SANDWICH", "TOAST",
              "BAGEL", "BRUNCH", "SIDE", "DRINK, COFFEE"]

_BG = re.compile(r"url\(\s*['\"]?([^'\")]+)")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _abs(src: str) -> str:
    if not src:
        return ""
    return src if src.startswith("http") else HOST + src


def _bg_image(node) -> str:
    """style="background-image: url('/upload/menu/….png')" 에서 경로만."""
    if not node:
        return ""
    m = _BG.search(node.attributes.get("style", "") or "")
    return _abs(m.group(1)) if m else ""


def _seq(href: str) -> str:
    m = re.search(r"seq=(\d+)", href or "")
    return m.group(1) if m else ""


def _detail(c, seq: str) -> tuple:
    """상세의 (영문명, 설명). 출시일 필드는 이 페이지에 없다(docstring 참조)."""
    r = base.retry(lambda: c.get(HOST + VIEW_PATH, params={"seq": seq}))
    r.raise_for_status()
    t = HTMLParser(r.text)
    h2 = t.css_first(".page-menu-view .menu header h2")
    p = t.css_first(".page-menu-view .visual > p")
    return _clean(h2.text()) if h2 else "", _clean(p.text()) if p else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    by_key: dict = {}
    with base.client() as c:
        for cat in CATEGORIES:
            r = base.retry(lambda: c.get(HOST + LIST_PATH, params={"category": cat}))
            r.raise_for_status()
            cards = HTMLParser(r.text).css(".list > ul > li > a")
            if not cards and cat == NEW_CATEGORY:
                raise RuntimeError("에그드랍 NEW: 상품 0건 — 셀렉터가 깨졌을 수 있다")

            for a in cards:
                name = _clean(a.css_first(".text").text()) if a.css_first(".text") else ""
                if not name:
                    continue
                href = a.attributes.get("href", "")
                it = by_key.get(base.make_key(BRAND, name))
                if it:
                    # 같은 상품이 NEW 와 일반 카테고리에 겹쳐 실린다.
                    # NEW 여부는 살리고, 분류명은 NEW 가 아닌 쪽에서 채운다.
                    it.is_new = it.is_new or (cat == NEW_CATEGORY)
                    if not it.category and cat != NEW_CATEGORY:
                        it.category = cat
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    image=_bg_image(a.css_first("figure .img")),
                    category="" if cat == NEW_CATEGORY else cat,
                    is_new=(cat == NEW_CATEGORY),
                    url=_abs(href),
                )
                by_key[it.key] = it
                items.append(it)

            time.sleep(DELAY)

        # 영문명·설명은 상세에만 있다. 화면에 오를 신제품만 받는다.
        for it in [x for x in items if x.is_new][:MAX_DETAILS]:
            seq = _seq(it.url)
            if not seq:
                continue
            it.name_en, it.desc = _detail(c, seq)
            time.sleep(DELAY)

    return items
