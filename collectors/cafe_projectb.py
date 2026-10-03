"""고망고 · 차얌 — ㈜프로젝트비의 두 브랜드.

같은 회사가 같은 CMS 로 만든 사이트라 한 파일에 묶는다(bon_if 선례).
개인정보처리방침에 두 사이트 모두 "(주)프로젝트비" 가 주체로 적혀 있고,
DNS 도 같은 IP(211.110.44.68) 다 — 그래서 `chayumm.com`·`chayumm.co.kr`
(NXDOMAIN)로 못 찾던 차얌 도메인을 **고망고 IP 를 역으로 짚어** 찾았다.
공식은 `chayam.co.kr`(차얌 - 茶원이 다른 밀크티), `gomango.kr`(고망고
공식홈페이지)다. `gomango.co.kr` 은 NXDOMAIN 이다.

⚠️ **둘 다 http 전용이다.** 443 이 Connection refused 라 https 로 못 바꾼다
(2026-10-03 실측). 그래서 사진 주소를 넣어도 base.derive() 가 지운다
(혼합 콘텐츠). 사진 없는 카드로 그린다 — 이 두 브랜드에서 가져오는 값은
**상품명과 날짜**다.

── 경로 ───────────────────────────────────────────────────────────────
둘 다 서버렌더 정적 HTML 이고 카드가 `ul.menu_list > li` 다. 브라우저 불필요.
  고망고 /contents/{mango,coffee,beverage,tea,dessert}.html   89건
  차얌   /contents/{menu_milktea,menu_coffee,menu_tea}.html    33건
카드 안쪽은 브랜드마다 조금 다르다.
  고망고 `<dd>상품명</dd>`
  차얌   `<dd><div class="menu_name"><h3>상품명</h3></div>
          <p class="menu_info">설명(사이즈)</p></dd>`
그래서 이름은 h3 가 있으면 h3, 없으면 dd 의 글자를 쓴다.

상품 상세 페이지가 **없다**(카드에 <a> 자체가 없다). Item.url 은 비워서
base.derive 가 SITES 의 브랜드 메뉴 주소로 떨어뜨리게 둔다.

── 신상 판정 (2026-10-03 실측) ─────────────────────────────────────────
🔴 **NEW 배지도 신메뉴 탭도 없다.** 두 사이트 어디에도 신제품 표시가 없어서
is_new 를 채울 근거가 0 이다(None 으로 둔다). 대신 **사진 파일명이 13자리
epoch(ms)** 다 — `/files/menu/IMG_1777863203573.png`. 이걸 uploaded_at 에
넣는다. released_at 은 비운다(브랜드가 출시일이라 말한 적이 없다).

날짜가 진짜 상품별인지 분포로 확인했다.
  고망고 89건 전건 날짜 있음. 2022-03 26건(사이트 구축분)을 빼면 나머지
         63건이 19개 달에 흩어져 있고, 같은 날 묶음이 2~10건이다 —
         '청포도 망고' 4종 2026-03-13, '딸망' 5종 2025-12-22, '초코망고'
         5종 2025-10-30 처럼 **라인 단위 출시**로 읽힌다. 일괄 재업로드로
         보이는 건 구축분 하나뿐이다.
  차얌   33건 전건 날짜 있음. 다만 **2020-07-06 이 마지막**이고 2019-03 에
         17건이 몰려 있다. 사이트가 5년째 멈춰 있다는 뜻이다. 그래도 0건이
         아니라 '최근 게 없다'가 맞는 그림이라 그대로 둔다 — 새 상품이
         올라오면 그날 날짜와 함께 잡힌다.
날짜가 60일 창 밖이면 rules.is_fresh 가 알아서 뺀다. is_new 가 없으니
화면에 올라오는 길은 날짜뿐이고, 그게 이 브랜드들에 맞는 수준이다.

⚠️ 이미지 Last-Modified 는 보지 않는다. 파일명 epoch 와 달리 서버 쪽
사정으로 바뀐다.
"""
import re
import time
from datetime import datetime, timedelta, timezone

from selectolax.parser import HTMLParser

from . import base
from .base import Item

KST = timezone(timedelta(hours=9))

# (브랜드, 사이트, 메뉴 경로들). 같은 CMS 라 파싱은 공통이다.
#
# ⚠️ 이 목록을 `BRANDS` 라고 부르면 안 된다. 모듈 수준의 `BRANDS` 는
# collect.orphans() 와 등록 검사가 **브랜드 이름 문자열 목록**으로 읽는 자리다
# (bon_if.py 선례). 튜플을 넣어 뒀더니 "base.BRANDS 에 '('고망고', …)' 없음"
# 이라는 엉뚱한 경고가 났다. 사양은 SPECS, 이름 목록만 BRANDS 로 둔다.
SPECS = [
    ("고망고", "http://gomango.kr",
     ("mango", "coffee", "beverage", "tea", "dessert")),
    ("차얌", "http://chayam.co.kr",
     ("menu_milktea", "menu_coffee", "menu_tea")),
]
BRANDS = [name for name, _site, _pages in SPECS]

DELAY = 2.0
MAX_PAGES = 10        # 폭주 방지. 현재 브랜드당 최대 5면.

# 사진 파일명의 13자리 epoch(ms). `/files/menu/IMG_1777863203573.png`.
_STAMP = re.compile(r"(\d{13})")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _uploaded_at(src: str) -> str:
    """사진 파일명의 epoch(ms) → 'YYYY-MM-DD'. 아니면 빈 문자열."""
    m = _STAMP.search(src or "")
    if not m:
        return ""
    ts = int(m.group(1)) / 1000
    # 2015~오늘+1일 밖이면 epoch 가 아니라 다른 숫자다. 지어내지 않는다.
    if not (1420070400 <= ts <= datetime.now().timestamp() + 86400):
        return ""
    # 러너가 UTC 면 KST 새벽 업로드분이 하루 당겨진다.
    return datetime.fromtimestamp(ts, KST).strftime("%Y-%m-%d")


def _abs(site: str, src: str) -> str:
    if not src:
        return ""
    if src.startswith("http"):
        return src
    return site + "/" + src.lstrip("./")


def _cards(html: str, site: str) -> list:
    """`ul.menu_list > li` → [(이름, 설명, 사진 주소)]."""
    out = []
    for li in HTMLParser(html).css(".menu_list li"):
        img = li.css_first("img")
        h3 = li.css_first("h3")
        dd = li.css_first("dd")
        info = li.css_first(".menu_info")
        if h3:
            name = _clean(h3.text())
        elif dd:
            # 차얌 꼴이 아니면 dd 전체가 이름이다. 설명 노드가 섞여 있으면 뺀다.
            name = _clean(dd.text().replace(info.text() if info else "", ""))
        else:
            name = ""
        if not name or not img:
            continue
        out.append((name,
                    _clean(info.text()) if info else "",
                    _abs(site, img.attributes.get("src", ""))))
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    with base.client() as c:
        for brand, site, pages in SPECS:
            seen = set()
            got = 0
            for page in pages[:MAX_PAGES]:
                url = f"{site}/contents/{page}.html"
                r = base.retry(lambda: c.get(url))
                r.raise_for_status()
                for name, info, img in _cards(r.text, site):
                    it = Item(
                        brand=brand,
                        name=name,
                        # 사이즈 표기뿐인 설명('(L, XL)')은 설명이 아니다.
                        desc="" if re.fullmatch(r"[()\sA-Za-z,/0-9iLter]*", info) else info,
                        image=img,              # http 라 derive 가 지운다(docstring)
                        uploaded_at=_uploaded_at(img),
                    )
                    if it.key in seen:
                        continue
                    seen.add(it.key)
                    items.append(it)
                    got += 1
                time.sleep(DELAY)
            # 브랜드 하나가 통째로 비면 조용한 0건 수집이 된다. 드러낸다.
            if not got:
                raise RuntimeError(f"{brand} 메뉴 0건 — 셀렉터나 경로가 깨졌을 수 있다")
            dated = sum(1 for it in items if it.brand == brand and it.uploaded_at)
            # 날짜가 유일한 신상 근거다. 전건이 비면 신상 판정이 통째로 사라진다.
            if not dated:
                raise RuntimeError(
                    f"{brand} 날짜 0건 — 사진 파일명 꼴(IMG_<epoch ms>)이 바뀐 것 같다")
    return items
