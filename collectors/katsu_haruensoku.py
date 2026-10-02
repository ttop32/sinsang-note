"""하루엔소쿠. 가맹점 94개 — 돈까스 업종 6위.

도메인 주의. `haruensoku.com` 은 **https 인증서 호스트명이 안 맞는다**(SAN 에 .com 이
없다). 그런데 우회할 필요가 없다 — `http://haruensoku.com/` 이 `https://haruensoku.co.kr/`
로 리다이렉트되고 그쪽은 인증서가 정상이다. 그래서 어댑터는 처음부터 `.co.kr` 로 간다.
에그드랍처럼 평문으로 떨어질 일이 없다. 2026-10-02 실측.

메뉴는 홈의 탭이고 **카테고리마다 AJAX 조각이 따로 있다.** 홈 HTML 에 그 주소가
`<a href>` 로 그대로 적혀 있다. 조각은 쿠키·리퍼러 없이 열리고 순수 HTML 이다.

  GET /bbs/load-cuisine.php?cat_no=1   돈까스  15건
  GET /bbs/load-cuisine.php?cat_no=2   면       10건
  GET /bbs/load-cuisine.php?cat_no=3   밥       16건
  GET /bbs/load-cuisine.php?cat_no=4   사이드    7건
4요청에 48건. 마크업은 `li.cuisine-slide-item > (div.cuisine-photo > img) + div.cuisine-tit`
한 가지뿐이라 셀렉터가 단순하다.

**신제품 신호는 두 개이고 서로를 검증한다.** 이 브랜드엔 NEW 배지도 '신메뉴' 탭도 없다.
  ① 이미지 경로의 상품 번호 — `/uploaded/product/<id>/large_<hash>.png` 의 `<id>` 가
     1씩 늘어나는 등록 순번이다. 48건이 2~50 범위에 들어 있다.
  ② 그 이미지의 Last-Modified 헤더.
둘을 대조하니 **번호 순서와 시각 순서가 어긋나는 데가 한 군데도 없었다**(2026-10-02).

  id 50·49·48  2026-09-28  투움바카츠 · 투움바우동 · 스키야키나베
  id 47        2026-06-26  체다철판카츠
  id 46~40     2026-05-12  메가치즈바 · 비빔우동 · 붓카케우동 · 김치규동 … 6건
  id 39 이하    2025-02-10~17  38건 (사이트 구축 때 일괄 등록)

번호가 등록 순번이라는 걸 날짜가 독립적으로 뒷받침하므로 신호로 쓴다.
`uploaded_at` 에만 넣는다 — **`released_at` 로 올리지 않는다.** 이건 이미지 파일을
올린 시각이지 브랜드가 말하는 출시일이 아니다(본아이에프·BRAND-CANDIDATES §6-5 선례).
`is_new` 는 비운다(None). 브랜드가 신제품이라고 표시한 자리가 없다.

요청 수: 목록 4 + 이미지 HEAD 48 = 52회. HEAD 라 본문을 받지 않는다. 그래도 적지 않아서
`MAX_HEADS` 로 상한을 두고, **번호가 큰 쪽부터** 날짜를 채운다. 상한에 걸려 날짜를
못 받은 오래된 상품은 uploaded_at 이 빈 채로 남는다 — 어차피 화면에 오를 일이 없는
구간이고, 날짜를 지어내느니 비우는 쪽이다.
개별 HEAD 가 실패하면 그 상품만 비운다. 목록이 깨지면 RuntimeError 로 드러낸다.

상품 상세 페이지는 없다. 조각이 이름과 사진만 준다 — 설명·가격·영문명이 전부 없다.
그래서 Item.url 은 SITES 폴백(홈)으로 떨어진다.

robots.txt: `User-agent: * / Allow: / / Disallow: /backoffice/` — 우리가 받는
`/bbs/load-cuisine.php` 와 `/uploaded/` 는 허용 범위다.
이용약관: 푸터에 링크가 없다. `/include/pop_privacy.php`(개인정보처리방침)만 있다.
금지 조항을 확인하지 못했다는 뜻이지 없다는 뜻이 아니다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "하루엔소쿠"
HOST = "https://haruensoku.co.kr"      # .com 은 인증서 호스트명 불일치. docstring 참고
LIST_PATH = "/bbs/load-cuisine.php"
DELAY = 1.5          # 목록 요청 간격(초)
HEAD_DELAY = 0.8     # 이미지 HEAD 간격(초). 본문을 안 받으므로 조금 짧게 둔다
MAX_HEADS = 60       # 폭주 방지. 현재 48건

# cat_no → 화면 라벨. 홈의 탭 순서 그대로다(라벨은 사이트에 글자로 안 나와서 우리가 붙였다).
CATEGORIES = {
    1: "돈까스",
    2: "면",
    3: "밥",
    4: "사이드",
}

_PRODUCT_ID = re.compile(r"/uploaded/product/(\d+)/")

# Last-Modified: Mon, 28 Sep 2026 05:23:16 GMT
_MONTHS = {m: i for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}
_LM = re.compile(r"\w{3},\s*(\d{1,2})\s+(\w{3})\s+(\d{4})")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _uploaded_at(c, url: str) -> str:
    """이미지 Last-Modified 를 날짜로. 못 받으면 비운다."""
    try:
        r = base.retry(lambda: c.head(url))
    except Exception:
        return ""
    m = _LM.search(r.headers.get("last-modified", ""))
    if not m or m.group(2) not in _MONTHS:
        return ""
    return f"{m.group(3)}-{_MONTHS[m.group(2)]:02d}-{int(m.group(1)):02d}"


def fetch() -> list[Item]:
    items: list[Item] = []
    order: dict = {}        # Item.key → 상품 번호. 날짜를 받을 순서를 정하는 데 쓴다
    seen = set()
    with base.client() as c:
        for cat_no, label in CATEGORIES.items():
            r = base.retry(lambda: c.get(HOST + LIST_PATH,
                                         params={"cat_no": cat_no}))
            r.raise_for_status()
            cards = HTMLParser(r.text).css("li.cuisine-slide-item")
            if not cards:
                raise RuntimeError(
                    f"하루엔소쿠 {label}(cat_no={cat_no}): 상품 0건 — 셀렉터가 깨졌다")

            for li in cards:
                tit = li.css_first("div.cuisine-tit")
                img = li.css_first("div.cuisine-photo img")
                name = _clean(tit.text()) if tit else ""
                if not name:
                    continue
                src = (img.attributes.get("src") or "") if img else ""
                m = _PRODUCT_ID.search(src)
                it = Item(
                    brand=BRAND,
                    name=name,
                    image=HOST + src if src.startswith("/") else src,
                    category=label,
                    # NEW 배지도 신메뉴 탭도 없다. 모름은 모름으로 둔다.
                    is_new=None,
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                order[it.key] = int(m.group(1)) if m else -1
                items.append(it)

            time.sleep(DELAY)

        # 번호가 큰(= 최근 등록) 쪽부터 날짜를 채운다. 상한에 걸리면 오래된 쪽이 빈다.
        for it in sorted(items, key=lambda x: -order[x.key])[:MAX_HEADS]:
            if not it.image:
                continue
            it.uploaded_at = _uploaded_at(c, it.image)
            time.sleep(HEAD_DELAY)

    if not items:
        raise RuntimeError("하루엔소쿠: 상품 0건 — 목록 형식이 바뀌었다")
    return items
