"""카페만월경(만월경).

도메인부터 함정이다. 2026-10-02 실측 —
  manwolkyung.com   NXDOMAIN
  cafemanwol.com    NXDOMAIN
  manwolgyung.com   **남이 가져간 도메인이다.** 200/170KB 가 오는데 열어 보면
                    제목이 '카지노사이트 - 한국 유저 온라인 카지노 추천' 이고
                    본문이 전부 도박 홍보 글이다. 검색 결과 상위에 그대로 떠
                    있으니 조심해라 — 여기를 공식 사이트로 보고 긁으면 안 된다.
  **cafewhale.com** 이 진짜다. og:site_name 이 '만월경', 푸터가 '주식회사
                    만월경 | 대표이사 김재환' 이다. 브랜드가 고래(whale) 라
                    도메인이 브랜드명과 안 맞는다.

그누보드5(g5) 사이트고 SSR 이다. 메뉴는 /bbs/content.php?co_id=menu **한 장**이
전부다 — 페이징도 AJAX 도 없고 카테고리 탭은 같은 HTML 안의 div 토글이다.
**1요청이면 끝난다.** 브라우저 불필요.

상품 데이터가 전부 `div.con07_menu_box` 의 data-* 속성에 들어 있다.
  data-name / data-nameeng / data-content(설명) / data-photo(사진, 절대 https)
  data-hash(해시태그) / data-wr4~14(영양정보) / data-wr12(알레르기)
HTML 텍스트를 긁을 필요가 없다.

신제품 신호(2026-10-02 실측):
  - 메뉴 페이지에 **NEW MENU 탭과 ALL MENU 탭이 따로** 있다.
    NEW MENU = `.con6_mid_swiper_2` 스와이퍼, ALL MENU = `.con07_menu01~04`.
  - ⚠️ **NEW MENU 스와이퍼는 같은 항목을 두 번 뱉는다.** 셀 28개를 세서
    "28/82 = 34%, 버거킹급" 으로 접을 뻔했는데, 이름을 세어 보니 14개가
    정확히 2번씩이다(swiper 루프 클론). 실제는 **14건**이고 82건 대비
    **17.1%** — 탐앤탐스(17.6%)와 같은 수준이다. key 로 중복을 턴다.
  - 교차검증: NEW 14건이 ALL 82건에 **전건 포함**된다(차집합 0). NEW 전용
    목록이 따로 노는 가짜가 아니라 같은 카탈로그의 부분집합이다.
  - 내용도 맞다. 14건이 **유자레몬 7종 / 달링도넛 3종 / 랩노쉬 4종** 세 묶음
    뿐이고, 아메리카노·카페라떼 같은 상시 품목은 한 건도 안 들어 있다.
    (설빙에서 시그니처 배지를 NEW 로 세어 2013년 상품이 신상이 됐던 사고의
     반대 모양이다 — 여기는 묶음이 또렷하다.)

  🔴 **다만 이 탭은 '최근' 이 아니다.** 뉴스룸 5번 글이
     "카페 만월경, 청량한 여름 담은 '유자레몬' 신메뉴 8종 출시 06-05" 다.
     유자레몬 7종은 **넉 달 전** 출시분인데 아직 NEW MENU 에 걸려 있다.
     이디야가 2017년 상품에 NEW 를 달아둔 것과 같은 성질이고, 날짜가 없으니
     rules.is_fresh 의 STALE(90일, first_seen 기준) 가드에 맡기는 수밖에 없다.
     합류 첫날에는 이 7건이 신상으로 올라간다. 알고 올린다.

날짜는 **없다.** 지어내지 않는다. 실측한 후보와 왜 안 쓰는지 —
  - 메뉴 페이지 전체에서 날짜 문자열이 '2026-04-09' 단 하나(푸터 고지)다.
  - data-photo 파일명은 `<md5>_<토큰>_<sha1>.png` 라 시각이 없다.
  - 뉴스룸(co_id=newsroom)에 날짜가 붙은 글이 65건 있지만 **65건 중 50건이
    01-16** 이다. 13번 글이 "공식 홈페이지 새 단장 02-11" 인 걸 보면 사이트를
    옮기면서 과거 글을 한 날짜로 밀어 넣은 것이다. 연도 표기도 없다.
    남은 최신 13건(07-21 … 02-11)도 상품이 아니라 기사 단위라 어느 메뉴의
    출시일인지 이어 붙이려면 제목 키워드 매칭이라는 추측이 필요하다.
    `released_at` 에 넣을 자격이 없다.

굿즈는 없다. 82건 전부 먹는 것이다(커피·음료·티·디저트). 무인카페라 텀블러·
키링 같은 MD 라인 자체가 메뉴에 없다.

상품별 URL 도 없다 — 카드가 `<a>` 가 아니라 data-* 를 단 div 이고, 누르면
같은 페이지에서 모달이 뜬다. Item.url 을 비우고 SITES 폴백에 맡긴다.

robots.txt 200, `User-agent:*` / `Allow: /` 뿐이다(2026-10-02 확인).
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "카페만월경"
SITE = "https://cafewhale.com"
MENU_URL = f"{SITE}/bbs/content.php"
PARAMS = {"co_id": "menu"}
DELAY = 2.0

# ALL MENU 의 카테고리 탭. `.con3_top_2nd_item` 의 네 글자와 `.con07_menu01~04`
# 의 순서가 1:1 로 맞는다(2026-10-02 실측: 11 / 25 / 17 / 29건).
ALL_SECTIONS = ("con07_menu01", "con07_menu02", "con07_menu03", "con07_menu04")
TAB_SEL = ".con3_top_2nd_item"
# NEW MENU 스와이퍼. 같은 14건을 두 번 담는다(docstring 참고).
NEW_SEL = ".con6_mid_swiper_2 .con07_menu_box"

MIN_ITEMS = 40   # 이보다 적으면 마크업이 바뀐 것이다. 현재 82건.


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _abs(src: str) -> str:
    if not src:
        return ""
    if src.startswith("//"):
        return "https:" + src
    return src if src.startswith("http") else SITE + "/" + src.lstrip("/")


def _item(box, category: str) -> Item | None:
    a = box.attributes
    name = _clean(a.get("data-name"))
    if not name:
        return None
    return Item(
        brand=BRAND,
        name=name,
        name_en=_clean(a.get("data-nameeng")),
        desc=_clean(a.get("data-content")),
        image=_abs(a.get("data-photo") or a.get("data-photo2") or ""),
        category=category,
    )


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(MENU_URL, params=PARAMS))
        r.raise_for_status()
        time.sleep(DELAY)        # 1요청으로 끝나지만 다음 어댑터에 바로 안 붙는다
    doc = HTMLParser(r.text)

    tabs = [_clean(t.text()) for t in doc.css(TAB_SEL)]

    items: list[Item] = []
    seen = set()
    for i, sec in enumerate(ALL_SECTIONS):
        boxes = doc.css(f".{sec} .con07_menu_box")
        # 섹션 하나가 통째로 비면 조용한 부분수집이 된다. 드러낸다.
        if not boxes:
            raise RuntimeError(f"카페만월경 {sec}: 상품 0건 — 셀렉터가 깨졌을 수 있다")
        category = tabs[i] if i < len(tabs) else ""
        for b in boxes:
            it = _item(b, category)
            if not it or it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)

    if len(items) < MIN_ITEMS:
        raise RuntimeError(f"카페만월경 {len(items)}건 — 메뉴 구조가 바뀌었을 수 있다")

    # NEW MENU 탭. 중복 클론이 섞여 있으므로 key 집합으로 받는다.
    new_keys = set()
    for b in doc.css(NEW_SEL):
        it = _item(b, "")
        if it:
            new_keys.add(it.key)
    if not new_keys:
        raise RuntimeError("카페만월경 NEW MENU 0건 — 스와이퍼 셀렉터가 깨졌을 수 있다")

    # NEW 가 ALL 의 부분집합이 아니면 두 탭이 서로 다른 목록을 보고 있다는 뜻이다.
    # 그대로 두면 '신상인데 카탈로그에 없는' 유령이 생긴다. 드러낸다.
    if new_keys - seen:
        raise RuntimeError(
            f"카페만월경 NEW MENU 가 ALL MENU 에 없다: {sorted(new_keys - seen)[:3]}")

    # NEW 비율이 과하면 배지가 아니라 장식이다(버거킹 31% 선례). 막아 둔다.
    if len(new_keys) > len(items) // 2:
        raise RuntimeError(
            f"카페만월경 NEW {len(new_keys)}/{len(items)}건 — 배지를 믿을 수 없다")

    for it in items:
        it.is_new = it.key in new_keys

    return items
