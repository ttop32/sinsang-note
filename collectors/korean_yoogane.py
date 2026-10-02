"""유가네(유가네닭갈비, (주)바이올푸드글로벌).

가맹점 201개로 공정위 `한식` 업종 중위권이다(2025년도 정보공개서, 2024년 말 기준).

정적 HTML 두 장이 전부다. 쿠키·세션·JS 불필요. 2026-10-02 실측.
  /menu/menu.html?depth1=1..4   일품메뉴 14 · 식사메뉴 3 · 별미메뉴 11 · 추가메뉴 15
  /menu/lunch_box.html          유가네 도시락 10
**총 5요청에 53건**, 이름이 겹치는 2건을 턴 51건이다. 세 번째 탭 '온라인 상품' 은
네이버 스마트스토어로 나가는 외부 링크라 받지 않는다.

**신제품 배지가 없다.** 카드(`.menu-list-item`) 안의 class 를 전수로 훑어
`new`·`best`·`hot`·`badge`·`icon`·`tag` 를 찾아봤는데 **하나도 없다.** 원앤원처럼
주석으로 숨겨둔 자리도 없다 — 애초에 그런 마크업을 만들지 않은 사이트다.
그래서 `is_new` 는 전부 None(모름)이다.

  uploaded_at  **이미지 파일명 꼬리 14자리가 업로드 시각**이다.
          `/upload/product/3553870698_gXTJlyFd_20250917091538.jpg`
          → 2025-09-17 09:15:38. 53건 전부 파싱되고 **미래 날짜가 하나도 없다**
          (최대 2026-03-23, 조사일 2026-10-02). 한솥 imagePath·원앤원
          `_xUpFiles/xMenu/` 와 같은 모양이고 같은 처분이다.
          연도 분포는(중복 제거 51건 기준) 2020년 24 / 2021년 13 / 2022년 1 /
          2024년 7 / 2025년 4 / 2026년 2 다. 에그드랍 때처럼 epoch 로 착각해
          미래가 섞이는 사고는 없다.
          **released_at 에는 넣지 않는다.** 브랜드가 "출시일"이라고 말한 값이
          아니라 사진을 올린 시각이다(본아이에프·한솥·원앤원과 같은 처분).
          ⚠️ 2020-07-07 에 23건이 몰려 있다. 사이트를 만들 때 통째로 올린
          흔적이라 **그 22건의 날짜는 '그날 나왔다'가 아니라 '그 뒤로 안 바뀌었다'**
          정도로만 읽어야 한다(큰맘할매순대국 2025-12-22, 원앤원 2020-04-10 과
          같은 자리). 반대로 2025-09-17 4건(치폴레·청양 와르르닭갈비, 트리플
          닭갈비 2종)과 2026-03-23 2건(트리플치즈·모둠사리)은 따로 떨어져 있어
          그 뒤에 추가된 게 맞다.

released_at 은 **못 채운다.** 목록에 날짜 항목이 없고 상품 상세 페이지도 없다
(카드에 `<a>` 가 걸려 있지 않다). 지어내지 않고 비운다. 같은 이유로 `Item.url` 도
비워 `base.site()` 의 메뉴 페이지로 떨어뜨린다.

브랜드 뉴스(`/community/news.html`)도 받아 확인했다. 2026-08-31·08-26 로 **살아
있는 게시판이긴 한데** 실린 게 전부 외부 언론 기사 전재이고 대학생 협찬·할인
프로모션 얘기다. 최근 10건에 신메뉴 출시 기사가 하나도 없어 is_new 를 여기서
끌어올 수는 없었다. 브랜드가 신메뉴 기사를 올리기 시작하면 다시 볼 자리다.

이 브랜드는 `is_new` 가 없어 **합류 첫날에는 신제품을 하나도 못 내놓는다.**
그 대신 `collect.py` 가 uploaded_at 을 first_seen 으로 소급해 기준선으로 깔아두므로,
다음에 올라오는 새 메뉴부터 날짜와 함께 잡힌다. 그게 정직하다(원앤원 선례).

도시락 세트(`유가네닭갈비 1인 세트` 등)는 promo 로 찍지 않는다. 할인 행사가 아니라
구성 메뉴고, 거르는 건 `collect.drop_sets()` 담당이다(이삭토스트 선례).

이름이 겹치는 3건이 있다 — `유가네 닭갈비`·`닭갈비 철판 볶음밥` 계열이 메뉴와
도시락 양쪽에 실린다. key 기준으로 먼저 만난 쪽(메뉴)을 남긴다.

가격은 사이트에 없다. 영문명은 `.desc` 에 있는데 앞에 보이지 않는 공백 문자
(U+200B)가 붙은 게 있어 `_clean()` 으로 턴다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "유가네"
HOST = "https://www.yoogane.co.kr"
MENU_URL = HOST + "/menu/menu.html"
BOX_URL = HOST + "/menu/lunch_box.html"
DELAY = 1.4          # 요청 간격(초). 전부 5요청이다.

# depth1 → 분류명. 화면 탭 순서 그대로다.
TABS = {
    "1": "일품메뉴",
    "2": "식사메뉴",
    "3": "별미메뉴",
    "4": "추가메뉴",
}
BOX_CATEGORY = "유가네 도시락"

# 배경 이미지 URL. 카드 썸네일이 <img> 가 아니라 style 의 background-image 다.
_BG = re.compile(r"url\(\s*['\"]?([^'\")]+)")
# 파일명 꼬리의 업로드 시각. `..._20250917091538.jpg` 의 앞 8자리만 쓴다.
_STAMP = re.compile(r"_(\d{4})(\d{2})(\d{2})\d{6}\.[A-Za-z]+$")


def _clean(s: str) -> str:
    """공백 정리 + 보이지 않는 공백(U+200B) 제거. 영문명 앞에 섞여 들어온다."""
    return " ".join((s or "").replace("​", " ").split())


def _abs(src: str) -> str:
    if not src:
        return ""
    return src if src.startswith("http") else HOST + "/" + src.lstrip("./")


def _uploaded_at(src: str) -> str:
    """이미지 파일명 꼬리의 업로드 날짜. 출시일이 아니라서 released_at 엔 안 넣는다."""
    m = _STAMP.search((src or "").rsplit("/", 1)[-1])
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def _parse(html: str, category: str) -> list:
    out = []
    for card in HTMLParser(html).css(".menu-list-item"):
        tit = card.css_first(".tit")
        name = _clean(tit.text()) if tit else ""
        if not name:
            continue
        en = card.css_first(".desc")
        box = card.css_first(".img-bx")
        m = _BG.search(box.attributes.get("style", "") or "") if box else None
        src = _abs(m.group(1).strip()) if m else ""
        txt = card.css_first(".h-bx .txt")
        out.append(Item(
            brand=BRAND,
            name=name,
            name_en=_clean(en.text()) if en else "",
            desc=_clean(txt.text()) if txt else "",
            image=src,
            category=category,
            # 사진 올린 날짜. 출시일이 아니다(docstring 참고).
            uploaded_at=_uploaded_at(src),
            # 이 사이트에는 신제품 배지가 없다. 모름을 모름으로 둔다.
            is_new=None,
            # 1+1·할인 행사가 이 사이트에 없다. 도시락 세트는 promo 가 아니다.
            promo=False,
        ))
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    seen: set = set()
    with base.client() as c:
        pages = [(MENU_URL, {"depth1": d}, nm) for d, nm in TABS.items()]
        pages.append((BOX_URL, {}, BOX_CATEGORY))

        for url, params, category in pages:
            r = base.retry(lambda: c.get(url, params=params))
            r.raise_for_status()
            time.sleep(DELAY)

            parsed = _parse(r.text, category)
            if not parsed:
                raise RuntimeError(
                    f"유가네 {category}: 상품 0건 — 셀렉터가 깨졌을 수 있다")

            for it in parsed:
                # 메뉴와 도시락에 같은 이름이 겹쳐 실린다. 먼저 만난 쪽을 남긴다.
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
    return items
