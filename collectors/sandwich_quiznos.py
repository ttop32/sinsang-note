"""퀴즈노스(QUIZNOS).

가맹점 66개로 공정위 `패스트푸드` 업종 11위다(2025년도 정보공개서, 2024년 말
기준. 등록 영업표지는 '퀴즈노스서브', 가맹본부 (주)유썸). 이 프로젝트에
이미 있는 샌드위치 셋 — 써브웨이·이삭토스트·에그드랍 — 다음으로 큰 곳이다.

`/menu/menu.php` **한 장이 전체 메뉴를 SSR 로 담는다.** 1요청에 `li` 66장,
중복(신메뉴 칸에 겹쳐 실린 것)을 턴 62건. 쿠키·세션·JS 불필요.
칸은 7개다: new / sandwich / pizza(샐러드&피자) / soup / coffee / catering / set.

⚠️ **평문 HTTP 로 받는다.** `https://quiznos.co.kr` 는 **자체서명 인증서**라
`base.client()`(verify=True) 로는 접속 자체가 안 된다. 에그드랍과 같은 처분을
한다 — `verify=False` 로 검증을 끄지 않고(그러면 중간자를 몰래 덮어쓰는 셈),
`http://` 로 명시해 "이 연결은 처음부터 암호화되지 않았다"를 코드에 드러낸다.
받는 건 공개 메뉴 정보뿐이고 자격증명·개인정보를 보내지 않는다.
**그 대가로 이미지가 전부 버려진다** — 이미지도 같은 http 호스트라서
`base.derive()` 가 혼합 콘텐츠로 떨군다(에그드랍 73건과 같은 상황).
`Item.image` 에 담기는 하되 화면에는 사진 없는 카드로 나온다.

⚠️ **NEW 배지는 가짜다. 쓰지 마라.**
카드마다 `<span class="new_icon"><img src="/menu/img/new_icon.png" alt="new"></span>`
가 붙어 있는데, **66장 전부에 붙어 있다.** 숨김 처리라도 돼 있나 싶어
`/comm/css/sub.css` 를 받아 확인했더니 `.menuCont_in ul li a .new_icon` 에
위치·크기 규칙만 있고 `display:none` 이 없다. 즉 화면에서도 전 메뉴에 NEW 가
찍혀 있다. 2022년에 등록된 아메리카노·우유·소다까지 전부다.
세븐일레븐 '신상품' 탭과 같은 종류의 가짜 신호다.

진짜 신호는 둘이다. 2026-10-02 실측:
  is_new  `<div id="new">`('New Menu / 신메뉴') 칸에 실린 **4건**뿐이다.
          브랜드가 따로 골라 담는 칸이고 전체 62건 중 4건이라 가짜가 아니다.
          그 4건의 등록일도 2026-04-28 / 2026-08-10(2건) / 2026-09-07 로
          최근이라 앞뒤가 맞는다. 여기 안 실린 건 False 로 둔다
          (에그드랍 category=NEW, 폴바셋 newIcon 과 같은 처분).
  released_at  `data-idx` 10자리 앞 6자리가 YYMMDD 다. 62건 전부 유효한 과거
          날짜로 파싱되고 **미래 날짜가 하나도 없다**(최대 2026-09-07).
          연도 분포는 2022년 48 / 2023년 2 / 2024년 2 / 2025년 4 / 2026년 6 이고,
          2022-04 에 몰린 48건은 사이트를 새로 만들며 한꺼번에 넣은 흔적이다.
          **이삭토스트 `prdcode` 와 완전히 같은 규칙이고, 이미지 경로까지
          `/admin/data/product2/<코드>_R.jpg` 로 똑같다** — 같은 CMS 를 쓴다.
          그래서 이삭토스트와 같은 급의 유보를 단다: 브랜드가 "출시일"이라고
          써놓은 값은 아니고 등록일일 가능성이 있다. 그래도 uploaded_at 이
          아니라 released_at 에 넣는 건 이삭토스트 선례를 따른 것이다.

이미지 경로가 `/admin/` 아래라 **어댑터는 이 URL 을 절대 요청하지 않는다**
(이삭토스트와 같다). URL 을 담기만 하고 실제 요청은 방문자 브라우저가 한다.
어차피 http 라 지금은 화면에 뜨지도 않는다.

상품 상세는 같은 페이지 안의 모달(`.prdView`)이라 **주소가 없다.** 그래서
Item.url 을 비워 `base.site()` 의 메뉴 페이지로 떨어뜨린다.
설명문·가격은 목록에 없다(모달 안에 있고, 그건 JS 가 따로 받아온다).

세트메뉴(모닝 콤보·런치 콤보) 6건은 단품의 구성 메뉴다. promo 로 찍지 않는다 —
거르는 건 `collect.drop_sets()` 담당이다(이삭토스트 선례).
"""
import re

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "퀴즈노스"
HOST = "http://quiznos.co.kr"      # ↑ docstring 참조. https 는 자체서명이라 불가.
URL = HOST + "/menu/menu.php"

NEW_SECTION = "new"
# 칸 id → 화면에 쓸 분류명. 'pizza' 안에 샐러드가 같이 들어 있다(브랜드 표기 그대로).
SECTIONS = {
    "sandwich": "샌드위치",
    "pizza":    "샐러드 & 피자",
    "soup":     "스프 & 사이드",
    "coffee":   "커피 & 음료",
    "catering": "케이터링",
    "set":      "세트메뉴",
}

_IDX = re.compile(r"^(\d{2})(\d{2})(\d{2})\d{4}$")
_BG = re.compile(r"url\(\s*['\"]?([^'\")]+)")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _released_at(idx: str) -> str:
    """data-idx 앞 6자리 YYMMDD 를 날짜로. 날짜로 안 읽히면 조용히 버린다."""
    m = _IDX.match(idx or "")
    if not m:
        return ""
    y, mo, d = (int(g) for g in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return ""
    return f"20{y:02d}-{mo:02d}-{d:02d}"


def _image(li) -> str:
    """썸네일은 img[src](blank_img.png 자리표시자)가 아니라 style 의 background-image 다."""
    node = li.css_first(".prdImg img[style]")
    if not node:
        return ""
    m = _BG.search(node.attributes.get("style", "") or "")
    if not m:
        return ""
    src = m.group(1)
    return HOST + src if src.startswith("/") else src


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(URL))
        r.raise_for_status()
    t = HTMLParser(r.text)

    secs = t.css("div.menuCont_in")
    if not secs:
        raise RuntimeError("퀴즈노스: 메뉴 칸 0개 — div.menuCont_in 셀렉터가 깨졌다")

    by_key: dict = {}
    items: list[Item] = []
    for sec in secs:
        sid = sec.attributes.get("id") or ""
        cards = sec.css("li")
        if sid == NEW_SECTION and not cards:
            raise RuntimeError("퀴즈노스 신메뉴 칸: 상품 0건 — 구조가 바뀌었다")
        # 아는 칸이 비면 그것도 드러낸다. 전체 0건 가드만으로는 한 칸이 통째로
        # 빠져도 조용히 넘어간다 — 실측으로 `sandwich` 칸 하나를 비웠더니
        # 62 → 4건이 **예외 없이** 돌아왔다. 일곱 칸이 전부 같은 `li` 마크업을
        # 쓰니 한 칸만 0인 건 구조 변경이지 정상이 아니다.
        if sid in SECTIONS and not cards:
            raise RuntimeError(
                f"퀴즈노스 {SECTIONS[sid]}({sid}): 상품 0건 — 구조가 바뀌었다")

        for li in cards:
            a = li.css_first("a")
            h4 = li.css_first("h4.prdName")
            name = _clean(h4.text()) if h4 else ""
            if not a or not name:
                continue
            key = base.make_key(BRAND, name)
            if key in by_key:
                # 신메뉴 칸과 본래 칸에 같은 상품이 겹쳐 실린다.
                it = by_key[key]
                it.is_new = it.is_new or (sid == NEW_SECTION)
                if not it.category and sid != NEW_SECTION:
                    it.category = SECTIONS.get(sid, "")
                continue

            en = li.css_first("small.prdNameEng")
            it = Item(
                brand=BRAND,
                name=name,
                name_en=_clean(en.text()) if en else "",
                image=_image(li),
                category="" if sid == NEW_SECTION else SECTIONS.get(sid, ""),
                released_at=_released_at(a.attributes.get("data-idx", "")),
                # ⚠️ new_icon 은 전건에 붙어 있어 못 쓴다(docstring 참조).
                # 신메뉴 칸에 실렸는가만 본다.
                is_new=(sid == NEW_SECTION),
            )
            by_key[key] = it
            items.append(it)

    return items
