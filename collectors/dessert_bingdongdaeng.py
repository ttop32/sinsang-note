"""빙동댕 — Wix 사이트의 **'신메뉴' 전용 메뉴 탭** 한 장을 읽는다.

공정위 `아이스크림/빙수`(K1) 가맹점 수 **79개**로 배스킨라빈스·설빙·카페요아정·
요거트아이스크림의정석·달롱도르 다음 6위다(2024년 말, notes/FRANCHISE-MASTER.md).
가맹본부 (주)시원한여자들. 빙수 전업 브랜드라 `brand_sub` 는 `빙수` 다.

## 사이트 구조 — Wix. 도메인이 **퓨니코드**다

  https://빙동댕.kr → `https://www.xn--hl1bno83x.kr`
  httpx 는 퓨니코드로 그대로 적어야 붙는다(한글 도메인을 넣으면 IDNA 변환은
  되지만 이 레포 러너의 DNS 가 한 번씩 실패했다). **상수에 퓨니코드로 박아 둔다.**

페이지 목록은 홈 HTML 안의 Wix 라우터 JSON(`"pageId":…,"pageUriSEO":…`)에 다 있다.
2026-10-02 실측:

| pageId | title      | pageUriSEO       |
|--------|------------|------------------|
| ha19q  | 메뉴 신메뉴 | `복제-메뉴-빙수`  | ← **우리가 쓰는 면**
| rscon  | 메뉴 빙수   | `team-4`         |
| jfbzt  | 메뉴 크로플 | `복제-메뉴`       |
| oincg  | 메뉴 음료   | `복제-메뉴-크로플` |

⚠️ **slug 와 내용이 어긋나 있다.** `복제-메뉴-빙수` 가 신메뉴 면이고
`복제-메뉴-크로플` 이 음료 면이다. 운영자가 페이지를 복제해 만들면서 slug 를
안 고친 흔적이다. **이름만 보고 고르지 마라 — 위 표가 실측이다.**

## 마크업

  GET https://www.xn--hl1bno83x.kr/복제-메뉴-빙수   200 / 776,680B   SSR 로 다 나온다
    <div role="listitem">
      <img src="https://static.wixstatic.com/media/28b05a_c9cc…~mv2.png/v1/fill/
                w_258,h_151,…/%EC%91%A5…_%EB%B0%B0%EB%8B%AC%EC%95%B1.png"
           alt="쑥인절미빙수_배달앱.png">
      <h2>​쑥인절미 빙수</h2>                       ← 1번째 h2 = 상품명
      <h2>쑥과 인절미가 포근하게 어우러지는<br>쫀득고소한 매력 가득한 빙수</h2>
    </div>                                        ← 2번째 h2 = 설명
  선택자: `div[role=listitem]` → `h2`(2개) · `img`.
  ⚠️ 상품명 앞에 **제로폭 공백(U+200B)** 이 붙어 온다(`​쑥인절미 빙수`).
     Wix 리치텍스트가 넣는 것이다. `strip()` 만으로는 안 지워진다 — 따로 턴다.
  이미지는 `static.wixstatic.com` 절대 **https** URL 이라 그대로 쓴다.

## 신상 판정 — '신메뉴' 탭이 전부이고, **비율로 받친다**

날짜가 **어디에도 없다.** 목록에도, 상세 페이지도 없다(상품 상세가 아예 없다).
`released_at`·`uploaded_at` 을 **비워 둔다.** 지어내지 않는다 —
이 브랜드는 `first_seen` diff 로만 판정되고, 합류 첫날엔 신제품 0건이 정상이다.

`is_new=True` 의 근거는 **브랜드가 직접 운영하는 '신메뉴' 탭**이다. 화면에
`NEW` 글자도 떠 있지만 그건 별도 컴포넌트라 상품에 붙여 읽을 수 없다.

**배지/탭을 믿기 전에 분모를 셌다(2026-10-02 실측).**
```
신메뉴 (복제-메뉴-빙수)      3건   ← 수집 대상
빙수   (team-4)            36건   (그중 7건은 이름이 'WINTER' 인 구분선)
크로플 (복제-메뉴)           13건
음료   (복제-메뉴-크로플)     26건
                      전체 75건 → 신메뉴 비율 **4.0%**
```
4% 다. 퀴즈노스(66건 **전부**에 NEW)·설빙(시그니처 배지가 섞여 들어옴) 같은
'장식 배지' 가 아니다. 신메뉴 3건 중 '쑥인절미 빙수' 는 빙수 탭에도 있어서
(신상이 상시 메뉴로 옮겨 가는 중) 탭이 실제로 관리되고 있음을 보여 준다.
아래 `fetch()` 에 **0% / 과반** 양쪽을 터뜨리는 가드를 넣었다.

robots: https://www.xn--hl1bno83x.kr/robots.txt → 200 / 494B.
        `User-agent: * / Allow: / / Disallow: *?lightbox=` — **우리 경로는 허용**이다.
        PetalBot 만 전면 차단이고, dotbot·AhrefsBot 에 `Crawl-delay: 10` 이 있다.
        `*` 그룹에는 Crawl-delay 가 없어서 이 어댑터는 `DELAY=2.2` 를 쓴다.
약관:   확인하지 않았다(운영자 판단으로 약관 제약은 무시).
"""
import time

from selectolax.parser import HTMLParser

from . import base
from .base import Item

BRAND = "빙동댕"
SITE = "https://www.xn--hl1bno83x.kr"       # 빙동댕.kr 의 퓨니코드
NEWMENU = SITE + "/복제-메뉴-빙수"           # ⚠️ slug 와 내용이 어긋난다. 위 docstring 표 참고
# 분모용 카탈로그 면. 신메뉴 비율을 재는 데만 쓰고 상품으로 넣지 않는다.
CATALOG = [SITE + "/team-4", SITE + "/복제-메뉴", SITE + "/복제-메뉴-크로플"]
DELAY = 2.2

# 신메뉴 탭이 전체 메뉴의 이 비율을 넘으면 '신메뉴' 가 아니라 카탈로그로 바뀐 것이다.
MAX_NEW_RATIO = 0.5

# Wix 리치텍스트가 상품명 앞에 끼워 넣는 제로폭 공백.
_ZWSP = "​﻿"


def _text(node) -> str:
    return " ".join(node.text().split()).strip(_ZWSP + " ") if node else ""


def _rows(html: str) -> list:
    return HTMLParser(html).css("div[role=listitem]")


def fetch() -> list[Item]:
    items: list[Item] = []
    seen = set()
    with base.client() as c:
        r = base.retry(lambda: c.get(NEWMENU))
        r.raise_for_status()
        rows = _rows(r.text)

        # 신메뉴 면이 통째로 비면 Wix 가 리페이터 마크업을 바꾼 것이다.
        # 조용히 0건을 돌려주지 않는다.
        if not rows:
            raise ValueError(
                f"빙동댕 신메뉴 면이 비었다. {r.url} → {len(r.content)}B — "
                f"Wix 리페이터 선택자(div[role=listitem] / h2 / img)가 "
                f"바뀌었는지 확인하라")

        # ── 비율 가드 ──────────────────────────────────────────────
        # 배지·전용탭은 '있다'가 아니라 '전체의 몇 %냐'로 믿는다. 이 레포가
        # 퀴즈노스(NEW 가 66건 전부)·설빙(시그니처 배지 혼입)·컴포즈(배지가
        # 그림 안에 합성)로 세 번 데였다. 2026-10-02 실측 3/75 = 4.0%.
        total = len(rows)
        for u in CATALOG:
            time.sleep(DELAY)
            rr = base.retry(lambda u=u: c.get(u))
            rr.raise_for_status()
            total += len(_rows(rr.text))
        if total <= len(rows):
            raise ValueError(
                f"빙동댕 카탈로그 면에서 상품을 하나도 못 읽었다(전체 {total}, "
                f"신메뉴 {len(rows)}). 분모를 못 세면 신메뉴 탭을 믿을 수 없다 — "
                f"카탈로그 slug({', '.join(CATALOG)})가 바뀌었는지 확인하라")
        if len(rows) > total * MAX_NEW_RATIO:
            raise ValueError(
                f"빙동댕 신메뉴가 전체 {total}건 중 {len(rows)}건"
                f"({len(rows) / total:.0%})이다. 과반이 신메뉴일 수는 없다 — "
                f"신메뉴 탭이 전체 카탈로그로 바뀌었는지 확인하라"
                f"(퀴즈노스 선례: NEW 가 66건 전부)")

        for li in rows:
            h2 = li.css("h2")
            name = _text(h2[0]) if h2 else ""
            # 'WINTER' 처럼 이름 자리에 구분선이 들어오는 행이 카탈로그 면에
            # 있다. 신메뉴 면엔 아직 없지만 같은 리페이터라 막아 둔다.
            if not name or name.isupper() and len(name) <= 10:
                continue
            img = li.css_first("img")
            src = (img.attributes.get("src") or "").strip() if img else ""
            it = Item(
                brand=BRAND,
                name=name,
                desc=_text(h2[1]) if len(h2) > 1 else "",
                image=src if src.startswith("https://") else "",
                # 날짜가 사이트 어디에도 없다. 지어내지 않고 비워 둔다.
                is_new=True,
                url=NEWMENU,
            )
            if it.key not in seen:
                seen.add(it.key)
                items.append(it)

    if not items:
        raise ValueError(
            f"빙동댕 신메뉴 면에서 상품명을 하나도 못 뽑았다({len(rows)}행). "
            f"h2 구조가 바뀌었는지 확인하라")
    return items
