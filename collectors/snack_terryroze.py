"""태리로제떡볶이.

(주)캔푸드(777-87-01342, 서울 성북구 고려대로17가길 4) 운영. 공정위 `분식`
등록명은 **태리로제떡볶이&닭강정**, 84개점(2024년 말). 여기서는 사이트가 스스로
쓰는 이름(`<title>태리로제떡볶이`·로고)을 `BRAND` 로 쓴다.

도메인은 **`terryroze.com`** 이다. 검색에 `xn--2o2b1x303a6pi.com`(한글도메인)이
같이 뜨는데 **NXDOMAIN 이다** — 지금은 안 산다. 로마자 쪽만 살아 있다.

robots.txt: **200 / 21바이트 / `User-agent:* / Allow: /`**. 전부 https, SSR.
이용약관은 푸터에 없다(개인정보처리방침·개인정보수집동의만). 즉 "약관에 금지
조항이 없다"가 아니라 **"약관을 확인하지 못했다"** 상태로 붙는다.

## 한 요청이면 끝난다

`/bbs/content.php?co_id=sub03` 한 장(110KB)에 7개 분류 56건이 전부 SSR 로 들어
있다. 브라우저 불필요, UTF-8. 33떡볶이와 같은 제작사(VWEB)의 gnuboard 테마다.

## ⭐ 배지는 `.ccon3_card_badge` div 를 세지 말고 `data-badge` 값을 세라

수유리우동집(§5-3)에서 배운 그대로다. 화면 배지는 `<span class="ccon3_card_badge
is-new">NEW</span>` 인데, 판정 기준으로 쓸 값은 카드 자신이 들고 있는
`data-badge` 속성이다.

    <button class="ccon3_card swiper-slide has-image" type="button"
            data-category="마라꼬치"
            data-title="[로제찍먹] 콘치즈떡 마라꼬치"
            data-desc="알싸한 마라와 톡톡 터지는 옥수수, 쫀쫀한 치즈와 떡이…"
            data-badge="new"
            data-flavors="조금 매운맛"
            data-image="https://terryroze.com/data/file/main_menu/….png">

**2026-10-02 실측 비율 — 전체 56건 중 `new` 10 · `best` 12 · 값 없음 34.**
전수(56/56)가 아니니 섹션 장식이 아니고(퀴즈노스 66/66과 반대), 0건도 아니다
(컴포즈커피는 그림 합성이라 DOM 0건이었다).

### ⚠️ 붙은 이름을 읽어 봤다 — NEW 10건이 **마라꼬치 분류 10건 전부**다

| 분류 | 건수 | NEW |
|---|---:|---:|
| 튀김 시리즈 | 13 | 0 |
| 컵시리즈 | 10 | 0 |
| **마라꼬치** | **10** | **10** |
| 닭강정 | 9 | 0 |
| 떡볶이 | 6 | 0 |
| 세트메뉴 | 5 | 0 |
| 떡스타 | 3 | 0 |

이름이 전부 `[로제찍먹] … 마라꼬치` 라서 **분류 하나가 통째로 새로 생긴 것**이다
(브랜드 페이지 GNB 에도 `마라꼬치 Mala Skewers` 가 축으로 새로 들어가 있다).
간판 메뉴가 섞인 게 아니다 — 겐로쿠우동의 유일한 NEW 가 `카모난우동(일시중단)`
이었던 함정(§5-4)과 반대쪽 결과다. 분류 단위라 **다음에 그 분류가 상시가 되면
10건이 한꺼번에 가짜 신상으로 남는다.** 날짜가 없어 그걸 막을 수단이 우리에겐
없고, `rules.is_fresh` 의 STALE(first_seen 기준) 가 걷어가는 데 맡긴다.

`data-badge` 가 비어 있는 34건은 **'신상이 아니다'가 아니라 '모른다'** 라서
`is_new=None` 이다(계약대로).

## 날짜는 없다

소식(`co_id=sub01`)에 `NEWS ★ 태리로제 새로운 소식` 묶음이 있는데 내용이
`이벤트 5`·`이벤트 4`·`이벤트 3`·`태리로제 봄 이벤트 안내` 넷뿐이고 **날짜가
붙어 있지 않다.** 제품 출시 글은 0건이다. 그래서 받지 않는다(1요청 절약).
`data-image` 경로는 `/data/file/main_menu/<해시>_<해시>_<해시>.png` 라 날짜가
없다. `released_at`·`uploaded_at` 둘 다 빈다.

⚠️ 사이트 템플릿이 아직 덜 채워져 있다 — 개인정보처리방침 본문에
`본 방침은 {{시행일}}부터 시행됩니다.` 가 그대로 남아 있다. 33떡볶이(같은 제작사)
에는 `test` 더미 글이 남아 있다. **같은 제작사 사이트를 만나면 더미를 의심해라.**

상품별 주소는 **없다.** 카드가 `<button>` 이고 클릭하면 같은 페이지의 모달을
연다. `url` 을 비워 `base.SITES` 폴백에 맡긴다. 가격은 사이트에 없다.
`data-flavors`(순한맛|…|아주 매운맛)는 상품 속성이 아니라 주문 옵션이라
`labels` 에 넣지 않는다 — 넣으면 화면이 매운맛 다섯 칸으로 덮인다.
"""
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "태리로제떡볶이"
ROOT = "https://terryroze.com"
URL = ROOT + "/bbs/content.php?co_id=sub03"
DELAY = 2.5   # 1요청뿐이지만 다음 사람이 페이지를 늘릴 때를 위해 둔다.

# 카드 수가 이보다 적으면 테마가 바뀐 것이다. 56건 실측(2026-10-02)의 절반.
MIN_CARDS = 20


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(URL))
        r.raise_for_status()
        time.sleep(DELAY)

    cards = HTMLParser(r.text).css("button.ccon3_card")
    if len(cards) < MIN_CARDS:
        # 조용히 빈 리스트를 돌려주지 않는다. 구조 가정이 깨진 것이다.
        raise ValueError(f"{BRAND}: 메뉴 카드가 {len(cards)}건뿐이다 "
                         f"(2026-10-02 실측 56건). 선택자가 깨졌는지 확인해라")

    for card in cards:
        a = card.attributes
        name = " ".join((a.get("data-title") or "").split())
        if not name:
            continue
        # 화면 배지 div 가 아니라 카드가 들고 있는 값을 쓴다(위 docstring 참고).
        badge = (a.get("data-badge") or "").strip().lower()
        it = Item(
            brand=BRAND,
            name=name,
            desc=" ".join((a.get("data-desc") or "").split()),
            # ⚠️ `.get(k, "")` 를 쓰면 안 된다. selectolax 는 값이 없는 속성을
            # **키는 있고 값이 None** 으로 돌려줘서 기본값이 안 먹는다. 그대로
            # 두면 image=None 이 되고 derive 의 `startswith("http://")` 에서
            # AttributeError 로 어댑터가 통째로 죽는다(실측). 같은 파일의
            # data-title·data-desc 는 이미 `or ""` 를 쓰고 있다 — 여기만 빠졌다.
            image=a.get("data-image") or "",
            # new/best 둘뿐이다. data-flavors 는 주문 옵션이라 안 넣는다.
            labels=[badge.upper()] if badge else [],
            category=" ".join((a.get("data-category") or "").split()),
            # new 만 True. 값 없음은 '아니다'가 아니라 '모른다'다.
            is_new=True if badge == "new" else None,
            # 상품별 주소가 없다(모달을 여는 <button>).
            url="",
        )
        if it.key in keys:
            continue
        keys.add(it.key)
        items.append(it)

    # 이 브랜드의 신호는 data-badge 하나뿐이다. 테마가 바뀌어 속성이 사라지면
    # 건수는 56 그대로라 collect 의 0건·급감 가드에 안 걸리고, 화면에서는
    # '신상이 없는 브랜드' 로 조용히 바뀐다. 그 날 로그에 이유를 남긴다.
    if items and not any(i.is_new for i in items):
        print(f"[{BRAND}] data-badge=new 가 0건이다 — 배지가 내려간 건지 "
              f"속성이 바뀐 건지 확인해야 한다")
    return items
