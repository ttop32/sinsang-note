"""팔도.

앞의 세 제조사와 성격이 다르다. 보도자료가 아니라 **제품 카탈로그**를 읽는다.
카탈로그에 브랜드가 직접 켜고 끄는 `신제품` 배지가 SSR 로 붙어 있다. 2026-09-30 실측:

    <li><a href="/product/noodle/202">
        <span class="flag new">신제품</span>
        <span class="thumb-block"><img src="/data/product/104157_noodle-054-thumb.png"
                                       alt="아리 모던누들 간장버터"></span>
        <span class="tit-block">아리 모던누들 간장버터</span>
    </a></li>

상품 축이 1:1 이라 보도자료처럼 "2종"을 쪼개는 문제가 없다. 대신 **날짜가 없다.**
목록에도 상세(/product/noodle/202)에도 날짜 토큰이 0개다. 그래서 released_at 은
비우고 is_new 만 채운다. 배지가 브랜드의 명시적 표시이므로 배지가 없으면 False 로
내린다(모름이 아니다). 배지가 낡을 수는 있어도 그건 브랜드가 관리하는 값이다.

목록은 첫 화면에 12건만 SSR 로 내주고 나머지는 '12개 더보기'로 붙인다.
그 버튼(common.js #next_page)이 **같은 URL 로 POST** 를 한다 — 멀티파트로
`m=g`, `page=N`, `code=<슬러그>` 를 보내면 `{code, msg:<li>…</li>, etc:{nextPage}}`
가 온다. nextPage 가 0이면 끝이다. 브라우저는 필요 없다.
⚠️ 조사 문서는 "면류 75건 중 신제품 12건"이라 적었는데, 그 12건은 **첫 화면에
   보이는 12건**이었다. 2페이지에도 `flag new` 가 계속 나온다. 첫 화면만 보면
   신제품을 놓친다.
/product/archive 는 받지 않는다. 상품명이 없는 단종 아카이브다(10건, 전부 빈 제목).

2026-09-30 실측 총 102건 / `신제품` 46건
(면 43/18 · 음료 29/14 · 소스 17/8 · 해외브랜드 6/0 · 스낵 4/3 · 간편식 3/3).

desc 는 상세 페이지에만 있다(`.tit .desc`). 상품 102건을 하나씩 더 받아야 해서
받지 않는다. 비워 둔다.
⚠️ 도메인 주의: `paldo.com` 은 파킹이다. 정본은 `paldofood.co.kr`.

robots: https://www.paldofood.co.kr/robots.txt → 200, text/plain, 본문 첫 글자 'U'.
        `User-agent: *` / `Disallow: /adm/` / `Allow: /` 순서다. Disallow 가 먼저라
        뒤의 `Allow: /` 가 앞을 지우지 않는다. /product/ 도 /data/ 도 허용이다.
약관: 이용약관 링크를 못 찾았다. 푸터에 개인정보처리방침만 있다. 확인 못 함.
"""
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "팔도"
SITE = "https://www.paldofood.co.kr"
DELAY = 2.2
MAX_PAGES = 15       # 카테고리당 상한. 한 페이지 12건. 폭주 방지.

# (경로, 화면에 쓸 분류명). archive(단종)는 뺀다.
CATEGORIES = (
    ("noodle", "면"),
    ("beverage", "음료"),
    ("convenient-food", "간편식"),
    ("snack", "스낵"),
    ("source", "소스"),
    ("overseas-brand", "해외브랜드"),
)


def _parse(html: str, slug: str, label: str, seen: set) -> list:
    out = []
    for a in HTMLParser(html).css("li a"):
        href = a.attributes.get("href", "")
        # 카테고리 내비게이션(/product/noodle)과 상품(/product/noodle/202)을 가른다
        if not href.startswith(f"/product/{slug}/") or href in seen:
            continue
        tit = a.css_first(".tit-block")
        name = " ".join(tit.text().split()) if tit else ""
        if not name:
            continue
        seen.add(href)
        img = a.css_first(".thumb-block img")
        flag = a.css_first("span.flag")
        out.append(Item(
            brand=BRAND,
            name=name,
            image=(SITE + img.attributes.get("src", "")) if img else "",
            category=label,
            # 브랜드가 직접 켜고 끄는 배지다. 없으면 신제품이 아니라는 뜻으로 읽는다.
            is_new=bool(flag and "신제품" in flag.text()),
            url=SITE + href,
        ))
    return out


def fetch() -> list[Item]:
    items: list[Item] = []
    keys = set()
    first = True
    with base.client() as c:
        for slug, label in CATEGORIES:
            url = f"{SITE}/product/{slug}"
            seen = set()          # 상단 추천 블록이 같은 상품을 한 번 더 싣는다
            if not first:
                time.sleep(DELAY)
            first = False
            r = base.retry(lambda: c.get(url))
            r.raise_for_status()
            found = _parse(r.text, slug, label, seen)

            for page in range(2, MAX_PAGES + 1):
                if not found:
                    break
                time.sleep(DELAY)
                # '12개 더보기' 버튼이 보내는 것과 같은 멀티파트 POST
                r = base.retry(lambda: c.post(url, files={
                    "m": (None, "g"), "page": (None, str(page)), "code": (None, slug)}))
                r.raise_for_status()
                data = r.json()
                if str(data.get("code")) != "1":
                    break
                more = _parse(data.get("msg") or "", slug, label, seen)
                found += more
                if not more or int((data.get("etc") or {}).get("nextPage") or 0) <= 0:
                    break

            for it in found:
                if it.key not in keys:
                    keys.add(it.key)
                    items.append(it)
    return items
