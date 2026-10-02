"""큰맘할매순대국.

가맹점 336개로 공정위 `한식` 업종 11위다(2025년도 정보공개서, 2024년 말 기준).

`/html/menu.html` 한 장이 전체 메뉴를 SSR 로 담고 있다. 쿠키·세션·JS 불필요.
탭이 7개(신메뉴·순대국·요리류·순대류·세트메뉴·철판볶음·전골)이고 전부 같은
HTML 안에 `div.tab-panel` 로 들어 있다. **1요청에 카드 30장**(중복 제거 25건).
⚠️ 2026-10-02 재실측으로 24 → 25 로 고쳤다. 전에 적혀 있던 24건은 틀린 수였다.

신제품 신호가 둘이고 서로 맞물린다. 2026-10-02 실측:
  is_new  카드 썸네일 위에 배지 이미지가 붙는다(`alt="new"`/`"best"`/`"tip"`/`"season"`).
          `new` 배지가 카드 30장 중 10장, 중복을 턴 25건 중 **5건**에 붙어 있다
          (초계 찰면·누룽지 녹두 삼계탕·부추 백순대 철판볶음·통마늘 양념
           순대 철판볶음·부추고기순대).
  교차검증 `#tab-new`('신메뉴' 탭)에 실린 5건이 **new 배지 5건과 정확히 같은 집합**이다.
          세븐일레븐 '신상품' 탭처럼 분류만 다르고 목록은 같은 가짜가 아니다 —
          나머지 6개 탭 25장 중 new 배지는 신메뉴 상품이 겹쳐 실린 5장뿐이고,
          순대국·세트메뉴·전골 쪽 고정 메뉴에는 하나도 붙어 있지 않다.
  그래서 배지를 **True 로도 False 로도** 쓴다. 한 페이지가 전체 메뉴를 다 보여주고
  그 안에서 브랜드가 직접 5건만 골라 표시한 것이라, '안 붙은 건 신상이 아니다'로
  읽어도 무리가 없다(에그드랍 category=NEW, 폴바셋 newIcon 과 같은 처분).

  uploaded_at  **이미지의 Last-Modified 헤더**로 채운다. 카드 25건 전부 HEAD 가
          200 과 Last-Modified 를 돌려준다.
          ⚠️ **다만 이 값은 신상 5건에만 쓸모가 있다.** 고정 메뉴 20건 중 19건이
          `2025-12-22` 한 날짜에 몰려 있다(나머지 1건은 12-24). 사이트를 새로
          만들 때 이미지를 통째로 올린 흔적이지 그 메뉴가 그때 나왔다는 뜻이
          아니다. 반면 new 배지 5건은 2026-03-31(3건)·2026-06-17(2건)로
          따로 떨어져 있어 그 뒤에 추가된 게 맞다.
          즉 "최근 날짜는 믿을 만하고, 2025-12-22 는 사이트 구축일"로 읽어야 한다.
          두 종류의 경로를 쓰는데 서로 어긋나지 않는 걸 확인했다:
            `/updata/menu/menu_20260617191514_2330.png` — 파일명에 업로드 시각이
              박혀 있고, Last-Modified 가 `Wed, 17 Jun 2026 10:15:14 GMT`
              (= KST 19:15:14) 로 **초 단위까지 일치**한다.
            `/image/sub/menu/mu-img23.png` — 파일명에 날짜가 없는 사이트 고정
              이미지. Last-Modified 만 있다(부추고기순대 = 2026-03-31,
              순대국 = 2025-12-22).
          **released_at 에는 넣지 않는다.** 브랜드가 "출시일"이라고 말한 값이
          아니라 파일을 올린 시각이고, 사이트를 손볼 때 갱신될 수 있다
          (본아이에프 cmdtListImg·한솥 imagePath 와 같은 처분).

released_at 은 **못 채운다.** 페이지에 출시일·등록일 항목이 없고, 상품 상세
페이지 자체가 없다(카드에 링크가 걸려 있지 않다). 지어내지 않고 비운다.
같은 이유로 Item.url 도 비워 `base.site()` 의 메뉴 페이지로 떨어뜨린다.

`세트메뉴` 탭은 단품의 세트 구성이라 분류명으로만 남기고 promo 로 찍지 않는다
(세트 거르기는 `collect.drop_sets()` 담당이다 — 이삭토스트 선례).

가격은 사이트 어디에도 없다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "큰맘할매순대국"
HOST = "https://www.keunmam.co.kr"
URL = HOST + "/html/menu.html"
DELAY = 0.6          # 이미지 HEAD 간격(초)
MAX_HEADS = 60       # 폭주 방지. 현재 25건.

# 탭 id → 화면에 쓰는 분류명. '신메뉴' 는 판매채널이라 분류로 쓰지 않는다.
NEW_TAB = "tab-new"
TABS = {
    "tab-soondaesoup": "순대국",
    "tab-dishes":      "요리류",
    "tab-soondae":     "순대류",
    "tab-setmenu":     "세트메뉴",
    "tab-teppan":      "철판볶음",
    "tab-jeongol":     "전골",
}

_LM = re.compile(r"^[A-Za-z]{3}, (\d{2}) ([A-Za-z]{3}) (\d{4})")
_MON = {m: i for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _abs(src: str) -> str:
    if not src:
        return ""
    if src.startswith("http"):
        return src
    return HOST + "/" + src.lstrip("./")


def _uploaded_at(c, img: str) -> str:
    """이미지 Last-Modified 를 날짜로. 못 읽으면 조용히 비운다(날짜는 지어내지 않는다).

    GMT 로 오지만 KST 로 돌리지 않는다. 날짜만 쓰는데 한 칸 틀릴 수 있는 건
    GMT 15:00 이후에 올린 파일뿐이고, 그걸 맞추자고 시간대 변환을 넣으면
    서버가 Last-Modified 를 어느 시간대로 내보내는지에 대한 가정이 하나 더 는다.
    """
    if not img:
        return ""
    try:
        r = c.head(img)
    except Exception:
        return ""
    m = _LM.match(r.headers.get("last-modified", "") or "")
    if not m or m.group(2) not in _MON:
        return ""
    return f"{m.group(3)}-{_MON[m.group(2)]:02d}-{int(m.group(1)):02d}"


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(URL))
        r.raise_for_status()
    t = HTMLParser(r.text)

    panes = t.css("div.tab-panel")
    if not panes:
        raise RuntimeError("큰맘할매순대국: 탭 패널 0개 — 셀렉터가 깨졌을 수 있다")

    by_key: dict = {}
    items: list[Item] = []
    for pane in panes:
        pid = pane.attributes.get("id") or ""
        cards = pane.css("article.menu-card")
        if pid == NEW_TAB and not cards:
            raise RuntimeError("큰맘할매순대국 신메뉴 탭: 상품 0건 — 구조가 바뀌었다")
        # 아는 탭이 비면 그것도 드러낸다. 전체 0건 가드만 두면 한 탭이 통째로
        # 빠져도 조용히 지나간다 — 실측으로 순대국 탭 하나를 비웠더니 25 → 21건
        # 으로 예외 없이 끝났고, 감소폭이 16%라 collect.FLOOR(30%)에도 안 걸린다.
        # 다른 탭들이 전부 같은 `article.menu-card` 를 쓰니 한 탭만 0인 건
        # 구조 변경이지 정상이 아니다(하루엔소쿠·홍익돈까스·유가네와 같은 선).
        if pid in TABS and not cards:
            raise RuntimeError(
                f"큰맘할매순대국 {TABS[pid]}({pid}): 상품 0건 — 구조가 바뀌었다")

        for card in cards:
            h3 = card.css_first("h3")
            name = _clean(h3.text()) if h3 else ""
            if not name:
                continue
            badges = [i.attributes.get("alt", "").strip()
                      for i in card.css(".menu-thumb span img")]
            thumb = card.css_first(".menu-thumb > img")
            image = _abs(thumb.attributes.get("src", "")) if thumb else ""

            key = base.make_key(BRAND, name)
            if key in by_key:
                # 신메뉴 탭과 본래 분류에 같은 상품이 겹쳐 실린다.
                # 신상 여부는 살리고, 분류명은 신메뉴가 아닌 쪽에서 채운다.
                it = by_key[key]
                it.is_new = it.is_new or ("new" in badges)
                if not it.category and pid != NEW_TAB:
                    it.category = TABS.get(pid, "")
                continue

            it = Item(
                brand=BRAND,
                name=name,
                desc=_clean(card.css_first(".menu-body p").text())
                     if card.css_first(".menu-body p") else "",
                image=image,
                # best·tip·season 은 화면에 보여줄 값이다. new 는 is_new 로 가므로 뺀다.
                labels=[b for b in badges if b and b != "new"],
                category="" if pid == NEW_TAB else TABS.get(pid, ""),
                is_new="new" in badges,
            )
            by_key[key] = it
            items.append(it)

    # 날짜는 이미지 헤더에만 있다. 카드 수만큼 HEAD 를 친다(현재 25회).
    with base.client() as c:
        for it in items[:MAX_HEADS]:
            it.uploaded_at = _uploaded_at(c, it.image)
            time.sleep(DELAY)

    return items
