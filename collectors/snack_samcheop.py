"""삼첩분식.

씨지에프(주)(CGF, 894800359, 대구 달서구). 공정위 `분식` 232개점.
`notes/CANDIDATES-THIN.md` §1 이 **"robots 302 → 미확인"** 으로 남겨 둔 건이다.
2026-10-02 에 해소했다 — robots 는 **200 / 21바이트 / `User-agent:* / Allow: /`** 이고,
사이트는 멀쩡히 살아 있다. 도메인은 `samcheop.com` 이 맞다(cafe24 호스팅).

## ⚠️ 게시판 주소가 둘인데 하나는 막혀 있다

이 사이트는 같은 글을 두 경로로 낸다.

    /bbs/board.php?bo_table=main_event          → 403 "목록을 볼 권한이 없습니다"
    /bbs/content.php?co_id=news&tab=1           → 200. 같은 글이 전부 들어 있다

검색엔진에 색인된 건 앞쪽(`board.php?...&wr_id=44`)이고 **목록이 막혀 있다.**
그것만 보고 "게시판을 못 읽는다"로 판정하면 살아 있는 소스를 버린다.
뒤쪽 `content.php` 가 테마가 감싼 같은 게시판이고 **목록이 열려 있다.**
글 하나하나를 `wr_id` 로 찍어 보는 식으로 우회하지 않는다 — 그럴 필요가 없다.

## 두 소스를 합친다

**① 메뉴 — `/bbs/content.php?co_id=menu&tab=1` 한 장(74KB)에 6개 탭이 전부 들어 있다.**
`tab` 값은 화면에서 어느 탭을 열어 둘지만 정하고 **응답은 같다**(tab=1 과 tab=3 이
바이트까지 동일). 그래서 **1요청**이면 끝난다.

    <div class="swiper_menuwrap_in on">          ← 첫 묶음이 '신메뉴'
      <div class="swiper_menu_slide"
           data-name="불닭호오박인절미 떡볶이"
           data-nameeng="Buldak Pumpkin Injeolmi Tteokbokki"
           data-content="불닭팽이와 달달한 호박인절미의 조합"
           data-photo="https://samcheop.com/data/file/main_menu/…png">

탭이 6개(New 신메뉴 · 1첩 떡볶이 · 2첩 토핑 · 3첩 사이드 · 더하다 튀김 · Set 세트메뉴)이고
`.swiper_menuwrap_in` 묶음도 6개라 순서대로 짝이 맞는다. 2026-10-02 실측 건수는
**3 / 7 / 8 / 8 / 13 / 3 = 42건**이다.

**신메뉴 묶음 3건은 상품별 배지가 아니라 큐레이션된 별도 탭**이다 — 세 건이
다른 탭에도 그대로 또 나온다(로제샹궈 떡볶이는 1첩에, 하오츠 꿔바로우는 2첩에).
김가네의 신메뉴 탭과 같은 성격이고, 전수(42/42)가 아니라 3/42 라 섹션 장식도 아니다.

**② 새소식 — `/bbs/content.php?co_id=news&tab=1` 에 날짜가 있다.**

    <div class="swiper_news_slide" data-title="불닭 호오박 인절미 떡볶이" data-date="26.06.01">

최신 글이 **2026-08-05** 로 살아 있다(이 조사에서 본 분식 게시판 중 가장 신선하다).
`출시` 가 든 글이 꾸준하다 — 26.06.01 · 26.02.02 · 25.06.20 · 25.03.29 · 25.02.17 …

그래서 **메뉴에서 상품을, 새소식에서 출시일을 가져와 이름으로 붙인다.**
붙은 것만 `released_at` 이 차고, 못 붙은 건 **비운다**(추정해서 채우지 않는다).
2026-10-02 실측으로 신메뉴 3건 중 2건이 붙는다.

⚠️ **띄어쓰기가 두 소스에서 다르다.** 새소식은 `불닭 호오박 인절미 떡볶이`,
메뉴는 `불닭호오박인절미 떡볶이` 다. 공백을 턴 뒤 맞춘다. 제목에서
`신메뉴`·`출시` 같은 꾸밈말도 턴다. 그래도 안 붙는 건 그냥 둔다 — 느슨하게
맞추면 `마라로제 떡볶이 출시 5주년 기념 반값 이벤트`(행사 글)가 상품에 붙는다.

⚠️ 새소식에는 행사·콜라보 글이 섞여 있다(`반값 이벤트`·`쿠키런 콜라보레이션`·
`삼첩박스 출시`). 이름이 정확히 같을 때만 붙이므로 그 글들은 저절로 안 붙지만,
`출시` 가 든 글만 후보로 두어 한 겹 더 막는다.

## 날짜를 메뉴 쪽에서 줍지 않는 이유
`data-photo` 가 `/data/file/main_menu/…` 로 날짜가 없는 해시 경로다. 주울 게 없다.
(있었더라도 업로드 시각이라 안 썼을 것이다 — 김가네 반례 참고.)

상품별 주소는 **없다.** 카드가 `data-*` 를 들고 있는 JS 슬라이드라 href 가 없다.
`url` 을 비워 `base.SITES` 폴백에 맡긴다. 가격은 사이트에 없다.
이미지는 전부 https 다. 이용약관은 푸터에 링크가 없어 확인하지 못했다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "삼첩분식"
ROOT = "https://samcheop.com"
CONTENT = ROOT + "/bbs/content.php"
DELAY = 2.5

# 탭 이름이 'New 신메뉴' 처럼 두 줄로 들어 있다. 첫 묶음이 신메뉴다.
NEW_TAB = 0

_NOISE = re.compile(r"신메뉴|출시|\s+")
_DATE = re.compile(r"^(\d{2})\.\s*(\d{2})\.\s*(\d{2})$")


def _norm(name: str) -> str:
    """두 소스의 이름을 맞추는 키. 공백과 '신메뉴'·'출시' 꾸밈말을 턴다."""
    return _NOISE.sub("", name or "")


def _released(c) -> dict:
    """새소식의 '출시' 글 → {정규화 이름: YYYY-MM-DD}. 날짜가 여기에만 있다."""
    r = base.retry(lambda: c.get(CONTENT, params={"co_id": "news", "tab": 1}))
    r.raise_for_status()
    time.sleep(DELAY)

    out = {}
    for n in HTMLParser(r.text).css("div.swiper_news_slide"):
        title = " ".join((n.attributes.get("data-title") or "").split())
        m = _DATE.match(" ".join(
            (n.attributes.get("data-date") or "").split()).replace(" ", ""))
        if not (title and m and "출시" in title):
            continue
        key = _norm(title)
        # 목록이 최신순이라 먼저 본 것이 더 최근이다. 같은 상품이 두 번
        # 나오면(리뉴얼 출시 등) 처음 출시한 날을 쓰고 싶으므로 덮어쓴다.
        out[key] = f"20{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        dates = _released(c)

        r = base.retry(lambda: c.get(CONTENT, params={"co_id": "menu",
                                                      "tab": 1}))
        r.raise_for_status()
        time.sleep(DELAY)

    doc = HTMLParser(r.text)
    tabs = [" ".join(b.text().split())
            for b in doc.css(".menu_btnwrap .menu_btn")]
    groups = doc.css(".swiper_menuwrap .swiper_menuwrap_in")
    if len(tabs) != len(groups):
        # 탭과 묶음이 안 맞으면 어느 묶음이 신메뉴인지 알 수 없다. 그 상태로
        # is_new 를 찍으면 엉뚱한 상품이 신상이 된다. 조용히 넘기지 않는다.
        raise ValueError(f"{BRAND}: 탭 {len(tabs)}개 ≠ 상품묶음 {len(groups)}개")

    new_names = {(_norm(s.attributes.get("data-name") or ""))
                 for s in groups[NEW_TAB].css(".swiper_menu_slide")}
    new_names.discard("")

    for i, group in enumerate(groups):
        if i == NEW_TAB:
            continue      # 신메뉴 탭은 다른 탭의 복제라 분류로 쓰지 않는다
        category = tabs[i]
        for slide in group.css(".swiper_menu_slide"):
            name = " ".join((slide.attributes.get("data-name") or "").split())
            if not name:
                continue
            key = _norm(name)
            it = Item(
                brand=BRAND,
                name=name,
                name_en=" ".join(
                    (slide.attributes.get("data-nameeng") or "").split()),
                desc=" ".join(
                    (slide.attributes.get("data-content") or "").split()),
                image=slide.attributes.get("data-photo", ""),
                category=category,
                # 새소식에 출시 글이 있는 상품만 찬다. 없으면 비운다.
                released_at=dates.get(key, ""),
                # 신메뉴 탭에 든 것만 True. 없으면 '아니다'가 아니라 '모른다'다.
                is_new=True if key in new_names else None,
                # 상품별 주소가 없다(JS 슬라이드).
                url="",
            )
            if it.key in keys:
                continue
            keys.add(it.key)
            items.append(it)

    # 신메뉴 탭에만 있고 다른 탭엔 없는 상품도 담는다. 지금은 3건 전부 양쪽에
    # 있지만 그게 보장된 구조는 아니다.
    for slide in groups[NEW_TAB].css(".swiper_menu_slide"):
        name = " ".join((slide.attributes.get("data-name") or "").split())
        if not name:
            continue
        it = Item(
            brand=BRAND,
            name=name,
            name_en=" ".join(
                (slide.attributes.get("data-nameeng") or "").split()),
            desc=" ".join((slide.attributes.get("data-content") or "").split()),
            image=slide.attributes.get("data-photo", ""),
            category=tabs[NEW_TAB],
            released_at=dates.get(_norm(name), ""),
            is_new=True,
            url="",
        )
        if it.key in keys:
            continue
        keys.add(it.key)
        items.append(it)
    return items
