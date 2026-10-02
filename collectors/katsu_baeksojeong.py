"""백소정 (돈카츠·마제소바). 가맹점 199개 — 돈까스 업종 1위.

사이트는 아임웹(imweb)이고 **가맹 모집용 원페이지**다. 상품 목록 페이지가 따로 없다.
`baeksojeong.com/` 이 `/35` 로 열리고(canonical 도 `/35`), 사이트맵의 14개 주소 중
메뉴 데이터를 들고 있는 건 `/35`·`/home`·`/32` 셋뿐이다. 셋은 같은 페이지의 복사본이고
canonical 이 가리키는 `/35` 만 쓴다. 2026-10-02 실측.

**메뉴는 HTML 마크업이 아니라 인라인 스크립트의 `var menuData = {...}` 객체다.**
아임웹 '코드' 위젯에 통째로 박아 넣었다. jsrender 템플릿(본아이에프)과 달리 API 가
따로 없고, 서버가 그 스크립트를 그대로 내려주므로 브라우저 없이 1요청으로 끝난다.

  new:       { badge: 'NEW',       bgText: 'SUMMER', items: [...] }   3건
  signature: { badge: 'SIGNATURE', bgText: 'Signature', items: [...] } 2건
  best:      { badge: 'BEST',      bgText: 'Best', items: [...] }      5건

신제품 신호:
  is_new  **`new` 가 브랜드가 따로 고른 독립 탭이다.** 에그드랍 `category=NEW` 와
          같은 모양이라 같은 처분을 한다 — `new` 에 담긴 것만 True, 나머지 둘은 False.
          '모름'이 아니라 '아님'으로 보는 근거는 세 탭의 품목이 실제로 갈린다는 것이다.
          new = 마제동·연어 냉소바·연어 자루소바 / signature = 마제소바·키마카레 /
          best = 돈카츠·치즈카츠·마제소바·냉소바·가츠동. 겹치는 건 마제소바
          (signature∩best) 하나뿐이고 new 와 겹치는 건 0건이다.
          세븐일레븐 '신상품' 탭처럼 같은 목록을 다시 불러오는 가짜가 아니다.
  uploaded_at  **이미지 Last-Modified 헤더.** 교차검증이 여기서 한 번 더 붙는다 —
          new 3건은 전부 `2026-06-18`, signature·best 7건은 전부 `2026-01-09` 다.
          탭 구분과 업로드 시점이 독립적으로 일치한다. `bgText: 'SUMMER'` 가 여름
          한정이라고 말하는 것과도 맞는다.
          ⚠️ 그래서 지금(2026-10-02) 기준으로 NEW 3건은 이미 3개월 반쯤 묵었다.
          낡은 배지는 collect 쪽에서 날짜와 대조해 걸러진다(이삭토스트 선례).
  released_at  **없다.** 브랜드가 말하는 출시일 필드가 어디에도 없다.
          이미지 업로드일을 released_at 으로 승격하지 않는다(본아이에프 선례).

이미지 HEAD 는 상품당 1회, 전부 합쳐 10회다. 목록 1 + HEAD 10 = 11요청.
헤더가 없거나 요청이 실패하면 **그 상품만** uploaded_at 을 비운다 — 날짜를 지어내느니
비우는 쪽이다. 목록 자체가 깨지면 RuntimeError 로 드러낸다.

이미지는 `cdn.imweb.me/upload/S2025010718822c5ee116f/…` 로 사이트 업로드 원본이다.
`/thumbnail/YYYYMMDD/` 경로가 아니라서 **경로에서는 날짜가 안 나온다**(미소야와 다른 점).
그 썸네일 경로를 쓰는 건 로고·파비콘뿐이고, 로고는 재생성 때마다 날짜가 바뀐다 —
쑝쑝돈까스에서 그 날짜를 상품 신호로 착각한 전례가 있으니 쓰지 마라.

가격은 사이트 어디에도 없다. 상품 상세 페이지도 없어서 Item.url 은 SITES 폴백으로
떨어진다(앵커 `#s…` 로 메뉴 섹션까지는 보낼 수 있지만 아임웹 섹션 id 는 편집하면
바뀌는 값이라 쓰지 않는다).

robots.txt: `Allow: /` + `/site_join`·`/login`·`/logout.cm`·`/shop_cart`·`/?mode*`·
`/admin` 만 Disallow. 같은 블록이 두 번 중복돼 있다(아임웹 기본값 위에 손으로 덧붙인 모양).
우리가 받는 `/35` 와 cdn 이미지는 전부 허용 범위다.
이용약관: `/?mode=policy` 인데 **robots 가 `/?mode*` 를 막아서 확인하지 못했다**
(미소야·쑝쑝돈까스와 같은 상황). 금지 조항이 없다는 뜻이 아니라 못 봤다는 뜻이다.
"""
import re
import time

from . import base
from .base import Item

BRAND = "백소정"
URL = "https://baeksojeong.com/35"      # canonical. '/' 도 같은 페이지를 준다
DELAY = 1.5          # 요청 간격(초)

# `new: { badge: 'NEW', …` 처럼 카테고리 머리를 연다. 키와 배지를 같이 집는다.
_CAT = re.compile(r"(\w+)\s*:\s*\{\s*badge\s*:\s*'([^']*)'")

# 항목 하나. 네 필드가 항상 이 순서로 붙어 있다(10건 전부 확인).
_ITEM = re.compile(
    r"name\s*:\s*'([^']*)'\s*,\s*"
    r"nameEn\s*:\s*'([^']*)'\s*,\s*"
    r"desc\s*:\s*'([^']*)'\s*,\s*"
    r"image\s*:\s*'([^']*)'", re.S)

# Last-Modified: Thu, 18 Jun 2026 08:31:04 GMT
_MONTHS = {m: i for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}
_LM = re.compile(r"\w{3},\s*(\d{1,2})\s+(\w{3})\s+(\d{4})")

# 브랜드가 신제품이라고 고른 탭. 나머지 탭은 '신제품 아님'으로 본다.
NEW_KEY = "new"


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _menu_data(html: str) -> str:
    """인라인 스크립트의 `var menuData = { … };` 블록만 떼어낸다."""
    i = html.find("var menuData")
    if i < 0:
        raise RuntimeError("백소정: menuData 블록이 없다 — 사이트 구조가 바뀌었다")
    j = html.find("};", i)
    if j < 0:
        raise RuntimeError("백소정: menuData 블록이 닫히지 않았다")
    return html[i:j + 2]


def _uploaded_at(c, url: str) -> str:
    """이미지 Last-Modified 를 날짜로. 못 받으면 비운다 — 지어내지 않는다."""
    if not url:
        return ""
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
    seen = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(URL))
        r.raise_for_status()
        blk = _menu_data(r.text)

        # 카테고리 머리의 위치로 블록을 잘라, 각 항목이 어느 탭 소속인지 가린다.
        heads = [(m.start(), m.group(1), m.group(2)) for m in _CAT.finditer(blk)]
        if not heads:
            raise RuntimeError("백소정: menuData 안에 카테고리가 0개다")
        if not any(k == NEW_KEY for _, k, _ in heads):
            # 브랜드가 신메뉴 탭을 없앴다면 조용히 '전부 신상 아님'이 되는 게 아니라
            # 드러나야 한다. 이 어댑터의 신호가 통째로 그 탭 하나에 걸려 있다.
            raise RuntimeError(f"백소정: '{NEW_KEY}' 탭이 사라졌다 — 신상 신호 없음")

        bounds = [(s, heads[i + 1][0] if i + 1 < len(heads) else len(blk), k, b)
                  for i, (s, k, b) in enumerate(heads)]

        for start, end, key, badge in bounds:
            for m in _ITEM.finditer(blk[start:end]):
                name = _clean(m.group(1))
                if not name:
                    continue
                it = Item(
                    brand=BRAND,
                    name=name,
                    name_en=_clean(m.group(2)),
                    desc=_clean(m.group(3)),
                    image=m.group(4).strip(),
                    # 배지는 NEW 를 중복으로 찍지 않게 base.shown_labels 가 턴다.
                    labels=[badge] if badge else [],
                    is_new=(key == NEW_KEY),
                )
                # 마제소바가 signature 와 best 양쪽에 있다. 먼저 만난 쪽을 남긴다
                # (new 가 맨 앞이라 신제품 판정이 뒤집히는 일은 없다).
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)

        if not items:
            raise RuntimeError("백소정: 상품 0건 — menuData 형식이 바뀌었다")

        for it in items:
            it.uploaded_at = _uploaded_at(c, it.image)
            time.sleep(DELAY)

    return items
