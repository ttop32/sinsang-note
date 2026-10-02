"""원앤원 2개 브랜드 — 원할머니보쌈족발 · 박가부대.

가맹점 수는 공정위 2025년도 정보공개서(2024년 말 기준)로 원할머니 278개(`한식`
13위), 박가부대 94개다. 같은 사이트 같은 템플릿이라 파일을 쪼개지 않았다.
그래서 BRAND 상수 대신 BRANDS 목록을 내보낸다(본아이에프 선례).

  GET wonandone.co.kr/bossam/menu.asp?KeyCtgM=<분류>   원할머니보쌈족발
  GET wonandone.co.kr/parkga/menu.asp?KeyCtgM=<분류>   박가부대

classic ASP 서버렌더다. 쿠키·세션·JS 불필요. 분류 11장에 75건(2026-10-02 실측).
세 번째 브랜드 감탄계숯불치킨은 치킨이라 이 프로젝트의 다른 담당 영역이고,
애초에 이 사이트에 메뉴 페이지가 없다(매장찾기만 있다).

**신제품 배지는 못 쓴다.** 카드마다 자리는 있는데 전부 주석 처리돼 있다:

    <!--<div class="ctg new">NEW</div>-->
    <!--div class="ctg best">BEST</div-->

75건 **전부** 그렇다. 하나라도 살아 있으면 썼을 텐데 한 건도 없다. 주석을
벗겨 읽는 건 하지 않는다 — 브랜드가 화면에서 내린 표시를 우리가 되살리는
셈이고, 언제 내렸는지도 모른다. 그래서 `is_new` 는 전부 None(모름)이다.

  uploaded_at  **이미지 파일명 앞 14자리가 업로드 시각**이다.
          `/_xUpFiles/xMenu/20260626174527222928617.png` → 2026-06-26 17:45:27.
          75건 전부 파싱되고, **미래 날짜가 하나도 없다**(최대 2026-06-26,
          조사일 2026-10-02). 연도 분포도 2020년 17 / 2021년 6 / 2022년 10 /
          2023년 13 / 2024년 9 / 2025년 19 / 2026년 1 로 꾸준히 쌓인 모양이다.
          에그드랍 때처럼 epoch 로 착각해 미래가 섞이는 사고는 여기선 없다.
          **released_at 에는 넣지 않는다.** 브랜드가 "출시일"이라고 말한 값이
          아니라 이미지를 올린 시각이다(본아이에프·한솥과 같은 처분).
          2025-09-12 에 16건, 2020-04-10 에 13건이 몰려 있는데 도시락 분류를
          한 번에 갈아끼운 흔적으로 보인다. 그래서 이 날짜는 '그 메뉴가 그날 나왔다'가 아니라
          '그날 이후로는 안 바뀌었다' 정도로만 읽어야 한다.

released_at 은 **못 채운다.** 목록에도 상세에도 날짜 항목이 없고, 애초에 상품
상세 페이지가 없다(카드에 링크가 걸려 있지 않다). 지어내지 않고 비운다.
같은 이유로 Item.url 은 분류 페이지까지만 건다.

이 브랜드는 `is_new` 가 없어 **합류 첫날에는 신제품을 하나도 못 내놓는다.**
그 대신 `collect.py` 가 uploaded_at 을 first_seen 으로 소급해 기준선으로
깔아두므로, 다음에 올라오는 새 메뉴부터 날짜와 함께 잡힌다. 그게 정직하다.

세트 메뉴(`50주년보족세트`·`부대찌개 세트`)는 promo 로 찍지 않는다. 할인 행사가
아니라 구성 메뉴고, 거르는 건 `collect.drop_sets()` 담당이다(이삭토스트 선례).

가격은 사이트에 없다(도시락 가격 주석 자리만 비어 있다).
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

HOST = "https://wonandone.co.kr"
DELAY = 1.2          # 요청 간격(초)

# 브랜드 → (경로 조각, [(쿼리, 분류명), …]). 분류 코드·이름은 메뉴 페이지
# 상단 탭(`.tab_mn a`)의 href 에서 그대로 옮겼다. 2026-10-02 실측.
# 박가부대는 KeyCtgM 만 주면 첫 하위 탭(세트메뉴)밖에 안 나온다. 하위 탭
# KeyCtgS 를 같이 줘야 닭갈비·부대찌개·별미가 열린다.
SECTIONS = {
    "원할머니보쌈족발": ("bossam", [
        ({"KeyCtgM": "1"},  "보쌈"),
        ({"KeyCtgM": "12"}, "족발"),
        ({"KeyCtgM": "4"},  "가마솥밥 반상"),
        ({"KeyCtgM": "6"},  "명품도시락/덮밥"),
        ({"KeyCtgM": "8"},  "국수/보쌈"),
        ({"KeyCtgM": "14"}, "정식/사이드"),
    ]),
    "박가부대": ("parkga", [
        ({"KeyCtgM": "16", "KeyCtgS": "28"}, "세트메뉴"),
        ({"KeyCtgM": "16", "KeyCtgS": "29"}, "닭갈비"),
        ({"KeyCtgM": "16", "KeyCtgS": "30"}, "부대찌개"),
        ({"KeyCtgM": "16", "KeyCtgS": "31"}, "별미메뉴"),
        ({"KeyCtgM": "17"},                  "배달메뉴"),
    ]),
}

# 레지스트리가 등록할 브랜드명. 이 모듈이 뱉는 Item.brand 는 전부 이 안에 있다.
BRANDS = list(SECTIONS)

# 파일명 앞 14자리가 YYYYMMDDHHMMSS, 그 뒤는 중복 방지용 난수다.
_STAMP = re.compile(r"/(\d{4})(\d{2})(\d{2})\d{6}\d*\.[a-zA-Z]+$")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _uploaded_at(src: str) -> str:
    """이미지 파일명 앞의 업로드 날짜. 날짜로 안 읽히면 조용히 비운다."""
    m = _STAMP.search(src or "")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        for brand, (seg, cats) in SECTIONS.items():
            got = 0
            for q, cat in cats:
                url = f"{HOST}/{seg}/menu.asp"
                r = base.retry(lambda: c.get(url, params=q))
                r.raise_for_status()
                time.sleep(DELAY)

                for li in HTMLParser(r.text).css("ul.menu_list li"):
                    strong = li.css_first(".info strong")
                    name = _clean(strong.text()) if strong else ""
                    if not name:
                        continue
                    img = li.css_first(".img img")
                    src = img.attributes.get("src", "") if img else ""
                    p = li.css_first(".info p")
                    it = Item(
                        brand=brand,
                        name=name,
                        desc=_clean(p.text()) if p else "",
                        image=HOST + src if src.startswith("/") else src,
                        category=cat,
                        uploaded_at=_uploaded_at(src),
                        url=str(r.url),
                    )
                    if it.key in keys:
                        continue      # 홀메뉴/배달메뉴에 같은 상품이 겹쳐 실린다
                    keys.add(it.key)
                    items.append(it)
                    got += 1
            if not got:
                raise RuntimeError(f"{brand}: 상품 0건 — ul.menu_list 셀렉터가 깨졌다")
    return items
