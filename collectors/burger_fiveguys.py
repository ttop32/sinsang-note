"""파이브가이즈 — 메뉴판에는 신호가 없고, **'기간 한정' 배너 한 블록**만 담는다.

한국 법인은 에프지코리아(갤러리아)이고 사이트는 본사 WordPress 멀티사이트의
한국 서브사이트다(`wp-content/uploads/sites/47/`). WP REST 가 인증 없이 열려
있어서 **요청 1회**로 메뉴 전체가 온다.

    GET https://www.fiveguys.co.kr/wp-json/wp/v2/menu_category?per_page=100
        → 7건(버거 / 핫도그 / 샌드위치 / 프라이즈 / 쉐이크 / 드링크 / 토핑)
          각 건의 content.rendered 안에 그 카테고리 페이지가 통째로 들어 있다.

robots.txt 는 `User-agent: * / Disallow:`(= 전면 허용) + `Crawl-delay: 10` 이다.
요청이 1회라 크롤딜레이는 자연히 지켜진다.

## 왜 메뉴판을 안 긁는가 — 2026-10-02 전수 실측

7개 페이지의 HTML 을 다 뒤졌다.
  - `NEW`·`신메뉴`·`신제품`·`출시` **0건**.
  - `badge` 가 1건 걸리는데 **Vimeo 임베드 URL 의 `&badge=0` 파라미터**다.
    `notes/` 가 경고하는 '문자열로 세면 안 된다' 의 교과서 사례라 적어 둔다.
  - 메뉴 카드(`.card-menu-item`) 67건은 전 세계 공통 코어 메뉴다 —
    햄버거·치즈버거·베이컨버거(각 리틀 포함) 8종, 핫도그 4종, 샌드위치 6종,
    프라이 2종, 믹스인 10종, 토핑 15종. 한국에서 바뀌는 게 거의 없다.
  - 이미지 경로의 `/sites/47/2025/06/` 은 181건이 한 달에 몰린 **사이트 개설
    때의 일괄 업로드**다(2025-06 181 / 2025-09 51 / 2025-02 48 / 2025-07 35).
    상품별 날짜로 못 쓴다.
  - `wp/v2/posts` 14건은 **해외 매체 링크 모음**이고 마지막 글이 2025-07-25 다.
    한국 출시 소식이 아니다.

## 담는 것 — 브랜드가 '한정' 이라고 쓴 히어로 블록

쉐이크 페이지 맨 위에 이런 블록이 하나 있다(2026-10-02).

    <section data-comname="section-split-media-content">
      <p class="is-style-p-lead">복숭아 크럼블</p>
      <p>“과즙 가득 복숭아. 바삭한 크럼블.</p>
      <p>달콤하고 과즙 가득한 복숭아에 크리미한 바닐라 쉐이크, …</p>
      <p>한정 기간 동안 만나보세요!”</p>
      <img class="split-media-feature-image" src="…/2026/09/Peach-Crumble-LTO.png">

같은 페이지 목차에 `기간 한정 메뉴`(`#limited-time-drinks-menu`) 항목이 있어
브랜드가 이 블록을 한정 메뉴 자리로 쓰고 있음이 확인된다. 파일명도 `-LTO`
(limited time offer)다. **`한정` 이 들어간 split-media 블록만** 담는다.
7개 페이지 전체에서 `한정` 은 이 페이지에 2회(본문 1 + 목차 1)뿐이고
나머지 6개 페이지는 0회라 오탐 여지가 없다.

⚠️ **수확이 1건이다. 그리고 손으로 만든 블록이라 레이아웃이 바뀌면 깨진다.**
그래서 "0건"이 '한정 메뉴가 없는 상태' 인지 '파서가 고장난 상태' 인지 구분할
수 있게 안전판을 둔다 — 메뉴 카드가 `MIN_CARDS` 미만이면 마크업이 바뀐 것으로
보고 **예외를 올린다.** 카드가 정상인데 한정 블록만 없으면 0건이 맞다.

## 날짜는 비운다

이 블록에는 날짜가 없다. 이미지가 네덜란드 사이트(`fiveguys.nl`, 같은 멀티사이트
망이라 미디어를 공유한다) 경로라 `…/2026/09/` 까지만 나오고 **일(日)이 없다.**
`uploaded_at` 은 `YYYY-MM-DD` 자리라 날을 지어내야 하는데 그건 안 한다.
페이지의 `modified`(2026-10-01)도 쓰지 않는다 — 오타 하나만 고쳐도 갱신되는
문서 수정 시각이라 출시일로 읽히면 안 된다.

날짜 없이 `is_new=True` 만 두면 `rules.is_fresh` 가 `first_seen` + `STALE`(90일)
로 알아서 내린다. 그게 이 신호에 맞는 수명이다.

상품별 주소는 없다. 블록이 `<a>` 가 아니라 본문이라 `url` 은 비우고
`base.SITES` 폴백(쉐이크 메뉴 페이지)에 맡긴다.

## 두 번째 소스 — 한화갤러리아 보도자료. 2026-10-08 합류, **현재 수확 0건**

한국 법인(에프지코리아)의 모회사 한화갤러리아가 보도자료를 낸다. 공용 모듈이
`collectors/hanwhagalleria_press.py` 이고 벤슨(`collectors/dessert_benson.py`)과
같은 목록을 **한 번만** 받아 나눠 쓴다.

🔴 **실측 수확이 0건이다. 그래도 넣는다.** 4년치 144건 중 파이브가이즈 기사가
18건인데 **전부 매장·실적 이야기**다 — 4·5·6·7·8·9호점 오픈, 용산 상륙, 배달
개시, 글로벌 TOP5, 일본 진출 MOU, 1주년 행사. **신메뉴 출시 기사가 한 건도
없다.** 한국 파이브가이즈는 코어 메뉴가 전 세계 공통이고 한국 한정 메뉴는
위의 '기간 한정' 히어로 블록으로만 알린다는 뜻이고, 이 어댑터가 메뉴판을
안 긁는 이유와 같은 그림이다. 배선을 미리 깔아 두는 쪽을 택한 건, 이 브랜드가
한국에서 신메뉴를 내면 **그 소식이 올라올 곳이 거기뿐**이기 때문이다.

중복은 `it.key`(= `base.make_key`) 로 본다. 한정 블록이 **먼저** 들어가고
보도자료가 뒤에 붙으므로 겹치면 메뉴판 쪽 이름이 남는다.
"""
import re

from selectolax.parser import HTMLParser

from . import base
from .base import Item
from . import hanwhagalleria_press as press

BRAND = "파이브가이즈"
ROOT = "https://www.fiveguys.co.kr"
API = ROOT + "/wp-json/wp/v2/menu_category"
PER_PAGE = 100
MAX_PAGES = 30        # 폭주 방지. 현재 카테고리 7건.
MIN_CARDS = 20        # 이보다 적으면 마크업이 바뀐 것으로 본다(현재 67건)

LIMITED = "한정"      # 브랜드가 이 말로 기간 한정을 알린다
LTO_SECTION = 'section[data-comname="section-split-media-content"]'

_TRAIL = re.compile(r'^[“"\'\s]+|[”"\'\s]+$')


def _clean(s: str) -> str:
    return " ".join((s or "").split())


def _desc(section, name: str) -> str:
    """리드 문단(=상품명) 말고 나머지 문단을 설명으로 잇는다."""
    out = []
    for p in section.css("p.wp-block-paragraph"):
        t = _TRAIL.sub("", _clean(p.text()))
        if t and t != name:
            out.append(t)
    return " ".join(out)


def fetch() -> list[Item]:
    with base.client() as c:
        def call():
            r = c.get(API, params={"per_page": PER_PAGE})
            r.raise_for_status()
            return r.json()

        pages = base.retry(call)

    if not isinstance(pages, list) or not pages:
        raise RuntimeError(f"{API}: menu_category 가 비었다")
    if len(pages) > MAX_PAGES:
        raise RuntimeError(f"{BRAND}: 카테고리가 {MAX_PAGES}건을 넘었다")

    cards = 0
    items: list[Item] = []
    seen = set()
    for page in pages:
        html = ((page.get("content") or {}).get("rendered")) or ""
        doc = HTMLParser(html)
        cards += len(doc.css(".card-menu-item h3"))
        category = _clean((page.get("title") or {}).get("rendered"))
        for sec in doc.css(LTO_SECTION):
            if LIMITED not in sec.text():
                continue
            lead = sec.css_first("p.is-style-p-lead")
            name = _TRAIL.sub("", _clean(lead.text())) if lead is not None else ""
            if not name:
                continue
            img = sec.css_first("img.split-media-feature-image")
            it = Item(
                brand=BRAND,
                name=name,
                desc=_desc(sec, name),
                image=img.attributes.get("src", "") if img is not None else "",
                labels=["기간 한정"],
                # 카테고리 제목이 SEO 문장이라 길다. 첫 조각만 쓴다.
                category=category.split(":")[0].split("|")[0].strip(),
                is_new=True,
                # 날짜 없음 — 블록에 없고 지어내지 않는다(위 docstring).
            )
            if it.key in seen:
                continue
            seen.add(it.key)
            items.append(it)

    # 한정 블록이 0건인 건 정상일 수 있다(그달에 한정 메뉴가 없으면). 하지만
    # 메뉴 카드까지 안 잡히면 마크업이 바뀐 것이다 — 조용히 0건을 돌려주지 않는다.
    if cards < MIN_CARDS:
        raise RuntimeError(
            f"{API}: 메뉴 카드가 {cards}건뿐이다(기대 {MIN_CARDS}건 이상). "
            "WordPress 템플릿이 바뀌었는지 확인해라")

    # 한화갤러리아 보도자료를 **더하기만** 한다. 메뉴판 쪽이 먼저 들어가 있어서
    # 이름이 겹치면(`it.key`) 보도자료 건을 버린다 — 정규 표기는 메뉴판이다.
    for it in press.items(BRAND):
        if it.key in seen:
            continue
        seen.add(it.key)
        items.append(it)
    return items
