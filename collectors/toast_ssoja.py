"""쏘자토스트(SSOJATOAST). 가맹점 33개. 가맹본부 (주)에스앤비푸드(432-81-01049).

공정위 업종은 `패스트푸드` 지만 파는 건 **토스트·핫도그**다. 햄버거가 아니라
이삭토스트·참토스트와 같은 칸(`샌드위치`)에 둔다. 2026-10-02 실측.

아임웹(imweb) **쇼핑몰 위젯**이다. 참토스트(갤러리 위젯)와 같은 플랫폼이지만
상품이 갤러리 캡션이 아니라 쇼핑 상품으로 들어 있어서 파싱이 다르다.

    GET /toast/?sort=recent     12건
    GET /hotdog/?sort=recent     8건
    GET /drinks/?sort=recent    12건      합계 32건(키 중복을 접으면 26), 3요청

카드 한 장이 필요한 걸 다 들고 있다.

    <div class="shop-item"
         data-product-properties='{"idx":73,"code":"s202411251f271a0458de1",
           "name":"달콤 치킨 토스트","price":0,
           "image_url":"https://cdn-optimized.imweb.me/upload/…/b803945868925.jpg?w=800"}'>
      <a href="/toast/?idx=73">…</a>
      <div class="item-summary"><p>SWEET CHICKEN TOAST</p>…</div>
      <div class="item-icon _unit_list unit-list"></div>     ← 배지 자리. 전건 비어 있다

## 날짜 — 상품 코드에 박힌 등록일

`code` 가 `s<YYYYMMDD><랜덤>` 꼴이다. 아임웹이 상품을 만들 때 그날 날짜로
찍는 식별자다. 추측이 아니라 **`idx` 와 교차검증**했다 — `idx` 는 상품 등록
순서대로 올라가는 일련번호인데, 32건을 `idx` 로 정렬하면 코드 날짜가 **한 번도
역행하지 않는다**(14~16→11-01, 19~20→11-04, 21~47→11-06, 71~74→11-25, 76→
2025-02-20). 두 값이 독립인데 같은 순서를 가리키면 등록 시각으로 봐도 된다.

**`uploaded_at` 까지만이다 — `released_at` 으로 올리지 않는다**(참토스트·본아이에프
선례). 사이트에 상품을 올린 날이지 매장에서 판 날이 아니다.

분포:

    2024-11-06  22건   2024-11-25  4건   2024-11-01  3건
    2024-11-04   2건   2025-02-20  1건

2024-11 에 사이트를 열며 넣은 뭉치이고 그 뒤로 **단 1건**(감자 베이컨칩 핫도그,
2025-02-20)만 늘었다. 즉 지금(2026-10) 화면에 오를 건 0건이다. 그래도 등록하는
건 신호가 가짜가 아니라 실재하고, 다음에 뭔가 올라오면 그날 바로 잡히기
때문이다. 건수를 채우려고 전 메뉴를 신상으로 밀어 올리지 않는다(잇샌드와 같다).

## ⚠️ `is_new` 는 비운다(None) — '시즌메뉴' 칸을 신호로 믿지 마라

내비에 `포스터`(= 시즌메뉴, `/season`)와 `사이드`(= 세트메뉴, `/set`) 칸이 있어서
잇샌드의 `sca=mn_new` 처럼 쓸 수 있을 줄 알았다. 받아 보니 **두 주소가 완전히
같은 페이지를 돌려준다.** 쇼핑 위젯이 아예 없고(`data-widget-type="shopping"` 0개)
갤러리 위젯 두 벌에 **캡션 없는 포스터 이미지 4장**만 있다(최신 2025-04-01).
칸이 비어 있는 게 아니라 **상품 칸으로 만들어지지 않았다.** 그래서 잇샌드처럼
`is_new=False`(= 브랜드가 신메뉴로 고른 게 없다)로 단정하지 않고 모름으로 둔다.

배지도 없다. `/menu`·`/toast`·`/hotdog`·`/drinks` 어디에도 `NEW`·`신메뉴`·`신제품`·
`출시` 문자열이 0회다(대문자 `NEW` 1회는 루트의 내비 CSS 다). 카드마다 있는
`div.item-icon._unit_list` 가 아임웹이 NEW·BEST 아이콘을 꽂는 자리인데 **32건
전부 비어 있다.** 브랜드가 여기에 달기 시작하면 그게 훨씬 좋은 신호이니
그때 갈아타라(잇샌드 `ul.mn_icon` 과 같은 자리다).

## 그 밖의 실측

- 가격은 `판매가 회원공개` 로 가려져 있고 JSON 의 `price` 도 0 이다. 어차피
  Item 에 가격 자리가 없어 버린다.
- `item-summary` 는 **영문명**이다(`SWEET CHICKEN TOAST`). 설명문이 아니라서
  `desc` 가 아니라 `name_en` 에 넣는다. 안쪽 `<p>` 만 읽는다 — 블록 전체를
  읽으면 스크린리더용 `상품 요약설명` 이 따라 들어온다.
- `체다 칠리 핫도`(idx 27)와 `체다 칠리 핫도그`(idx 28)가 둘 다 살아 있다.
  브랜드 쪽 오타로 보이지만 우리가 고칠 자리가 아니라 그대로 둔다.
- 음료는 사이트에 12건인데 **들어오는 건 6건**이다. 전부 `(HOT)`/`(ICE)` 쌍이고
  base.make_key 가 온도 괄호를 털어 같은 키가 되기 때문이다. 먼저 나온 `(HOT)`
  쪽이 남는다. 빽다방·이디야도 같은 식으로 키 중복을 접는다 — 여기만 다르게
  두면 안 되므로 그대로 둔다. 그래서 32건이 아니라 **26건**이 정상이다.
- 공지사항(`/notice`)·이벤트(`/event`)는 **로그인 벽**이다("권한이 없습니다").
  게시판 경로는 쓸 수 없다.
- 상품 상세 주소는 `/<칸>/?idx=<번호>` 로 존재한다. `Item.url` 에 붙인다.

robots.txt 는 받지 않았다 — 금지 조항을 확인하지 못했다는 뜻이다. 이용약관은
`https://ssojatoast8947.imweb.me/?mode=policy` 인데 아임웹 기본 robots 가
`/?mode*` 를 막는 경로라 역시 받지 않았다(참토스트와 같다).
"""
import html as _html
import json
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "쏘자토스트"
ROOT = "https://ssoja.co.kr"
# 쇼핑 위젯이 붙어 있는 칸만. `/season`·`/set` 은 포스터 갤러리라 뺀다(docstring).
CATEGORIES = {
    "toast":  "토스트",
    "hotdog": "핫도그",
    "drinks": "음료",
}
DELAY = 2.0
MAX_ITEMS = 300          # 폭주 방지. 현재 32건이다.

# code = s<YYYYMMDD><랜덤>. 아임웹이 상품을 만든 날이다(idx 와 교차검증했다).
_CODE_DATE = re.compile(r"^s(\d{4})(\d{2})(\d{2})")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _props(node) -> dict:
    """카드의 data-product-properties(HTML 이스케이프된 JSON). 깨지면 빈 dict."""
    raw = node.attributes.get("data-product-properties") or ""
    try:
        return json.loads(_html.unescape(raw))
    except ValueError:
        return {}


def _uploaded_at(code: str) -> str:
    """상품 코드에서 등록일. 꼴이 다르면 지어내지 말고 비운다."""
    m = _CODE_DATE.match(code or "")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        for slug, category in CATEGORIES.items():
            url = f"{ROOT}/{slug}/"
            r = base.retry(lambda: c.get(url, params={"sort": "recent"}))
            r.raise_for_status()
            time.sleep(DELAY)

            doc = HTMLParser(r.text)
            cards = doc.css("div.shop-item")
            if not cards:
                # 세 칸 다 상품이 들어 있는 게 정상이다. 하나라도 비면
                # 쇼핑 위젯이 바뀐 것이지 상품이 없는 게 아니다.
                raise RuntimeError(f"{BRAND}: {slug} 칸 상품 0건 — 셀렉터가 깨졌다")

            for card in cards[:MAX_ITEMS]:
                p = _props(card)
                name = _clean(p.get("name"))
                if not name:
                    continue
                en = card.css_first(".item-summary p")
                idx = p.get("idx")
                it = Item(
                    brand=BRAND,
                    name=name,
                    # item-summary 는 설명이 아니라 영문명이다(docstring).
                    name_en=_clean(en.text()) if en else "",
                    image=p.get("image_url") or "",
                    category=category,
                    # 상품을 올린 날이지 출시일이 아니다. released_at 으로 안 올린다.
                    uploaded_at=_uploaded_at(p.get("code")),
                    # NEW 배지도 '신메뉴' 칸도 없다. 모름은 모름으로 둔다.
                    is_new=None,
                    url=f"{url}?idx={idx}" if idx else "",
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)

    if not items:
        raise RuntimeError(f"{BRAND}: 상품 0건")
    return items
