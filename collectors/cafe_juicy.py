"""쥬씨(JUICY) — 메뉴판엔 날짜가 없다. 'NEWS' 게시판의 출시 기사에서 뽑는다.

쥬씨 주식회사. **도메인부터 함정이다.**

    juicy.co.kr   DNS 는 풀리는데(203.217.210.155) 443·80 둘 다 Connection refused
    juicy.kr      AWS IP. 200 이지만 본문 0바이트짜리 빈 응답(파킹)
    juicykorea.co.kr  NXDOMAIN
    → 사는 곳은 **`no1juicy.com`** 이다.

⚠️ 그리고 `no1juicy.com` 은 **https 가 없다.** 443 이 Connection refused 라
평문 http 로만 열린다(쉐이크쉑·부어치킨과 같은 자리). 그래서
`Item.image` 에 담는 `/uploads/...` 주소도 http 뿐이고, `base.derive()` 가
혼합 콘텐츠를 막으려고 그걸 지운다 — **이 브랜드는 사진이 안 붙는다.**
주소는 그대로 담아 둔다(https 가 생기면 그날 바로 살아난다).

## 메뉴판 — 이름은 다 있는데 신상 신호가 0건이다

    /products/latest   JUICY SPECIAL  0건(탭 껍데기만 있다)
    /products/fruits   FRESH JUICE   67
    /products/coffee   COFFEE        10
    /products/bowl     BOWL           3
    /products/beverage BEVERAGE      38
    /products/dessert  DESSERT       39     → 합계 152종

`section.menu_type ul li` 안에 `dt`(상품명) + `dd`(설명) + `img[data-src-pc]`.
2026-10-03 전수 실측:
  - **날짜가 없다.** 이미지 파일명이 `/uploads/menu/coffee/72ba1a37…080.png`
    처럼 MD5 해시라 날짜를 못 읽는다. CDN 경로에도 날짜가 없다.
  - **NEW 배지가 없다.** 있는 배지는 `strong.hit` 하나인데 그건 '인기'다
    (아메리카노·카페라떼·밸런스볼처럼 상시 메뉴에 붙는다). 신상이 아니다.
  - ⚠️ `strong.hit` 안에도 `<img>` 가 들어 있다. `li` 의 첫 `img` 를 집으면
    상품 사진이 아니라 `hit.png` 배지를 집는다. `/uploads/` 로 거른다.
  - `/products/latest`(JUICY SPECIAL)가 이름값을 할 것 같지만 **0건**이다.
    탭만 남고 내용이 비었다. 신메뉴 면이 아니다.
  - 그 밖에 소스에만 남아 있고 내비에서 빠진 경로가 8개 더 있다
    (`pressoNew`·`pressoCoffee`·`winter` 등 — 2브랜드 '쥬씨프레소' 와
    'ONLY HOT' 의 잔재다). **전부 0건**이라 읽지 않는다.

즉 메뉴판만 긁으면 152종이 통째로 '신상'이 된다. 그래서 안 긁는다.

## NEWS 게시판 — 여기에 날짜와 상품이 같이 있다

    목록  /bbs/board/lists?bo_table=news            (1면 5건)
    2면~  /bbs/board/lists/<n>?bo_table=news        ⚠️ `page=` 쿼리는 **무시된다**.
          쪽 번호가 **경로**에 붙는다. 이걸 모르고 `page=2` 로 돌리면 1면
          5건을 12번 받아 60건인 줄 알게 된다(실제로 그랬다).

목록이 특이하게 **본문 전문과 날짜를 그대로 싣는다.** `dt`=제목,
`dd.dot-ellipsis`=본문, 그 다음 `dd`=작성일. 상세를 안 받아도 된다 —
12면 60건이 요청 12회로 끝난다.

일괄 재등록부터 셌다(버거운버거 24건 중 22건이 한 날이라 못 쓴 전례).
60건의 날짜가 **2019-12-10 ~ 2026-04-13 에 걸쳐 48개 날짜**로 흩어지고,
가장 큰 묶음이 2021-07-16 **5건(8%)** 이다. 몰아 올리기가 아니다.

⚠️ **다만 이 게시판은 느리다.** 2026년 글이 1월 3건 + 4월 1건뿐이고
최신 글이 2026-04-13 이다(이 글을 쓰는 2026-10-03 기준 6개월 전). 그래서
**평소에는 60일 창에 걸리는 게 0건인 게 정상이다.** 0건을 수집 실패로
읽지 마라. 커피에반하다(최신 2024-12, 22개월)는 '멈췄다'고 보고 뺐지만
쥬씨는 아직 올해 글이 있어 넣는다 — 다음 시즌 글이 또 반년 비면 다시 본다.

## 상품명 — 따옴표 ∩ 메뉴판

보도자료가 상품명을 `‘…’` 로 감싼다. 그런데 따옴표 안이 상품이 아닌 게 더 많다 —
`‘Allday Strawberry’`·`‘Fall in Winter’`·`‘청포도 빛나는 봄’`·`‘수박 퀘스트’`
는 전부 **캠페인 이름**이고, `"오리온과 두 번째 콜라보"`·`'달콤 시원'` 도 걸린다.
금지어를 늘리는 대신 **메뉴판 152종과 교집합**을 쓴다(우지커피와 같은 방법).
위 오집은 메뉴판에 없어서 전부 떨어지고, 남는 건 `청포도 사과 프라페`·
`딸기 카페라떼`·`생아보카도커피` 처럼 지금 파는 상품뿐이다.

제목 거르기는 60건 전수를 읽고 맞췄다. 출시어(`신메뉴`·`신제품`·`출시`·
`선보`·`신상`·`시즌 메뉴`·`런칭`·`론칭`)가 있고 제외어가 없을 것.
제외어는 매장 오픈·창업박람회·멤버십 앱·캠페인·보증금제 홍보물처럼
'출시' 를 쓰지만 상품이 아닌 글들이다(쥬씨는 **앱 출시**·**가맹점 오픈** 글이
유난히 많다). 29건이 남고 그중 11건에서 상품이 잡혀 **21종**이 나온다.

같은 메뉴가 여러 해에 걸쳐 다시 나온다(수박·딸기·복숭아는 매년이다).
**가장 이른 기사 날짜**를 쓴다 — 재출시는 신상이 아니다(우지커피와 같은 방침).

`is_new=True` 는 '출시 기사에서만 담았다'는 뜻이다. 메뉴판 152종 중 21종(14%)
이라 '전건 NEW' 와는 다르다. 그래도 교집합이 깨져 메뉴판을 통째로 담는 사고를
막으려고 상한 가드를 둔다.

robots.txt: `no1juicy.com/robots.txt` 는 404 다(금지 규칙 없음).
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "쥬씨"
# ⚠️ https 는 443 Connection refused 다. 평문 http 뿐이다(docstring).
ROOT = "http://www.no1juicy.com"
LIST_PATH = "/bbs/board/lists"
BO_TABLE = "news"

# 경로 → 화면에 쓸 분류. /latest(JUICY SPECIAL)는 0건이라 뺐다.
MENU_PATHS = {
    "/products/fruits": "생과일주스",
    "/products/coffee": "커피",
    "/products/bowl": "볼",
    "/products/beverage": "음료",
    "/products/dessert": "디저트",
}

DELAY = 2.0
MAX_LIST_PAGES = 15        # 폭주 방지. 현재 12면 60건이 전부다.
MIN_MENU = 100             # 이보다 적으면 메뉴 선택자가 깨진 것이다(실측 152)
_MAX_SHARE = 0.50          # 담은 게 메뉴의 절반을 넘으면 교집합이 깨진 것이다

_RELEASE = ("신메뉴", "신제품", "출시", "선보", "신상", "시즌 메뉴", "런칭", "론칭")
# 60건 제목 전수를 읽고 맞췄다. 쥬씨는 앱·가맹점 글이 '출시/론칭'을 자주 쓴다.
_NOT_PRODUCT = ("오픈", "박람회", "캠페인", "이벤트", "멤버십", "돌파", "창업",
                "가맹", "앱", "보증금", "업데이트", "성료", "프로모션", "쿠폰",
                "리뷰", "계약", "진출", "안내", "홍보물", "전달")

# 홑따옴표(‘’ ')와 쌍따옴표(“” ")를 다 받는다. 어차피 메뉴판 교집합이 거른다.
_QUOTED = re.compile(r"[‘'\"“”]([^’'‘\"“”]{2,30})[’'\"“”]")
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _flat(s: str) -> str:
    return (s or "").replace(" ", "")


def _menu(c) -> dict:
    """메뉴 색인. 공백 턴 상품명 → (표시용 이름, 분류, 이미지, 설명)."""
    out = {}
    for path, label in MENU_PATHS.items():
        r = base.retry(lambda: c.get(ROOT + path))
        r.raise_for_status()
        time.sleep(DELAY)
        for li in HTMLParser(r.text).css("section.menu_type ul li"):
            dt = li.css_first("dt")
            dd = li.css_first("dd")
            name = _clean(dt.text()) if dt is not None else ""
            if not name:
                continue
            # ⚠️ 첫 img 는 strong.hit 안의 '인기' 배지일 수 있다(docstring).
            srcs = [i.attributes.get("data-src-pc", "") for i in li.css("img")]
            img = next((s for s in srcs if "/uploads/" in s), "")
            out.setdefault(_flat(name),
                           (name, label, ROOT + img if img.startswith("/") else img,
                            _clean(dd.text()) if dd is not None else ""))
    if len(out) < MIN_MENU:
        raise RuntimeError(f"쥬씨 메뉴 색인 {len(out)}건 — "
                           "section.menu_type 선택자나 메뉴 경로가 바뀌었다")
    return out


def _posts(c) -> list:
    """NEWS 목록에서 (제목, 본문, 날짜, 주소). 목록이 본문 전문을 싣는다."""
    out, seen = [], set()
    for page in range(1, MAX_LIST_PAGES + 1):
        # ⚠️ 쪽 번호가 쿼리가 아니라 경로다. `page=` 는 무시된다(docstring).
        url = ROOT + LIST_PATH + (f"/{page}" if page > 1 else "")
        r = base.retry(lambda: c.get(url, params={"bo_table": BO_TABLE}))
        r.raise_for_status()
        time.sleep(DELAY)
        rows = HTMLParser(r.text).css("ul.ntcList li")
        if not rows:
            break
        fresh = 0
        for li in rows:
            dt = li.css_first("dt")
            dds = li.css("dd")
            a = li.css_first("a")
            href = a.attributes.get("href", "") if a is not None else ""
            if dt is None or not dds or not href or href in seen:
                continue
            seen.add(href)
            fresh += 1
            body = _clean(dds[0].text())
            day = next((m.group(0) for d in dds
                        for m in [_DATE.search(_clean(d.text()))] if m), "")
            out.append((_clean(dt.text()), body, day, href))
        if not fresh:
            break           # 같은 면이 되풀이되면 쪽 번호 규칙이 바뀐 것이다
    if not out:
        raise RuntimeError(f"{ROOT}{LIST_PATH}?bo_table={BO_TABLE}: 글 목록이 비었다")
    return out


def _is_product_post(title: str) -> bool:
    return (any(w in title for w in _RELEASE)
            and not any(w in title for w in _NOT_PRODUCT))


def fetch() -> list[Item]:
    with base.client() as c:
        menu = _menu(c)
        found: dict = {}
        for title, body, day, href in _posts(c):
            if not day or not _is_product_post(title):
                continue
            for q in _QUOTED.findall(f"{title} {body}"):
                m = menu.get(_flat(q))
                if m is None:
                    continue
                prev = found.get(m[0])
                if prev is None or day < prev[0]:
                    found[m[0]] = (day, href)

    if not found:
        raise RuntimeError("쥬씨 0건 — NEWS 본문에서 메뉴판과 겹치는 "
                           "상품명을 하나도 못 찾았다")
    if len(found) > len(menu) * _MAX_SHARE:
        raise RuntimeError(f"쥬씨 {len(found)}건 / 메뉴 {len(menu)}건 — "
                           "따옴표 교집합이 깨져 메뉴판을 통째로 담고 있다")

    items = []
    for name, (day, href) in found.items():
        _, label, image, desc = menu[_flat(name)]
        items.append(Item(
            brand=BRAND,
            name=name,
            desc=desc,
            # http 뿐이라 base.derive() 가 지운다. 주소는 남겨 둔다(docstring).
            image=image,
            category=label,
            released_at=day,
            is_new=True,        # '출시' 기사에서만 담는다
            url=ROOT + href if href.startswith("/") else href,
        ))
    items.sort(key=lambda i: i.released_at, reverse=True)
    return items
