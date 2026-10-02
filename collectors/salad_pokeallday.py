"""포케올데이.

(주)네오에프앤비(681-81-02539). 샐러드 분류의 세 번째 브랜드다.
⚠️ **도메인이 둘인데 둘 다 200 을 준다** — `pokeallday.co.kr`(210.114.6.164)과
`pokeallday.com`(222.122.86.254). 푸터로 확인한 정본은 **`.co.kr`** 이고,
`.com` 은 가맹문의용이다(내비의 '가맹문의 안내'가 그쪽을 가리킨다).

Rhymix/XE 계열 SSR. 브라우저 불필요, UTF-8, 4요청.
robots.txt: **200 / 22바이트 / `User-agent: * / Allow: /`**.
TLS·이미지 모두 https 다. 이용약관은 사이트에서 찾지 못했다.

## ⚠️ `/poke` 는 받지 않는다 — 상품이 아니라 조합 구성기 부품이다

내비에 메뉴가 6장(`/poke`·`/menu_balance_box`·`/protein_poke`·`/rice_bowl`·
`/side`·`/drink`) 있는데 **`/poke` 52건은 SKU 목록이 아니다.** "나만의 포케
만들기 — Step 01 Base / Step 02 Main / Step 03 Sauce" 페이지이고 내용이
`곡물밥`·`메밀면`·`저당 스파이시 오리엔탈 소스`·`김페스토`·`구운 두부` 같은
**베이스·소스·토핑**이다. 더 나쁜 건 **NEW 배지가 그 부품에 붙어 있다는 것**이다
(NEW 8건 중 5건이 소스·토핑). 요아정에 내린 "조합 구성기라 SKU 목록이 아니다"와
같은 함정인데 배지까지 달려 있어 더 헷갈린다. **되살리지 마라.**
`/menu_balance_box` 도 받지 않는다 — 구성 묶음이라 같은 성격이다.

## 신제품 신호 — `div.new_badge`

2026-10-02 실측, 4장 36건 중 **NEW 5건**. 전수가 아니고 장별로 갈린다
(protein_poke 0/3 · rice_bowl 2/2 · side 1/20 · drink 2/11).
원본에 주석 처리된 배지는 **0건**이다.

    <div class="bh bh_img_content">
        <div class="new_badge">NEW</div>
        <img src="/files/attach/images/2026/06/30/27e41….png">
    …
    <div class="bh_title"><a href="#" data-srl="53737"><span>스파이시 육회 참기름 메밀면 샐러드</span></a></div>
    <div class="en_title">Spicy beef tartare and Sesame oil salad</div>

⚠️ rice_bowl 은 2/2 라 그 장만 보면 "전수 = 장식"으로 읽힌다. **4장을 합쳐서
세야 판정이 선다**(36건 중 5건). 장 하나만 보고 판단하지 마라.

전용 신메뉴 게시판(`/newmenu`)도 있는데 `<title>포케올데이 - 신메뉴</title>` 까지
제대로 나오면서 **총 0건**이다. 만들어 놓고 한 번도 안 썼다. 받지 않는다.

## 날짜 — `uploaded_at` 까지만. 그리고 그 근거를 적어 둔다

출시일을 주는 자리는 어디에도 없다. 대신 첨부 경로가
`/files/attach/images/2026/06/30/…` 라 CMS 업로드 날짜가 일 단위로 들어온다.
**바르다김선생과 같은 기준으로 `uploaded_at` 에만 넣는다** — 사진만 교체해도
갱신되는 값이라 출시일이 아니다(김가네 반례 참고).

쓸 만하다고 본 근거는 분포다. 2026-10-02 실측 36건:

    2024-04 17 · 2025-11 4 · 2026-06 3 · 2025-05 3 · 2024-12 3 ·
    2026-08 2 · 2026-04 2 · 2024-06 2

**NEW 5건이 전부 최근 세 묶음(2026-08-03 · 2026-06-30 · 2026-04-28)에 들어
있다.** 배지와 날짜가 독립적으로 같은 답을 낸다.

⚠️ **2024-04-22 의 17건은 사이트 이관 자국이다**(전체의 절반). 그날 상품 17종이
나온 게 아니다. 2년 반 전이라 신선도 판정에서 어차피 걸러지지만, 브랜드가
사이트를 다시 옮기면 36건이 전부 그날 날짜를 달고 올라온다. 하루에 열 건 넘게
같은 날짜로 들어오면 그건 출시일이 아니라 이관일이다(얌샘김밥 2023-11-23 62건과
같은 자국).

## ⚠️ `uploaded_at` 을 채우면 자기 배지가 60일 창에 깎인다 — 알고 쓰는 것이다

`rules.is_fresh` 는 `is_new=True` 라도 날짜가 **있으면** 60일 창을 적용하고,
없으면 `first_seen + STALE(90일)` 까지 띄운다. 그래서 날짜를 채운 대가로
2026-10-02 기준 NEW 5건 중 **2건만 화면에 오른다**(2026-08-03 두 건).
2026-06-30·2026-04-28 세 건은 창 밖이라 빠진다.

**이게 맞다고 본다.** 날짜를 비우면 다섯 건 다 뜨지만, 그건 반년 전 상품을
"최근 60일"이라고 써 둔 화면에 올리는 것이다. 다른 브랜드에서 2013년 간판
메뉴에 배지가 계속 달려 있던 사고가 있었고, 이 레포는 그걸 날짜로 깎는 쪽을
택했다. 배지만 믿고 싶으면 `uploaded_at` 을 비우면 되는데 **그러면 안 된다.**

## ⚠️ 온도 표기가 접히면서 배지를 잃을 뻔했다

`base._SIZE` 가 괄호 안의 `HOT`·`ICE` 를 털기 때문에 `/drink` 에서 두 쌍이
같은 키가 된다 — `아메리카노 (Hot)`/`(Ice)`, `카페라떼(ICE)`/(핫 쪽). 36 → 35 가
여기서 난다. 그런데 **`카페라떼` 는 NEW 가 붙은 ICE 가 DOM 에서 먼저 와서
우연히 살아남았다.** 브랜드가 HOT 을 위로 올리면 그 배지가 조용히 사라진다.
그래서 접을 때 **배지 가진 쪽이 이기게** 한다.

상품별 주소는 **없다.** 카드 링크가 전부 `href="#"` 이고 `data-srl` 만 있는
JS 모달이다. `url` 을 비워 `base.SITES` 폴백에 맡긴다. 가격은 사이트에 없다.
"""
import re
import time
from urllib.parse import urljoin

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "포케올데이"
ROOT = "https://pokeallday.co.kr"
DELAY = 2.5

# (분류명, 경로). /poke 와 /menu_balance_box 는 상품 목록이 아니다(위 docstring).
PAGES = (
    ("PROTEIN POKE", "/protein_poke"),
    ("RICE BOWL",    "/rice_bowl"),
    ("SIDE",         "/side"),
    ("DRINK",        "/drink"),
)

# /files/attach/images/2026/06/30/27e41….png → 2026-06-30
_UPLOADED = re.compile(r"/files/attach/images/(\d{4})/(\d{2})/(\d{2})/")


def _text(node, sel) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _uploaded_at(src: str) -> str:
    """첨부 경로의 업로드 날짜. 출시일이 아니다(위 docstring 참고)."""
    m = _UPLOADED.search(src or "")
    return "-".join(m.groups()) if m else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen: dict = {}   # key → items 안의 자리. 배지 가진 쪽이 이기게 한다.
    with base.client() as c:
        for category, path in PAGES:
            r = base.retry(lambda: c.get(ROOT + path))
            r.raise_for_status()
            time.sleep(DELAY)

            for card in HTMLParser(r.text).css(
                    "div.bh_widget_content div.bh_item"):
                name = _text(card, ".bh_title span") or _text(
                    card, ".hover_title")
                if not name:
                    continue
                img = card.css_first("img")
                src = img.attributes.get("src", "") if img else ""
                it = Item(
                    brand=BRAND,
                    name=name,
                    name_en=_text(card, ".en_title"),
                    image=urljoin(ROOT, src) if src else "",
                    category=category,
                    uploaded_at=_uploaded_at(src),
                    # NEW 배지만 True. 배지 없음은 '아니다'가 아니라 '모른다'다.
                    is_new=True if card.css_first("div.new_badge") else None,
                    # 상품별 주소가 없다(전부 href="#" 인 JS 모달).
                    url="",
                )
                old = seen.get(it.key)
                if old is None:
                    seen[it.key] = len(items)
                    items.append(it)
                elif it.is_new and not items[old].is_new:
                    # 같은 상품의 다른 온도 표기가 접힌다(아래 ⚠️). 배지가
                    # 늦게 온 쪽에만 붙어 있으면 그쪽으로 바꿔 끼운다.
                    items[old] = it

    # 이 브랜드의 신호는 배지 하나뿐이다(날짜가 없다). `div.new_badge` 가
    # 안 잡히면 건수는 35 그대로라 collect 의 0건·급감 가드에 안 걸리고,
    # 화면에서만 조용히 '신상 없는 브랜드' 가 된다. 로그에 이유를 남긴다.
    if items and not any(i.is_new for i in items):
        print(f"[{BRAND}] new_badge 가 0건이다 — 배지가 사라진 건지 "
              f"선택자가 깨진 건지 확인해야 한다")
    return items
