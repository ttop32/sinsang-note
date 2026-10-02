"""블루샥(Blu Shaak).

www.blushaak.co.kr 은 Next.js **App Router** 사이트다. `/menu` 를 그냥 받으면
HTML 12KB 에 상품이 한 건도 없다(한글 문자열이 브랜드 슬로건 10개뿐). `RSC: 1`
헤더로 플라이트 페이로드를 받아봐도 7.6KB 에 역시 상품이 없다. 내부 API 도 없다 —
`_next/static/chunks/*.js` 13개(합계 780KB)를 전부 받아 `http(s)://` 호스트와
`/api` 경로를 훑었는데 **단 한 건도 안 나왔다.**

메뉴가 **JS 번들 안에 통째로 하드코딩**돼 있다. 청크 하나에 `"MENU_ITEMS"` 라는
이름과 함께 객체 배열이 들어 있고, 항목이 이렇게 생겼다.

    {id:"dolce-latte",name:"Dolce Latte",nameKo:"돌체 라떼",category:"coffee",
     image:"/images/menu/dolce-latte.jpg",nutrition:{calories:252.2,…}}

그래서 이 어댑터는 `/menu` 를 받아 거기 걸린 청크 주소를 모으고, 그중
`MENU_ITEMS` 가 든 청크를 찾아 정규식으로 항목을 뽑는다. **청크 파일명 해시는
배포할 때마다 바뀌므로 주소를 박아두면 안 된다.** 요청은 많아야 15회쯤이다.

신제품 신호(2026-10-02 실측):
  - 카테고리가 8개인데 그중 하나가 **`new`(신메뉴)** 다. 거기 속한 6건에만
    `isNew:!0` 이 같이 붙어 있다. 두 표시가 **완전히 일치**한다 —
    category=="new" 6건, isNew 6건, 교집합 6건.
  - 전체 139건 중 6건이면 4.3% 다. 버거킹(31%)처럼 아무 데나 붙은 배지가 아니고,
    이름·파일명도 전부 `new-` 로 시작해 브랜드가 실제로 분리해 둔 묶음이다
    (A2우유 딥 라떼, 레드빈/망고 컵빙수, 프응 야생화 꿀 토마토·참외 주스·말차 레몬 티).
  - `isNew` 가 없는 나머지는 브랜드가 신제품이 아니라고 말한 것이므로
    is_new=False 로 내보낸다(모름이 아니다).

**날짜는 없다.** 번들 어디에도 출시일·등록일 문자열이 없다.
이미지 Last-Modified 는 쓰지 않는다 — `/images/` 아래 정적 파일이라 배포할 때마다
전건이 같이 갱신된다(실측: 신메뉴 이미지가 2026-09-29 22:28, 사이트 배포 시각이다).
컴포즈커피에서 Last-Modified 149건이 한 날에 몰려 가짜로 판명된 것과 같은 함정이다.
그래서 released_at·uploaded_at 은 **비운다.** 날짜 없이 is_new 만 들고 간다.

MD 카테고리(12건)는 굿즈라 `nonfood=True` 로 표시한다.
상품 상세 주소가 없어 Item.url 은 비우고 SITES 폴백(/menu)에 맡긴다.
"""
import re
import time

from . import base
from .base import Item

BRAND = "블루샥"
SITE = "https://www.blushaak.co.kr"
MENU_URL = f"{SITE}/menu"
# 메뉴 배열이 든 청크를 고르는 기준.
# ⚠️ '어떤 문자열이 들어 있는 첫 청크' 로 고르면 **틀린 청크**를 잡는다. 두 번 겪었다 —
#   `MENU_ITEMS` 는 배열을 쓰는 화면 컴포넌트 청크(`p.MENU_ITEMS.filter(…)`)에도 있고,
#   `nameKo:"` 는 브랜드 정보 청크(`BRAND` 객체)에도 한 번 나온다. 둘 다 먼저 걸려서 0건.
# 그래서 **항목 정규식이 가장 많이 걸리는 청크**를 고른다. 임계값을 넘으면 거기서 멈춘다.
ENOUGH = 50
NEW_CATEGORY = "new"
MD_CATEGORY = "md"
MAX_CHUNKS = 30              # 폭주 방지. 현재 13개.
DELAY = 2.0

# `src="/_next/static/chunks/xxx.js"` 와 preload link 를 둘 다 모은다.
_CHUNK = re.compile(r'(?:src|href)="(/_next/[^"]+\.js)"')

# 번들 안의 객체 리터럴. 키가 따옴표 없이 오고 불리언이 `!0` 이라 JSON 으로 못 읽는다.
# 항목마다 뒤에 붙는 nutrition 이 `null` 이거나 중첩 객체라 길이가 제각각이다.
# 한 정규식에 다 넣으려다 0건이 나왔다 — 앞쪽 다섯 필드만 고정으로 잡고,
# isNew 는 **다음 항목이 시작되기 전까지의 꼬리**에서 따로 찾는다.
_ITEM = re.compile(
    r'id:"([a-z0-9\-]+)",name:"([^"]*)",nameKo:"([^"]*)",'
    r'category:"([a-z\-]+)",image:"([^"]*)"')
_IS_NEW = "isNew:!0"

# 카테고리 코드 → 화면에 쓸 이름. 번들의 labelKo 와 같은 값이다.
CATEGORIES = {
    "new": "신메뉴", "coffee": "커피", "beverage": "베버리지",
    "blended": "블렌디드", "bakery": "베이커리", "ice-cream": "아이스크림",
    "md": "MD 상품", "deli": "델리",
}


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _bundle(c) -> str:
    """메뉴 배열이 든 청크 본문. 청크 해시가 배포마다 바뀌어 매번 찾아야 한다."""
    r = base.retry(lambda: c.get(MENU_URL))
    r.raise_for_status()
    paths = list(dict.fromkeys(_CHUNK.findall(r.text)))[:MAX_CHUNKS]
    if not paths:
        raise RuntimeError("블루샥 /menu 에서 청크 주소를 못 찾았다 — 빌드가 바뀌었다")
    best, best_n = "", 0
    for p in paths:
        time.sleep(DELAY)
        j = base.retry(lambda: c.get(SITE + p)).text
        n = len(_ITEM.findall(j))
        if n > best_n:
            best, best_n = j, n
        if best_n >= ENOUGH:
            return best
    if not best_n:
        raise RuntimeError(f"블루샥 청크 {len(paths)}개 어디에도 메뉴 항목이 없다 "
                           "— 메뉴가 번들 밖으로 옮겨갔을 수 있다")
    return best


def fetch() -> list[Item]:
    # TLS 체인은 멀쩡하지만 Next 정적 자산이 http 로 새는 일이 있어 base.client 기본값을 쓴다.
    with base.client() as c:
        bundle = _bundle(c)

    items: list[Item] = []
    seen = set()
    hits = list(_ITEM.finditer(bundle))
    for n, m in enumerate(hits):
        pid, name_en, name_ko, cat, image = m.groups()
        # 이 항목의 꼬리(다음 항목 시작 전까지)에서만 isNew 를 본다.
        tail = bundle[m.end():(hits[n + 1].start() if n + 1 < len(hits) else m.end() + 400)]
        is_new = _IS_NEW in tail
        name = _clean(name_ko) or _clean(name_en)
        if not name or pid in seen:
            continue
        seen.add(pid)
        items.append(Item(
            brand=BRAND,
            name=name,
            name_en=_clean(name_en),
            image=SITE + image if image.startswith("/") else image,
            category=CATEGORIES.get(cat, cat),
            # category=="new" 와 isNew 가 전건 일치한다(docstring). 둘 다 본다.
            is_new=is_new or cat == NEW_CATEGORY,
            nonfood=cat == MD_CATEGORY,
        ))

    # 번들 구조가 바뀌면 정규식이 조용히 0건을 뱉는다. 그걸 막는다.
    if len(items) < 50:
        raise RuntimeError(f"블루샥 {len(items)}건 — 번들의 메뉴 배열 모양이 바뀌었다")
    return items
