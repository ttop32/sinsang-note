"""매스커피(MASS COFFEE). 매스컴퍼니.

⚠️ **도메인부터 틀리기 쉽다.** `masscoffee.com` 은 브랜드 것이 아니다 —
http·https 둘 다 HugeDomains 의 '도메인 판매' 페이지(44KB)로 떨어진다.
TLS 가 UNEXPECTED_EOF 로 보이던 것도 그 주차 서버 쪽 사정이었다.
`masscoffee.co.kr` 은 NXDOMAIN. 진짜 공식은 **`mass-coffee.com`** 이다
(Vercel 호스팅, https 정상, 2026-10-03 실측). 창업 상담이 앞에 있는
사이트지만 `/menu` 에 **전체 메뉴가 서버렌더 정적 HTML** 로 다 들어 있다.
브라우저 불필요, 요청 한 번이면 끝난다.

── 구조 ───────────────────────────────────────────────────────────────
`/menu` 한 장에 `section.cat` 여섯 칸이 순서대로 박혀 있다.
  SEASON 5 · COFFEE 13 · BEVERAGE 18 · TEA 7 · 1L 3 · OPTION(상품 아님)
카드는 `article.item` 이고 `h3`(한글명) · `p.en`(영문명) · `span.badge`
(ONLY ICE / ICE·HOT 등) · `p.desc`(설명) · `figure img`(사진)로 되어 있다.
OPTION 칸만 카드가 아니라 `.optgrid` 의 글자 목록이라 `article.item` 이
0건이다 — 샷 추가·펄 같은 **끼워 파는 옵션**이라 안 담는 게 맞다.

사진 주소는 `assets/img-<해시>.jpg` 상대경로인데 기준이 `/menu` 라서
`/assets/...` 로 붙는다(`/menu/assets/...` 는 404 다. 실측했다).

── 신상 판정 (2026-10-03 실측) ─────────────────────────────────────────
🔴 **NEW 배지가 없다.** 문서 전체에서 `new` 는 자바스크립트
`new IntersectionObserver` 한 번뿐이다. 신제품 신호로 쓸 수 있는 건
**SEASON 칸** 하나다 — 머리글이 `시즌 메뉴 · 26SS 여름 시즌 · 총 5종`.
  SEASON 5건 / 전체 46건 = **10.9%**. 전건이 아니므로 가짜는 아니다.
나머지 41건은 is_new 를 비워 둔다(None). 브랜드가 '신제품이 아니다'라고
말한 적은 없지만 '신제품이다'라고도 안 했다.

⚠️ **시즌 칸은 '신메뉴' 칸과 다르다.** 여름마다 돌아오는 수박 주스 같은
상품이 섞일 수 있다. 그래서 이 is_new 를 '브랜드가 올여름 라인업으로
묶었다'는 뜻 이상으로 읽으면 안 된다. 머리글의 `26SS` 는 시즌 표기이지
날짜가 아니라서 released_at·uploaded_at 으로 옮기지 않는다 —
**날짜를 지어내지 않는다.** 날짜가 없으므로 rules.is_fresh 의 STALE(90일)
가드가 대신 받친다.

날짜 후보가 하나도 없다는 것도 확인했다. 사진 파일명이 내용 해시
(`img-7e47242bebd9.jpg`)라 epoch 가 없고, 상품 상세 페이지도, 공지·
보도자료 게시판도 없다(사이트가 `/`·`/menu`·`/store` 세 장뿐이다).
`/` 의 '신규 오픈' 목록은 **매장** 오픈이라 상품이 아니다 — 담지 않는다.
"""

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "매스커피"
SITE = "https://mass-coffee.com"
MENU_URL = f"{SITE}/menu"

NEW_SECTION = "SEASON"      # 유일한 신제품 신호. 머리글이 '시즌 메뉴 · 26SS …'
SKIP_SECTIONS = {"OPTION"}  # 음료에 얹는 추가 옵션. 상품이 아니다.

# 시즌 칸이 전체의 이 비율을 넘으면 '시즌'이 아니라 그냥 전체다. 실측 10.9%.
MAX_NEW_RATIO = 0.5


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _abs(src: str) -> str:
    """`assets/img-….jpg` 는 `/menu` 기준이라 루트로 붙는다(=/assets/…)."""
    if not src:
        return ""
    if src.startswith("http"):
        return src
    return f"{SITE}/{src.lstrip('./')}"


def fetch() -> list[Item]:
    with base.client() as c:
        r = base.retry(lambda: c.get(MENU_URL))
        r.raise_for_status()
    doc = HTMLParser(r.text)

    sections = doc.css("section.cat")
    if not sections:
        raise RuntimeError("매스커피 메뉴 칸 0건 — 셀렉터가 깨졌을 수 있다")

    items: list[Item] = []
    seen = set()
    new_names, all_names = set(), set()
    for sec in sections:
        h2 = sec.css_first("h2")
        cat = _clean(h2.text()) if h2 else ""
        if cat in SKIP_SECTIONS:
            continue
        for art in sec.css("article.item"):
            h3 = art.css_first("h3")
            name = _clean(h3.text()) if h3 else ""
            if not name:
                continue
            en = art.css_first("p.en")
            desc = art.css_first("p.desc")
            img = art.css_first("figure img")
            all_names.add(name)
            if cat == NEW_SECTION:
                new_names.add(name)
            it = Item(
                brand=BRAND,
                name=name,
                name_en=_clean(en.text()) if en else "",
                desc=_clean(desc.text()) if desc else "",
                image=_abs(img.attributes.get("src", "") if img else ""),
                labels=[_clean(b.text()) for b in art.css("span.badge") if b.text().strip()],
                category=cat,
                # 시즌 칸만 True. 나머지는 '모른다'(None)로 둔다.
                is_new=True if cat == NEW_SECTION else None,
            )
            if it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)

    if not items:
        raise RuntimeError("매스커피 메뉴 0건 — 카드 셀렉터(article.item)가 깨졌다")
    if not new_names:
        raise RuntimeError(f"매스커피 {NEW_SECTION} 칸 0건 — 시즌 칸 이름이 바뀐 것 같다")
    ratio = len(new_names) / len(all_names)
    if ratio > MAX_NEW_RATIO:
        raise RuntimeError(
            f"매스커피 시즌 칸이 전체의 {ratio:.0%}"
            f"({len(new_names)}/{len(all_names)}) — 칸 구분이 깨진 것으로 본다")
    return items
