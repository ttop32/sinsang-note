"""네네치킨.

공정위 등록 가맹점 869개로 치킨 업종 7위다.

예전 조사는 '불가 — 주문이 SPA 고 메뉴가 매장 선택에 딸려 있다'로 판정했다.
**그 판정은 틀렸다.** 주문 화면과 별개로 `/home_menu.asp` 가 SSR 이고, 그 안의
목록 조각을 그대로 돌려주는 공개 엔드포인트가 있다. 매장 선택도 쿠키도 필요 없다.

    GET /process/home_menu_list.fuse?SUBID=<분류번호>&GUBUN=MENU

응답은 HTML 조각이다. `/home_menu.asp` 페이지 안의 주석이 "검색엔진/크롤러도 실제
메뉴 목록을 바로 볼 수 있도록 서버에서 미리 렌더링" 한다고 적어뒀고, 같은 렌더링
로직(`process/_home_menu_list_render.asp`)을 이 엔드포인트가 공유한다. 브라우저 불필요.

────────────────────────────────────────────────────────────────────────
분류 번호를 짐작하지 않는다 — 내비게이션에서 읽는다
────────────────────────────────────────────────────────────────────────
SUBID 를 1..N 으로 훑으면 **가맹 브랜드가 아닌 것까지 딸려 온다.** 2026-10-02 실측:

    SUBID  1 인기메뉴  7건     2 치킨 26건    3 피자  9건
           4 밥버거·봉구스꿀맛·컵밥·봉구스사이드 **116건**
           5 후라이드 6 · 6 반반 1 · 7 반반반 1   (전부 SUBID 2 의 부분집합)
           8 사이드 23 ·  9 소스 11 · 10 음료 2
          11 네네치킨X테스트 0 · 13 배달료 2 · 14 신메뉴 1 · 15 증정메뉴 6
          22 조합메뉴 0 · 93 밥버거 38(SUBID 4 의 부분집합)

🔴 **SUBID=4 의 116건은 봉구스밥버거다. 다른 프랜차이즈다.** 같은 사이트에서 같이
   팔 뿐이고 브랜드가 다르다. 이걸 '네네치킨' 으로 올리면 그냥 틀린 데이터이고,
   봉구스는 base.BRANDS 에 등록도 안 돼 있다. **절대 넣지 않는다.**
🔴 SUBID=13 '배달료' 는 상품이 아니라 배달팁 1,000원·2,000원이다.
⚠️ SUBID 5·6·7 은 2 의 부분집합, 93 은 4 의 부분집합이다. 번호를 훑으면 중복이다.

그래서 번호를 하드코딩하지도, 범위로 훑지도 않는다. `/home_menu.asp` 의 분류
아이콘(`div.Category` → `iconBox[onclick=MENUCATEGORY('N')]` + `span.Title`)을 읽어
**사이트가 사람에게 내거는 분류만** 돈다. 2026-10-02 실측으로 그 내비에는
증정메뉴·인기메뉴·치킨·피자·사이드·소스·음료 7개만 있고 **봉구스도 배달료도 없다** —
즉 브랜드 자신이 이미 갈라놨다. 굽네(`.maintab li span`)·또래오래
(`div.tabMenu ul li a`)가 탭을 마크업에서 읽는 것과 같은 처분이다.
그래도 내비가 바뀔 날을 대비해 봉구스·배달료는 이름으로 한 번 더 막는다(SKIP_TABS).

'인기메뉴' 는 뺀다. 7건 전부 치킨 분류에 그대로 있는 **BEST 롤업**이라, 먼저 돌면
야자치킨의 분류가 '시그니처' 가 아니라 '인기메뉴' 로 굳는다. 라벨(인기)은 치킨
쪽 카드에도 똑같이 붙어 있어 잃는 게 없다(2026-10-02 실측 7/7).

분류는 내비 이름이 아니라 **조각 안의 `div.MTitle`** 에서 읽는다. 한 SUBID 안에
섹션이 여러 개 들어 있어서다 — SUBID=2 한 장에 시그니처/간장/양념/후라이드/반반/
반반반 6개가 들어 있고, 내비 이름('치킨')만 쓰면 그 구분이 통째로 사라진다.

────────────────────────────────────────────────────────────────────────
신제품 신호 = 카드 배지 `span.icon2` 의 'NEW'
────────────────────────────────────────────────────────────────────────
배지는 세 종류이고 서로 다른 뜻이다. 섞으면 안 된다.

    span.icon1  인기    = BEST. 신제품이 아니다.
    span.icon2  NEW     = 신제품. **이게 유일한 신제품 신호다.**
    span.icon3  이벤트  = 행사. 신제품이 아니다.

2026-10-03 실측 분포(내비 7개 분류, 중복 제거 전 **84건**): NEW 6 / 인기 15 /
이벤트 6 / 배지 없음 63. 선별적으로 붙는다 — 전건 True 가 되는 종류의 배지가 아니다.
(전날 '인기 11' 로 적혀 있었는데, 인기메뉴 탭 7건에도 같은 배지가 달려 있어
 중복 제거 전 기준으로는 15 가 맞다. 그 탭은 SKIP_TABS 로 빠진다.)
⚠️ NEW 6건은 **전부 증정메뉴 분류의 베트남핫스파이스 한 상품**이다(본품 1 +
   끼워팔기 5). 아래 '증정메뉴' 절에서 5건을 버리므로 **최종 is_new=True 는 1건**이다.
   6 이 안 나온다고 파서를 의심하지 마라.
NEW 면 `is_new=True`, 아니면 **False 가 아니라 None** 이다. 배지가 없다는 건
'옛날 것' 이라는 증거가 못 된다.

⚠️ 배지가 카드 한 장에 **두 번** 나온다. PC 용은 `div.imgBox > div.iconWrap`,
   모바일용은 `div.MenuTitle > div.moiconWrap` 에 같은 span 이 복제돼 있다.
   `div.MenuBox` 전체에 대고 `span.icon2` 를 세면 라벨이 두 벌 붙는다.
   **imgBox 안쪽으로 한정해서** 읽는다.
⚠️ 같은 이유로 상품명도 `div.MenuTitle` 을 `.text()` 로 통째로 읽으면 안 된다.
   그 안에 `div.moiconWrap` 이 들어 있어 'NEW 이벤트 베트남핫스파이스' 가 된다.
   **자식 텍스트 노드만** 모은다.

🔴 NEW 배지가 한 건도 안 걸리면 RuntimeError 로 터뜨린다. 건수(86)는 그대로라
collect.py 의 0건 가드도 FLOOR 도 통과하고, "네네치킨은 신제품이 없다" 가 조용히
영구화된다. 교촌(`신메뉴 목록이 비었다`)·페리카나(`신제품 엔드포인트가 비었다`)와
같은 처분이다. 브랜드가 정말로 NEW 를 다 내린 날에도 터지는데, 그 오탐은 감수한다 —
신호가 사라진 걸 모르고 지나가는 쪽이 훨씬 나쁘다.

⚠️ '신메뉴'(SUBID=14, 케이준스노윙 1건)는 **내비에 없는 숨은 분류**다. 사람이 사이트
   어디서도 닿을 수 없고 설명문이 상품명과 같은(=미입력) 준비 중 데이터로 보인다.
   내비에 올라오면 그때 자동으로 따라 들어온다 — 우리가 번호로 끌어오지 않는다.

────────────────────────────────────────────────────────────────────────
증정메뉴 — 본품은 담고 끼워팔기는 버린다
────────────────────────────────────────────────────────────────────────
2026-10-02 실측 SUBID=15 '증정메뉴' 6건이 전부 `NEW`+`이벤트` 를 달고 있고,
그중 **5건이 끼워팔기**다.

    베트남핫스파이스                                  23,000   ← 본품
    베트남핫스파이스+네네피자볼(5개)+콜라1.25L           31,000   ← 끼워팔기
    베트남핫스파이스+포테이토치즈스틱(2개)+콜라1.25L       29,500   ← 끼워팔기
    … (오징어스틱·멘보샤·쫀득감자 조합 3건 더)

본품 '베트남핫스파이스' 는 2세대 핫후라이드로 **진짜 신제품**이고, 치킨 분류에는
안 들어 있어서 여기서 안 담으면 아예 사라진다. 반면 `+` 로 이어 붙인 5건은
구성일 뿐 신제품이 아니다.

🔴 `rules.drop_sets()` 는 이걸 못 잡는다. 이름에 '세트'·'콤보' 가 없기 때문이다.
   그래서 **증정메뉴 분류 안에서만** 이름에 `+` 가 든 행을 끼워팔기로 보고 버린다.
   ⚠️ 전역 규칙으로 올리지 마라 — 후라이드 분류의 `콤보(닭다리반(5개)+날개반(6개))`
      는 부위 조합이지 끼워팔기가 아니고, 전역으로 걸면 그게 같이 날아간다.
   세트 판정 자체는 그대로 `rules.drop_sets()` 몫이다. 여기서 흉내내지 않는다.
`이벤트` 배지가 붙은 행은 `promo=True` 로 둔다. 증정 행사가 맞다. `is_new` 가 먼저
평가되므로(`rules.is_fresh`) 신제품 판정을 가리지는 않고, 나중에 NEW 가 떨어지고
이벤트만 남는 날 제대로 걸러진다.

────────────────────────────────────────────────────────────────────────
🔴 날짜는 비운다. 이 사이트에서 날짜는 전부 가짜다.
────────────────────────────────────────────────────────────────────────
출시일·등록일을 알려주는 자리가 목록·상세 어디에도 없다. `released_at` 은 당연히 비운다.

**`uploaded_at` 도 비운다. 이미지 HEAD 를 아예 보내지 않는다.**
2026-10-02 실측 73장의 Last-Modified 분포:

    2026-02-02  60장   ← 사이트 일괄 재업로드 한 번
    2026-08-24   7장
    2026-08-11   5장
    2026-03-30   1장

82%가 한 날짜에 몰려 있다. 이걸 넣으면 수십 년 된 후라이드·양념치킨이 2026-02-02
신상으로 올라온다. 도미노피자 일괄 재업로드 때 똑같은 사고가 났었다
(`rules.untrust_bulk_dates` 가 뒤에서 걸러주긴 하지만, 애초에 안 보내는 게 맞다).
🔴 **요청 73번을 아낄 수 있다며 HEAD 를 되살리지 마라.** 날짜가 없는 쪽이
   틀린 날짜보다 낫고, 이 브랜드는 NEW 배지가 이미 신호를 주고 있다.

⚠️ 이미지 주소 끝의 `?v=20241011` 은 날짜처럼 생겼지만 **전 상품이 같은 값**인
   전역 캐시버스터다. 날짜로 읽지 마라. 떼고 쓴다.

────────────────────────────────────────────────────────────────────────
나머지 판단
────────────────────────────────────────────────────────────────────────
url   카드 onclick 의 `/home_menu_detail.asp?no=<no>&subid=<SUBID>&GUBUN=MENU` 다.
      추가 요청 없이 조립만 한다. ⚠️ 그 상세 페이지는 클라이언트 렌더라 HTML 만
      받으면 `no` 가 뭐든 같은 껍데기(73KB)가 온다 — 서버 응답으로는 검증이 안 된다
      (BBQ 의 Next.js 정적 export 와 같은 사정). 사람 브라우저에서는 정상이다.
image `/images/goods/<no>.webp|jpg|png` 에 origin 을 붙인다. 전부 https 라
      base.derive() 의 http 폐기에 안 걸린다.
가격이 `span.Price` 에 있지만 Item 에 자리가 없어 버린다.
robots: https://nenechicken.com/robots.txt 는 200 이고 `Allow : /`, Disallow 는
        `/manager/` 와 `/Program/` 둘뿐이다(2026-10-02 실측). 우리 경로
        `/process/`·`/home_menu.asp` 는 영향 없다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "네네치킨"
SITE = "https://nenechicken.com"
MENU_PAGE = SITE + "/home_menu.asp"                      # 내비(분류 목록)이자 사람이 보는 페이지
FRAG = SITE + "/process/home_menu_list.fuse"             # 목록 조각 엔드포인트

DELAY = 0.4          # 분류 요청 간격(초). robots 에 Crawl-delay 는 없다
MAX_CATEGORIES = 30  # 폭주 방지. 현재 내비 7개.
MAX_ITEMS = 300      # 폭주 방지. 현재 86건(중복 제거 전).

# 내비에서 읽히더라도 담지 않는 분류. 지금은 내비에 없지만 들어오는 날을 대비한 방어다.
#   봉구스·밥버거 — 같은 사이트에 얹힌 **다른 프랜차이즈**다(docstring 참고)
#   배달료        — 상품이 아니라 배달팁이다
#   인기메뉴      — 치킨 분류의 BEST 롤업. 먼저 돌면 분류명을 덮어쓴다
SKIP_TABS = ("봉구스", "밥버거", "배달료", "인기메뉴")

# 끼워팔기를 버리는 분류. 여기서만 이름의 `+` 를 본다 — 전역으로 올리면
# `콤보(닭다리반(5개)+날개반(6개))` 같은 부위 조합이 같이 날아간다.
BUNDLE_TAB = "증정메뉴"

# 배지 class → 라벨. icon2(NEW)만 신제품 신호다.
BADGES = {"icon1": "인기", "icon2": "NEW", "icon3": "이벤트"}
NEW_BADGE = "NEW"

_SUBID = re.compile(r"MENUCATEGORY\('(\d+)'\)")
_NO = re.compile(r"[?&]no=(\d+)")


def _tabs(html: str) -> list:
    """내비의 분류 아이콘에서 (SUBID, 분류명)을 순서대로 읽는다.

    PC·모바일 두 벌이 같은 마크업으로 들어 있어 번호 기준으로 중복을 턴다.
    번호를 하드코딩하지 않는 이유는 docstring 참고 — 봉구스밥버거 116건이
    같은 번호 공간에 섞여 있다.
    """
    out, seen = [], set()
    for d in HTMLParser(html).css("div.Category"):
        box, title = d.css_first("div.iconBox"), d.css_first("span.Title")
        m = _SUBID.search(box.attributes.get("onclick", "") if box else "")
        name = " ".join(title.text().split()) if title else ""
        if not m or not name or m.group(1) in seen:
            continue
        seen.add(m.group(1))
        out.append((m.group(1), name))
    return out


def _name(box) -> str:
    """상품명. `div.MenuTitle` 의 **자식 텍스트 노드만** 모은다.

    .text() 를 그대로 쓰면 안쪽 `div.moiconWrap` 의 배지가 딸려 들어와
    'NEW 이벤트 베트남핫스파이스' 가 된다(모바일용 배지 복제본이다).
    """
    t = box.css_first("div.MenuTitle")
    if not t:
        return ""
    raw = "".join(n.text() for n in t.iter(include_text=True) if n.tag == "-text")
    return " ".join(raw.split())


def _labels(box) -> list:
    """배지. **imgBox 안쪽만** 본다 — MenuTitle 쪽에 같은 게 한 벌 더 있다."""
    wrap = box.css_first("div.imgBox div.iconWrap")
    if not wrap:
        return []
    out = []
    for span in wrap.css("span"):
        label = BADGES.get(span.attributes.get("class", "").strip())
        if label and label not in out:
            out.append(label)
    return out


def _image(box) -> str:
    """`/images/goods/6144.webp?v=20241011` → origin 붙이고 캐시버스터는 뗀다.

    `?v=` 는 전 상품이 같은 값인 전역 캐시버스터다. 날짜가 아니다(docstring 참고).
    """
    img = box.css_first("div.imgBox img")
    src = (img.attributes.get("src", "") if img else "").strip().split("?", 1)[0]
    if not src:
        return ""
    return SITE + src if src.startswith("/") else src


def _text(node, sel: str) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    new_badges = 0

    with base.client() as c:
        r = base.retry(lambda: c.get(MENU_PAGE))
        r.raise_for_status()
        tabs = _tabs(r.text)
        if not tabs:
            raise RuntimeError(
                "네네치킨 분류 내비가 비었다 — 'div.Category' 가 안 걸린다. "
                "셀렉터가 깨졌을 가능성. 번호로 훑는 폴백은 두지 않는다 — "
                "같은 번호 공간에 봉구스밥버거 116건이 섞여 있다")

        for subid, tab in tabs[:MAX_CATEGORIES]:
            if any(w in tab for w in SKIP_TABS):
                continue
            time.sleep(DELAY)
            d = base.retry(lambda s=subid: c.get(
                FRAG, params={"SUBID": s, "GUBUN": "MENU"}))
            d.raise_for_status()

            for inner in HTMLParser(d.text).css("div.MenuInner"):
                # 분류는 내비 이름이 아니라 조각 안의 소제목이다. SUBID 하나에
                # 섹션이 여럿 들어 있다(치킨 = 시그니처/간장/양념/후라이드/반반/반반반).
                category = _text(inner, "div.MTitle") or tab

                for box in inner.css("div.MenuBox"):
                    name = _name(box)
                    if not name:
                        continue
                    # 증정 행사 분류의 `본품+사이드+음료` 는 끼워팔기다. 이 분류
                    # 안에서만 본다 — 전역으로 올리면 부위 콤보가 같이 날아간다.
                    if tab == BUNDLE_TAB and "+" in name:
                        continue

                    labels = _labels(box)
                    if NEW_BADGE in labels:
                        new_badges += 1
                    no = _NO.search(box.attributes.get("onclick", ""))

                    it = Item(
                        brand=BRAND,
                        name=name,
                        desc=_text(box, "div.MenuInfo .InfoTxt"),
                        image=_image(box),
                        labels=labels,
                        category=category,
                        # 🔴 날짜는 둘 다 비운다. 브랜드가 준 출시일이 없고,
                        # 이미지 Last-Modified 는 82%가 2026-02-02 한 날에 몰린
                        # 일괄 재업로드다. HEAD 도 보내지 않는다(docstring 참고).
                        released_at="",
                        uploaded_at="",
                        # NEW 배지만 신호다. 인기(BEST)·이벤트는 신제품이 아니고,
                        # 배지가 없는 건 False 가 아니라 None 이다.
                        is_new=True if NEW_BADGE in labels else None,
                        # '이벤트' 배지는 증정 행사다. promo 는 할인·행사 전용이고
                        # 세트에는 찍지 않는다(rules.drop_sets() 가 이름으로 거른다).
                        promo="이벤트" in labels,
                        url=(f"{SITE}/home_menu_detail.asp"
                             f"?no={no.group(1)}&subid={subid}&GUBUN=MENU"
                             if no else ""),
                    )
                    if it.key in seen:
                        continue
                    seen.add(it.key)
                    items.append(it)
                    if len(items) >= MAX_ITEMS:
                        break

    if not items:
        raise RuntimeError(
            "네네치킨 메뉴 0건 — 'div.MenuBox' 가 안 걸린다. 셀렉터가 깨졌을 가능성")
    # 목록이 멀쩡해도 배지만 사라지면 건수는 그대로라 collect.py 의 0건 가드도
    # FLOOR 도 안 걸린다. 그 상태가 굳으면 "네네치킨은 신제품이 없다" 가 영구화된다.
    if not new_badges:
        raise RuntimeError(
            "네네치킨 NEW 배지가 0건 — 'div.imgBox div.iconWrap span.icon2' 가 "
            "안 걸린다. 이 브랜드의 유일한 신제품 신호라, 날아가도 건수는 그대로여서 "
            "아무도 못 알아챈다")
    return items
