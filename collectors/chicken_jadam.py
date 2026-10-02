"""자담치킨.

공정위 가맹점 708개(치킨 업종 14위). ejadam.co.kr 은 그누보드 기반 PHP 사이트라
목록이 전부 서버에서 렌더돼 나온다. 쿠키·세션 없이 열리고 브라우저도 불필요하다.

소스를 둘 쓴다. 성격이 정반대라 섞지 않고 역할을 나눠 둔다.

────────────────────────────────────────────────────────────────────────
① 신메뉴 전용 페이지 — 날짜가 있고 is_new=True 다 (4건)
────────────────────────────────────────────────────────────────────────
/bbs/content.php?co_id=new_menu (`<title>신메뉴 | 자담치킨</title>`). 브랜드가
직접 '신메뉴'라고 내건 페이지라 여기 실린 건 전건 is_new=True 로 둔다.
chicken_goobne.py 가 /menu/new_p 를 같은 근거로 전건 True 로 두는 것과 같다.

마크업은 `section.new_menu_list` 하나가 상품 하나다.
  `.newmenu_postimg img`  포스터
  `h5`                    캐치프레이즈
  `h2`                    상품명 (안에 span.color_orange 가 들어 있다)
  `p`                     긴 설명

⚠️ 2~4번째 section 에 `style="display: none;"` 이 붙어 있다. 슬라이더라서 그런
   것이고 **전부 실제 판매 상품이다.** display 로 거르면 3건이 통째로 사라진다.
⚠️ `alt` 속성이 틀려 있다. 뿌슐랭 포스터의 alt 가 `치즈핑 치킨 포스터`다
   (2026-10-02 실측). **상품명은 절대 alt 에서 읽지 않는다. h2 에서 읽는다.**

🔴 날짜 — 파일명이 날짜처럼 생겼지만 **거짓말이다.**
   `newmenu_postimg_25060219.jpg` 는 뿌슐랭 포스터인데 파일명대로 읽으면
   2025-06-02 다. 실제 `Last-Modified` 는 **2026-02-19** 다. 뒤 두 자리를
   잘라 읽은 25/06/02 가 아니라 250219 + 일련번호였던 셈인데, 어느 쪽으로
   읽어도 맞지 않는다. 그래서 **HTTP Last-Modified 헤더만 쓴다.**
   2026-10-02 실측 4건:
       뿌슐랭 치킨   2026-02-19
       치즈핑 치킨   2025-04-01
       맵쏘이킥 치킨 2025-02-19
       허니팝 치킨   2025-02-19
   날짜가 실제로 흩어져 있어 일괄 재업로드가 아니다. 다만 어디까지나 파일
   업로드 시각이지 브랜드가 말해준 출시일이 아니라서 released_at 이 아니라
   **uploaded_at** 까지만 쓴다(chicken_kyochon.py·chicken_bbq.py 와 같은 선).
   누가 "요청을 줄이자"며 파일명 정규식으로 되돌리지 않도록 여기 박아 둔다.

ℹ️ **이 페이지는 낡았다.** 가장 최신이 2026-02-19 로 7개월 전이다. 그래서
   rules.is_fresh() 의 날짜 창에 걸려 지금은 한 건도 화면에 안 올라간다.
   그게 맞는 동작이다 — 자담이 새 포스터를 올리는 날 올라간다.

────────────────────────────────────────────────────────────────────────
② 전체 메뉴 게시판 — 날짜가 없다. 그래도 넣는다 (약 68건)
────────────────────────────────────────────────────────────────────────
/bbs/board.php?bo_table=menuChicken (31건, 2페이지) · menuPizza (6건) ·
menuEtc (31건). 그누보드 light_gallery 스킨이라 `ul#grid > li` 가 카드,
`ul#information > li#infoN` 이 그 카드의 상세(큰 이미지·설명·알레르기)다.
카드의 `a.more[href="#infoN"]` 이 둘을 잇는다.

🔴 이 게시판 이미지는 **전건 Last-Modified 가 2026-09-15 다**(2026-10-02 실측).
   일괄 재업로드라 날짜로서 아무 뜻이 없다. 가짜 최신 날짜를 68건에 붙이면
   그날 하루 화면이 자담으로 도배된다 — 도미노 2026-09-14 재업로드 9건이
   실제로 그 사고를 냈다(rules.is_fresh() 주석 참고). 그래서
   **uploaded_at="" · is_new=None** 으로 둔다. Last-Modified HEAD 도 아예
   보내지 않는다 — 쓰지 않을 값을 받자고 68요청을 더 쏠 이유가 없다.

   그러면 왜 넣나. ①번 페이지가 7개월째 멈춰 있어서, 자담이 진짜 새 메뉴를
   내면 **게시판에 먼저 뜬다.** 날짜도 배지도 없는 행은 collect.py 의
   '어제 없던 키가 오늘 있다' 경로로만 판정되는데, 그러려면 어제치가 쌓여
   있어야 한다. 지금 안 넣으면 그 비교 대상이 영영 생기지 않는다.
   합류 첫날 68건은 collect.py 가 baseline 으로 깔아주므로(브랜드 신규 합류
   경로) '오늘 신규' 를 오염시키지 않는다.

   비용은 요청 4번과 날짜 없는 행 68개다. 날짜가 없는 건 숨기지 않고 비워
   두므로 shown_date() 가 빈칸을 찍는다 — 모르는 날짜를 지어내는 것보다 낫다.

⚠️ menuChicken 은 2페이지다(18+13). 페이지를 안 돌면 13건이 조용히 빠진다.
   `#bo_list_total` 의 'Total N건' 과 실제 수집 건수를 대조해 모자라면 터뜨린다.
⚠️ 게시판에 세트가 섞여 있다('3반치킨세트', bo_cate 의 '세트메뉴' 분류).
   여기서는 거르지 않는다 — 세트 판정은 collect.drop_sets() 가 이름으로 한다.
   promo 도 찍지 않는다. promo 는 할인·행사 전용이고 이 사이트엔 그 표시가 없다.

ℹ️ ①과 ②는 이름이 겹친다('뿌슐랭 치킨' ↔ '뿌슐랭치킨'). base.make_key() 가
   공백을 털기 때문에 같은 키가 되고, **①을 먼저 돌려** seen 으로 ②쪽을
   버린다. 날짜와 is_new 를 가진 쪽이 남아야 한다 — 순서를 바꾸지 마라.

────────────────────────────────────────────────────────────────────────
나머지 판단
────────────────────────────────────────────────────────────────────────
url   ① 신메뉴 페이지에는 상품별 앵커가 없다. 4건 모두 신메뉴 페이지를 가리킨다.
      ② 게시판은 상품별 주소도 없지만 `#infoN` 이 CSS `:target` 으로 모달을
         여는 진짜 앵커다(skin/board/light_gallery/css/css3_3d.css 에
         `#information li[id]:target` 규칙 확인). 그래서
         `board.php?bo_table=…&page=N#infoM` 까지 만들어 준다. N·M 은 그 페이지
         안의 순번이라 게시판 순서가 바뀌면 어긋날 수 있다 — 매 수집마다
         다시 만들어지므로 당일분은 항상 맞는다.
image 사이트가 `https://www.ejadam.co.kr:443/...` 로 기본 포트를 명시해 준다.
      동작엔 지장이 없지만 지저분해서 `:443` 만 떼고 쓴다. 전부 https 라
      base.derive() 의 http 폐기에 걸리지 않는다.
      게시판은 썸네일(`thumb-…_320x300.jpg`) 말고 상세의 큰 이미지를 쓴다.
desc  ① h5(캐치프레이즈)+p(설명). ② 상세의 설명 문단. '[알레르기 유발 식품
      표시]' 부터는 설명이 아니라 고지라서 버린다.
가격은 어느 쪽에도 없다.
robots: https://www.ejadam.co.kr/robots.txt 는 `Allow: /` 에 Disallow 가 딱 하나,
        `/bbs/board.php?bo_table=menuBurger` 다. 운영자 판단으로 robots 를
        따르지 않기로 돼 있지만, **그 한 줄은 존중해서 menuBurger 는 안 읽는다**
        — 브랜드가 유일하게 명시적으로 빼달라고 한 경로다.
"""
import re
import time
from email.utils import parsedate_to_datetime

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "자담치킨"
SITE = "https://www.ejadam.co.kr"
NEW_MENU = SITE + "/bbs/content.php?co_id=new_menu"
BOARD = SITE + "/bbs/board.php"

# (bo_table, 화면상 분류). menuBurger 는 robots 가 명시적으로 막은 유일한 경로라 뺀다.
BOARDS = [
    ("menuChicken", "치킨"),
    ("menuPizza", "피자"),
    ("menuEtc", "사이드"),
]

DELAY = 0.4       # 요청 간격(초). robots 에 Crawl-delay 는 없다.
IMG_DELAY = 0.15  # 포스터 HEAD 간격(초). 4건뿐이다.
MAX_PAGES = 10    # 폭주 방지. 현재 최대 2페이지(menuChicken).
MAX_ITEMS = 300   # 폭주 방지. 현재 72건.

_TOTAL = re.compile(r"Total\s*([\d,]+)\s*건")
# 그누보드가 기본 포트를 박아 준다. 동작엔 지장 없지만 떼고 쓴다.
_PORT443 = re.compile(r"^https://([^/]+):443/")


def _text(node, sel: str) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _img(url: str) -> str:
    return _PORT443.sub(r"https://\1/", (url or "").strip())


def _uploaded_at(client, img_url: str) -> str:
    """포스터의 Last-Modified 를 날짜로. 실패하면 조용히 비운다.

    파일명은 날짜처럼 생겼지만 틀렸다 — docstring 의 🔴 항목 참고.
    """
    if not img_url:
        return ""
    try:
        lm = client.head(img_url).headers.get("last-modified", "")
        return parsedate_to_datetime(lm).date().isoformat() if lm else ""
    except Exception:
        return ""


def _new_menu(client) -> list[Item]:
    """① 신메뉴 전용 페이지. 전건 is_new=True, 날짜는 포스터 Last-Modified."""
    r = base.retry(lambda: client.get(NEW_MENU))
    r.raise_for_status()
    secs = HTMLParser(r.text).css("section.new_menu_list")
    if not secs:
        raise RuntimeError(
            "자담치킨 신메뉴 0건 — 'section.new_menu_list' 가 안 걸린다. "
            "셀렉터가 깨졌을 가능성")

    out = []
    for s in secs[:MAX_ITEMS]:
        # 상품명은 h2 에서만 읽는다. img[alt] 는 틀려 있다(docstring ⚠️).
        name = _text(s, "h2")
        if not name:
            continue
        img = s.css_first(".newmenu_postimg img")
        src = img.attributes.get("src", "") if img else ""
        desc = " ".join(t for t in (_text(s, "h5"), _text(s, "p")) if t)
        out.append(Item(
            brand=BRAND,
            name=name,
            desc=desc,
            image=_img(SITE + src if src.startswith("/") else src),
            labels=["신메뉴"],
            category="치킨",
            is_new=True,          # 브랜드가 '신메뉴' 라고 내건 페이지다
            promo=False,          # 할인·행사 표시가 없다
            url=NEW_MENU,         # 상품별 앵커가 없다
        ))
    return out


def _board_page(client, bo_table: str, category: str, page: int) -> tuple:
    """게시판 한 페이지. (상품 목록, 게시판이 밝힌 전체 건수) 를 돌려준다."""
    r = base.retry(lambda: client.get(
        BOARD, params={"bo_table": bo_table, "page": page}))
    r.raise_for_status()
    tree = HTMLParser(r.text)

    m = _TOTAL.search(_text(tree, "#bo_list_total"))
    total = int(m.group(1).replace(",", "")) if m else -1

    # 카드(`ul#grid > li`)와 상세(`ul#information > li#infoN`)를 href 로 잇는다.
    details = {li.attributes.get("id", ""): li
               for li in tree.css("ul#information > li")}

    out = []
    for li in tree.css("ul#grid > li"):
        name = _text(li, "h3")      # h3 안에 <b class="sch_word"> 가 섞여 있다
        if not name:
            continue
        a = li.css_first("a.more")
        frag = (a.attributes.get("href", "") if a else "").lstrip("#")
        detail = details.get(frag)

        # 큰 이미지가 있으면 그쪽을, 없으면 카드 썸네일을 쓴다.
        img = detail.css_first(".info-modal > p img") if detail else None
        if img is None:
            img = li.css_first("img")
        image = _img(img.attributes.get("src", "") if img else "")

        # 설명 문단. '[알레르기 유발 식품 표시]' 부터는 고지라 버린다.
        desc_parts = []
        if detail:
            for p in detail.css(".info-chicken p"):
                t = " ".join(p.text().split())
                if not t or t.startswith("[알레르기"):
                    break
                desc_parts.append(t)

        out.append(Item(
            brand=BRAND,
            name=name,
            desc=" ".join(desc_parts),
            image=image,
            category=category,
            # 이미지 Last-Modified 가 전건 2026-09-15 인 일괄 재업로드라
            # 날짜로 쓸 수 없다. 비워 둔다(docstring 🔴).
            uploaded_at="",
            # 신제품 표시가 게시판에 없다. '아니다' 의 근거도 없으니 None.
            is_new=None,
            # 세트가 섞여 있지만 promo 가 아니다. collect.drop_sets() 담당.
            promo=False,
            url=f"{BOARD}?bo_table={bo_table}&page={page}"
                + (f"#{frag}" if frag else ""),
        ))
    return out, total


def _board(client, bo_table: str, category: str) -> list[Item]:
    """게시판 전체. 페이지를 끝까지 돌고 'Total N건' 과 대조한다."""
    rows: list[Item] = []
    total = -1
    for page in range(1, MAX_PAGES + 1):
        if page > 1:
            time.sleep(DELAY)
        got, total = _board_page(client, bo_table, category, page)
        if not got:
            break
        rows += got
        if len(rows) >= MAX_ITEMS:
            break

    if not rows:
        raise RuntimeError(
            f"자담치킨 {bo_table} 0건 — 'ul#grid > li' 가 안 걸린다. "
            f"셀렉터가 깨졌을 가능성")
    # 게시판이 스스로 밝힌 건수와 맞춰 본다. 페이지네이션을 놓치면 여기 걸린다.
    if total > 0 and len(rows) < total:
        raise RuntimeError(
            f"자담치킨 {bo_table} 부분수집 — 게시판은 {total}건이라는데 "
            f"{len(rows)}건만 받았다. 페이지네이션이 깨졌을 가능성")
    return rows


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        # ① 신메뉴를 **먼저** 넣는다. 게시판과 이름이 겹칠 때 날짜·is_new 를
        #    가진 쪽이 남아야 한다(docstring ℹ️).
        sources = [_new_menu(c)]
        for bo_table, category in BOARDS:
            time.sleep(DELAY)
            sources.append(_board(c, bo_table, category))

        for rows in sources:
            for it in rows:
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)

        # 포스터 Last-Modified. 신메뉴 4건에만 보낸다 — 게시판 이미지는
        # 전건 같은 날짜라 받아 봐야 쓸 수 없다(docstring 🔴).
        for it in items:
            if it.is_new is True and it.image:
                time.sleep(IMG_DELAY)
                it.uploaded_at = _uploaded_at(c, it.image)
    return items
