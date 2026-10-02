"""엔제리너스(Angelinus). 롯데지알에스(주).

도메인부터 바로잡는다. angelinus.com 은 **브랜드 사이트가 아니다** —
2026-10-02 실측으로 TLS 인증서가 만료됐고, 검증을 꺼도 `403 /error.html` 만
돌려준다. IP 가 lottegrs.com 과 같은 210.93.146.27 이라 본사 서버에 남은
옛 호스트로 보인다. www.angelinus.com 은 DNS 자체가 없다.

살아 있는 곳은 롯데GRS 통합몰 **www.lotteeatz.com** 이다(롯데리아·엔제리너스·
크리스피크림 3개 브랜드가 한 사이트에 있다). robots 차단은 운영자 승인 아래
무시한다. 삭제 요청이 오면 즉시 내린다.
⚠️ **롯데리아(/brand/ria)는 이 어댑터가 건드리지 않는다.** 담당이 다르다.

## 경로를 다시 쟀다

1차 조사는 `/brand/...` 가 404 JSON 이고 sitemap 의 실제 경로는 주문 플로우
셸(`/hsv/products/{divcd}/{storecd}`)뿐이라고 봤다. 2026-10-02 재측정 결과
**`/brand/angel` 은 200 이고 완전한 SSR 이다**(550KB, 상품 112카드).
주문 플로우를 읽을 이유가 없다 — 거기는 세트·할인이 섞인다.

  GET https://www.lotteeatz.com/brand/angel   200, 1요청, 브라우저 불필요

마크업은 `section.mn-section` > `h2.mn-section-title`(카테고리) >
`ul.mn-grid > li` > `.mn-card`(이미지·배지·이름) 다.

## 신제품 신호

두 가지가 있고 **겹치지 않는다**. 둘 다 쓴다.

  ① 카테고리 '❤️신제품❤️' — 11건
  ② 카드 배지 `span.mn-badge` 의 **글자가 'NEW'** — 4품목

②는 ①의 부분집합이다(4건 전부 신제품 카테고리 안에 있다). 그런데 ①에만 있는
7건이 **②보다 더 최신이다** — 배지 쪽은 이미지 업로드일이 2026-07-16 인데
배지 없는 라이트모카크림라떼 등은 2026-09-10 이다. 즉 배지는 늦게 붙고 늦게
떨어지는 쪽이고, 카테고리가 브랜드가 실제로 관리하는 '신제품' 칸이다.
그래서 **둘의 합집합**을 is_new=True 로 둔다(11품목 / 106품목 = 10.4%).

⚠️ **`aria-label` 을 믿으면 안 된다.** 'BEST' 배지에도 `aria-label="신메뉴"` 가
그대로 박혀 있다(5건). aria-label 로 세면 9품목이 되고 아메리카노·에그햄치즈
토스트·딸기 스노우 같은 상시 메뉴가 신상이 된다. **글자로 가른다.**
배지 글자 분포는 NEW 8회(4품목×2카테고리) / BEST 5회뿐이다.

## 날짜

상세에도 출시일이 없다. 이미지 경로의 업로드 날짜만 쓴다.
  /upload/product/**2026/07/16**/20260716143051430_0.png → 2026-07-16
**uploaded_at 까지만 쓰고 released_at 에는 넣지 않는다.** 일괄 재업로드 자국은
없다 — 112장이 2019-12 부터 2026-09 까지 29개 월에 흩어져 있고 최다 달이 13장
(12%)이다. 할리스(한 달에 1/3)와는 모양이 다르다.

## 그 밖에

- 한 상품이 두 카테고리에 걸친다(텐션젤리에이드 = 신제품 + 엔제린 밸런스).
  처음 만난 카테고리로 적고 뒤는 버린다. 다만 is_new 는 **둘 중 하나라도
  신상이면 True** 로 올린다 — 먼저 만난 쪽이 일반 카테고리일 수 있다.
- '(D)보틀+반미세트' 같은 세트가 신제품 칸에 섞인다. 여기서 거르지 않는다 —
  collect.drop_sets() 가 이름으로 처리한다(Item 주석의 지침).
- desc 는 목록에 없고 상세(/products/introductions/REP_xxxxxx)에만 있다.
  상세가 1건당 약 390KB 라 전건 받으면 40MB 다. **신상만** 받는다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "엔제리너스"
SITE = "https://www.lotteeatz.com"
LIST_URL = f"{SITE}/brand/angel"
DETAIL_URL = f"{SITE}/products/introductions"
BRAND_CODE = "ANGELINUS"
DELAY = 2.0
MAX_DETAILS = 25     # 폭주 방지. 현재 신상 11건.

# 신제품 카테고리 이름에 하트 이모지가 붙어 있다(❤️신제품❤️). 이모지가 바뀌어도
# 따라가게 '신제품' 포함 여부로 본다.
NEW_CATEGORY = "신제품"
NEW_BADGE = "NEW"


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _uploaded_at(img: str) -> str:
    """이미지 경로의 업로드 날짜(/upload/product/2026/07/16/...)."""
    m = re.search(r"/upload/\w+/(\d{4})/(\d{2})/(\d{2})/", img or "")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def _image(src: str) -> str:
    """썸네일 변환 꼬리(/dims/resize/x214/optimize)를 떼고 원본을 쓴다.

    카드에 박힌 건 214px 짜리라 상세 화면에서 흐리다. 꼬리만 떼면 원본이 온다.
    """
    src = (src or "").split("/dims/")[0]
    if src.startswith("//"):
        return "https:" + src
    return src if src.startswith("http") else (SITE + src if src else "")


def _desc(c, pid: str) -> str:
    """상세의 한 줄 소개. 실패하면 조용히 빈 값으로 둔다."""
    r = base.retry(lambda: c.get(f"{DETAIL_URL}/{pid}",
                                 params={"brandCode": BRAND_CODE}))
    r.raise_for_status()
    p = HTMLParser(r.text).css_first(".prod-detail-header p.btext")
    return _clean(p.text()) if p else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    by_key: dict = {}
    with base.client() as c:
        r = base.retry(lambda: c.get(LIST_URL))
        r.raise_for_status()
        doc = HTMLParser(r.text)

        sections = doc.css("section.mn-section")
        # 섹션이 통째로 비면 조용한 0건 수집이 된다. 예외로 올려 드러낸다.
        if not sections:
            raise RuntimeError("엔제리너스 섹션 0건 — 셀렉터가 깨졌을 수 있다")

        for sec in sections:
            h = sec.css_first(".mn-section-title")
            cat = _clean(h.text()) if h else ""
            for li in sec.css("ul.mn-grid > li"):
                n = li.css_first(".mn-card-name")
                name = _clean(n.text()) if n else ""
                if not name:
                    continue
                # 배지는 **글자**로 가른다. aria-label 은 BEST 에도 '신메뉴'다.
                badges = [_clean(b.text()).upper() for b in li.css(".mn-badge")]
                is_new = (NEW_CATEGORY in cat) or (NEW_BADGE in badges)
                img = li.css_first("img.mn-card-img")
                body = li.css_first(".mn-card-body")
                pid = (body.attributes.get("id") or "") if body else ""
                it = Item(
                    brand=BRAND,
                    name=name,
                    image=_image(img.attributes.get("src", "") if img else ""),
                    category=cat,
                    uploaded_at=_uploaded_at(img.attributes.get("src", "") if img else ""),
                    is_new=is_new,
                    url=f"{DETAIL_URL}/{pid}?brandCode={BRAND_CODE}" if pid else "",
                )
                old = by_key.get(it.key)
                if old:
                    # 같은 상품이 신제품 칸과 일반 칸에 둘 다 있다. 신상 쪽을 남긴다.
                    old.is_new = old.is_new or is_new
                    continue
                by_key[it.key] = it
                items.append(it)

        for it in [i for i in items if i.is_new][:MAX_DETAILS]:
            pid = it.url.split("?")[0].rsplit("/", 1)[-1]
            if not pid:
                continue
            time.sleep(DELAY)
            it.desc = _desc(c, pid)

    return items
