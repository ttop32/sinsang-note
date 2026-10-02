"""버거운버거. 가맹점 25개. 가맹본부 (주)안스푸드(142-88-00544, 충남 아산).

아임웹(imweb)이고 **`/menu` 한 장(450KB)에 전 메뉴가 SSR** 로 들어온다. 1요청이면
끝이고 브라우저는 필요 없다. 2026-10-02 실측.

## 신제품 신호 — 카드의 `data-meta` 에 박힌 `new` 칸

카드는 `<a>` 가 아니라 `<button class="bub-menu-card">` 이고, 사람이 보는 이름·
분류·배지가 전부 **속성**에 들어 있다. JS 가 그걸 읽어 `<h3>`·배지를 채운다.

    <button class="bub-menu-card"
            data-name-en="통모짜치즈버거 || Whole Mozzarella Cheese Burger"
            data-meta="burger|b-beef|new || 비프,통모짜렐라,치즈,베이컨,패티x2">
      …<span class="bub-card-new" hidden>NEW</span>…
      <img src="https://cdn-optimized.imweb.me/v2/brand/…">
      <div hidden><div data-desc><p>통으로 꽉 찬 모짜렐라 패티의 …</p></div></div>
    </button>

`data-meta` 는 `<분류들> || <태그들>` 이다. 분류 목록에 `new` 가 들어 있으면
상단 `NEW` 탭(`<button data-main="new">`)에 걸리는 상품이고, 그게 **브랜드가
직접 고른 신메뉴 칸**이다. 그래서 거기에 `is_new` 를 건다.

🔴 **대문자 `NEW` 문자열을 세면 안 된다. 58건 전부에 붙어 있다.**
`<span class="bub-card-new" hidden>NEW</span>` 가 카드마다 꽂혀 있는 **빈 템플릿**
이고 `hidden` 이 달려 화면엔 안 보인다. JS 가 해당 카드에만 `hidden` 을 떼는
구조다. 문자열로 세면 59(= 58 + 탭 버튼 1)가 나와 전건이 신상이 된다 —
퀴즈노스(`new_icon` 66건 전건)와 같은 함정이고, 여긴 **속성**을 봐야 한다.

실측 비율: 57건 중 **5건(8.8%)** 만 `new` 다. `BEST` 태그는 8건으로 따로 논다.

    클래식치즈버거 / 통모짜치즈버거 / 불닭통모짜치즈버거 (burger)
    칠리스치즈스틱 / 버팔로스틱                         (side)

**교차검증.** 보도자료 게시판(`/NEWS`)에 「버거운버거, 통모짜렐라치즈패티 담은
신메뉴 2종 출시」 글이 있고 그 2종이 위 `통모짜치즈버거`·`불닭통모짜치즈버거` 와
정확히 일치한다. 배지가 실제 출시와 맞물려 움직인다는 증거다.

## 날짜 — 없다. 지어내지 않는다

메뉴 페이지에 날짜가 없고, 이미지 주소도 `…/v2/brand/<사이트id>/<uuid>` 라
날짜가 안 박힌다(같은 아임웹이라도 `cdn.imweb.me/thumbnail/YYYYMMDD/` 를 쓰는
참토스트와 경로 체계가 다르다). `released_at`·`uploaded_at` 을 비운다.
`is_new=True` + 날짜 없음이면 rules.is_fresh 가 `STALE` 일 동안 신상으로 본다.

## ⚠️ `/NEWS` 보도자료 게시판은 쓰지 않는다 — 날짜가 일괄 재등록이다

처음엔 왓더버거처럼 게시판에서 '출시' 글만 뽑으려 했다. 날짜 분포를 세고 접었다.

    2026-08-19   1건
    2026-08-20  22건   ← 사이트를 열며 과거 기사 스크랩을 하루에 몰아 넣었다
    2026-09-15   1건

24건 중 22건이 한 날짜다. 글 제목이 `매체명|||기사제목|||기사주소` 꼴인 **외부
언론 스크랩**이고, `작성시간` 은 기사가 나온 날이 아니라 관리자가 붙여넣은 날이다.
실제로 그 22건 안에는 2024년에 연 매장 오픈 기사까지 섞여 있다. 이걸
`released_at` 으로 쓰면 신메뉴·매장오픈·2+1 이벤트가 전부 같은 날 출시한 게 된다
(노브랜드버거 2025-05-07 20건·탐앤탐스 56건과 같은 자국이다).

게시판 쪽에서 가져올 게 하나도 없진 않지만 — 날짜 없는 제목뿐이라 메뉴 카드의
`new` 칸보다 나을 게 없다. 메뉴 한 장이 더 정확하고 더 싸다.
`/EVENT`(7건, 전부 할인·증정)와 `/NOTICES`(1건, 추석 휴무)도 상품이 아니다.

## 그 밖의 실측

- 카드 58개 중 **1개는 빈 템플릿**이다(`data-name-en=""`, 이미지 src 빈 문자열).
  이름이 비면 건너뛴다. 실제 상품은 57건이다.
- 상단 탭은 7개(NEW·버거·베이크·치킨·실속세트·사이드·음료)인데 **실속세트·음료
  칸에 담긴 카드가 0건**이다. 탭만 만들어 두고 비워 둔 상태다.
- `치킨텐더 (2조각)` 한 건만 이미지가 없다. 사진 없는 카드로 그린다.
- 상품 상세 페이지가 없다(카드가 `<button>` 이고 `<a>`·onclick 이 없다).
  `Item.url` 은 비우고 base.SITES 폴백(`/menu`)에 맡긴다.
- 이름은 `data-name-en` 의 `한글명 || 영문명` 이다. 구분자 앞뒤 공백이 들쭉날쭉
  (`버거운치킨버거||Burgerun…`, `양념치킨 ||  Seasoned…`)이라 쪼개고 턴다.
- 괄호 안 조각 수(`치즈스틱 (2조각/4조각)`)는 상품명 일부라 남긴다.

robots.txt: 200/218바이트, `User-agent: * / Allow: /` + 아임웹 기본 Disallow
(`/site_join`·`/login`·`/logout.cm`·`/shop_cart`·`/?mode*`·`/admin`).
`/menu` 와 cdn 이미지는 허용 범위다. 이용약관은 `/?mode=policy` 라
**robots 가 막는 경로여서 받지 않았다** — 금지 조항을 확인하지 못했다는 뜻이다
(참토스트·미소야와 같다).
"""
from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "버거운버거"
URL = "https://www.burgerunburger.com/menu"

# data-meta 의 분류 토큰 → 화면 분류. 상단 탭 라벨 그대로다.
# b-* 는 버거 안의 소분류(치킨/비프/포크/씨푸드)라 여기 넣지 않는다 —
# Item 에 2단 분류 자리가 없고, 넣으면 '버거' 가 네 칸으로 쪼개진다.
CATEGORIES = {
    "burger":  "버거",
    "bake":    "베이크",
    "chicken": "치킨",
    "side":    "사이드",
    "set":     "실속세트",
    "drink":   "음료",
}

# 브랜드가 신메뉴로 고른 칸. 상단 NEW 탭(`data-main="new"`)과 같은 키다.
NEW_KEY = "new"


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _split2(s: str) -> tuple:
    """`앞 || 뒤` 를 쪼갠다. 구분자 앞뒤 공백이 들쭉날쭉이라 턴다."""
    head, _, tail = (s or "").partition("||")
    return _clean(head), _clean(tail)


def _cats(meta: str) -> list:
    """data-meta 앞쪽의 분류 토큰 목록. `burger|b-beef|new` → [burger, b-beef, new]."""
    head, _ = _split2(meta)
    return [t.strip().lower() for t in head.split("|") if t.strip()]


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(URL))
        r.raise_for_status()

    doc = HTMLParser(r.text)
    # 신메뉴 칸이 살아 있는지 먼저 본다. 이 어댑터의 is_new 가 거기 걸려 있다.
    if not doc.css(f'button[data-main="{NEW_KEY}"]'):
        raise RuntimeError(
            f"{BRAND}: 상단 '{NEW_KEY}'(NEW) 탭이 사라졌다 — 신상 신호 없음")

    cards = doc.css("button.bub-menu-card")
    if not cards:
        raise RuntimeError(f"{BRAND}: 상품 0건 — 카드 셀렉터가 깨졌다")

    items: list[Item] = []
    seen = set()
    for card in cards:
        name, name_en = _split2(card.attributes.get("data-name-en") or "")
        if not name:
            continue              # 빈 템플릿 카드 1개
        cats = _cats(card.attributes.get("data-meta") or "")
        img = card.css_first("img")
        desc = card.css_first("[data-desc]")
        it = Item(
            brand=BRAND,
            name=name,
            name_en=name_en,
            desc=_clean(desc.text()) if desc else "",
            image=(img.attributes.get("src") or "") if img else "",
            category=next((CATEGORIES[t] for t in cats if t in CATEGORIES), ""),
            # 브랜드가 NEW 탭에 담은 것만 True. 담지 않은 건 '모름' 이 아니라
            # '신메뉴 아님' 이라고 브랜드가 말한 것이므로 False 다(프랭크버거 선례).
            is_new=NEW_KEY in cats,
        )
        if it.key in seen:
            continue
        seen.add(it.key)
        items.append(it)

    if not items:
        raise RuntimeError(f"{BRAND}: 이름 있는 상품 0건 — data-name-en 이 비었다")
    # 전건이 신메뉴면 배지가 아니라 템플릿이 깨진 것이다. 조용히 메뉴판 전체를
    # 신상으로 올려보내느니 드러낸다(퀴즈노스 66건 전건 선례).
    if all(i.is_new for i in items):
        raise RuntimeError(
            f"{BRAND}: {len(items)}건 전부 NEW — data-meta 의 분류가 깨졌다")
    return items
