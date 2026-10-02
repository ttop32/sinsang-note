"""소림마라 — 메뉴 페이지의 NEW 배지를 쓴다.

공정위 `중식` 업종 가맹점 수 **6위**(137개, 2024년 말). (주)지씨컴퍼니글로벌.

이 브랜드는 **중식 상위권에서 드물게 메뉴 페이지가 쓸 만하다.** 마라탕 브랜드인데도
메뉴판이 '재료 바구니'가 아니라 완성된 요리 21종(마라탕·꿔바로우·전골·볶음밥…)이고,
카드마다 배지가 붙는다. 탕화쿵푸·춘리마라탕·라홍방이 재료만 늘어놓는 것과 다르다.

수집 경로. 2026-10-02 실측:
  - `/html/menu.html` 한 장에 21건이 전부 SSR 로 들어 있다. 요청 1회면 끝난다.
  - 카드가 `<li>` 이고 `.menu_list_name`(이름) / `.menu_list_deco`(배지) /
    `.menu_list_thumb` 의 `background-image:url(...)`(사진)로 구성된다.
  - 배지는 **NEW 전용이 아니라 범용**이다. 21건 중 HOT 5건, NEW 2건, 나머지 14건은
    배지가 없다(죠스떡볶이와 같은 구조). 그래서 `.menu_list_deco.new` 만 본다.
  - 화면 위쪽 탭(메인/사이드/자사상품)은 **클라이언트 필터**다. HTML 에는 21건이
    한 `<ul>` 에 다 들어 있어서 탭별로 따로 받을 필요가 없다.
  - '펍&포차 메뉴'는 별도 '메뉴 보기' 버튼이 있는데 **같은 /html/menu.html 로
    가는 링크뿐**이다(사이트 전체 `a[href*=menu]` 가 그 하나다). 팝업 안에서 JS 로
    갈리는 구조로 보이고, 공개 경로를 찾지 못했다. 그래서 받지 않는다.

🔴 **이 브랜드의 NEW 배지는 낡았다. 반드시 읽어라.**
   사진 경로에 업로드 날짜가 박혀 있다 — `/upload/menu_01/2023_09_25/hero_….png`.
   21건의 날짜를 전부 세어 보니 **2023-09-25 18건 / 2023-09-01 1건 / 2023-03-03 1건**
   이고 2024년 이후가 **0건**이다. NEW 가 붙은 두 건(짜장샹궈 2023-09-01,
   치킨꿔바로우 2023-09-25)도 3년 전 사진이다. 즉 배지는 실재하지만 **3년째 그대로**다.
   보도자료 게시판(`/board/index.php?board=sns`)도 마지막 글이 **2023-03-07** 이라
   사이트 전체가 2023년에 멈춰 있다.

   그래서 **`uploaded_at` 에 사진 업로드 날짜를 넣는다.** 날짜를 비우면 collect 가
   first_seen(=오늘)으로 떨어뜨려 3년 묵은 메뉴 2건이 '오늘의 신상'으로 올라간다.
   날짜를 넣으면 60일 창 밖이라 화면에 안 오르고, 나중에 브랜드가 사진을 갈아끼우면
   그때 자동으로 잡힌다. **`released_at` 에는 안 넣는다** — 브랜드가 말한 출시일이
   아니라 사진 올린 날이다(본아이에프 어댑터와 같은 규칙).

   ⚠️ 그러니 이 어댑터는 **지금 화면에 0건을 올린다.** 그게 정상이고 의도다.
   "건수가 0이니 고장났다"고 판단하지 마라. 고장이면 `fetch()` 가 예외를 던진다.

is_new 는 NEW 배지가 있을 때만 True 다. 배지가 없는 건 '아니다'가 아니라 '모른다'라서
None 으로 둔다(죠스떡볶이와 같은 계약). HOT 는 그냥 라벨로 남긴다.

가격·설명은 사이트 어디에도 없다(`.menu_list_text` 가 21건 전부 빈 문자열이다).
상세는 `data-idx` 로 여는 JS 팝업이라 URL 이 없다. 그래서 Item.url 을 비우고
base.SITES 의 메뉴 페이지로 떨어지게 둔다.

robots: `sorimmara.co.kr/robots.txt` → 200, text/plain. 본문이 두 줄뿐이다 —
        `User-agent: *` / `Allow:/`. 전면 허용이다.
약관: 푸터에 이용약관 링크가 없다. 수집·복제를 금지하는 문구는 찾지 못했다.
"""
import re

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "소림마라"
SITE = "https://sorimmara.co.kr"
MENU = SITE + "/html/menu.html"

# 사진 경로의 업로드 날짜. `/upload/menu_01/2023_09_25/hero_…`
_UPLOADED = re.compile(r"/upload/[^/]+/(\d{4})_(\d{2})_(\d{2})/")
_URL = re.compile(r"url\(\s*['\"]?([^'\")]+)")


def _text(node) -> str:
    return " ".join(node.text().split()) if node else ""


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(MENU))
        r.raise_for_status()

    items: list[Item] = []
    seen = set()
    for li in HTMLParser(r.text).css("li"):
        name = _text(li.css_first(".menu_list_name"))
        if not name:
            continue
        thumb = li.css_first(".menu_list_thumb")
        style = thumb.attributes.get("style", "") if thumb else ""
        m = _URL.search(style)
        img = m.group(1).strip() if m else ""
        d = _UPLOADED.search(img)
        badges = [b for b in (_text(p) for p in li.css(".menu_list_deco")) if b]
        it = Item(
            brand=BRAND,
            name=name,
            image=img if img.startswith("https://") else "",
            labels=badges,
            # 사진 올린 날이지 출시일이 아니다. released_at 에 넣지 않는다.
            uploaded_at=f"{d.group(1)}-{d.group(2)}-{d.group(3)}" if d else "",
            # NEW 만 True. 배지 없음은 '아니다'가 아니라 '모른다'다.
            is_new=True if "NEW" in badges else None,
        )
        if it.key in seen:
            continue
        seen.add(it.key)
        items.append(it)

    # 메뉴가 통째로 비면 마크업이 바뀐 것이다. 조용히 빈 목록을 돌려주지 않는다.
    if not items:
        raise RuntimeError(f"{MENU} 에서 상품을 하나도 못 찾았다. 마크업을 확인해라")
    return items
