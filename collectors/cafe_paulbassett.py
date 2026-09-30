"""폴 바셋(엠즈씨드).

도메인부터 조심해야 한다. paulbassett.co.kr 은 NXDOMAIN 이고 pbkorea.co.kr 은
'파티앤벌룬코리아'라는 무관한 풍선 쇼핑몰이다(2026-09-30 실측, 제목으로 확인).
정답은 baristapaulbassett.co.kr 인데 여기도 apex 는 TLS 에서 끊기고 www 만 붙는다
— 설빙과 정반대다. 어느 쪽이 살아나도 붙도록 후보를 순회한다.

/menu/List.pb?cid1=A..E 다섯 장이 전부다. SSR 이고 페이징이 없어 5요청이면 끝난다.
브라우저 불필요.

신제품 신호:
  is_new  카드의 <span class="newIcon">New</span>. 219건 중 38건에 붙어 있고 나머지는
          iconArea 가 비었거나 bestIcon 이다. 브랜드가 선별해서 다는 배지라 없으면
          '신제품 아님'이 확인된 것으로 보고 False 를 준다.
  날짜    브랜드가 상품 단위로 출시일을 주지 않는다. released_at 은 비워둔다.
          이미지 파일명 끝의 타임스탬프(thumbnail_1_202609210743289101.jpg)는
          uploaded_at 까지만 쓴다. 메가·할리스 선례대로 업로드 시각을 출시일이라고
          우기지 않는다. 다만 여기선 newIcon 붙은 것들이 2026-05~09, bestIcon 은
          2019-03 으로 갈려 있어 신호로서 꽤 맞는 편이다.

url 은 목록 카드의 goView('PB183714') 에서 뽑은 dpid 로 조립한다. 사이트 자체는
숨은 폼(moveFrm)을 POST 로 던지지만 같은 주소에 GET 으로 dpid 를 붙여도 같은 상세가
나온다(2026-09-30 실측: GET /menu/View.pb?dpid=PB183714 → 200, 19,001바이트,
title 'MENU | PaulBassett', .menuTit 에 '커피큐브 WITH 아메리카노'). 조각이 아니라
레이아웃이 다 붙은 독립 페이지다. dpid 는 목록 HTML 에 이미 있어서 요청이 늘지 않는다.

MENU > NEW 전용 탭(/menu/new/List.pb)은 쓰지 않는다. 상품 목록이 아니라
'Mellow Sweet, Autumn Moment' 같은 캠페인 글 2건이고, 본문이 이미지 한 장뿐이라
어떤 상품이 그 캠페인인지 텍스트로 알 방법이 없다(2026-09-30 실측).

desc 는 상세(POST /menu/View.pb, dpid=제품코드)에만 있다. 219건 전부 받으면
219요청이라 값이 안 맞고, 이 서비스가 화면에 올리는 건 신제품뿐이라
newIcon 붙은 것만 상한을 두고 받는다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "폴바셋"
HOSTS = ("https://www.baristapaulbassett.co.kr", "https://baristapaulbassett.co.kr")
LIST_PATH = "/menu/List.pb"
VIEW_PATH = "/menu/View.pb"
DELAY = 1.0          # 요청 간격(초)
MAX_DETAILS = 80     # 폭주 방지. 현재 newIcon 은 38건.

# 목록 탭 cid1 ↔ 대분류. 하위 cid2(Coffee/Latte/Cold Brew…)까지 돌면 요청이
# 다섯 배가 되는데 얻는 게 소분류 이름뿐이라 대분류만 쓴다.
CATEGORIES = [
    ("A", "COFFEE"),
    ("B", "BEVERAGE"),
    ("C", "ICE-CREAM"),
    ("D", "FOOD"),
    ("E", "PRODUCT"),
]


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _abs(host: str, src: str) -> str:
    if not src:
        return ""
    return src if src.startswith("http") else host + src


def _uploaded_at(img_url: str) -> str:
    """이미지 파일명 끝의 업로드 타임스탬프(202609210743289101)를 날짜로."""
    m = re.search(r"_(\d{4})(\d{2})(\d{2})\d{10}\.", img_url)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def _dpid(node) -> str:
    """goView('PB184039') 의 제품코드. 상세 요청과 상품 URL 조립에 쓴다."""
    a = node.css_first("a[onclick]")
    m = re.search(r"goView\('([^']+)'\)", a.attributes.get("onclick", "")) if a else None
    return m.group(1) if m else ""


def _live_host(c) -> str:
    """목록을 실제로 돌려주는 호스트를 고른다. 전부 죽었으면 마지막 오류를 올린다.

    상태코드만 보지 않는다. 죽은 쪽이 파킹 페이지를 200 으로 주는 사고가
    스타벅스에서 이미 있었다. 목록 요소가 파싱되는지까지 확인한다.
    """
    last = None
    for h in HOSTS:
        try:
            r = c.get(h + LIST_PATH, params={"cid1": CATEGORIES[0][0]})
            r.raise_for_status()
            if not HTMLParser(r.text).css(".menuList ul.listStyleB > li"):
                raise RuntimeError("목록 요소 없음")
            return h
        except Exception as e:                       # 연결 실패·TLS·HTTP·빈 목록 전부
            last = f"{h} → {type(e).__name__}"
    raise RuntimeError(f"폴바셋 호스트 전부 사용 불가 ({last})") from None


def _desc(c, host: str, dpid: str) -> str:
    """상세의 한 줄 소개(.menuTit dd). 상세는 GET 이 아니라 폼 POST 로 연다."""
    r = base.retry(lambda: c.post(host + VIEW_PATH, data={"dpid": dpid}))
    r.raise_for_status()
    dd = HTMLParser(r.text).css_first(".menuTit dd")
    return _clean(dd.text()) if dd else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        host = _live_host(c)
        pending = []                                  # (Item, dpid) — 상세를 받을 신제품

        for cid, label in CATEGORIES:
            r = base.retry(lambda: c.get(host + LIST_PATH, params={"cid1": cid}))
            r.raise_for_status()
            cards = HTMLParser(r.text).css(".menuList ul.listStyleB > li")
            # 탭이 통째로 비면 조용한 부분수집이 된다. 예외로 올려 드러낸다.
            if not cards:
                raise RuntimeError(f"{cid}({label}): 상품 0건 — 셀렉터가 깨졌을 수 있다")

            for card in cards:
                txt = card.css_first(".txtArea")
                # 국문명은 .txtArea 의 직계 텍스트, 영문명은 그 안의 .sTxt 다.
                name = _clean(txt.text(deep=False)) if txt else ""
                if not name:
                    continue
                en = txt.css_first(".sTxt")
                img = card.css_first(".thum img")
                src = _abs(host, img.attributes.get("src", "") if img else "")
                dpid = _dpid(card)
                it = Item(
                    brand=BRAND,
                    name=name,
                    name_en=_clean(en.text()) if en else "",
                    image=src,
                    labels=["Best"] if card.css_first(".bestIcon") else [],
                    category=label,
                    uploaded_at=_uploaded_at(src),
                    is_new=bool(card.css_first(".newIcon")),
                    url=f"{host}{VIEW_PATH}?dpid={dpid}" if dpid else "",
                )
                if it.key in seen:            # 같은 상품이 두 탭에 걸쳐 있다
                    continue
                seen.add(it.key)
                items.append(it)
                if it.is_new and dpid:
                    pending.append((it, dpid))

            time.sleep(DELAY)

        for it, dpid in pending[:MAX_DETAILS]:
            it.desc = _desc(c, host, dpid)
            time.sleep(DELAY)

    return items
