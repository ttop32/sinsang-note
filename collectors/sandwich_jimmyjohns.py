"""지미존스(Jimmy John's). 2025-12 가맹사업 등록, 가맹본부 (주)역전에프앤씨.

1983년 미국 일리노이에서 시작한 샌드위치 브랜드다. 2024-10 서울 강남에 한국·아시아
1호점을 열었고 공정위에는 2025-12-09 에 '지미존스 샌드위치'로 등록됐다. 그래서
2024년 말 기준 가맹점 수가 없다 — 담당 12곳 중 가장 늦게 들어온 곳이고,
**신제품 신호는 그중 제일 또렷하다.**

구조가 둘로 나뉜다. 2026-10-02 실측.
  GET /homepage/menu.php                  카테고리 9장(라벨 + 대표 상품 id)
  GET /homepage/menu_detail.php?id=JJxxxx 그 카테고리의 상품 전량
둘 다 SSR 이고 쿠키·JS 불필요. 10요청에 전 메뉴가 나온다.
상품은 `li > a` 의 data 속성에 통째로 들어 있어 파싱이 단순하다.

  data-name="스모크 바비큐 풀드포크" data-item-id="JG00160"
  data-description="진한 풍미의 BBQ 풀드포크에 …" data-img="../images/item/JG00160_main.png"
  data-item-kcal="" data-item-comment=""
(kcal·comment 는 전건 빈 값이라 받지 않는다. 가격은 응답 어디에도 없다.)

**신제품 신호가 셋이고 서로를 검증한다.**
  is_new  **`신메뉴` 가 독립 카테고리(JJ0024)다.** 거기 실린 건 4건
          (스모크 바비큐 풀드포크 / 스모크 과카몰리 풀드포크 / 각 세트).
          전 카테고리를 합친 상품 수에 견주면 한 줌이라 퀴즈노스 `new_icon`
          (66건 전건에 붙어 가짜였다) 같은 종류가 아니다.
          🔴 **거기 실린 것만 True 로 올리고, 나머지는 False 가 아니라 None 이다.**
          에그드랍 `category=NEW` 와 다른 처분인데 이유가 있다 — 에그드랍은 그
          칸이 브랜드의 유일한 신메뉴 표시라 '안 담긴 건 신상이 아니다'가 성립하는데,
          **이 브랜드는 새 라인을 전용 카테고리로 만들고 신메뉴 칸에는 안 넣는다**
          (바로 아래 ⚠️ 항목). 그래서 False 로 단정하면 안 된다.
          2026-10-02 실측에서 실제로 사고가 났다: `지미모닝` 8건이 2026-08-26
          업로드(브랜드 공지도 "New 지미모닝 2026.08.27~")인데 신메뉴 칸에
          없다는 이유로 `is_new=False` 가 붙었고, `rules.is_fresh` 가
          "브랜드가 신제품 아니라고 했으면 업로드 시각으로 뒤집지 않는다"는
          규칙에 따라 **8건을 통째로 화면에서 뺐다.** 아래 '두 신호를 둘 다
          내보내고 어느 한쪽으로 다른 쪽을 덮어쓰지 않는다'는 서술과 코드가
          어긋나 있었던 것이다. None 으로 바꿔 uploaded_at 이 살아나게 했다.
  uploaded_at  **이미지 Last-Modified.** 신메뉴 4건은 2026-06-19 이고 다른
          카테고리는 2025-06-26 / 2026-03-11 / 2026-04-21 / 2026-05-18 로 흩어져
          있다. 카테고리 구분과 업로드 시점이 독립적으로 맞는다.
  (검증용) `/homepage/notice.php` 가 **"NEW 신메뉴 풀드포크 시리즈 출시!
          2026.06.25 ~ 2026.09.24"** 를 걸고 있다. 이미지 날짜(6/19)보다 엿새 뒤라
          '사진 올리고 공지 띄웠다'는 순서와 맞는다. 공지는 이 어댑터가 받지
          않는다 — 상품 목록이 아니라 배너라서 상품명을 뽑을 수 없다.
          **다만 그 행사 기간은 2026-09-24 에 끝났는데 신메뉴 칸은 그대로다.**
          배지가 낡는다는 뜻이니 is_new 를 날짜 없이 믿지 마라.

⚠️ **이 브랜드에서는 is_new 보다 uploaded_at 이 더 최신을 가리킨다.** 실측 67건의
날짜를 세어 보면 제일 최근은 신메뉴 칸(2026-06-19)이 아니라 `지미모닝` 8건
(2026-08-26)과 `지미런치` 6건(2026-07-29)이다. 공지도 "New 지미모닝 2026.08.27~"
를 걸고 있다. **새 라인을 전용 카테고리로 만들면 신메뉴 칸에는 안 넣는다**는 뜻이다.
그래서 두 신호를 둘 다 내보내고 어느 한쪽으로 다른 쪽을 덮어쓰지 않는다.
  released_at  **없다.** 브랜드가 말하는 출시일 필드가 응답에 없다. 공지의
          시작일(2026.06.25)을 출시일로 승격할 수도 있겠지만, 그건 행사 시작일이지
          출시일이 아니고 상품별로 붙지도 않는다. 비워 둔다.

`data-item-id`(JG00160 등)는 증가하는 등록 번호로 보인다 — 신메뉴 4건이 160·162·
173·174 로 가장 크고 추천메뉴는 9·15·134·151·154·157 이다. 다만 **순번과 Last-Modified
가 어긋나는 쌍이 있어**(JG00134=2026-03-11 < JG00157=2026-05-18 은 맞지만 JG00009=
2026-04-21 이 JG00015=2025-06-26 보다 늦다) 순번을 날짜 대용으로 쓰지 않는다.
사진을 나중에 갈아끼운 흔적이라 Last-Modified 쪽만 쓴다.

같은 상품이 여러 카테고리에 겹쳐 실린다(신메뉴 4건은 단품·세트에도 있다).
먼저 만난 쪽을 남기되 **is_new 는 올리기만 한다**(신메뉴 칸에서 만났으면 True 로
덮고, 그 밖에서 만난 것은 None 그대로 둔다). `or` 로 합치면 None 이 False 로
깎여 위의 지미모닝 사고가 그대로 되살아난다. 신메뉴 칸을 먼저 돌므로 순서가
바뀌어도 신제품 판정이 떨어지지 않는다(에그드랍 선례).

세트(…세트, 세트 (11AM-2PM))는 promo 로 찍지 않는다. 거르는 건
`collect.drop_sets()` 담당이다(이삭토스트 선례).

robots.txt: **404 다**(아파치 기본 404, HTML 함정 아님). 금지 규칙이 없다.
이용약관: 푸터에 `/policy.php`(개인정보 처리방침)와 `/email_policy.php`만 있고
이용약관 링크가 없다. 금지 조항을 확인하지 못했다는 뜻이지 없다는 뜻은 아니다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "지미존스"
HOST = "https://www.jimmyjohns.co.kr"
MENU_URL = HOST + "/homepage/menu.php"
DETAIL_URL = HOST + "/homepage/menu_detail.php"
IMG_ROOT = HOST + "/images/item/"
DELAY = 1.5          # 목록 요청 간격(초)
HEAD_DELAY = 0.8     # 이미지 HEAD 간격(초)
MAX_HEADS = 80       # 폭주 방지. 현재 상품 수가 이보다 적다

NEW_LABEL = "신메뉴"   # 브랜드가 신제품을 담는 카테고리 이름

# Last-Modified: Fri, 19 Jun 2026 07:32:37 GMT
_MONTHS = {m: i for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}
_LM = re.compile(r"\w{3},\s*(\d{1,2})\s+(\w{3})\s+(\d{4})")
_CAT_ID = re.compile(r"menu_detail\.php\?id=(JJ\d+)")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


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


def _categories(html: str) -> list:
    """메뉴 첫 화면의 카테고리 카드 → [(JJ코드, 라벨)]. 순서는 화면 그대로."""
    out, seen = [], set()
    for a in HTMLParser(html).css("ul.menu-list a[href]"):
        m = _CAT_ID.search(a.attributes.get("href") or "")
        label = _clean(a.text())
        if not m or not label or m.group(1) in seen:
            continue
        seen.add(m.group(1))
        out.append((m.group(1), label))
    return out


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(MENU_URL))
        r.raise_for_status()
        cats = _categories(r.text)
        if not cats:
            raise RuntimeError("지미존스: 카테고리 0개 — menu.php 구조가 바뀌었다")
        # 이 어댑터의 is_new 는 통째로 '신메뉴' 칸 하나에 걸려 있다. 사라지면 드러낸다.
        if not any(label == NEW_LABEL for _, label in cats):
            raise RuntimeError(f"지미존스: '{NEW_LABEL}' 카테고리가 사라졌다 — 신상 신호 없음")
        # 신메뉴를 먼저 돈다. 겹쳐 실린 상품의 is_new 가 떨어지지 않게.
        cats.sort(key=lambda x: x[1] != NEW_LABEL)
        time.sleep(DELAY)

        items: list[Item] = []
        by_key: dict = {}
        for code, label in cats:
            rr = base.retry(lambda: c.get(DETAIL_URL, params={"id": code}))
            rr.raise_for_status()
            cards = HTMLParser(rr.text).css("ul.menu-detail-list a[data-name]")
            if not cards:
                raise RuntimeError(
                    f"지미존스 {label}({code}): 상품 0건 — 셀렉터가 깨졌다")

            for a in cards:
                name = _clean(a.attributes.get("data-name"))
                if not name:
                    continue
                key = base.make_key(BRAND, name)
                if key in by_key:
                    it = by_key[key]
                    # `or` 를 쓰면 None 이 False 로 깎인다. 올리기만 한다.
                    if label == NEW_LABEL:
                        it.is_new = True
                    if not it.category and label != NEW_LABEL:
                        it.category = label
                    continue
                iid = _clean(a.attributes.get("data-item-id"))
                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=_clean(a.attributes.get("data-description")),
                    image=f"{IMG_ROOT}{iid}_main.png" if iid else "",
                    # 신메뉴는 분류가 아니라 상태다. 분류는 다른 칸에서 채운다.
                    category="" if label == NEW_LABEL else label,
                    # 신메뉴 칸이면 True, 아니면 **None(모름)** 이다. False 로
                    # 단정하면 전용 카테고리로 나온 새 라인이 통째로 묻힌다
                    # (docstring is_new 항목의 지미모닝 사고 참고).
                    is_new=True if label == NEW_LABEL else None,
                    # 상세 주소가 없다(목록에서 모달을 띄운다). SITES 폴백으로 떨어진다.
                )
                by_key[key] = it
                items.append(it)

            time.sleep(DELAY)

        if not items:
            raise RuntimeError("지미존스: 상품 0건")

        # 사진을 올린 날이다. 출시일이 아니라 uploaded_at 에 넣는다.
        # 신메뉴부터 채워 상한에 걸려도 최근 것이 먼저 날짜를 갖게 한다.
        for it in sorted(items, key=lambda x: x.is_new is not True)[:MAX_HEADS]:
            it.uploaded_at = _uploaded_at(c, it.image)
            time.sleep(HEAD_DELAY)

    return items
