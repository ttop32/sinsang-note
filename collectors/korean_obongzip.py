"""오복 오봉집(㈜조은음식드림).

가맹점 232개로 공정위 `한식` 업종 중위권이다(2025년도 정보공개서, 2024년 말 기준).
공정위 등록명은 '오복 오봉집' 인데 사이트·간판은 전부 '오봉집' 이라 그쪽을 쓴다.

아임웹(imweb) 사이트다. 분류가 다섯 장이고 각각 `gallery2` 위젯 하나에 상품이
들어 있다. 쿠키·세션·JS 불필요(아임웹은 서버렌더다). **총 5요청에 25건**
(2026-10-02 실측).
  /setmenu 3 · /mainmenu 9 · /soupmenu 4 · /snackmenu 4 · /sidemenu 5

**신제품 배지가 없다.** 아임웹 쇼핑 모듈의 `prod_badge_new` 설정이 페이지 JSON 에
들어 있긴 한데 값이 전부 빈 문자열이고, 애초에 이 사이트는 쇼핑 모듈이 아니라
갤러리 위젯으로 메뉴를 그린다. 카드에 배지 자리가 없다. 그래서 `is_new` 는 전부
None(모름)이다.

  uploaded_at  **아임웹 CDN 썸네일 경로에 날짜가 박힌다.**
          `https://cdn.imweb.me/thumbnail/20260427/f93afa750ae05.jpg` → 2026-04-27.
          25건 전부 파싱되고 미래 날짜가 없다(최대 2026-04-27, 조사일 2026-10-02).
          분포는 2025-12-08 2건 / **2025-12-22 16건** / 2026-03-18 2건 /
          2026-04-16 4건 / 2026-04-27 1건이다.

  🔵 **교차검증** — 같은 파일에 HEAD 를 쳐서 `Last-Modified` 와 맞춰봤다.
          `20251208/7de0262759486.jpeg` → Mon, 08 Dec 2025 05:36:23 GMT
          `20251208/125a604f12f25.jpeg` → Mon, 08 Dec 2025 05:36:24 GMT
          `20260427/f93afa750ae05.jpg`  → Mon, 27 Apr 2026 05:28:16 GMT
          경로의 날짜와 헤더가 **같은 날**이다. 아임웹이 업로드 시점에 썸네일을
          만들면서 그날 폴더에 넣는다는 뜻이라, 경로만 읽으면 된다. HEAD 25번을
          아낀다.

**released_at 에는 넣지 않는다.** 브랜드가 "출시일"이라고 말한 값이 아니라 사진을
올린 날짜다(본아이에프·한솥·원앤원과 같은 처분).
⚠️ **2025-12-22 16건은 사이트 구축일이다.** 25건 중 16건이 거기 몰려 있고,
네비게이션 메뉴 코드도 `m20251208...`·`m202512081ef...` 로 같은 시기다. 사이트를
2025년 12월에 새로 만들면서 사진을 통째로 올린 흔적이지 그 16종이 그때 나왔다는
뜻이 아니다(큰맘할매순대국 2025-12-22, 유가네 2020-07-07 과 같은 자리 —
공교롭게 큰맘과 날짜까지 같지만 서로 무관한 우연이다).
반대로 2026-03-18·04-16·04-27 7건은 따로 떨어져 있어 그 뒤에 추가된 게 맞다.

released_at 은 **못 채운다.** 갤러리 캡션에 이름과 한 줄 설명만 있고 날짜 항목이
없다. 상품 상세 페이지도 없다(`item_container` 에 `<a>` 가 걸려 있지 않다 — 링크가
걸린 갤러리도 아임웹엔 있지만 이 사이트는 안 걸었다). 지어내지 않고 비운다.
같은 이유로 `Item.url` 도 비워 `base.site()` 의 메뉴 페이지로 떨어뜨린다.

이 브랜드는 `is_new` 가 없어 **합류 첫날에는 신제품을 하나도 못 내놓는다.**
그 대신 `collect.py` 가 uploaded_at 을 first_seen 으로 소급해 기준선으로 깔아두므로,
다음에 올라오는 새 메뉴부터 날짜와 함께 잡힌다. 그게 정직하다(원앤원 선례).

`세트메뉴` 분류 3건(낙지오봉스페셜·오징어오봉스페셜·매생이연포보쌈)은 promo 로
찍지 않는다. 할인 행사가 아니라 구성 메뉴고, 거르는 건 `collect.drop_sets()`
담당이다(이삭토스트 선례).

상품명·설명은 화면에 안 보이는 `div[id^=caption_]` 안에 들어 있다. 아임웹 갤러리가
라이트박스에 쓰려고 숨겨둔 것인데(`style="display:none"`), 보이는 `.text_wrap` 은
이름만 갖고 설명이 없다. 그래서 캡션 쪽을 읽는다.

사이트가 6개 국어(한국어/English/中文/日本語/Tiếng Việt/Español)지만 상품명은
전부 한국어 한 벌이다. 언어 전환은 같은 URL 에 쿠키로 걸려서 기본값만 받는다.

가격은 사이트에 없다. 이용약관(`/이용약관`)이 있으나 자동 수집 금지 조항은
찾지 못했다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "오봉집"
HOST = "https://www.obongzip.com"
DELAY = 1.4          # 요청 간격(초). 전부 5요청이다.

# (분류명, 경로). 화면 네비게이션 순서 그대로다.
CATEGORIES = (
    ("세트메뉴",   "setmenu"),
    ("메인메뉴",   "mainmenu"),
    ("탕메뉴",     "soupmenu"),
    ("안주메뉴",   "snackmenu"),
    ("사이드메뉴", "sidemenu"),
)

# background-image 안의 CDN 주소. `data-bg` 쪽을 읽는다 — `style` 은 아임웹이
# 뷰포트에 따라 지웠다 썼다 하는 자리라 `data-bg` 가 더 안정적이다.
_BG_URL = re.compile(r"url\(\s*([^)]+?)\s*\)")
# 아임웹 CDN 썸네일 경로의 업로드 날짜.
_CDN_DATE = re.compile(r"/thumbnail/(\d{4})(\d{2})(\d{2})/")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _uploaded_at(url: str) -> str:
    """CDN 썸네일 경로의 날짜. 출시일이 아니라서 released_at 엔 안 넣는다."""
    m = _CDN_DATE.search(url or "")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen: set = set()
    with base.client() as c:
        for category, path in CATEGORIES:
            r = base.retry(lambda: c.get(f"{HOST}/{path}"))
            r.raise_for_status()
            time.sleep(DELAY)

            cards = HTMLParser(r.text).css(
                ".widget._gallery_wrap ._item.item_gallary")
            if not cards:
                raise RuntimeError(
                    f"오봉집 {category}: 상품 0건 — 셀렉터가 깨졌을 수 있다")

            for card in cards:
                # 이름·설명은 라이트박스용 숨은 캡션에만 있다(docstring 참고).
                cap = card.css_first("div[id^=caption_]")
                if not cap:
                    continue
                h4 = cap.css_first("h4")
                name = _clean(h4.text()) if h4 else ""
                if not name:
                    continue
                key = base.make_key(BRAND, name)
                if key in seen:
                    continue
                seen.add(key)

                desc = cap.css_first("p")
                wrap = card.css_first(".img_wrap")
                bg = wrap.attributes.get("data-bg", "") if wrap else ""
                m = _BG_URL.search(bg)
                image = m.group(1).strip("'\" ") if m else ""

                items.append(Item(
                    brand=BRAND,
                    name=name,
                    desc=_clean(desc.text()) if desc else "",
                    image=image,
                    category=category,
                    # 사진 올린 날짜. 출시일이 아니다(docstring 참고).
                    uploaded_at=_uploaded_at(image),
                    # 이 사이트에는 신제품 배지가 없다. 모름을 모름으로 둔다.
                    is_new=None,
                    # 1+1·할인 행사가 이 사이트에 없다. 세트메뉴는 promo 가 아니다.
                    promo=False,
                ))
    return items
