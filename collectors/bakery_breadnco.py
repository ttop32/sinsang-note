"""브레댄코.

워드프레스인데 상품이 파리바게뜨처럼 REST 로 열려 있지는 않다. 2026-09-30 실측.

  GET /wp-json/wp/v2/types      → post / page / attachment / wp_block 넷뿐
  GET /wp-json/wp/v2/portfolio  → 404 rest_no_route

**상품이 어디 있는지는 sitemap 이 알려줬다.** sitemap.xml 이 인덱스인데 그 안에
portfolio-sitemap.xml(214건)과 portfolio_category-sitemap.xml(30건)이 있다. 상품은
`portfolio` 커스텀 타입이고 show_in_rest 가 꺼져 있어서 REST 에는 안 뜬다.
분류 아카이브는 HTML 로 정상 렌더된다.

  GET /portfolio-category/new/            신제품 1페이지 (12건)
  GET /portfolio-category/new/page/2/ ~   2·3페이지 (12 + 2건)

**신제품 분류만 받는다.** 전체 214건을 받으려면 분류 아카이브를 30개 돌아야 하고
한 아카이브가 또 최대 9페이지다(bread 분류가 그렇다). posts_per_page 는 무시된다.
반면 `new` 분류는 지금도 관리되고 있다 — 26건의 sitemap lastmod 가 2025-09 ~
2026-09-29 이고 제일 최근 건이 어제다. 이 서비스가 필요한 건 신제품이라
3요청으로 끝나는 이 목록을 쓴다. 전체 카탈로그가 필요해지면 portfolio-sitemap.xml
한 번으로 이름·이미지·lastmod 까지는 받을 수 있다(이름이 슬러그라 '10051' 같은
숫자 제목이 섞이는 게 문제다).

**날짜는 uploaded_at 까지만 쓴다.** 이미지 파일명이 `YYMMDD_웹누끼_제품명` 규칙이라
사진 촬영·업로드 시점이 드러나지만 출시일은 아니다. 26건 중 17건에 날짜가 붙고
고유 일자는 9개다. 2026-09-07 하루에 4건(쿠키·선물세트 묶음 촬영)이 몰려 있어
released_at 으로 올리면 그날 신제품 4종이 나온 걸로 오보가 난다. 날짜 없는 9건은
비워 둔다. 파일 경로의 /uploads/YYYY/MM/ 은 연·월뿐이라 대체로 쓰지 않는다.

is_new 는 전부 True 다. 브랜드가 직접 `new` 분류에 넣은 상품만 담기 때문이다.
설명은 없다. 아카이브의 excerpt 가 26건 전부 "Product info" 라는 자리표시자다.

robots.txt: 200 text/plain 115B, 본문 첫 글자 'U'. /wp-admin/ 만 막는다.
이용약관 문서는 사이트에서 찾지 못했다. 가격 정보도 없다.
"""
import re
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "브레댄코"
LIST = "https://www.breadnco.kr/portfolio-category/new/"
MAX_PAGES = 8   # 폭주 방지. 현재 3페이지(26건).
DELAY = 2.0

# /wp-content/uploads/2026/08/260818_웹누끼_왁뿌소금빵.png → 2026-08-18
_DATE = re.compile(r"/uploads/\d{4}/\d{2}/(\d{2})(\d{2})(\d{2})_")


def _uploaded_at(src: str) -> str:
    """이미지 파일명 앞의 YYMMDD. 사진 업로드 시점이지 출시일이 아니다."""
    m = _DATE.search(src or "")
    return f"20{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        for page in range(1, MAX_PAGES + 1):
            url = LIST if page == 1 else f"{LIST}page/{page}/"
            r = base.retry(lambda: c.get(url))
            if r.status_code == 404:   # 마지막 페이지 다음은 404 로 끝난다
                break
            r.raise_for_status()

            cards = HTMLParser(r.text).css(".portfolio-entry-inner")
            if not cards:
                break

            added = 0
            for card in cards:
                title = card.css_first(".portfolio-entry-title")
                if not title:
                    continue
                name = " ".join(title.text().split())
                it = Item(brand=BRAND, name=name)
                if not name or it.key in seen:
                    continue
                seen.add(it.key)

                link = title.css_first("a")
                img = card.css_first("img.portfolio-entry-img")
                src = img.attributes.get("src", "") if img else ""

                it.image = src
                it.uploaded_at = _uploaded_at(src)
                it.is_new = True          # 브랜드의 '신제품' 분류에 들어있는 상품만 본다
                it.url = link.attributes.get("href", "") if link else ""
                items.append(it)
                added += 1

            if not added:
                break
            time.sleep(DELAY)
    return items
