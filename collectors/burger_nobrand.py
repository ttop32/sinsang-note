"""노브랜드버거 — 신세계푸드 브랜드 홈 **1요청**에 전체 메뉴가 다 있다.

`www.nobrandburger.com` 은 `https://www.shinsegaefood.com/nobrandburger/index.sf`
로 리다이렉트된다. 그 한 장이 647KB SSR 이고 메뉴 55건이 통째로 들어 있다.
브라우저·API·토큰 전부 불필요. 요청 1회.

⚠️ **TLS 를 verify=False 로 우회하지 않는다.** 앞선 조사 메모에는 두 호스트가
`CERTIFICATE_VERIFY_FAILED` 라 적혀 있었는데 2026-10-02 실측에서는 **재현되지
않는다.** 인증서가 2026-08-05 에 갱신됐고 체인이 완전하다(GlobalSign GCC R46
OV TLS CA 2025 → Root R46 → Root R3, `openssl s_client` 로 확인). `base.client()`
기본값(verify=True)으로 6회 연속 200 이다. `www.nobrandburger.com` 으로 걸어도
같은 곳으로 떨어지며 검증을 통과한다. 다시 깨지면 그때 `verify=False` 가 아니라
먼저 체인을 확인해라 — `notes/CANDIDATES-PIZZA-FASTFOOD.md` §5-5 방침이다.

## 상품은 속성에 들어 있다

카드가 `<a>` 가 아니라 JS 모달 버튼이고, 데이터는 버튼의 data-* 에 있다.

    <li class="menu_item new">
      <button class="menu_anch" onclick="openPop('popup-menu', this)"
        data-name="버크셔K 카츠</br>Berkshire K Katsu"
        data-img="2026/07/29/버크셔K카츠_단품_06.홈페이지(보정본).png"
        data-story='…설명…'>

`data-name` 은 **한글명과 영문명이 `</br>` 로 붙어 있다.** 그대로 쓰면 상품명에
영문이 들러붙으니 끊어서 `name` / `name_en` 으로 나눈다(구분자가 `</br>`·`<br/>`
둘 다 나온다 — 한 카드 안에서 섞인다). `data-story` 에는 `<br />` 과 색상
`<span>` 이 섞여 있어 태그를 벗긴다.

이미지 실주소는 `https://www.shinsegaefood.com/uimages/` + `data-img` 다. 파일명이
한글이라 퍼센트 인코딩해서 넣는다(인코딩 없이도 서버는 받지만, 우리 HTML 에
그대로 박히는 주소라 인코딩된 쪽이 안전하다). 2026-10-02 실측 200/157KB.

## 신제품 신호 — `li` 의 `new` 클래스다

🔎 **대문자 'NEW' 로 세면 0건이 나온다.** 이 페이지에는 `NEW`·`icon_new`·
`badge` 문자열이 한 번도 안 나오고, '신메뉴' 는 **파일명 한 곳**
(`신메뉴_06.홈페이지_주스_(1).png`)에만 있다. 신호는 소문자 클래스다.

55건의 `li.menu_item` 클래스 분포(2026-10-02 전수) —
`menu_item` 41 · **`menu_item new` 8** · `menu_item best` 5 · `menu_item kids` 1.

## 교차검증 — new 8건이 업로드일 상위 8건과 정확히 겹친다

`data-img` 경로 앞이 `YYYY/MM/DD` 라 상품마다 업로드일이 나온다. 55건을 날짜로
세웠더니 `new` 8건이 **전부 최신 구간**에 있었다.

| 날짜 | new | 상품 |
|---|---|---|
| 2026-08-13 | ✅ | 풀드포크 샐러드 · 아보카도 새우 샐러드 |
| 2026-07-29 | ✅ | 버크셔K 카츠 · 버크셔K 카츠 어니언 |
| 2026-07-28 | ✅ | 데일리 치킨 |
| 2026-06-30 | ✅ | 메이플 고구마 · 슈크림 츄러스 · 아이스 슈 |
| 2026-06-30 | ❌ | 크런치 새우볼 · 치즈스틱 ← 같은 날인데 배지가 없다 |
| 2026-06-12 이전 | ❌ | 나머지 45건 전부 |

`new` 가 붙은 것 중 2026-06-30 보다 오래된 건 **0건**이다. 배지와 날짜가
서로를 받쳐준다. 같은 2026-06-30 안에서도 3건만 붙은 걸 보면 배지는 날짜보다
세밀하게 관리되고 있다 — 일괄로 찍고 방치한 게 아니다.

⚠️ 날짜는 `released_at` 이 아니라 `uploaded_at` 이다. 2025-05-07 에 20건이
몰려 있는데 그건 사이트 개편 때의 일괄 재업로드다(`rules.untrust_bulk_dates`
가 알아서 무효화한다 — 그 브랜드 중앙값 2건의 10배를 넘는다).

배지 없는 카드는 `is_new=None` 이다. False 가 아니다 — 이 템플릿에는
'여긴 신메뉴 아님' 을 명시하는 표시가 없다(프랭크버거 `icon_none` 과 다르다).

## 담지 않는 것

상품별 주소가 없다. 카드가 `openPop('popup-menu', this)` 로 같은 페이지에
모달을 띄울 뿐이라 가리킬 URL 자체가 존재하지 않는다. `url` 은 비우고
`base.SITES` 폴백에 맡긴다. 가격은 페이지에 없다.
"""
import certifi
import pathlib
import ssl
import re
from urllib.parse import quote

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "노브랜드버거"
ROOT = "https://www.shinsegaefood.com"
MENU_URL = ROOT + "/nobrandburger/index.sf"
IMG_BASE = ROOT + "/uimages/"
MAX_ITEMS = 300      # 폭주 방지. 현재 55건.

NEW_CLASS = "new"    # li.menu_item 에 붙는 소문자 클래스 (위 docstring)

# data-name 의 한·영 구분자. 한 페이지 안에 `</br>` 와 `<br />` 가 섞여 있다.
_BR = re.compile(r"<\s*/?\s*br\s*/?\s*>", re.I)
_TAG = re.compile(r"<[^>]+>")
_IMG_DATE = re.compile(r"^(\d{4})/(\d{2})/(\d{2})/")


# 서버가 중간 인증서를 빠뜨린다. 2026-10-08 실측 10/10 전부 리프 한 장만 보낸다
# (`openssl s_client` 로 확인). 리프의 issuer 는 GlobalSign GCC R46 OV TLS CA
# 2025 이고 AIA 가 가리키는 곳에서 그 한 장을 받아 두었다.
#
# ⚠️ 10-02 실측에서는 **재현되지 않았다**(docstring 에 "verify=True 로 6회 연속
# 200" 이라고 적혀 있다). 그 사이 서버 설정이 바뀐 것이다. 사이트가 멀쩡해
# 보여도 체인은 따로 봐야 한다는 뜻이라 적어 둔다.
#
# `verify=False` 는 쓰지 않는다 — notes/CRAWLING-POLICY.md §6-1 이 명시적으로
# 금지하고, 같은 사유·같은 처리의 선례가 lottechilsung.py·chicken_toreore.py 다.
# 검증은 켜진 채 돈다. certifi 루트에 **더하기만** 한다.
_CA_EXTRA = pathlib.Path(__file__).parent / "certs" / \
    "globalsign-gcc-r46-ov-tls-ca-2025.pem"


def _ssl_context() -> ssl.SSLContext:
    """certifi 루트에 서버가 빠뜨린 중간 인증서 한 장을 **더한** 컨텍스트."""
    if not _CA_EXTRA.exists():
        raise FileNotFoundError(
            f"중간 인증서가 없다: {_CA_EXTRA} — 이게 없으면 이 사이트는 "
            "unable to get local issuer certificate 로 붙지 않는다")
    ctx = ssl.create_default_context(cafile=certifi.where())
    ctx.load_verify_locations(cafile=str(_CA_EXTRA))
    return ctx


def _clean(s: str) -> str:
    return " ".join(_TAG.sub(" ", s or "").replace("&nbsp;", " ").split())


def _split_name(data_name: str) -> tuple:
    """`한글명</br>English Name` → (한글명, 영문명). 영문이 없으면 뒤는 빈 값."""
    parts = [p.strip() for p in _BR.split(data_name or "") if p.strip()]
    parts = [_clean(p) for p in parts]
    parts = [p for p in parts if p]
    if not parts:
        return "", ""
    if len(parts) == 1:
        # `주스 / Juice` 처럼 슬래시로 붙여 둔 것도 있다. 뒤가 라틴문자뿐이면 영문명이다.
        head, sep, tail = parts[0].partition(" / ")
        if sep and re.fullmatch(r"[A-Za-z0-9 &'().,\-]+", tail):
            return head.strip(), tail.strip()
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def _image(data_img: str) -> str:
    """`2026/07/29/버크셔K카츠….png` → 절대 주소. 파일명이 한글이라 인코딩한다."""
    if not data_img:
        return ""
    return IMG_BASE + quote(data_img.strip(), safe="/")


def _uploaded_at(data_img: str) -> str:
    m = _IMG_DATE.match((data_img or "").strip())
    return "-".join(m.groups()) if m else ""


def fetch() -> list[Item]:
    with base.client(verify=_ssl_context()) as c:
        r = base.retry(lambda: c.get(MENU_URL))
        r.raise_for_status()

    doc = HTMLParser(r.text)
    groups = doc.css(".menu_group")
    if not groups:
        raise RuntimeError(f"{MENU_URL}: .menu_group 이 0개다(마크업이 바뀌었다)")

    items: list[Item] = []
    seen = set()
    for g in groups:
        title = g.css_first(".menu_group_title")
        category = " ".join(title.text().split()) if title else ""
        for li in g.css("li.menu_item"):
            btn = li.css_first("[data-name]")
            if btn is None:
                continue
            name, name_en = _split_name(btn.attributes.get("data-name"))
            if not name:
                continue
            data_img = btn.attributes.get("data-img") or ""
            is_new = NEW_CLASS in (li.attributes.get("class") or "").split()
            it = Item(
                brand=BRAND,
                name=name,
                name_en=name_en,
                desc=_clean(btn.attributes.get("data-story")),
                image=_image(data_img),
                category=category,
                uploaded_at=_uploaded_at(data_img),
                is_new=True if is_new else None,
            )
            if it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)
            if len(items) > MAX_ITEMS:
                raise RuntimeError(f"{BRAND}: 상품이 {MAX_ITEMS}건을 넘었다")

    if not items:
        raise RuntimeError(f"{MENU_URL}: data-name 에서 상품을 하나도 못 뽑았다")
    return items
