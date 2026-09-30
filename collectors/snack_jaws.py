"""죠스떡볶이.

/menu/menu.html(메인 메뉴)·/menu/side.html(사이드 메뉴)이 쿠키·세션 없이
카드를 그대로 내려준다. UTF-8, 브라우저 불필요, 2요청이면 끝난다.
바르다김선생과 같은 회사(나상균)의 같은 CMS(newriver)라 마크업이 거의 같다.

세 번째 메뉴 페이지 /menu/setmenu.html 은 받지 않는다. 조사에서 배지 유무가
미확인으로 남아 있던 곳인데, 2026-09-30 실측 결과 **상품 카드가 아예 없다.**
파티박스·죠스1~4인세트 큰 이미지 5장을 fullpage 슬라이드로 깔아놓은 게 전부라
상품명도 배지도 없다. 어차피 전부 세트라 collect.drop_sets() 가 이름으로 거른다.

**robots.txt 가 404(HTML)** 다. 허용도 금지도 아니라 간격을 길게 잡는다.
이용약관(/guide/termsofuse.html)은 확인하지 않았다. 붙이기 전에 사람이 봐야 한다.

신제품 신호 — 2026-09-30 실측.
  - `<div class="badge"><div class="new">NEW</div></div>` 가 실재한다. 다만
    **조사가 본 그대로는 아니다.** badge 는 NEW 전용이 아니라 범용 배지라서
    사이드의 '콰삭닭강정'에는 HIT 가 붙어 있다. NEW 는 14건 중 1건이다.
  - 그 1건이 하필 **'죠스떡볶이'** — 브랜드명과 같은 간판 상품이다. 신제품이라기보다
    리뉴얼이나 대표메뉴 강조일 가능성이 있다. 그래도 브랜드가 NEW 라고 써놓은 것을
    근거 없이 뒤집지는 않는다(계약: 모르면 None, 아니라고 확인돼야 False).
    배지 없는 카드도 False 가 아니라 None 이다.
  - 날짜를 주는 자리가 어디에도 없다. 이미지 파일명도 img_menu_main1.png 식이라
    날짜가 없고, 일부만 _230404 같은 꼬리가 붙어 있는데 상품이 아니라 이미지
    교체 시점이라 uploaded_at 으로도 쓰지 않는다. released_at·uploaded_at 둘 다 빈다.
    이 브랜드의 신제품 판정은 NEW 배지와 collect 의 어제 대비 diff 에 맡긴다.

가격은 사이트 어디에도 없다. url 은 카드가 가리키는 상세(view.html?seq=…)를 그대로 쓴다.
"""
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "죠스떡볶이"
ROOT = "https://jawsfood.co.kr"
DELAY = 2.5   # robots.txt 가 없는 브랜드다. 허용도 금지도 아니니 간격을 길게 잡는다.

# (분류명, 경로). setmenu.html 은 상품 카드가 없어 뺐다(위 주석 참고).
PAGES = (
    ("메인 메뉴", "/menu/menu.html"),
    ("사이드",    "/menu/side.html"),
)


def _text(node, sel) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _badges(section) -> list:
    """.badge 안의 배지 문자열들. 지금 관측되는 값은 NEW 와 HIT 둘뿐이다.

    자식 선택자로 한 단계만 내려간다. selectolax 의 node.css() 는 자기 자신도
    후보로 치기 때문에 .badge 노드에서 'div' 를 찾으면 껍데기와 알맹이가 같은
    글자로 두 번 잡힌다(NEW 가 2건으로 세어졌다).
    """
    return [t for t in (" ".join(d.text().split())
                        for d in section.css(".badge > div")) if t]


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        for category, path in PAGES:
            r = base.retry(lambda: c.get(ROOT + path))
            r.raise_for_status()
            time.sleep(DELAY)

            for sec in HTMLParser(r.text).css("#contents .menu_list section"):
                name = _text(sec, ".tit")
                link = sec.css_first("a")
                if not name or not link:
                    continue
                img = sec.css_first(".img_area img")
                badges = _badges(sec)
                it = Item(
                    brand=BRAND,
                    name=name,
                    # 설명 자리가 페이지마다 다르다. 메인은 p.desc, 사이드는
                    # p.subtit-2 다(subtit-1 은 '콰삭!꾸덕' 같은 머리 문구라 뺀다).
                    desc=_text(sec, ".desc") or _text(sec, ".subtit-2"),
                    image=img.attributes.get("src", "") if img else "",
                    labels=badges,
                    category=category,
                    # NEW 만 True 로 올린다. 배지 없음은 '아니다'가 아니라 '모른다'다.
                    is_new=True if "NEW" in badges else None,
                    url=link.attributes.get("href", ""),
                )
                if it.key in keys:
                    continue
                keys.add(it.key)
                items.append(it)
    return items
