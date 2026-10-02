"""스쿨푸드.

(주)에스에프이노베이션 운영. `/menu/menu.html` 한 장(70KB)에 81건이 통째로
SSR 로 들어 있다. 브라우저 불필요, UTF-8, **1요청**이면 끝난다.
루트(`/`)가 `/main/gate.html`(홈페이지 / 창업문의 갈림길)로 302 되는 구조라
`/` 만 받고 "빈 셸"로 판정하면 살아 있는 사이트를 버린다.

robots.txt: **200 / 25바이트 / `User-agent: * / Allow: /`**.
이용약관은 푸터에 링크가 없어 확인하지 못했다. 즉 이 브랜드는 "약관에 금지
조항이 없다"가 아니라 "약관을 확인하지 못했다" 상태로 붙는 것이다.
삭제 요청이 오면 다투지 말고 즉시 내린다(김밥천국과 같은 처분).

## ⚠️ https 가 자체서명이다. http 로 받아야 한다

`www.schoolfood.co.kr:443` 인증서가 **nginx 기본 더미**다.

    s:C=GB, ST=Berkshire, L=Newbury, O=My Company Ltd
    i:  (self-signed)   sigalg: md5WithRSAEncryption   NotAfter: 2117-03-20

`*.gabia.io`(태극당)·`*.blueweb.co.kr`(노브랜드)와 같은 계열인데 **지문이 또
다르다** — 호스팅사 와일드카드가 아니라 OpenSSL 예제 인증서 그대로다.
curl 은 exit 60, 브라우저도 거부한다. **`http://` 로는 200 이고 내용이 진짜다.**
`verify=False` 로 https 를 뚫지 않는다 — 뚫어도 아래 이미지 문제가 안 풀린다.

## ⚠️ 이미지는 들어와도 화면에 안 뜬다. 그래도 넣는다

상품 이미지 90장이 전부 `http://www.schoolfood.co.kr/upload/product/…` 절대경로다
(https 는 1장뿐). 우리 페이지가 https 라 브라우저가 혼합콘텐츠로 막고,
`base.derive()` 가 `http://` 를 아예 빈 값으로 지운다. 에그드랍 73건이 빈
네모였던 그 건과 같다. **그런데 스킴만 올려서도 안 된다** — 이 호스트는
https 가 위의 자체서명이라 `https://` 로 바꿔치기하면 브라우저가 또 거부한다.
이미지를 우리 쪽으로 받아 재호스팅하는 수밖에 없는데 그건 이 어댑터가 할
일이 아니다. 받은 그대로 담고 derive 가 지우게 둔다 — 여기서 우리가 미리
비우면 "왜 사진이 없나"를 다음 사람이 다시 조사하게 된다.

## 신제품 신호 — `<span class="new">` 배지

2026-10-02 실측: 81건 중 **new 14건 · best 13건**. 같은 `.type_txt` 안에
두 종류가 들어가는 선별 배지이고 전수가 아니다(달콤왕가탕후루 14/14 전수
장식과 정반대). 원본에 주석 처리된 배지는 **0건**이다.

    <div class="type_txt"><span class="new">new</span></div>
    <p class="tit">짱아치 충무마리</p>
    <p class="des">오징어·어묵·짱아치가 완성하는 충무의 삼합</p>

## ⚠️ 날짜는 안 쓴다 — 이미지 파일명의 타임스탬프는 출시일이 아니다

상품 이미지 파일명 끝이 전부 `_20260120082502.jpg` 꼴 14자리다. 분포가
2020-06 ~ 2026-08 로 넓어 "일괄 재업로드"는 아니라서 쓰고 싶어지는데,
**같은 종류의 파일명 날짜가 김가네에서 틀렸음이 증명됐다**(`data-idx=20`
짜리 오래된 상품의 이미지 날짜가 어제. `collectors/snack_gimgane.py` 참고).
사진만 교체해도 갱신되는 값이라 `released_at` 은 물론 `uploaded_at` 에도
넣지 않는다. 신제품 판정은 배지와 collect 의 어제 대비 diff 에 맡긴다.

상품별 주소는 **없다.** 카드의 `<a>` 에 `href` 가 아예 없다. `url` 을 비워
`base.SITES` 폴백에 맡긴다. 가격도 사이트에 없다.
"""
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "스쿨푸드"
# https 가 자체서명이라 http 로 받는다. 위 docstring 참고 — 고치지 마라.
URL = "http://www.schoolfood.co.kr/menu/menu.html"
DELAY = 2.0   # 1요청뿐이지만 다음 사람이 페이지를 늘릴 때를 위해 둔다.


def _text(node, sel) -> str:
    n = node.css_first(sel)
    return " ".join(n.text().split()) if n else ""


def _badges(card) -> list:
    """`.type_txt` 안의 배지. 지금 관측되는 값은 new 와 best 둘뿐이다."""
    return [t for t in (" ".join(s.text().split())
                        for s in card.css(".type_txt span")) if t]


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(URL))
        r.raise_for_status()
        time.sleep(DELAY)

    # 분류는 섹션 제목이다(마리·떡볶이·라이스·면·사이드). 상품 카드 자체에는
    # 분류 정보가 없어서 섹션을 돌며 붙인다.
    for sec in HTMLParser(r.text).css("section.menu_sec"):
        category = _text(sec, "h3") or _text(sec, "h2")
        for card in sec.css("ul.menu_list > li"):
            name = _text(card, ".txt_bx .tit")
            if not name:
                continue
            img = card.css_first(".img_cover img")
            labels = _badges(card)
            it = Item(
                brand=BRAND,
                name=name,
                desc=_text(card, ".txt_bx .des"),
                # http 로 들어온다. derive 가 지운다(위 docstring 참고).
                image=img.attributes.get("src", "") if img else "",
                labels=labels,
                category=category,
                # new 배지만 True. 배지 없음은 '아니다'가 아니라 '모른다'다.
                is_new=True if "new" in labels else None,
                # 상품별 주소가 없다(카드 <a> 에 href 자체가 없다).
                url="",
            )
            if it.key in keys:
                continue
            keys.add(it.key)
            items.append(it)

    # 이 브랜드의 신호는 배지 하나뿐이다. 테마가 바뀌어 `.type_txt span` 이
    # 안 잡히면 건수는 81 그대로라 collect 의 0건·급감 가드에 안 걸리고,
    # 화면에서는 '신상이 없는 브랜드' 로 조용히 바뀐다. 그 날 로그에 이유를 남긴다.
    if items and not any(i.is_new for i in items):
        print(f"[{BRAND}] new 배지가 0건이다 — 배지가 사라진 건지 "
              f"선택자가 깨진 건지 확인해야 한다")
    return items
