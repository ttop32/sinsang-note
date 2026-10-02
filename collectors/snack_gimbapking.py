"""김밥킹 — 한 장짜리 아임웹 랜딩의 메뉴 섹션에서 NEW 배지를 센다.

(주)아이윈엔터프라이즈(공동대표 윤한주·한범구, 서울 강남 테헤란로25길 20).
공정위 `분식` 27개점(2024년 말). 도메인은 **한글도메인뿐**이다 —
`김밥킹.com` = **`xn--4k0bn7xt5p.com`**. `gimbapking.*`·`kimbabking.*` 같은
로마자는 안 산다(인스타 핸들만 `gimbapking_official` 이다).
2026-10-02 실측 200 / 857KB / UTF-8 / 완전 SSR.

robots.txt: 200 / 236바이트. `Allow: /` 에 `/site_join`·`/login`·`/logout.cm`·
`/shop_cart`·`/?mode*`·`/admin` 만 막는다. ⚠️ **`/?mode*` 가 막혀 있어 푸터의
이용약관(`/?mode=policy`)을 받을 수 없다.** 김밥천국과 같은 처분이다 —
"약관에 금지 조항이 없다"가 아니라 **"약관을 확인하지 못했다"** 상태로 붙는다.
삭제 요청이 오면 다투지 말고 즉시 내린다.

## ⭐ 배지 비율 — 83건 중 NEW 19 (22.9%) · BEST 2

전수(퀴즈노스 66/66)도 0건(컴포즈커피)도 아니다. 분류별로는 이렇다.

| 탭 | 건수 | NEW |
|---|---:|---:|
| 김밥 | 19 | 4 |
| 떡볶이 | 7 | 1 |
| 면류 | 13 | 5 |
| 식사 | 24 | 3 |
| 계절메뉴 | 7 | 0 |
| 사이드 | 13 | 6 |
| **합계** | **83** | **19** |

**붙은 이름을 읽어 봤다**(겐로쿠우동의 `카모난우동(일시중단)` 교훈).
볶음김치김밥·김말이김밥·매운어묵김밥·닭갈비김밥·마라로제떡볶이·토마토라면·
알탕면·불닭볶음면·불닭볶음우동·카레볶음우동·닭갈비덮밥·볶음김치참치덮밥·
오징어제육덮밥(2인)·고추튀김(2개)·모듬튀김·찰순대·야채튀김(2개)·
어묵튀김(5개)·윙&봉. **간판 메뉴 `김밥킹김밥` 은 NEW 가 아니라 BEST 다** —
브랜드가 둘을 구분해 쓰고 있다는 증거다. `계절메뉴` 탭만 NEW 0건인 것도
장식이 아니라는 쪽을 가리킨다(전수로 깔았으면 거기에도 붙었을 것이다).

### 숨김 배지(수유리우동집)와 다르다 — 브라우저로 확인했다
`div.menu_mid` 여섯 개가 전부 `menu_hide` 클래스를 달고 있어 원본만 보면
"CSS 로 숨긴 전수 배지"처럼 읽힐 수 있다. **탭 전환용이다.**
브라우저에서 `offsetParent !== null` 로 세면 활성 탭(`.on` = 김밥)의
**19건만 보이고 그 안의 NEW 가 4건**으로, 원본에서 센 김밥 탭 4건과 같다.
전수로 깔린 뒤 숨겨진 게 아니라 **탭마다 선별로 붙어 있다.**

## 날짜는 비운다 — 이미지 경로에 반례가 있다

NEW 19건의 썸네일이 전부 `cdn.imweb.me/thumbnail/20260522/` 또는
`/20260523/` 이고, 배지 없는 상품은 대부분 `/20250131/`(사이트 제작일)이다.
수가 깔끔해서 출시일로 쓰고 싶어지는데 **쓰면 안 된다.**

    식사 탭: NEW 가 아닌 상품 4건의 이미지가 20260523
    사이드 탭: NEW 가 아닌 상품 2건의 이미지가 20260523

즉 **2026-05-23 에 올라간 그림 중에 신상이 아닌 것이 6건 있다.** 사진만
교체해도 경로가 바뀐다는 김가네 반례와 같은 종류다. 반대 방향(모든 NEW 가
2026-05 업로드)은 성립하므로 **배지가 관리되고 있다는 정황**으로만 쓰고,
`released_at`·`uploaded_at` 둘 다 비운다. 날짜 판정은 배지와 collect 의
어제 대비 diff 에 맡긴다(싸다김밥·김가네와 같은 처분).

## 상품별 주소가 없다
한 장짜리 랜딩이라 상세 페이지가 없고 카드에 링크도 없다. 그나마 브랜드가
GNB 에 심어 둔 메뉴 섹션 앵커(`/#s20250131df8755b47afce`, 원본에 264회
등장)가 있어 전 상품을 그리로 보낸다. 섹션 id 가 바뀌면 앵커가 무시되고
루트가 열릴 뿐이라 피해 상한이 거기까지다.

가격은 화면에 없다(창업 모집 랜딩이라 메뉴는 이름과 사진뿐이다).
`메뉴 더보기` 버튼이 탭마다 있는데 누르면 같은 섹션이 펼쳐질 뿐 추가 요청이
없다 — 83건이 전부다. 요청 **1회**로 끝난다.
"""
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "김밥킹"
ROOT = "https://xn--4k0bn7xt5p.com"      # 김밥킹.com
# 전 상품이 이 앵커로 떨어진다(상품별 주소가 없다. 위 docstring 참고).
MENU_URL = ROOT + "/#s20250131df8755b47afce"
DELAY = 2.5   # robots 에 Crawl-delay 는 없다. 1요청뿐이라 여유를 둔다.

# 탭 순서 = `div.menu_top h3` 순서 = `div.menu_mid` 순서. 2026-10-02 실측으로
# 둘이 1:1 이고 건수 합이 83 으로 맞는다. 어긋나면 분류를 비운다(아래 참고).
MIN_ITEMS = 40   # 구조가 바뀌어 카드를 절반도 못 찾으면 올린다.


def _one(node, sel: str) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _name(card) -> str:
    """상품명.

    카드 안에 `h4.tt` 가 둘 들어갈 수 있다 — 하나는 배지(`h4.tt.desc`, 글자가
    BEST·NEW), 하나는 이름이다. **배지에도 같은 클래스가 붙어 있어** 첫 번째를
    집으면 상품명이 'NEW' 가 된다. 배지 노드를 뺀 나머지의 첫 번째를 쓴다.
    """
    for n in card.css("h4.tt"):
        cls = n.attributes.get("class", "") or ""
        if "desc" in cls.split():
            continue
        t = " ".join(n.text().split())
        if t:
            return t
    return ""


def _badge(card) -> str:
    """`h4.desc` 안의 **글자**를 읽는다. 요소 존재만으로 세지 않는다.

    설빙에서 `span.flag` 를 존재만 보고 세다가 2013년 메뉴가 신상으로 올라간
    적이 있다. 여기서도 같은 자리에 BEST 가 섞여 들어온다(2건).
    """
    return _one(card, "h4.desc").upper()


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(ROOT))
        r.raise_for_status()
        time.sleep(DELAY)

        doc = HTMLParser(r.text)
        tabs = [" ".join(n.text().split())
                for n in doc.css("div.menu_top h3")]
        mids = doc.css("div.menu_mid")
        if not mids:
            raise RuntimeError(
                f"[{BRAND}] 메뉴 탭(div.menu_mid)을 못 찾았다 — "
                f"랜딩 구조가 바뀌었다")

        for i, mid in enumerate(mids):
            # 탭 제목과 본문 개수가 어긋나면 분류를 지어내지 않고 비운다.
            category = tabs[i] if i < len(tabs) else ""
            for card in mid.css("div.mid_item"):
                name = _name(card)
                if not name:
                    continue
                badge = _badge(card)
                img = card.css_first(".item_img img")
                items_src = img.attributes.get("src", "") if img else ""
                it = Item(
                    brand=BRAND,
                    name=name,
                    # 이미지 경로의 20260522 는 업로드일이고 반례가 있다
                    # (위 docstring). 날짜 칸에 넣지 않는다.
                    image=items_src,
                    labels=[badge] if badge else [],
                    category=category,
                    is_new=True if badge == "NEW" else None,
                    url=MENU_URL,
                )
                if it.key in keys:
                    continue
                keys.add(it.key)
                items.append(it)

    if len(items) < MIN_ITEMS:
        raise RuntimeError(
            f"[{BRAND}] 상품이 {len(items)}건뿐이다(실측 83) — "
            f"선택자가 깨졌는지 확인해야 한다")

    # 이 브랜드의 신호는 배지 하나뿐이다. `h4.desc` 가 안 잡혀도 건수는 83
    # 그대로라 collect 의 0건·급감 가드에 안 걸리고, 화면에서는 '신상이 없는
    # 브랜드' 로 조용히 바뀐다. 그 날 로그에 이유를 남긴다.
    if items and not any(i.is_new for i in items):
        print(f"[{BRAND}] NEW 배지가 0건이다 — 배지가 사라진 건지 "
              f"선택자가 깨진 건지 확인해야 한다")
    return items
