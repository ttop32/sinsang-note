"""쉬즈베이글 커피. 가맹점 79개 — 담당 샌드위치·토스트 12곳 중 1위.
가맹본부 (주)쉬즈베이글(561-81-01202).

아임웹(imweb)이고 메뉴가 네 장으로 나뉜다. 주소는 상단 네비게이션에 그대로 적혀
있다(숫자 경로가 아니라 말로 된 경로라 덜 바뀐다). 2026-10-02 실측.

  /toastandbread      토스트 / 베이글 / 랩          42건
  /51                 샐러드 / 샌드위치 / 그릭요거트   21건
  /coffeeandtea       커피 / 티                   43건
  /juiceandbeverage   과일쥬스 / 음료               40건
4요청에 146건. SSR 이라 브라우저 불필요.

상품은 갤러리 위젯의 `div#caption_<n>`(화면에선 `display:none`) 안에 있고,
썸네일은 같은 번호의 `div#gal_item_<n>` style 에 배경이미지로 들어간다.
**둘 다 있어야 상품으로 본다** — 짝 없는 캡션은 브랜드 문구라서 이 조건이 걸러준다.

**신제품 신호는 이미지 CDN 경로의 날짜뿐이다.** NEW 배지도 '신메뉴' 칸도 없다
(네 장 전체에서 `NEW`·`신메뉴` 문자열 0건). `cdn.imweb.me/thumbnail/YYYYMMDD/` 의
YYYYMMDD 가 상품마다 갈린다.

  20201212 45건  20210919 29건  20220227 24건  20231021 17건
  20220116 13건  20241129 12건  20220821 4건   20210606 2건
  (2026-10-02 실측 합계 146건. 전에 20231021 을 11건으로 적어 합이 140이었다.)

2020~2021 에 몰아 올린 위에 2022·2023·2024 가 얹혀 있다. 증분 업로드가 실제로 돈다.
**`uploaded_at` 까지만이다 — `released_at` 로 올리지 않는다**(본아이에프 선례).
`is_new` 는 비운다(None). 가장 최근이 2024-11-29 라 지금(2026-10) 화면에 오를 건
없지만, 다음에 올라오는 건 잡는다.

⚠️ 날짜를 믿기 전에 교차검증을 했다. 같은 아임웹인 **쑝쑝돈까스에서 '당일 날짜
4건'이 상품이 아니라 로고였고**, imweb CDN 이 썸네일을 다시 만들 때마다 그 날짜가
바뀐다. 여기서도 로고가 `thumbnail/20251108/`·`20191117/` 로 잡히는데, 위의
'캡션+갤러리 이미지' 조건이 로고를 애초에 상품으로 세지 않는다.
**상품에 붙은 날짜만 세라.**
🔵 2026-10-02 에 여덟 묶음 전부 표본을 HEAD 로 쳐서 경로 날짜와 `Last-Modified`
가 같은 날인 걸 확인했다(2020-12-12 ~ 2024-11-29). 경로가 3~6년 전 날짜를
그대로 들고 있으니 '요청할 때마다 다시 만들어진다'는 쪽이 아니다.

⚠️ **아임웹은 같은 갤러리를 데스크톱용·모바일용으로 두 번 그리기도 한다.**
참토스트가 그래서 146개 캡션으로 부풀어 있었다(실제 73). 쉬즈베이글 네 장은 전부
`data-widget-parent-is-mobile="N"` 한 벌뿐이라 지금은 중복이 없지만, 브랜드가
모바일 전용 섹션을 넣으면 바로 두 배가 된다. 그래서 **데스크톱 벌만** 읽는다.

⚠️ **같은 이름이 다른 칸에 다른 상품으로 들어 있다.** 과일쥬스/음료 한 장 안에만도
`딸기`가 생과일주스·스무디·쉐이크에 각각 있고 `오레오`도 둘이다. 이름만으로 키를
만들면 서로를 지운다. 그래서 **브랜드 안에서 겹치는 이름에 한해** 소분류를 앞에
붙여 `스무디 딸기` 처럼 만든다. 전건에 붙이지 않는 건 안 겹치는 이름까지 바꾸면
읽기만 나빠지기 때문이고, 겹치는 쪽만 바꾸므로 **브랜드가 겹치는 상품을 새로
추가하면 그때 키가 한 번 바뀐다**(그건 실제 변화라 감수한다).
소분류는 갤러리 바로 앞 텍스트 위젯에서 읽는다. 브랜드 표기 그대로다.

캡션의 `<p>` 는 설명이 든 것과 빈 것이 섞여 있다. 있는 것만 desc 로 담는다.
가격은 사이트 어디에도 없다. 상품 상세 페이지도 없어 Item.url 은 SITES 폴백이다.

robots.txt: `Allow: /` + 아임웹 기본 Disallow(`/site_join`·`/login`·`/logout.cm`·
`/shop_cart`·`/?mode*`·`/admin`). 우리가 받는 네 장과 cdn 이미지는 허용 범위다.
이용약관: `/?mode=policy` 인데 **robots 가 `/?mode*` 를 막아 받지 않았다.**
확인하지 못했다는 뜻이지 금지 조항이 없다는 뜻이 아니다(미소야·쑝쑝돈까스와 같다).
"""
import html as _html
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "쉬즈베이글"
HOST = "https://shesbagel.com"
DELAY = 1.5          # 요청 간격(초)

# 경로 → 화면 분류. 상단 네비게이션의 MENU 하위 항목 그대로다.
PAGES = {
    "/toastandbread":    "토스트 / 베이글 / 랩",
    "/51":               "샐러드 / 샌드위치 / 그릭요거트",
    "/coffeeandtea":     "커피 / 티",
    "/juiceandbeverage": "과일쥬스 / 음료",
}

# 숨은 캡션. <h4> 이름 + (있으면) <p> 설명.
_CAPTION = re.compile(
    r'<div id="caption_(\d+)"[^>]*>\s*<h4>(.*?)</h4>\s*(?:<p>(.*?)</p>)?', re.S)
# 같은 번호의 갤러리 타일. `_img` 꼬리가 붙는 스킨도 있어 선택적으로 받는다.
_TILE = re.compile(
    r'id="gal_item_(\d+)(?:_img)?"[^>]*background-image:\s*url\('
    r'(https://cdn\.imweb\.me/thumbnail/(\d{8})/[^)\s]+?)\)')


def _clean(s: str) -> str:
    """태그를 털고 엔티티를 풀어 한 줄로."""
    return " ".join(_html.unescape(re.sub(r"<[^>]*>", " ", s or "")).split())


def _widgets(page: str) -> list:
    """데스크톱 벌의 (소제목, 갤러리 HTML) 목록을 문서 순서대로.

    아임웹은 위젯을 평평하게 늘어놓는다. 텍스트 위젯이 소제목이고 그 다음에 오는
    갤러리 위젯이 그 소제목의 상품들이다. 모바일 벌은 같은 내용을 한 번 더 그리므로
    `data-widget-parent-is-mobile="Y"` 는 통째로 건너뛴다.
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
            # 소제목만 쓴다. 긴 홍보 문구는 분류가 아니다.
            heading = label if 0 < len(label) <= 24 else heading
        elif kind and kind.startswith("gallery"):
            out.append((heading, w.html or ""))
    return out


def _parse(block: str) -> list:
    """갤러리 하나에서 (이름, 설명, 이미지, 업로드일). 짝이 없는 캡션은 버린다."""
    names = {m.group(1): (_clean(m.group(2)), _clean(m.group(3)))
             for m in _CAPTION.finditer(block)}
    tiles = {m.group(1): (m.group(2), m.group(3)) for m in _TILE.finditer(block)}
    rows = []
    for no, (name, desc) in names.items():
        if not name or no not in tiles:
            continue
        img, ymd = tiles[no]
        rows.append((name, desc, img, f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}"))
    return rows


def fetch() -> list[Item]:
    rows = []
    with base.client() as c:
        for path, label in PAGES.items():
            r = base.retry(lambda: c.get(HOST + path))
            r.raise_for_status()
            found = 0
            for heading, block in _widgets(r.text):
                for name, desc, img, ymd in _parse(block):
                    rows.append((heading or label, name, desc, img, ymd))
                    found += 1
            if not found:
                raise RuntimeError(
                    f"쉬즈베이글 {label}({path}): 상품 0건 — 갤러리 셀렉터가 깨졌다")
            time.sleep(DELAY)

    if not rows:
        raise RuntimeError("쉬즈베이글: 상품 0건")

    # 겹치는 이름에만 소분류를 앞에 붙인다(docstring 참고).
    counts: dict = {}
    for _, name, _, _, _ in rows:
        counts[name] = counts.get(name, 0) + 1

    items, seen = [], set()
    for category, name, desc, img, ymd in rows:
        label = name
        if counts[name] > 1 and category and not name.startswith(category):
            label = f"{category} {name}"
        it = Item(
            brand=BRAND,
            name=label,
            desc=desc,
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
