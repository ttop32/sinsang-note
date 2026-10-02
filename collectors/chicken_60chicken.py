"""60계 (60계치킨).

공정위 등록 가맹점 665개로 치킨 업종 15위다.

⚠️ **도메인은 `60chicken.co.kr` 다.** 브랜드 이름대로 `60ke.co.kr` 를 치면 NXDOMAIN 이고
`60ke.com` 은 주차 페이지다. 짐작으로 못 맞히니 적어둔다.

그누보드 사이트고 메뉴는 `/bbs/content.php?co_id=menu` **한 페이지에 전부** 서버 렌더로
들어 있다. 쿠키·세션 없이 열리고 브라우저도 불필요하다. 요청 1번이면 끝난다.
카드 하나는 `#menu div.btnlist li > div.menu_tit` 이고 그 안에
  `div.img > img`   썸네일 (`../theme/basic/img/sub/menu_img41.png`)
  `p.name`          이름. 꼬리 `<span>` 은 `(뼈/순살)`·`(콤보/윙봉/순살)` 같은
                    **주문 옵션 표기**지 상품명이 아니다. 이름에서 떼어낸다
  `p.text`          설명
  `a.btn`           'DETAIL' 버튼. **href 가 없다** — JS 팝업이라 상품별 주소가 없다

🔴 **정규식으로 긁지 마라. 48건이 정답이고 51도 33도 아니다.**
추천받은 정규식(`<img alt="" src="\\.\\./theme/basic/img/sub/(menu_img\\d+\\.\\w+)">`…)은
51건을 물고 파일명으로 접으면 32건이 되는데, **셋 다 틀린 숫자**다. 2026-10-02 실측으로
원인이 셋이었다.
  1. `menu_img<숫자>` 만 매칭한다. 살아 있는 48건 중 **20건은 이름 파일**이라
     (`menu_img_kkk.jpg`·`menu_img_horang.jpg`·`menu_img_241206_01.png` …) 통째로 빠진다.
     크크크치킨·크랑이치킨·호랑이치킨·튀밥 아이스크림 등이 그렇게 사라진다.
  2. 같은 48건이 **두 번** 나온다. 다만 'PC/모바일 중복'이 아니라, 뒤쪽
     `div.popup` 안에 **DETAIL 팝업용 복사본**(`li.row`, 알레르기 성분 `p.stxt` 포함)이
     한 벌 더 들어 있는 것이다. 두 벌의 이름 집합은 2026-10-02 실측 **완전히 같다**.
  3. 🔴 **주석 처리된 죽은 상품을 주워온다.** 이 페이지에는 단종 메뉴가 `<!-- … -->`
     안에 그대로 남아 있다(짜장계란치킨·장스치킨·6초치킨·육육치킨·해물어묵탕·
     짜장치킨 순한맛 …). 정규식은 주석 경계를 모르니 그걸 상품으로 올린다.
     selectolax 는 주석을 파싱 단계에서 버리므로 이 사고가 구조적으로 안 난다.
그래서 DOM 으로 읽는다. 결과는 **중복 없는 48건**이라 파일명으로 접을 필요도 없다
(그래도 다른 어댑터와 같게 `seen` 은 둔다).

**부분 수집 가드.** 위 2번의 팝업 복사본이 공짜 대조군이다. 같은 요청 안에서 두 벌을
모두 세고, 팝업에만 있고 목록에 없는 이름이 생기면 목록 쪽 셀렉터가 깨진 것이므로
터뜨린다. 건수만 48 → 20 으로 줄면 0건 가드에도 급감 가드에도 안 걸려서 조용히 굳는다.

🔴 **신제품 신호는 이미지 Last-Modified 하나뿐이다.**
NEW 배지도 '신메뉴' 탭도 출시일 표기도 **없다**. 그래서 **is_new 는 전건 None 이다** —
'신제품이 아니다(False)'가 아니라 '브랜드가 말해주지 않았다'는 뜻이다. 지어내지 마라.
🔴 **`pop_icon.png` 를 NEW 배지로 읽지 마라.** `div.icon` 안에 들어 있어서 배지처럼
보이는데 **48건 전부에 똑같이 붙어 있다.** 신구를 전혀 못 가른다. 썸네일을 고를 때도
`pop_icon` 이 아닌 쪽을 집어야 한다.

2026-10-02 실측 48건의 Last-Modified 분포다.
    2024-03-06 ×20   2024-04-01 ×2   2024-05-21 ×2   2024-07-07 ×1
    2024-07-28 ×1    2024-11-04 ×1   2024-12-04 ×5   2024-12-05 ×2
    2025-05-13 ×3    2025-05-20 ×5   2025-12-04 ×3   2026-06-25 ×2
    2026-07-21 ×1
13개 날짜로 흩어진다. 2024-03-06 덩어리 20건은 사이트 개편·일괄 재업로드 흔적이라
그 안에서는 신구를 못 가리지만, 나머지 28건은 제품별로 흩어져 있어 기준선으로 쓸 만하다.
최신은 크크크치킨 2026-07-21, 참지마라치킨·쯔란콤보 2026-06-25 다.
어디까지나 파일이 올라간 시각이지 브랜드가 말해준 출시일이 아니다. 그래서
**released_at 은 전건 비운다.**

⚠️ 파일명 끝 숫자(`menu_img41`·`42`)는 **보조 단서일 뿐이다.** 번호가 클수록 나중에
붙은 건 맞고 실제로 41·42 가 최신 축에 든다. 그렇지만 48건 중 20건은 번호 자체가
없고(`menu_img_kkk.jpg`), 2026-07-21 로 제일 최신인 크크크치킨이 바로 그 번호 없는
쪽이다. **번호를 날짜로 환산하지 마라.**

분류 탭이 없다. 메뉴가 치킨·사이드·안주 구분 없이 한 줄로 늘어선 단일 목록이라
Item.category 는 비운다. 상단 내비에도 메뉴 하위 분류가 없다(메뉴/매장/가맹문의/
보도자료/이벤트/고객센터 6개가 전부).

상품별 페이지가 없어 url 은 비우고 base.SITES 폴백으로 브랜드 메뉴 페이지로 보낸다
(처갓집·김가네와 같은 처분). 가격은 페이지에 없다.
'윙봉세트'·'마른안주세트'·'사이드모듬 2인/3인' 은 그 자체가 하나의 상품이지
할인·행사가 아니므로 promo 는 전건 False 다. 세트 판정은 rules.drop_sets() 담당이다.

robots.txt 는 AdsBot-Google·Googlebot·Yeti·Daumoa·KakaoBot 에게 `Allow: /` 를 주고,
`User-agent: *` 그룹에는 `/adm/`·`/data/`·`/editor/`·`/extend/`·`/lib/`·`/plugin/`·
`/skin/` 과 `/bbs/password.php` 등 회원 인증 경로 4개만 Disallow 로 적어뒀다.
우리 UA(base.UA)는 `*` 그룹에 걸리고, 우리가 읽는 `/bbs/content.php` 는 그 목록에
없으므로 허용 범위다.
"""
import time
from email.utils import parsedate_to_datetime

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "60계"
SITE = "https://60chicken.co.kr"
MENU = SITE + "/bbs/content.php?co_id=menu"

MAX_ITEMS = 200   # 폭주 방지. 현재 48건.
IMG_DELAY = 0.15  # 이미지 HEAD 간격(초). 목록은 요청 1번이다.


def _name(node) -> str:
    """`p.name` 의 상품명. 꼬리 <span> 의 주문 옵션 표기는 떼어낸다.

    떼지 않으면 이름이 '참지마라치킨 (뼈/순살)' 이 된다. 옵션 표기는 브랜드가
    수시로 고치는 자리라, 붙여두면 표기가 바뀔 때마다 Item.key 가 바뀌어
    같은 상품이 신규로 다시 올라온다. 팝업 복사본에는 아예 이 <span> 이 없어서
    두 벌을 대조하려면 어차피 떼야 한다.
    """
    p = node.css_first("p.name")
    if not p:
        return ""
    opt = p.css_first("span")
    if opt:
        opt.decompose()
    return " ".join(p.text().split())


def _image(node) -> str:
    """썸네일. `pop_icon.png` 는 전건에 붙는 장식이라 건너뛴다(위 docstring 참고)."""
    for img in node.css("div.img img"):
        src = (img.attributes.get("src", "") or "").strip()
        if src and "pop_icon" not in src:
            # `../theme/...` 상대경로다. /bbs/content.php 기준이라 ../ 를 떼면
            # 사이트 루트가 된다.
            return SITE + src[2:] if src.startswith("../") else src
    return ""


def _uploaded_at(client, img_url: str) -> str:
    """이미지의 Last-Modified 를 날짜로. 실패하면 조용히 비운다."""
    if not img_url:
        return ""
    try:
        lm = client.head(img_url).headers.get("last-modified", "")
        return parsedate_to_datetime(lm).date().isoformat() if lm else ""
    except Exception:
        return ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(MENU))
        r.raise_for_status()
        doc = HTMLParser(r.text)

        cards = doc.css("#menu .menu_tit")
        if not cards:
            raise RuntimeError("메뉴 목록이 비었다 — 셀렉터가 깨졌을 가능성")

        # DETAIL 팝업 복사본. 같은 48건이 한 벌 더 들어 있어 대조군으로 쓴다.
        names = {_name(n) for n in cards} - {""}
        popup = {_name(n) for n in doc.css("#menu li.row")} - {""}
        missing = popup - names
        if missing:
            raise RuntimeError(
                f"팝업에만 있고 목록에 없는 상품 {len(missing)}건"
                f"({', '.join(sorted(missing)[:5])}) — 셀렉터가 깨졌을 가능성")

        for node in cards[:MAX_ITEMS]:
            name = _name(node)
            if not name:
                continue
            desc = node.css_first("p.text")
            it = Item(
                brand=BRAND,
                name=name,
                desc=" ".join(desc.text().split()) if desc else "",
                image=_image(node),
                # 분류 탭이 없는 단일 목록이다. 위 docstring 참고.
                category="",
                # NEW 배지도 신메뉴 탭도 없다. pop_icon.png 는 배지가 아니다.
                # '아니다(False)'가 아니라 '브랜드가 말해주지 않았다'라서 None 이다.
                is_new=None,
                # 할인·행사 표시가 없는 카탈로그다. 세트는 promo 가 아니다
                # (rules.drop_sets() 가 이름으로 거른다).
                promo=False,
                # 상품별 페이지가 없다(DETAIL 은 href 없는 JS 팝업). SITES 폴백.
                url="",
            )
            if it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)

        for it in items:
            time.sleep(IMG_DELAY)
            it.uploaded_at = _uploaded_at(c, it.image)
    return items
