"""호식이두마리치킨.

공정위 등록 가맹점 722개로 치킨 업종 12위다.

⚠️ **도메인이 `9922.co.kr` 다.** `hosigi.co.kr` 가 아니다 — 브랜드 대표번호가 그대로
도메인이라 짐작으로는 절대 못 맞춘다. 한 줄 적어두는 게 다음 사람에게 제일 쓸모 있다.

imweb(아임웹)으로 만든 사이트고 갤러리 위젯이 **서버 렌더**라 HTML 에 상품이 그대로
들어 있다. 쿠키·세션 없이 열리고 브라우저도 불필요하다. 카드 하나가
`div._item.item_gallary` 이고 그 안에
  `div#caption_<id>` → `<h4>` 이름 (+ 꼬리 `<span>` 은 "*순살, 안심텐더 변경가능"
                      같은 **주문 옵션 안내**지 배지가 아니다. 이름에서 떼어낸다)
                   → `<p>` 설명
  `a.item_container[href]`  상품 상세 (`/204`·`/fried` 등. 없는 카드도 있다)
  `div.img_wrap[data-src]`  실제 이미지(`https://cdn.imweb.me/thumbnail/<YYYYMMDD>/…`)
정규식 대신 selectolax 로 읽는다. 더 안전해서다 — 추천받은 정규식은
`[\\s\\S]{0,2000}?` 로 카드 경계를 넘나들고, 실제로 이 사이트에는 주석 처리된
옛 카드가 섞여 있어서 경계를 안 지키면 죽은 상품을 주워온다(60계에서 실제로 그랬다).
DOM 으로 끊으면 그 사고가 구조적으로 안 난다. 덤으로 설명·상세링크까지 같이 나온다.

🔴 **목록을 `/menu`(전체 메뉴)가 아니라 분류 3면에서 받는다.** 2026-10-02 실측:
    /menu    32건      /chicken 14 + /parts 6 + /side 15 = 35건
`/menu` 가 **3건 모자란다** — 쉬림프 미니튀김(칠리)·(레몬크림)(둘 다 2025-11-19 업로드,
즉 비교적 새 상품)과 치킨무가 빠져 있다. 전체 메뉴 면이 갱신에서 밀린 것이다.
게다가 같은 상품의 이름 표기가 두 면에서 다르다 — `날개+다리`/`윙+다리`,
`허니갈릭치즈볼(6개)`/`허니갈릭치즈볼`, `트리플 치즈볼(6개)`/`트리플치즈볼`.
base.make_key() 는 `(6개)`를 사이즈 표기로 보지 않아 안 턴다. 그래서 두 면을 **같이**
긁으면 같은 상품이 두 줄로 들어간다. 분류 3면만 쓰면 건수도 더 많고 Item.category 도
공짜로 채워진다. `/menu` 는 쓰지 마라.
⚠️ 같은 상품이라도 면마다 이미지가 **따로 업로드**돼 있어서 `caption_<id>` 와 경로
날짜가 면마다 다르다(예: 간장 치킨이 /menu 는 20200120, /chicken 은 20200122).
그러니 caption id 는 상품 식별자가 아니다. 중복 판정은 base.make_key(이름)으로 한다.

🔴 **신제품 신호는 이미지 경로의 날짜 하나뿐이다.**
NEW 배지도 '신메뉴' 탭도 출시일 표기도 **없다**. 그래서 **is_new 는 전건 None 이다** —
'신제품이 아니다(False)'가 아니라 '브랜드가 말해주지 않았다'는 뜻이다. 배지를 지어내지 마라.
⚠️ 이 사이트 HTML 에는 "new" 라는 글자가 수백 번 나오는데 전부 테마 CSS 클래스
(`new_fixed_header`·`new_header_mode`)다. NEW 를 정규식으로 찾으면 전건 오탐이다.

🔴 **`notes/CANDIDATES-CHICKEN.md` §7-5 의 예외다.** 그 조항은 "imweb 경로 날짜는
보통 일괄 업로드 한 덩어리라 쓰지 마라"이고, **그 규칙의 출처가 바로 호식이**다
(당시 전 상품이 `20200120` 하나였다). **그 측정은 이제 낡았다.** 2026-10-02 실측
35건의 경로 날짜 분포다.
    20200122 ×11   20200519 ×2   20201120 ×1   20201201 ×1   20210719 ×2
    20221223 ×1    20230608 ×1   20231012 ×1   20240425 ×1   20240627 ×4
    20241114 ×1    20250416 ×1   20250619 ×4   20251119 ×3   20260616 ×1
15개 날짜로 흩어진다. 2020-01-22 덩어리 11건은 사이트 구축 배치라 그 안에서는
신구를 못 가리지만, 나머지 24건은 제품별로 흩어져 있어 기준선으로 쓸 만하다.
§7-5 규칙 자체는 여전히 유효하다 — **이 브랜드에 대해서만** 뒤집힌 것이고,
땅땅치킨도 같은 예외다. 브랜드마다 재서 흩어지면 쓰고 한 덩어리면 버려라.

경로 날짜가 진짜 업로드 시각인지 HEAD 로 35건 전수 확인했다(2026-10-02).
27건은 Last-Modified 날짜와 그대로 일치하고, 어긋난 8건은 **전부 정확히 하루 차이**다.
확인해 보니 Last-Modified 가 UTC 라서 그렇다 — 예: 경로 `20250619`,
헤더 `Wed, 18 Jun 2025 23:16:11 GMT` = KST 2025-06-19 08:16. 즉 **경로 날짜가 KST 기준
업로드일**이고 헤더보다 오히려 우리가 쓰고 싶은 값이다. 땅땅치킨에서 내린 결론과 같다.
그래서 HEAD 를 35번 더 때리지 않고 경로에서 읽는다(굽네 선례).

업로드일이지 브랜드가 말해준 출시일이 아니므로 **released_at 은 전건 비운다.**

상품 상세는 카드가 이미 들고 있는 `a.item_container[href]` 다(`/204`·`/fried`).
3건은 `<a>` 에 href 가 없어 비고, base.SITES 폴백으로 떨어진다.
가격은 사이트 어디에도 없다.
'플라윙 세트 (윙+봉)'·'치즈볼 2종세트' 는 그 자체가 하나의 상품이지 할인·행사가
아니므로 promo 는 전건 False 다. 세트 판정은 rules.drop_sets() 가 이름으로 한다.

robots.txt 는 `User-agent: *` / `Allow: /` 에 가입·로그인·장바구니·`/admin`·`/?mode*`
만 Disallow 다. 우리가 읽는 `/chicken`·`/parts`·`/side` 는 허용 범위다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "호식이두마리치킨"
SITE = "https://www.9922.co.kr"

# (경로, 화면상 분류). '전체 메뉴'(/menu)는 일부러 뺐다 — 위 docstring 참고.
LISTS = [
    ("/chicken", "치킨"),
    ("/parts", "부위별"),
    ("/side", "사이드"),
]

MAX_ITEMS = 200   # 폭주 방지. 현재 35건.
DELAY = 0.5       # 목록 요청 간격(초). 전부 합쳐 3요청이다.


def _uploaded_at(img_url: str) -> str:
    """이미지 경로의 업로드일(cdn.imweb.me/thumbnail/20260616/…)을 YYYY-MM-DD 로.

    KST 기준 날짜다(위 docstring 의 UTC 하루 차이 검증 참고).
    """
    m = re.search(r"/thumbnail/(\d{4})(\d{2})(\d{2})/", img_url or "")
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def _name_desc(cap) -> tuple:
    """캡션에서 (이름, 설명). <h4> 꼬리의 <span> 은 주문 옵션 안내라 떼어낸다.

    떼지 않으면 이름이 '딥블랙갈릭 치킨*순살, 안심텐더 변경가능' 이 된다. 안내 문구는
    브랜드가 수시로 고치는 자리라, 붙여두면 문구가 바뀔 때마다 Item.key 가 바뀌어
    같은 상품이 신규로 다시 올라온다.
    """
    h4 = cap.css_first("h4")
    if not h4:
        return "", ""
    note = h4.css_first("span")
    if note:
        note.decompose()
    p = cap.css_first("p")
    return " ".join(h4.text().split()), " ".join(p.text().split()) if p else ""


def _cards(client, path: str) -> list:
    r = base.retry(lambda: client.get(SITE + path))
    r.raise_for_status()
    return HTMLParser(r.text).css("div._item.item_gallary")


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        for path, category in LISTS:
            time.sleep(DELAY)
            cards = _cards(c, path)
            # 한 면이 비면 그 분류가 통째로 사라진다. 나머지 두 면이 살아 있으면
            # 건수가 35 → 20 으로만 줄어서 0건 가드에 안 걸리고 조용히 굳는다.
            if not cards:
                raise RuntimeError(
                    f"{path} 목록이 비었다 — 셀렉터가 깨졌을 가능성")

            for card in cards:
                cap = card.css_first("div[id^=caption_]")
                if not cap:
                    continue
                name, desc = _name_desc(cap)
                if not name:
                    continue
                img = card.css_first("div.img_wrap")
                image = (img.attributes.get("data-src", "") if img else "").strip()
                a = card.css_first("a.item_container")
                href = (a.attributes.get("href", "") if a else "").strip()

                it = Item(
                    brand=BRAND,
                    name=name,
                    desc=desc,
                    image=image,
                    category=category,
                    uploaded_at=_uploaded_at(image),
                    # NEW 배지도 신메뉴 탭도 없다. '아니다(False)'가 아니라
                    # '브랜드가 말해주지 않았다'라서 None 이다.
                    is_new=None,
                    # 할인·행사 표시가 없는 카탈로그다. 세트는 promo 가 아니다
                    # (rules.drop_sets() 가 이름으로 거른다).
                    promo=False,
                    url=SITE + href if href.startswith("/") else "",
                )
                if it.key in seen:
                    continue
                seen.add(it.key)
                items.append(it)
                if len(items) >= MAX_ITEMS:
                    break

    # 🔴 '건수는 멀쩡한데 날짜만 사라진' 상태를 막는다. 이 브랜드는 NEW 배지도
    # 신메뉴 탭도 없어서 경로 날짜가 **유일한 신호**인데, imweb 이 CDN 경로를
    # 바꾸면(`/thumbnail/<8자리>/` 가 아니게 되면) `_uploaded_at` 이 전건 빈
    # 문자열을 돌려준다. 건수는 35 그대로라 collect.py 의 0건 가드도 FLOOR 도
    # 통과하고 "호식이는 신제품이 없다" 가 조용히 굳는다 — 2026-10-03 리뷰에서
    # 재현했다(경로만 바꿔치니 35건·날짜 0건으로 성공 처리됐다).
    # 치킨플러스·노랑통닭·가마치통닭과 같은 가드다(실측 35/35 가 날짜를 받는다).
    dated = sum(1 for it in items if it.uploaded_at)
    if dated * 2 < len(items):
        raise RuntimeError(
            f"호식이두마리치킨 업로드일 {len(items)}건 중 {dated}건만 붙었다 — "
            f"CDN 경로(cdn.imweb.me/thumbnail/<YYYYMMDD>/)가 바뀌었을 가능성. "
            f"이 브랜드의 유일한 신제품 신호다")
    return items
