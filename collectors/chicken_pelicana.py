"""페리카나.

공정위 등록 가맹점 995개로 치킨 업종 6위다. 이번에 붙이는 치킨 중 가맹점 수가 가장 많다.

pelicana.co.kr 은 Nuxt SPA 라 HTML 에는 상품이 한 건도 없다. 907KB 를 받아도 렌더
텍스트가 500자 남짓이고, 그래서 2026-09-30 조사(`notes/CANDIDATES-CHICKEN.md` §3)는
'수집 불가' 로 판정했다. **그 판정은 틀렸다.** 번들 청크를 까면 공개 JSON API 가
평문으로 들어 있다. `/_nuxt/1fb53df.js` 의 repository 모듈이 이렇다.

    getCategoryList: e.get("/api/goods/category")
    getGoodsList:    e.get("/api/goods/list", {params:{scmNo, cateCd}})
    getNewGoodsList: e.get("/api/goods/list/new")

그리고 같은 번들의 화면 코드가 `"001001"===this.selectedCate ? this.getNewGoods()
: this.getGoodsList()` 라 **신제품 탭은 아예 다른 엔드포인트**임을 알려준다.
쿠키·토큰·리퍼러 없이 열리고 `scmNo=0` 이면 매장 선택도 필요 없다. 브라우저 불필요.

신제품 신호가 셋이고 서로 독립이다. 치킨 브랜드 중 제일 두텁다.
  1. **전용 엔드포인트** `/api/goods/list/new` → `result_data.special[]`, 2026-10-02 실측 4건.
  2. **상품별 아이콘** `goodsIconCd`. 전 53건 분포는 none 41 / best 8 / **new 4** 다.
     그 4건이 1번 엔드포인트의 4건과 **정확히 일치**한다 — 두 신호가 서로를 검증한다.
     `best` 는 인기 상품이지 신제품이 아니다. 섞지 않는다.
  3. 이미지 Last-Modified. 최신 두 날짜(2026-06-18 ×3 · 2026-06-23 ×1)가 위 new 4건과
     정확히 겹친다.
     🔴 **다만 이건 약한 신호다. 2026-10-02 실측 53건 중 37건(70%)이 2023-10-23
     하루에 몰려 있다.** 사이트 이관·일괄 재업로드 자국이고, 그 덩어리 안에서는
     신구를 전혀 못 가린다. 나머지 분포는 2023-10-06 ×4 · 2026-06-18 ×3 ·
     2024-09-09 ×3 … 로 8개 날짜다.
     `rules.untrust_bulk_dates()` 가 이 덩어리를 잡아 37건의 날짜를 지워 준다
     (2026-10-02 실행 확인). 그래도 **여기서 날짜를 지워 보내지는 않는다** —
     덩어리 밖 16건은 진짜 정보이고, 덩어리 판정은 브랜드 전체를 봐야 하는
     일이라 rules 쪽이 정본이다. 어댑터가 흉내내면 규칙이 두 벌이 된다.
     ⚠️ "흩어져 있다" 고만 적어두면 안 된다. 70%가 하루에 몰린 건 '흩어짐' 이
        아니다 — 이 줄을 읽는 다음 사람이 그걸 모르고 신뢰하지 않도록 적는다.

목록은 분류 8개(`신제품 / 오리지널 / 순살치킨 / 다리치킨 / 날개치킨 / 페리윙봉 /
스페셜치킨 / 사이드`)를 전부 돌아 53건을 모은다. 분류 코드를 하드코딩하지 않고
`/api/goods/category` 에서 받아 브랜드가 분류를 늘려도 따라가게 했다.

🔴 **파일명 앞 8자리를 날짜로 쓰지 마라.** `2026061812128300.jpg` 처럼 생겨서 업로드일로
읽고 싶어지고 실제로 최근 것들은 맞는다(2026-06-18·2026-06-23 둘 다 Last-Modified 와 일치).
그런데 **구 상품에서 어긋난다** — 후라이드·양념치킨·반반치킨은 파일명이 `20230414…`
인데 Last-Modified 는 **2023-10-23** 이다(2026-10-02 실측). 파일명은 처음 만든 날이고
헤더는 지금 서버에 있는 파일의 시각이다. 요청 53번을 아끼려다 반년을 틀리게 되므로
**헤더를 쓴다**(BBQ·교촌과 같은 처분). 어디까지나 업로드 시각이지 브랜드가 말해준
출시일이 아니라서 released_at 은 비운다.

⚠️ 이미지 호스트가 다르다. 목록이 주는 `imagePath`+`imageName` 앞에 **`pcdn.pelicana.co.kr`**
를 붙여야 한다. `www` 를 붙이면 404 다.

상품 페이지는 전용 엔드포인트가 `menuLink` 로 완성형 주소를 준다
(`/menu/detail?goodsNo=…`). 목록 쪽은 `goodsNo` 만 주므로 같은 모양으로 조립한다.

가격(`goodsPrice`)·품절(`soldOutFl`)·최소주문수량이 API 에 있지만 Item 에 자리가 없어 버린다.
세트·행사 상품은 이 카탈로그에 없다. 전부 단품이고 할인 표시도 없어 promo 는 전건 False 다.
robots.txt 는 404 다(규칙 없음).
"""
import time
from email.utils import parsedate_to_datetime

from . import base
from .base import Item

BRAND = "페리카나"
SITE = "https://www.pelicana.co.kr"
API = SITE + "/api/goods"
IMG = "https://pcdn.pelicana.co.kr"   # www 는 이미지에 404 를 준다

MAX_CATEGORIES = 30  # 폭주 방지. 현재 8개.
MAX_ITEMS = 300      # 폭주 방지. 현재 53건.
DELAY = 0.4          # 목록 요청 간격(초)
IMG_DELAY = 0.15     # 이미지 HEAD 간격(초)


def _data(client, path: str, **params):
    r = base.retry(lambda: client.get(f"{API}{path}", params=params or None))
    r.raise_for_status()
    return r.json().get("result_data")


def _image(g: dict) -> str:
    path, name = g.get("imagePath") or "", g.get("imageName") or ""
    return f"{IMG}{path}{name}" if name else ""


def _uploaded_at(client, img_url: str) -> str:
    """이미지의 Last-Modified 를 날짜로. 실패하면 조용히 비운다."""
    if not img_url:
        return ""
    try:
        lm = client.head(img_url).headers.get("last-modified", "")
        return parsedate_to_datetime(lm).date().isoformat() if lm else ""
    except Exception:
        return ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        # 먼저 신제품 전용 엔드포인트. 이름을 걷어뒀다가 목록에 대조한다
        # (교촌 new_names 와 같은 구조). 아이콘과 교차검증하는 게 목적이다.
        special = _data(c, "/list/new") or {}
        new_names = {" ".join((s.get("title") or "").split())
                     for s in (special.get("special") or [])}
        new_names.discard("")
        # 비어 있으면 엔드포인트가 바뀐 것이다. 건수는 53 그대로라 collect.py 의
        # 0건 가드도 급감 가드도 안 걸리고 "페리카나는 신제품이 없다"가 조용히 굳는다.
        if not new_names:
            raise RuntimeError("신제품 엔드포인트가 비었다 — API 가 바뀌었을 가능성")

        cats = _data(c, "/category") or []
        if not cats:
            raise RuntimeError("분류 목록이 비었다 — API 가 바뀌었을 가능성")

        for cat in cats[:MAX_CATEGORIES]:
            time.sleep(DELAY)
            goods = _data(c, "/list", scmNo=0, cateCd=cat["cateCd"]) or []
            for g in goods:
                name = " ".join((g.get("goodsNm") or "").split())
                if not name:
                    continue
                icon = (g.get("goodsIconCd") or "").lower()
                labels = []
                if icon == "new":
                    labels.append("NEW")
                elif icon == "best":
                    labels.append("BEST")

                it = Item(
                    brand=BRAND,
                    name=name,
                    name_en="",
                    desc=" ".join((g.get("goodsDescriptionMobile") or "").split()),
                    image=_image(g),
                    labels=labels,
                    category=cat.get("cateNm", ""),
                    # 아이콘과 전용 엔드포인트 둘 중 하나라도 신제품이라면 신제품이다.
                    # 둘이 어긋나는 날을 대비해 OR 로 둔다. 아닌 것은 False 가 아니라
                    # None 이다 — 아이콘이 없다는 게 오래됐다는 증거는 못 된다.
                    is_new=True if (icon == "new" or name in new_names) else None,
                    # 할인·행사 표시가 없는 카탈로그다. 세트는 promo 가 아니다
                    # (rules.drop_sets() 가 이름으로 거른다).
                    promo=False,
                    url=(f"{SITE}/menu/detail?goodsNo={g['goodsNo']}"
                         if g.get("goodsNo") else ""),
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
                if len(items) >= MAX_ITEMS:
                    break

        if not items:
            raise RuntimeError("상품 목록이 비었다 — API 가 바뀌었을 가능성")

        for it in items:
            time.sleep(IMG_DELAY)
            it.uploaded_at = _uploaded_at(c, it.image)

    # 🔴 '건수는 멀쩡한데 날짜만 사라진' 상태를 막는다. 이미지 호스트가
    # Last-Modified 를 끊거나 경로가 바뀌면 HEAD 가 전건 조용히 실패하는데,
    # 건수는 그대로라 collect.py 의 0건 가드도 FLOOR 도 통과한다. BBQ 의
    # _head_guard·가마치통닭·노랑통닭과 같은 처분이다(실측 53/53 이 날짜를 받는다).
    dated = sum(1 for it in items if it.uploaded_at)
    if dated * 2 < len(items):
        raise RuntimeError(
            f"페리카나 업로드일 {len(items)}건 중 {dated}건만 붙었다 — 이미지 "
            f"Last-Modified 가 끊겼거나 경로가 바뀌었을 가능성")
    return items
