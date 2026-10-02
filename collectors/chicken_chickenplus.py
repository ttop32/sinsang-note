"""치킨플러스.

공정위 등록 가맹점 279개로 치킨 업종 20위. 아임웹(imweb) 게시판을 메뉴판으로 쓰고
목록이 SSR 이라 브라우저는 필요 없다. 분류가 곧 페이지다 —
`/CHICKEN`(18) · `/PLUS-MENU`(3) · `/SIDE-MENU`(18) = 39건.

🔴 **이 브랜드는 신호가 약하다. 넣을지 말지가 갈리는 경계선이라 근거를 남긴다.**

신제품 신호:
  is_new  **없다.** NEW 배지도 신메뉴 탭도 등록일 컬럼도 없다. 전건 None 이다.
  released_at  없다. 비운다.
  uploaded_at  아임웹 CDN 경로의 날짜(`cdn.imweb.me/thumbnail/20260304/…`).
          2026-10-02 실측 39건 분포가 이렇다 —
              20251110 **22건** · 20241112 **14건** · 20230209 2건 · 20260304 1건
          네 갈래지만 실상은 **두 번의 일괄 업로드(36건, 92%)에 낱개 셋**이다.
          호식이두마리치킨·땅땅치킨은 같은 아임웹인데도 날짜가 10~20갈래로 흩어져
          제품별 업로드일로 쓸 만했다. 여기는 그 수준이 아니다.
          그래도 비우지 않고 넣는 이유는 **덩어리 밖 세 건이 진짜 정보**이기 때문이다
          (핫쵸킹 레드 2026-03-04 등). 덩어리 안의 선후는 못 가린다 — 그건
          collect.py 의 '어제 없던 키가 오늘 있다' diff 가 판정한다.
          어디까지나 업로드 시각이라 released_at 에는 안 넣는다.

함정 셋. 전부 실제로 밟았다.

🔴 ① **`idx` 를 날짜로 바꾸지 마라.** 게시물 번호가 단조증가라
   (170256122 > 168532972 > 162957850 > 123793499 > 18941583 > 12672927)
   타임스탬프처럼 보이지만 정렬 힌트일 뿐이다.

🔴 ② **상품명으로 신제품을 판정하지 마라.** 상품 하나가 아예 `NEW 크리스피 후라이드`
   라는 **이름**을 달고 있다. 배지가 아니라 이름의 일부다. 이름에서 NEW 를 긁으면
   그 한 건만 영원히 신제품이 된다.

🔴 ③ **정규식으로 이미지와 이름을 멀리서 짝지으면 어긋난다.** 처음에 수백 글자를
   건너뛰며 묶는 정규식을 썼더니 **사이트 로고**(`20260304/ca3810a975b8f.png`)가
   상품 이미지 자리에 끼어들 수 있었다. 로고가 하필 상품 하나와 같은 날짜 폴더에
   있어서 눈으로는 안 드러난다. 그래서 `div.ma-item._post_item_wrap` 카드 **안에서만**
   이미지·이름·링크를 꺼낸다.

⚠️ 제목 앞에 숨은 `<em class="notice-block" style="display: none">공지</em>` 가 붙어
   있다. `.text()` 를 그대로 쓰면 전 상품 이름이 '공지 …' 로 시작한다. 떼어낸다.
⚠️ 아임웹 HTML 에는 테마 CSS 때문에 'new' 문자열이 수백 번 나온다
   (`new_fixed_header`·`new_header_mode`). NEW 를 정규식으로 세면 전건 오탐이다.

상품 상세는 게시판 보기 주소(`?bmode=view&idx=…`)다. 목록 href 에 base64 검색
파라미터(`?q=…`)가 붙어 오는데 상품과 무관해서 `idx` 만 떼어 깔끔하게 조립한다.
가격은 목록에 없다. 세트·행사 상품은 이 게시판에 없고 할인 표시도 없어 promo 는
전건 False 다. robots.txt 는 아임웹 기본(`Allow: /` + 회원·장바구니 Disallow)이다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "치킨플러스"
SITE = "https://chickenplus.co.kr"
# (경로, 화면상 분류)
LISTS = [("/CHICKEN", "치킨"), ("/PLUS-MENU", "플러스메뉴"), ("/SIDE-MENU", "사이드")]

MAX_ITEMS = 200   # 폭주 방지. 현재 39건.
DELAY = 0.6       # 목록 요청 간격(초). 한 장이 크다.

# 카드 배경에 박힌 CDN 이미지. 경로 가운데 8자리가 업로드 날짜다.
_IMG = re.compile(
    r'url\(["\']?(https://cdn\.imweb\.me/thumbnail/(\d{8})/[^"\')]+)')


def _card(node):
    """카드 하나에서 (이미지, YYYY-MM-DD, 이름, idx). 못 읽으면 None."""
    box = node.css_first("div.card")
    m = _IMG.search(box.attributes.get("style", "") if box else "")
    title = node.css_first("div.title.title-block")
    if not title:
        return None
    # 숨은 '공지' 뱃지를 떼고 이름만 남긴다.
    for em in title.css("em"):
        em.decompose()
    name = " ".join(title.text().split())
    a = node.css_first("a.post_link_wrap")
    idx = re.search(r"idx=(\d+)", a.attributes.get("href", "") if a else "")
    d = m.group(2) if m else ""
    return (m.group(1) if m else "",
            f"{d[:4]}-{d[4:6]}-{d[6:]}" if d else "",
            name,
            idx.group(1) if idx else "")


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        for path, cate in LISTS:
            time.sleep(DELAY)
            r = base.retry(lambda p=path: c.get(SITE + p))
            r.raise_for_status()
            cards = HTMLParser(r.text).css("div.ma-item._post_item_wrap")
            if not cards:
                raise RuntimeError(f"{path} 목록이 비었다 — 셀렉터가 깨졌을 가능성")

            for node in cards:
                got = _card(node)
                if not got:
                    continue
                image, day, name, idx = got
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    image=image,
                    category=cate,
                    # 경로 날짜는 업로드일이다. 출시일이 아니라 released_at 은 비운다.
                    uploaded_at=day,
                    # NEW 배지도 신메뉴 탭도 없다. 모르는 건 모른다고 둔다.
                    # (이름에 'NEW' 가 든 상품이 있지만 그건 이름이다 — 위 함정 ②)
                    is_new=None,
                    promo=False,
                    url=f"{SITE}{path}/?bmode=view&idx={idx}" if idx else SITE + path,
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
                if len(items) >= MAX_ITEMS:
                    break

        if not items:
            raise RuntimeError("상품이 하나도 안 나왔다 — 셀렉터가 깨졌을 가능성")
    return items
