"""카페베네(CAFFEBENE).

⚠️ **http 전용이다.** `caffebene.co.kr`·`www.caffebene.co.kr` 둘 다 DNS 는
223.130.162.98 로 풀리는데 443 이 ConnectTimeout 이다(2026-10-03 실측).
`caffebene.com` 도 같은 IP 이고 http 로 `caffebene.co.kr` 로 떨어진다.
`eng.caffebene.co.kr` 은 영문 사이트다. 그래서 평문 http 로 연다
(쉐이크쉑·부어치킨과 같은 처지다).

그 대가로 **사진이 화면에 안 올라간다.** 이미지 주소가 http 뿐이라
base.derive() 가 지운다(혼합 콘텐츠). 주소를 그대로 넣어두지도 못한다 —
지워지는 게 설계다. 사진 없는 카드로 그린다(에그드랍 선례).

── 경로 ───────────────────────────────────────────────────────────────
`/menu/new.html` 이 신메뉴 전용 면이고 **서버렌더**다. 카테고리 면
(`/menu/menu_list.html?code=001000`)은 껍데기만 오고 목록은
`POST /menu/lib/ajax.menu_data.php` 가 HTML 조각으로 돌려준다
(`Data.Load(code)`, /menu/lib/menu.js). code 는 5개다 —
001000 커피 · 002000 음료 · 003000 푸드 · 004000 MD · 005000 Retail.

상세는 `/menu/menu_view.html?seq=<번호>&code=&scode=` 로 사람도 열 수 있고
설명(`p.t1`)이 거기 있다. 신메뉴 면의 카드가 이미 그 주소를 href 로 들고
있어서 조립하지 않고 그대로 쓴다.

── 신상 판정 (2026-10-03 실측) ─────────────────────────────────────────
  신메뉴 면 9건 / 전체 207건(중복 1건 제외한 208행) = **4.3%**
  신메뉴에만 있고 전체엔 없는 건 0건.
카테고리 목록에는 NEW 배지가 **아예 없다**(`class="…new…"` 0건). 배지로는
셀 수 없고 전용 면이 유일한 신호다. 전건이 아니므로 가짜는 아니다.
신메뉴 면은 배너(`.sd img[alt]`)로 묶여 있는데 지금은 '26_여름 신메뉴1/2'
두 묶음이다. 배너 alt 는 시즌 표기일 뿐이라 날짜로 쓰지 않는다.

⚠️ **신메뉴 면이 재등장 시즌메뉴를 같이 담는다.** 9건 중 '애플망고 눈꽃빙수'
(seq=540)는 사진이 2024-07-16 자다. 여름마다 돌아오는 상품을 그 해 라인업에
다시 올린 것이다. 브랜드가 신메뉴라 묶었으니 is_new 는 True 로 두되,
날짜(아래)가 낡은 그대로라 60일 창에서 저절로 빠진다. 날짜를 지어내
'새 상품'으로 밀어 올리지 않는다.

── 날짜 ───────────────────────────────────────────────────────────────
브랜드가 출시일을 적지 않는다. 사진 파일명이 `/uploads/product/
20260611193053.png` 꼴로 **앞 8자리가 날짜**다. 이걸 uploaded_at 에만 넣고
released_at 은 비운다.

⚠️ 일괄 재업로드가 크다. 전체 208건의 월 분포가 2020-06 53건 · 2026-02 63건
으로 두 번 몰려 있다(사이트 개편분으로 보인다). 그래서 이 날짜는 '출시'가
아니라 '사진 올린 날'이다. 지금 신메뉴 9건은 2026-06-10(6건)·2026-06-11(2건)
·2024-07-16(1건)로, 2026년 여름 라인업 한 번에 해당한다.
"""
import re
import time
from datetime import datetime

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "카페베네"
SITE = "http://caffebene.co.kr"          # https 는 443 이 안 열린다
NEW_URL = f"{SITE}/menu/new.html"
AJAX_URL = f"{SITE}/menu/lib/ajax.menu_data.php"
LIST_URL = f"{SITE}/menu/menu_list.html"

# 전체 메뉴 코드. 대조(가드)에만 쓰고 상품으로는 담지 않는다.
CODES = ("001000", "002000", "003000", "004000", "005000")

DELAY = 2.0
MAX_DETAILS = 40          # 폭주 방지. 현재 신메뉴 9건.
MAX_NEW_RATIO = 0.5       # 신메뉴가 전체의 절반을 넘으면 가짜다. 실측 4.3%.

# 사진 파일명 앞 8자리가 날짜다. `/uploads/product/20260611193053.png`.
_STAMP = re.compile(r"/(\d{8})\d{6}\.[A-Za-z]{3,4}")


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _abs(u: str) -> str:
    if not u:
        return ""
    return u if u.startswith("http") else SITE + "/" + u.lstrip("/")


def _uploaded_at(src: str) -> str:
    """사진 파일명 앞 8자리 → 'YYYY-MM-DD'. 날짜로 안 읽히면 빈 문자열."""
    m = _STAMP.search(src or "")
    if not m:
        return ""
    try:
        d = datetime.strptime(m.group(1), "%Y%m%d")
    except ValueError:
        return ""
    # 2015~오늘+1일 밖이면 날짜가 아니라 다른 숫자다. 지어내지 않는다.
    if not (2015 <= d.year <= datetime.now().year + 1):
        return ""
    return d.strftime("%Y-%m-%d")


def _cards(html: str) -> list:
    """목록/조각 HTML → [(상품명, 사진 src, 상세 href)]."""
    out = []
    for li in HTMLParser(html).css("li"):
        nm = li.css_first(".m-name")
        name = _clean(nm.text()) if nm else ""
        if not name:
            continue
        img = li.css_first(".m-photo img")
        a = li.css_first("a")
        out.append((name,
                    _abs(img.attributes.get("src", "") if img else ""),
                    a.attributes.get("href", "") if a else ""))
    return out


def _desc(c, url: str) -> str:
    """상세의 `p.t1`. 실패하면 조용히 빈 값으로 둔다."""
    r = base.retry(lambda: c.get(url))
    r.raise_for_status()
    p = HTMLParser(r.text).css_first(".menu-detail-view-info p.t1")
    return _clean(p.text()) if p else ""


def fetch() -> list[Item]:
    with base.client(headers={"Referer": NEW_URL}) as c:
        r = base.retry(lambda: c.get(NEW_URL))
        r.raise_for_status()
        new_rows = _cards(r.text)
        if not new_rows:
            raise RuntimeError("카페베네 신메뉴 0건 — 셀렉터가 깨졌을 수 있다")

        # 🔴 전용 면을 믿기 전에 전체와 센다. 전건에 붙으면 가짜다.
        full = []
        for code in CODES:
            time.sleep(DELAY)
            rr = base.retry(lambda: c.post(
                AJAX_URL, data={"code": code},
                headers={"X-Requested-With": "XMLHttpRequest",
                         "Referer": f"{LIST_URL}?code={code}"}))
            rr.raise_for_status()
            full += _cards(rr.text)
        if not full:
            raise RuntimeError("카페베네 전체 메뉴 0건 — 대조를 못 하니 신상 판정도 못 한다")

        new_names = {n for n, _, _ in new_rows}
        full_names = {n for n, _, _ in full}
        ratio = len(new_names & full_names) / len(full_names)
        if ratio > MAX_NEW_RATIO:
            raise RuntimeError(
                f"카페베네 신메뉴가 전체의 {ratio:.0%}"
                f"({len(new_names)}/{len(full_names)}) — 전용 면이 가짜로 보인다")

        items: list[Item] = []
        seen = set()
        for name, img, href in new_rows:
            it = Item(
                brand=BRAND,
                name=name,
                image=img,                      # http 라 derive 가 지운다(위 docstring)
                uploaded_at=_uploaded_at(img),
                is_new=True,
                url=_abs(href),
            )
            if it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)

        for it in items[:MAX_DETAILS]:
            if not it.url:
                continue
            time.sleep(DELAY)
            it.desc = _desc(c, it.url)

    return items
