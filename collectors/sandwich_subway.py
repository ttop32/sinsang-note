"""써브웨이.

🔴 이용약관 제5조 제2항 (b)가 수집·재배포를 정면으로 막는다. 2026-09-30 실측
(`www.subway.co.kr/agreement`):

    5.2 제한 — 이용자는 사이트에서 다음의 행위를 하거나, 제3자가 다음 행위를
    하도록 허가할 수 없습니다. …
    (b) 회사의 자료를 어떠한 방식으로든 복사, 복제, 재발행, 업로드, 게시,
        전송, 재판매 또는 배포하는 행위

이마트24 제8조 ⑧(크롤러·매크로 같은 *수단* 금지)보다 넓다. 수단을 가리지 않고
복제·재게시 자체를 막으므로, 메뉴를 복제해 다시 싣는 이 서비스는 정면으로 걸린다.
문구가 한국 프랜차이즈 약관 톤이 아니라 미국 본사 약관 번역체다.
운영자 방침("robots 는 열려 있고 약관만 금지면 수집하되 기록")에 따라 붙이되,
이 브랜드가 이 레포에서 약관 저촉이 가장 뚜렷한 곳임을 여기 남겨 둔다.
삭제 요청이 오면 다투지 말고 즉시 내린다.
robots.txt 는 404(JSON 본문)라 경로 제한은 없다 — 다만 404 는 허용 근거가 아니라
'파일이 없다'일 뿐이고, 여기서 막는 건 robots 가 아니라 약관이다.

목록은 `/menuList/<카테고리>` 가 전부다. SSR 이고 브라우저 불필요.
2026-09-30 실측 건수: sandwich 33 / salad 20 / grain_salad 19 / sidedrink 15 /
catering 6 / morning 4 / unit 3 / wrap 0 / sides 0 — 원본 100건, 카테고리 간
중복(토핑·음료가 여러 탭에 겹친다)을 key 로 합쳐 81건이다.
`wrap` 과 `sides` 는 200 을 주지만 상품이 0건이다. 랩 상품은 `unit` 으로 옮겨
있다(그쪽 li 의 class 가 `ITEM_WRAP.*` 다). 비어 있어도 에러로 보지 않고,
전 카테고리 합계가 0일 때만 셀렉터 파손으로 본다.

신제품 신호가 세 겹이다.
  is_new  ① 필터 탭 이름이 그대로 '신제품'이고 ② 상품 li 의 class 가
          `ITEM_<카테고리>.NEW` 이며 ③ `.label span.new` 에 NEW 배지가 붙는다.
          ②와 ③이 항상 같지는 않다 — 2026-09-30 sandwich 에서 class 는 4건,
          배지는 5건이고 '잠봉'은 class 가 CLASSIC 인데 NEW 배지가 붙어 있다.
          둘 중 하나라도 있으면 True 로 본다(합집합). 조사 문서는 "class 4 / 배지 5"
          라고만 적었는데 둘의 대상이 어긋난다는 건 적히지 않았다.
          브랜드가 골라 붙이는 표시라 없으면 False 를 준다.
  released_at  비운다. 페이지에 날짜 필드가 없다.
  uploaded_at  이미지 파일명에서만 뽑는다. 두 형식이 섞여 있다 —
          최근 것은 13자리 epoch ms(`1785741671083_TyCRBr.png`),
          예전 것은 `이름_20211231095455613.png` 다.
          **released_at 에는 넣지 않는다.** 날짜가 몇 개 날에 뭉쳐 있다 —
          81건 중 2021-03-15 에 17건, 2021-12-31 에 11건, 2026-05-31 에 11건
          (리뉴얼 때 일괄 재업로드 흔적). 메가에서 173건 중 81건이 한 달에
          몰렸던 것과 같은 사고라 출시일로 쓰면 그대로 오보다.
          7건은 파일명에 시각이 없어(`img_toppping_01.png` 류) 비어 있다.

url 은 채운다. 카드의 `menuDetail()` 이 `/js/menu/menuList.js` 에서
`/menuView/<data-category>?menuItemIdx=<data-menuitemidx>` 로 이동한다(실측,
`/menuView/sandwich?menuItemIdx=1613` 200 확인). 토핑·케이터링 17건은
`data-menuitemidx` 가 아예 없어 상세가 존재하지 않는다 — 그건 비워 둔다.

labels 에는 NEW 를 뺀 나머지 배지(SUBPICK)를 담는다.
promo 는 쓰지 않는다. SUBPICK 은 할인·행사가 아니라 브랜드 추천 표시다.
칼로리는 마크업이 주석 처리돼 있어 오지 않는다. 가격도 목록에 없다.
"""
import re
import time
from datetime import datetime, timezone

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "써브웨이"
HOST = "https://www.subway.co.kr"
LIST_PATH = "/menuList/{cat}"
VIEW_PATH = "/menuView/{cat}?menuItemIdx={idx}"
DELAY = 2.0

# 경로 ↔ 화면에 쓸 분류명. wrap·sides 는 현재 비어 있지만, 브랜드가 다시 채울 수
# 있으니 목록에는 남겨 둔다(비면 조용히 넘어간다).
CATEGORIES = [
    ("sandwich", "샌드위치"),
    ("salad", "샐러드"),
    ("grain_salad", "그레인 샐러드"),
    ("wrap", "랩"),
    ("unit", "랩·미니"),
    ("morning", "모닝"),
    ("sidedrink", "사이드·음료"),
    ("sides", "사이드"),
    ("catering", "케이터링"),
]

_EPOCH_MS = re.compile(r"/(\d{13})_")          # 1785741671083_TyCRBr.png
_YMD = re.compile(r"_(\d{4})(\d{2})(\d{2})\d{9}\.")   # …_20211231095455613.png


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _abs(src: str) -> str:
    if not src:
        return ""
    return src if src.startswith("http") else HOST + src


def _uploaded_at(src: str) -> str:
    """이미지 파일명의 업로드 시각. 두 형식이 섞여 있다. 출시일이 아니다."""
    m = _EPOCH_MS.search(src)
    if m:
        return datetime.fromtimestamp(int(m.group(1)) / 1000, timezone.utc).strftime("%Y-%m-%d")
    m = _YMD.search(src)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        for cat, label in CATEGORIES:
            r = base.retry(lambda: c.get(HOST + LIST_PATH.format(cat=cat)))
            r.raise_for_status()
            cards = HTMLParser(r.text).css("li[data-menusubsort]")

            for li in cards:
                tit = li.css_first(".tit")
                name = _clean(tit.text()) if tit else ""
                if not name:
                    continue
                eng = li.css_first(".eng")
                summary = li.css_first(".summary p")
                img = li.css_first(".img img")
                src = _abs(img.attributes.get("src", "") if img else "")
                badges = [_clean(s.text()) for s in li.css(".label span")]
                cls = li.attributes.get("class", "") or ""
                view = li.css_first("a.btn_view")
                idx = view.attributes.get("data-menuitemidx", "") if view else ""
                vcat = (view.attributes.get("data-category", "") if view else "") or cat

                it = Item(
                    brand=BRAND,
                    name=name,
                    name_en=_clean(eng.text()) if eng else "",
                    desc=_clean(summary.text()) if summary else "",
                    image=src,
                    labels=[b for b in badges if b and b != "NEW"],
                    category=label,
                    uploaded_at=_uploaded_at(src),
                    is_new=(cls.endswith(".NEW") or "NEW" in badges),
                    url=HOST + VIEW_PATH.format(cat=vcat, idx=idx) if idx else "",
                )
                if it.key in seen:      # 같은 상품이 두 카테고리에 걸쳐 있다
                    continue
                seen.add(it.key)
                items.append(it)

            time.sleep(DELAY)

    # 개별 카테고리는 비어 있을 수 있다(wrap·sides). 전부 비면 셀렉터가 깨진 것이다.
    if not items:
        raise RuntimeError("써브웨이: 전 카테고리 상품 0건 — 셀렉터가 깨졌을 수 있다")
    return items
