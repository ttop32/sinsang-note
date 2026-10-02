"""참토스트. 가맹점 40개. 가맹본부 (주)와이에스컴퍼니.

아임웹(imweb)이고 `/menu` **한 장(1.2MB)에 전 메뉴가 SSR** 로 들어온다. 1요청이면
끝이고 브라우저는 필요 없다. 2026-10-02 실측.

상품은 갤러리 위젯의 `div#caption_<n>`(화면에선 `display:none`) 안에 있고, 썸네일은
같은 번호의 `div#gal_item_<n>` style 배경이미지다. **둘 다 있어야 상품으로 본다.**

🔴 **아임웹이 같은 갤러리를 데스크톱용과 모바일용으로 두 번 그린다.**
`data-widget-parent-is-mobile` 가 `N` 인 벌과 `Y` 인 벌이 **내용이 완전히 같은
채로 아홉 쌍** 있다. 모르고 세면 89건이 나오는데 실제 상품은 **45건**이다.
`Y` 를 통째로 건너뛴다. 이름으로 중복을 터는 방법은 쓰면 안 된다 — 아래처럼
다른 칸에 같은 이름의 **진짜 다른 상품**이 있어서 그것까지 지워버린다.

⚠️ **같은 이름이 다른 칸에 다른 상품으로 들어 있다.** `오리지널`이 싱글토스트
(2,400원)와 에그플렉스(4,200원)에 각각 있고, `햄치즈`·`베이컨치즈`·`감자샐러드`·
`모짜렐라피자` 등도 그렇다. 이름만으로 키를 만들면 서로를 지운다. 그래서
**브랜드 안에서 겹치는 이름에 한해** 소분류를 앞에 붙여 `에그플렉스 오리지널`
처럼 만든다. 전건에 붙이면 `리얼토스트 리얼햄치즈스페셜` 같은 군더더기가 생긴다.
겹치는 쪽만 바꾸므로 **브랜드가 겹치는 상품을 새로 추가하면 그때 키가 한 번
바뀐다**(그건 실제 변화라 감수한다).
소분류(리얼토스트 / 싱글토스트 / 에그플렉스 / 참맛도그 / 커피 / 라떼 / 에이드 /
티 / 1리터)는 갤러리 바로 앞 텍스트 위젯에서 읽는다. 브랜드 표기 그대로다.

**신제품 신호는 이미지 CDN 경로의 날짜뿐이다.** NEW 배지도 '신메뉴' 칸도 없다
(`/menu` 전체에서 `NEW`·`신메뉴` 문자열 0건). `cdn.imweb.me/thumbnail/YYYYMMDD/`
의 YYYYMMDD 가 상품마다 갈린다(데스크톱 벌 45건 기준).

  20250304 19건   20231010 17건   20220318 6건   20231012 3건
  20231016 1건    20220329 1건

2022·2023 위에 2025-03 이 한 뭉치 얹혀 있다. 증분 업로드가 실제로 돈다.
**`uploaded_at` 까지만이다 — `released_at` 로 올리지 않는다**(본아이에프 선례).
`is_new` 는 비운다(None). 가장 최근이 2025-03-04 라 지금(2026-10) 화면에 오를
건 없지만, 다음에 올라오는 건 잡는다.

⚠️ 날짜를 믿기 전에 교차검증을 했다. 같은 아임웹인 **쑝쑝돈까스에서 '당일 날짜
4건'이 상품이 아니라 로고였고**, imweb CDN 이 썸네일을 다시 만들 때마다 그 날짜가
바뀐다. 여기서는 '캡션+갤러리 이미지' 조건이 로고를 애초에 상품으로 세지 않는다.

캡션의 `<p>` 는 **가격**이다 — `3.9` = 3,900원. 설명문이 아니라서 desc 에 넣지
않는다(Item 에 가격 자리가 없어 버린다). 커피 칸에 `아메리카노`만 `L size 3.0 →
2.0` 으로 할인 표기가 붙어 있는데, 그건 상시 가격 표기지 1+1·증정 같은 행사가
아니라서 `promo` 로 찍지 않는다. promo 는 행사 전용이다.

상품 상세 페이지는 없다. Item.url 은 SITES 폴백(메뉴 페이지)으로 떨어진다.

robots.txt: `Allow: /` + 아임웹 기본 Disallow(`/site_join`·`/login`·`/logout.cm`·
`/shop_cart`·`/?mode*`·`/admin`). `/menu` 와 cdn 이미지는 허용 범위다.
이용약관: `/?mode=policy` 인데 **robots 가 `/?mode*` 를 막아 받지 않았다.**
확인하지 못했다는 뜻이지 금지 조항이 없다는 뜻이 아니다(미소야·쑝쑝돈까스와 같다).
"""
import html as _html
import re

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "참토스트"
URL = "https://charmtoast.com/menu"

_CAPTION = re.compile(
    r'<div id="caption_(\d+)"[^>]*>\s*<h4>(.*?)</h4>\s*(?:<p>(.*?)</p>)?', re.S)
_TILE = re.compile(
    r'id="gal_item_(\d+)(?:_img)?"[^>]*background-image:\s*url\('
    r'(https://cdn\.imweb\.me/thumbnail/(\d{8})/[^)\s]+?)\)')

# 소제목이 아니라 가격 안내인 텍스트 위젯. 커피 칸 앞에 소제목('커피') 다음으로
# `아메리카노L size3.5 → 2.0` 이 한 장 더 끼어 있어서 분류가 그걸로 덮였다.
# 가격 표기(3.5)·화살표·size 가 들어가면 분류가 아니다. '1리터보틀' 은 소수점이
# 없어 그대로 남는다 — 숫자만으로 걸러내면 그게 같이 날아간다.
_NOT_HEADING = re.compile(r"\d+\.\d|→|->|size", re.I)


def _clean(s: str) -> str:
    return " ".join(_html.unescape(re.sub(r"<[^>]*>", " ", s or "")).split())


def _widgets(page: str) -> list:
    """데스크톱 벌의 (소제목, 갤러리 HTML)을 문서 순서대로.

    모바일 벌(`data-widget-parent-is-mobile="Y"`)은 같은 내용을 한 번 더 그린다.
    통째로 건너뛴다 — 자세한 사정은 docstring 🔴 항목 참고.
    """
    out, heading = [], ""
    for w in HTMLParser(page).css('div[doz_type="widget"]'):
        data = w.css_first("div._widget_data")
        if not data:
            continue
        if data.attributes.get("data-widget-parent-is-mobile") == "Y":
            continue
        kind = data.attributes.get("data-widget-type")
        if kind == "text":
            label = _clean(w.text())
            # 소제목만 쓴다. 긴 홍보 문구와 가격 안내는 분류가 아니다.
            if 0 < len(label) <= 24 and not _NOT_HEADING.search(label):
                heading = label
        elif kind and kind.startswith("gallery"):
            out.append((heading, w.html or ""))
    return out


def _parse(block: str) -> list:
    """갤러리 하나에서 (이름, 이미지, 업로드일). 짝 없는 캡션은 버린다.

    캡션의 <p> 는 가격이라 받지 않는다(docstring 참고).
    """
    names = {m.group(1): _clean(m.group(2)) for m in _CAPTION.finditer(block)}
    tiles = {m.group(1): (m.group(2), m.group(3)) for m in _TILE.finditer(block)}
    rows = []
    for no, name in names.items():
        if not name or no not in tiles:
            continue
        img, ymd = tiles[no]
        rows.append((name, img, f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}"))
    return rows


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(URL))
        r.raise_for_status()

    rows = []
    for heading, block in _widgets(r.text):
        for name, img, ymd in _parse(block):
            rows.append((heading, name, img, ymd))
    if not rows:
        raise RuntimeError("참토스트: 상품 0건 — 캡션·갤러리 짝짓기가 깨졌다")

    # 겹치는 이름에만 소분류를 앞에 붙인다(docstring 참고).
    counts: dict = {}
    for _, name, _, _ in rows:
        counts[name] = counts.get(name, 0) + 1

    items, seen = [], set()
    for category, name, img, ymd in rows:
        label = name
        if counts[name] > 1 and category and not name.startswith(category):
            label = f"{category} {name}"
        it = Item(
            brand=BRAND,
            name=label,
            image=img,
            category=category,
            # 이미지 올린 날이지 출시일이 아니다. released_at 으로 올리지 않는다.
            uploaded_at=ymd,
            # NEW 배지도 신메뉴 칸도 없다. 모름은 모름으로 둔다.
            is_new=None,
        )
        if it.key in seen:
            continue
        seen.add(it.key)
        items.append(it)
    return items
