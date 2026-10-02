"""싸다김밥.

(주)참에프앤디(211-87-87253, 서울 광진). 공정위 `분식` 97개점.
⚠️ **도메인 함정 하나.** 검색에 `ssadagimbab.co.kr` 이 같이 뜨는데 그건
**NXDOMAIN** 이다. 사는 건 **`www.ssadagb.com`** 이다(cafe24 쇼핑몰 엔진).
메뉴가 상품 목록 템플릿(`xans-product-listnormal`)으로 올라가 있어 SSR 이고,
카테고리 7장이면 전부다. 2026-10-02 실측 **상품 81건**
(목록의 `ul.prdList li` 는 162개인데 cafe24 가 상품 `li` 안에 `li` 를 또
넣어서 딱 절반이다. **`li` 를 세지 말고 `.description .name` 이 있는 것만 세라** —
'162건인데 81건만 나온다, 절반 유실' 로 오진할 자리다).

    /menu/list?cate_no=23 김밥류 26 · 24 분식류 32 · 25 면류 30 · 26 덮밥류 30
                       27 오므라이스류 8 · 28 까스&볶음밥류 20 · 42 찌개&비빔밥류 16

## 신제품 신호 — 상품별 배지. 단 **글자가 아니라 그림이고 alt 가 없다**

cafe24 의 아이콘 슬롯(`div.icons`)에 이미지가 붙는다. 그런데 `alt` 속성이
**없어서**(`alt=None`) 텍스트로는 아무것도 안 잡힌다. 원본 HTML 을 `NEW` 로
grep 하면 0건이 나오고, 거기서 "신호 없음"으로 적으면 **틀린다.**
실제로는 파일명이 다른 PNG 두 장이 선별로 붙어 있다.

| 파일 | 실물 | 2026-10-02 실측 |
|---|---|---|
| `/web/upload/custom_117324561831424.png` | 노란 **NEW** 리본 | **8 / 81** |
| `/web/upload/custom_317413267861216.png` | 초록 **BEST** 리본 | 23 / 81 |

둘 다 브라우저에서 `offsetParent !== null` 로 보이는 것을 확인했고, 그림을
직접 열어 글자를 읽었다(배지 이미지는 열어 봐야 뭔지 안다 — 겐로쿠우동에서
"배지 1건"이 `카모난우동(일시중단)` 이었던 것과 같은 교훈이다).

**그래서 판정 기준이 파일명이다.** 글자가 없으니 어쩔 수 없는데, 브랜드가
배지 그림을 교체하면 파일명이 바뀌고 **조용히 0건이 된다.** 그 사고를 막으려고
`fetch()` 가 아이콘 파일명을 전수로 세서 **아는 두 장 말고 다른 그림이 나오면
경고를 찍는다.** 0건이 되는 날 로그에 이유가 남게 하려는 것이다.

### 배지 8건이 공지와 정확히 맞는다
공지 게시판(`/board/free/list.html?board_no=1`)에
**`[뉴스] 2026년 신메뉴 8종 출시` (2026.01.26)** 가 있다. NEW 배지가 붙은 게
**정확히 8건**이다. 두 신호가 독립적으로 같은 수를 낸다 — 섹션 장식이 아니라
관리되는 배지라는 뜻이다(81건 중 8건이라 전수도 아니다).

    소세지계란김밥 · 통통계란김밥 · 매콤야끼만두 · 얼큰장우동 ·
    짬뽕라면 · 고구마치즈돈까스 · 차돌된장찌개 · 제육비빔밥

세 번째 정황도 같은 방향이다 — **NEW 8건의 상품 이미지가 전부
`/web/product/medium/202601/…` 이고, 배지 없는 상품은 `/202503/` 이다.**
(이미지 경로가 연·월까지만이라 `uploaded_at` 으로도 쓰지 않는다. 브레댄코에
적어 둔 기준과 같다.)

⚠️ **그래도 그 공지 날짜를 `released_at` 에 넣지 않는다.** 공지는 "8종"이라고만
하고 품목을 적지 않았다. 수가 맞는 건 정황이지 그 글이 이 여덟 개를 가리킨다는
기록이 아니다. **날짜는 비운다.** 신제품 판정은 배지와 collect 의 어제 대비
diff 에 맡긴다(죠스떡볶이·김가네와 같은 처분).

공지 게시판은 날짜가 연도까지 찍히고(`2026.02.06` 최신) 살아 있지만,
**상품 글은 1년에 1건 수준**이고 나머지는 `2월 오픈예정점`·`푸드뱅크 후원`
같은 매장·홍보 소식이다. 그래서 게시판은 소스로 쓰지 않았다.

## 이미지는 프로토콜 상대경로다
`src="//www.ssadagb.com/web/product/medium/…jpg"` 로 스킴이 없다. 그대로 두면
`base.derive()` 의 `http://` 검사에는 안 걸리지만 우리 페이지에서 깨진다.
`urljoin` 으로 https 를 붙인다.

상품별 주소는 **없다.** 목록의 `<a>` 가 `name="anchorBoxName_9"` 뿐이고 href 가
없다(cafe24 가 상세를 안 쓰게 구성했다). `url` 을 비워 `base.SITES` 폴백에 맡긴다.
"""
import time
from urllib.parse import urljoin

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "싸다김밥"
ROOT = "https://www.ssadagb.com"
LIST = ROOT + "/menu/list"
DELAY = 2.5

# (분류명, cate_no)
CATEGORIES = (
    ("김밥류",          "23"),
    ("분식류",          "24"),
    ("면류",            "25"),
    ("덮밥류",          "26"),
    ("오므라이스류",     "27"),
    ("까스&볶음밥류",    "28"),
    ("찌개&비빔밥류",    "42"),
)

# 배지 그림의 파일명. alt 가 없어서 이것 말고 가릴 방법이 없다(위 docstring).
BADGES = {
    "custom_117324561831424.png": "NEW",
    "custom_317413267861216.png": "BEST",
}


def _text(node, sel) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _badges(card, unknown: set) -> list:
    """카드에 붙은 배지. 모르는 그림이 나오면 모아 둔다(호출자가 경고한다)."""
    out = []
    for im in card.css("div.icons img"):
        f = im.attributes.get("src", "").split("/")[-1]
        if f in BADGES:
            out.append(BADGES[f])
        elif f:
            unknown.add(f)
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    unknown: set = set()
    with base.client() as c:
        for category, cate_no in CATEGORIES:
            r = base.retry(lambda: c.get(LIST, params={"cate_no": cate_no}))
            r.raise_for_status()
            time.sleep(DELAY)

            for card in HTMLParser(r.text).css("ul.prdList li"):
                name = _text(card, ".description .name")
                if not name:
                    continue
                img = card.css_first(".prdImg img")
                src = img.attributes.get("src", "") if img else ""
                labels = _badges(card, unknown)
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=_text(card, ".spec .summary_desc").split(":", 1)[-1]
                         .strip(),
                    # 스킴 없는 //… 경로다. https 를 붙인다.
                    image=urljoin(ROOT, src) if src else "",
                    labels=labels,
                    category=category,
                    # NEW 배지만 True. 배지 없음은 '아니다'가 아니라 '모른다'다.
                    is_new=True if "NEW" in labels else None,
                    # 상품별 주소가 없다(목록 <a> 에 href 자체가 없다).
                    url="",
                )
                if it.key in keys:
                    continue
                keys.add(it.key)
                items.append(it)

    if unknown:
        # 배지 그림이 바뀌면 is_new 가 조용히 전건 None 이 된다. 그 날
        # 로그에 이유가 남게 한다(판정 자체는 막지 않는다).
        print(f"[{BRAND}] 모르는 배지 그림: {sorted(unknown)} "
              f"— BADGES 를 확인해야 한다")
    # ⚠️ 위 경고는 '모르는 **파일명**' 에만 운다. 컨테이너(`div.icons`)가
    # 개명되면 unknown 이 빈 집합이라 **아무 말도 없이** is_new 가 0건이 된다
    # (선택자를 일부러 깨뜨려 실측 확인했다). 그 구멍을 한 겹 더 막는다.
    if items and not any(i.is_new for i in items):
        print(f"[{BRAND}] NEW 배지가 0건이다 — 배지가 내려간 건지 "
              f"`div.icons` 선택자가 깨진 건지 확인해야 한다")
    return items
