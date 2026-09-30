"""설빙.

/menu/?type=설빙|사이드|음료 세 탭이 전부다. 쿠키·세션 없이 SSR 로 상품이 다 들어있고
페이징도 없어서 요청 3번이면 끝난다. 브라우저 불필요.

호스트가 함정이다. www.sulbing.com 은 TLS 핸드셰이크에서 연결이 끊기고(2026-09-30
실측, 같은 IP 인데도 apex 만 인증서를 내놓는다) apex sulbing.com 만 응답한다.
지금 죽은 www 가 살아날 수도 있고 반대가 될 수도 있어 스타벅스처럼 후보를 순회한다.

신제품 신호:
  is_new  목록 카드의 <span class="flag"><img src="/new/images/icon_new.png"> 가 NEW 배지다.
          96건 중 14건에만 붙어 있고 나머지 82건엔 flag 요소 자체가 없다. 브랜드가
          배지를 선별해서 달고 있다는 뜻이라, 없으면 '신제품 아님'이 확인된 것으로 보고
          False 를 준다.
  날짜    어디에도 없다. menu=166 같은 상세 링크의 번호는 등록 순번으로 보이지만
          날짜가 아니고 기준 시점도 알 수 없어 released_at/uploaded_at 둘 다 비워둔다.
          이미지 파일명도 product_small_ubriiie.png 처럼 난수라 단서가 없다.

설명(desc)·영양정보·알레르기는 menu_view.php?menu=N 상세에만 있다. 상세 한 장은
그 탭의 상품 하나치 텍스트만 담고 있어서(나머지는 클릭 시 재요청) 96건이면 96요청이다.
3요청으로 끝나는 목록에 96요청을 더할 값이 아니라 desc 는 비워둔다.
"""
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "설빙"
HOSTS = ("https://sulbing.com", "https://www.sulbing.com")
PATH = "/menu/"
# 탭 이름이 그대로 쿼리값이다(한글). 늘어나도 여기만 고치면 된다.
TYPES = ("설빙", "사이드", "음료")
DELAY = 0.8          # 요청 간격(초)


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _abs(host: str, src: str) -> str:
    if not src:
        return ""
    return src if src.startswith("http") else host + src


def _live_host(c) -> str:
    """상품 목록을 실제로 돌려주는 호스트를 고른다. 전부 죽었으면 마지막 오류를 올린다.

    상태코드만으로는 판정하지 않는다. 죽은 쪽이 파킹 페이지를 200 으로 주는 사고가
    스타벅스에서 이미 있었다. 목록 요소가 파싱되는지까지 확인한다.
    """
    last = None
    for h in HOSTS:
        try:
            r = c.get(h + PATH, params={"type": TYPES[0]})
            r.raise_for_status()
            if not HTMLParser(r.text).css("ul.menuList > li"):
                raise RuntimeError("목록 요소 없음")
            return h
        except Exception as e:                       # 연결 실패·TLS·HTTP·빈 목록 전부
            last = f"{h} → {type(e).__name__}"
    raise RuntimeError(f"설빙 호스트 전부 사용 불가 ({last})") from None


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        host = _live_host(c)
        for tp in TYPES:
            r = base.retry(lambda: c.get(host + PATH, params={"type": tp}))
            r.raise_for_status()
            cards = HTMLParser(r.text).css("ul.menuList > li")
            # 탭이 통째로 비면 조용한 부분수집이 된다. 예외로 올려 드러낸다.
            if not cards:
                raise RuntimeError(f"{tp} 탭에서 상품 0건 — 셀렉터가 깨졌을 수 있다")

            for card in cards:
                name = _clean(card.css_first(".txt").text()) if card.css_first(".txt") else ""
                if not name:
                    continue
                img = card.css_first(".img img")
                it = Item(
                    brand=BRAND,
                    name=name,
                    image=_abs(host, img.attributes.get("src", "") if img else ""),
                    category=tp,
                    is_new=bool(card.css_first("span.flag")),
                )
                if it.key not in seen:
                    seen.add(it.key)
                    items.append(it)

            time.sleep(DELAY)
    return items
